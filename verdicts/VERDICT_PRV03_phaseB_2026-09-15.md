# VERDICT PRV-03 PHASE B (2026-09-15)

## VERDICT: RESIDUAL-STREAM-CLOSED → H3 (attention routing). Pre-committed positive-null → PRV-04.
Mechanical, PREREG_PRV03.md sha256 `1e5ad707…d3f0`. Lambda A100, transformers 4.46.0. Subspace intervention at L8 (Phase A WEAK@L8). B = −3.879 nats.

## Subspace (iterative deflation) — a result in its own right
Deflation curve (refit P_e vs # directions removed), L8:
`0.035, 0.074, 0.086, 0.108, 0.120, 0.137, 0.157, 0.177, 0.184, 0.208, 0.221, 0.238, 0.254, 0.267, 0.287, 0.302, 0.313, 0.327, 0.343, 0.348, 0.361, 0.369, 0.378, 0.382, 0.393, 0.398`
- **k = 25 (hit cap); held-out P_e reached only 0.398, NOT chance (0.45).** ⇒ **for this contrast, provenance at L8 survives removal of ≥25 orthogonal discriminative directions.** Dimension is **≥25 and unmeasured above** — the cap bound before chance, so >25 is a floor, not a measurement. The concept-cone 9–17 came from a different contrast/instrument; it sits **beside** this number, does not overrule it. (Corrected 2026-09-15 per the lead researcher — Edit 2.) P_e is held-out at every step (refit on train split, scored on span-disjoint test — `phaseB_lambda.py:66-67`), so the ≥25 floor is genuine generalization, not fit accuracy.

## Intervention (projection-exchange swap, matched random-subspace control)
- ‖delta_vec‖ = 0.364 (≈2× the L8 needle Δ=0.179); control norm-matched, random 25-dim subspace.
- dYw = −0.124, dYc = −0.201.
- **M_subspace = +0.0100, 95% CI [−0.0090, +0.0331] → INCLUDES 0.**
- Comparison: L8 single-needle (Phase A) M = −0.0284 (CI excl 0). **The full subspace does NOT amplify the needle's sliver — M shrinks toward zero and flips sign, CI includes 0.**
- Manip sanity (zero inferential weight, per prereg): sys→user 0.99, usr→system 1.00 (tautological — projection set by construction).

## Reads (mechanical)
1. **H1 (subspace mediation) NOT supported.** If provenance drove arbitration via a subspace, the full-subspace swap would give a larger, cleaner M than the single needle. It gives a smaller one, CI-includes-0.
2. **Residual-stream story CLOSED** across the arc: PRV-02 L16 null (replicated Phase A) · Phase A no layer LOCALIZED (only a ~3% L8 sliver) · Phase B L8 subspace null.
3. ⇒ **H3 (causal path in the attention pattern — which positions attend where) is the SURVIVING CANDIDATE by elimination, NOT a demonstrated result.** What is established: the causal path is not in any linear residual subspace we could construct, at six layers, up to k=25. Eliminating the residual subspace ≠ demonstrating routing (Corrected 2026-09-15 per the lead researcher — Edit 1). → **H4 (downstream re-derivation) must run BEFORE PRV-04**, because every intervention so far edited a *derived* representation at one layer while leaving the source (role markers, headers, positions) intact — a downstream layer can attend back and recompute provenance, guaranteeing M≈0 without telling us the residual path is non-causal. The layer curve (decodable everywhere, raw separation growing toward output) is positive evidence for re-derivation. PRV-04 (attention-pattern intervention) follows H4.

## Caveat (locked k=25 cap)
Deflation hit the cap without reaching chance (P_e 0.398), so the top-25 subspace does not span all of role — a residual path via dims 26+ is not fully excluded. The top-25 holds the bulk of decodable role and shows no mediation; note the incompleteness in any writeup.

## Standing finding (carried)
B = −3.879 nats: model obeys user slot in content-matched contest. Role represented near-perfectly (95.5%, >25-dim) AND behaviorally strong (3.9 nats), yet no residual direction/subspace connects them. Sharpest sentence in the corpus.

Cost: $0.91; instance terminated clean. Artifacts: `prv03_phaseB.json`, `prv03B_full.log`.

---
## HUMAN RULING & READING — (reserved for the lead researcher; mechanical verdict above stands)
*(the reading is the lead researcher's separate step)*
