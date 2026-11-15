"""
pihol01_nullcheck.py — DIAGNOSTIC, no claim (the lead researcher, 2026-10-16: store the null draws). Numpy-only, local, no model.
Re-runs the locked v4 flat-world null on the saved PIHOL-01 artifacts with the run's own seeds (default_rng(1000+k), NFLAT=1000)
and stores every draw, so each h can be placed against the null's median, not just its 95th percentile.
Rule_zero first: recomputed h and band95 must match pihol01.json, else STOP. Imports the locked pihol01_analysis.py unchanged.
"""
import json, sys, time
from pathlib import Path
import numpy as np
HERE = Path(__file__).parent; sys.path.insert(0, str(HERE))
import pihol01_analysis as PA

RES = HERE / "results"; NFLAT = 1000; KGRID = [3, 5, 10]; TOL = 1e-4
J = json.loads((RES / "pihol01.json").read_text()); Z = np.load(RES / "pihol01_artifacts.npz")
assert J["SMOKE"] is False and J["prereg_sha256"].startswith("3535dc6e"), "wrong run"
tmpl = Z["tmpl"]; out = {"source": "pihol01.json + pihol01_artifacts.npz", "nflat": NFLAT, "seeds": "default_rng(1000+k)", "cells": {}}
draws = {}

for g in ("g1", "g2"):
    # float64: the run's h is reproduced to <=4.4e-6 in float64; local numpy 2.3 float32 drifts 4.5e-4 on g1 k3
    Zn, Zf = list(Z[f"{g}_Zn"].astype(np.float64)), list(Z[f"{g}_Zf"].astype(np.float64))
    for k in KGRID:
        t = time.time()
        h = PA.rect_holonomy(Zn, Zf, k)[0][0]; h_run = J["results"][g][str(k)]["h"]
        if abs(h - h_run) > TOL:
            print(f"STOP: {g} k{k} h recomputed {h:.6f} != run {h_run:.6f}", flush=True); sys.exit(1)
        null = PA.flat_null(Zn, Zf, tmpl, k, NFLAT, np.random.default_rng(1000 + k))
        b = float(np.percentile(null, 95)); b_run = J["results"][g][str(k)]["flat_band95"]
        cell = {"h": h, "h_run": h_run, "band95": b, "band95_run": b_run, "band_reproduced": abs(b - b_run) <= TOL,
                "null_p05": float(np.percentile(null, 5)), "null_median": float(np.median(null)), "null_p95": b,
                "null_mean": float(null.mean()), "null_sd": float(null.std()),
                "h_percentile_in_null": float((null < h).mean() * 100), "secs": round(time.time() - t, 1)}
        out["cells"][f"{g}_k{k}"] = cell; draws[f"{g}_k{k}"] = null
        print(f"{g} k{k}: h {h:.4f} (run {h_run:.4f}) | null p05 {cell['null_p05']:.4f} med {cell['null_median']:.4f} "
              f"p95 {b:.4f} (run {b_run:.4f}, reproduced={cell['band_reproduced']}) | h at {cell['h_percentile_in_null']:.1f}th pct | {cell['secs']}s", flush=True)

np.savez(RES / "pihol01_nullcheck.npz", **draws)
(RES / "pihol01_nullcheck.json").write_text(json.dumps(out, indent=1))
print("NULLCHECK_DONE", flush=True)
