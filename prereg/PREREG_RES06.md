# PREREG — RES-06: does the decomposition add up?

**Status: LOCKED 2026-09-21.** the lead researcher spec ("price it, lock it, run it"). Same harness/estimand/normalization as
RES-02/04/05. Chained to PREREG_CAL01.md sha256
`32cf270f37672908bdd06f1d78b929ec9c4bb3119d2e35ef3c1e557903dcb91b`. CAL-01 established the estimator is unbiased under a
known convex mixture (M̂=w, three artifact mechanisms excluded), so a decomposition measured with it is interpretable.

## §0 The change: ONE operation throughout (twin-patch)
Additivity is only well-posed if every region is patched the same way. RES-02/04 used cross-role EXCHANGE (system↔user
within the item); RES-05's readout arm used TWIN-PATCH (item's residual ← counterbalanced twin's, aligned). Different
operations; their M's do not belong in the same sum. **Twin-patch is used for EVERY region here**, for two reasons:
intermediate content positions cannot be cross-role exchanged (blocks aren't content-matched — the wall that killed the
full-block arm), and **twin-patch partitions the prompt with a KNOWN TOTAL**: patch every position from the twin and you
have run the twin → M = 1 by construction. So the sum has a target — "does it add up" becomes a measurement.
**Cost:** span (S) and markers (K) are RE-MEASURED under twin-patch in this run. Their cross-role numbers (RES-02: 0.462;
RES-04: K 0.091) stay banked and comparable to each other; they do NOT enter this sum.

## §1 Regions — a partition of ALL token positions
- **K** — role markers / headers (BOS, the three `<|start_header_id|>…<|end_header_id|>` header spans, EOT tokens, and the
  `\n\n` after the system & user headers).
- **S** — imperative spans (system + user imperative spans, as RES-02/04).
- **I** — intermediate content (everything else in system/user content that is not an imperative span).
- **R** — the readout position (last token).
Every prompt token belongs to EXACTLY one. Verified per item (complete + disjoint) as a hard gate. Twin-patch, all layers
L8–31, same estimand/normalization.

## §2 Arms (twin-patch, aligned same-index; twins are same-length cb-flips → zero position import)
1. **Each region alone:** M_K, M_S, M_I, M_R.
2. **All four together (M_all)** — the calibration anchor, expected ≈ 1 by construction.
3. **Floors** — per region, patch from a DIFFERENT item's SAME region (foreign content, same slot assignment; region-order
   aligned where token-counts match) — imports content without the counterfactual assignment. Report each region net of
   its floor as the interpretation aid.
4. **VOID** — all-layer readout twin-patch from a same-slot source keeps compliance ≥ 90% of unsteered; group the source
   pool BEFORE subsampling.

## §3 The number
**Σ M_region (K+S+I+R) versus M_all**, with M_all's deviation from 1 reported as the validity check. Secondary (labeled,
not part of the locked readings): Σ_KSI (upstream partition, excluding the tautological readout) versus M_all.

## §4 Readings (pre-committed) — reading order: M_all FIRST (the gate), then Σ and the gap, then the per-region table
- **M_all materially off 1** (|M_all − 1| > 0.15) → harness problem, NOT a finding. HALT and report; do not interpret Σ.
- **Σ ≈ M_all ≈ 1** (|Σ − M_all| ≤ 0.15, paired CI incl 0) → the arbitration DECOMPOSES ADDITIVELY across positions and
  every piece is accounted for. The "missing half" was an artifact of only ever patching subsets.
- **Σ ≪ M_all** (Σ − M_all < −0.15, CI < 0) → a genuine INTERACTION term: regions that do little alone do the work
  together. First mechanism this arc would have FOUND rather than eliminated; names what "distributed composition" means.
- **Σ ≫ M_all** (Σ − M_all > +0.15, CI > 0) → REDUNDANT / super-additive: regions overlap (the downstream readout
  re-derives upstream content). The partition over-counts; Σ_KSI is then the meaningful decomposition.
- **M_I large** (M_I net of floor > 0.25, CI > 0) → the missing half was in the intermediate content all along, and
  composition softens.

## §5 Scope
Twin-patch imports the counterfactual ASSIGNMENT, not provenance in isolation — the standing decomposition caveat carries
unchanged (RES-03b: provenance/position permanently undecomposed). ZERO position import (twins are same-length
counterbalance flips; RES-05 gen-shift=0.0 confirmed), so the diagnostic window is clean.

## §6 Artifacts
`res06_arms.csv`, `res06.json` (M_K/S/I/R + floors + nets, M_all + deviation, Σ + gap CI, Σ_KSI, VOID, partition-gate),
`res06_peritem.npz` (per-item Y all arms — persisted), `VERDICT_RES06.md`, chained to CAL-01. SMOKE-gated, watchdog armed
(watchdog_always), auto-terminate, ledger, instance prompt-inj-res06.

---
## LOCK
**LOCKED 2026-09-21.** Regions (§1), arms (§2), the number (§3), readings + order (§4) fixed. Executor specifics
(partition via BOS/SH/EOH/EOT/\n\n + imperative spans, twin/source pairing from RES-02/04/05, region-order-aligned floors,
paired bootstrap on Σ) in the runner. sha256 in sidecar `PREREG_RES06.md.sha256`, chained to CAL-01 `32cf270f…`. No edit
after this line without a superseding ruling + re-lock.
