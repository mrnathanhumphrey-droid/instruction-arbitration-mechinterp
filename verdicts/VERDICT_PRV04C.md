# VERDICT — PRV-04c: per-head-matched block-swap (STAMPABLE)

**LOCKED VERDICT: NOTHING-ROUTES.** At genuinely matched per-head magnitude (every arm delivers τ≈0.045, all
match_ok, none VOID), NO head type causally routes the arbitration via generation-position block-attention.
Ran 2026-09-19, Lambda a100_sxm4, FULL n=720 (B=−3.8713), terminated clean, $0.39. PREREG_PRV04C.md sha256
`e33230a7b02e475c152dfefd3a7346beee60c85994376559e29a89d70450545c`, chained to PRV-04b `49bbc893…`. Artifacts:
`prv04c.json`, `prv04c_arms.csv`.

## The fix that made it valid
PRV-04b failed because its survivor arm (top-25 by within-level correlation robustness) was accidentally
LOW-capacity: the purest trackers route via SMALL block-mass differences. Capacity has a closed form —
d_h = |m_sys − m_usr| (the shape-preserving full-block-swap TV) = mean_i |blk_raw| from att01c_peritem.npz,
computed locally with no GPU. It showed 110/173 blk-survivors have capacity ≥ 0.05 (median 0.088). PRV-04c
restricts every arm to capacity ≥ τ heads, so each delivers EXACTLY τ=0.05 → airtight head-for-head match.

## Arm table (from prv04c_arms.csv, matched τ≈0.045)
| arm | n | M_att | CI95 | delivered_tv | match_ok | VOID |
|---|---|---|---|---|---|---|
| survivor_matched | 25 | +0.0035 | [0.0015, 0.0055] | 0.0442 | yes | no |
| bookkeeper_matched | 25 | −0.0040 | [−0.0097, 0.0006] | 0.0448 | yes | no |
| random_matched | 25 | +0.0081 | [0.0062, 0.0104] | 0.0455 | yes | no |
| survivor_imp_matched | 10 | +0.0007 | [−0.0003, 0.0017] | 0.0459 | yes | no |
| defeater_matched | 110 | −0.0264 | [−0.0347, −0.0210] | 0.0462 | yes | no |

Δ survivor − bookkeeper = +0.0075, CI[0.0031, 0.0129], excl0=True.
Δ survivor − random = −0.0046, CI[−0.0075, −0.0025], excl0=True.

## Reading
- **NOTHING-ROUTES (§5, locked).** Every arm |M_att| < 0.01 — nowhere near the 0.20 REAL cut, all under the 0.05
  floor. At equal per-head magnitude, tracking survivors, bookkeepers, and random heads are all indistinguishable
  from zero.
- **The tiny significant Δs are scientifically nil.** Survivor sits trivially ABOVE bookkeeper (+0.0075) and
  trivially BELOW random (−0.0046) — resolvable at n=720/5000 boots, but ~3% of the 0.20 threshold and straddling
  zero. Tracking heads are NOT more efficient routers; if anything they are marginally below the random floor.
- **The bookkeeper effect was pure magnitude, now proven:** +0.228 (PRV-04a, deliv≈0.29) → −0.005 (PRV-04b,
  0.081) → −0.004 (PRV-04c matched, 0.045). Monotonic to zero as magnitude drops.
- **Even 110 survivors swapped at once (defeater) move behavior only −0.026** — the aggregate of every testable
  tracking head at matched magnitude is still ~1/8 of the REAL threshold.

## Consequence — the ATT/routing line CLOSES
- Generation-position block-attention is NOT the arbitration router, for any head type. The ATT line ran:
  correlational (ATT-01) → ~85% shared-sign artifact with a small real core (ATT-01c) → that core is causally
  INERT at matched magnitude (PRV-04a/b/c). **H3 (arbitration routed via attention), demoted-not-dead after H4,
  is now DEAD — causally tested and null.**
- **Structural-anchor hypothesis gets NO causal leg.** The convergence claim collapses to its two clean legs:
  RDV-01 (re-derivation) + KDR-01 (linear-residual saturation), both untouched (no shared sign, no attention
  intervention).
- **The unexplained ~53% (KDR-01) is now bounded:** not linear-residual (saturated at k=50), not
  block-attention-routing at the readout (PRV-04c null). → composition, non-generation positions, or non-linear
  residual.
- **Caveat (honest scope):** only generation-position, block-TOTAL mass tested. Positional / within-block /
  upstream-position attention routing is untested. The negative is specifically: the winner is not routed by how
  these heads split attention between the two role blocks at the readout.

## Method lessons
1. **Capacity closed form:** for a shape-preserving block-mass swap, TV = |m_sys − m_usr|. No construction/second
   forward needed to measure intervention capacity.
2. **Select the intervention arm by the intervention's active variable (capacity), not by a correlate
   (tracking strength).** PRV-04b tested the wrong heads because the strongest trackers are the lowest-capacity;
   the question was only answerable once arms were selected on capacity. anchor_shape for interventions.
3. **Match per-head, not per-arm-mean,** when capacities are heterogeneous — a mean-match gate cannot be satisfied
   across arms with different capacity distributions (PRV-04b v1/v2 both INVALID for exactly this).
