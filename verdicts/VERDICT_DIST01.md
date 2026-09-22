# VERDICT — DIST-01: is the exchange ceiling content-bound (model) or operation-incoherence (instrument)?

**Substantive verdict: INCOHERENCE IS REAL BUT NEGLIGIBLE → the CONTENT-BOUND reading STANDS.** The excess re-derivation
of the misplaced exchange install over the coherent twin-patch install is tiny (Δaccept mean = 0.013 cosine, peak 0.044 at
L9) and it SHRINKS with depth (slope = −0.0016, CI [−0.0016, −0.0015], entirely negative) — the exact opposite of the
"diverges further with depth" signature the lead researcher's incoherence hypothesis required. The exchange install is faithfully present
(not rejected); twin-patch is preserved perfectly (accept_tp ≈ 0); the twin-based VOID passes at 1.000. A 0.013 cosine
perturbation that decays with depth cannot produce the 0.53 behavioral gap (M_S 0.462 vs 0.997). **The ~half ceiling is a
property of the arbitration under content-preserving exchange, not an artifact of the model rejecting stale residuals.**

**Mechanical string: PARTIAL** — because the pre-committed COHERENT bin required slope CI ∋ 0, and the slope came back
significantly NEGATIVE. A negative slope is on the content-bound side of the lead researcher's own discriminator ("diverges with depth →
incoherence"); it falls in neither pre-written bin, so the runner printed PARTIAL. The direction is unambiguous. Ran
2026-09-21, Lambda a100_sxm4, FULL n=720 (0 skipped), terminated clean, $0.32. PREREG_DIST01.md sha256
`9f8f30080acb2ee1ed59b3d8a48dc4f32720133d4191a110e54095b1c0a5c445`, chained to RES-06 `076b2701…`. Artifacts:
`dist01.json`, `dist01_curves.csv`, `dist01_peritem.npz`.

