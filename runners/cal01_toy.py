#!/usr/bin/env python
# CAL-01 -- calibrate the estimator M=-dY/2B against KNOWN ground truth. PREREG_CAL01.md, chained RES-05 f0b75186...
# Hand-built toy transformer (weights set by hand, NOT trained), CPU only, NO Llama forwards. Ground truth M_hat=w by
# construction. Driven by the SAME hook/run/capture/M_of/bootstrap code path as RES-05 (copied verbatim below). Sweep
# w x rederivation x depth = 20 cells; report bias=M_hat-w with CI + slope; sensitivity control proves the toy can
# detect an artifact. Validity gates: patch-replaces-A at w=1, B~-3.9, sensitivity collapses. See PREREG for readings.
import os, json, time, csv
import numpy as np, torch, torch.nn as nn

torch.manual_seed(20260921)
DEV = torch.device("cpu")          # HARD CPU -- never touch the GPU (blast-radius rule)
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
DMODEL = 8
# residual dims: 0=A(span role), 1=B(header role), 2=is_header, 3=is_span, 4=is_readout, 5=readout-value V
DONE, READY = 6, 7                  # toy output token ids
VOCAB = 8
Kc = -1.95                          # unembed scale: logit diff = 2*Kc*V ; baseline V=r -> Y=2Kc=-3.9
NTMPL = 30; ITEMS_PER = 6; NOISE = 0.30; TMPL_SD = 0.15
WS = [0.0, 0.25, 0.5, 0.75, 1.0]
SEED = 20260914
BOOT = 5000
# token ids: 0 hdr r+1, 1 hdr r-1, 2 span r+1, 3 span r-1, 4 readout, 5 filler
def log(*a): print(*a, flush=True)

# ---- embedding lookup (hand-set) ----
EMB = torch.zeros(VOCAB, DMODEL)
EMB[0, 1] = +1.0; EMB[0, 2] = 1.0   # header, role +1
EMB[1, 1] = -1.0; EMB[1, 2] = 1.0   # header, role -1
EMB[2, 0] = +1.0; EMB[2, 3] = 1.0   # span, role +1
EMB[3, 0] = -1.0; EMB[3, 3] = 1.0   # span, role -1
EMB[4, 4] = 1.0                     # readout
# id5 filler -> zeros

HEADER_POS, SPAN_POS, READOUT_POS = 0, [1, 2], 4   # item seq: [hdr, span, span, filler, readout]

class ToyBlock(nn.Module):
    def __init__(self, rederiv, is_aggregator, w):
        super().__init__(); self.rederiv = rederiv; self.agg = is_aggregator; self.w = w
    def forward(self, hidden):
        h = hidden.clone()
        if self.agg:
            # aggregate from INPUT (patched) spans + header -> write readout value V (dim5)
            A = hidden[0, SPAN_POS, 0].mean()
            Bh = hidden[0, HEADER_POS, 1]
            h[0, READOUT_POS, 5] = self.w * A + (1.0 - self.w) * Bh
        elif self.rederiv:
            # re-derive Channel A at spans from the header's role each block (overwrites prior A)
            for p in SPAN_POS:
                h[0, p, 0] = hidden[0, HEADER_POS, 1]
        return (h,)   # tuple -> harness hook uses out[0]

class _Sub(nn.Module):
    def __init__(self, layers): super().__init__(); self.layers = layers

class ToyOut:
    def __init__(self, logits, hidden_states): self.logits = logits; self.hidden_states = hidden_states

