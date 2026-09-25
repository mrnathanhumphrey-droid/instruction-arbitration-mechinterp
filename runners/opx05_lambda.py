#!/usr/bin/env python
# OPX-05 -- the JOINT STRIP: is the role-dominance asymmetry a REDUNDANT textual code, or genuinely non-textual?
# OPX-03 (marker~0, preamble~6%) and OPX-04 (filler BODY-NULL) each neutralized textual features SEPARATELY, never JOINTLY.
# A redundant code (>=2 features each sufficient) survives every single neutralization yet collapses only when all are removed
# at once. This is the FIRST genuine construction check of the whole textual enumeration.
# Arms (normal order; one-sided same-index span patch from cb-flip twin, L8-31; twin surged the SAME way per arm):
#   BASE  : native                                                        -- anchor, reproduce OPX-01 (raw = M x -2B)
#   PM    : marker->NEUTRAL + system preamble stripped, filler KEPT       -- reproduces OPX-03 PM in-run
#   STRIP : filler removed, markers + preamble NATIVE                     -- reproduces OPX-04 STRIP in-run
#   JOINT : marker->NEUTRAL + preamble stripped + filler removed          -- PM u STRIP, all textual differences gone at once
# PRIMARY = raw dY, B per arm. KEY = r = asym_JOINT / asym_BASE. Pre-registered bands (the reviewer):
#   r <= 0.25            -> REDUNDANT-TEXTUAL-CODE (collapses; enumeration was redundant, non-textual fork does NOT fire)
#   0.25 < r <= 0.75     -> PARTIAL (some jointly textual, a residual isn't -> residual goes to the non-textual class)
#   r > 0.75             -> TEXTUAL-EXHAUSTED (fork (a) fires: non-textual / positional-slot probe class)
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
NEUTRAL = "info"                                          # single-token role word (both headers); matches OPX-03
HDR_END = "<|end_header_id|>\n\n"
NTMPL = 30; BOOT = 300 if SMOKE else 5000; SEED = 20260925
ARMS = ["BASE", "PM", "STRIP", "JOINT"]
def log(*a): print(*a, flush=True)

def place(imp, filler, pos): return f"{imp} {filler}" if pos == "early" else f"{filler} {imp}"

