# PREREG — DIST-01: is the exchange ceiling content-bound (model) or operation-incoherence (instrument)?

**Status: LOCKED 2026-09-21.** the lead researcher spec ("run the distance diagnostic"). Descriptive, forwards only, no new intervention
type (uses the existing cross-role EXCHANGE and TWIN-PATCH operations). Chained to PREREG_RES06.md sha256
`076b270179f52c37c4f569f738544747fea63e90b226c8c7e24225afa8e79409`.

## §1 The two stories RES-06 leaves open (only one survives)
Same span positions, two operations: cross-role EXCHANGE M_S = 0.462, TWIN-PATCH M_S = 0.997.
- **Content-bound (a fact about the MODEL):** exchange holds the literal target text fixed, so the ~0.53 gap is a
  content-bound share of the arbitration — half rides on literal text.
- **Operation-incoherence (a fact about the INSTRUMENT, the lead researcher's competitor, the better one):** both operations target the
  same counterfactual (the twin). Twin-patch installs the twin's residual at the correct position/context — coherent.
  Exchange installs the opposite-slot span's residual at a position it never occupied — a stale hybrid with the wrong
  positional/contextual signature, which the model partially re-derives / rejects (exactly RDV-01's finding, within ~3
  layers). Then exchange caps near half because exchange installs states the model won't fully accept — a ceiling on the
  OPERATION, not on the arbitration.
Both explain everything measured. CAL-01 CANNOT adjudicate (its 8-dim hand-set toy has no contextualization to go stale;
the span feature is a fixed tag, identical wherever placed — incoherence was the unconstructed mechanism).

## §2 The discriminator (descriptive; measures re-derivation, RDV-01 logic)
With the ALL-LAYER exchange the span positions are re-pinned each layer, so a raw distance there cannot diverge. So we
measure what the model COMPUTES at the patched positions at each layer BEFORE the hook re-overwrites it (its
re-derivation R_model[L] = block_L output at the span positions), against the installed value — with TWIN-PATCH as the
on-manifold coherent baseline (it installs the correctly-placed residual).
Per item (twinned, contested), four forwards, no new operation:
1. clean ITEM forward → item_H[L] at spans (origin / reversion target).
2. clean TWIN forward → twin_H[L] at all spans (the installed values + the coherent twin state).
3. EXCHANGE forward (RES-02 op: sys-span←twin usr-span, usr-span←twin sys-span, all L8–31); capture R_exch[L] at spans
   BEFORE each overwrite.
4. TWIN-PATCH forward (sys-span←twin sys-span, usr-span←twin usr-span, all L8–31); capture R_tp[L].
Per layer, cosine distance (mean over span tokens), aggregated template-cluster with bootstrap CI:
- **accept_exch[L]** = cos_dist(R_exch[L], installed exchange value at L) — how much the model ALTERS the misplaced install.
- **accept_tp[L]** = cos_dist(R_tp[L], installed twin value at L) — the coherent baseline (correctly-placed).
- **Δaccept[L] = accept_exch[L] − accept_tp[L]** — the excess re-derivation attributable to the positional/contextual
  signature mismatch = the incoherence, isolated.
- **to_twin_exch[L]** = cos_dist(R_exch[L], twin SAME-slot state at L) — the lead researcher's literal "distance from the twin's state
  at the patched positions" (content-confounded; reported as support).
- **revert_exch[L]** = cos_dist(R_exch[L], item's own span at L) — does the model re-derive back toward the item.

## §3 Readings (pre-committed)
- **Δaccept small and flat** (mean over L≥9 < 0.05, depth-slope CI includes 0) → exchange is installed as coherently as
  twin-patch; the model accepts it → NOT incoherence → **CONTENT-BOUND reading STANDS**: half the arbitration rides on
  literal text; the ~half is a MODEL property.
- **Δaccept large and/or grows with depth** (depth-slope CI > 0, or late-layer Δaccept > 0.10) → exchange installs
  off-manifold states the model re-derives → **INCOHERENCE is real, quantified** → the ~half across KDR, H4, RES-02/04/05
  is a CEILING ON WHAT EXCHANGE CAN DO, not a property of the arbitration. Every exchange number becomes a floor.
- **to_twin_exch grows with depth while accept_tp stays flat** → corroborates incoherence (exchange diverges from the
  coherent twin trajectory the deeper it propagates).
- Report the full per-layer curves regardless; the slope with depth is the decisive statistic.

## §4 The VOID fix (twin-based, executed here)
VOID has failed to execute three times by reaching for a same-length uncontested source that does not exist. Replace it
with a TWIN-BASED coherence gate, executed in THIS run and to be folded into future twin-patch harnesses:
**all-position twin-patch of item i must reproduce the twin's own top-1 next token** (argmax(twin-patch-all-of-i) ==
argmax(clean twin)). Rate over the battery; ≥ 0.90 = the patch mechanism faithfully installs the twin (coherent). This is
the executed coherence gate RES-06 lacked (its M_all=1 is a construction identity, not a check).

## §5 Scope
Descriptive: measures re-derivation/coherence, not an M estimand. Cosine distance is scale-invariant. The
provenance/position split stays undecomposed (RES-03b); this asks a different question (does the operation install states
the model accepts). Zero position import is not relevant here (we WANT to see the model's response to the misplaced
residual). Forwards only; no new intervention type.

## §6 Artifacts
`dist01.json` (per-layer accept_exch/accept_tp/Δaccept/to_twin/revert with CIs; depth-slopes; twin-VOID rate),
`dist01_curves.csv`, `dist01_peritem.npz`, `VERDICT_DIST01.md`, chained to RES-06. SMOKE-gated, watchdog armed
(watchdog_always), auto-terminate, ledger, instance prompt-inj-dist01.

---
## LOCK
**LOCKED 2026-09-21.** Discriminator (§2), readings + decisive statistic (§3), twin-based VOID (§4) fixed. Executor
specifics (cosine distance, per-layer capture-before-overwrite, template-cluster bootstrap on the curves and slopes) in
the runner. sha256 in sidecar `PREREG_DIST01.md.sha256`, chained to RES-06 `076b2701…`. No edit after this line without a
superseding ruling + re-lock.
