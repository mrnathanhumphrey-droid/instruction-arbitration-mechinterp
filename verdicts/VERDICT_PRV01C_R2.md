# VERDICT — PRV-01c-r2: VOID (G0b saturation + G6 position-null). The boundary fix worked; two deeper confounds — both pre-predicted — remain. No provenance finding.

**Result: the redesign fixed the PRV-01c boundary confound (G0 embedding-chance PASSES: L0 balanced acc = 0.524 ≤ 0.60 at
the primary interior read — the token-identity artifact is gone), but the run is VOID on the two confounds the PRV-01c-r2 spec
§1 explicitly named. G6 POSITION-NULL fails at 0.995: U0-padded vs U0u-unpadded separate almost perfectly, because the
stub-padding used to equalize content-start offset is arm-correlated (each arm needs a different pad count) and therefore is
itself a channel proxy. G0b NON-SATURATION fails at 32/33 layers ≥ 0.99: the tool-vs-user channel is ~100% linearly decodable
at every layer ≥ 1, i.e. lexical/structural information is laundered forward at depth. The headline T − W_J = +0.095
[0.091, 0.099] is NOT reportable — the run is VOID.** Ran 2026-09-23, Lambda a100, FULL N=297 (drops 3, 1.0%), $0.37,
terminated clean; re-verified from json. PREREG_PRV01C_R2.md sha256 `2f58285c...` (chained PRV-01c `32c8413e`).

## Gate readout
| gate | value | pass |
|---|---|---|
| G0 embedding-chance (L0 acc ≤ 0.60) | 0.524 | ✅ **(boundary fix worked)** |
| G0b non-saturation (<50% layers ≥0.99) | 32/33 ≥0.99 | ❌ VOID |
| G0c shuffled-label null (0.50±0.08) | 0.487 | ✅ |
| G1 probe-validity (≥0.80) | 1.000 | ✅ |
| G2 offset-match (297/297, drop ≤5%) | 297/297, 1.0% | ✅ |
| G3 reproduction (±0.05 vs PRV-01) | +0.045 | ✅ |
| G4 wrapper-separation (\|T−W_J\|≥0.15) | 0.095 | ❌ (markers inert-if-it-counted) |
| G5 read-robustness (range ≤0.25) | 0.084 | ✅ |
| G6 position-null (≤0.60; ≥0.80 VOID) | 0.995 | ❌ VOID |

## The structural impasse (this is the substantive result, and it's a method finding)
1. **G0 is fixed — and that was the whole point of the interior read.** L0 at chance (0.524) confirms the read token is no
   longer a channel giveaway at the embedding layer. The PRV-01c tell is closed.
2. **G6 exposes an unavoidable tension in offset-matching-by-padding.** To match the content-start offset across arms with
   different natural scaffolds, each arm needs a DIFFERENT amount of padding (T0 +4, U0 +9, F/N/J +5, R +0). Pad count is
   therefore perfectly correlated with arm identity, so a probe reads pad count as a channel proxy (0.995). You cannot both
   match the offset (requires arm-varying padding) and avoid the position proxy (requires arm-invariant padding). The padding
   approach is fundamentally confounded, not fixable by choosing a better pad token — this is §1 flaw 1, confirmed as
   structural.
3. **G0b says the channels are too surface-separable for a clean linear provenance probe.** tool vs user differ in role
   header, JSON wrapper, and whole-turn structure; a linear probe hits ~100% at every layer ≥1 on those surface features.
   "Linearly recoverable channel" here is dominated by surface form, not a distinct "provenance" representation — §1 flaw 2,
   confirmed.

## What T − W_J = 0.095 would have said (recorded, NOT claimed — run is VOID)
Had the gates passed, T − W_J = 0.095 (< 0.25, and G4-inert) would have been TRUE-PROVENANCE / markers representationally
inert (the pre-committed H1). W_J = 0.644 ≈ W_N = 0.629 (JSON key vs generic quote wrapper track alike). T′ = −0.135. This is
directionally consistent with SPOOF-01's behavioral inertness — but it rides on a probe that G0b/G6 show is reading surface
form, so it is a suggestive coincidence, not evidence. Not reported as a result.

## Consequence — a design decision for the lead researcher/the reviewer (not mine)
The representational-provenance question is not cleanly answerable by a linear channel probe on the tool-vs-user contrast:
the channels are surface-distinguishable everywhere (G0b) and offset-matching injects its own position proxy (G6). Two honest
routes, both yours to choose:
- **(a) Different contrast / read site** where the two channels share surface form (so the probe can't win on lexical/
  structural features) and where no per-arm padding is needed (so G6 can pass). This is a real redesign, not a parameter tweak.
- **(b) Route the question to the CAUSAL probe (PRV-01d):** patch along a provenance direction and measure ΔY. A causal read
  sidesteps "is the channel linearly decodable" (it always is, from surface form) and asks the question a defender actually
  cares about — whether behavior consults it. PRV-01d was already the staged follow-on; this run is an argument for promoting it.
- SPOOF-01's BEHAVIORAL result (markers inert, position beats marker identity) stands independently and is unaffected.
- §8 scope held: no causal verb used; no recoverability number reported (the one measured is VOID).
