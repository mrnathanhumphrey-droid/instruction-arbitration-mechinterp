# HUNT-DRIFT-01 B-b — B5 pooled drift vs filler + §3 with-instruction — EXPLORATORY

Main transcripts 96 · with-instruction 12 · items 8 · k ∈ [0, 1, 2, 4, 8, 16, 32] · δ = 0.234 Y_signed · two-way bootstrap 2000 (items × seeds), seed 7101001.

Drift / filler token distance mismatches: 0 (must be 0).

## PRIMARY — pooled Δ = mean(Y_drift − Y_filler), k ∈ {4, 8, 16, 32}, all main transcripts

**Δ = -0.62 [-1.86, +0.72] (n = 3072) → indeterminate**

(− = drift pulls the readout further from the system target than token-matched filler, i.e. content-driven decay; + = drift protects.)

## Secondary — Δ per mode × k (band label shown; no verdict carries the headline)

| mode | k=1 | k=2 | k=4 | k=8 | k=16 | k=32 | pooled k ∈ {4..32} |
|---|---|---|---|---|---|---|---|
| all | -1.26 [-2.84, +0.20] indeterminate | -0.90 [-2.38, +0.57] indeterminate | -0.48 [-2.06, +1.09] indeterminate | -0.56 [-2.05, +1.07] indeterminate | -0.72 [-1.98, +0.59] indeterminate | -0.71 [-1.88, +0.41] indeterminate | -0.62 [-1.86, +0.72] indeterminate |
| M1 | -1.06 [-2.17, -0.16] content-driven | -0.75 [-1.93, +0.26] indeterminate | -0.48 [-1.83, +0.84] indeterminate | -0.80 [-2.35, +0.72] indeterminate | -0.92 [-2.16, +0.28] indeterminate | -1.03 [-2.33, +0.02] indeterminate | -0.81 [-2.06, +0.41] indeterminate |
| M3 | -1.46 [-3.77, +0.87] indeterminate | -1.05 [-3.11, +1.12] indeterminate | -0.48 [-2.47, +1.56] indeterminate | -0.33 [-1.93, +1.53] indeterminate | -0.52 [-1.86, +0.96] indeterminate | -0.38 [-1.60, +0.86] indeterminate | -0.43 [-1.80, +1.15] indeterminate |

## §3 — A(k) with-instruction − A(k) matched main (same M1, persona, T 1.0, seed, item); ratio of means, paired, descriptive

| k | A with-instruction | A matched main | difference | pairs |
|---|---|---|---|---|
| 0 | +1.00 | +1.00 | +0.00 | 12 |
| 1 | +0.95 | +0.65 | +0.30 | 12 |
| 2 | +0.65 | +0.58 | +0.07 | 12 |
| 4 | +0.48 | +0.58 | -0.10 | 12 |
| 8 | +0.45 | +0.36 | +0.09 | 12 |
| 16 | +0.28 | +0.32 | -0.04 | 12 |
| 32 | +0.23 | +0.39 | -0.16 | 12 |

Bare-target rate of each with-instruction transcript (assistant turns that are just the system target word):

| with-instruction | item (target) | persona | seed | bare-target turns |
|---|---|---|---|---|
| 0 | c0144 (DONE) | P-none | 7101201 | 0% |
| 1 | c0525 (READY) | P-none | 7101201 | 0% |
| 2 | c0144 (DONE) | P-none | 7101202 | 0% |
| 3 | c0525 (READY) | P-none | 7101202 | 0% |
| 4 | c0144 (DONE) | P-neutral | 7101201 | 0% |
| 5 | c0525 (READY) | P-neutral | 7101201 | 0% |
| 6 | c0144 (DONE) | P-neutral | 7101202 | 0% |
| 7 | c0525 (READY) | P-neutral | 7101202 | 0% |
| 8 | c0144 (DONE) | P-curious | 7101201 | 0% |
| 9 | c0525 (READY) | P-curious | 7101201 | 0% |
| 10 | c0144 (DONE) | P-curious | 7101202 | 0% |
| 11 | c0525 (READY) | P-curious | 7101202 | 0% |

## Single-pass + crop vs fresh pass (reported; A3.3) — n = 48, max 0.547, median 0.100 nats

| condition | n | median | max |
|---|---|---|---|
| drift | 14 | 0.094 | 0.381 |
| filler | 18 | 0.091 | 0.381 |
| none | 16 | 0.112 | 0.547 |

Drift and filler are token-matched at every k, so both are computed in identical kernel shapes; the gap is a per-unit numeric error, not a bias by condition, unless the rows above differ by condition.
