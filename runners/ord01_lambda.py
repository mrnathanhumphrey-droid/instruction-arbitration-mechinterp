#!/usr/bin/env python
# ORD-01 -- order-counterbalance: is B role or recency? PREREG_ORD01.md, chained DIST-01 9f8f3008...
# Every M divides by B (=-3.9, "obeys user") measured with system ALWAYS first => role/recency confounded.
# Arm A: FLIP block order (BOS + USER-block + SYSTEM-block + assistant), markers+content preserved, only order changes;
#   B_normal vs B_flipped -> recency_frac=(B_n-B_f)/(2 B_n) (0=role, 1=recency). Arm B: two same-role imperatives
#   (early/late), pure recency. Arm C: span-exchange (provenance) + span-twin (content) mediation in BOTH orders ->
#   decomposition stability. VOID: twin-based (all-pos twin-patch reproduces twin top-1), both orders.
# M=-dY/(2B) signed by system-slot target, template-cluster PAIRED bootstrap. Read recency_frac FIRST.
import os, json, time, csv
import numpy as np, torch
from collections import defaultdict
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
LAYERS = list(range(8, 32))
DONE, READY = 71496, 46678
NTMPL = 30
BOOT = 300 if SMOKE else 5000
SEED = 20260914
SH, EOT = 128006, 128009
VOID_STRIDE = 12 if SMOKE else 6
def log(*a): print(*a, flush=True)