def main():
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_contested.jsonl"), encoding="utf-8")]
    from make_stimuli import TEMPLATES, FILLERS
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import transformers
    log(f"[OPX5] model on {dev}; tf {transformers.__version__} L{LAYERS[0]}..{LAYERS[-1]} NEUTRAL={NEUTRAL!r} ({time.time()-t0:.0f}s)")

    def variant(it, mode):
        """return (ids, si, ui) for the item under mode, or None on failure."""
        ti, fi, pos = it["template_idx"], it["filler_idx"], it["position"]
        imp_sys = TEMPLATES[ti].format(T=it["target_sys"]); imp_usr = TEMPLATES[ti].format(T=it["target_usr"])
        fsys, fusr = FILLERS[fi]
        keep_filler = mode in ("BASE", "PM")
        s = place(imp_sys, fsys, pos) if keep_filler else imp_sys
        u = place(imp_usr, fusr, pos) if keep_filler else imp_usr
        text = tok.apply_chat_template([{"role": "system", "content": s}, {"role": "user", "content": u}],
                                       tokenize=False, add_generation_prompt=True)
        if mode in ("PM", "JOINT"):                                   # marker -> NEUTRAL (both headers)
            for role in ("system", "user"):
                text = text.replace(f"<|start_header_id|>{role}<|end_header_id|>", f"<|start_header_id|>{NEUTRAL}<|end_header_id|>")
            h = text.find(HDR_END)                                    # strip system preamble (between 1st header end and sys content)
            if h < 0: return None
            h += len(HDR_END); c = text.find(s)
            if c > h: text = text[:h] + text[c:]
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]
        def sp(imp, start=0):
            cs = text.find(imp, start)
            if cs < 0: return None
            ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        si = sp(imp_sys)
        ui = sp(imp_usr, start=(text.find(imp_sys) + len(imp_sys)) if text.find(imp_sys) >= 0 else 0)
        if not si or not ui: return None
        return ids, si, ui

    twin_g = defaultdict(dict)
    for i, it in enumerate(stim):
        twin_g[(it["template_idx"], it["filler_idx"], it["position"])][it["counterbalance"]] = i
    twin_of = {}
    for d in twin_g.values():
        if len(d) == 2: a, b = list(d.values()); twin_of[a] = b; twin_of[b] = a

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
            lp = torch.log_softmax(model(input_ids=t, use_cache=False).logits[0, -1, :].float(), -1)
        STATE["repl"] = None
        return float(lp[DONE] - lp[READY]), float(torch.exp(lp[DONE]) + torch.exp(lp[READY]))
    def ysig(R, it): return R if it["target_sys"] == "DONE" else -R
    def capture(ids, si, ui):
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        return {L: {"s": hs[L][0, si, :].detach().clone(), "u": hs[L][0, ui, :].detach().clone()} for L in LAYERS}
    def repl_one(pos, cap, key):
        return {L: (torch.tensor(pos, dtype=torch.long, device=dev), cap[L][key].to(torch.bfloat16)) for L in LAYERS}

    def usable(i):
        tw = twin_of.get(i)
        if tw is None: return False
        for m in ARMS:
            a = variant(stim[i], m); b = variant(stim[tw], m)
            if a is None or b is None: return False
            if len(a[1]) != len(b[1]) or len(a[2]) != len(b[2]): return False
        return True
    use = [i for i in range(len(stim)) if usable(i)]
    if SMOKE: use = use[:40]
    log(f"[OPX5] usable={len(use)} skipped={len(stim)-len(use)} ({time.time()-t0:.0f}s)")

    tmpl = np.array([stim[i]["template_idx"] for i in use]); N = len(use)
    Yb = {m: np.zeros(N) for m in ARMS}; Ys = {m: np.zeros(N) for m in ARMS}; Yu = {m: np.zeros(N) for m in ARMS}
    ms = {m: np.zeros(N) for m in ARMS}
    for n, i in enumerate(use):
        it = stim[i]; tw = twin_of[i]
        for m in ARMS:
            ids, si, ui = variant(it, m); tids, tsi, tui = variant(stim[tw], m)
            cap = capture(tids, tsi, tui)
            rb, mb = run(ids); Yb[m][n] = ysig(rb, it); ms[m][n] = mb
            Ys[m][n] = ysig(run(ids, repl_one(si, cap, "s"))[0], it)
            Yu[m][n] = ysig(run(ids, repl_one(ui, cap, "u"))[0], it)
        if (n + 1) % 60 == 0: log(f"[OPX5] {n+1}/{N} ({time.time()-t0:.0f}s)")
    for h in handles: h.remove()

    def per_t(a): return np.array([a[tmpl == tt].mean() if (tmpl == tt).any() else 0.0 for tt in range(NTMPL)])
    B = {m: float(Yb[m].mean()) for m in ARMS}
    ptds = {m: per_t(Ys[m] - Yb[m]) for m in ARMS}; ptdu = {m: per_t(Yu[m] - Yb[m]) for m in ARMS}
    dY_sys = {m: float(ptds[m].mean()) for m in ARMS}; dY_usr = {m: float(ptdu[m].mean()) for m in ARMS}
    raw_asym = {m: dY_usr[m] - dY_sys[m] for m in ARMS}
    ptB = {m: per_t(Yb[m]) for m in ARMS}
    def Mof(pt, m): return float(-pt.mean() / (2 * ptB[m].mean())) if abs(ptB[m].mean()) > 1e-9 else float("nan")
    M_sys_BASE = Mof(ptds["BASE"], "BASE"); M_usr_BASE = Mof(ptdu["BASE"], "BASE")

    rng = np.random.default_rng(SEED)
    def boot_asym(m, pk): return (ptdu[m][pk].mean() - ptds[m][pk].mean())
    bas = {m: np.empty(BOOT) for m in ARMS}; b_ratio = np.empty(BOOT)
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL); a = {m: boot_asym(m, pk) for m in ARMS}
        for m in ARMS: bas[m][b] = a[m]
        b_ratio[b] = a["JOINT"] / a["BASE"] if abs(a["BASE"]) > 1e-9 else np.nan
    def ci(x): lo, hi = np.nanpercentile(x, [2.5, 97.5]); return [float(lo), float(hi)]

    # length check on the JOINT effect (JOINT removes filler + preamble; tokens/offset move) -- same discipline as OPX-04
    flen_s = np.array([len(tok(FILLERS[stim[i]["filler_idx"]][0], add_special_tokens=False)["input_ids"]) for i in use], float)
    flen_u = np.array([len(tok(FILLERS[stim[i]["filler_idx"]][1], add_special_tokens=False)["input_ids"]) for i in use], float)
    joint_eff = (Yu["JOINT"] - Ys["JOINT"]) - (Yu["BASE"] - Ys["BASE"])
    def pear(x, y): return float(np.corrcoef(x, y)[0, 1]) if (np.std(x) > 1e-9 and np.std(y) > 1e-9) else float("nan")
    tmpl_idx = {tt: np.where(tmpl == tt)[0] for tt in range(NTMPL)}
    rng2 = np.random.default_rng(SEED + 1); brtot = np.empty(BOOT); brdif = np.empty(BOOT)
    for b in range(BOOT):
        pk = rng2.integers(0, NTMPL, NTMPL); idx = np.concatenate([tmpl_idx[tt] for tt in pk])
        brtot[b] = pear((flen_s + flen_u)[idx], joint_eff[idx]); brdif[b] = pear((flen_u - flen_s)[idx], joint_eff[idx])
    r_joint_tot = pear(flen_s + flen_u, joint_eff); r_joint_dif = pear(flen_u - flen_s, joint_eff)

    aB, aPM, aST, aJ = (raw_asym[m] for m in ("BASE", "PM", "STRIP", "JOINT"))
    r = aJ / aB if abs(aB) > 1e-9 else float("nan")
    anchor_ok = abs(dY_sys["BASE"] - (-7.19)) <= 2.5 and abs(dY_usr["BASE"] - 14.75) <= 3.0
    ctx = (f"PM {aPM:+.2f}({100*aPM/aB:.0f}%,OPX-03 repro) STRIP {aST:+.2f}({100*aST/aB:.0f}%,OPX-04 repro) "
           f"JOINT {aJ:+.2f}({100*r:.0f}%) r={r:.2f} CI{ci(b_ratio)}")
    if not anchor_ok:
        band = "ANCHOR-FAIL"; verdict = f"ANCHOR-FAIL BASE dY_sys={dY_sys['BASE']:.2f} dY_usr={dY_usr['BASE']:.2f}"
    elif r <= 0.25:
        band = "REDUNDANT-TEXTUAL-CODE"
        verdict = (f"REDUNDANT-TEXTUAL-CODE: joint strip COLLAPSES the asymmetry (r={r:.2f} <= 0.25). Marker/preamble/filler are a "
                   f"redundant textual code (>=2 each sufficient); each single neutralization survived only because the others "
                   f"remained. Enumeration was redundant, NOT exhausted -> the non-textual fork does NOT fire. [{ctx}]")
    elif r <= 0.75:
        band = "PARTIAL"
        verdict = (f"PARTIAL: joint strip partly collapses (0.25 < r={r:.2f} <= 0.75). Some of the asymmetry is jointly textual; a "
                   f"residual survives all textual neutralization and is the part that goes to the non-textual/positional class. [{ctx}]")
    else:
        band = "TEXTUAL-EXHAUSTED"
        verdict = (f"TEXTUAL-EXHAUSTED: asymmetry SURVIVES the joint strip (r={r:.2f} > 0.75). Every textual difference "
                   f"(marker+preamble+filler) removed at once and it persists -> textual enumeration genuinely exhausted; fork (a) "
                   f"fires -> non-textual / positional-slot probe class. [{ctx}]")

    out = {"prereg": "PREREG_OPX05.md", "SMOKE": SMOKE,
           "chained_to_OPX04": "356ca526d60fe1aa1026d988c778456b2c0cff932486c3eb22c80dc50bbd6248",
           "transformers": transformers.__version__, "layers": LAYERS, "NEUTRAL": NEUTRAL, "n_pairs": N,
           "B_per_arm": B, "mass_per_arm": {m: float(ms[m].mean()) for m in ARMS},
           "dY_sys": dY_sys, "dY_usr": dY_usr, "raw_asym": raw_asym, "raw_asym_ci": {m: ci(bas[m]) for m in ARMS},
           "joint_ratio_r": r, "joint_ratio_ci": ci(b_ratio),
           "pm_frac_of_base": aPM / aB, "strip_frac_of_base": aST / aB,
           "M_A_sys_BASE_advisory": M_sys_BASE, "M_A_usr_BASE_advisory": M_usr_BASE,
           "corr_jointeff_vs_totlen": r_joint_tot, "corr_jointeff_vs_totlen_ci": ci(brtot),
           "corr_jointeff_vs_diflen": r_joint_dif, "corr_jointeff_vs_diflen_ci": ci(brdif),
           "anchor_base_reproduces_opx01": bool(anchor_ok), "verdict_band": band, "verdict": verdict,
           "scope": "raw dY primary (surgeries change B). r = asym_JOINT/asym_BASE with pre-registered bands "
                    "(<=0.25 redundant / 0.25-0.75 partial / >0.75 textual-exhausted). JOINT = PM u STRIP = all textual "
                    "differences removed at once; first genuine construction check of the textual enumeration. PM/STRIP reproduce "
                    "OPX-03/OPX-04 in-run. Property of these spans/layers/model/battery, normal order. NEUTRAL='info'.",
           "runtime_s": round(time.time() - t0, 1)}
    import csv
    with open(os.path.join(OUT, "opx05_arms_smoke.csv" if SMOKE else "opx05_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["arm", "dY_sys", "dY_usr", "raw_asym", "frac_of_base", "B", "mass"])
        for m in ARMS: w.writerow([m, round(dY_sys[m], 4), round(dY_usr[m], 4), round(raw_asym[m], 4),
                                   round(raw_asym[m] / aB, 4), round(B[m], 4), round(float(ms[m].mean()), 3)])
    np.savez(os.path.join(OUT, "opx05_peritem" + ("_smoke" if SMOKE else "") + ".npz"),
             use=np.array(use), tmpl=tmpl, flen_s=flen_s, flen_u=flen_u,
             **{f"Yb_{m}": Yb[m] for m in ARMS}, **{f"Ys_{m}": Ys[m] for m in ARMS}, **{f"Yu_{m}": Yu[m] for m in ARMS})
    fn = os.path.join(OUT, "opx05_smoke.json" if SMOKE else "opx05.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[OPX5] {ctx}")
    log(f"[OPX5] corr(joint_eff,totlen)={r_joint_tot:+.3f}{ci(brtot)} corr(joint_eff,diflen)={r_joint_dif:+.3f}{ci(brdif)}")
    log(f"[OPX5] anchor={anchor_ok} band={band} -> {verdict}; wrote {fn}")

if __name__ == "__main__":
    main()
