#!/usr/bin/env python
# RES-03 -- position-import control: decompose RES-02's cross-role ceiling into provenance vs imported position.
# PREREG_RES03.md, chained RES-02 66ec4cee... Full-span residual replacement (all layers L8-31), 3 arms:
#  1 cross-role (provenance+position), P position-only (position-twin, same role/content, position flipped),
#  2 disruption (same-role/same-target/diff-filler). Per arm report the MEASURED abs token-position shift so the
#  magnitude-match is a number. M=-dY/(2B) signed by counterbalance, template-cluster bootstrap. VOID fixed
#  (group uncontested sources BEFORE subsampling).
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
    log(f"[R3] model on {dev}; tf {transformers.__version__} n={len(stim)} ({time.time()-t0:.0f}s)")

    def blocks_and_imp(it):
        imp_s = TEMPLATES[it["template_idx".format(T=it["target_sys"])
        imp_u = TEMPLATES[it["template_idx".format(T=it["target_usr"])
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]
        def span(imp):
            cs = text.index(imp); ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        return ids, span(imp_s), span(imp_u)

    twin_g = defaultdict(dict); postwin_g = defaultdict(dict); src_g = defaultdict(list)
    for i, it in enumerate(stim):
        twin_g[(it["template_idx"], it["filler_idx"], it["position"])][it["counterbalance" = i
        postwin_g[(it["template_idx"], it["filler_idx"], it["counterbalance"])][it["position" = i
        src_g[(it["template_idx"], it["position"], it["counterbalance"])].append(i)
    twin_of = {}; postwin_of = {}
    for d in twin_g.values():
        if len(d) == 2: a, b = d.values(); twin_of[a] = b; twin_of[b] = a
    for d in postwin_g.values():
        if len(d) == 2: a, b = d.values(); postwin_of[a] = b; postwin_of[b] = a
    def source_of(i):
        it = stim[i]; c = [j for j in src_g[(it["template_idx"], it["position"], it["counterbalance"])] if j != i]
        return c[0] if c else None

    SEG = {i: blocks_and_imp(stim[i]) for i in range(len(stim))}

    def capture(i):
        ids, si, ui = SEG[i]
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        return {L: {"s": hs[L][0, si, :].detach().clone(), "u": hs[L][0, ui, :].detach().clone()} for L in LAYERS}

    STATE = {"repl": None}; handles = []
    def make_hook(L):
        def hook(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            r = STATE["repl"]
            if r is not None and L in r:
                pos, val = r[L]; h[0, pos, :] = val
            return out
        return hook
    for L in LAYERS:
        handles.append(model.model.layers[L - 1].register_forward_hook(make_hook(L)))

    def run(ids, repl=None):
        STATE["repl"] = repl; t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lg = model(input_ids=t, use_cache=False).logits[0, -1, :].float()
        STATE["repl"] = None
        lp = torch.log_softmax(lg, -1); return float(lp[DONE] - lp[READY])
    def ysig(R, it): return R if it["target_sys"] == "DONE" else -R

    def repl_from(i, cap, cross):
        """cross=True: item sys<-src 'u', usr<-src 's' (role swapped). cross=False: sys<-src 's', usr<-src 'u'."""
        ids, si, ui = SEG[i]; repl = {}
        sk, uk = ("u", "s") if cross else ("s", "u")
        for L in LAYERS:
            pos = []; val = []
            if si and len(si) == cap[L][sk].shape[0]: pos += si; val.append(cap[L][sk])
            if ui and len(ui) == cap[L][uk].shape[0]: pos += ui; val.append(cap[L][uk])
            if pos: repl[L] = (torch.tensor(pos, dtype=torch.long, device=dev), torch.cat(val, 0).to(torch.bfloat16))
        return repl

    def pos_shift(i, j, cross):
        """mean |source-span mean pos - injection-site mean pos| over the two slots."""
        _, si, ui = SEG[i]; _, sj, uj = SEG[j]
        if cross: src_s, src_u = uj, sj    # item sys-site gets src user-span; usr-site gets src sys-span
        else:     src_s, src_u = sj, uj
        vals = []
        if si and src_s: vals.append(abs(np.mean(src_s) - np.mean(si)))
        if ui and src_u: vals.append(abs(np.mean(src_u) - np.mean(ui)))
        return float(np.mean(vals)) if vals else np.nan
    def spans_ok(i, j, cross):
        _, si, ui = SEG[i]; _, sj, uj = SEG[j]
        return (len(si) == len(uj) and len(ui) == len(sj)) if cross else (len(si) == len(sj) and len(ui) == len(uj))

    use = []
    for i in range(len(stim)):
        tw = twin_of.get(i); pw = postwin_of.get(i); sc = source_of(i)
        if tw is None or pw is None or sc is None: continue
        if not SEG[i][1] or not SEG[i][2]: continue
        if spans_ok(i, tw, True) and spans_ok(i, pw, False) and spans_ok(i, sc, False): use.append(i)
    if SMOKE: use = use[:40]
    n_skip = len(stim) - len(use)
    log(f"[R3] usable={len(use)} skipped={n_skip} ({time.time()-t0:.0f}s)")

    i0 = use[0]; yb0 = run(SEG[i0][0]); yt0 = run(SEG[i0][0], repl_from(i0, capture(twin_of[i0]), True))
    if abs(yt0 - yb0) < 1e-4:
        for h in handles: h.remove()
        raise SystemExit("SELFCHECK FAILED: cross-role did not move Y")
    log(f"[R3] SELFCHECK ok (item0 {yb0:+.3f}->{yt0:+.3f})")

    tmpl = np.array([stim[i]["template_idx"] for i in use])
    Yb = np.zeros(len(use)); Y1 = np.zeros(len(use)); YP = np.zeros(len(use)); Y2 = np.zeros(len(use))
    sh1 = []; shP = []; sh2 = []
    for n, i in enumerate(use):
        it = stim[i]; ids = SEG[i][0]
        Yb[n] = ysig(run(ids), it)
        Y1[n] = ysig(run(ids, repl_from(i, capture(twin_of[i]), True)), it);    sh1.append(pos_shift(i, twin_of[i], True))
        YP[n] = ysig(run(ids, repl_from(i, capture(postwin_of[i]), False)), it); shP.append(pos_shift(i, postwin_of[i], False))
        Y2[n] = ysig(run(ids, repl_from(i, capture(source_of(i)), False)), it);  sh2.append(pos_shift(i, source_of(i), False))
        if (n + 1) % 120 == 0: log(f"[R3] {n+1}/{len(use)} ({time.time()-t0:.0f}s)")
    B = float(Yb.mean()); log(f"[R3] B={B:+.4f} shifts: cross={np.nanmean(sh1):.1f} pos-only={np.nanmean(shP):.1f} disrupt={np.nanmean(sh2):.1f} ({time.time()-t0:.0f}s)")

    # ---- VOID (fixed: group full unc BEFORE subsampling) ----
    def unc_span(it):
        try:
            imp = TEMPLATES[it["template_idx".format(T=it["target"])
            msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
            text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
            ids = enc["input_ids"]; offs = enc["offset_mapping"]
            cs = text.index(imp); ce = cs + len(imp)
            return ids, [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
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
    test_idx = list(range(0, len(unc), FLOOR_STRIDE))
    uok = un = 0; sok = sn = 0
    for k in test_idx:
        it = unc[k]; seg = unc_span(it)
        if seg is None or not seg[1]: continue
        un += 1; uok += ucomply(seg[0])
        cand = [m for m in grp[(it["template_idx"], it["position"], it["slot"], it["target"])] if m != k]
        if not cand: continue
        ssg = unc_span(unc[cand[0)
        if ssg is None or len(ssg[1]) != len(seg[1]): continue
        t = torch.tensor([ssg[0, dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        repl = {L: (torch.tensor(seg[1], dtype=torch.long, device=dev), hs[L][0, ssg[1], :].to(torch.bfloat16)) for L in LAYERS}
        sn += 1; sok += ucomply(seg[0], repl)
    for h in handles: h.remove()
    floor_uns = uok / max(1, un); floor_steer = sok / max(1, sn) if sn else float("nan")
    thresh = 0.90 * floor_uns; VOID = bool(sn > 0 and floor_steer < thresh)
    log(f"[R3] floor: unsteered {floor_uns:.3f}(n={un}) steered {floor_steer:.3f}(n={sn}) VOID={VOID}")

    def per_t(a): return np.array([a[tmpl == t].mean() if (tmpl == t).any() else 0.0 for t in range(NTMPL)])
    ptB = per_t(Yb); pt1 = per_t(Y1 - Yb); ptP = per_t(YP - Yb); pt2 = per_t(Y2 - Yb)
    def M_of(pt): return float(-pt.mean() / (2 * ptB.mean())) if abs(ptB.mean()) > 1e-9 else float("nan")
    M1, MP, M2 = M_of(pt1), M_of(ptP), M_of(pt2)
    rng = np.random.default_rng(SEED)
    B1 = np.empty(BOOT); BP = np.empty(BOOT); B2 = np.empty(BOOT); BdP = np.empty(BOOT); Bd2 = np.empty(BOOT)
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL); den = 2 * ptB[pk].mean()
        if abs(den) < 1e-9: B1[b]=BP[b]=B2[b]=BdP[b]=Bd2[b]=np.nan; continue
        m1=-pt1[pk].mean()/den; mp=-ptP[pk].mean()/den; m2=-pt2[pk].mean()/den
        B1[b]=m1; BP[b]=mp; B2[b]=m2; BdP[b]=m1-mp; Bd2[b]=m1-m2
    def ci(a): lo,hi=np.nanpercentile(a,[2.5,97.5]); return [float(lo),float(hi)]
    c1,cP,c2,cdP,cd2 = ci(B1),ci(BP),ci(B2),ci(BdP),ci(Bd2)
    sh1m, shPm, sh2m = float(np.nanmean(sh1)), float(np.nanmean(shP)), float(np.nanmean(sh2))

    # reading (PREREG §4)
    shift_ok = shPm >= 0.6 * sh1m
    if VOID:
        verdict = "VOID -- NOT a null"
    elif not shift_ok:
        verdict = f"POSITION-UNDER-TESTED (pos-only shift {shPm:.1f} < 0.6*cross shift {sh1m:.1f}); M_P={MP:+.3f} but inconclusive on position"
    elif abs(MP) < 0.05 or (cP[0] <= 0 <= cP[1]):
        verdict = "PROVENANCE (position-only ~0 at matched shift -> RES-02's ~0.46 is provenance, position-independent)"
    elif MP >= M1 - 0.05:
        verdict = "POSITION-ARTIFACT (position-only ~= cross-role -> RES-02 effect was position; provenance ~0)"
    else:
        verdict = f"BOTH (provenance ~ M1-M_P = {M1-MP:+.3f}; position ~ M_P = {MP:+.3f})"

    out = {"prereg": "PREREG_RES03.md", "SMOKE": SMOKE,
           "chained_to_RES02": "66ec4cee6f380fc9f33e308eb077fe73dbbc5eee94c163a21bc39a9809bb6cc5",
           "transformers": transformers.__version__, "B": B, "n_pairs": len(use), "n_skipped": n_skip,
           "M1_cross_role": M1, "M1_ci": c1, "MP_position_only": MP, "MP_ci": cP,
           "M2_disruption": M2, "M2_ci": c2,
           "M1_minus_MP_provenance": M1 - MP, "M1_minus_MP_ci": cdP,
           "M1_minus_M2": M1 - M2, "M1_minus_M2_ci": cd2,
           "shift_cross": sh1m, "shift_pos_only": shPm, "shift_disrupt": sh2m, "shift_ok": shift_ok,
           "floor_unsteered": floor_uns, "floor_steered": floor_steer, "VOID": VOID, "verdict": verdict,
           "runtime_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "res03_arms_smoke.csv" if SMOKE else "res03_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["arm", "M", "ci_lo", "ci_hi", "pos_shift", "n_pairs", "VOID"])
        w.writerow(["cross_role", round(M1,5), round(c1[0],5), round(c1[1],5), round(sh1m,2), len(use), VOID])
        w.writerow(["position_only", round(MP,5), round(cP[0],5), round(cP[1],5), round(shPm,2), len(use), VOID])
        w.writerow(["disruption", round(M2,5), round(c2[0],5), round(c2[1],5), round(sh2m,2), len(use), VOID])
        w.writerow(["cross_minus_posonly(prov)", round(M1-MP,5), round(cdP[0],5), round(cdP[1],5), "", len(use), VOID])
    fn = os.path.join(OUT, "res03_smoke.json" if SMOKE else "res03.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[R3] M1={M1:+.4f}{c1} MP={MP:+.4f}{cP} M1-MP={M1-MP:+.4f}{cdP} shifts x={sh1m:.1f}/p={shPm:.1f} -> {verdict}; wrote {fn}")

if __name__ == "__main__":
    main()
