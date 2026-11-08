"""HUNT-DRIFT-01 — attractor-metric validation (Wilson step 2; local, no model, EXPLORATORY).
  python attractor_validation.py <pulled full-run folder>
Uses the run's OWN per-turn L16 vectors (phase4.npz). The PLAN §8 loop rule (cos(t, t−p) ≥ 0.95 for some p ≤ 8,
≥ 4 consecutive turns, ≥ 25% of turns) must: FLAG constructed periodic sequences (positive control: real turn
vectors repeated with period p = 1, 2, 3); NOT flag the same vectors with their turn order SHUFFLED (negative
control 1); NOT flag the token-matched word-pool FILLER turns (negative control 2: non-conversational, a different
word salad every turn). If a negative control flags, the 0.95 threshold is lax on mean-pooled residuals (a shared
component) and the run's attractor flags are not evidence. Also reports the cosine distribution between turns of
DIFFERENT transcripts (the floor a 'shared component' would set)."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import drift01_core as D
F = Path(sys.argv[1]); P4 = np.load(F / "REAL_phase4.npz")
tids = sorted({int(k.split("_")[0][1:]) for k in P4.files})
V = {t: P4[f"t{t}_drift_L16"].astype(np.float64) for t in tids}; Fv = {t: P4[f"t{t}_filler_L16"].astype(np.float64) for t in tids}
rng = np.random.default_rng(7101001)
real = sum(D.loops(D.selfsim(V[t]))[0] for t in tids)
shuf = sum(D.loops(D.selfsim(V[t][rng.permutation(len(V[t]))]))[0] for t in tids)
fill = sum(D.loops(D.selfsim(Fv[t]))[0] for t in tids)
pos = {p: sum(D.loops(D.selfsim(np.array([V[t][j % p] for j in range(len(V[t]))])))[0] == 1 and
              D.loops(D.selfsim(np.array([V[t][j % p] for j in range(len(V[t]))])))[1] == p for t in tids) for p in (1, 2, 3)}
adj = np.concatenate([[D.cos(V[t][j], V[t][j - 1]) for j in range(1, len(V[t]))] for t in tids])
cross = np.array([D.cos(V[a][int(rng.integers(len(V[a])))], V[b][int(rng.integers(len(V[b])))]) for a, b in rng.integers(0, len(tids), (2000, 2)) if a != b])
fadj = np.concatenate([[D.cos(Fv[t][j], Fv[t][j - 1]) for j in range(1, len(Fv[t]))] for t in tids])
n = len(tids)
print(f"transcripts {n}")
print(f"REAL drift turns flagged as looping: {real}/{n}")
print(f"POSITIVE control (period p repeated, must flag with that p): " + ", ".join(f"p={p}: {v}/{n}" for p, v in pos.items()))
print(f"NEGATIVE control 1 (real turns, order SHUFFLED, must not flag): {shuf}/{n}")
print(f"NEGATIVE control 2 (token-matched word-pool FILLER, must not flag): {fill}/{n}")
q = lambda x: f"median {np.median(x):.3f}, 5% {np.percentile(x, 5):.3f}, 95% {np.percentile(x, 95):.3f}"
print(f"cos(turn t, t−1), real drift:            {q(adj)}  | share ≥ 0.95: {(adj >= 0.95).mean():.0%}")
print(f"cos(turn t, t−1), filler:                {q(fadj)}  | share ≥ 0.95: {(fadj >= 0.95).mean():.0%}")
print(f"cos(random turns of DIFFERENT transcripts): {q(cross)}  | share ≥ 0.95: {(cross >= 0.95).mean():.0%}")
lax = shuf > 0.05 * n or fill > 0.05 * n
print("VERDICT:", "metric LAX — negative controls flag; attractor flags are not evidence" if lax else
      "metric passes both negative controls; positive control " + ("passes" if all(v == n for v in pos.values()) else "PARTIAL"))
