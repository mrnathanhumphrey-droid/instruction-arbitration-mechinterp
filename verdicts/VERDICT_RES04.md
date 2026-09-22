# VERDICT — RES-04 (re-locked markers+span): extent — is the missing half on the role MARKERS?

**Mechanical verdict: PARTIAL-EXTENT (report band). The extent effect is REAL but SMALL. Substantively: the missing
~half is essentially NOT on the role markers — the widest in-block residual edit tops out at ~0.52.** Ran 2026-09-21,
Lambda a100_sxm4 (us-east-1), FULL n=720 (0 skipped), VOID clean, terminated clean, $0.30. PREREG_RES04.md re-lock sha256
`e1f1c6ea6741ec5fa7d76726e02679d3cb697c184259187d6b3f9a6feeba842b` (supersedes `3cea2712…`), chained to RES-02
`66ec4cee…`. Artifacts: `res04.json`, `res04_arms.csv`, `res04_peritem.npz` (per-item Y all arms — persisted).

## Results (B=−3.8792, n=720, VOID=False; floors unsteered 1.000 / steered 1.000, n=120)
| arm | M | CI95 | same-role floor | net-of-floor | pos shift (tok) |
|---|---|---|---|---|---|
| span-only cross-role (S) | 0.4617 | [0.345, 0.560] | 0.0396 (S2) | 0.422 [0.265, 0.553] | 23.2 |
| markers-only cross-role (K) | 0.0912 | [0.048, 0.134] | 0.0323 (K2) | 0.059 [0.015, 0.100] | 42.0 |
| markers+span cross-role (M) | 0.5167 | [0.393, 0.620] | 0.0470 (M2) | 0.470 [0.308, 0.605] | 32.6 |

**Reporting order (as locked):**
1. **M_M − M_S (extent, paired CI FIRST) = +0.0551, CI [0.0309, 0.0788].** Excludes 0 (real) but below the 0.10
   "missing-half-in-block" bar AND its magnitude sits inside the ≤0.08 "ruled-out" band while the CI clears 0 → neither
   pre-committed CLEAN reading fires → mechanical string PARTIAL-EXTENT.
2. **M_K (marker channel alone) = 0.0912, CI [0.048, 0.134]** (net-of-floor 0.059, CI [0.015, 0.100]). Small, but CI
   excludes 0 → NOT the "markers-carry-nothing" clean negative. Markers are a real, specific, small channel.
3. **Additivity M_M − (M_K + M_S) = −0.0361, CI [−0.0740, +0.0025].** CI includes 0 (just) → **ADDITIVE: K and S are
   independent channels.** No interaction — the marker does not need the span to agree (the SMOKE's "interaction" was
   n=40 noise; FULL n=720 is additive, leaning marginally sub-additive). K+S = 0.553 ≈ M_M = 0.517.

## Reading (the lead researcher's step; facts above)
- **Reproduction:** M_S = 0.4617 reproduces RES-02's 0.462 within-run — the harness is stable and the paired contrast is
  trustworthy (the whole point of re-measuring S in the same run). B = −3.879 also matches RES-02/03/03b.
- **Extent effect is real but small.** Widening the cross-role edit from the imperative span to include the role markers
  moves the ceiling 0.462 → 0.517: +0.055, CI excludes 0. So the markers DO carry a small, provenance-specific slice of
  the arbitration (M_K=0.091 alone, net-of-floor 0.059, both CI>0) — the structural-anchor story that has hovered since
  ATT-01 survives, but at SMALL magnitude, not as the missing half.
- **The missing ~half is NOT in the block.** The widest in-block residual exchange available (markers+span, M_M) tops out
  at 0.517 — ~0.48 of the arbitration is recovered by NO in-block residual edit. Per §4, this is the extent-ruled-out
  DIRECTION in substance (the block is not where the missing half lives), even though the mechanical string is
  PARTIAL-EXTENT because the marker channel is a small non-zero (M−S and M_K CIs exclude 0). Remaining candidates for the
  missing half: generation position and cross-position composition.
- **Additive, not interactive.** Markers and span are independent channels (additivity CI incl 0). Nothing in the arc
  predicted an interaction and none appeared.
- **Specificity + validity clean.** All three arms clear their same-role disruption floors (net CIs all > 0); VOID clean
  (steered compliance 1.000 = unsteered).

## Incidental — logged, NOT a decomposition (RES-03b ruling stands)
The marker arm imports the MOST absolute position (shift 42.0 tok) yet produces the SMALLEST effect (M_K=0.091); the span
arm imports far less position (23.2 tok) for far more effect (M_S=0.462). If raw position shift drove these M's, the
ordering would reverse. This is consistent with RES-03b (the text/position lever has no usable dynamic range) and is a
consistency note only — it is NOT used to split provenance from position, which remains permanently undecomposed.

## What survives / arc position
- **SURVIVES untouched:** RES-01a/b (provenance REPRESENTED — decodable, non-linear, position-independent). RES-02
  (lens-free span-exchange ceiling ~0.46 ≈ KDR linear), now REPRODUCED within-run at 0.462.
- **RES-04 adds:** the ceiling of the *widest token-alignable in-block* cross-role edit is ~0.52. Role markers are a
  small, real, additive, provenance-specific channel (+0.055 extent; 0.091 alone) — NOT the locus of the missing half.
  The missing ~half is NOT in the block; it lives at the generation position or in cross-position composition.
- **Does not touch:** PRV-04c (attention not router), RDV-01, RES-03/03b (decomposition permanently undecomposed).

## Method note
Re-measuring S within-run was load-bearing: the paired M_M−M_S CI [0.031, 0.079] is tight precisely because it is
paired; a cross-run compare against banked 0.462 would have straddled 0 (M_M CI alone is [0.393, 0.620]). anchor_shape
— the increment is the quantity, so measure both extents in one run. Per-item persisted this time (`res04_peritem.npz`) —
the recurring discard bug did not recur.
