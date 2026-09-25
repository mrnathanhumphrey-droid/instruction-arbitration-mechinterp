#!/usr/bin/env python
# OPX-04 -- does the BLOCK FILLER/BODY content carry the OPX-01 role-dominance asymmetry (A_sys ~ -0.93/-7.2 raw,
# A_usr ~ +1.90/+14.8 raw)? OPX-03 ruled out the role-word marker (~0%) and the system preamble (~6%); 94% survives, leading
# candidate the never-matched filler (fsys = system-voice framing vs fusr = user-voice framing, the only role-differentiated
# body content). This is a SWAP design (the reviewer): matching can only collapse (construction check), swapping INVERTS -- and
# inversion is the unique signature nothing else produces (OPX-02: offset only shifts magnitude ~5 nats, never flips sign).
# Arms (normal order; one-sided same-index span patch from the cb-flip twin, L8-31; twin surged the SAME way per arm):
#   BASE  : native (sys=imp_sys+fsys, usr=imp_usr+fusr)                    -- anchor, reproduce OPX-01
#   SWAP  : fillers swapped (sys=imp_sys+fusr, usr=imp_usr+fsys), markers+imperatives NATIVE  -- PRIMARY discriminator
#   MATCH : both fillers -> one neutral filler FN (construction check; can only collapse)
#   STRIP : no filler (sys=imp_sys, usr=imp_usr; markers+spans only)       -- high-upside: survival => almost nothing standing
# PRIMARY = raw dY (surgeries change B; OPX-02/03 lesson). asym(arm) = dY_usr - dY_sys. inversion = sign(asym_SWAP) flips vs
# sign(asym_BASE). B reported per arm.
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
FN = "The following is a short block of text."   # MATCH neutral filler (judgment call, flagged); role-neutral, both blocks
NTMPL = 30; BOOT = 300 if SMOKE else 5000; SEED = 20260925
ARMS = ["BASE", "SWAP", "MATCH", "STRIP"]
def log(*a): print(*a, flush=True)

def place(imp, filler, pos):
    return f"{imp} {filler}" if pos == "early" else f"{filler} {imp}"

