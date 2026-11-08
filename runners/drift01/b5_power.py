"""HUNT-DRIFT-01 B5 power read (EXPLORATORY, descriptive; no verdict). Local, numpy only.
  python b5_power.py <pulled B-b folder> [TAG]
Δ rows = Y_drift − Y_filler, main transcripts, k ∈ {4, 8, 16, 32} (the B5 primary set). Cell means over the balanced
items × seeds grid (8 × 8; 12 transcripts × 4 k per cell) → two-way random-effects ANOVA: σ²_item, σ²_seed, σ²_resid.
Projected SE(Δ̄) = sqrt(σ²_i/I + σ²_s/S + σ²_r/(I·S)); the pooled bootstrap CI half-width is shown beside the ANOVA's
for calibration and every projection is reported on both scales. Power = P(upper 95% bound < 0 AND point < −δ)
under a true Δ (normal approximation)."""
import json, sys
from pathlib import Path
from math import erf, sqrt
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D
import phaseb_core as B
sys.stdout.reconfigure(encoding="utf-8")
C = [json.loads(l) for l in open(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl", encoding="utf-8")]
F = Path(sys.argv[1]); TAG = sys.argv[2] if len(sys.argv) > 2 else "REAL_"
q = np.load(F / f"{TAG}b5_q0.npz")["rows"]; cells = json.loads((F / f"{TAG}b5_transcripts_manifest.json").read_text(encoding="utf-8"))["cells"]
q = q[(q[:, 0] < B.WI_TID0) & np.isin(q[:, 3], (4, 8, 16, 32))]
Y = D.y_signed(q[:, 4], q[:, 5], [C[int(i)]["target_sys"] for i in q[:, 1]])
key = lambda r: (int(r[0]), int(r[1]), int(r[3]))
dr = {key(r): y for r, y in zip(q, Y) if r[2] == 0}; fi = {key(r): y for r, y in zip(q, Y) if r[2] == 1}
items = sorted({k[1] for k in dr}); seeds = sorted({c[3] for c in cells})
M = np.zeros((len(items), len(seeds))); N = np.zeros_like(M)
for k, y in dr.items():
    i, s = items.index(k[1]), seeds.index(cells[k[0]][3]); M[i, s] += y - fi[k]; N[i, s] += 1
assert (N == N[0, 0]).all(), "unbalanced grid"
M /= N; I, S = M.shape; g = M.mean()
ms_i = S * ((M.mean(1) - g) ** 2).sum() / (I - 1); ms_s = I * ((M.mean(0) - g) ** 2).sum() / (S - 1)
res = M - M.mean(1, keepdims=True) - M.mean(0, keepdims=True) + g; ms_r = (res ** 2).sum() / ((I - 1) * (S - 1))
vi, vs, vr = max((ms_i - ms_r) / S, 0), max((ms_s - ms_r) / I, 0), ms_r
se = lambda I_, S_: sqrt(vi / I_ + vs / S_ + vr / (I_ * S_))
boot_hw = (0.72 - (-1.86)) / 2                       # the reported primary CI [−1.86, +0.72]
cal = boot_hw / (1.96 * se(I, S))
Phi = lambda x: 0.5 * (1 + erf(x / sqrt(2)))
power = lambda d, s_: Phi((abs(d) - 1.96 * s_) / s_) if abs(d) > D.BAND else 0.0
print(f"grid {I} items × {S} seeds, {int(N[0, 0])} rows per cell; Δ̄ = {g:+.3f}")
tot = vi + vs + vr / 1
print(f"variance of a cell mean: item {vi:.3f} · seed {vs:.3f} · item×seed+within {vr:.3f}  "
      f"(shares {vi / tot:.0%} / {vs / tot:.0%} / {vr / tot:.0%})")
print(f"SE of Δ̄ now: item {sqrt(vi / I):.3f}, seed {sqrt(vs / S):.3f}, resid {sqrt(vr / (I * S)):.3f} → ANOVA 95% half-width "
      f"{1.96 * se(I, S):.2f} vs bootstrap {boot_hw:.2f} (bootstrap / ANOVA = {cal:.2f}; projections below shown on both)")
print("\nprojected 95% half-width [ANOVA | bootstrap-scaled] and power to call content-driven at true Δ = −0.62 / −0.40")
print("items  seeds   half-width        power(−0.62)    power(−0.40)")
for S_ in (8, 16):
    for I_ in (8, 16, 24, 32, 48, 64):
        s_ = se(I_, S_)
        print(f"{I_:5d} {S_:6d}   {1.96 * s_:.2f} | {1.96 * s_ * cal:.2f}     {power(-0.62, s_):.2f} | {power(-0.62, s_ * cal):.2f}     "
              f"{power(-0.40, s_):.2f} | {power(-0.40, s_ * cal):.2f}")
print("\nitem means (Δ by item, pooled over seeds):", " ".join(f"{C[it]['id']} {m:+.2f}" for it, m in zip(items, M.mean(1))))
print("seed means:", " ".join(f"{s} {m:+.2f}" for s, m in zip(seeds, M.mean(0))))
