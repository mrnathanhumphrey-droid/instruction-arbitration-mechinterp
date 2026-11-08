# HUNT-DRIFT-01 Phase B-a — analysis (REAL, EXPLORATORY)

Plan `PLAN_PHASE_B.md` 1a660770 (locked). Rows: B1 full 5040, B1 panel 32256, B3 432, B4 5760. δ = 0.234; bootstrap 2000, seed 7101001.

## B1 — does on-policy (self-likely) text pull harder?

Full battery, depth 0, P-none, 720 items. pull = Y_inert − Y_plant (+ = the plant pulls away from the system target); self-likelihood = mean log-prob of the plant's tokens (nats/token). CIs template-clustered.

| cell | mean pull | mean self-lik (SD) | Spearman ρ [95% CI] | partial ρ \| ntok [95% CI] |
|---|---|---|---|---|
| asst_imp | +2.56 | -4.30 (1.68) | -0.121 [-0.23, -0.01] | -0.159 [-0.27, -0.06] |
| asst_int | +2.59 | -4.43 (1.42) | -0.131 [-0.26, -0.01] | -0.139 [-0.27, +0.01] |
| quot_imp | +3.07 | -4.86 (0.58) | +0.028 [-0.15, +0.19] | -0.139 [-0.22, -0.05] |
| quot_int | +3.35 | -4.80 (0.57) | -0.042 [-0.18, +0.09] | -0.034 [-0.11, +0.04] |
| user_imp (user, secondary) | +7.69 | -4.09 (1.45) | -0.014 [-0.21, +0.20] | -0.229 [-0.36, -0.06] |
| user_int (user, secondary) | +3.99 | -4.69 (1.47) | -0.236 [-0.40, -0.05] | -0.237 [-0.37, -0.08] |

**B1 verdict (own-turn cells, pre-stated rule): mixed.** Cells with ρ > 0 and CI > 0: 0 of 4. User cells (secondary): user_imp ρ -0.014 [-0.21, +0.20], user_int ρ -0.236 [-0.40, -0.05].

**Panel (secondary)** — frozen transcripts × 8 items, per k; two-way bootstrap (items × generation seeds):

| k | asst_imp | asst_int | quot_imp | quot_int | rule |
|---|---|---|---|---|---|
| 0 | -0.416 [-0.85, +0.51] | -0.016 [-0.59, +0.61] | +0.023 [-0.67, +0.77] | +0.106 [-0.50, +0.76] | no |
| 4 | -0.193 [-0.60, +0.37] | -0.086 [-0.40, +0.33] | -0.088 [-0.48, +0.33] | -0.024 [-0.40, +0.29] | no |
| 16 | -0.213 [-0.64, +0.39] | -0.016 [-0.41, +0.38] | -0.237 [-0.64, +0.31] | -0.044 [-0.41, +0.35] | no |
| 32 | -0.152 [-0.68, +0.51] | -0.004 [-0.50, +0.48] | -0.247 [-0.70, +0.45] | -0.089 [-0.56, +0.47] | no |

## B3 — does the agent's own (sampled) choice hold harder than a planted one? (PARTLY USER-INDUCED)

Choice points 432; valid 431; dropped 1 (first sampled token not DONE / READY). Gate ≥ 200 valid: MET.

R = lp(assistant-turn word) − lp(the word the user then asks for); + = the earlier word holds.

- mean R ON (sampled) -14.39, OFF (planted) -14.77
- **ON − OFF = +0.38 [+0.08, +0.64]** (two-way: design cells × seeds) → **on-policy choice holds more**

| split | n | ON − OFF [95% CI] |
|---|---|---|
| chose DONE | 235 | +1.70 [+1.55, +1.87] |
| chose READY | 196 | -1.21 [-1.42, -0.96] |
| k = 4 | 143 | -0.23 [-0.55, +0.08] |
| k = 16 | 144 | +0.68 [+0.10, +1.18] |
| k = 32 | 144 | +0.69 [+0.17, +1.15] |

Covariate (B1's logic): Spearman ρ(ON − OFF, the choice's own log-prob) = +0.420; choice log-prob median -0.43 nats.
Choices: DONE 235, READY 196. Dropped tokens: [82889].

## B4 — mention vs use, user turn vs tool-result turn (depth 0, 720 items)

| arm | mean Y | target → readout tokens (median) |
|---|---|---|
| user_issued_imp | -2.54 | 26 |
| user_issued_int | +1.14 | 26 |
| user_quoted_imp | +0.01 | 26 |
| user_quoted_int | +1.46 | 26 |
| tool_issued_imp | +1.49 | 26 |
| tool_issued_int | +1.92 | 26 |
| tool_quoted_imp | +3.51 | 27 |
| tool_quoted_int | +3.48 | 27 |

+Y = obeys the system target. Contrast = Y_quoted − Y_issued (+ = the quote pulls LESS than the instruction).

| slot | pooled (imp + int) [95% CI] | imperative | intention | verdict |
|---|---|---|---|---|
| user | +1.44 [+0.76, +2.08] | +2.55 [+1.74, +3.34] | +0.32 [-0.35, +0.96] | rule not met |
| tool | +1.79 [+1.52, +2.08] | +2.02 [+1.65, +2.42] | +1.57 [+1.29, +1.83] | rule not met |

**Indirect-injection (Greshake et al. 2023) link: NOT claimed — the rule is not met in the tool slot; the headline stays scoped to the agent own turn.**

## Reported — B1 panel readouts vs the full run's own (same rows, different cache-prefill chunking)

n 32256; exact 62%; median 0.0000; p99 0.316; max 1.797 nats; > δ 3.0%. Not a gate. B1 reads its readout and plant log-probs from ONE pass; the full battery (fresh passes) matched the full run exactly.

