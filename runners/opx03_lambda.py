#!/usr/bin/env python
# OPX-03 -- which TEXTUAL FEATURE carries the OPX-01 role-dominance asymmetry (A_sys -0.93 / A_usr +1.90): the role-word
# MARKER, or the system-only date PREAMBLE (which also pushes the system span deeper = within-block OFFSET)?
# Arms (normal order; one-sided same-index span patch from the cb-flip twin, L8-31; twin surged the SAME way per arm):
#   (i)  BASE    : as OPX-01 (anchor, A_sys ~ -0.93 / A_usr ~ +1.90)
#   (ii) NEUTRAL : both role-word header tokens -> a single neutral word (markers indistinguishable)
#   (iii) PM     : NEUTRAL + system date preamble STRIPPED (both blocks structurally identical: [header][\n\n][content],
#                  matched within-block offset). CONSTRUCTION CHECK -- asym should collapse to ~0; if it SURVIVES the
#                  enumeration is incomplete (a tell nobody listed), NOT a "deep prior". Failure => go find the tell.
# asym(arm) = M(A_usr) - M(A_sys). marker share = asym(BASE)-asym(NEUTRAL); preamble/offset share = asym(NEUTRAL)-asym(PM);
# residual = asym(PM) (construction check). M per arm uses that arm's own baseline B (surgery changes B).
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
NEUTRAL = "info"                                          # neutral role word (both headers); single-token, verified pre-lock
HDR_END = "<|end_header_id|>\n\n"
NTMPL = 30; BOOT = 300 if SMOKE else 5000; SEED = 20260925
ARMS = ["BASE", "NEUTRAL", "PM"]
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
    log(f"[OPX3] model on {dev}; tf {transformers.__version__} L{LAYERS[0]}..{LAYERS[-1]} NEUTRAL={NEUTRAL!r} ({time.time()-t0:.0f}s)")

    def render(it):
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

    def variant(it, mode):
        """return (ids, si, ui) for the item under mode in {BASE,NEUTRAL,PM}, or None on failure."""
        text = render(it)
        if mode in ("NEUTRAL", "PM"):
            for role in ("system", "user"):
                text = text.replace(f"<|start_header_id|>{role}<|end_header_id|>", f"<|start_header_id|>{NEUTRAL}<|end_header_id|>")
        if mode == "PM":
            h = text.find(HDR_END)                                   # after the (former-system) header
            if h < 0: return None
            h += len(HDR_END); c = text.find(it["system"])          # start of actual system content
            if c > h: text = text[:h] + text[c:]                    # excise the preamble between header and content
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]
        def sp(imp):
            cs = text.find(imp)
            if cs < 0: return None
            ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        imp_s = TEMPLATES[it["template_idx"]].format(T=it["target_sys"])
        imp_u = TEMPLATES[it["template_idx"]].format(T=it["target_usr"])
        si = sp(imp_s); ui = sp(imp_u)
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

    # usable: all 3 modes build for item AND twin, spans same-index aligned in every mode
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
    log(f"[OPX3] usable={len(use)} skipped={len(stim)-len(use)} ({time.time()-t0:.0f}s)")

    tmpl = np.array([stim[i]["template_idx"] for i in use]); N = len(use)
    Yb = {m: np.zeros(N) for m in ARMS}
    Ys = {m: np.zeros(N) for m in ARMS}; Yu = {m: np.zeros(N) for m in ARMS}
    ms = {m: np.zeros(N) for m in ARMS}
    for n, i in enumerate(use):
        it = stim[i]; tw = twin_of[i]
        for m in ARMS:
            ids, si, ui = variant(it, m); tids, tsi, tui = variant(stim[tw], m)
            cap = capture(tids, tsi, tui)
            rb, mb = run(ids); Yb[m][n] = ysig(rb, it); ms[m][n] = mb
            Ys[m][n] = ysig(run(ids, repl_one(si, cap, "s"))[0], it)   # A_sys: item sys-span <- twin sys-span
            Yu[m][n] = ysig(run(ids, repl_one(ui, cap, "u"))[0], it)   # A_usr: item usr-span <- twin usr-span
        if (n + 1) % 60 == 0: log(f"[OPX3] {n+1}/{N} ({time.time()-t0:.0f}s)")
    for h in handles: h.remove()

    def per_t(a): return np.array([a[tmpl == tt].mean() if (tmpl == tt).any() else 0.0 for tt in range(NTMPL)])
    B = {m: float(Yb[m].mean()) for m in ARMS}
    ptB = {m: per_t(Yb[m]) for m in ARMS}
    pts = {m: per_t(Ys[m] - Yb[m]) for m in ARMS}; ptu = {m: per_t(Yu[m] - Yb[m]) for m in ARMS}
    def Mof(pt, m): return float(-pt.mean() / (2 * ptB[m].mean())) if abs(ptB[m].mean()) > 1e-9 else float("nan")
    Ms = {m: Mof(pts[m], m) for m in ARMS}; Mu = {m: Mof(ptu[m], m) for m in ARMS}
    asym = {m: Mu[m] - Ms[m] for m in ARMS}
    marker_share = asym["BASE"] - asym["NEUTRAL"]; preamble_share = asym["NEUTRAL"] - asym["PM"]; residual = asym["PM"]

    rng = np.random.default_rng(SEED)
    def bootpair(arr_s, arr_u, m):
        # returns array of asym over boots for mode m
        out = np.empty(BOOT)
        for b in range(BOOT):
            pk = rng.integers(0, NTMPL, NTMPL); den = 2 * ptB[m][pk].mean()
            if abs(den) < 1e-9: out[b] = np.nan; continue
            out[b] = (-ptu[m][pk].mean() / den) - (-pts[m][pk].mean() / den)
        return out
    rng = np.random.default_rng(SEED); bas = {m: bootpair(pts[m], ptu[m], m) for m in ARMS}
    # shares with shared resample
    rng = np.random.default_rng(SEED); bmk = np.empty(BOOT); bpre = np.empty(BOOT); bres = np.empty(BOOT)
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL)
        a = {}
        for m in ARMS:
            den = 2 * ptB[m][pk].mean()
            a[m] = np.nan if abs(den) < 1e-9 else (-ptu[m][pk].mean() / den) - (-pts[m][pk].mean() / den)
        bmk[b] = a["BASE"] - a["NEUTRAL"]; bpre[b] = a["NEUTRAL"] - a["PM"]; bres[b] = a["PM"]
    def ci(x): lo, hi = np.nanpercentile(x, [2.5, 97.5]); return [float(lo), float(hi)]

    anchor_ok = abs(Ms["BASE"] - (-0.930)) <= 0.15 and abs(Mu["BASE"] - 1.899) <= 0.20
    constr_pass = abs(residual) <= 0.30                       # arm (iii): asym should collapse toward 0
    if not anchor_ok:
        verdict = f"ANCHOR-FAIL BASE A_sys={Ms['BASE']:.3f} A_usr={Mu['BASE']:.3f} (harness diverged)"
    elif not constr_pass:
        verdict = (f"CONSTRUCTION-CHECK FAIL: asym survives at PM ({residual:+.3f}) -> ENUMERATION INCOMPLETE, an unlisted "
                   f"tell remains; do NOT read as a slot prior")
    elif marker_share >= 0.6 * abs(asym["BASE"]):
        verdict = "MARKER-CARRIES (role-word token carries the majority of the asymmetry)"
    elif preamble_share >= 0.6 * abs(asym["BASE"]):
        verdict = "PREAMBLE/OFFSET-CARRIES (the system date preamble / within-block offset carries the majority)"
    else:
        verdict = "SPLIT (marker + preamble each carry part; report shares)"

    out = {"prereg": "PREREG_OPX03.md", "SMOKE": SMOKE,
           "chained_to_OPX02": "bce394380057a6811512d84dbcdf5634c5e7590c816cfe303299df1b99db0d82",
           "transformers": transformers.__version__, "layers": LAYERS, "NEUTRAL": NEUTRAL, "n_pairs": N,
           "B": B, "mass": {m: float(ms[m].mean()) for m in ARMS},
           "M_A_sys": Ms, "M_A_usr": Mu, "asym_usr_minus_sys": asym, "asym_ci": {m: ci(bas[m]) for m in ARMS},
           "marker_share": marker_share, "marker_share_ci": ci(bmk),
           "preamble_offset_share": preamble_share, "preamble_share_ci": ci(bpre),
           "residual_asym_at_PM": residual, "residual_ci": ci(bres),
           "anchor_base_reproduces_opx01": bool(anchor_ok), "construction_check_PM_collapses": bool(constr_pass),
           "verdict": verdict,
           "scope": "arm (iii) PM is a CONSTRUCTION CHECK: survival => enumeration incomplete (find the tell), not a slot prior "
                    "(nothing left to key on once marker+preamble gone, order already OPX-02-killed). Candidates are textual "
                    "features (marker, preamble/offset); 'training prior' is the explanation for whichever wins, not a row. "
                    "Property of these spans/layers/model/battery, normal order. NEUTRAL='info' (both headers).",
           "runtime_s": round(time.time() - t0, 1)}
    import csv
    with open(os.path.join(OUT, "opx03_arms_smoke.csv" if SMOKE else "opx03_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["arm", "M_A_sys", "M_A_usr", "asym", "B", "mass"])
        for m in ARMS: w.writerow([m, round(Ms[m], 4), round(Mu[m], 4), round(asym[m], 4), round(B[m], 4), round(float(ms[m].mean()), 3)])
        w.writerow(["marker_share", round(marker_share, 4), "", "", "", ""])
        w.writerow(["preamble_offset_share", round(preamble_share, 4), "", "", "", ""])
        w.writerow(["residual_at_PM", round(residual, 4), "", "", "", ""])
    np.savez(os.path.join(OUT, "opx03_peritem" + ("_smoke" if SMOKE else "") + ".npz"),
             use=np.array(use), tmpl=tmpl, **{f"Yb_{m}": Yb[m] for m in ARMS},
             **{f"Ys_{m}": Ys[m] for m in ARMS}, **{f"Yu_{m}": Yu[m] for m in ARMS})
    fn = os.path.join(OUT, "opx03_smoke.json" if SMOKE else "opx03.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[OPX3] asym BASE {asym['BASE']:+.3f} NEUTRAL {asym['NEUTRAL']:+.3f} PM {asym['PM']:+.3f}")
    log(f"[OPX3] marker_share {marker_share:+.3f}{ci(bmk)} preamble_share {preamble_share:+.3f}{ci(bpre)} residual {residual:+.3f}{ci(bres)}")
    log(f"[OPX3] anchor={anchor_ok} constr_collapse={constr_pass} -> {verdict}; wrote {fn}")

if __name__ == "__main__":
    main()
