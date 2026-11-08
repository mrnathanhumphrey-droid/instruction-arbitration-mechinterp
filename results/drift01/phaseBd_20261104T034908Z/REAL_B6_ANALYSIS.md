# HUNT-DRIFT-01 B6 — Amendment 4 (569919b6…) — fresh items × drift / filler / none / prose — EXPLORATORY

Transcripts 96 · fresh items 80 from 29 templates · k ∈ [0, 1, 2, 4, 8, 16, 32] · δ = 0.234 · bootstrap 2000 over templates × seeds, seed 7101001. Filler / prose distance mismatches vs drift: 0 (must be 0).

Y_drift(0) spread over the 80 drawn items: 22 > 0 · 58 < 0 · min / Q1 / median / Q3 / max = -10.95 / -4.66 / -2.13 / +0.28 / +8.90.

## PRIMARY — H1: Spearman ρ(Δ_i, Y_drift(0)_i), predicted +

**ρ = +0.13 [-0.11, +0.35] (n = 80 items) → not supported**

## S1 — mean Δ = mean(Y_drift − Y_filler), k ∈ {4..32}

Δ = -0.36 [-1.06, +0.44] templates × seeds → **indeterminate** · items × seeds [-0.89, +0.17] → indeterminate (n = 30720)

## S2 — sign rule: sign(Δ_i) = sign(Y0_i) on 60% of 67 items (ties |Δ_i| < δ: 13); permutation null mean 55%, p = 0.248

## S3 — H2 (CORRELATED WITH H1): ρ(Δ_i, headroom_i), predicted −

ρ = +0.05 [-0.16, +0.25] · partial ρ given Y0 = -0.05 [-0.34, +0.23] · ρ(headroom, Y0) = +0.70

## S4 — amplification vs compression: signed move m_X = sign(Y0) · (Y_X(k) − Y_X(0)), pooled

| arm | m | 95% CI |
|---|---|---|
| drift | -0.09 | [-1.22, +1.09] |
| filler | -0.59 | [-1.68, +0.55] |
| prose | -1.24 | [-2.18, -0.26] |
| none | +0.35 | [-0.30, +1.05] |

Reading (A4.3 rule): **neither**

## S5 — prose contrasts (descriptive)

Δ_prose = Y_drift − Y_prose = -1.71 [-2.29, -1.16] · ρ vs Y0 +0.19 [-0.03, +0.41]

Δ_coh = Y_prose − Y_filler = +1.35 [+0.88, +1.82] · ρ vs Y0 -0.05 [-0.32, +0.23]

## S6 — by mode, counterbalance, k

| subset | items | ρ(Δ, Y0) | 95% CI | mean Δ |
|---|---|---|---|---|
| mode M1 | 80 | +0.11 | [-0.14, +0.35] | -0.26 |
| mode M3 | 80 | +0.12 | [-0.09, +0.33] | -0.47 |
| cell DONEsys | 39 | +0.09 | [-0.16, +0.37] | -1.18 |
| cell READYsys | 41 | -0.00 | [-0.36, +0.28] | +0.41 |

| k | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| mean Δ | -1.75 | -1.00 | -0.78 | -0.58 | -0.14 | +0.05 |

## S7 — the B-b 8 items (apart; never pooled)

Repro vs B-b's b5_q0: 16128 rows, bitwise 16128, max |Δ| 0 nats (stop above 0.05).

| item | Δ_i | Y0_i | Δ at k = 1 |
|---|---|---|---|
| c0062 | -2.38 | -5.44 | +0.05 |
| c0144 | +1.99 | +0.22 | +1.84 |
| c0239 | -2.81 | -0.06 | -1.03 |
| c0315 | -1.41 | -3.31 | -1.77 |
| c0457 | +2.52 | +3.23 | +1.42 |
| c0525 | -2.07 | -4.97 | -2.20 |
| c0550 | -1.04 | -4.10 | -3.14 |
| c0668 | +0.26 | +8.63 | -5.25 |

