# VERDICT — ATT-01c: within-level control for the shared-sign artifact

**TRUSTED. Verdict: PARTIAL (P = 0.1514).** Ran 2026-09-18, Lambda a100_sxm4, FULL n=720 (360/360 per
counterbalance level, 30 template clusters each), terminated clean, $0.32 (+$0.26 SMOKE#1 that caught an
unbalanced-subsample bug). PREREG_ATT01C.md sha256 `c99fdaa9ccea199d5e2cd3709cfacafb3ffd00f67499c6081337df6f26800a84`,
chained to PRV-04 `a71824cf…`. Artifacts: `att01c.json`, `att01c_withinlevel.csv`, `att01c_peritem.npz`
(per-item raw arrays — the persistence fix so no re-analysis needs the GPU again).

## Reproduction gate — PASSED EXACT
Recomputed pooled `corr(s·A_raw, s·R)` vs ATT-01's `att01_heads.csv`: **max|Δ| = 5.0e-7** (imp and blk),
median 2.5e-7. The re-run measures the identical quantity; the within-level split is on solid ground. (PREREG
§3 HALT would have fired at median|Δ|>0.05; it did not.)

## Result (locked thresholds, PREREG §5)
P = fraction of ATT-01 blk-survivors passing the within-level control (both counterbalance levels, same-sign,
bootstrap 95% CI excludes 0, |r|≥0.10). **P = 0.1514 → PARTIAL** (TRACKING-REAL needs ≥0.50; ARTIFACT needs
<0.10 or top-10 collapse).

| set | ATT-01 n | P@0.05 | P@0.10 (lock) | P@0.15 |
|---|---|---|---|---|
| blk-survivors (primary) | 733 | 0.1651 | **0.1514** | 0.1010 |
| imp-survivors | 662 | 0.0559 | 0.0544 | 0.0332 |
| marker-readers (blk & ¬imp) | 192 | 0.2031 | 0.1979 | 0.1510 |
| text-readers (imp & ¬blk) | 121 | 0.0744 | 0.0661 | 0.0496 |
| top-10 by \|track_r\| | 10 | 0.70 | 0.70 | 0.70 |

Whole 1024-head family: **173 pass the blk control, 56 pass imp** (at |r|≥0.10).

## Reading (the lead researcher's step; mechanical facts above)
- **The pooled ATT-01 tracking result was mostly — but not wholly — the shared-sign artifact.** ~85% of the 733
  blk-"survivors" collapse within-level: their pooled r was the between-level mean-shift of a positional bias
  (constant `A_raw`, signed by `s`, correlated with `s·R` by construction). Headline survivor count inflated ~4–6×.
- **A real core survives at the top of the ranking.** 7/10 top trackers pass. #1 **L28H1** holds in both levels
  (blk_r +1: −0.177 CI[−0.348,−0.012]; −1: −0.485 CI[−0.569,−0.392]) — genuine content-following, though
  level-asymmetric. Others that pass: L19H29, L22H23, L24H19 (blk); L28H8, L30H16, L27H15 (imp).
- **Head-by-head artifact is visible.** L31H13 pooled_blk +0.359 → within-level +0.504 / +0.018 (one level ≈0).
  L30H31 (ATT-01 #2) fails: +1-level CI includes 0. These were pooled-correlation ghosts.
- **Marker-vs-text asymmetry survives directionally:** markers pass ~3× more than text (19.8% vs 6.6%). "Anchor
  is the marker, not the content" holds in relative terms even as both sets are decimated in absolute terms.
- **Even survivors are level-asymmetric** (e.g. L28H1 −0.18 vs −0.49) — a clean content-follower would track
  symmetrically. A yellow flag on how clean even the real core is; (a)'s intervention must handle both levels.

## Consequences (recorded)
- **ATT-01's three-probe convergence leg is WOUNDED, not retracted.** Restate it on the ~173 real heads, NOT
  733, and flag that most of the headline count was artifact. RDV-01 + KDR-01 stand independently (no shared
  sign) → structural-anchor hypothesis keeps two clean legs + one reduced.
- **PRV-04 (a) has a clean, smaller target** (PREREG_ATT01C §5: PARTIAL → build (a) only on passers). Candidate
  set = the 173 blk-passers, or conservatively the top survivors above. Whether (a) proceeds is the lead researcher/a second reviewer's §2
  call.
- PRV-04 Phase A remains INVALID (swap-magnitude gate), not a null.

## Method lesson
Signing both the statistic and the readout by the same latent (counterbalance s) manufactures correlation from
any constant bias in the statistic. ATT-01 did this (`A_signed=s·A_raw`, `Y_signed=s·Y_raw`) and pooled across
levels; the within-level split (s constant → the sign cancels) is the correct control and should have been the
ATT-01 estimator from the start. See probe_upstream (statistic & reference by the same path aren't
comparable) — here the *sign* was the shared path. Also: persist per-item arrays (ATT-01 discarded them, forcing
a GPU re-run to answer a question the saved aggregates could not).
