# HUNT-DRIFT-01 A8 — Amendment 8 (6bc527cd…) — the k = 1 splice — EXPLORATORY

Row checks: 23040 pair × cell × item (spliced turns = their sources' ids; filler token-matched; unspliced = A5's rows); longest row 419 tokens. Prefill + probe vs a fresh pass (reported): n 48, max 0.490, median 0.121 nats.

Items 120 (60 DONEsys · 60 READYsys) from 30 templates · 48 M1 / M3 pairs (8 seeds) · cells M1.M1, M3.M3, M1.M3, M3.M1 (user turn . reply) · Δ = drift − filler at k = 1 · bootstrap 2000 over templates × seeds, seed 7101001.

## PRIMARY (95% CI)

**P1 — R  reply effect (answer − clarification), aligned part A, predicted −: A = -1.27 [-1.78, -0.78] → supported** (30 templates; W = -0.15 [-0.49, +0.19])

## S1 / S2 — user-turn effect and interaction (95%)

| contrast | A | 95% CI | W | 95% CI |
|---|---|---|---|---|
| U  user-turn effect (question − 'Continue.') | -0.82 | [-1.33, -0.30] | -0.23 | [-0.62, +0.14] |
| R × U interaction | -0.95 | [-1.35, -0.59] | +0.34 | [-0.05, +0.75] |

## S3 — each cell's Δ (drift − filler, k = 1; 95%)

| cell | A | 95% CI | W | 95% CI |
|---|---|---|---|---|
| M1.M1 | -0.40 | [-0.95, +0.13] | +0.31 | [-0.10, +0.70] |
| M3.M3 | -2.49 | [-3.07, -1.89] | -0.08 | [-0.54, +0.45] |
| M1.M3 | -1.19 | [-1.75, -0.66] | -0.02 | [-0.48, +0.44] |
| M3.M1 | -0.74 | [-1.15, -0.30] | -0.10 | [-0.53, +0.31] |

A5's own k = 1 Δ, M1 transcripts (its 120 items, point estimate): A = -0.58.

A5's own k = 1 Δ, M3 transcripts (its 120 items, point estimate): A = -2.98.

## S4 — R by persona and by temperature (95%)

- persona P-curious (16 pairs): R = -0.41 [-0.74, -0.11]
- persona P-neutral (16 pairs): R = -1.55 [-2.26, -0.88]
- persona P-none (16 pairs): R = -1.85 [-2.60, -1.11]
- temperature 0.7 (24 pairs): R = -1.30 [-1.83, -0.80]
- temperature 1.0 (24 pairs): R = -1.24 [-1.74, -0.74]

## S5 — the no-space readout

R = -1.66 [-2.24, -1.11] (supported by the same rule; reported); cell-level r with the locked readout +0.970.

## S6 — re-read of 8 A5 items, unspliced, vs A5's a5_q0 at k = 1

1536 rows matched; bitwise 1088; |ΔY| median 0.000, max 0.570 nats (A5 reached k = 1 by cropping a 32-turn prefill; reported).