class ToyLM(nn.Module):
    def __init__(self, nlayers, rederiv, w):
        super().__init__()
        blocks = [ToyBlock(rederiv, (i == nlayers - 1), w) for i in range(nlayers)]
        self.model = _Sub(nn.ModuleList(blocks))
        self.unemb = torch.zeros(VOCAB, DMODEL); self.unemb[DONE, 5] = Kc; self.unemb[READY, 5] = -Kc
        self.nlayers = nlayers
    def forward(self, input_ids=None, output_hidden_states=False, use_cache=False):
        h = EMB[input_ids[0.unsqueeze(0).clone()      # [1,T,d]
        hs = [h]
        for blk in self.model.layers:
            out = blk(h)                                 # hook fires here, may overwrite out[0] in place
            h = out[0]; hs.append(h)
        logits = torch.einsum("btd,vd->btv", h, self.unemb)   # [1,T,V]
        return ToyOut(logits, tuple(hs) if output_hidden_states else None)

# ---- toy stimuli: items + cross-role twins, counterbalanced, template-clustered ----
def make_items():
    rng = np.random.default_rng(1234)
    items = []
    for t in range(NTMPL):
        toff = float(rng.normal(0, TMPL_SD))
        for k in range(ITEMS_PER):
            r = +1 if (k % 2 == 0) else -1                # counterbalance within template
            hdr = 0 if r == +1 else 1; spn = 2 if r == +1 else 3
            ids = [hdr, spn, spn, 5, 4]
            twin_hdr = 1 if r == +1 else 0; twin_spn = 3 if r == +1 else 2
            twin_ids = [twin_hdr, twin_spn, twin_spn, 5, 4]
            items.append({"tmpl": t, "toff": toff, "r": r, "ids": ids, "twin_ids": twin_ids,
                          "target_sys": "DONE" if r == +1 else "READY",
                          "eb": float(rng.normal(0, NOISE)), "ep": float(rng.normal(0, NOISE))})
    return items

def scale_ids_offset(model, toff):
    # template heterogeneity: scale readout value by (1+toff) equally for A and B (mixture identity preserved)
    model._toff = toff

def run_cell(nlayers, rederiv, w, items, LAYERS_override=None):
    START = nlayers // 4
    LAYERS = LAYERS_override if LAYERS_override is not None else list(range(max(1, START), nlayers))
    model = ToyLM(nlayers, rederiv, w).to(DEV).eval()

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

    def raw_run(ids, repl=None, toff=0.0):
        STATE["repl"] = repl; t = torch.tensor([ids], dtype=torch.long, device=DEV)
        with torch.inference_mode():
            lg = model(input_ids=t, use_cache=False).logits[0, -1, :].float()
        STATE["repl"] = None
        lp = torch.log_softmax(lg * (1.0 + toff), -1)      # toff scales the logit diff (template heterogeneity)
        return float(lp[DONE] - lp[READY])
    def ysig(R, it): return R if it["target_sys"] == "DONE" else -R

    def capture(twin_ids):
        t = torch.tensor([twin_ids], dtype=torch.long, device=DEV)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        return {L: hs[L][0, SPAN_POS, :].detach().clone() for L in LAYERS}
    def build_cross(cap):
        repl = {}
        for L in LAYERS:
            repl[L] = (torch.tensor(SPAN_POS, dtype=torch.long, device=DEV), cap[L].to(torch.float32))
        return repl

    N = len(items); tmpl = np.array([it["tmpl"] for it in items])
    Yb = np.zeros(N); Yc = np.zeros(N)
    patch_ok = None
    for n, it in enumerate(items):
        cap = capture(it["twin_ids"])
        Yb[n] = ysig(raw_run(it["ids"], None, it["toff"]), it) + it["eb"]
        Yc[n] = ysig(raw_run(it["ids"], build_cross(cap), it["toff"]), it) + it["ep"]
        if w == 1.0 and patch_ok is None:
            # validity gate 1: inspect that the patch replaced Channel A at spans with twin's value (-r)
            STATE["repl"] = build_cross(cap)
            with torch.inference_mode():
                hs = model(input_ids=torch.tensor([it["ids", device=DEV),
                           output_hidden_states=True, use_cache=False).hidden_states
            STATE["repl"] = None
            Lc = LAYERS[len(LAYERS) // 2]
            patched_A = float(hs[Lc][0, SPAN_POS[0], 0]); twin_A = float(cap[Lc][0, 0])
            patch_ok = abs(patched_A - twin_A) < 1e-5
    for h in handles: h.remove()

    B = float(Yb.mean())
    def per_t(a): return np.array([a[tmpl == t].mean() if (tmpl == t).any() else 0.0 for t in range(NTMPL)])
    ptB = per_t(Yb); ptC = per_t(Yc - Yb)
    def M_of(pt): return float(-pt.mean() / (2 * ptB.mean())) if abs(ptB.mean()) > 1e-9 else float("nan")
    Mhat = M_of(ptC)
    rng = np.random.default_rng(SEED); bM = np.empty(BOOT)
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL); den = 2 * ptB[pk].mean()
        bM[b] = -ptC[pk].mean() / den if abs(den) > 1e-9 else np.nan
    lo, hi = np.nanpercentile(bM, [2.5, 97.5])
    return {"w": w, "nlayers": nlayers, "rederiv": rederiv, "LAYERS": [LAYERS[0], LAYERS[-1,
            "B": B, "Mhat": Mhat, "bias": Mhat - w, "ci": [float(lo), float(hi)],
            "patch_ok": patch_ok, "Yb": Yb, "Yc": Yc, "tmpl": tmpl}

def main():
    t0 = time.time()
    items = make_items()
    log(f"[CAL] items={len(items)} templates={NTMPL} d_model={DMODEL} (CPU) ({time.time()-t0:.1f}s)")

    # ---- toy VOID discipline: uncontested (single-role) same-content span patch keeps compliance ----
    def void_check():
        model = ToyLM(8, False, 1.0).eval()
        STATE = {"repl": None}; handles = []
        def mk(L):
            def hook(mod, inp, out):
                h = out[0]; r = STATE["repl"]
                if r is not None and L in r: pos, val = r[L]; h[0, pos, :] = val
                return out
            return hook
        LAYERS = list(range(2, 8))
        for L in LAYERS: handles.append(model.model.layers[L - 1].register_forward_hook(mk(L)))
        def comply(ids, repl=None):
            STATE["repl"] = repl
            with torch.inference_mode():
                lg = model(input_ids=torch.tensor([ids]), use_cache=False).logits[0, -1, :].float()
            STATE["repl"] = None
            return 1 if (lg[DONE] - lg[READY]) > 0 else 0
        uok = un = sok = sn = 0
        for r in (+1, -1):
            hdr = 0 if r == +1 else 1; spn = 2 if r == +1 else 3
            ids = [hdr, spn, spn, 5, 4]
            un += 1; uok += comply(ids)
            with torch.inference_mode():
                hs = model(input_ids=torch.tensor([ids]), output_hidden_states=True, use_cache=False).hidden_states
            repl = {L: (torch.tensor(SPAN_POS), hs[L][0, SPAN_POS, :]) for L in LAYERS}  # same-content
            sn += 1; sok += comply(ids, repl)
        for h in handles: h.remove()
        return uok / un, sok / sn
    fu, fs = void_check()
    VOID = bool(fs < 0.90 * fu)
    log(f"[CAL] VOID: unsteered {fu:.3f} steered {fs:.3f} VOID={VOID}")

    cells = []; peritem = {}
    for depth in (4, 32):
        for rederiv in (False, True):
            for w in WS:
                c = run_cell(depth, rederiv, w, items)
                peritem[f"Yb_d{depth}_r{int(rederiv)}_w{w}"] = c.pop("Yb")
                peritem[f"Yc_d{depth}_r{int(rederiv)}_w{w}"] = c.pop("Yc")
                c.pop("tmpl")
                cells.append(c)
                log(f"[CAL] d{depth} rederiv={int(rederiv)} w={w:.2f} -> Mhat={c['Mhat']:+.4f} "
                    f"bias={c['bias']:+.4f} CI{[round(x,3) for x in c['ci'} B={c['B']:+.3f} patch_ok={c['patch_ok']}")

    # slope of Mhat on w per (rederiv, depth) group
    slopes = {}
    for depth in (4, 32):
        for rederiv in (False, True):
            g = [c for c in cells if c["nlayers"] == depth and c["rederiv"] == rederiv]
            ws = np.array([c["w"] for c in g]); ms = np.array([c["Mhat"] for c in g])
            slope = float(np.polyfit(ws, ms, 1)[0])
            slopes[f"d{depth}_r{int(rederiv)}"] = slope

    # ---- sensitivity control: w=1, rederiv on, depth 32, but SKIP the last re-deriving block (block 30 output=hs[31])
    #      so re-derivation should win -> Mhat collapses toward 0 (proves the toy can detect an artifact).
    bad_layers = list(range(8, 31))   # drops L=31 (=block30 output), the last patch before the aggregator's input
    sc = run_cell(32, True, 1.0, items, LAYERS_override=bad_layers)
    log(f"[CAL] SENSITIVITY (w=1,rederiv,d32,skip-last-patch) -> Mhat={sc['Mhat']:+.4f} (expect ~0)")

    # ---- gate summary ----
    B_ok = all(abs(c["B"] - (-3.9)) < 0.2 for c in cells)
    patch_ok_all = all((c["patch_ok"] is None) or c["patch_ok"] for c in cells)
    sens_ok = sc["Mhat"] < 0.3
    max_abs_bias = max(abs(c["bias"]) for c in cells)

    # ---- pre-committed mechanical reading ----
    def cell(depth, rederiv, w): return next(c for c in cells if c["nlayers"] == depth and c["rederiv"] == rederiv and c["w"] == w)
    def biased(c): return not (c["ci"][0] <= 0 <= c["ci"][1])   # CI excludes 0 -> biased
    pinned = [c for c in cells if abs(c["Mhat"] - 0.5) < 0.05 and c["w"] not in (0.5,)]  # pins at .5 regardless of w
    depth_dep = any(biased(cell(32, rd, w)) and not biased(cell(4, rd, w)) and cell(32, rd, w)["bias"] < 0
                    for rd in (False, True) for w in WS)
    rederiv_dep = any(biased(cell(d, True, w)) and not biased(cell(d, False, w)) and cell(d, True, w)["bias"] < 0
                      for d in (4, 32) for w in WS)
    if not (B_ok and patch_ok_all and sens_ok):
        verdict = "GATE-FAIL (calibration invalid; see gate flags)"
    elif pinned:
        verdict = "ARTIFACT-REAL (Mhat pins ~0.5 regardless of w) -- every M in the arc reinterpreted"
    elif rederiv_dep:
        verdict = "ALL-LAYER-PATCHING-DOES-NOT-DEFEAT-RE-DERIVATION (H4 premise contradicted)"
    elif depth_dep:
        verdict = "DEPTH-DEPENDENT-ATTENUATION (real-model M's are FLOORS not estimates)"
    elif max_abs_bias < 0.05:
        verdict = "BIAS~0-EVERYWHERE (no artifact found under any constructed mechanism; the ~half survives)"
    else:
        verdict = "PARTIAL (report band; some cells biased, no single clean mechanism)"

    out = {"prereg": "PREREG_CAL01.md", "chained_to_RES05": "f0b75186bb0068442014cea854131c438183d10e78360eb9b1b157bd47ef3f3c",
           "torch": torch.__version__, "device": "cpu", "n_items": len(items), "NTMPL": NTMPL,
           "Kc": Kc, "noise": NOISE, "cells": cells, "slopes": slopes,
           "sensitivity_control": {"Mhat": sc["Mhat"], "bias": sc["bias"], "ci": sc["ci"], "expect": "~0"},
           "gates": {"B_ok": B_ok, "patch_ok_all": patch_ok_all, "sensitivity_collapses": sens_ok,
                     "max_abs_bias": max_abs_bias, "VOID_unsteered": fu, "VOID_steered": fs, "VOID": VOID},
           "verdict": verdict,
           "asymmetry": "This CAN kill the ~half; it CANNOT certify it. A clean curve licenses 'no artifact found under "
                        "the constructed mechanisms', NEVER 'the number is real'.",
           "runtime_s": round(time.time() - t0, 2)}
    np.savez(os.path.join(OUT, "cal01_peritem.npz"), **peritem)
    with open(os.path.join(OUT, "cal01_arms.csv"), "w", newline="") as fc:
        w_ = csv.writer(fc); w_.writerow(["depth", "rederiv", "w", "Mhat", "bias", "ci_lo", "ci_hi", "B", "patch_ok"])
        for c in cells:
            w_.writerow([c["nlayers"], int(c["rederiv"]), c["w"], round(c["Mhat"],5), round(c["bias"],5),
                         round(c["ci"][0],5), round(c["ci"][1],5), round(c["B"],4), c["patch_ok")
        w_.writerow(["32_SENSITIVITY_skiplast", 1, 1.0, round(sc["Mhat"],5), round(sc["bias"],5),
                     round(sc["ci"][0],5), round(sc["ci"][1],5), round(sc["B"],4), sc["patch_ok")
    json.dump(out, open(os.path.join(OUT, "cal01.json"), "w"), indent=2)
    log(f"[CAL] max|bias|={max_abs_bias:.4f} slopes={ {k:round(v,3) for k,v in slopes.items()} } "
        f"sens={sc['Mhat']:+.3f} gates B={B_ok} patch={patch_ok_all} sens={sens_ok} -> {verdict}")

if __name__ == "__main__":
    main()
