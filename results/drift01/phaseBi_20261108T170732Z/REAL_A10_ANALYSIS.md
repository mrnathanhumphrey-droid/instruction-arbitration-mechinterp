# HUNT-DRIFT-01 A10 — Amendment 10 (cec4ef76…) — stance toward the user, or a word function learned in context? — EXPLORATORY

Row checks: 960 probe × draw × 4 renderings, arms token-identical but for the swaps; longest rows {'native': 358, 'headers': 358, 'quoted': 331, 'stated': 430}. Prefill / crop vs fresh (reported): n 48, max 0.312, median 0.108 nats.
S7 repro gate: native vs A7's C rows, 1032 rows, bitwise 1032, max |Δ| 0.000, median 0.000 nats (tol 0.05).

Items 120 (60 DONEsys · 60 READYsys) from 30 templates · draws 8 · arms obey, defer, agree, defy · n ∈ [1, 2, 4, 8] · probe C · renderings native, headers, quoted, stated · bootstrap 2000 over templates × draws, seed 7101001, the same resamples for every rendering; differences paired per cell.

## PRIMARY (97.5% CIs, Bonferroni over the two)

**P1 — D_rel = I_native − I_headers (role headers → Sam / Alex), A over n ∈ {1, 2, 4, 8}, predicted +: A = +3.06 [+2.29, +3.82] → supported** (30 templates; W = +0.74 [+0.14, +1.35])

**P2 — I_stated (every demo user turn asks for the other word), predicted −: A = +4.12 [+2.97, +5.25] → contradicted** (30 templates; W = -0.37 [-0.82, +0.12])

## S1 / S2 — I per rendering and differences from native (A, 95%)

| rendering | I | 95% CI | share of native | native − this | 95% CI |
|---|---|---|---|---|---|
| native | +10.19 | [+9.28, +11.02] | 1 | — | — |
| headers | +7.13 | [+6.41, +7.80] | 0.70 | +3.06 | [+2.39, +3.74] |
| quoted | +9.18 | [+8.14, +10.19] | 0.90 | +1.01 | [-0.13, +2.12] |
| stated | +4.12 | [+3.12, +5.09] | 0.40 | +6.07 | [+4.89, +7.18] |

The quoted log removes the chat form as well as the roles: a drop there can be format, not role (A10.4 S2).

## S3 — dose: I at each n, and intercept (n = 1) + slope per doubling of n (A, 95%)

| rendering | n=1 | n=2 | n=4 | n=8 | intercept | slope / doubling |
|---|---|---|---|---|---|---|
| native | +9.91 [+8.61, +11.13] | +11.05 [+9.97, +12.08] | +10.11 [+9.04, +11.08] | +9.68 [+8.65, +10.66] | +10.43 [+9.15, +11.65] | -0.16 [-0.65, +0.33] |
| headers | +5.17 [+4.41, +5.98] | +7.62 [+6.84, +8.38] | +8.14 [+7.25, +8.96] | +7.59 [+6.74, +8.36] | +5.97 [+5.19, +6.76] | +0.78 [+0.45, +1.11] |
| quoted | +7.20 [+6.19, +8.25] | +9.62 [+8.56, +10.65] | +10.18 [+8.95, +11.35] | +9.71 [+8.44, +10.99] | +7.96 [+6.96, +8.97] | +0.81 [+0.43, +1.23] |
| stated | +5.04 [+4.28, +5.77] | +5.58 [+4.50, +6.65] | +4.12 [+2.91, +5.30] | +1.74 [+0.20, +3.16] | +5.82 [+5.05, +6.59] | -1.14 [-1.57, -0.72] |

## S4 — disruption check: word main effects per rendering, pooled over n (A, 95%)

| rendering | assistant word (system − competing) | user word (asked competing − asked system) |
|---|---|---|
| native | +0.28 [-0.36, +0.88] | -2.05 [-2.62, -1.49] |
| headers | -0.20 [-0.74, +0.32] | +1.25 [+0.82, +1.66] |
| quoted | +3.91 [+3.09, +4.77] | +1.53 [+1.08, +1.97] |
| stated | -2.95 [-3.42, -2.45] | +1.94 [+1.36, +2.52] |

