# HUNT-DRIFT-01 — Amendment 7 — does the model follow the system, or go against the user?

Status: LOCKED 2026-11-06 (Nate "Go"), exploratory. Builds on Amendment 6 (1e6de4f1…, locked, P1 supported); estimator A6.2 = A5.2.

## A7.0 Why
Amendment 6: I = (defer − obey) − (agree − defy) = +10.41 [+9.36, +11.44]. Algebraically I = (defer + defy) − (obey + agree):
demo replies that went against the demo user minus replies that did what the user asked. The A6 probe user always asks
for the competing word, so "follow the system" and "go against the user" give the same answer there. Two arms lean to the
second (post-hoc): agree shows the system word throughout yet moves the readout toward the competing word at n = 1
(−2.36), and defy never shows the system word yet gives the largest shift toward it (+4.41).
Separating probe: the user asks for the SYSTEM word (no conflict at the probe). There
  - "go against the user" → the competing word;
  - "follow the system" and "do what the user asks" → the system word;
  - copying the demo reply's word still cancels in I.

## A7.1 Design
- **Probes:** 120 items never probed before (not panel, Amendment 4 or Amendment 5): 2 DONEsys + 2 READYsys per
  template, 30 templates (checked 2026-11-06: every template × counterbalance cell has 5–10 free items, 508 in all).
  Drawn with seed 7101701 (grep 2026-11-06: 71017xx unused) → `a7_items.json`; positions as they fall, reported.
- **Demonstrations:** exactly A6.1. Per probe, 8 draws of 8 ordered items from the other 11 of its template ×
  counterbalance cell (seed 7101702) → `a7_demos.json`; the four arms obey / defer / agree / defy; n ∈ {1, 2, 4, 8},
  nested; arms token-identical but for the DONE ↔ READY swaps, asserted on every row.
- **Two probe turns, one prefix:** each row is read with
  - **C (conflict):** the item's user turn as is (asks for the competing word), i.e. A6's probe → replication;
  - **N (no conflict):** the same user turn with the competing word swapped for the system word (same token count,
    asserted).
  Both read off one prefill (two suffixes per crop).
- **Anchors:** n = 0, once per probe, for C and for N.
- **Readout:** the locked Y_signed (" DONE" / " READY"), as A1–A6. The no-space tokens ("DONE" / "READY", the demo
  replies' tokens) are stored and reported (S5).
- Rows: 120 × 8 draws × 4 arms × 4 n × 2 probes = 30,720 + 240 anchors. Contexts ≤ ≈ 360 tokens (A6 max 356).

## A7.2 Estimator (fixed; A6.2's)
- Per item and contrast: c_i = mean over draws and n. Template-balanced aligned part A and READY part W as A5.2;
  two-way cluster bootstrap (templates × draws), 2,000 resamples, SEED_BOOT 7101001. I_C on C probes, I_N on N probes,
  both with A6's weights (−1, +1, −1, +1) over (obey, defer, agree, defy).

## A7.3 Primary tests — two, directions pre-stated (97.5% CIs, Bonferroni over the two)
- **P1 (replication on fresh items): I_C, A pooled over n ∈ {1, 2, 4, 8}, predicted POSITIVE.**
- **P2 (separation): I_N, A pooled over n ∈ {1, 2, 4, 8}, predicted NEGATIVE** ("go against the user").
  "supported": CI upper bound < 0 → the demonstrations teach whether to go against the user, not to follow the system ·
  "contradicted": lower bound > 0 → following the system (or the user, who now agree with it) wins · otherwise
  "not supported". P2's direction comes from A6's post-hoc arm pattern; this amendment pre-registers that reading.
- Each verdict by the rule as for A6.3.

## A7.4 Secondary (reported, 95%, none carries the headline)
- **S1** each arm − its anchor at every n, C and N; the N anchor's level (headroom, see A7.6 risk).
- **S2** on N: assistant-word and user-word main effects (as A6 S2).
- **S3** I_N at each n.
- **S4** on N: defer − defy (both go against the user; defer also shows the system word) and obey − agree.
- **S5** P1 and P2 on the no-space readout; cell-level r with the locked readout.
- **S6** I_C and I_N by position and by counterbalance (counterbalance descriptive, as A6).
- **S7** I_C here vs A6's +10.41 (different items; descriptive).

## A7.5 Cost and order
- A6: 15,480 rows, $1.25 (0.38 h incl. boot). A second short probe per crop adds about half again → ≈ $2–3. Cap $10.
- Order, each step on its own go: lock (sha into LOG) → draw → build (runner stage + analysis + FAKE tests incl.
  planted I_C / I_N of each sign) → DRY / red-team → fire.

## A7.6 Choices (SETTLED at lock, Nate "Go" 2026-11-06 = the recommendations: O1 this = Amendment 7, splice family → Amendment 8 · O2 120 fresh probes · O3 locked " DONE" readout primary, no-space reported)
- **O1 Numbering:** this question = Amendment 7 and the splice family (A6.6 O3) → Amendment 8 (recommended: it follows
  directly from A6's result and costs ≈ $2) · or splice keeps Amendment 7 and this becomes 8.
- **O2 Probes:** 120 fresh items (recommended: P1 becomes a true replication) · or A6's 120 items and draws (C would
  re-read A6 exactly; less build).
- **O3 Readout:** locked " DONE" primary, no-space reported (recommended: continuity with A1–A6; A6 cell r +0.986) ·
  or no-space primary.
- **Risk, stated:** on N both the system text and the user ask for the system word, so the anchor may sit near the
  ceiling (lp(system word) near 0). Shifts away from the system word (P2's predicted direction) have room; shifts
  toward it may be compressed, which would push a "follow the system" result toward "not supported" rather than
  "contradicted". Reported via S1's anchor level.
