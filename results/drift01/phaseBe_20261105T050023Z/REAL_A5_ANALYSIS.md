# HUNT-DRIFT-01 A5 — Amendment 5 (9b92498d…) — 120 items × drift / filler / prose — EXPLORATORY

Transcripts 96 · items 120 (60 DONEsys · 60 READYsys) from 30 templates · k ∈ [0, 1, 2, 4, 8, 16, 32] · bootstrap 2000 over templates × seeds, seed 7101001.

Repro gate (first 8 A4 items × 3 arms vs A4's b6_q0): 16128 rows, bitwise 16128, max |Δ| 0 nats (stop above 0.05).

## PRIMARY (Bonferroni, 97.5% CIs)

**P1 — drift − filler, aligned part A over k ∈ {1, 2, 4}, predicted −: A = -1.32 [-1.79, -0.83] → supported** (30 templates)

**P2 — prose − filler, aligned part A over k ∈ {8, 16, 32}, predicted +: A = +1.48 [+1.07, +1.95] → supported** (30 templates)

## S1 — READY part W (95%)

drift − filler, k 1–4: W = +0.22 [-0.18, +0.63] · prose − filler, k 8–32: W = +0.42 [+0.14, +0.72]

## S2 — prose − filler at k = 1 (descriptive; A4: A −0.93, W −0.55)

A = -0.87 [-1.22, -0.44] · W = -0.73 [-1.01, -0.45]

## S3 — A and W at every k (95%)

| contrast | k | A | 95% CI | W | 95% CI |
|---|---|---|---|---|---|
| drift − filler | 1 | -1.78 | [-2.21, -1.36] | -0.00 | [-0.41, +0.43] |
| drift − filler | 2 | -1.23 | [-1.67, -0.78] | +0.25 | [-0.17, +0.68] |
| drift − filler | 4 | -0.95 | [-1.44, -0.42] | +0.42 | [+0.01, +0.83] |
| drift − filler | 8 | -0.82 | [-1.29, -0.33] | +0.69 | [+0.36, +1.04] |
| drift − filler | 16 | -0.27 | [-0.76, +0.24] | +0.68 | [+0.34, +1.06] |
| drift − filler | 32 | +0.12 | [-0.38, +0.62] | +0.60 | [+0.18, +1.01] |
| prose − filler | 1 | -0.87 | [-1.22, -0.44] | -0.73 | [-1.01, -0.45] |
| prose − filler | 2 | -0.27 | [-0.64, +0.15] | -0.46 | [-0.76, -0.14] |
| prose − filler | 4 | +0.44 | [+0.01, +0.91] | -0.21 | [-0.51, +0.09] |
| prose − filler | 8 | +0.57 | [+0.21, +0.94] | +0.12 | [-0.16, +0.40] |
| prose − filler | 16 | +1.28 | [+0.91, +1.69] | +0.51 | [+0.22, +0.81] |
| prose − filler | 32 | +2.59 | [+2.12, +3.15] | +0.63 | [+0.28, +1.01] |
| drift − prose | 1 | -0.91 | [-1.46, -0.39] | +0.73 | [+0.35, +1.10] |
| drift − prose | 2 | -0.96 | [-1.54, -0.36] | +0.71 | [+0.32, +1.11] |
| drift − prose | 4 | -1.39 | [-2.01, -0.76] | +0.63 | [+0.29, +0.98] |
| drift − prose | 8 | -1.38 | [-1.89, -0.88] | +0.57 | [+0.31, +0.84] |
| drift − prose | 16 | -1.54 | [-1.97, -1.15] | +0.17 | [-0.08, +0.44] |
| drift − prose | 32 | -2.47 | [-2.90, -2.05] | -0.03 | [-0.36, +0.28] |

## S4 — A4's S1 for continuity: mean Δ = mean(Y_drift − Y_filler), k 4–32

Δ = -0.48 [-0.91, -0.01] templates × seeds → content-driven (n = 46080)

## S5 — P1 / P2 aligned part by subset (95%)

| subset | templates | P1 A | 95% CI | P2 A | 95% CI |
|---|---|---|---|---|---|
| mode M1 | 30 | -0.54 | [-0.98, -0.06] | +1.45 | [+1.07, +1.88] |
| mode M3 | 30 | -2.10 | [-2.61, -1.56] | +1.51 | [+1.16, +1.92] |
| position early | 13 | -0.49 | [-1.61, +0.55] | +1.64 | [+0.87, +2.39] |
| position late | 20 | -1.78 | [-2.13, -1.40] | +1.24 | [+0.70, +1.87] |

## S6 — prose passages

96 transcripts, 764,955 tokens; target-family words DONE 242 · READY 108 (reported, not filtered).

Single-pass + crop vs fresh pass (reported): n 48, max 0.343, median 0.124 nats.
