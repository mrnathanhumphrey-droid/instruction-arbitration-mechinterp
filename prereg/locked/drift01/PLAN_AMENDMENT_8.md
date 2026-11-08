# HUNT-DRIFT-01 — Amendment 8 — is drift's k = 1 damage carried by a compliant first reply?

Status: LOCKED 2026-11-07 (Nate "Go"), exploratory. The splice family reserved by A6.6 O3 and renumbered by A7.6 O1. Builds on
Amendment 5 (9b92498d…, locked; estimator A5.2) and Amendments 6–7 (demonstration factorials, both supported).

## A8.0 Why
- A5 (post-hoc, verified): drift's damage belongs to the transcript (per-transcript A4 ↔ A5 Spearman +0.99) and is
  largest at k = 1 where the first assistant turn is a compliant answer: drift − filler aligned A at k = 1 is −4.40 for
  M3 P-none and +0.15 for M1 P-none.
- Checked 2026-11-07 on the frozen B-b transcripts: M1's first turn is user "Continue." → assistant asks for
  clarification ("Could you please provide more details…"); M3's is user = the perfect-number prompt → assistant
  answers it ("A perfect number is…").
- A6 / A7: one-word demonstrations in which the assistant did what the user asked (obey) move the readout toward the
  user's word (≈ −3 at n = 1). One reading of A5's k = 1 gap: a compliant first reply teaches "this assistant does what
  the user asks", a clarification request does not. A splice separates the reply from the user turn that produced it.

## A8.1 Design — a 2 × 2 splice at k = 1
- **Transcripts:** the 96 frozen B-b main transcripts (manifest pinned) form 48 matched pairs: M1 and M3 with the same
  persona × temperature × seed. Only turn 1 is used (k = 1).
- **Cells** (user turn × assistant reply, both taken from the pair, as generated ids, never re-encoded):
  | cell | user turn 1 | assistant turn 1 |
  |---|---|---|
  | M1·M1 | "Continue." (M1) | clarification (M1) — A5's M1 row |
  | M3·M3 | perfect-number prompt (M3) | answer (M3) — A5's M3 row |
  | M1·M3 | "Continue." (M1) | answer (M3) |
  | M3·M1 | perfect-number prompt (M3) | clarification (M1) |
- **Contrast per cell:** Δ = Y(drift) − Y(filler), filler = word-pool text of the SAME token count per turn (A5's
  construction, keyed by the cell), so turn lengths and the distance to the readout cancel within each cell.
- **Probe:** the item's system text + the pair's persona (as A5) → the spliced turn 1 → the item's user turn →
  readout Y_signed, locked tokens " DONE" / " READY"; the no-space tokens stored and reported (S5).
- **Items:** 120 items never used as a probe (not panel, A4, A5, A7): 2 DONEsys + 2 READYsys per template, seed
  7101801 (grep 2026-11-07: 71018xx unused) → `a8_items.json`. Re-read: the first 8 A5 items × the 96 transcripts ×
  drift / filler at k = 1, unspliced, compared with A5's a5_q0 rows (reported, not a stop: A5 reached k = 1 by cropping
  a 32-turn prefill, A8 prefills turn 1 only — the known kernel-path gap).
- Rows: 48 pairs × 4 cells × drift / filler × 120 items = 46,080, + the re-read 8 × 96 × 2 = 1,536. Contexts ≤ ≈ 500
  tokens.

## A8.2 Estimator (fixed; A5.2's)
- Per item and cell: c_i = mean over the 48 pairs of Δ. Template-balanced aligned part A and READY part W as A5.2;
  two-way cluster bootstrap over templates × seeds (8 seeds; each seed holds 6 pairs), 2,000 resamples, SEED_BOOT 7101001.
- **Reply effect** R = ½[(Δ_M1·M3 − Δ_M1·M1) + (Δ_M3·M3 − Δ_M3·M1)]: compliant answer minus clarification, the user
  turn held fixed. **User-turn effect** U = ½[(Δ_M3·M1 − Δ_M1·M1) + (Δ_M3·M3 − Δ_M1·M3)].

## A8.3 Primary test — one, direction pre-stated (95% CI)
- **P1: R, aligned part A, predicted NEGATIVE** (the compliant answer pulls the readout away from the system target).
  "supported": upper bound < 0 · "contradicted": lower bound > 0 · otherwise "not supported".
- Readings, written before any data: **supported** = the first reply's content carries the k = 1 gap, whichever user
  turn preceded it (consistent with A6–A7's "does what the user asks" lesson, though A8 does not show that this is the
  route) · **not supported** = the reply alone does not carry it; S1 (U) and S2 (R × U) say whether the user turn or
  the pairing does · **contradicted** = the clarification request pulls harder than the answer.

## A8.4 Secondary (reported, 95%, none carries the headline)
- **S1** U, the user-turn effect. **S2** the interaction (Δ_M3·M3 − Δ_M3·M1) − (Δ_M1·M3 − Δ_M1·M1).
- **S3** each cell's Δ (A and W); M1·M1 and M3·M3 vs A5's k = 1 M1 / M3 values (different items; descriptive).
- **S4** R by persona (P-none, where A5's gap lives, separately) and by temperature.
- **S5** P1 on the no-space readout; cell-level r with the locked readout.
- **S6** the re-read: 8 A5 items, unspliced, vs a5_q0 (agreement, |ΔY| median / max).

## A8.5 Cost and order
- A7: 30,960 rows of ≤ 360 tokens, $1.69. ≈ 47,600 rows of ≤ ≈ 500 tokens, one prefill per (pair × cell × cond × item)
  with no crop reuse → ≈ $3–5. Cap $10.
- Order, each step on its own go: lock (sha into LOG) → draw → build (runner stage + analysis + FAKE tests incl. a
  planted R of each sign and a planted splice break) → DRY / red-team → fire. Then (Nate, 2026-11-07): zoom out over the
  whole hunt's findings and scope.

## A8.6 Choices (SETTLED at lock, Nate "Go" 2026-11-07 = the recommendations: O1 120 never-probed items + the 8-item A5 re-read · O2 all three personas pooled, 48 pairs, P-none in S4 · O3 k = 1 only)
- **O1 Items:** 120 never-probed items + an 8-item A5 re-read (recommended) · or A5's 120 items (the unspliced cells
  re-read A5; but the gap was found on them).
- **O2 Personas:** all three pooled, 48 pairs, P-none in S4 (recommended: more pairs, and A6–A7 had no persona) · or
  P-none only (16 pairs, where A5's gap lives).
- **O3 Depth:** k = 1 only (recommended: the gap is at k = 1; one question) · or k ∈ {1, 2}.
- **Risk, stated:** a reply spliced after the other mode's user turn is off-topic (an answer to a question nobody
  asked; a clarification after a clear question). R then mixes "compliant vs clarifying" with "on-topic vs off" in the
  M3·M1 cell; S2 shows whether the two user turns disagree.