## S5 — each arm minus the n = 0 anchor, native (A, 95%)

| arm | n=1 | n=2 | n=4 | n=8 |
|---|---|---|---|---|
| obey | -3.68 [-4.47, -2.91] | -3.91 [-4.74, -3.08] | -3.21 [-4.09, -2.33] | -2.54 [-3.58, -1.50] |
| defer | -1.02 [-2.05, +0.03] | +2.18 [+1.38, +2.98] | +3.27 [+2.48, +4.10] | +3.74 [+2.92, +4.56] |
| agree | -2.84 [-3.63, -2.09] | -1.00 [-1.83, -0.15] | -0.19 [-1.26, +0.97] | +0.04 [-1.25, +1.38] |
| defy | +4.41 [+3.38, +5.47] | +3.95 [+2.99, +4.97] | +3.45 [+2.48, +4.46] | +3.44 [+2.36, +4.53] |

## S5 — each arm minus the n = 0 anchor, headers (A, 95%)

| arm | n=1 | n=2 | n=4 | n=8 |
|---|---|---|---|---|
| obey | -1.61 [-2.47, -0.72] | -1.78 [-2.57, -0.97] | -0.84 [-1.73, +0.04] | +0.49 [-0.54, +1.48] |
| defer | -0.45 [-1.32, +0.38] | +2.56 [+1.74, +3.37] | +3.80 [+2.94, +4.67] | +3.80 [+2.92, +4.72] |
| agree | -1.86 [-2.56, -1.17] | -1.66 [-2.38, -0.94] | -2.52 [-3.32, -1.69] | -3.54 [-4.32, -2.73] |
| defy | +2.16 [+1.39, +2.96] | +1.62 [+0.92, +2.30] | +0.99 [+0.32, +1.67] | +0.74 [-0.13, +1.61] |

## S5 — each arm minus the n = 0 anchor, quoted (A, 95%)

| arm | n=1 | n=2 | n=4 | n=8 |
|---|---|---|---|---|
| obey | -2.21 [-3.10, -1.28] | -1.80 [-2.85, -0.77] | -0.59 [-1.88, +0.60] | +0.93 [-0.53, +2.31] |
| defer | +3.31 [+2.28, +4.33] | +7.65 [+6.68, +8.70] | +9.33 [+8.27, +10.39] | +10.05 [+9.10, +10.99] |
| agree | +0.26 [-0.61, +1.15] | +1.63 [+0.73, +2.52] | +1.99 [+0.93, +3.03] | +1.98 [+0.86, +3.02] |
| defy | +1.93 [+1.12, +2.72] | +1.80 [+0.92, +2.65] | +2.26 [+1.27, +3.25] | +2.57 [+1.44, +3.71] |

## S5 — each arm minus the n = 0 anchor, stated (A, 95%)

| arm | n=1 | n=2 | n=4 | n=8 |
|---|---|---|---|---|
| obey | +2.14 [+1.36, +2.96] | +4.56 [+3.71, +5.44] | +4.60 [+3.78, +5.47] | +5.19 [+4.31, +6.06] |
| defer | +1.06 [+0.28, +1.90] | +5.08 [+4.41, +5.75] | +4.47 [+3.66, +5.32] | +2.32 [+1.29, +3.38] |
| agree | -1.93 [-2.78, -1.02] | -0.05 [-0.99, +0.93] | -0.31 [-1.37, +0.76] | -0.75 [-1.90, +0.43] |
| defy | +4.18 [+3.10, +5.16] | +5.00 [+4.15, +5.82] | +3.94 [+2.97, +4.87] | +3.86 [+2.67, +4.94] |

Anchor (n = 0, shared): mean aligned Y -2.57.

## S6 — the no-space readout ("DONE" / "READY", the demo replies' tokens), 97.5%

- P1 D_rel: A = +4.51 [+3.47, +5.54] (supported by the same rule; reported)
- P2 I_stated: A = +5.04 [+3.65, +6.38] (contradicted by the same rule; reported)
- cell-level r, locked vs no-space readout, all renderings: +0.985
