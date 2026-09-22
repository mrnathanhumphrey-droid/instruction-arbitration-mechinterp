#!/usr/bin/env python
# RES-03b -- within-arm position dose-response for RES-03 Arm P (position-only). PREREG in RES-03 lineage.
# RES-03 saved only aggregate M_P; per-item shift/dY were discarded. This re-runs baseline + Arm P ONLY,
# PERSISTS per-item (shift, dY_P, Yb, template) to npz, and fits M_P vs its OWN per-item position shift within
# the arm (templates differ in length -> the early/late shift varies item to item). Replaces the single-point +
# near-linearity assumption with a measured curve. Chained to RES-03 befaa3ca... No M2/content point used.
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
    log(f"[R3b] model on {dev}; tf {transformers.__version__} n={len(stim)} ({time.time()-t0:.0f}s)")

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

    postwin_g = defaultdict(dict)
    for i, it in enumerate(stim):
        postwin_g[(it["template_idx"], it["filler_idx"], it["counterbalance"])][it["position" = i
    postwin_of = {}
    for d in postwin_g.values():
        if len(d) == 2: a, b = d.values(); postwin_of[a] = b; postwin_of[b] = a
    SEG = {i: blocks_and_imp(stim[i]) for i in range(len(stim))}

    def capture(i):
        ids, si, ui = SEG[i]; t = torch.tensor([ids], dtype=torch.long, device=dev)
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
    for L in LAYERS: handles.append(model.model.layers[L - 1].register_forward_hook(make_hook(L)))
    def run(ids, repl=None):
        STATE["repl"] = repl; t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lg = model(input_ids=t, use_cache=False).logits[0, -1, :].float()
        STATE["repl"] = None
        lp = torch.log_softmax(lg, -1); return float(lp[DONE] - lp[READY])
    def ysig(R, it): return R if it["target_sys"] == "DONE" else -R
    def repl_posonly(i, cap):   # same role: item sys<-src sys, usr<-src usr
        ids, si, ui = SEG[i]; repl = {}
        for L in LAYERS:
            pos = []; val = []
            if si and len(si) == cap[L]["s"].shape[0]: pos += si; val.append(cap[L]["s"])
            if ui and len(ui) == cap[L]["u"].shape[0]: pos += ui; val.append(cap[L]["u"])
            if pos: repl[L] = (torch.tensor(pos, dtype=torch.long, device=dev), torch.cat(val, 0).to(torch.bfloat16))
        return repl
    def pos_shift(i, j):
        _, si, ui = SEG[i]; _, sj, uj = SEG[j]; vals = []
        if si and sj: vals.append(abs(np.mean(sj) - np.mean(si)))
        if ui and uj: vals.append(abs(np.mean(uj) - np.mean(ui)))
        return float(np.mean(vals)) if vals else np.nan

    use = []
    for i in range(len(stim)):
        pw = postwin_of.get(i)
        if pw is None or not SEG[i][1] or not SEG[i][2]: continue
        _, si, ui = SEG[i]; _, sj, uj = SEG[pw]
        if len(si) == len(sj) and len(ui) == len(uj): use.append(i)
    if SMOKE: use = use[:60]
    log(f"[R3b] usable={len(use)} ({time.time()-t0:.0f}s)")

    tmpl = np.array([stim[i]["template_idx"] for i in use])
    Yb = np.zeros(len(use)); YP = np.zeros(len(use)); shP = np.zeros(len(use))
    for n, i in enumerate(use):
        it = stim[i]; ids = SEG[i][0]
        Yb[n] = ysig(run(ids), it)
        YP[n] = ysig(run(ids, repl_posonly(i, capture(postwin_of[i]))), it)
        shP[n] = pos_shift(i, postwin_of[i])
        if (n + 1) % 150 == 0: log(f"[R3b] {n+1}/{len(use)} ({time.time()-t0:.0f}s)")
    for h in handles: h.remove()
    B = float(Yb.mean()); dP = YP - Yb; e = -dP / (2 * B)     # per-item position-only M contribution
    np.savez_compressed(os.path.join(OUT, "res03b_peritem_smoke.npz" if SMOKE else "res03b_peritem.npz"),
                        Yb=Yb, YP=YP, dP=dP, e=e, shift=shP, tmpl=tmpl, item=np.array(use), B=B)
    log(f"[R3b] B={B:+.4f} shift[min={shP.min():.1f} med={np.median(shP):.1f} max={shP.max():.1f}] mean_e={e.mean():+.4f} ({time.time()-t0:.0f}s)")

    # ---- within-arm dose-response ----
    def M_boot(mask):
        idx = np.where(mask)[0]
        if len(idx) < 5: return (float("nan"), [float("nan"), float("nan")], len(idx))
        tm = tmpl[idx]; ee = e[idx]
        pt = np.array([ee[tm == t].mean() if (tm == t).any() else np.nan for t in range(NTMPL)])
        M = float(np.nanmean(pt)); r = np.random.default_rng(SEED); bs = np.empty(BOOT)
        uu = np.unique(tm)
        for b in range(BOOT):
            pk = r.choice(uu, len(uu), replace=True)
            bs[b] = np.nanmean([ee[tm == t].mean() for t in pk])
        lo, hi = np.nanpercentile(bs, [2.5, 97.5]); return (M, [float(lo), float(hi)], len(idx))
    # quartile bins by shift
    qs = np.quantile(shP, [0, 0.25, 0.5, 0.75, 1.0])
    bins = []
    for a, b in zip(qs[:-1], qs[1:]):
        m = (shP >= a) & (shP <= b if b == qs[-1] else shP < b)
        M, ci, n = M_boot(m)
        bins.append({"shift_lo": float(a), "shift_hi": float(b), "shift_mean": float(shP[m].mean()) if m.any() else None,
                     "M": M, "ci": ci, "n": n})
        log(f"[R3b] bin [{a:.1f},{b:.1f}] shift_mean={shP[m].mean() if m.any() else float('nan'):.1f} M={M:+.4f} CI{ci} n={n}")
    # OLS slope of e on shift, cluster-boot by template
    def ols(x, y):
        A = np.vstack([x, np.ones_like(x)]).T
        return np.linalg.lstsq(A, y, rcond=None)[0]   # slope, intercept
    slope, icpt = ols(shP, e)
    r2 = np.random.default_rng(SEED + 7); sl = np.empty(BOOT); uu = np.unique(tmpl)
    for b in range(BOOT):
        pk = r2.choice(uu, len(uu), replace=True)
        idx = np.concatenate([np.where(tmpl == t)[0] for t in pk])
        s, _ = ols(shP[idx], e[idx]); sl[b] = s
    sl_lo, sl_hi = np.nanpercentile(sl, [2.5, 97.5])
    CROSS_SHIFT = 23.3   # RES-03 cross-role shift
    PROV = 0.414         # RES-03 provenance estimate to compare extrapolation against
    extrap_through_origin = float(slope * CROSS_SHIFT)         # if position ~ linear-through-origin
    extrap_with_icpt = float(icpt + slope * CROSS_SHIFT)
    log(f"[R3b] slope={slope:+.5f}/tok CI[{sl_lo:+.5f},{sl_hi:+.5f}] icpt={icpt:+.4f} "
        f"extrap@{CROSS_SHIFT}: origin={extrap_through_origin:+.3f} w/icpt={extrap_with_icpt:+.3f}")

    # reading: is near-linearity supported (position minor even extrapolated) or steep?
    hi_q_M = bins[-1]["M"]; lo_q_M = bins[0]["M"]
    if not np.isfinite(slope):
        verdict = "INCONCLUSIVE"
    elif max(extrap_through_origin, extrap_with_icpt) < 0.20 and (hi_q_M < 0.20):
        verdict = "NEAR-LINEAR-SHALLOW (position minor even extrapolated to cross shift; RES-03 (a) stands on measurement)"
    elif max(extrap_through_origin, extrap_with_icpt) >= 0.30 or hi_q_M >= 0.30:
        verdict = "STEEP-WITHIN-ARM (position climbs with shift; magnitude-matched control (b) warranted)"
    else:
        verdict = "INTERMEDIATE (extrapolation ambiguous; report band)"

    M_P_agg = M_boot(np.ones(len(use), bool))[0]
    out = {"prereg": "RES-03 lineage (within-arm dose-response addendum)", "SMOKE": SMOKE,
           "chained_to_RES03": "befaa3ca84c50f9a67031808314f5322c0ded026a8304ac06040a4b3c939be5b",
           "B": B, "n": len(use), "M_P_aggregate": float(M_P_agg),
           "shift_min": float(shP.min()), "shift_med": float(np.median(shP)), "shift_max": float(shP.max()),
           "quartile_bins": bins, "slope_per_tok": float(slope), "slope_ci": [float(sl_lo), float(sl_hi)],
           "intercept": float(icpt), "cross_shift": CROSS_SHIFT,
           "extrap_origin_at_cross": extrap_through_origin, "extrap_icpt_at_cross": extrap_with_icpt,
           "provenance_ref": PROV, "verdict": verdict, "runtime_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "res03b_dose_smoke.csv" if SMOKE else "res03b_dose.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["shift_lo", "shift_hi", "shift_mean", "M", "ci_lo", "ci_hi", "n"])
        for bn in bins:
            w.writerow([round(bn["shift_lo"], 2), round(bn["shift_hi"], 2),
                        round(bn["shift_mean"], 2) if bn["shift_mean"] is not None else "",
                        round(bn["M"], 5), round(bn["ci"][0], 5), round(bn["ci"][1], 5), bn["n")
    fn = os.path.join(OUT, "res03b_smoke.json" if SMOKE else "res03b.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[R3b] slope={slope:+.5f} extrap@cross={extrap_through_origin:+.3f}/{extrap_with_icpt:+.3f} -> {verdict}; wrote {fn}")

if __name__ == "__main__":
    main()
