# HUNT-DRIFT-01 A11 — Amendment 11 (9c4c627f…) — is word-pool filler a valid baseline? — EXPLORATORY

Transcripts 96 · items 120 (60 DONEsys · 60 READYsys) from 30 templates · k ∈ [0, 1, 2, 4, 8, 16, 32] · old arms from A5's a5_q0, diverse from a11_q0, paired · bootstrap 2000 over templates × seeds, seed 7101001.

Repro gate (S7; first 8 A5 items × drift / filler / prose vs A5's a5_q0): 16128 rows, bitwise 16128, max |Δ| 0 nats (stop above 0.05).

k = 0 identity (no turns, every arm the same row): diverse = drift bitwise on 11520 / 11520 (transcript, item).

## PRIMARY (Bonferroni, 97.5% CIs)

**P1 — drift − diverse, aligned part A over k ∈ {1, 2, 4}, predicted −: A = -1.21 [-1.80, -0.65] → supported** (30 templates)

**P2 — filler − diverse, aligned part A over k ∈ {8, 16, 32}, predicted −: A = -0.56 [-1.03, -0.08] → supported** (30 templates)

Readings written before any data (A11.3): P1 supported → drift's short-distance damage is not a property of the word-pool baseline · P1 not supported / contradicted → A5's P1 is read as relative to word-pool filler only · P2 supported → part of A5's 'prose strengthens' is 'filler weakens' (S2 says how much is left for prose) · P2 not supported → A5's P2 stands as read · P2 contradicted → natural text weakens the target more than word-pool filler; no simple reading.

## S1 — no-filler reference: each arm's Y(k) − Y(0) (95%; distance not matched, descriptive)

| arm | k | A | 95% CI | W | 95% CI |
|---|---|---|---|---|---|
| drift | 1 | -1.80 | [-2.40, -1.16] | -1.23 | [-1.68, -0.73] |
| drift | 2 | -2.00 | [-2.60, -1.40] | -1.28 | [-1.78, -0.72] |
| drift | 4 | -2.20 | [-2.81, -1.58] | -1.08 | [-1.59, -0.51] |
| drift | 8 | -2.29 | [-2.99, -1.61] | -1.46 | [-2.02, -0.86] |
| drift | 16 | -3.01 | [-3.79, -2.31] | -2.08 | [-2.74, -1.40] |
| drift | 32 | -4.79 | [-5.67, -3.87] | -2.59 | [-3.22, -1.94] |
| filler | 1 | -0.02 | [-0.66, +0.65] | -1.23 | [-1.63, -0.82] |
| filler | 2 | -0.77 | [-1.46, -0.09] | -1.53 | [-1.97, -1.07] |
| filler | 4 | -1.25 | [-2.04, -0.51] | -1.50 | [-2.02, -0.96] |
| filler | 8 | -1.47 | [-2.40, -0.63] | -2.15 | [-2.72, -1.60] |
| filler | 16 | -2.75 | [-3.69, -1.84] | -2.76 | [-3.42, -2.12] |
| filler | 32 | -4.91 | [-5.93, -3.91] | -3.19 | [-3.88, -2.50] |
| prose | 1 | -0.88 | [-1.58, -0.16] | -1.96 | [-2.38, -1.49] |
| prose | 2 | -1.04 | [-1.86, -0.25] | -1.99 | [-2.47, -1.46] |
| prose | 4 | -0.81 | [-1.74, +0.06] | -1.71 | [-2.24, -1.14] |
| prose | 8 | -0.91 | [-1.88, -0.03] | -2.03 | [-2.61, -1.43] |
| prose | 16 | -1.47 | [-2.42, -0.60] | -2.25 | [-2.92, -1.58] |
| prose | 32 | -2.32 | [-3.35, -1.33] | -2.56 | [-3.26, -1.86] |
| diverse | 1 | -0.57 | [-1.25, +0.10] | -1.96 | [-2.35, -1.56] |
| diverse | 2 | -0.84 | [-1.60, -0.10] | -2.08 | [-2.57, -1.56] |
| diverse | 4 | -0.95 | [-1.81, -0.14] | -1.82 | [-2.41, -1.23] |
| diverse | 8 | -1.41 | [-2.30, -0.61] | -2.27 | [-2.89, -1.62] |
| diverse | 16 | -2.48 | [-3.33, -1.66] | -2.55 | [-3.24, -1.84] |
| diverse | 32 | -3.55 | [-4.48, -2.59] | -2.87 | [-3.60, -2.13] |

## S2 — prose − diverse, k 8–32 (95%): is A5's prose effect specific to one coherent book?

A = +0.91 [+0.60, +1.23] · W = +0.28 [+0.07, +0.50]

## S3 — A and W at every k (95%)

| contrast | k | A | 95% CI | W | 95% CI |
|---|---|---|---|---|---|
| drift − diverse | 1 | -1.23 | [-1.73, -0.73] | +0.74 | [+0.37, +1.11] |
| drift − diverse | 2 | -1.16 | [-1.65, -0.66] | +0.80 | [+0.42, +1.18] |
| drift − diverse | 4 | -1.25 | [-1.82, -0.64] | +0.75 | [+0.35, +1.14] |
| drift − diverse | 8 | -0.88 | [-1.37, -0.37] | +0.81 | [+0.47, +1.15] |
| drift − diverse | 16 | -0.54 | [-0.99, -0.09] | +0.47 | [+0.11, +0.84] |
| drift − diverse | 32 | -1.24 | [-1.68, -0.77] | +0.28 | [-0.13, +0.69] |
| filler − diverse | 1 | +0.55 | [+0.17, +0.90] | +0.74 | [+0.48, +0.99] |
| filler − diverse | 2 | +0.07 | [-0.31, +0.41] | +0.55 | [+0.25, +0.84] |
| filler − diverse | 4 | -0.30 | [-0.77, +0.16] | +0.33 | [-0.02, +0.66] |
| filler − diverse | 8 | -0.06 | [-0.45, +0.35] | +0.12 | [-0.20, +0.43] |
| filler − diverse | 16 | -0.27 | [-0.69, +0.19] | -0.22 | [-0.52, +0.10] |
| filler − diverse | 32 | -1.36 | [-1.90, -0.88] | -0.32 | [-0.73, +0.09] |
| prose − diverse | 1 | -0.31 | [-0.51, -0.11] | +0.01 | [-0.14, +0.16] |
| prose − diverse | 2 | -0.21 | [-0.44, +0.04] | +0.09 | [-0.06, +0.25] |
| prose − diverse | 4 | +0.14 | [-0.14, +0.43] | +0.11 | [-0.07, +0.30] |
| prose − diverse | 8 | +0.50 | [+0.21, +0.79] | +0.24 | [+0.01, +0.45] |
| prose − diverse | 16 | +1.01 | [+0.67, +1.38] | +0.30 | [+0.06, +0.54] |
| prose − diverse | 32 | +1.23 | [+0.89, +1.57] | +0.31 | [+0.07, +0.56] |

## S4 — READY part W of both primaries (95%)

drift − diverse, k 1–4: W = +0.76 [+0.40, +1.12] · filler − diverse, k 8–32: W = -0.14 [-0.45, +0.18]

## S5 — P1 / P2 aligned part by subset (95%)

| subset | templates | P1 A | 95% CI | P2 A | 95% CI |
|---|---|---|---|---|---|
| mode M1 | 30 | -0.73 | [-1.28, -0.17] | -0.47 | [-0.88, -0.08] |
| mode M3 | 30 | -1.70 | [-2.26, -1.11] | -0.66 | [-1.09, -0.21] |
| position early | 13 | -0.13 | [-1.17, +0.80] | -0.16 | [-0.96, +0.66] |
| position late | 20 | -1.82 | [-2.48, -1.12] | -0.76 | [-1.32, -0.20] |

## S6 — diverse passages (reported, not filtered)

96 transcripts, 764,955 tokens; target-family words DONE 420 · READY 282.

S2 (prose − diverse, k 8–32) split by the book of assistant turn k, the turn nearest the probe (95%, descriptive):

| book | turns | tokens | DONE | READY | (t, k) cells | A | 95% CI | W | 95% CI |
|---|---|---|---|---|---|---|---|---|---|
| fiction | 773 | 96,652 | 72 | 32 | 34 | +1.02 | [+0.68, +1.38] | +0.20 | [-0.06, +0.48] |
| history | 760 | 94,947 | 22 | 34 | 34 | +1.15 | [+0.75, +1.53] | +0.32 | [+0.11, +0.52] |
| essays | 747 | 94,408 | 39 | 19 | 41 | +0.87 | [+0.52, +1.22] | +0.33 | [+0.08, +0.56] |
| travel | 791 | 94,056 | 39 | 40 | 42 | +0.65 | [+0.36, +0.99] | +0.24 | [+0.00, +0.52] |
| science | 802 | 103,002 | 52 | 78 | 42 | +0.93 | [+0.59, +1.27] | +0.21 | [-0.02, +0.46] |
| letters | 788 | 97,368 | 62 | 28 | 36 | +0.76 | [+0.35, +1.13] | +0.33 | [+0.08, +0.57] |
| drama | 720 | 87,793 | 38 | 21 | 25 | +0.80 | [+0.44, +1.18] | +0.44 | [+0.20, +0.69] |
| philosophy | 763 | 96,729 | 96 | 30 | 34 | +1.17 | [+0.78, +1.61] | +0.25 | [-0.02, +0.50] |

Single-pass + crop vs fresh pass (reported): n 48, max 0.488, median 0.135 nats.
