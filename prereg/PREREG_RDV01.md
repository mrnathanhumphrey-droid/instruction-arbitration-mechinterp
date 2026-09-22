# PREREG — RDV-01 v2: does the model actually re-derive provenance? (corrected instrument)

**Status: LOCKED v2 2026-09-16.** v1 (sha `125df9c8…4f27`) FAILED as an instrument (content shortcut +
fresh-fit → anchor never scrambled → 0/0; NOT a result). v2 folds the lead researcher's redesign + two additions. Chained to
prior: PREREG_H4.md v3 sha256 `23d169b02ea9c555d6e58179749b836a3c0d06d1ac35e1d0c84583ba706dad4d`. Mechanism
test for the H4 finding. **Observational; no M claim.** Model Llama-3.1-8B-Instruct, bf16, Lambda.

## §1 Estimand
After a single-layer subspace edit at L8, does provenance **decodability** recover at layers above it?

## §2 Method (corrected)
Substrate: **CONTESTED imperative spans, BOTH counterbalance cells pooled** (system vs user slot, content +
DONE/READY lexicon balanced → the probe is forced onto provenance, no shortcut). Group-disjoint split **by
template** (idx%3==0 → test). Edit = projection-EXCHANGE (k=25 deflation subspace fit on the contested
substrate, system −Δ / user +Δ) at imperative-span content tokens.
- **FIXED reference probe (not fresh-fit):** train the provenance probe on **UNEDITED** layer-L residuals
  (train templates); **EVALUATE that fixed probe on EDITED** residuals (test templates). This is exactly what
  Phase B's manip check did — it registered the edit. Fresh-fit was v1's killer (it re-learns the split).
- Passes: (U) unedited, capture {8,9,12,16,24,30,31}; (E8) L8-edit, capture {8,9,12,16,24,31}; (E30) L30-edit
  positive control, capture {30,31}. P_e = held-out error of the fixed layer-L probe on each.

## §3 Two additions (the lead researcher, both cheap)
**(a) POSITIVE CONTROL — edit at L30, read at L31.** One layer of headroom ⇒ near-total PERSISTENCE is the
expected value. If the control persists AND the L8 condition recovers, the instrument is demonstrated working
and both readings are interpretable. If the control also "recovers," it's the probe not the model — and we
learn that for $0.60. (Operational: control **persists** iff L31 does NOT meet the recovery criterion; if it
recovers → verdict CONTROL-FAILED, L8 reading uninterpretable.)
**(b) HARD SCRAMBLE GATE (in-runner, not post-hoc).** The L8 edit MUST drop the fixed L8 probe
(P_e_edit_L8 ≥ 0.30, vs unedited ~0.03) or the run HALTS. No recovery is interpretable without a scramble to
recover from. (v1's lesson: a manip/anchor check must be a hard gate in the code.)

## §4 Recovery — pre-committed BEFORE the number (not binary)
Per-layer P_e trajectory above the edit, against the unedited curve at the same layers. **RECOVERED at layer
L iff (P_e_edit[L] − P_e_uned[L]) ≤ 0.20 × (0.5 − P_e_uned[L])** — i.e. post-edit P_e returns to within 20%
of the unedited-vs-chance gap. Report `gap_closed[L]` = 1 − (P_e_edit−P_e_uned)/(0.5−P_e_uned) (1=fully
recovered, 0=at chance) for every read layer + bootstrap CI (cluster by template) on gap_closed@L31.
**Report the SHAPE, not just the endpoint** — a slow climb across ten layers and a snap-back at L9 are
different mechanisms wearing the same verdict.

## §5 Verdict (pre-committed)
Gates first: L8 not-scrambled → HALT; control not-landed → HALT; control recovers → CONTROL-FAILED. Then, with
control persisting: **RE-DERIVATION-DEMONSTRATED** (L31 recovered or gap_closed ≥ 0.80) / **EDIT-PERSISTS**
(gap_closed@L31 < 0.20 → "re-derived layer-by-layer" leaves the framing) / **PARTIAL** (between; report shape).
M = 0.347 is untouched by any outcome — this can kill the mechanism story while leaving the claim.

## §6 Scope / artifacts
Recovery of decodability is the behavioral SIGNATURE of re-derivation, not a watched circuit rebuild. Edit and
probe on the same contested substrate for internal consistency (mechanism test, not the M estimate). Not free
(no cached residuals) → cheap Lambda ~$0.60–1. `rdv01.json`, `VERDICT_RDV01_<date>.md`. SMOKE-gated,
auto-terminate, ledger. Runner frozen: `run/rdv01/rdv01_lambda.py`.

---
## LOCK
**LOCKED v2 2026-09-16.** Design + two additions the lead researcher's; executor specifics (contested both-cb substrate,
k=25 contested-fit exchange, fixed reference probes, template split, 20%-gap recovery + template-cluster
bootstrap, hard scramble gate, positive control L30→L31, verdict tiers) in the runner. sha256 in sidecar
`PREREG_RDV01.md.sha256`, chained to H4 v3 `23d169b0…4d`. v1 superseded. No edit after this line without a
superseding ruling + re-lock.
