# HUNT-DRIFT-01 A6 — Amendment 6 (1e6de4f1…) — demonstration factorial — EXPLORATORY

Row checks: 960 probe × draw, arms token-identical but for the swaps; longest row 356 tokens. Single-pass + crop vs fresh (reported): n 48, max 0.533, median 0.099 nats.
Anchors (n = 0) vs A5's k = 0 rows of the P-none transcripts: bitwise on 0 / 120 probes (reported).

Items 120 (60 DONEsys · 60 READYsys) from 30 templates · draws 8 · arms obey, defer, agree, defy · n ∈ [1, 2, 4, 8] · bootstrap 2000 over templates × draws, seed 7101001.

## PRIMARY (95% CI)

**P1 — I = (defer − obey) − (agree − defy), aligned part A over n ∈ {1, 2, 4, 8}, predicted +: A = +10.41 [+9.36, +11.44] → supported** (30 templates; W = +0.54 [+0.03, +1.05])

## S1 — each arm minus the n = 0 anchor (A, 95%)

| arm | n=1 | n=2 | n=4 | n=8 |
|---|---|---|---|---|
| obey | -3.34 [-4.05, -2.58] | -3.48 [-4.21, -2.74] | -2.80 [-3.68, -1.88] | -2.26 [-3.35, -1.19] |
| defer | -0.29 [-1.13, +0.54] | +2.97 [+2.11, +3.73] | +3.95 [+3.08, +4.75] | +4.49 [+3.61, +5.34] |
| agree | -2.36 [-3.15, -1.57] | -0.42 [-1.24, +0.47] | +0.28 [-0.79, +1.36] | +0.45 [-0.75, +1.63] |
| defy | +4.41 [+3.40, +5.47] | +4.23 [+3.27, +5.21] | +4.04 [+3.03, +5.06] | +3.92 [+2.86, +4.95] |

Anchor (n = 0) mean aligned Y: -3.06.

## S2 / S5 — main effects and pairwise contrasts, pooled over n (95%)

| contrast | A | 95% CI | W | 95% CI |
|---|---|---|---|---|
| assistant word (system − competing) | +0.54 | [-0.06, +1.15] | +0.33 | [+0.04, +0.63] |
| user word (asked competing − asked system) | -1.91 | [-2.55, -1.25] | +0.16 | [-0.19, +0.49] |
| defer − agree | +3.29 | [+2.33, +4.20] | +0.43 | [-0.06, +0.95] |
| obey − defy | -7.12 | [-7.84, -6.40] | -0.11 | [-0.46, +0.22] |

## S3 — I at each n (95%)

| n | A | 95% CI | W | 95% CI |
|---|---|---|---|---|
| 1 | +9.81 | [+8.65, +11.06] | +0.45 | [-0.16, +1.07] |
| 2 | +11.09 | [+10.03, +12.18] | +0.89 | [+0.32, +1.43] |
| 4 | +10.51 | [+9.32, +11.63] | +0.47 | [-0.18, +1.11] |
| 8 | +10.23 | [+8.87, +11.52] | +0.37 | [-0.41, +1.12] |

## S4 — I by position and by counterbalance (A, 95%)

- position early: A = +10.77 [+8.91, +12.43] (13 templates)
- position late: A = +9.48 [+8.21, +10.76] (20 templates)
- DONEsys items: mean I = +9.87 (n 60 items; descriptive)
- READYsys items: mean I = +10.96 (n 60 items; descriptive)

## Reported only (post-lock, not in A6) — Y read on the no-space tokens "DONE" / "READY" (the demo replies' tokens)

| contrast, pooled over n | A | 95% CI | W | 95% CI |
|---|---|---|---|---|
| I = (defer − obey) − (agree − defy) | +13.56 | [+12.25, +14.79] | +0.42 | [-0.30, +1.12] |
| assistant word (system − competing) | +0.71 | [-0.08, +1.50] | +0.31 | [-0.07, +0.68] |
| user word (asked competing − asked system) | -2.68 | [-3.50, -1.86] | -0.15 | [-0.56, +0.26] |

Cell-level Pearson r, locked Y vs no-space Y (all item × draw × arm × n): +0.986. Anchor mean aligned Y, no-space: -3.77.
