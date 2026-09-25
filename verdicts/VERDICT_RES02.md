# VERDICT — RES-02: lens-free ceiling (full-residual cross-role exchange)

> **RE-SCOPED by OPX-01 (2026-09-25):** this 0.462 is an **exchange-operator deficit**, not "half the arbitration lives in the
> residual." OPX-01 patched each span one-sided, same-index: the two spans sum to M≈0.97 (additivity gap +0.032). The material
> is all in the spans; the two-sided cross-index *exchange* under-reads it. Read "≈half **under exchange**," not "half in the
> residual." (Component signs are the finding: A_sys −0.93 / A_usr +1.90 — competition with renormalization. See
> `verdicts/VERDICT_OPX01.md`.)

**VERDICT: CEILING-HALF-OR-LESS.** Even complete, lens-free residual exchange at the imperative spans (all layers
L8–31, no probe/subspace/linearity) moves behavior only ~half. Ran 2026-09-20, Lambda a100_sxm4, FULL n=720
(all usable, 0 skipped), terminated clean, $0.25. PREREG_RES02.md sha256
`66ec4cee6f380fc9f33e308eb077fe73dbbc5eee94c163a21bc39a9809bb6cc5`, chained to RES-01b `d00e8852…`. Artifacts:
`res02.json`, `res02_arms.csv`.

## Results (B=−3.879; report Arm1−Arm2 first, per the lead researcher)
| quantity | M | CI95 |
|---|---|---|
| **Arm1 − Arm2** (cross-role net of disruption) | **+0.422** | [0.265, 0.553] |
| Arm1 cross-role (lens-free ceiling) | +0.462 | [0.345, 0.560] |
| Arm2 same-role/same-target/diff-filler (disruption) | +0.040 | [−0.014, 0.099] |

Arm1 ≫ Arm2 (M1−M2 CI excludes 0). dY1=+3.58, dY2=+0.31.

## Reading (the lead researcher's step; facts above)
- **The lens-free CAUSAL ceiling at these spans is ~half (0.46).** Arm1 is materially below 1 → per §4 the
  remainder of the arbitration is NOT in the residual stream at these positions (generation position,
  cross-position composition, or block/header context the imperative-span swap does not carry).
- **Cross-role exchange is real and specific:** Arm1−Arm2 = +0.42 (disruption Arm2 ≈ 0.04). Swapping provenance
  (at fixed content) moves behavior; swapping benign filler barely does.
- **Striking convergence: 0.462 (lens-free, full-span) ≈ 0.471 (KDR-01 linear-subspace, blocks).** The full
  lens-free exchange recovers essentially the same causal M as the linear-subspace exchange. Provisional reading
  (pending the position-import control, §2b): the CAUSAL residual-mediation ceiling is ~half and lens-INVARIANT;
  the extra non-linear provenance RES-01a/b found is richly REPRESENTED but does not translate into ADDITIONAL
  causal mediation at these positions.

## Correction to the post-RES-01a wording
After RES-01a I wrote "KDR's M=0.471 is a floor on the LINEAR lens, not on residual mediation." RES-02 shows
that is wrong on the CAUSAL axis: KDR's ~0.47 is close to the causal ceiling here, not a large undercount.
Precise split:
- **Representation axis (RES-01a/b):** non-linear provenance IS present and decodable at 0.90+, position-
  independent; the linear PROBE undercounted DECODABILITY. STANDS.
- **Causal axis (RES-02):** exchanging the residual moves behavior ~half, lens-invariant (linear ≈ full). KDR's
  M was ~the causal ceiling, not a big undercount. The `linear_saturation_is_a_lens` lesson is about
  decodability and is unaffected; the "KDR undercounts residual mediation" gloss is retracted.

## Limitations logged (not footnotes)
- **§2b position-import is live and material.** The contested battery is system-early/user-late, so cross-slot
  exchange imports the twin's position along with provenance. Arm1=0.46 includes this; provenance-only could be
  higher or lower. Per §4 (Arm1 < 0.80), the decomposition is load-bearing → a position-import control is the
  earned next step BEFORE any provenance attribution.
- **The dedicated VOID arm did not execute** (steered n=0): a runner bug — uncontested was subsampled (stride 6)
  BEFORE grouping by (template,position,slot,target), leaving source groups as singletons → no same-content
  source found. NOT fatal to the reading: unsteered floor = 1.000, and Arm 2 is itself a full same-role span
  swap that moved Y only +0.040 with coherent logits and a sane baseline B — direct evidence the patch does not
  lobotomize the model. But the pre-registered uncontested VOID gate is unfilled; fix (group before subsample)
  before any re-run.
- SMOKE (n=40) gave M1=0.315, weak by n; FULL (n=720) is the result.

## Consequence for the arc
- **Residual mediation causal ceiling at these span positions ≈ half, lens-free.** The other half is elsewhere
  (generation position / composition / block context) — this is the lens-free confirmation of KDR's "half," and
  it bounds where the rest can be.
- Does not touch PRV-04c (attention not the router) or RDV-01 (re-derivation).
- **Earned next step: the position-import control** (decompose Arm1's 0.46 into provenance vs imported position),
  e.g. a position-matched cross-role exchange or a position-only swap arm. THEN, if provenance survives, the
  question of the missing half's locus (generation position vs composition).
