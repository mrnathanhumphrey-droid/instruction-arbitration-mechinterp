#!/usr/bin/env python
# RES-04 (RE-LOCKED markers+span) -- extent: is the missing half on the role MARKERS? PREREG_RES04.md, chained
# RES-02 66ec4cee... Three token-alignable EXTENTS, cross-role, all layers L8-31, RES-02 harness/estimand:
#   S span-only cross-role (RES-02 recap, within-run paired ref)
#   K markers-only cross-role (system-header <-> user-header region, SH..EOH; fixed len both roles)
#   M markers+span cross-role (both channels together)
# + same-role disruption floor at each extent (S2/K2/M2), + VOID (M-extent, group-before-subsample).
# M=-dY/(2B) signed by counterbalance, template-cluster PAIRED bootstrap. Report M_M-M_S FIRST (paired CI),
# then M_K, then additivity M_M-(M_K+M_S). Per-arm position shift logged (NOT to decompose -- closed). Persists
# per-item Y for every arm (res04_peritem.npz).
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
SH, EOH, EOT = 128006, 128007, 128009
FLOOR_STRIDE = 12 if SMOKE else 6
def log(*a): print(*a, flush=True)

def main():
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_contested.jsonl"), encoding="utf-8")]
    unc = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_uncontested.jsonl"), encoding="utf-8")]
    from make_stimuli import TEMPLATES
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import transformers
    log(f"[R4] model on {dev}; tf {transformers.__version__} n={len(stim)} ({time.time()-t0:.0f}s)")

    def segment(it):
        """Returns ids, si, ui (imperative spans), ksys, kusr (marker regions SH..EOH inclusive)."""
        imp_s = TEMPLATES[it["template_idx".format(T=it["target_sys"])
        imp_u = TEMPLATES[it["template_idx".format(T=it["target_usr"])
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]
        sh = [i for i, t in enumerate(ids) if t == SH]; eoh = [i for i, t in enumerate(ids) if t == EOH]
        ksys = list(range(sh[0], eoh[0] + 1)); kusr = list(range(sh[1], eoh[1] + 1))
        def span(imp):
            cs = text.index(imp); ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        return ids, span(imp_s), span(imp_u), ksys, kusr

    twin_g = defaultdict(dict); src_g = defaultdict(list)
    for i, it in enumerate(stim):
        twin_g[(it["template_idx"], it["filler_idx"], it["position"])][it["counterbalance" = i
        src_g[(it["template_idx"], it["position"], it["counterbalance"])].append(i)
    twin_of = {}
    for d in twin_g.values():
        if len(d) == 2: a, b = list(d.values()); twin_of[a] = b; twin_of[b] = a
    def source_of(i):
        it = stim[i]; c = [j for j in src_g[(it["template_idx"], it["position"], it["counterbalance"])] if j != i]
        return c[0] if c else None
    SEG = {i: segment(stim[i]) for i in range(len(stim))}

    def capture(i):
        ids, si, ui, ks, ku = SEG[i]; t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        return {L: {"s": hs[L][0, si, :].detach().clone(), "u": hs[L][0, ui, :].detach().clone(),
                    "ks": hs[L][0, ks, :].detach().clone(), "ku": hs[L][0, ku, :].detach().clone()} for L in LAYERS}

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
    def ysig(R, it): return R if it["target_sys"] == "DONE" else -R

    def build(i, cap, mapping):
        """mapping: list of (item_positions, source_key). None if any length mismatches."""
        for item_pos, key in mapping:
            if not item_pos or len(item_pos) != cap[LAYERS[0[key].shape[0]: return None
        repl = {}
        for L in LAYERS:
            pos = []; val = []
            for item_pos, key in mapping:
                pos += item_pos; val.append(cap[L][key])
            repl[L] = (torch.tensor(pos, dtype=torch.long, device=dev), torch.cat(val, 0).to(torch.bfloat16))
        return repl
    def shift_of(pairs):
        vals = [abs(np.mean(sp) - np.mean(ip)) for ip, sp in pairs if ip and sp]
        return float(np.mean(vals)) if vals else np.nan

    # usable: twin+source present, both spans present, span cross+same length match, marker cross length match.
    # (same-role marker match is guaranteed: identical role tokens.) One paired set for all arms.
    def usable(i):
        _, si, ui, ks, ku = SEG[i]; tw = twin_of.get(i); sc = source_of(i)
        if tw is None or sc is None or not si or not ui: return False
        _, tsi, tui, tks, tku = SEG[tw]; _, ssi, sui, sks, sku = SEG[sc]
        return (len(si) == len(tui) and len(ui) == len(tsi) and       # span cross
                len(si) == len(ssi) and len(ui) == len(sui) and       # span same
                len(ks) == len(tku) and len(ku) == len(tks) and       # marker cross
                len(ks) == len(sks) and len(ku) == len(sku))          # marker same
    use = [i for i in range(len(stim)) if usable(i)]
    if SMOKE: use = use[:40]
    log(f"[R4] usable={len(use)} skipped={len(stim)-len(use)} ({time.time()-t0:.0f}s)")

    # self-check: M (widest cross-role) must move item0
    i0 = use[0]; c0 = capture(twin_of[i0]); s0 = SEG[i0]
    rM0 = build(i0, c0, [(s0[3], "ku"), (s0[4], "ks"), (s0[1], "u"), (s0[2], "s")])
    yb0 = run(s0[0]); yM0 = run(s0[0], rM0)
    if abs(yM0 - yb0) < 1e-4:
        for h in handles: h.remove()
        raise SystemExit("SELFCHECK FAILED: markers+span cross-role did not move Y")
    log(f"[R4] SELFCHECK ok (item0 {yb0:+.3f}->{yM0:+.3f})")

    tmpl = np.array([stim[i]["template_idx"] for i in use])
    N = len(use)
    Yb = np.zeros(N); YS = np.zeros(N); YK = np.zeros(N); YM = np.zeros(N)
    YS2 = np.zeros(N); YK2 = np.zeros(N); YM2 = np.zeros(N)
    shS = []; shK = []; shM = []
    for n, i in enumerate(use):
        it = stim[i]; ids, si, ui, ks, ku = SEG[i]
        tw = twin_of[i]; sc = source_of(i)
        capt = capture(tw); caps = capture(sc)
        _, tsi, tui, tks, tku = SEG[tw]; _, ssi, sui, sks, sku = SEG[sc]
        Yb[n]  = ysig(run(ids), it)
        # cross-role (from twin): span<-opposite span, markers<-opposite markers
        YS[n]  = ysig(run(ids, build(i, capt, [(si, "u"), (ui, "s")])), it)
        YK[n]  = ysig(run(ids, build(i, capt, [(ks, "ku"), (ku, "ks")])), it)
        YM[n]  = ysig(run(ids, build(i, capt, [(ks, "ku"), (ku, "ks"), (si, "u"), (ui, "s")])), it)
        # same-role floor (from source): same role regions, foreign filler/context
        YS2[n] = ysig(run(ids, build(i, caps, [(si, "s"), (ui, "u")])), it)
        YK2[n] = ysig(run(ids, build(i, caps, [(ks, "ks"), (ku, "ku")])), it)
        YM2[n] = ysig(run(ids, build(i, caps, [(ks, "ks"), (ku, "ku"), (si, "s"), (ui, "u")])), it)
        shS.append(shift_of([(si, tui), (ui, tsi)]))
        shK.append(shift_of([(ks, tku), (ku, tks)]))
        shM.append(shift_of([(si, tui), (ui, tsi), (ks, tku), (ku, tks)]))
        if (n + 1) % 100 == 0: log(f"[R4] {n+1}/{N} ({time.time()-t0:.0f}s)")
    B = float(Yb.mean())
    log(f"[R4] B={B:+.4f} shifts S={np.nanmean(shS):.1f} K={np.nanmean(shK):.1f} M={np.nanmean(shM):.1f} ({time.time()-t0:.0f}s)")

    # persist per-item BEFORE bootstrap (recurring discard bug)
    np.savez(os.path.join(OUT, "res04_peritem_smoke.npz" if SMOKE else "res04_peritem.npz"),
             use=np.array(use), tmpl=tmpl, Yb=Yb, YS=YS, YK=YK, YM=YM, YS2=YS2, YK2=YK2, YM2=YM2,
             shS=np.array(shS), shK=np.array(shK), shM=np.array(shM), B=B)

    # ---- VOID (M extent; group unc BEFORE subsample) ----
    def unc_seg(it):
        try:
            imp = TEMPLATES[it["template_idx".format(T=it["target"])
            msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
            text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
            ids = enc["input_ids"]; offs = enc["offset_mapping"]
            sh = [i for i, t in enumerate(ids) if t == SH]; eoh = [i for i, t in enumerate(ids) if t == EOH]
            slot = 0 if it["slot"] == "system" else 1
            kk = list(range(sh[slot], eoh[slot] + 1))
            cs = text.index(imp); ce = cs + len(imp)
            sp = [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
            return ids, sp, kk
        except Exception:
            return None
    grp = defaultdict(list)
    for k, it in enumerate(unc): grp[(it["template_idx"], it["position"], it["slot"], it["target"])].append(k)
    def ucomply(ids, repl=None):
        STATE["repl"] = repl; t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lp = torch.log_softmax(model(input_ids=t, use_cache=False).logits[0, -1, :].float(), -1)
        STATE["repl"] = None
        return 1 if (lp[DONE] - lp[READY]) > 0 else 0
    uok = un = sok = sn = 0
    for k in range(0, len(unc), FLOOR_STRIDE):
        it = unc[k]; seg = unc_seg(it)
        if seg is None or not seg[1]: continue
        un += 1; uok += ucomply(seg[0])
        cand = [m for m in grp[(it["template_idx"], it["position"], it["slot"], it["target"])] if m != k]
        if not cand: continue
        ssg = unc_seg(unc[cand[0)
        if ssg is None or len(ssg[1]) != len(seg[1]) or len(ssg[2]) != len(seg[2]): continue
        t = torch.tensor([ssg[0, dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        repl = {}
        for L in LAYERS:
            pos = seg[2] + seg[1]
            val = torch.cat([hs[L][0, ssg[2], :], hs[L][0, ssg[1], :, 0).to(torch.bfloat16)
            repl[L] = (torch.tensor(pos, dtype=torch.long, device=dev), val)
        sn += 1; sok += ucomply(seg[0], repl)
    for h in handles: h.remove()
    floor_uns = uok / max(1, un); floor_steer = sok / max(1, sn) if sn else float("nan")
    thresh = 0.90 * floor_uns; VOID = bool(sn > 0 and floor_steer < thresh)
    log(f"[R4] floor: unsteered {floor_uns:.3f}(n={un}) steered {floor_steer:.3f}(n={sn}) VOID={VOID}")

    # ---- M + paired template-cluster bootstrap ----
    def per_t(a): return np.array([a[tmpl == t].mean() if (tmpl == t).any() else 0.0 for t in range(NTMPL)])
    ptB = per_t(Yb)
    ptS = per_t(YS - Yb); ptK = per_t(YK - Yb); ptM = per_t(YM - Yb)
    ptS2 = per_t(YS2 - Yb); ptK2 = per_t(YK2 - Yb); ptM2 = per_t(YM2 - Yb)
    def M_of(pt): return float(-pt.mean() / (2 * ptB.mean())) if abs(ptB.mean()) > 1e-9 else float("nan")
    MS, MK, MM = M_of(ptS), M_of(ptK), M_of(ptM)
    MS2, MK2, MM2 = M_of(ptS2), M_of(ptK2), M_of(ptM2)
    rng = np.random.default_rng(SEED)
    keys = ["S","K","M","S2","K2","M2","MM_minus_MS","additivity","MS_net","MK_net","MM_net"]
    boot = {k: np.empty(BOOT) for k in keys}
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL); den = 2 * ptB[pk].mean()
        if abs(den) < 1e-9:
            for k in keys: boot[k][b] = np.nan
            continue
        s  = -ptS[pk].mean()/den;  kk = -ptK[pk].mean()/den;  m  = -ptM[pk].mean()/den
        s2 = -ptS2[pk].mean()/den; k2 = -ptK2[pk].mean()/den; m2 = -ptM2[pk].mean()/den
        boot["S"][b]=s; boot["K"][b]=kk; boot["M"][b]=m; boot["S2"][b]=s2; boot["K2"][b]=k2; boot["M2"][b]=m2
        boot["MM_minus_MS"][b]=m-s; boot["additivity"][b]=m-(kk+s)
        boot["MS_net"][b]=s-s2; boot["MK_net"][b]=kk-k2; boot["MM_net"][b]=m-m2
    def ci(a): lo,hi=np.nanpercentile(a,[2.5,97.5]); return [float(lo),float(hi)]
    C = {k: ci(boot[k]) for k in keys}
    shSm, shKm, shMm = float(np.nanmean(shS)), float(np.nanmean(shK)), float(np.nanmean(shM))

    d_ext = MM - MS; d_add = MM - (MK + MS)
    if VOID: verdict = "VOID -- NOT a null"
    elif MM >= 0.85 and C["M"][0] > 0.75: verdict = "MARKERS+SPAN-NEAR-1 (accounts for ~the arbitration)"
    elif d_ext > 0.10 and C["MM_minus_MS"][0] > 0:
        verdict = "MARKERS-CARRY-MISSING-HALF (extent climbs; missing half rides on role markers; 0.462~0.471 = shared-extent artifact)"
    elif abs(d_ext) <= 0.08 and C["MM_minus_MS"][0] <= 0 <= C["MM_minus_MS"][1]:
        verdict = "EXTENT-RULED-OUT (markers add nothing beyond span; missing half NOT in block -> gen-position/composition)"
    else: verdict = "PARTIAL-EXTENT (report band)"
    # additivity annotation
    if C["additivity"][0] > 0: add_note = "INTERACTION (M >> K+S; marker works only when span agrees)"
    elif C["additivity"][0] <= 0 <= C["additivity"][1]: add_note = "ADDITIVE (K,S independent channels)"
    else: add_note = "SUB-ADDITIVE (M < K+S)"
    if abs(MK) < 0.05 and abs(d_ext) <= 0.08: add_note += " | MARKERS-CARRY-NOTHING (clean negative for structural-anchor)"

    out = {"prereg": "PREREG_RES04.md (re-locked markers+span 2026-09-21)", "SMOKE": SMOKE,
           "supersedes_lock": "3cea2712be34cf988ae6b514a83066f3283d4857729d89861d1f9ec843235cc4",
           "chained_to_RES02": "66ec4cee6f380fc9f33e308eb077fe73dbbc5eee94c163a21bc39a9809bb6cc5",
           "transformers": transformers.__version__, "B": B, "n_pairs": N, "n_skipped": len(stim) - N,
           "MS_span_cross": MS, "MS_ci": C["S"], "MK_marker_cross": MK, "MK_ci": C["K"],
           "MM_markerspan_cross": MM, "MM_ci": C["M"],
           "MS2_floor": MS2, "MK2_floor": MK2, "MM2_floor": MM2,
           "MM_minus_MS_extent": d_ext, "MM_minus_MS_ci": C["MM_minus_MS"],
           "additivity_MM_minus_KplusS": d_add, "additivity_ci": C["additivity"],
           "MS_net_of_floor": MS - MS2, "MS_net_ci": C["MS_net"],
           "MK_net_of_floor": MK - MK2, "MK_net_ci": C["MK_net"],
           "MM_net_of_floor": MM - MM2, "MM_net_ci": C["MM_net"],
           "shift_span": shSm, "shift_marker": shKm, "shift_markerspan": shMm,
           "floor_unsteered": floor_uns, "floor_steered": floor_steer, "VOID": VOID,
           "res02_span_reference": 0.462, "verdict": verdict, "additivity_note": add_note,
           "runtime_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "res04_arms_smoke.csv" if SMOKE else "res04_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["arm", "M", "ci_lo", "ci_hi", "pos_shift", "floor_M", "n_pairs", "VOID"])
        w.writerow(["span(S)", round(MS,5), round(C["S"][0],5), round(C["S"][1],5), round(shSm,2), round(MS2,5), N, VOID])
        w.writerow(["marker(K)", round(MK,5), round(C["K"][0],5), round(C["K"][1],5), round(shKm,2), round(MK2,5), N, VOID])
        w.writerow(["marker+span(M)", round(MM,5), round(C["M"][0],5), round(C["M"][1],5), round(shMm,2), round(MM2,5), N, VOID])
        w.writerow(["M_minus_S(extent)", round(d_ext,5), round(C["MM_minus_MS"][0],5), round(C["MM_minus_MS"][1],5), "", "", N, VOID])
        w.writerow(["additivity_M-(K+S)", round(d_add,5), round(C["additivity"][0],5), round(C["additivity"][1],5), "", "", N, VOID])
    fn = os.path.join(OUT, "res04_smoke.json" if SMOKE else "res04.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[R4] M_M-M_S={d_ext:+.4f}{C['MM_minus_MS']} (FIRST) | M_K={MK:+.4f}{C['K']} | "
        f"add={d_add:+.4f}{C['additivity']} | M_S={MS:+.4f} M_M={MM:+.4f} -> {verdict} :: {add_note}; wrote {fn}")

if __name__ == "__main__":
    main()
