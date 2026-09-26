# VERDICT — OPX-07: does the role marker mediate the anchoring, or the block content?

**Verdict (mechanical, from the pre-registered 4-arm matrix): CONTENT-MEDIATED.** Pattern (ROLE, NSAME, NDIST, NSTRIP) =
**(keep, keep, keep, keep)**, all four arms determinate. The block-anchoring of the arbitration asymmetry (its order-reversal
invariance) survives neutralizing the role-word marker (NSAME), replacing it with role-agnostic distinct labels (NDIST), **and**
additionally stripping the system preamble (NSTRIP). **The marker does NOT mediate the anchoring; neither does the preamble; the
block content/filler does.**

- prereg: `PREREG_OPX07.md` sha256 `32c0364cad520ca99ac7a8c27a598fdeb34a8f0d13274fe3153300124620b9f0` (chained TPL-02 Phase-1
  `0e20e5a0…`); runner sha256 `8af333744d6843a7a2b0d250b15df9fc0300072181e5696f94f71943eb700fc4`
- run: a100_sxm4 @ asia-south-1, FULL n=720, $0.60, terminated clean, no orphan. `run/opx07/results/opx07.json` + `_arms.csv` +
  `_peritem.npz`.

## Per-arm (raw ΔY; signs_keep = block-anchored, signs_swap = position-follow)
| arm | dY_sys n/f | dY_usr n/f | asym n/f | B n/f | determinate | outcome |
|---|---|---|---|---|---|---|
| **ROLE** | −7.22 / −12.10 | +14.73 / +9.36 | +21.95 / +21.46 | −3.88 / +1.64 | ✓ | **keep** |
| **NSAME** (→info) | −10.21 / −12.26 | +11.62 / +10.59 | +21.83 / +22.85 | −0.83 / +1.10 | ✓ | **keep** |
| **NDIST** (alpha/beta) | −9.50 / −11.92 | +9.95 / +9.80 | +19.45 / +21.72 | −0.31 / +1.36 | ✓ | **keep** |
| **NSTRIP** (info + no preamble) | −11.85 / −9.93 | +8.73 / +11.38 | +20.58 / +21.31 | +1.32 / −0.51 | ✓ | **keep** |

## Gates
- **ANCHOR ✓ (exact).** ROLE reproduces OPX-02 to the digit: dY normal {−7.22, +14.73}, flipped {−12.10, +9.36}, B flips
  −3.88→+1.64. Harness faithful.
- **SIGN-DETERMINACY ✓ all arms.** nuisance = 0.06·|asym_ROLE_n| = 1.32; threshold 3× = 3.95. Every |dY| exceeds it (smallest
  NSTRIP dY_usr_n +8.73) and every CI excludes 0 → no INDETERMINATE arm; the keep/swap reads are real, not sign-noise.
- **NON-DEGENERACY (step-zero) ✓** flip==twin 0/720 all four arms; near-miss flip==normal 0/720; offset single→single 0 shift;
  span-align 720/720. The design is the non-degenerate reopening of the OPX-06 branch (content kept ⇒ flip is a real reorder).

## Reading (the lead researcher's step; facts above)
- **The marker was never doing the binding.** OPX-02 made the asymmetry look "role-anchored," but with the marker neutralized to
  identical (NSAME), swapped for neutral labels (NDIST), and the preamble also removed (NSTRIP), the asymmetry **still keeps its
  sign under order reversal** — it stays bound to the *block content*, not to the role word or the structural preamble.
- **Magnitude and anchoring dissociate, and this closes the loop.** OPX-03/04 showed none of marker/preamble/filler carries the
  normal-order *magnitude* individually (marker ~0%, preamble ~6%, filler BODY-NULL). OPX-07 shows the *anchoring* — the thing that
  binds the asymmetry to a block rather than a position — is carried by the **content/filler**. So the surviving role-differentiating
  content (system-framing vs user-voice text) is what makes the effect block-bound, even though it is not what sets the effect's size.
  This is the mechanism behind "block-anchored": content-mediation, not marker-mediation.
- **It reconciles the whole OPX line.** With the marker present the effect *appeared* role-anchored (OPX-02) because the role word
  travels with the block's content; strip every lexical distinguisher except content and the anchoring is unmoved. The earlier
  "marker-mediation" hypothesis is refuted by its own construction check.

## Prediction outcome
- ANCHOR reproduces — HIT. Sign-determinacy clean — HIT.
- **CONTENT-MEDIATED (NSTRIP keeps) — HIT.** My pre-registered call, and the **first mechanistic prediction to land in the arc**
  (after six straight misses). Notably it was the call *against* my usual bias (I bet the carrier was diffuse/content rather than a
  clean identifiable token, and that was right). The reviewer's least-surprising alternative — preamble-mediated (NSTRIP swaps) — did
  not occur; the preamble's ~6% magnitude share does not translate into anchoring.

## Scope (binding)
Property of these spans/layers/model/battery, single model, under residual overwrite. "Content-mediated" here means the block's
content/filler (the role-differentiating text that survives NSTRIP), established via the order-reversal keep/swap discriminator with
a per-arm sign-determinacy gate; it is a statement about *anchoring*, not magnitude, and does not relocate where arbitration is
computed. Non-degenerate by construction (content kept); the four-arm matrix separates content from marker, distinct-label, and
preamble.
