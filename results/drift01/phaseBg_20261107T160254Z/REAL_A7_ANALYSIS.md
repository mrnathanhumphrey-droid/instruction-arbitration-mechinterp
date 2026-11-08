# HUNT-DRIFT-01 A7 — Amendment 7 (a66ef98b…) — follow the system, or go against the user? — EXPLORATORY

Row checks: 960 probe × draw, arms token-identical but for the swaps, N = C but the requested word; longest row 358 tokens. Single-pass + crop vs fresh, C and N (reported): n 48, max 0.404, median 0.125 nats.

Items 120 (60 DONEsys · 60 READYsys) from 30 templates · draws 8 · arms obey, defer, agree, defy · n ∈ [1, 2, 4, 8] · probes C (asks the competing word) and N (asks the system word) · bootstrap 2000 over templates × draws, seed 7101001, the same resamples for C and N.

## PRIMARY (97.5% CIs, Bonferroni over the two)

**P1 — I_C, I = (defer − obey) − (agree − defy) on the conflict probe, A over n ∈ {1, 2, 4, 8}, predicted +: A = +10.19 [+9.15, +11.14] → supported** (30 templates; W = -0.05 [-0.65, +0.53])

**P2 — I_N, the same contrast on the no-conflict probe, predicted −: A = -15.85 [-16.73, -14.99] → supported** (30 templates; W = -0.77 [-1.38, -0.15])

## S1 — each arm minus the n = 0 anchor, probe C (A, 95%)

| arm | n=1 | n=2 | n=4 | n=8 |
|---|---|---|---|---|
| obey | -3.68 [-4.47, -2.91] | -3.91 [-4.74, -3.08] | -3.21 [-4.09, -2.33] | -2.54 [-3.58, -1.50] |
| defer | -1.02 [-2.05, +0.03] | +2.18 [+1.38, +2.98] | +3.27 [+2.48, +4.10] | +3.74 [+2.92, +4.56] |
| agree | -2.84 [-3.63, -2.09] | -1.00 [-1.83, -0.15] | -0.19 [-1.26, +0.97] | +0.04 [-1.25, +1.38] |
| defy | +4.41 [+3.38, +5.47] | +3.95 [+2.99, +4.97] | +3.45 [+2.48, +4.46] | +3.44 [+2.36, +4.53] |

Anchor (n = 0), probe C: mean aligned Y -2.57; mean lp(system word) -11.25, 0% of probes above −0.1 (headroom).

## S1 — each arm minus the n = 0 anchor, probe N (A, 95%)

| arm | n=1 | n=2 | n=4 | n=8 |
|---|---|---|---|---|
| obey | -3.17 [-3.93, -2.43] | -3.36 [-4.23, -2.51] | -2.08 [-2.96, -1.24] | -1.46 [-2.21, -0.71] |
| defer | -10.22 [-11.28, -9.17] | -10.37 [-11.39, -9.37] | -9.08 [-9.93, -8.23] | -9.26 [-10.05, -8.45] |
| agree | +0.76 [+0.27, +1.24] | +1.33 [+0.77, +1.83] | +1.60 [+1.03, +2.16] | +1.74 [+1.13, +2.32] |
| defy | -5.02 [-5.72, -4.30] | -6.90 [-7.68, -6.09] | -8.00 [-8.88, -7.15] | -9.20 [-10.06, -8.35] |

Anchor (n = 0), probe N: mean aligned Y +11.55; mean lp(system word) -7.43, 0% of probes above −0.1 (headroom).

## S2 / S4 — on N: word main effects and pairwise contrasts, pooled over n (95%)

| contrast | A | 95% CI | W | 95% CI |
|---|---|---|---|---|
| assistant word (system − competing) | +0.71 | [-0.06, +1.50] | -0.44 | [-0.80, -0.04] |
| user word (asked competing − asked system) | -3.16 | [-3.76, -2.57] | -0.39 | [-0.73, -0.04] |
| defer − defy (both against the user; defer shows the system word) | -2.45 | [-3.69, -1.25] | -0.83 | [-1.40, -0.18] |
| obey − agree (both do what the user asks) | -3.87 | [-4.59, -3.23] | +0.05 | [-0.34, +0.42] |

## S3 — I_N at each n (95%)

| n | A | 95% CI | W | 95% CI |
|---|---|---|---|---|
| 1 | -12.83 | [-13.66, -12.00] | -0.08 | [-0.73, +0.59] |
| 2 | -15.24 | [-16.12, -14.35] | -0.17 | [-0.75, +0.42] |
| 4 | -16.61 | [-17.55, -15.68] | -1.10 | [-1.71, -0.47] |
| 8 | -18.73 | [-19.58, -17.85] | -1.74 | [-2.31, -1.21] |

## S5 — the no-space readout ("DONE" / "READY", the demo replies' tokens), 97.5%

- P1 I_C: A = +13.45 [+12.06, +14.73] (supported by the same rule; reported); cell-level r with the locked readout +0.985
- P2 I_N: A = -18.45 [-19.66, -17.26] (supported by the same rule; reported); cell-level r with the locked readout +0.988

## S6 — I by position and by counterbalance (A, 95%)

- C, position early: A = +10.64 [+9.51, +11.63] (23 templates)
- C, position late: A = +9.69 [+8.43, +11.02] (19 templates)
- C, DONEsys items: mean I = +10.24 (n 60 items; descriptive)
- C, READYsys items: mean I = +10.14 (n 60 items; descriptive)
- N, position early: A = -15.93 [-16.92, -14.87] (23 templates)
- N, position late: A = -15.48 [-16.57, -14.46] (19 templates)
- N, DONEsys items: mean I = -15.08 (n 60 items; descriptive)
- N, READYsys items: mean I = -16.63 (n 60 items; descriptive)

## S7 — I_C here vs Amendment 6

I_C = +10.19 on 120 fresh items vs A6's +10.41 on the A5 items (different items; descriptive).
