#!/usr/bin/env python
# OPX-01 (revised) -- do the two imperative spans ADDITIVELY determine Y, or is the remainder interactional?
# Extends RES-02/RES-06 harness (Llama-3.1-8B, stimuli_contested, cross-role residual overwrite L8-31, cb-flip twin).
# Cells (span positions only; twin activations; single-token DONE/READY -> spans always length-aligned):
#   A_sys  same-index, sys span only : item si <- twin si
#   A_usr  same-index, usr span only : item ui <- twin ui
#   B_sys  cross-index, sys span only: item si <- twin ui
#   B_usr  cross-index, usr span only: item ui <- twin si
#   EXCH   cross-index, two-sided    : item si<-twin ui, ui<-twin si   (RES-02 Arm1 anchor, ~0.462)
#   CONSTR same-index, two-sided     : item si<-twin si, ui<-twin ui   (become-the-twin, ~1.0 BY CONSTRUCTION -- pipeline
#          check ONLY, NEVER evidence)
# PRIMARY: gap = 1 - (M(A_sys)+M(A_usr)). gap~0 => additive (spans determine Y; exchange 0.46 is an operator deficit).
#          gap large => sub-additive => the remainder is INTERACTIONAL (carried by the between-block comparison, not either span).
import os, json, time
import numpy as np, torch
from collections import defaultdict
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
LAYERS = list(range(8, 32))
DONE, READY = 71496, 46678
NTMPL = 30; BOOT = 300 if SMOKE else 5000; SEED = 20260925
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
    log(f"[OPX] model on {dev}; tf {transformers.__version__} L{LAYERS[0]}..{LAYERS[-1]} n={len(stim)} ({time.time()-t0:.0f}s)")

    def seg(it):
        imp_s = TEMPLATES[it["template_idx"]].format(T=it["target_sys"])
        imp_u = TEMPLATES[it["template_idx"]].format(T=it["target_usr"])
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]
        def span(imp):
            cs = text.index(imp); ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        return ids, span(imp_s), span(imp_u)

    twin_g = defaultdict(dict); src_g = defaultdict(list)
    for i, it in enumerate(stim):
        twin_g[(it["template_idx"], it["filler_idx"], it["position"])][it["counterbalance"]] = i
        src_g[(it["template_idx"], it["position"], it["counterbalance"])].append(i)
    twin_of = {}
    for d in twin_g.values():
        if len(d) == 2:
            a, b = list(d.values()); twin_of[a] = b; twin_of[b] = a

    SEG = {i: seg(stim[i]) for i in range(len(stim))}

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
        STATE["repl"] = repl
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lp = torch.log_softmax(model(input_ids=t, use_cache=False).logits[0, -1, :].float(), -1)
        STATE["repl"] = None
        return float(lp[DONE] - lp[READY]), float(torch.exp(lp[DONE]) + torch.exp(lp[READY]))
    def ysig(R, it): return R if it["target_sys"] == "DONE" else -R

    def rp(i, ct, cell):
        """build repl dict for a cell. positions are item's own; values from twin capture ct."""
        ids, si, ui = SEG[i]; out = {}
        for L in LAYERS:
            pos = []; val = []
            if cell == "A_sys":   pos += si; val.append(ct[L]["s"])
            elif cell == "A_usr": pos += ui; val.append(ct[L]["u"])
            elif cell == "B_sys": pos += si; val.append(ct[L]["u"])
            elif cell == "B_usr": pos += ui; val.append(ct[L]["s"])
            elif cell == "EXCH":  pos += si + ui; val += [ct[L]["u"], ct[L]["s"]]
            elif cell == "CONSTR":pos += si + ui; val += [ct[L]["s"], ct[L]["u"]]
            out[L] = (torch.tensor(pos, dtype=torch.long, device=dev), torch.cat(val, 0).to(torch.bfloat16))
        return out

    def aligned(i, j):
        _, si, ui = SEG[i]; _, sj, uj = SEG[j]
        return len(si) == len(sj) and len(ui) == len(uj) and len(si) == len(uj) and len(ui) == len(sj)

    use = [i for i in range(len(stim)) if twin_of.get(i) is not None and SEG[i][1] and SEG[i][2] and aligned(i, twin_of[i])]
    if SMOKE: use = use[:40]
    log(f"[OPX] usable={len(use)} skipped={len(stim)-len(use)} ({time.time()-t0:.0f}s)")

    # self-check: EXCH must move item0; CONSTR must nearly flip it
    i0 = use[0]; ct0 = capture(twin_of[i0]); yb0, _ = run(SEG[i0][0])
    ye0, _ = run(SEG[i0][0], rp(i0, ct0, "EXCH")); yc0, _ = run(SEG[i0][0], rp(i0, ct0, "CONSTR"))
    if abs(ye0 - yb0) < 1e-4:
        for h in handles: h.remove()
        raise SystemExit(f"SELFCHECK FAILED: EXCH did not move Y (base {yb0:.4f} exch {ye0:.4f})")
    log(f"[OPX] SELFCHECK item0 base {yb0:+.4f} EXCH {ye0:+.4f} CONSTR {yc0:+.4f}")

    CELLS = ["A_sys", "A_usr", "B_sys", "B_usr", "EXCH", "CONSTR"]
    tmpl = np.array([stim[i]["template_idx"] for i in use])
    Yb = np.zeros(len(use)); mB = np.zeros(len(use))
    Yc = {c: np.zeros(len(use)) for c in CELLS}; mc = {c: np.zeros(len(use)) for c in CELLS}
    for n, i in enumerate(use):
        it = stim[i]; ids = SEG[i][0]; ct = capture(twin_of[i])
        r, m = run(ids); Yb[n] = ysig(r, it); mB[n] = m
        for c in CELLS:
            r, m = run(ids, rp(i, ct, c)); Yc[c][n] = ysig(r, it); mc[c][n] = m
        if (n + 1) % 120 == 0: log(f"[OPX] {n+1}/{len(use)} ({time.time()-t0:.0f}s)")
    B = float(Yb.mean()); log(f"[OPX] B={B:+.4f} massB={mB.mean():.3f} ({time.time()-t0:.0f}s)")

    # VOID (uncontested same-content replacement) -- inherited from RES-02
    uncsel = unc[::FLOOR_STRIDE]
    def unc_seg(it):
        try:
            imp = TEMPLATES[it["template_idx"]].format(T=it["target"])
            msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
            text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
            ids = enc["input_ids"]; offs = enc["offset_mapping"]
            cs = text.index(imp); ce = cs + len(imp)
            return ids, [k for k, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        except Exception:
            return None
    def ucomply(ids, repl=None):
        STATE["repl"] = repl; t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lp = torch.log_softmax(model(input_ids=t, use_cache=False).logits[0, -1, :].float(), -1)
        STATE["repl"] = None
        return 1 if (lp[DONE] - lp[READY]) > 0 else 0
    uok = un = 0
    for it in uncsel:
        s = unc_seg(it)
        if s and s[1]: un += 1; uok += ucomply(s[0])
    floor_uns = uok / max(1, un)
    grp = defaultdict(list)
    for k, it in enumerate(uncsel): grp[(it["template_idx"], it["position"], it["slot"], it["target"])].append(k)
    sok = sn = 0
    for k, it in enumerate(uncsel):
        s = unc_seg(it)
        if not s or not s[1]: continue
        cand = [mm for mm in grp[(it["template_idx"], it["position"], it["slot"], it["target"])] if mm != k]
        if not cand: continue
        ss = unc_seg(uncsel[cand[0]])
        if not ss or len(ss[1]) != len(s[1]): continue
        t = torch.tensor([ss[0]], dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        repl = {L: (torch.tensor(s[1], dtype=torch.long, device=dev), hs[L][0, ss[1], :].to(torch.bfloat16)) for L in LAYERS}
        sn += 1; sok += ucomply(s[0], repl)
    floor_steer = sok / max(1, sn) if sn else float("nan")
    for h in handles: h.remove()
    VOID = bool(sn > 0 and floor_steer < 0.90 * floor_uns)
    log(f"[OPX] floor uns {floor_uns:.3f}(n{un}) steer {floor_steer:.3f}(n{sn}) VOID={VOID}")

    # M + paired template-cluster bootstrap (matches RES-02/06 estimator so the 0.462 anchor is comparable)
    def per_t(a): return np.array([a[tmpl == tt].mean() if (tmpl == tt).any() else 0.0 for tt in range(NTMPL)])
    ptB = per_t(Yb)
    d = {c: Yc[c] - Yb for c in CELLS}; pt = {c: per_t(d[c]) for c in CELLS}
    def M_of(p): return float(-p.mean() / (2 * ptB.mean())) if abs(ptB.mean()) > 1e-9 else float("nan")
    M = {c: M_of(pt[c]) for c in CELLS}
    gap_pt = 1.0 - (M["A_sys"] + M["A_usr"])
    rng = np.random.default_rng(SEED)
    bM = {c: np.empty(BOOT) for c in CELLS}; bgap = np.empty(BOOT)
    bregS = np.empty(BOOT); bregU = np.empty(BOOT); bside = np.empty(BOOT)
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL); den = 2 * ptB[pk].mean()
        if abs(den) < 1e-9:
            for c in CELLS: bM[c][b] = np.nan
            bgap[b] = bregS[b] = bregU[b] = bside[b] = np.nan; continue
        mm = {c: -pt[c][pk].mean() / den for c in CELLS}
        for c in CELLS: bM[c][b] = mm[c]
        bgap[b] = 1.0 - (mm["A_sys"] + mm["A_usr"])
        bregS[b] = mm["A_sys"] - mm["B_sys"]; bregU[b] = mm["A_usr"] - mm["B_usr"]
        bside[b] = (mm["B_sys"] + mm["B_usr"]) - mm["EXCH"]
    def ci(a): lo, hi = np.nanpercentile(a, [2.5, 97.5]); return [float(lo), float(hi)]
    cM = {c: ci(bM[c]) for c in CELLS}; cgap = ci(bgap)
    cregS, cregU, cside = ci(bregS), ci(bregU), ci(bside)

    anchor_exch_ok = abs(M["EXCH"] - 0.462) <= 0.03
    constr_ok = M["CONSTR"] >= 0.97
    if VOID:
        verdict = "VOID -- not a null"
    elif not anchor_exch_ok:
        verdict = f"ANCHOR-FAIL exch M={M['EXCH']:.3f} (harness diverged; downstream unreadable)"
    elif not constr_ok:
        verdict = f"CONSTRUCTION-CHECK-FAIL constr M={M['CONSTR']:.3f}<0.97 (harness broken)"
    elif cgap[0] > 0.10:
        verdict = "SUB-ADDITIVE / INTERACTIONAL (spans do not additively determine Y; remainder is the between-block comparison)"
    elif abs(gap_pt) <= 0.10 and cgap[0] <= 0 <= cgap[1]:
        verdict = "ADDITIVE (two spans additively determine Y; exchange 0.46 is an operator deficit, demonstrated)"
    else:
        verdict = "INTERMEDIATE (gap small/uncertain; report table)"

    out = {"prereg": "PREREG_OPX01.md", "SMOKE": SMOKE,
           "chained_to_EXT01": "86b066c70025e518f16abf009e752235b42b96997df209b27376e0d38962b9fe",
           "transformers": transformers.__version__, "layers": LAYERS, "B": B, "n_pairs": len(use),
           "M": M, "M_ci": cM, "mass": {c: float(mc[c].mean()) for c in CELLS}, "mass_B": float(mB.mean()),
           "gap_additivity_1_minus_Asys_plus_Ausr": gap_pt, "gap_ci": cgap,
           "region_effect_sys_AminusB": M["A_sys"] - M["B_sys"], "region_sys_ci": cregS,
           "region_effect_usr_AminusB": M["A_usr"] - M["B_usr"], "region_usr_ci": cregU,
           "sidedness_Bsum_minus_EXCH": (M["B_sys"] + M["B_usr"]) - M["EXCH"], "sidedness_ci": cside,
           "dY": {c: float(d[c].mean()) for c in CELLS},
           "anchor_exch_reproduces_0.462_pm0.03": bool(anchor_exch_ok),
           "construction_check_constr_ge_0.97": bool(constr_ok),
           "floor_unsteered": floor_uns, "floor_steered": floor_steer, "VOID": VOID, "verdict": verdict,
           "scope": "Explains the exchange OPERATOR, not the model. CONSTR=1.0 is a construction identity (become-the-twin), "
                    "never evidence. gap large => the missing half is interactional (between-block comparison), which is why "
                    "6 single-component interventions came back null: there is no component. Property of these span positions/"
                    "layers under residual overwrite; single model.",
           "runtime_s": round(time.time() - t0, 1)}
    import csv
    with open(os.path.join(OUT, "opx01_arms_smoke.csv" if SMOKE else "opx01_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["cell", "M", "ci_lo", "ci_hi", "dY", "mass"])
        for c in CELLS:
            w.writerow([c, round(M[c], 5), round(cM[c][0], 5), round(cM[c][1], 5), round(float(d[c].mean()), 5), round(float(mc[c].mean()), 4)])
        w.writerow(["GAP_additivity", round(gap_pt, 5), round(cgap[0], 5), round(cgap[1], 5), "", ""])
    np.savez(os.path.join(OUT, "opx01_peritem" + ("_smoke" if SMOKE else "") + ".npz"),
             use=np.array(use), tmpl=tmpl, Yb=Yb, **{f"Y_{c}": Yc[c] for c in CELLS}, **{f"m_{c}": mc[c] for c in CELLS})
    fn = os.path.join(OUT, "opx01_smoke.json" if SMOKE else "opx01.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[OPX] M={{" + ", ".join(f'{c}:{M[c]:+.3f}' for c in CELLS) + "}}")
    log(f"[OPX] GAP=1-(Asys+Ausr)={gap_pt:+.4f} {cgap} anchor_exch={anchor_exch_ok} constr={constr_ok} VOID={VOID} -> {verdict}; wrote {fn}")

if __name__ == "__main__":
    main()
