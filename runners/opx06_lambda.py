#!/usr/bin/env python
# OPX-06 -- does removing the lexical marker make block ORDER matter? 2x2 completion (marker x order).
# Composes OPX-05's JOINT surgery (marker->info + preamble stripped + filler stripped) with OPX-02/ORD-01's block-order flip.
# Cells = {BASE, JOINT} x {normal, reversed}; asym(cell) = dY_usr - dY_sys from one-sided same-index span patches (A_sys, A_usr),
# L8-31, cb-flip twin. The one NEW cell is JOINT-reversed; the other three reproduce OPX-01/05 (BASE-n, JOINT-n) and OPX-02 (BASE-r).
# PRIMARY q = asym_JOINT_reversed / asym_JOINT_normal. Pre-registered bands (the reviewer):
#   q <= -0.50            -> MARKER-MEDIATED POSITION (asym falls back to position once the marker is gone; reconciles OPX-02+05)
#   |q| <= 0.50           -> ORDER-DESTROYS (reversal kills it without inverting)
#   q >  0.50             -> NO-FLIP (nothing in the PROMPT distinguishes the blocks -> property of the PATCHING OPERATION, i.e.
#                            how A_sys/A_usr are constructed; the OPX chain's subject would need renaming, NOT a "slot prior")
# A flip is disambiguated position-vs-target*position by computing q within each counterbalance half. raw dY MANDATORY (B~0 at JOINT).
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
SH, EOT = 128006, 128009
NEUTRAL = "info"; HDR_END = "<|end_header_id|>\n\n"
NTMPL = 30; BOOT = 300 if SMOKE else 5000; SEED = 20260925
MODES = ["BASE", "JOINT"]
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
    log(f"[OPX6] model on {dev}; tf {transformers.__version__} L{LAYERS[0]}..{LAYERS[-1]} ({time.time()-t0:.0f}s)")

    def segment(it, mode):
        ti, fi, pos = it["template_idx"], it["filler_idx"], it["position"]
        imp_s = TEMPLATES[ti].format(T=it["target_sys"]); imp_u = TEMPLATES[ti].format(T=it["target_usr"])
        fsys, fusr = FILLERS[fi]
        if mode == "BASE": s, u = place(imp_s, fsys, pos), place(imp_u, fusr, pos)
        else:              s, u = imp_s, imp_u                                   # JOINT: filler stripped
        text = tok.apply_chat_template([{"role": "system", "content": s}, {"role": "user", "content": u}],
                                       tokenize=False, add_generation_prompt=True)
        if mode == "JOINT":
            for role in ("system", "user"):
                text = text.replace(f"<|start_header_id|>{role}<|end_header_id|>", f"<|start_header_id|>{NEUTRAL}<|end_header_id|>")
            h = text.find(HDR_END)
            if h < 0: return None
            h += len(HDR_END); c = text.find(s)
            if c > h: text = text[:h] + text[c:]
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]
        sh = [i for i, t in enumerate(ids) if t == SH]; eot = [i for i, t in enumerate(ids) if t == EOT]
        if len(sh) < 3 or len(eot) < 2: return None
        def sp(imp, start=0):
            cs = text.find(imp, start)
            if cs < 0: return None
            ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        si = sp(imp_s); ui = sp(imp_u, start=(text.find(imp_s) + len(imp_s)) if text.find(imp_s) >= 0 else 0)
        if not si or not ui: return None
        return ids, si, ui, sh, eot

    def flip(ids, sh, eot):                                   # pre + USER-blk + SYSTEM-blk + assistant ; old->new map
        pre = list(range(0, sh[0]))
        sys_blk = list(range(sh[0], eot[0] + 1)); usr_blk = list(range(sh[1], eot[1] + 1))
        asst = list(range(sh[2], len(ids)))
        order = pre + usr_blk + sys_blk + asst
        return [ids[i] for i in order], {old: new for new, old in enumerate(order)}

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
    def capture(ids):
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        return {L: hs[L][0].detach().clone() for L in LAYERS}
    def repl_one(pos_idx, cap, tw_idx):                       # item span at pos_idx <- twin activations at tw_idx (same-index)
        return {L: (torch.tensor(pos_idx, dtype=torch.long, device=dev),
                    cap[L][tw_idx].to(torch.bfloat16)) for L in LAYERS}

    def usable(i):
        tw = twin_of.get(i)
        if tw is None: return False
        for m in MODES:
            a = segment(stim[i], m); b = segment(stim[tw], m)
            if a is None or b is None: return False
            _, si, ui, _, _ = a; _, tsi, tui, _, _ = b
            if not (len(si) == len(tsi) and len(ui) == len(tui) and len(si) == len(tui) and len(ui) == len(tsi)):
                return False
        return True
    use = [i for i in range(len(stim)) if usable(i)]
    if SMOKE: use = use[:40]
    log(f"[OPX6] usable={len(use)} skipped={len(stim)-len(use)} ({time.time()-t0:.0f}s)")

    tmpl = np.array([stim[i]["template_idx"] for i in use]); N = len(use)
    cb = np.array([1 if stim[i]["counterbalance"] == "DONEsys" else 0 for i in use])
    CELLS = [(m, o) for m in MODES for o in ("n", "f")]
    Yb = {c: np.zeros(N) for c in CELLS}; Ys = {c: np.zeros(N) for c in CELLS}; Yu = {c: np.zeros(N) for c in CELLS}
    mB = {c: np.zeros(N) for c in CELLS}
    for n, i in enumerate(use):
        it = stim[i]; tw = twin_of[i]
        for m in MODES:
            ids, si, ui, sh, eot = segment(it, m); tids, tsi, tui, tsh, teot = segment(stim[tw], m)
            # normal
            capn = capture(tids)
            rb, mb = run(ids); Yb[(m, "n")][n] = ysig(rb, it); mB[(m, "n")][n] = mb
            Ys[(m, "n")][n] = ysig(run(ids, repl_one(si, capn, tsi))[0], it)
            Yu[(m, "n")][n] = ysig(run(ids, repl_one(ui, capn, tui))[0], it)
            # reversed (flip both item and twin; remap spans into flipped index space)
            fids, o2n = flip(ids, sh, eot); ftids, to2n = flip(tids, tsh, teot)
            fsi = [o2n[p] for p in si]; fui = [o2n[p] for p in ui]
            ftsi = [to2n[p] for p in tsi]; ftui = [to2n[p] for p in tui]
            capf = capture(ftids)
            rbf, mbf = run(fids); Yb[(m, "f")][n] = ysig(rbf, it); mB[(m, "f")][n] = mbf
            Ys[(m, "f")][n] = ysig(run(fids, repl_one(fsi, capf, ftsi))[0], it)
            Yu[(m, "f")][n] = ysig(run(fids, repl_one(fui, capf, ftui))[0], it)
        if (n + 1) % 60 == 0: log(f"[OPX6] {n+1}/{N} ({time.time()-t0:.0f}s)")
    for h in handles: h.remove()

    def per_t(a, mask=None):
        m = np.ones(N, bool) if mask is None else mask
        return np.array([a[(tmpl == tt) & m].mean() if ((tmpl == tt) & m).any() else 0.0 for tt in range(NTMPL)])
    B = {c: float(Yb[c].mean()) for c in CELLS}
    asym = {c: float((Yu[c] - Ys[c]).mean()) for c in CELLS}          # raw dY asym = dY_usr - dY_sys
    aJn, aJf, aBn, aBf = asym[("JOINT", "n")], asym[("JOINT", "f")], asym[("BASE", "n")], asym[("BASE", "f")]
    q = aJf / aJn if abs(aJn) > 1e-9 else float("nan")

    rng = np.random.default_rng(SEED)
    def boot_asym_pt(c, pk, mask=None):
        d = per_t(Yu[c] - Ys[c], mask); return d[pk].mean()
    bq = np.empty(BOOT); baJn = np.empty(BOOT); baJf = np.empty(BOOT); banchor = np.empty(BOOT)
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL)
        jn = boot_asym_pt(("JOINT", "n"), pk); jf = boot_asym_pt(("JOINT", "f"), pk); bn = boot_asym_pt(("BASE", "n"), pk)
        baJn[b] = jn; baJf[b] = jf; bq[b] = jf / jn if abs(jn) > 1e-9 else np.nan
        banchor[b] = jn / bn if abs(bn) > 1e-9 else np.nan
    def ci(x): lo, hi = np.nanpercentile(x, [2.5, 97.5]); return [float(lo), float(hi)]

    # counterbalance-half disambiguation of q (position vs target x position)
    qhalf = {}
    for name, mask in (("DONEsys", cb == 1), ("READYsys", cb == 0)):
        jn = per_t(Yu[("JOINT", "n")] - Ys[("JOINT", "n")], mask).mean()
        jf = per_t(Yu[("JOINT", "f")] - Ys[("JOINT", "f")], mask).mean()
        qhalf[name] = (jf / jn) if abs(jn) > 1e-9 else float("nan")

    anchor_ratio = aJn / aBn if abs(aBn) > 1e-9 else float("nan")
    anchor_ok = abs(anchor_ratio - 0.904) <= 0.05
    if not anchor_ok:
        band = "ANCHOR-FAIL"; verdict = f"ANCHOR-FAIL JOINT_n/BASE_n={anchor_ratio:.3f} (expected 0.904+-0.05)"
    elif q <= -0.50:
        band = "MARKER-MEDIATED-POSITION"
        verdict = (f"MARKER-MEDIATED POSITION: with the marker gone, reversal INVERTS the asymmetry (q={q:.2f} <= -0.5). "
                   f"Marker present -> block-bound (OPX-02); marker absent -> position. Reconciles OPX-02 with OPX-05. "
                   f"[q_DONEsys={qhalf['DONEsys']:.2f} q_READYsys={qhalf['READYsys']:.2f}: "
                   f"{'holds both halves -> POSITION' if (qhalf['DONEsys']<=-0.5 and qhalf['READYsys']<=-0.5) else 'one half only -> TARGET x POSITION'}]")
    elif abs(q) <= 0.50:
        band = "ORDER-DESTROYS"
        verdict = f"ORDER-DESTROYS: reversal kills the asymmetry without inverting it (|q|={abs(q):.2f} <= 0.5). Report the curve."
    else:
        band = "NO-FLIP"
        verdict = (f"NO-FLIP: reversal does NOT move the asymmetry (q={q:.2f} > 0.5). Neither marker nor position; target already "
                   f"excluded (OPX-05 cb-split) -> NOTHING IN THE PROMPT distinguishes the two blocks. The asymmetry is a property "
                   f"of the PATCHING OPERATION (how A_sys/A_usr are constructed), not of what it acts on. The OPX chain's subject "
                   f"needs renaming: 'role asymmetry' would be a property of the contrast's construction (an instrument), NOT a "
                   f"slot prior (there is no slot left). Next probe = the operation: are A_sys/A_usr symmetric in source and write?")

    out = {"prereg": "PREREG_OPX06.md", "SMOKE": SMOKE,
           "chained_to_OPX05": "e110307e317778e9ae9a3cd2f81c6dd9a5ce49ad8bb436ac7ae01b7eb890079c",
           "transformers": transformers.__version__, "layers": LAYERS, "n_pairs": N,
           "asym": {f"{m}_{o}": asym[(m, o)] for (m, o) in CELLS}, "asym_ci": {f"{m}_{o}": ci([boot_asym_pt((m, o), rng.integers(0, NTMPL, NTMPL)) for _ in range(200)]) for (m, o) in CELLS},
           "B_per_cell": {f"{m}_{o}": B[(m, o)] for (m, o) in CELLS}, "mass_per_cell": {f"{m}_{o}": float(mB[(m, o)].mean()) for (m, o) in CELLS},
           "q_joint_rev_over_norm": q, "q_ci": ci(bq),
           "q_DONEsys": qhalf["DONEsys"], "q_READYsys": qhalf["READYsys"],
           "anchor_ratio_JOINTn_over_BASEn": anchor_ratio, "anchor_ci": ci(banchor), "anchor_ok": bool(anchor_ok),
           "opx02_inrun_BASE_flip_keeps_sign": bool(np.sign(aBf) == np.sign(aBn)),  # reproduce OPX-02 role-keep
           "asym_BASE_normal": aBn, "asym_BASE_flipped": aBf, "asym_JOINT_normal": aJn, "asym_JOINT_flipped": aJf,
           "verdict_band": band, "verdict": verdict,
           "scope": "raw dY primary (B~0 at JOINT; M uninterpretable). q=asym_JOINT_rev/asym_JOINT_norm with pre-registered bands "
                    "(<=-0.5 marker-mediated-position / |q|<=0.5 order-destroys / >0.5 no-flip). NO-FLIP points at the PATCHING "
                    "OPERATION (design/instrument), NOT a slot prior -- there is no slot left after the joint strip. Flip "
                    "disambiguated position-vs-target*position via per-counterbalance-half q. Property of these spans/layers/model/"
                    "battery. BASE-n/JOINT-n reproduce OPX-01/05; BASE-f reproduces OPX-02 (role-keep).",
           "runtime_s": round(time.time() - t0, 1)}
    import csv
    with open(os.path.join(OUT, "opx06_arms_smoke.csv" if SMOKE else "opx06_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["cell", "asym", "B", "mass"])
        for (m, o) in CELLS: w.writerow([f"{m}_{o}", round(asym[(m, o)], 4), round(B[(m, o)], 4), round(float(mB[(m, o)].mean()), 3)])
        w.writerow(["q_rev_over_norm", round(q, 4), "", ""])
        w.writerow(["anchor_JOINTn_over_BASEn", round(anchor_ratio, 4), "", ""])
    np.savez(os.path.join(OUT, "opx06_peritem" + ("_smoke" if SMOKE else "") + ".npz"),
             use=np.array(use), tmpl=tmpl, cb=cb,
             **{f"Yb_{m}_{o}": Yb[(m, o)] for (m, o) in CELLS},
             **{f"Ys_{m}_{o}": Ys[(m, o)] for (m, o) in CELLS},
             **{f"Yu_{m}_{o}": Yu[(m, o)] for (m, o) in CELLS})
    fn = os.path.join(OUT, "opx06_smoke.json" if SMOKE else "opx06.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[OPX6] asym BASE_n {aBn:+.2f} BASE_f {aBf:+.2f} JOINT_n {aJn:+.2f} JOINT_f {aJf:+.2f}")
    log(f"[OPX6] q={q:+.3f}{ci(bq)} q_DONE={qhalf['DONEsys']:+.2f} q_READY={qhalf['READYsys']:+.2f} anchor={anchor_ratio:.3f} B_JOINT_n={B[('JOINT','n')]:+.2f} B_JOINT_f={B[('JOINT','f')]:+.2f}")
    log(f"[OPX6] anchor={anchor_ok} band={band} -> {verdict}; wrote {fn}")

if __name__ == "__main__":
    main()
