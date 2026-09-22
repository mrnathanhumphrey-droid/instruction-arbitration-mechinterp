# VERDICT — RES-06: does the decomposition add up?

**Mechanical verdict: REDUNDANT / SUPER-ADDITIVE. Σ = 2.479 ≫ M_all = 1.000 (gap +1.479, CI [1.42, 1.53]). The four
regions OVERLAP massively — span (0.997), readout (0.965), and markers (0.512) each independently carry most or half of
the counterfactual assignment; intermediate content (0.004) carries NONE. This is the OPPOSITE of an interaction term:
regions redundantly re-encode the assignment, they do not synergize.** Ran 2026-09-21, Lambda a100_sxm4, FULL n=720
(0 skipped), terminated clean, $0.35. PREREG_RES06.md sha256 `076b270179f52c37c4f569f738544747fea63e90b226c8c7e24225afa8e79409`,
chained to CAL-01 `32cf270f…`. Artifacts: `res06.json`, `res06_arms.csv`, `res06_peritem.npz`.

## Results (B=−3.8792, n=720; twin-patch, all layers L8–31)
Reading order per §4: **M_all first (gate), then Σ and the gap, then the per-region table.**

- **M_all = 1.0000, CI [1.000, 1.000], dev from 1 = 0.0** — GATE PASSES, but see Caveat 1: this is a CONSTRUCTION
  IDENTITY (within-template twins ⇒ ΔY_t = −2·B_t exactly ⇒ M=1 per bootstrap resample), not an independent
  measurement. It confirms all-position twin-patch reproduces the twin (self-check: item0 −6.625 → +8.312), which is what
  "known total" means; it is not additional validation beyond that.
- **Σ (K+S+I+R) = 2.479, CI [2.42, 2.53]; gap = Σ − M_all = +1.479, CI [1.42, 1.53]** → **Σ ≫ M_all → REDUNDANT /
  super-additive.**
- **Σ_KSI (upstream, readout excluded) = 1.513, CI [1.45, 1.56]; gap_KSI = +0.513, CI [0.45, 0.56]** → still
  super-additive without the tautological readout (driven by S≈1 plus K≈0.5).

| region | M (twin-patch) | CI95 | floor | net of floor | CI95 | floor n |
|---|---|---|---|---|---|---|
| K markers/headers | 0.512 | [0.458, 0.560] | 0.063 | 0.449 | [0.372, 0.522] | 720 |
| S imperative spans | 0.997 | [0.986, 1.006] | 0.040 | 0.957 | [0.898, 1.010] | 720 |
| I intermediate content | 0.004 | [−0.022, 0.037] | −0.091 | 0.095 | [0.017, 0.171] | 240 |
| R readout | 0.965 | [0.960, 0.972] | 0.091 | 0.874 | [0.803, 0.933] | 720 |

## Reading (the lead researcher's step; facts above)
- **The decomposition does NOT add up — it OVER-adds.** gap = +1.48 (CI ≫ 0). This is the §4 "Σ ≫ M_all → redundant"
  branch, the opposite of the interaction branch (Σ ≪ M_all). The pre-committed "interaction term / distributed
  composition would name itself here" is REJECTED: the regions are redundant, not synergistic. Whatever "distributed
  composition" (RES-05) is, it is not regions-that-do-nothing-alone-working-together — it is the assignment being
  redundantly readable from several regions at once.
- **Intermediate content is inert (M_I = 0.004, CI includes 0; net 0.095, barely off 0).** The last untested patchable
  region is ruled OUT as a locus. The missing half is not in the filler.
- **Operation-dependence is the whole story (§5 caveat, now quantified).** Twin-patch S = 0.997 vs cross-role EXCHANGE
  S = 0.462 (RES-02). Both patch the SAME span positions. The difference: twin-patch imports the twin's SAME-slot span
  (opposite TARGET TEXT → a literal instruction flip), while cross-role exchange imports the twin's OPPOSITE-slot span
  (SAME target text, different provenance/position). So:
  - 0.462 (exchange) = behavior movable by provenance/position alone, holding the literal instruction fixed.
  - 0.997 (twin-patch) = behavior movable by flipping the actual instruction text.
  - The ≈0.53 gap between them ≈ **the "missing half" of the exchange arc = the literal-content/assignment-bound
    component that cross-role exchange was designed to hold fixed.** It is not a hidden location; it is the part exchange
    cannot touch by construction. RES-05's "not localized under exchange" and RES-06's "span-localized under twin-patch"
    are consistent: the residual can't move the content-bound half without changing the content.
- **Markers carry ~half the assignment via contextualization (M_K = 0.512, net 0.449, CI ≫ 0).** The marker TOKENS are
  identical between item and twin (headers don't change with counterbalance); what differs is the twin's marker RESIDUALS,
  contextualized by the flipped assignment through attention. Patching them alone flips behavior by ~half. Much larger
  than the cross-role marker number (RES-04 K = 0.091) — again because that was a different operation (swap
  system-marker↔user-marker), not a same-slot twin import.
- **Readout redundant (M_R = 0.965, net 0.874).** The tautology/downstream re-derivation from RES-05, reproduced under
  all-layer twin-patch. It re-encodes the assignment that the span already carries.

## What survives / arc position
- **The "missing half" is resolved as an operation property, not a location.** Cross-role exchange caps at ~0.46 because
  it holds the literal instruction fixed; the uncaptured half is content-bound. Twin-patch (which flips the instruction)
  moves it completely, primarily through the span, redundantly through markers and the readout. Intermediate content is
  inert. Consistent with CAL-01 (the ~half is not an estimator artifact — here it's shown to be an artifact of the
  content-preserving EXCHANGE operation, which is a design property, not an estimator bias).
- **No interaction term found.** The arc's first hope of FINDING (rather than eliminating) a synergistic mechanism did not
  materialize; the mechanism is redundancy.
- Banked cross-role numbers (RES-02 0.462, RES-04 K 0.091) are NOT comparable to these twin-patch numbers and do not enter
  the sum (as locked in §0).

## Caveats (honest)
1. **VOID did NOT execute (steered n=0).** The uncontested same-length source requirement found zero pairs, so the
   patch-coherence VOID gate is NON-EXECUTED, not passed (same class as the RES-02 VOID that hadn't run). Alternative
   coherence evidence: M_all=1.000 (twin reproduced) and the self-check (item0 moved strongly and in the correct
   direction). But the VOID-as-specified is a gap; a future twin-patch run should use a same-length uncontested source or
   twin-based VOID.
2. **M_all = 1.000 [1.0, 1.0] is a construction identity**, not an independent check (within-template twins). It confirms
   "patch all = run twin"; it does not certify per-region coherence beyond that.
3. **M_I floor n = 240/720** (I-region token counts vary with filler length, so region-order-aligned floors exist only for
   the length-matching subset). M_I raw = 0.004 is already ~0, so this barely affects the reading.
4. Twin-patch imports the counterfactual ASSIGNMENT, not provenance in isolation (§5) — the provenance/position split
   stays permanently undecomposed (RES-03b). Zero position import (twins same-length; confirmed n=720 skipped=0).

## Method note
the lead researcher's §0 discipline (ONE operation throughout, with a known total M_all=1) is what makes the super-additive gap
interpretable: without the M_all anchor, Σ=2.48 would be a number without a scale. The operation-dependence (twin-patch
0.997 vs exchange 0.462 on the same positions) is the load-bearing comparison — same region, different operation, and it
names the missing half as content-bound rather than mislocated. probe_upstream (a probe measures the operation applied
to it) / the k=100 lesson (an uninformative-location result can still be a decisive operation result).
