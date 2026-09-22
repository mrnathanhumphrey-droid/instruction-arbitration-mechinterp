# VERDICT — ORD-01: is B role or recency?

**Verdict: B IS RECENCY-DOMINANT. recency_frac = 0.711, CI [0.645, 0.780]. Flipping the block order FLIPS THE SIGN of B
(−3.88 → +1.64): the model obeys whichever role-block is LAST, not the untrusted role per se. ~71% of the baseline B is
recency (obey-last), ~29% is role (user-over-system beyond position). Every M in the program divides by B, so the
program's mediation numbers are normalized against a recency-dominated denominator and MUST be re-expressed. The flip is
coherent (twin-VOID = 1.000 both orders), so this is a real property, not a broken-patch artifact.** Ran 2026-09-21,
Lambda a100_sxm4, FULL n=720 (0 skipped), $0.28, per-item persisted, terminated clean. PREREG_ORD01.md sha256
`fab3eaafbe1f81c85e8288f4686022ca062f5478bd4b3d6a81359ced42198780`, chained to DIST-01 `9f8f3008…`.

## Results (n=720)
| quantity | value | CI95 |
|---|---|---|
| B_normal (system-first, user last) | **−3.879** | [−4.749, −3.007] |
| B_flipped (user-first, system last) | **+1.639** | [1.006, 2.278] |
| **recency_frac = (Bn−Bf)/(2Bn)** | **0.711** | [0.645, 0.780] |
| recency_B (arm B, same-role two-imperative) | −10.894 nats (−2.81·\|B\|) | [−12.19, −9.29] |
| MS_exch normal (provenance half) | 0.462 | [0.345, 0.560] |
| MS_exch flipped | 0.201 | [−0.054, 0.351] |
| MS_exch flip − normal | **−0.261** | [−0.485, −0.113] |
| MS_twin normal / flipped (content half) | 0.997 / 1.000 | — |
| twin-VOID normal / flipped | 1.000 / 1.000 | — |

## Reading (the lead researcher's step; facts above)
- **B is recency-dominant (§4 → B-IS-RECENCY-DOMINANT).** recency_frac 0.711, CI entirely above 0.5. Order-averaged
  B = (Bn+Bf)/2 = −1.12 (the ROLE component, survives order-flip); order-difference (Bn−Bf)/2 = −2.76 (the RECENCY
  component). Recency is ~2.5× the role part. The model's "obey the user slot" baseline is mostly "obey the last
  turn/block"; a real but minority (~29%) role component (user obeyed more than system beyond position) survives.
- **The single-number M-scale is confounded and is retracted pending re-expression.** M = −ΔY/(2B) with B ~71% recency
  means "M = 0.46 = half the arbitration" is really "the provenance swap moves ΔY, which is 46% of a baseline that is
  itself mostly recency." The numerator (the causal effect of the intervention) is unaffected; the DENOMINATOR's meaning
  is. Re-express before any "fraction of the arbitration" claim.
- **The provenance-exchange half is ORDER-DEPENDENT.** MS_exch drops 0.462 → 0.201 under flip (d = −0.261, CI excludes 0;
  flipped CI includes 0). So the "~half is provenance-movable" result is entangled with order/recency — it does not hold
  order-invariantly. The content half (twin-patch, MS ≈ 1) IS order-stable.
- **Within-message ordering is PRIMACY, not recency** (arm B: the EARLY imperative wins by 2.81·|B| when two imperatives
  share one user turn). So the recency here is a TURN/BLOCK-level effect (last turn wins — standard chat-model recency),
  NOT a token-position effect. Distinct phenomenon; refines "recency" to "last-turn-wins," and does not undercut arm A.
- **Coherence confirmed:** twin-VOID = 1.000 in both orders → the flipped forward is a valid computation; the sign-flip of
  B is a genuine behavioral property, not an OOD collapse.

## What this does and does NOT overturn
- **Does NOT overturn:** provenance is richly REPRESENTED (RES-01, decodability — unaffected by B); the exchange operation
  is COHERENT (DIST-01); the estimator arithmetic is UNBIASED (CAL-01 — this is a denominator-*meaning* problem, not an
  estimator-*bias* problem); the CONTENT half moves behavior and is order-stable (twin MS≈1). These stand.
- **DOES overturn / rescope:** the QUANTITATIVE "arbitration is ~half provenance-movable, ~half content-bound" headline.
  The denominator it was normalized against is ~71% recency, and the provenance half is order-dependent. The clean 50/50
  causal split is retracted pending re-expression. The qualitative facts survive; the number does not.
- **CAL-01 + DIST-01 + ORD-01 are orthogonal and all true:** unbiased estimator, coherent operation, recency-dominated
  denominator. ORD-01 is the third leg the first two did not test.

## Re-expression options (the lead researcher's call — this is now the gating decision before CoAx/TOOL/B/A)
1. **Order-resolved M** — report M_normal and M_flipped separately (÷ each order's B). Cleanest, no new normalization
   assumption; but B_flipped is small (1.64) so flipped M's are noisy.
2. **Role-baseline normalization** — divide by the order-averaged role component (|B_role| ≈ 1.12) instead of B_normal.
   Warning: this pushes MS_exch toward/above 1 (0.462×3.88/1.12 ≈ 1.6), which is likely ill-posed — the exchange ΔY is
   not simply a fraction of the role baseline. Needs care; may not be meaningful.
3. **Raw ΔY reporting** — report the intervention's raw nats effect and stop dividing by B entirely for the
   cross-order comparison; keep M only within a fixed order as a within-order fraction.
Recommendation: **order-resolved (1) + raw ΔY (3)** as the honest re-expression; retire the single cross-order "fraction
of arbitration" number.

## Caveats
- Arm-B (within-message primacy) is a distinct, strong effect (−2.81|B|) whose exact interpretation is muddier than arm A
  (both imperatives in one benign frame); reported as a refinement, not load-bearing.
- The block-reorder is mildly OOD (system-not-first); twin-VOID=1.000 both orders is the coherence guard that licenses the
  flipped measurement.

## Method note
This is why the denominator probe ran FIRST — everything was quoted in B's units, and B turned out to be mostly recency.
A cheap ($0.28) order-flip caught a confound that CAL-01 (estimator) and DIST-01 (operation) could not, because it lives
in neither the estimator nor the operation but in what the baseline MEANS. unit_of_independence /
feedback_the_numbers_resolution_must_match_the_decisions — the denominator has to denote what the decision needs, and
here it denoted recency.
