# VERDICT — PRV-01c: INVALID (tokenization-boundary confound). No provenance finding. Needs a read-position redesign + re-run.

**Result: PRV-01c as-run does NOT measure representational provenance — the read position is confounded by a one-token
tokenization boundary, so the mechanical "TRUE-PROVENANCE" (T−W = 0.000) is an artifact and is withdrawn.** At read
position (i) (content-span-final token), the fit-arm channel accuracy is 1.000 at ALL 33 layers INCLUDING layer 0
(embeddings), with decision values saturated at s(T0)=+12.0, s(U0)=−12.0, and s(F)=s(N)=s(R)=+12.0. Cause: the content-final
token is `."` (the final period MERGED with the trailing double-quote) in every quote-bounded arm — T0, F, N, R — versus `.`
alone in U0 (content followed by `<|eot_id|>`). The probe therefore separates on "does the content end in a quote," a local
tokenization fact, not context-integrated provenance; F/N/R all carry the quote so all trivially classify as "tool," giving
T=1.0, W=1.0, T−W=0.0 by construction. rule_zero caught it (T−W=0.000 exact; acc=1.0 at the embedding layer; s saturated).
Ran 2026-09-23, Lambda a10, FULL N=300, $0.31, terminated clean; F/N token-match 300/300 (that part worked). PREREG_PRV01C.md
sha256 `32c8413e838afce89a2e9b4dc112889945cc728114c3fb90236b3141c8974c69` (chained READOUT-01 `afb6d01b...`).

## What actually happened
- read (i) content-final: acc curve = [1.0]×33 (min=max=1.000). s@L0: T0 +12.0 / U0 −12.0 / F +12.0 / N +12.0 / R +12.0.
  → argmax-acc layer selection is degenerate (acc saturated) and lands on L0; T/W/T−W are boundary-token artifacts.
- read (ii) final-prompt token: acc 0.500 at L0 rising to 1.0 by L1 (L*=1); T−W=0.433 → "MIXED", but at L1 this is early
  structural context (tool-block close vs user-block close), not a credible mid-stack provenance read, and the per-layer
  T−W curve was not saved, so it cannot be read off depth. Not salvageable as-is.
- F/N token-match worked (300/300 content-final + length); the battery is fine. The flaw is the READ POSITION + layer
  selection, not the arms.

## Two design flaws (both fixable; both are prereg-METHOD changes → the lead researcher/the reviewer's call)
1. **Read position is boundary-confounded.** Reading the content-FINAL token lets the trailing wrapper character (`"` vs
   `<eot>`) leak channel identity through tokenization. Fix: read at a content-INTERIOR token (identical local token AND
   identical immediate neighbors across all five arms) so L0≈chance (0.5) and any separation at depth is context-integrated
   provenance — the actual quantity. (Average over interior content tokens, excluding the first/last, is the natural choice.)
2. **Layer selection by argmax-acc is degenerate when acc saturates.** With channel ~100% decodable everywhere, argmax picks
   L0. Fix: with the interior read (which makes L0 chance), report the FULL per-layer T−W curve and read the headline off the
   mid-stack region (the prior PRV-01c role probe peaked at L8; §8 predicted L12–20), rather than an auto-argmax. Save
   per-layer T, W, T−W, T′, acc for both read positions.

## Status
- **No provenance claim is made.** PRV-01c is re-opened: redesign the read position (interior content token) + save the
  per-layer curve, then re-run (Llama, ~$0.31). This is a method amendment to the locked prereg — same class as the Phase-2
  degenerate-gate and READOUT-01 respec — so it is the lead researcher/the reviewer's to approve before I re-lock and re-run.
- SPOOF-01's BEHAVIORAL result (markers behaviorally inert; position beats marker identity) stands on its own and does not
  depend on PRV-01c. The REPRESENTATIONAL question (encoded true vs claimed channel) remains OPEN.
- §7 scope held: nothing here says the model uses/ignores the signal; and there is no valid recoverability number to report.