Observation only (A4.4): c0668's k = 1 value is in the last column; not tested.

Prose passages: 96 transcripts, 764,955 tokens; target-family words DONE 242 · READY 108 (reported, not filtered).

Single-pass + crop vs fresh pass (A3.3, reported): n 48, max 0.676, median 0.125 nats.

## Per item (fresh)

| item | template | cell | Δ_i | Y0_i | headroom |
|---|---|---|---|---|---|
| c0189 | 1 | DONEsys|late | -2.42 | -10.95 | +2.93 |
| c0259 | 13 | DONEsys|late | -0.39 | -10.48 | -0.04 |
| c0181 | 0 | DONEsys|late | -2.74 | -9.97 | +2.96 |
| c0086 | 14 | DONEsys|early | -2.02 | -7.60 | +5.19 |
| c0339 | 26 | DONEsys|late | -2.30 | -7.60 | +4.03 |
| c0223 | 7 | DONEsys|late | +0.86 | -7.50 | +3.94 |
| c0191 | 1 | DONEsys|late | +1.51 | -7.21 | +4.05 |
| c0121 | 20 | DONEsys|early | +0.04 | -7.12 | +6.04 |
| c0068 | 11 | DONEsys|early | -0.87 | -7.11 | +1.36 |
| c0398 | 6 | READYsys|early | -0.04 | -6.50 | +6.77 |
| c0606 | 11 | READYsys|late | +2.22 | -6.36 | +1.48 |
| c0041 | 6 | DONEsys|early | -4.42 | -6.15 | +9.36 |
| c0115 | 19 | DONEsys|early | -0.14 | -6.09 | +5.19 |
| c0001 | 0 | DONEsys|early | +0.49 | -5.90 | +6.58 |
| c0452 | 15 | READYsys|early | -2.57 | -5.83 | +8.73 |
| c0069 | 11 | DONEsys|early | -1.51 | -5.78 | +0.60 |
| c0517 | 26 | READYsys|early | +1.57 | -5.42 | +7.52 |
| c0249 | 11 | DONEsys|late | -0.76 | -5.33 | -2.96 |
| c0235 | 9 | DONEsys|late | -3.21 | -4.85 | +6.27 |
| c0548 | 1 | READYsys|late | +0.75 | -4.71 | +6.95 |
| c0354 | 29 | DONEsys|late | -1.96 | -4.65 | +7.08 |
| c0520 | 26 | READYsys|early | +3.44 | -4.60 | +9.53 |
| c0440 | 13 | READYsys|early | +1.13 | -4.25 | +9.17 |
| c0010 | 1 | DONEsys|early | -0.13 | -4.23 | +4.18 |
| c0693 | 25 | READYsys|late | -0.43 | -4.17 | +6.04 |
| c0532 | 28 | READYsys|early | -1.08 | -3.98 | +3.42 |
| c0052 | 8 | DONEsys|early | -2.39 | -3.75 | +3.05 |
| c0587 | 7 | READYsys|late | -1.50 | -3.71 | +8.96 |
| c0034 | 5 | DONEsys|early | -1.00 | -3.54 | +5.97 |
| c0702 | 27 | READYsys|late | -2.11 | -3.19 | +4.48 |
| c0118 | 19 | DONEsys|early | -2.04 | -3.15 | +7.46 |
| c0472 | 18 | READYsys|early | +2.06 | -3.03 | +6.64 |
| c0613 | 12 | READYsys|late | +2.88 | -2.98 | +1.07 |
| c0600 | 10 | READYsys|late | -2.74 | -2.97 | +2.55 |
| c0552 | 2 | READYsys|late | -0.06 | -2.92 | +11.90 |
| c0585 | 7 | READYsys|late | -0.43 | -2.81 | +6.37 |
| c0137 | 22 | DONEsys|early | -4.85 | -2.75 | +11.07 |
| c0307 | 21 | DONEsys|late | -1.24 | -2.71 | +10.34 |
| c0673 | 22 | READYsys|late | -1.12 | -2.17 | +5.14 |
| c0556 | 2 | READYsys|late | -0.11 | -2.15 | +11.36 |
| c0102 | 17 | DONEsys|early | +0.53 | -2.10 | +11.71 |
| c0291 | 18 | DONEsys|late | -2.61 | -2.06 | +10.17 |
| c0099 | 16 | DONEsys|early | -0.55 | -1.81 | -2.18 |
| c0268 | 14 | DONEsys|late | -2.59 | -1.67 | +12.51 |
| c0502 | 23 | READYsys|early | +6.19 | -1.52 | +5.80 |
| c0226 | 7 | DONEsys|late | +0.46 | -1.50 | +9.83 |
| c0473 | 18 | READYsys|early | +2.60 | -1.44 | +8.15 |
| c0145 | 24 | DONEsys|early | +0.77 | -1.27 | +5.13 |
| c0312 | 22 | DONEsys|late | -3.11 | -1.15 | +10.94 |
| c0127 | 21 | DONEsys|early | +0.19 | -0.94 | +12.15 |
| c0646 | 17 | READYsys|late | -0.74 | -0.60 | +13.92 |
| c0674 | 22 | READYsys|late | +1.58 | -0.55 | +9.67 |
| c0022 | 3 | DONEsys|early | +1.48 | -0.45 | +2.84 |
| c0063 | 10 | DONEsys|early | -2.80 | -0.31 | +7.89 |
| c0580 | 6 | READYsys|late | -6.21 | -0.24 | +12.58 |
| c0482 | 20 | READYsys|early | +1.65 | -0.23 | +12.09 |
| c0064 | 10 | DONEsys|early | -1.93 | -0.17 | +4.66 |
| c0287 | 17 | DONEsys|late | +0.16 | -0.17 | +11.40 |
| c0498 | 23 | READYsys|early | +6.35 | +0.20 | +6.55 |
| c0501 | 23 | READYsys|early | +5.20 | +0.21 | +9.65 |
| c0588 | 8 | READYsys|late | +2.36 | +0.50 | +13.49 |
| c0214 | 5 | DONEsys|late | -2.31 | +0.56 | +12.41 |
| c0192 | 2 | DONEsys|late | +0.12 | +0.60 | +11.44 |
| c0686 | 24 | READYsys|late | -4.29 | +0.87 | +6.76 |
| c0630 | 15 | READYsys|late | -3.37 | +1.01 | +13.61 |
| c0275 | 15 | DONEsys|late | +0.03 | +1.02 | +11.61 |
| c0503 | 23 | READYsys|early | +4.55 | +1.51 | +8.47 |
| c0685 | 24 | READYsys|late | -2.38 | +1.62 | +8.83 |
| c0670 | 21 | READYsys|late | -0.28 | +1.69 | +13.92 |
| c0676 | 22 | READYsys|late | -1.20 | +2.10 | +14.51 |
| c0619 | 13 | READYsys|late | +1.07 | +2.75 | +8.90 |
| c0340 | 26 | DONEsys|late | -2.15 | +3.19 | +13.46 |
| c0336 | 26 | DONEsys|late | -0.17 | +3.62 | +13.69 |
| c0653 | 18 | READYsys|late | +3.01 | +3.67 | +14.52 |
| c0692 | 25 | READYsys|late | -0.49 | +3.98 | +8.91 |
| c0651 | 18 | READYsys|late | +0.83 | +4.02 | +15.93 |
| c0717 | 29 | READYsys|late | -4.99 | +4.91 | +10.77 |
| c0572 | 5 | READYsys|late | -0.17 | +4.96 | +16.05 |
| c0596 | 9 | READYsys|late | +3.70 | +5.00 | +14.04 |
| c0649 | 18 | READYsys|late | +0.06 | +8.90 | +18.74 |
