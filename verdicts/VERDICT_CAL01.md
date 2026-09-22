# VERDICT — CAL-01: calibrate the estimator M̂ = −ΔY/2B against known ground truth

**THE ASYMMETRY, STATED FIRST (per §6): this run CAN kill the ~half; it CANNOT certify it. The clean result below
licenses "NO ARTIFACT FOUND under the constructed mechanisms" — it does NOT license "the number is real."**

**Mechanical verdict: BIAS~0-EVERYWHERE. The estimator is unbiased — M̂ recovers the true convex weight w to within
0.0034 across all 20 cells (5 weights × 2 depths × 2 re-derivation states); slope of M̂ on w = 1.006 in every group. All
three artifact hypotheses are rejected, and the sensitivity control confirms the toy would have detected an artifact had
one existed.** Ran 2026-09-21, CPU (hand-built toy, NO Llama forwards, no GPU, no cloud spend), deterministic, torch
2.11.0. PREREG_CAL01.md sha256 `32cf270f37672908bdd06f1d78b929ec9c4bb3119d2e35ef3c1e557903dcb91b`, chained to RES-05
`f0b75186…`. Artifacts: `cal01.json`, `cal01_arms.csv`, `cal01_peritem.npz`.

## Validity gates (§5) — ALL PASS
- **Toy baseline B = −3.777** (target −3.9, |Δ|=0.123 < 0.2 tolerance) — same normalization regime as the real battery.
- **Patch-replaces-A verified at w=1.0** (patch_ok=True): direct inspection confirms the span patch overwrites Channel A
  in the hidden state with the twin's value. Not a mechanically-broken patch faking an artifact.
- **Sensitivity control COLLAPSES to M̂ = −0.0022** (w=1, rederiv on, depth 32, but patch set drops the last layer
  hs[31] = block-30 output): re-derivation then wins and M̂ falls from 1.003 → ~0. **The toy can detect an artifact**, so
  "bias≈0 in the 20 cells" is a real negative, not insensitivity.
- Same harness code path (hook / run / capture / M_of / template-cluster bootstrap) copied verbatim from RES-05. VOID
  discipline present (unsteered 0.500 = steered 0.500; same-content patch preserves behavior — the 0.5 is the
  counterbalanced toy's sign rate, and steered==unsteered is the point).

## Results (M̂ by cell; identical across all four depth×rederiv groups)
| w | M̂ | bias | CI95 |
|---|---|---|---|
| 0.00 | −0.0022 | −0.0022 | [−0.011, 0.006] |
| 0.25 | +0.2492 | −0.0008 | [0.243, 0.255] |
| 0.50 | +0.5006 | +0.0006 | [0.495, 0.506] |
| 0.75 | +0.7520 | +0.0020 | [0.745, 0.759] |
| 1.00 | +1.0034 | +0.0034 | [0.994, 1.013] |

**Slopes of M̂ on w:** d4/rederiv-off 1.006 · d4/rederiv-on 1.006 · d32/rederiv-off 1.006 · d32/rederiv-on 1.006.
**max|bias| = 0.0034.** **Sensitivity control (skip-last-patch): M̂ = −0.0022.**

## Reading (the lead researcher's step; facts above) — the four pre-committed readings
- **Bias ≈ 0 everywhere → CONFIRMED.** No artifact found under any mechanism we could construct. The ~half survives the
  calibration.
- **M̂ pins near 0.5 regardless of w → REJECTED.** M̂ tracks w linearly (slope 1.006, R²≈1); it does not saturate at 0.5.
  The four-instrument agreement near half is NOT an estimator-saturation artifact.
- **Depth-dependent attenuation (0 at 4 layers, negative at 32) → REJECTED.** d4 and d32 are bit-for-bit identical. The
  real-model M's are not turned into floors by depth in the estimator/patch machinery.
- **All-layer patching does not defeat re-derivation → REJECTED.** rederiv-on is identical to rederiv-off (M̂=w in both),
  because the patch is applied to each block's OUTPUT, after that block's internal re-derivation. H4's founding premise
  HOLDS. The sensitivity control is the proof-of-mechanism: it is exactly re-derivation defeating an INADEQUATE patch
  (one that skips the last re-deriving block); the real harness's L8–31 set does not skip it, so it wins.

## What this establishes / what it does NOT (the asymmetry, again — §6)
- **ESTABLISHES:** the estimator arithmetic (M=−ΔY/2B), the all-layer patch mechanism, the normalization, and the
  template-cluster bootstrap are UNBIASED and depth/re-derivation-robust under a known convex mixture. The near-half
  numbers in KDR/H4/RES-02/RES-04/RES-05 are NOT products of estimator saturation, depth attenuation, or re-derivation
  defeat — three concrete artifact stories, all excluded.
- **DOES NOT ESTABLISH:** that the ~half or the RES-05 composition finding is "real." A clean curve licenses "no artifact
  found under the constructed mechanisms," never "the number is real." The toy is 8-dim, hand-set; it shares the harness
  and estimator with the real runs but NOT the model's actual computation. Unconstructed artifact mechanisms remain
  possible. This sentence is the verdict, not a hedge in the discussion.

## Arc position
- The localization/mediation program's instruments are now calibrated: they measure what they claim to measure, without
  the three named biases. RES-02/04 (in-block ceiling ~0.52), RES-05 (distributed composition, missing half not
  localized), RES-01a/b (provenance represented) all survive CAL-01 — the estimator is not manufacturing the ~half.
- Does not touch the substantive findings; it removes three ways they could have been artifacts.

## Method note
Ground truth by construction (hand-set weights) beats "hoping training landed somewhere" — M̂=w is provable
(ΔY = 7.8w ⇒ M = −ΔY/2B = w) and reproduced to 3 decimals. The sensitivity control is the load-bearing companion to a
null: without it, "bias≈0" could mean an insensitive instrument; with it (M̂ 1.003→−0.002 on dropping one patch layer),
the null is informative. unit_of_independence (a same-condition control that can say "never resolvable") /
probe_upstream.