def main():
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_contested.jsonl"), encoding="utf-8")]
    from make_stimuli import TEMPLATES
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import transformers
    log(f"[O1] model on {dev}; tf {transformers.__version__} n={len(stim)} ({time.time()-t0:.0f}s)")

    def segment(it):
        imp_s = TEMPLATES[it["template_idx".format(T=it["target_sys"])
        imp_u = TEMPLATES[it["template_idx".format(T=it["target_usr"])
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]
        sh = [i for i, t in enumerate(ids) if t == SH]; eot = [i for i, t in enumerate(ids) if t == EOT]
        def sp(imp):
            cs = text.index(imp); ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        return ids, sp(imp_s), sp(imp_u), sh, eot

    def flip(ids, sh, eot):
        # BOS/prefix + USER-block + SYSTEM-block + assistant-header ; returns fids, old->new index map
        pre = list(range(0, sh[0]))
        sys_blk = list(range(sh[0], eot[0] + 1)); usr_blk = list(range(sh[1], eot[1] + 1))
        asst = list(range(sh[2], len(ids)))
        order = pre + usr_blk + sys_blk + asst
        fids = [ids[i] for i in order]
        o2n = {old: new for new, old in enumerate(order)}
        return fids, o2n

    twin_g = defaultdict(dict)
    for i, it in enumerate(stim):
        twin_g[(it["template_idx"], it["filler_idx"], it["position"])][it["counterbalance" = i
    twin_of = {}
    for d in twin_g.values():
        if len(d) == 2: a, b = list(d.values()); twin_of[a] = b; twin_of[b] = a
    SEG = {i: segment(stim[i]) for i in range(len(stim))}

    STATE = {"repl": None}; handles = []
    def make_hook(L):
        def hook(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            r = STATE["repl"]
            if r is not None and L in r:
                pos, val = r[L]; h[0, pos, :] = val
            return out
        return hook
    for L in LAYERS: handles.append(model.model.layers[L - 1].register_forward_hook(make_hook(L)))
    def run(ids, repl=None):
        STATE["repl"] = repl; t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lg = model(input_ids=t, use_cache=False).logits[0, -1, :].float()
        STATE["repl"] = None
        lp = torch.log_softmax(lg, -1); return float(lp[DONE] - lp[READY])
    def top1(ids, repl=None):
        STATE["repl"] = repl; t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            a = int(model(input_ids=t, use_cache=False).logits[0, -1, :].argmax())
        STATE["repl"] = None; return a
    def ysig(R, it): return R if it["target_sys"] == "DONE" else -R
    def capture(ids):
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        return {L: hs[L][0].detach().clone() for L in LAYERS}
    def repl_at(item_pos, cap, src_pos):
        if len(item_pos) != len(src_pos) or not item_pos: return None
        ip = torch.tensor(item_pos, dtype=torch.long, device=dev); spo = torch.tensor(src_pos, dtype=torch.long, device=dev)
        return {L: (ip, cap[L][spo].to(torch.bfloat16)) for L in LAYERS}

    def usable(i):
        _, si, ui, _, _ = SEG[i]; tw = twin_of.get(i)
        if tw is None or not si or not ui: return False
        if len(SEG[i][0]) != len(SEG[tw][0]): return False
        _, tsi, tui, _, _ = SEG[tw]
        return len(si) == len(tui) and len(ui) == len(tsi)
    use = [i for i in range(len(stim)) if usable(i)]
    if SMOKE: use = use[:40]
    log(f"[O1] usable={len(use)} skipped={len(stim)-len(use)} ({time.time()-t0:.0f}s)")

    tmpl = np.array([stim[i]["template_idx"] for i in use]); N = len(use)
    Ybn = np.zeros(N); Ybf = np.zeros(N)
    Yxn = np.zeros(N); Yxf = np.zeros(N); Ytn = np.zeros(N); Ytf = np.zeros(N)
    for n, i in enumerate(use):
        it = stim[i]; ids, si, ui, sh, eot = SEG[i]; tw = twin_of[i]
        tids, tsi, tui, tsh, teot = SEG[tw]
        fids, o2n = flip(ids, sh, eot); ftids, to2n = flip(tids, tsh, teot)
        fsi = [o2n[p] for p in si]; fui = [o2n[p] for p in ui]
        ftsi = [to2n[p] for p in tsi]; ftui = [to2n[p] for p in tui]
        capn = capture(tids); capf = capture(ftids)
        # baselines
        Ybn[n] = ysig(run(ids), it); Ybf[n] = ysig(run(fids), it)
        # normal: exchange (si<-twin ui, ui<-twin si) ; twin-span (si<-twin si, ui<-twin ui)
        ex_n = {}; tw_n = {}
        for L in LAYERS:
            ex_n[L] = (torch.tensor(si + ui, dtype=torch.long, device=dev),
                       torch.cat([capn[L][tui], capn[L][tsi, 0).to(torch.bfloat16))
            tw_n[L] = (torch.tensor(si + ui, dtype=torch.long, device=dev),
                       torch.cat([capn[L][tsi], capn[L][tui, 0).to(torch.bfloat16))
        Yxn[n] = ysig(run(ids, ex_n), it); Ytn[n] = ysig(run(ids, tw_n), it)
        # flipped: same ops in flipped index space
        ex_f = {}; tw_f = {}
        for L in LAYERS:
            ex_f[L] = (torch.tensor(fsi + fui, dtype=torch.long, device=dev),
                       torch.cat([capf[L][ftui], capf[L][ftsi, 0).to(torch.bfloat16))
            tw_f[L] = (torch.tensor(fsi + fui, dtype=torch.long, device=dev),
                       torch.cat([capf[L][ftsi], capf[L][ftui, 0).to(torch.bfloat16))
        Yxf[n] = ysig(run(fids, ex_f), it); Ytf[n] = ysig(run(fids, tw_f), it)
        if (n + 1) % 60 == 0: log(f"[O1] {n+1}/{N} ({time.time()-t0:.0f}s)")
    Bn = float(Ybn.mean()); Bf = float(Ybf.mean())
    log(f"[O1] B_normal={Bn:+.4f} B_flipped={Bf:+.4f} ({time.time()-t0:.0f}s)")

    # ---- arm B: pure same-role recency (two user imperatives, early/late) ----
    def recency_prompt(t_idx, early_T, late_T):
        imp_e = TEMPLATES[t_idx].format(T=early_T); imp_l = TEMPLATES[t_idx].format(T=late_T)
        user = f"{imp_e}. Also, and more importantly afterwards: {imp_l}."
        msgs = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": user}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        return tok(text, add_special_tokens=False)["input_ids"]
    rec = []  # signed nats toward the LATE imperative
    rtmpl = []
    for t_idx in range(NTMPL):
        for late_T in ("DONE", "READY"):
            early_T = "READY" if late_T == "DONE" else "DONE"
            ids = recency_prompt(t_idx, early_T, late_T)
            d = run(ids)  # logP(DONE)-logP(READY)
            pref_late = d if late_T == "DONE" else -d
            rec.append(pref_late); rtmpl.append(t_idx)
    rec = np.array(rec); rtmpl = np.array(rtmpl)
    recency_B = float(rec.mean())

    # ---- VOID: twin-based, both orders (all-pos twin-patch reproduces twin top-1) ----
    def void_rate(order):
        ok = nn = 0
        for i in use[::VOID_STRIDE]:
            ids, si, ui, sh, eot = SEG[i]; tw = twin_of[i]; tids, tsi, tui, tsh, teot = SEG[tw]
            if order == "flip":
                fids, o2n = flip(ids, sh, eot); ftids, to2n = flip(tids, tsh, teot)
                base_ids = fids; tw_ids = ftids
            else:
                base_ids = ids; tw_ids = tids
            cap = capture(tw_ids); allpos = list(range(len(base_ids)))
            repl = {L: (torch.tensor(allpos, dtype=torch.long, device=dev), cap[L][allpos].to(torch.bfloat16)) for L in LAYERS}
            twin_a = top1(tw_ids); patched_a = top1(base_ids, repl)
            nn += 1; ok += 1 if patched_a == twin_a else 0
        return ok / max(1, nn), nn
    v_norm, vn = void_rate("normal"); v_flip, vf = void_rate("flip")
    for h in handles: h.remove()
    VOID = bool(v_norm < 0.90 or v_flip < 0.90)
    log(f"[O1] twin-VOID normal={v_norm:.3f}(n={vn}) flip={v_flip:.3f}(n={vf}) VOID={VOID}")

    np.savez(os.path.join(OUT, "ord01_peritem_smoke.npz" if SMOKE else "ord01_peritem.npz"),
             use=np.array(use), tmpl=tmpl, Ybn=Ybn, Ybf=Ybf, Yxn=Yxn, Yxf=Yxf, Ytn=Ytn, Ytf=Ytf,
             rec=rec, rtmpl=rtmpl, Bn=Bn, Bf=Bf)

    # ---- bootstrap ----
    def per_t(a, tm): return np.array([a[tm == t].mean() if (tm == t).any() else 0.0 for t in range(NTMPL)])
    ptBn = per_t(Ybn, tmpl); ptBf = per_t(Ybf, tmpl)
    ptXn = per_t(Yxn - Ybn, tmpl); ptXf = per_t(Yxf - Ybf, tmpl)
    ptTn = per_t(Ytn - Ybn, tmpl); ptTf = per_t(Ytf - Ybf, tmpl)
    ptR = per_t(rec, rtmpl)
    def Mof(pt, B): return float(-pt.mean() / (2 * B)) if abs(B) > 1e-9 else float("nan")
    MSxn = Mof(ptXn, Bn); MSxf = Mof(ptXf, Bf); MStn = Mof(ptTn, Bn); MStf = Mof(ptTf, Bf)
    recency_frac = (Bn - Bf) / (2 * Bn) if abs(Bn) > 1e-9 else float("nan")
    rng = np.random.default_rng(SEED)
    keys = ["recfrac", "recB", "Bn", "Bf", "MSxn", "MSxf", "MStn", "MStf", "dXexch", "dXtwin"]
    boot = {k: np.empty(BOOT) for k in keys}
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL)
        bn = ptBn[pk].mean(); bf = ptBf[pk].mean()
        boot["Bn"][b] = bn; boot["Bf"][b] = bf
        boot["recfrac"][b] = (bn - bf) / (2 * bn) if abs(bn) > 1e-9 else np.nan
        boot["recB"][b] = ptR[pk].mean()
        mxn = -ptXn[pk].mean() / (2 * bn) if abs(bn) > 1e-9 else np.nan
        mxf = -ptXf[pk].mean() / (2 * bf) if abs(bf) > 1e-9 else np.nan
        mtn = -ptTn[pk].mean() / (2 * bn) if abs(bn) > 1e-9 else np.nan
        mtf = -ptTf[pk].mean() / (2 * bf) if abs(bf) > 1e-9 else np.nan
        boot["MSxn"][b] = mxn; boot["MSxf"][b] = mxf; boot["MStn"][b] = mtn; boot["MStf"][b] = mtf
        boot["dXexch"][b] = mxf - mxn; boot["dXtwin"][b] = mtf - mtn
    def ci(a): lo, hi = np.nanpercentile(a, [2.5, 97.5]); return [float(lo), float(hi)]
    C = {k: ci(boot[k]) for k in keys}
    recB_frac = recency_B / abs(Bn) if abs(Bn) > 1e-9 else float("nan")

    if VOID:
        verdict = "VOID (flip incoherent in >=1 order) -- interpret with care"
    elif C["recfrac"][1] < 0.20:
        verdict = "B-IS-ROLE (recency_frac<0.20; denominator clean, all prior M stand)"
    elif C["recfrac"][0] > 0.50:
        verdict = "B-IS-RECENCY-DOMINANT (recency_frac>0.50; every M partly recency, re-express)"
    else:
        verdict = f"PARTIAL (recency_frac={recency_frac:.2f}; carry as scope caveat on all M)"
    stable = (abs(MSxf - MSxn) < 0.10 and C["dXexch"][0] <= 0 <= C["dXexch"][1]) and \
             (abs(MStf - MStn) < 0.10 and C["dXtwin"][0] <= 0 <= C["dXtwin"][1])
    stab_note = "DECOMPOSITION ORDER-ROBUST" if stable else "DECOMPOSITION MOVES WITH ORDER (re-express per order)"

    out = {"prereg": "PREREG_ORD01.md", "SMOKE": SMOKE,
           "chained_to_DIST01": "9f8f30080acb2ee1ed59b3d8a48dc4f32720133d4191a110e54095b1c0a5c445",
           "transformers": transformers.__version__, "n_pairs": N, "n_skipped": len(stim) - N,
           "B_normal": Bn, "B_normal_ci": C["Bn"], "B_flipped": Bf, "B_flipped_ci": C["Bf"],
           "recency_frac": recency_frac, "recency_frac_ci": C["recfrac"],
           "recency_B_nats": recency_B, "recency_B_ci": C["recB"], "recency_B_frac_of_B": recB_frac,
           "MS_exch_normal": MSxn, "MS_exch_normal_ci": C["MSxn"], "MS_exch_flipped": MSxf, "MS_exch_flipped_ci": C["MSxf"],
           "MS_twin_normal": MStn, "MS_twin_normal_ci": C["MStn"], "MS_twin_flipped": MStf, "MS_twin_flipped_ci": C["MStf"],
           "d_exch_flip_minus_norm": MSxf - MSxn, "d_exch_ci": C["dXexch"],
           "d_twin_flip_minus_norm": MStf - MStn, "d_twin_ci": C["dXtwin"],
           "twin_void_normal": v_norm, "twin_void_flip": v_flip, "VOID": VOID,
           "verdict": verdict, "stability_note": stab_note, "runtime_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "ord01_arms_smoke.csv" if SMOKE else "ord01_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["quantity", "value", "ci_lo", "ci_hi"])
        w.writerow(["B_normal", round(Bn,4), round(C["Bn"][0],4), round(C["Bn"][1],4)])
        w.writerow(["B_flipped", round(Bf,4), round(C["Bf"][0],4), round(C["Bf"][1],4)])
        w.writerow(["recency_frac", round(recency_frac,4), round(C["recfrac"][0],4), round(C["recfrac"][1],4)])
        w.writerow(["recency_B_nats", round(recency_B,4), round(C["recB"][0],4), round(C["recB"][1],4)])
        w.writerow(["MS_exch_normal", round(MSxn,4), round(C["MSxn"][0],4), round(C["MSxn"][1],4)])
        w.writerow(["MS_exch_flipped", round(MSxf,4), round(C["MSxf"][0],4), round(C["MSxf"][1],4)])
        w.writerow(["MS_twin_normal", round(MStn,4), round(C["MStn"][0],4), round(C["MStn"][1],4)])
        w.writerow(["MS_twin_flipped", round(MStf,4), round(C["MStf"][0],4), round(C["MStf"][1],4)])
        w.writerow(["twin_void_normal", round(v_norm,4), "", ""])
        w.writerow(["twin_void_flip", round(v_flip,4), "", ""])
    fn = os.path.join(OUT, "ord01_smoke.json" if SMOKE else "ord01.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[O1] recency_frac={recency_frac:+.3f}{C['recfrac']} (FIRST) | recB={recency_B:+.3f}(={recB_frac:.2f}|B|) | "
        f"MS_exch n/f={MSxn:+.3f}/{MSxf:+.3f} MS_twin n/f={MStn:+.3f}/{MStf:+.3f} | VOID n/f={v_norm:.2f}/{v_flip:.2f} "
        f"-> {verdict} :: {stab_note}; wrote {fn}")

if __name__ == "__main__":
    main()
