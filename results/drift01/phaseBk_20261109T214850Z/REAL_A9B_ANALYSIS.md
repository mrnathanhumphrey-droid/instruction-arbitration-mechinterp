# HUNT-DRIFT-01 A9b — Amendment 9b (87eae7d9…) — what the readout-position state encodes — EXPLORATORY

Row checks: 960 probe × draw × 4 renderings (+ N), 11520 A8 units; longest rows {'native': 358, 'headers': 358, 'quoted': 331, 'stated': 430, 'a8': 417}. Prefill + probe_h vs a fresh pass (reported): n 72, max 0.406, median 0.104 nats.

Items 120 from 30 templates · draws 8 · native probe-C fit rows 15360 · folds (seed 7101901) [[3, 6, 10, 12, 17, 19, 22, 25, 26, 27], [1, 7, 8, 9, 11, 15, 16, 23, 24, 29], [0, 2, 4, 5, 13, 14, 18, 20, 21, 28]] · layers [8, 14, 16, 20, 26]; chosen per fold [14, 14, 14] · bootstrap 2000 (seed 7101001) · null 200 permutations.

## PRIMARY (98.33% CIs, Bonferroni over three)

**P1 — held-out native AUROC, flip vs copy, predicted > 0.5: 0.956 [0.929, 0.978] → supported** (shuffled null 97.5th pct 0.509, median 0.500; Control 1 0.500 [0.500, 0.500]). Pre-stated beside it: Control 2 (Qwen3-Embedding-8B) 0.563 [0.553, 0.578]; Llama − Control 2 +0.393 [0.364, 0.413].

**P2 — DD = (G_L,native − G_L,headers) − (G_enc,native − G_enc,headers), predicted +: +1.13 [+1.02, +1.24] → supported** (30 templates; within-class SD scales: Llama 0.487, Control 2 0.067).

**P3 — A8 reply effect on the projection, R_s, predicted −: -0.04 [-0.07, -0.00] → supported** (layer 14, the most chosen; 30 templates; 8 seeds; s in raw projection units).

## S1 — G per rendering (95%), share of native; per-rendering own-direction AUROC

| rendering | G Llama | 95% CI | share | G Control 1 | G Control 2 | share C2 | own-direction AUROC (Llama) |
|---|---|---|---|---|---|---|---|
| native | +2.33 | [+2.17, +2.47] | 1.00 | +0.00 | +0.23 | 1.00 | 0.956 |
| headers | +1.17 | [+1.05, +1.29] | 0.50 | +0.00 | +0.21 | 0.91 | 0.887 |
| quoted | +0.60 | [+0.53, +0.67] | 0.26 | -0.00 | +0.18 | 0.76 | 0.909 |
| stated | +1.46 | [+1.40, +1.53] | 0.63 | +0.00 | +0.31 | 1.35 | 0.944 |

Raw D_G = G_L,native − G_L,headers +1.16 [+1.07, +1.23] · quoted-log DD +1.67 [+1.55, +1.78] · G_stated sign: positive (word rule) (+1.46).

## S2 — layer profile (fixed layer, no choice)

| representation | native AUROC | inner AUROC by fold | G native |
|---|---|---|---|
| L8 | 0.747 | 0.749, 0.740, 0.753 | +0.95 |
| L14 | 0.956 | 0.959, 0.964, 0.951 | +2.33 |
| L16 | 0.925 | 0.932, 0.937, 0.917 | +2.04 |
| L20 | 0.849 | 0.858, 0.866, 0.839 | +1.45 |
| L26 | 0.812 | 0.824, 0.837, 0.808 | +1.19 |
| C1 | 0.500 | 0.500, 0.500, 0.500 | +0.00 |
| C2 | 0.563 | 0.570, 0.567, 0.562 | +0.23 |

## S3 — positive controls (held-out native AUROC of the single-word main effects) and probe N

| representation | user word | assistant word |
|---|---|---|
| L8 | 0.908 | 0.741 |
| L14 | 0.974 | 0.867 |
| L16 | 0.967 | 0.871 |
| L20 | 0.923 | 0.780 |
| L26 | 0.879 | 0.734 |
| C1 | 0.499 | 0.499 |
| C2 | 0.573 | 0.549 |

Probe N (native, directions fit on C): AUROC 0.944; G +2.03 [+1.90, +2.16].

## S4 — dose: G by n (Llama; Control 2), slope in log2 n

| rendering | n = 1 | n = 2 | n = 4 | n = 8 | slope | C2 slope |
|---|---|---|---|---|---|---|
| native | +1.88 | +2.41 | +2.52 | +2.51 | +0.20 | -0.04 |
| headers | +1.08 | +1.23 | +1.20 | +1.19 | +0.03 | -0.02 |
| quoted | +0.55 | +0.65 | +0.60 | +0.61 | +0.01 | -0.03 |
| stated | +1.27 | +1.56 | +1.53 | +1.49 | +0.06 | -0.03 |

## S5 — say–show: Spearman of s with the aligned readout Y within arm × n, pooled

C +0.254 · N -0.379 (on N the stance and Y run opposite ways by A7).

## S6 — A8 cells on Δs (95%)

| contrast / cell | A | 95% CI | W |
|---|---|---|---|
| R  reply effect (answer − clarification) | -0.04 | [-0.06, -0.01] | -0.01 |
| U  user-turn effect (question − 'Continue.') | -0.16 | [-0.20, -0.13] | +0.02 |
| R × U interaction | -0.09 | [-0.12, -0.06] | +0.01 |
| cell M1.M1 | -0.19 | [-0.24, -0.13] | -0.01 |
| cell M3.M3 | -0.39 | [-0.45, -0.33] | +0.00 |
| cell M1.M3 | -0.18 | [-0.23, -0.13] | -0.03 |
| cell M3.M1 | -0.30 | [-0.36, -0.25] | +0.01 |

Position on the copy (0) → flip (1) axis of the native rows: A8 filler rows +0.75, drift rows +0.52.

## S7 — anchors (n = 0) on the copy (0) → flip (1) axis

C anchors +0.52 · N anchors +0.60.

## S8 — gates

Repro: 5904 rows, bitwise 5904, max |Δ| 0.0000 nats ({'a10': 4104, 'a7n': 1032, 'a8': 768}) · encoder determinism: 1032 / 1032 bitwise; tokens max 730; truncated 0
