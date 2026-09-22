# VERDICT — RES-05: is the missing half SUMMARIZED at the generation position, or COMPOSED?

**Mechanical verdict: COMPOSITION-BY-ELIMINATION. The missing ~half is NOT summarized at any patchable single site
before the output — net-of-floor is flat/below-span across the diagnostic mid-stack (L≤20) and rises only into the
tautology gradient (L24→31). Combined accounting tops out at ~0.55 (CI-hi 0.67 < 0.80) → the rest is carried by NEITHER
the block NOR the mid-layer readout → intermediate positions / a distributed computation.** Ran 2026-09-21, Lambda
a100_sxm4 (us-east-1), FULL n=720 (0 skipped), VOID clean, terminated clean, $0.41. PREREG_RES05.md sha256
`f0b75186bb0068442014cea854131c438183d10e78360eb9b1b157bd47ef3f3c`, chained to RES-04 `e1f1c6ea…`. Artifacts:
`res05.json`, `res05_arms.csv`, `res05_peritem.npz` (per-item Y all arms — persisted).

## Results (B=−3.8792, n=720, VOID=False; VOID floor unsteered 1.000 / steered 0.950 @ L16, n=120)
**M_S span-only baseline (in-run) = 0.4617, CI [0.345, 0.560]** — reproduces RES-02/04 a third time.
**Cross-role gen-position arm imports ZERO position** (gen_shift_cross = 0.0; twins are same-length cb-flips), so the
sweep is not position-contaminated. Floor shift = 2.0 tok.

| layer | M_cross (raw) | M_floor | **net** [CI95] | net − M_S [CI95] |
|---|---|---|---|---|
| 8  | −0.002 | −0.001 | **−0.001** [−0.007, 0.005] | −0.463 [−0.561, −0.346] |
| 12 | −0.008 | −0.004 | **−0.004** [−0.014, 0.005] | −0.466 [−0.563, −0.349] |
| 16 | +0.085 | +0.034 | **+0.051** [0.025, 0.076] | −0.411 [−0.508, −0.298] |
| 20 | +0.308 | +0.066 | **+0.242** [0.202, 0.279] | −0.219 [−0.322, −0.109] |
| 24 | +0.681 | +0.091 | **+0.591** [0.535, 0.643] | +0.129 [0.043, 0.231] |
| 28 | +0.943 | +0.084 | **+0.858** [0.805, 0.914] | +0.397 [0.307, 0.511] |
| **31 (anchor)** | **+0.965** [0.960, 0.972] | +0.091 | +0.874 [0.803, 0.933] | +0.412 [0.335, 0.500] |

**L31 tautology anchor raw M = 0.965, CI [0.960, 0.972]** — confirms the readout works and marks where the sweep stops
meaning anything (M→1 by construction).

**Combined cell (markers+span all-L + gen@L16, cross-role):** raw M = 0.598 [0.493, 0.683], floor 0.049, **net = 0.549,
CI [0.405, 0.668]**.

## Reading (the lead researcher's step; facts above)
- **No mid-stack summary.** Across the diagnostic window L≤20, net-of-floor is flat and BELOW the span baseline at every
  layer (net−M_S is negative with CI excluding 0 at L8/12/16/20). By mid-stack the single-position gen-patch carries LESS
  than the distributed span edit — the opposite of "the arbitration is summarized at the readout." Per §4 this is the
  **COMPOSITION** reading.
- **The late rise is the tautology, not a discovery.** net climbs 0.051→0.242→0.591→0.858→0.874 (L16→31) exactly as the
  raw cross-M climbs toward the L31 anchor (0.965). The floor stays low (~0.09) at late layers because the same-role
  source carries the SAME answer — so net at L31 is mostly the tautology (importing the opposite-role answer near the
  output flips the logits). The crossing to net>M_S happens only at L24, deep in the gradient. There is no early/mid site
  that carries it.
- **Zero-position guarantee strengthens it.** The cross-role gen arm imports 0 position shift, so the mid-stack flatness
  is not a position artifact — the diagnostic window is clean.
- **Accounting does NOT close.** Block (markers+span, RES-04 ~0.517) + a mid-layer readout patch (gen@L16, net ~0.05)
  reaches only net 0.549 (CI-hi 0.668 < 0.80). ~0.45 of the arbitration is carried by NEITHER the block NOR the
  mid-readout position → **intermediate content positions we have never patched, or genuinely distributed composition**.
- **Bottom line:** the arbitration is a distributed computation. No span (RES-02), marker (RES-04), attention head
  (PRV-04c), or mid-stack readout position (RES-05) carries the missing half; it only collapses onto the readout in the
  tautological final layers. Composition wins by elimination.

## What survives / arc position
- **SURVIVES untouched:** RES-01a/b (provenance REPRESENTED — decodable, non-linear, position-independent). RES-02/04
  span+marker in-block ceiling ~0.52 (reproduced: M_S=0.462 a third time).
- **RES-05 adds:** the missing ~half is NOT localized to the generation position at any diagnostic layer (net below span
  through L20; the L24+ rise is the tautology gradient, floor-confirmed). Combined block+readout accounting = 0.55, does
  not close → the remainder is at untouched intermediate positions or is distributed. **The localization program has
  bottomed out: arbitration is distributed composition, not a patchable site.**
- **Does not touch:** PRV-04c, RDV-01, RES-03/03b (decomposition permanently undecomposed).

## Caveats (honest)
- The L24–28 band is where "pure tautology" and "genuine late-stack summarization" are least distinguishable. But both
  are LATE and downstream of any mid-stack localization; neither is the summarized-at-gen-position reading (which required
  a mid-stack, L≤20 excess over span, and did not appear). Composition holds under either interpretation of the late band.
- One patchable candidate remains untested: **intermediate content positions** (tokens between the imperative span and the
  readout). The combined-below-1 result points there. Whether to sweep them (RES-06) or call the localization arc complete
  is the lead researcher's read — the mechanical result is that no site tested so far carries the missing half.

## Method note
Re-measuring the span baseline in-run (third reproduction, 0.462) kept the net−M_S contrast paired. The cross-role gen
arm's zero position shift is a design windfall — the one arm in this program with NO position confound. Per-item persisted
(`res05_peritem.npz`). The floor did the heavy lifting exactly as pre-committed: raw M_cross at L31 = 0.965 would have been
a false "localized!" without subtracting the tautology floor. probe_upstream / anchor_shape.
