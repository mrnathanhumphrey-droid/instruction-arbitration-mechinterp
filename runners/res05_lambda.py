#!/usr/bin/env python
# RES-05 -- is the missing half SUMMARIZED at the generation position, or COMPOSED? PREREG_RES05.md, chained
# RES-04 e1f1c6ea... Single-position (readout, idx -1) single-LAYER patch, layer sweep L in {8,12,16,20,24,28,31}:
#   G_cross(L): item gen-pos residual @L <- counterbalanced TWIN gen-pos residual @L (opposite role)
#   G_floor(L): item gen-pos residual @L <- same-role different-filler SOURCE gen-pos residual @L (the FLOOR)
# net_L = M[G_cross]-M[G_floor] is the ONLY interpretable quantity (tautology gradient); raw shows the gradient.
# L31 = tautology anchor (raw M~1). Combined = RES-04 markers+span (all L) + gen-pos @L16, cross + same-role floor.
# In-run span-only baseline S (RES-02/04 recap). VOID @L16 gen-pos same-content, group-before-subsample.
# M=-dY/(2B) signed by counterbalance, template-cluster PAIRED bootstrap. Report net-by-layer FIRST (L31 anchor +
# M_S in the same table), then combined. Per-item persisted. Position shift logged, NOT decomposed.
import os, json, time, csv
import numpy as np, torch
from collections import defaultdict
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
LAYERS = list(range(8, 32))
SWEEP = [8, 12, 16, 20, 24, 28, 31]
COMB_L = 16
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
    log(f"[R5] model on {dev}; tf {transformers.__version__} n={len(stim)} sweep={SWEEP} ({time.time()-t0:.0f}s)")

    def segment(it):
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
        return ids, span(imp_s), span(imp_u), ksys, kusr, len(ids) - 1  # gen pos = last idx

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
        ids, si, ui, ks, ku, gp = SEG[i]; t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        return {L: {"s": hs[L][0, si, :].detach().clone(), "u": hs[L][0, ui, :].detach().clone(),
                    "ks": hs[L][0, ks, :].detach().clone(), "ku": hs[L][0, ku, :].detach().clone(),
                    "g": hs[L][0, -1:, :].detach().clone()} for L in LAYERS}

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

    def gen_repl(gp, cap, L):
        return {L: (torch.tensor([gp], dtype=torch.long, device=dev), cap[L]["g"].to(torch.bfloat16))}
    def build_ms(i, cap):  # RES-04 M: all-layer markers+span cross-role. None if length mismatch.
        _, si, ui, ks, ku, _ = SEG[i]; mapping = [(ks, "ku"), (ku, "ks"), (si, "u"), (ui, "s")]
        for item_pos, key in mapping:
            if not item_pos or len(item_pos) != cap[LAYERS[0[key].shape[0]: return None
        repl = {}
        for L in LAYERS:
            pos = []; val = []
            for item_pos, key in mapping: pos += item_pos; val.append(cap[L][key])
            repl[L] = (torch.tensor(pos, dtype=torch.long, device=dev), torch.cat(val, 0).to(torch.bfloat16))
        return repl
    def build_ms_same(i, cap):  # same-role markers+span from source
        _, si, ui, ks, ku, _ = SEG[i]; mapping = [(ks, "ks"), (ku, "ku"), (si, "s"), (ui, "u")]
        for item_pos, key in mapping:
            if not item_pos or len(item_pos) != cap[LAYERS[0[key].shape[0]: return None
        repl = {}
        for L in LAYERS:
            pos = []; val = []
            for item_pos, key in mapping: pos += item_pos; val.append(cap[L][key])
            repl[L] = (torch.tensor(pos, dtype=torch.long, device=dev), torch.cat(val, 0).to(torch.bfloat16))
        return repl
    def add_gen(repl, gp, cap, L):  # add gen-pos to an existing all-layer repl at layer L
        pos, val = repl[L]
        repl[L] = (torch.cat([pos, torch.tensor([gp], dtype=torch.long, device=dev)]),
                   torch.cat([val, cap[L]["g"].to(torch.bfloat16)], 0))
        return repl
    def build_span(i, cap):  # in-run span-only cross-role reference (RES-02)
        _, si, ui, _, _, _ = SEG[i]; mapping = [(si, "u"), (ui, "s")]
        for item_pos, key in mapping:
            if not item_pos or len(item_pos) != cap[LAYERS[0[key].shape[0]: return None
        repl = {}
        for L in LAYERS:
            pos = []; val = []
            for item_pos, key in mapping: pos += item_pos; val.append(cap[L][key])
            repl[L] = (torch.tensor(pos, dtype=torch.long, device=dev), torch.cat(val, 0).to(torch.bfloat16))
        return repl

    # usable: twin+source present, spans present, span cross+same length match (for S + combined)
    def usable(i):
        _, si, ui, ks, ku, _ = SEG[i]; tw = twin_of.get(i); sc = source_of(i)
        if tw is None or sc is None or not si or not ui: return False
        _, tsi, tui, tks, tku, _ = SEG[tw]; _, ssi, sui, sks, sku, _ = SEG[sc]
        return (len(si) == len(tui) and len(ui) == len(tsi) and
                len(si) == len(ssi) and len(ui) == len(sui) and
                len(ks) == len(tku) and len(ku) == len(tks) and
                len(ks) == len(sks) and len(ku) == len(sku))
    use = [i for i in range(len(stim)) if usable(i)]
    if SMOKE: use = use[:40]
    log(f"[R5] usable={len(use)} skipped={len(stim)-len(use)} ({time.time()-t0:.0f}s)")

    # self-check: L31 gen-pos cross-role (tautology) must move item0
    i0 = use[0]; c0 = capture(twin_of[i0]); gp0 = SEG[i0][5]
    yb0 = run(SEG[i0][0]); y31 = run(SEG[i0][0], gen_repl(gp0, c0, 31))
    if abs(y31 - yb0) < 1e-4:
        for h in handles: h.remove()
        raise SystemExit("SELFCHECK FAILED: L31 gen-pos cross-role did not move Y")
    log(f"[R5] SELFCHECK ok (item0 {yb0:+.3f}->L31gen {y31:+.3f})")

    tmpl = np.array([stim[i]["template_idx"] for i in use]); N = len(use)
    Yb = np.zeros(N); YS = np.zeros(N)
    Ycross = {L: np.zeros(N) for L in SWEEP}; Yfloor = {L: np.zeros(N) for L in SWEEP}
    Ycomb = np.zeros(N); YcombF = np.zeros(N)
    shC = []; shF = []
    for n, i in enumerate(use):
        it = stim[i]; ids, si, ui, ks, ku, gp = SEG[i]
        tw = twin_of[i]; sc = source_of(i)
        capt = capture(tw); caps = capture(sc)
        gpt = SEG[tw][5]; gps = SEG[sc][5]
        Yb[n] = ysig(run(ids), it)
        YS[n] = ysig(run(ids, build_span(i, capt)), it)
        for L in SWEEP:
            Ycross[L][n] = ysig(run(ids, gen_repl(gp, capt, L)), it)
            Yfloor[L][n] = ysig(run(ids, gen_repl(gp, caps, L)), it)
        # combined: markers+span (all L) cross + gen@L16 cross ; floor = same-role analog
        rc = build_ms(i, capt); rc = add_gen(rc, gp, capt, COMB_L)
        rf = build_ms_same(i, caps); rf = add_gen(rf, gp, caps, COMB_L)
        Ycomb[n] = ysig(run(ids, rc), it); YcombF[n] = ysig(run(ids, rf), it)
        shC.append(abs(gpt - gp)); shF.append(abs(gps - gp))
        if (n + 1) % 60 == 0: log(f"[R5] {n+1}/{N} ({time.time()-t0:.0f}s)")
    B = float(Yb.mean())
    log(f"[R5] B={B:+.4f} gen-shift cross={np.mean(shC):.1f} floor={np.mean(shF):.1f} ({time.time()-t0:.0f}s)")

    np.savez(os.path.join(OUT, "res05_peritem_smoke.npz" if SMOKE else "res05_peritem.npz"),
             use=np.array(use), tmpl=tmpl, Yb=Yb, YS=YS, Ycomb=Ycomb, YcombF=YcombF,
             shC=np.array(shC), shF=np.array(shF), B=B, sweep=np.array(SWEEP),
             **{f"Ycross_{L}": Ycross[L] for L in SWEEP}, **{f"Yfloor_{L}": Yfloor[L] for L in SWEEP})

    # ---- VOID @ L16 gen-pos same-content (group before subsample) ----
    def unc_seg(it):
        try:
            msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
            text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            ids = tok(text, add_special_tokens=False)["input_ids"]
            return ids, len(ids) - 1
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
        if seg is None: continue
        un += 1; uok += ucomply(seg[0])
        cand = [m for m in grp[(it["template_idx"], it["position"], it["slot"], it["target"])] if m != k]
        if not cand: continue
        ssg = unc_seg(unc[cand[0)
        if ssg is None: continue
        t = torch.tensor([ssg[0, dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        repl = {COMB_L: (torch.tensor([seg[1, dtype=torch.long, device=dev), hs[COMB_L][0, -1:, :].to(torch.bfloat16))}
        sn += 1; sok += ucomply(seg[0], repl)
    for h in handles: h.remove()
    floor_uns = uok / max(1, un); floor_steer = sok / max(1, sn) if sn else float("nan")
    thresh = 0.90 * floor_uns; VOID = bool(sn > 0 and floor_steer < thresh)
    log(f"[R5] VOID floor: unsteered {floor_uns:.3f}(n={un}) steered {floor_steer:.3f}(n={sn}) VOID={VOID}")

    # ---- M + paired template-cluster bootstrap ----
    def per_t(a): return np.array([a[tmpl == t].mean() if (tmpl == t).any() else 0.0 for t in range(NTMPL)])
    ptB = per_t(Yb); ptS = per_t(YS - Yb)
    ptC = {L: per_t(Ycross[L] - Yb) for L in SWEEP}; ptF = {L: per_t(Yfloor[L] - Yb) for L in SWEEP}
    ptComb = per_t(Ycomb - Yb); ptCombF = per_t(YcombF - Yb)
    def M_of(pt): return float(-pt.mean() / (2 * ptB.mean())) if abs(ptB.mean()) > 1e-9 else float("nan")
    MS = M_of(ptS)
    Mc = {L: M_of(ptC[L]) for L in SWEEP}; Mf = {L: M_of(ptF[L]) for L in SWEEP}
    net = {L: Mc[L] - Mf[L] for L in SWEEP}
    Mcomb = M_of(ptComb); McombF = M_of(ptCombF); comb_net = Mcomb - McombF

    rng = np.random.default_rng(SEED)
    bMS = np.empty(BOOT)
    bnet = {L: np.empty(BOOT) for L in SWEEP}; bnetmS = {L: np.empty(BOOT) for L in SWEEP}
    bcross = {L: np.empty(BOOT) for L in SWEEP}
    bcomb = np.empty(BOOT); bcombnet = np.empty(BOOT)
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL); den = 2 * ptB[pk].mean()
        if abs(den) < 1e-9:
            bMS[b] = bcomb[b] = bcombnet[b] = np.nan
            for L in SWEEP: bnet[L][b] = bnetmS[L][b] = bcross[L][b] = np.nan
            continue
        ms = -ptS[pk].mean() / den; bMS[b] = ms
        for L in SWEEP:
            mc = -ptC[L][pk].mean() / den; mf = -ptF[L][pk].mean() / den
            bcross[L][b] = mc; bnet[L][b] = mc - mf; bnetmS[L][b] = (mc - mf) - ms
        mcb = -ptComb[pk].mean() / den; mcbf = -ptCombF[pk].mean() / den
        bcomb[b] = mcb; bcombnet[b] = mcb - mcbf
    def ci(a): lo, hi = np.nanpercentile(a, [2.5, 97.5]); return [float(lo), float(hi)]
    cMS = ci(bMS)
    cnet = {L: ci(bnet[L]) for L in SWEEP}; cnetmS = {L: ci(bnetmS[L]) for L in SWEEP}
    ccross = {L: ci(bcross[L]) for L in SWEEP}
    ccomb = ci(bcomb); ccombnet = ci(bcombnet)

    # ---- mechanical verdict ----
    mid = [L for L in SWEEP if L <= 20]
    summarized = [L for L in mid if (net[L] - MS) > 0.10 and cnetmS[L][0] > 0]
    late_rise = (net[31] - max(net[L] for L in mid)) > 0.10
    if VOID:
        verdict = "VOID -- NOT a null"
    elif summarized:
        verdict = f"SUMMARIZED-AT-GEN-POSITION (net>>span at mid-stack L={summarized}; missing half localized there)"
    elif late_rise:
        verdict = "COMPOSITION-BY-ELIMINATION (net flat at L<=20, rises only into the tautology gradient; no single-position summary)"
    else:
        verdict = "PARTIAL/AMBIGUOUS (net neither clears span at mid-stack nor shows a clean tautology-only rise; report band)"
    if comb_net >= 0.80 and ccombnet[0] > 0.80: comb_note = "COMBINED ACCOUNTING CLOSES (net~1)"
    elif ccombnet[1] < 0.80: comb_note = "COMBINED BELOW 1 (carried by neither block nor readout -> intermediate positions)"
    else: comb_note = "COMBINED intermediate (report band)"

    out = {"prereg": "PREREG_RES05.md", "SMOKE": SMOKE,
           "chained_to_RES04": "e1f1c6ea6741ec5fa7d76726e02679d3cb697c184259187d6b3f9a6feeba842b",
           "transformers": transformers.__version__, "B": B, "n_pairs": N, "n_skipped": len(stim) - N,
           "sweep": SWEEP, "MS_span_baseline": MS, "MS_ci": cMS,
           "M_cross_by_L": {L: Mc[L] for L in SWEEP}, "M_cross_ci_by_L": {L: ccross[L] for L in SWEEP},
           "M_floor_by_L": {L: Mf[L] for L in SWEEP},
           "net_by_L": {L: net[L] for L in SWEEP}, "net_ci_by_L": {L: cnet[L] for L in SWEEP},
           "net_minus_MS_by_L": {L: net[L] - MS for L in SWEEP}, "net_minus_MS_ci_by_L": {L: cnetmS[L] for L in SWEEP},
           "L31_anchor_raw": Mc[31], "L31_anchor_ci": ccross[31],
           "combined_raw": Mcomb, "combined_raw_ci": ccomb, "combined_floor": McombF,
           "combined_net": comb_net, "combined_net_ci": ccombnet, "combined_L": COMB_L,
           "gen_shift_cross": float(np.mean(shC)), "gen_shift_floor": float(np.mean(shF)),
           "floor_unsteered": floor_uns, "floor_steered": floor_steer, "VOID": VOID,
           "verdict": verdict, "combined_note": comb_note, "runtime_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "res05_arms_smoke.csv" if SMOKE else "res05_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc)
        w.writerow(["layer", "M_cross_raw", "M_floor_raw", "net", "net_ci_lo", "net_ci_hi",
                    "net_minus_MS", "netmS_ci_lo", "netmS_ci_hi", "is_L31_anchor"])
        for L in SWEEP:
            w.writerow([L, round(Mc[L],5), round(Mf[L],5), round(net[L],5), round(cnet[L][0],5), round(cnet[L][1],5),
                        round(net[L]-MS,5), round(cnetmS[L][0],5), round(cnetmS[L][1],5), "YES" if L==31 else ""])
        w.writerow(["span_baseline(S)", round(MS,5), "", "", round(cMS[0],5), round(cMS[1],5), "", "", "", ""])
        w.writerow([f"combined(msp+genL{COMB_L})", round(Mcomb,5), round(McombF,5), round(comb_net,5),
                    round(ccombnet[0],5), round(ccombnet[1],5), "", "", "", ""])
    fn = os.path.join(OUT, "res05_smoke.json" if SMOKE else "res05.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[R5] MS={MS:+.4f} | net by L: " + " ".join(f"{L}:{net[L]:+.3f}" for L in SWEEP) +
        f" | L31anchor(raw)={Mc[31]:+.3f} | comb_net={comb_net:+.3f}{ccombnet} -> {verdict} :: {comb_note}; wrote {fn}")

if __name__ == "__main__":
    main()