def main():
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_contested.jsonl"), encoding="utf-8")]
    from make_stimuli import TEMPLATES, FILLERS
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import transformers
    log(f"[OPX4] model on {dev}; tf {transformers.__version__} L{LAYERS[0]}..{LAYERS[-1]} ({time.time()-t0:.0f}s)")

    def blocks(it, mode):
        """(system_text, user_text, imp_sys, imp_usr) for the item under mode."""
        ti, fi, pos = it["template_idx"], it["filler_idx"], it["position"]
        imp_sys = TEMPLATES[ti].format(T=it["target_sys"]); imp_usr = TEMPLATES[ti].format(T=it["target_usr"])
        fsys, fusr = FILLERS[fi]
        if mode == "BASE":    s, u = place(imp_sys, fsys, pos), place(imp_usr, fusr, pos)
        elif mode == "SWAP":  s, u = place(imp_sys, fusr, pos), place(imp_usr, fsys, pos)   # fillers swapped
        elif mode == "MATCH": s, u = place(imp_sys, FN, pos),   place(imp_usr, FN, pos)     # identical filler
        elif mode == "STRIP": s, u = imp_sys, imp_usr                                       # no filler
        else: raise ValueError(mode)
        return s, u, imp_sys, imp_usr

    def variant(it, mode):
        """return (ids, si, ui) for the item under mode, or None on failure."""
        s, u, imp_sys, imp_usr = blocks(it, mode)
        msgs = [{"role": "system", "content": s}, {"role": "user", "content": u}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]
        def sp(imp, start=0):
            cs = text.find(imp, start)
            if cs < 0: return None
            ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        # imp_sys sits in the system block (first), imp_usr in the user block (after it)
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
    log(f"[OPX4] usable={len(use)} skipped={len(stim)-len(use)} ({time.time()-t0:.0f}s)")

    tmpl = np.array([stim[i]["template_idx"] for i in use]); N = len(use)
    Yb = {m: np.zeros(N) for m in ARMS}; Ys = {m: np.zeros(N) for m in ARMS}; Yu = {m: np.zeros(N) for m in ARMS}
    ms = {m: np.zeros(N) for m in ARMS}
    for n, i in enumerate(use):
        it = stim[i]; tw = twin_of[i]
        for m in ARMS:
            ids, si, ui = variant(it, m); tids, tsi, tui = variant(stim[tw], m)
            cap = capture(tids, tsi, tui)
            rb, mb = run(ids); Yb[m][n] = ysig(rb, it); ms[m][n] = mb
            Ys[m][n] = ysig(run(ids, repl_one(si, cap, "s"))[0], it)   # A_sys: item sys-span <- twin sys-span
            Yu[m][n] = ysig(run(ids, repl_one(ui, cap, "u"))[0], it)   # A_usr: item usr-span <- twin usr-span
        if (n + 1) % 60 == 0: log(f"[OPX4] {n+1}/{N} ({time.time()-t0:.0f}s)")
    for h in handles: h.remove()

    def per_t(a): return np.array([a[tmpl == tt].mean() if (tmpl == tt).any() else 0.0 for tt in range(NTMPL)])
    B = {m: float(Yb[m].mean()) for m in ARMS}
    # PRIMARY: raw dY per arm (B changes across arms -> normalized M not comparable; OPX-02/03 lesson)
    ptds = {m: per_t(Ys[m] - Yb[m]) for m in ARMS}      # per-template dY_sys
    ptdu = {m: per_t(Yu[m] - Yb[m]) for m in ARMS}      # per-template dY_usr
    dY_sys = {m: float(ptds[m].mean()) for m in ARMS}; dY_usr = {m: float(ptdu[m].mean()) for m in ARMS}
    raw_asym = {m: dY_usr[m] - dY_sys[m] for m in ARMS}
    # M anchor only where B healthy (BASE); report advisory M for BASE
    ptB = {m: per_t(Yb[m]) for m in ARMS}
    def Mof(pt, m): return float(-pt.mean() / (2 * ptB[m].mean())) if abs(ptB[m].mean()) > 1e-9 else float("nan")
    M_sys_BASE = Mof(ptds["BASE"], "BASE"); M_usr_BASE = Mof(ptdu["BASE"], "BASE")

    rng = np.random.default_rng(SEED)
    def boot_asym(m, pk): return (ptdu[m][pk].mean() - ptds[m][pk].mean())
    bas = {m: np.empty(BOOT) for m in ARMS}
    b_invert = np.empty(BOOT)              # asym_BASE + asym_SWAP  (==0 iff SWAP is a clean sign inversion of BASE)
    b_swapmove = np.empty(BOOT)            # asym_BASE - asym_SWAP  (how much asym the swap removed+reversed)
    b_stripsurv = np.empty(BOOT)          # asym_STRIP / asym_BASE
    b_matchresid = np.empty(BOOT)         # asym_MATCH
    b_ratio = np.empty(BOOT)              # asym_SWAP / asym_BASE  (the three-way threshold quantity)
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL)
        a = {m: boot_asym(m, pk) for m in ARMS}
        for m in ARMS: bas[m][b] = a[m]
        b_invert[b] = a["BASE"] + a["SWAP"]
        b_swapmove[b] = a["BASE"] - a["SWAP"]
        b_stripsurv[b] = a["STRIP"] / a["BASE"] if abs(a["BASE"]) > 1e-9 else np.nan
        b_matchresid[b] = a["MATCH"]
        b_ratio[b] = a["SWAP"] / a["BASE"] if abs(a["BASE"]) > 1e-9 else np.nan
    def ci(x): lo, hi = np.nanpercentile(x, [2.5, 97.5]); return [float(lo), float(hi)]

    # --- Addition 1 (the reviewer): per-item filler length delta vs the effect (does length explain the swap move?) ---
    flen_s = np.array([len(tok(FILLERS[stim[i]["filler_idx"]][0], add_special_tokens=False)["input_ids"]) for i in use])
    flen_u = np.array([len(tok(FILLERS[stim[i]["filler_idx"]][1], add_special_tokens=False)["input_ids"]) for i in use])
    fdelta = np.abs(flen_u - flen_s).astype(float)
    FN_len = len(tok(FN, add_special_tokens=False)["input_ids"])          # Addition 2: FN length vs fsys/fusr
    asymB_i = Yu["BASE"] - Ys["BASE"]; asymS_i = Yu["SWAP"] - Ys["SWAP"]; move_i = asymB_i - asymS_i
    def pear(x, y):
        return float(np.corrcoef(x, y)[0, 1]) if (np.std(x) > 1e-9 and np.std(y) > 1e-9) else float("nan")
    r_delta_move = pear(fdelta, move_i); r_delta_base = pear(fdelta, asymB_i); r_delta_swap = pear(fdelta, asymS_i)
    rng2 = np.random.default_rng(SEED + 1); br = np.empty(BOOT)
    tmpl_idx = {tt: np.where(tmpl == tt)[0] for tt in range(NTMPL)}
    for b in range(BOOT):
        pk = rng2.integers(0, NTMPL, NTMPL); idx = np.concatenate([tmpl_idx[tt] for tt in pk])
        br[b] = pear(fdelta[idx], move_i[idx])
    r_delta_move_ci = ci(br)

    # --- Pre-registered THREE-WAY inversion verdict (the reviewer), on raw dY point estimate ratio r = asym_SWAP/asym_BASE ---
    aB, aSW, aST, aMA = raw_asym["BASE"], raw_asym["SWAP"], raw_asym["STRIP"], raw_asym["MATCH"]
    r_swap = aSW / aB if abs(aB) > 1e-9 else float("nan")            # BASE asym expected large positive
    swap_ci = ci(bas["SWAP"]); strip_frac = aST / aB if abs(aB) > 1e-9 else float("nan")
    strip_ci = ci(bas["STRIP"])
    anchor_ok = abs(dY_sys["BASE"] - (-7.19)) <= 2.5 and abs(dY_usr["BASE"] - 14.75) <= 3.0
    swap_excl0 = not (swap_ci[0] <= 0 <= swap_ci[1])
    strip_ctx = (f"STRIP {aST:+.2f} ({100*strip_frac:.0f}% of BASE, CI{strip_ci})"
                 f"{' survives' if (np.sign(aST)==np.sign(aB) and abs(aST)>=0.5*abs(aB) and not (strip_ci[0]<=0<=strip_ci[1])) else ' does-not-clearly-survive'}")
    match_ctx = f"MATCH resid {aMA:+.2f} (CI{ci(bas['MATCH'])})"
    if not anchor_ok:
        band = "ANCHOR-FAIL"
        verdict = f"ANCHOR-FAIL BASE dY_sys={dY_sys['BASE']:.2f} dY_usr={dY_usr['BASE']:.2f} (harness diverged)"
    elif r_swap <= -0.5:
        band = "BODY-CARRIES"
        verdict = (f"BODY-CARRIES: SWAP inverts and preserves magnitude (r=asym_SWAP/asym_BASE={r_swap:+.2f} <= -0.5; "
                   f"{aB:+.2f}->{aSW:+.2f}, SWAP CI{swap_ci} excl0={swap_excl0}). The block filler/body content carries the "
                   f"OPX-01 role-dominance. Inversion is the unique signature. [{strip_ctx}; {match_ctx}]")
    elif abs(r_swap) <= 0.5:
        band = "BODY-PARTIAL"
        verdict = (f"BODY-PARTIAL: SWAP substantially shrinks the asymmetry (|r|={abs(r_swap):.2f} <= 0.5; {aB:+.2f}->{aSW:+.2f}) "
                   f"-> the body carries a share, a residual is still unenumerated. [{strip_ctx}; {match_ctx}]")
    else:
        band = "BODY-NULL"
        verdict = (f"BODY-NULL: SWAP holds sign and preserves magnitude (r={r_swap:+.2f} > 0.5; {aB:+.2f}->{aSW:+.2f}) -> the "
                   f"filler does NOT carry it; with marker+preamble already ruled out (OPX-03), enumeration is still incomplete, "
                   f"go deeper. [{strip_ctx}; {match_ctx}]")

    out = {"prereg": "PREREG_OPX04.md", "SMOKE": SMOKE,
           "chained_to_OPX03": "ef1e7eb6e76db57e776bae49675ad8b7493df7ea098930ebd4167040a986c4ea",
           "transformers": transformers.__version__, "layers": LAYERS, "MATCH_neutral_filler": FN, "n_pairs": N,
           "B_per_arm": B, "mass_per_arm": {m: float(ms[m].mean()) for m in ARMS},
           "dY_sys": dY_sys, "dY_usr": dY_usr, "raw_asym": raw_asym,
           "raw_asym_ci": {m: ci(bas[m]) for m in ARMS},
           "M_A_sys_BASE_advisory": M_sys_BASE, "M_A_usr_BASE_advisory": M_usr_BASE,
           "swap_ratio_r": r_swap, "swap_ratio_ci": ci(b_ratio),           # three-way threshold quantity
           "invert_test_asymBASE_plus_asymSWAP": float(b_invert.mean()), "invert_ci": ci(b_invert),
           "swap_move_asymBASE_minus_asymSWAP": float(b_swapmove.mean()), "swap_move_ci": ci(b_swapmove),
           "swap_ci_excludes_0": bool(swap_excl0),
           "strip_survival_frac": strip_frac, "strip_survival_ci": ci(b_stripsurv),
           "match_residual_asym": aMA, "match_residual_ci": ci(b_matchresid),
           "filler_len_fsys_mean": float(flen_s.mean()), "filler_len_fusr_mean": float(flen_u.mean()),
           "filler_len_delta_abs_mean": float(fdelta.mean()), "filler_len_delta_abs_max": float(fdelta.max()),
           "FN_neutral_filler_len": int(FN_len),
           "corr_fillerdelta_vs_swapmove": r_delta_move, "corr_fillerdelta_vs_swapmove_ci": r_delta_move_ci,
           "corr_fillerdelta_vs_asymBASE": r_delta_base, "corr_fillerdelta_vs_asymSWAP": r_delta_swap,
           "anchor_base_reproduces_opx01": bool(anchor_ok), "verdict_band": band, "verdict": verdict,
           "scope": "raw dY is primary (surgeries change B; OPX-02/03). SWAP is the primary discriminator: inversion of the "
                    "asym sign is the unique body-content signature (offset only shifts magnitude, never flips -- OPX-02). MATCH "
                    "is a collapse-only construction check. STRIP is high-upside: survival with marker+preamble already ruled "
                    "out leaves almost nothing standing. Property of these spans/layers/model/battery, normal order. FN neutral "
                    "filler is a judgment call (flagged); the filler length asymmetry under SWAP is a named, offset-robust confound.",
           "runtime_s": round(time.time() - t0, 1)}
    import csv
    with open(os.path.join(OUT, "opx04_arms_smoke.csv" if SMOKE else "opx04_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["arm", "dY_sys", "dY_usr", "raw_asym", "B", "mass"])
        for m in ARMS: w.writerow([m, round(dY_sys[m], 4), round(dY_usr[m], 4), round(raw_asym[m], 4), round(B[m], 4), round(float(ms[m].mean()), 3)])
    np.savez(os.path.join(OUT, "opx04_peritem" + ("_smoke" if SMOKE else "") + ".npz"),
             use=np.array(use), tmpl=tmpl, flen_s=flen_s, flen_u=flen_u, fdelta=fdelta,
             **{f"Yb_{m}": Yb[m] for m in ARMS},
             **{f"Ys_{m}": Ys[m] for m in ARMS}, **{f"Yu_{m}": Yu[m] for m in ARMS})
    fn = os.path.join(OUT, "opx04_smoke.json" if SMOKE else "opx04.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[OPX4] raw_asym BASE {aB:+.2f} SWAP {aSW:+.2f} MATCH {aMA:+.2f} STRIP {aST:+.2f}  r_swap={r_swap:+.2f}{ci(b_ratio)}")
    log(f"[OPX4] FN_len={FN_len} fsys~{flen_s.mean():.1f} fusr~{flen_u.mean():.1f} |delta|max={fdelta.max():.0f}  "
        f"corr(delta,swap_move)={r_delta_move:+.3f}{r_delta_move_ci}")
    log(f"[OPX4] anchor={anchor_ok} band={band} -> {verdict}; wrote {fn}")

if __name__ == "__main__":
    main()