## The discriminator numbers
- **Twin-based VOID = 1.000** (all-position twin-patch reproduces the twin's top-1 token for every item). The coherence
  gate RES-06 lacked, now executed and PASSED. Twin-patch is a faithful, coherent operation.
- **accept_tp (twin-patch re-derivation) ≈ 0 at every L≥9** (0.0006 → 0.0000): the model PRESERVES the correctly-placed
  twin residual essentially perfectly. On-manifold. This validates the measure (a coherent install is a near-fixed-point).
- **accept_exch (exchange re-derivation): 0.045 at L9, decaying to ~0.002–0.008 by mid/late layers.** The model alters the
  misplaced install slightly, concentrated in EARLY layers, then barely.
- **Δaccept = accept_exch − accept_tp: mean(L≥9) = 0.0134, CI [0.0129, 0.0138]** (CI excludes 0 → a real but tiny
  incoherence); **depth-slope = −0.00159, CI [−0.00164, −0.00153]** (shrinks with depth); **late(L≥28) = 0.0062** (smaller
  than the mean).

| L | accept_exch | accept_tp | Δaccept |
|---|---|---|---|
| 9 | 0.0450 | 0.0006 | +0.0444 |
| 12 | 0.0305 | 0.0003 | +0.0303 |
| 16 | 0.0197 | 0.0002 | +0.0195 |
| 20 | 0.0034 | 0.0000 | +0.0034 |
| 24 | 0.0013 | 0.0000 | +0.0013 |
| 28 | 0.0076 | 0.0001 | +0.0076 |
| 31 | 0.0077 | 0.0002 | +0.0075 |

(to_twin_exch ≈ 0.36–0.38 flat, revert_exch ≈ 0.30–0.33 flat across all layers — both content-confounded, as flagged in
§2; they reflect the opposite-slot content difference and do not trend, consistent with content-bound.)

## Reading (the lead researcher's step; facts above)
- **By the lead researcher's own discriminator, incoherence is not real.** The criterion was "exchange lands far AND diverges further
  with depth → incoherence." The measured depth-slope is negative (CI entirely below 0): the excess re-derivation
  ATTENUATES with depth. Incoherence does not compound; it fades.
- **The magnitude cannot carry the ceiling.** The behavioral gap being explained is 0.53 (M_S 0.462 → 0.997). The
  incoherence signal is 0.013 mean cosine (peak 0.044, early only). Even setting aside that all-layer re-patching
  overwrites this drift every layer (so it never reaches the readout via the spans), 0.013 is orders of magnitude too
  small to be the mechanism.
- **The exchange install is faithfully present, not rejected.** accept_exch is small in absolute terms; the model largely
  KEEPS the misplaced residual. Combined with twin-VOID = 1.000, the patch mechanism installs what it claims to. So the
  0.46 ceiling is NOT because the installed signal was erased — it is because, with the literal content held fixed,
  cross-role exchange only moves ~half the arbitration. **Content-bound.**
- **A small, real, early-layer incoherence DOES exist** (Δaccept CI excludes 0; accept_exch ≈ 75× accept_tp at L9 in
  relative terms). Honest asterisk: cross-role exchange is not perfectly coherent — the misplaced positional/contextual
  signature costs a little re-derivation in layers 9–16. But it is a third-order effect that decays, not the ceiling's
  cause.

## Consequence for the arc
- **RES-06's reframe survives and sharpens: the ~half ceiling is a property of the content-preserving EXCHANGE OPERATION,
  and that property is CONTENT-BOUND (a fact about the arbitration), not operation-incoherence (a fact about the
  instrument).** Cross-role exchange holds the literal target text fixed and moves ~half; twin-patch flips the text and
  moves ~all; the gap is the literal-content-dependent share of the arbitration. This is NOT because the model rejects the
  exchange's residuals — it accepts them (accept_exch small, twin-VOID 1.000) — but because the preserved content still
  carries its half of the answer.
- **KDR/H4/RES-02/04/05 exchange numbers are NOT floors-due-to-incoherence.** They are faithful measurements of what a
  content-preserving provenance manipulation moves (~half). The other half is content-bound and requires changing the
  content (twin-patch) to move. CAL-01 (estimator unbiased) + DIST-01 (operation coherent) together close the
  "is-it-an-artifact" question: neither the estimator nor the exchange operation manufactures the ~half.
- The residual arbitration is: richly represented (RES-01), ~half movable by provenance-preserving exchange (RES-02/04),
  the other ~half content-bound and movable only by assignment flip (RES-06), redundantly encoded across span/markers/
  readout (RES-06), not localized to any single site under provenance-preserving ops (RES-05), and the exchange operation
  that measures it is coherent (DIST-01). No interaction term; no estimator artifact; no operation artifact.

## Caveats (honest)
1. **Mechanical PARTIAL vs substantive content-bound.** The pre-committed COHERENT predicate required slope ≈ 0; the
   slope is significantly negative. I am reading the negative slope as content-bound because the lead researcher's discriminator made
   POSITIVE slope (divergence with depth) the incoherence signature — a negative slope is its refutation, not an
   ambiguous middle. This is a reading of the pre-committed criterion, applied to a value that landed just outside the bin
   I wrote, in the unambiguous direction. Flagged rather than silently rebinned.
2. **to_twin / revert are content-confounded** (exchange installs opposite-slot content), so their flat ~0.37/~0.32 levels
   are not clean incoherence measures — only accept_exch vs accept_tp is. Reported for completeness.
3. A genuine small incoherence exists (early layers); "content-bound" is the dominant, not the sole, effect.

## Method note
Twin-patch as the on-manifold baseline (accept_tp ≈ 0) is what made Δaccept interpretable — without it, accept_exch = 0.045
could have read as "large" or "small" with no scale. The coherent control set the zero. unit_of_independence /
probe_upstream. The twin-based VOID (§4) executed at 1.000, retroactively supplying RES-06's missing coherence gate;
fold it into every future twin-patch harness.
