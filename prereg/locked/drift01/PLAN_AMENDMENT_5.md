# HUNT-DRIFT-01 — AMENDMENT 5 (LOCKED 2026-11-04; EXPLORATORY)

Amends `PLAN_PHASE_B.md` (1a660770…), Amendment 3 (34a16542…) and Amendment 4 (569919b6…), all locked. Written
AFTER the A4 readout (`out/phaseBd_20261104T034908Z/REAL_B6_ANALYSIS.md`) and its post-hoc counterbalance
decomposition (`POSTHOC_cb_decomp.txt` 89631c7d…). Both primaries below were chosen from that post-hoc look; they
are tested on items no run has read. Fence unchanged (hunt-only).

## A5.0 What it is for
Post-hoc, within the 19 A4 templates holding both counterbalance cells (63 items), the part of each contrast
aligned to the system target was: drift − filler −1.96 / −1.30 / −1.06 at k = 1 / 2 / 4 (fading to −0.49 at
k = 32); prose − filler +0.55 / +1.07 / +1.99 at k = 8 / 16 / 32 (−0.93 at k = 1). The READY-ward part was small
with intervals including zero, except prose at k = 1 (−0.55, toward DONE). A5 tests the two aligned effects with
the estimator that found them, fixed in advance, on fresh items balanced within every template.

## A5.1 Data — no new generation
- **Transcripts:** the 96 frozen B-b main transcripts (manifest sha 933a8123…), unchanged — the same 96 A4 read.
  A transcript-specific effect would carry over; seeds stay a bootstrap cluster for that reason (A5.6 O3).
- **Items:** from the 720-item battery minus the 12 panel items and A4's 80 (628 left; every template holds ≥ 7
  per cell), draw **per template 2 DONEsys + 2 READYsys** without replacement, seed **7101401** (grep 11-04:
  unused) → 120 items, 30 templates, 60 per cell (A5.6 O1). Drawn by a script before any GPU run; no re-draw.
  Early / late position is not stratified; its split is reported.
- **Arms:** drift · filler · prose, exactly as A4 (same pinned prose `pg1228_prose.txt` 164cc858…, same
  per-transcript offsets, seed 7101302; token-matched, asserted every row). "none" is dropped (A5.6 O2).
- k ∈ {0, 1, 2, 4, 8, 16, 32}. Single-pass prefill, probes in descending k. Repeat check unchanged.
- **Repro gate:** 8 A4 fresh items (the first 8 of `fresh_items.json` by item index) are re-read first on
  drift / filler / prose; stop if max |Δ| vs REAL_b6_q0 > 0.05 nats. Reported apart, never pooled.

## A5.2 Estimator (fixed)
- Y = Y_signed = lp(system target) − lp(competing). For a contrast X − F and a k set K, per item i:
  c_i = mean over transcripts and k ∈ K of (Y_X − Y_F).
- Per template t: D̄_t, R̄_t = mean c_i over its DONEsys, READYsys items.
  **Aligned part A = mean over templates of (D̄_t + R̄_t) / 2** (negative = X weakens the system target vs F).
  **READY part W = mean over templates of (R̄_t − D̄_t) / 2** (positive = X pulls toward READY).
- CI: two-way cluster bootstrap over **template × seed**, 2,000 resamples, SEED_BOOT 7101001 (seed weights
  recompute each item's mean; template weights weight A, W).

## A5.3 Primary tests — two, directions pre-stated, Bonferroni (97.5% CIs)
- **P1: drift − filler, A over K_near = {1, 2, 4}, predicted NEGATIVE.**
  "supported": the 97.5% CI's upper bound < 0 · "contradicted": lower bound > 0 · otherwise "not supported".
- **P2: prose − filler, A over K_far = {8, 16, 32}, predicted POSITIVE.**
  "supported": lower bound > 0 · "contradicted": upper bound < 0 · otherwise "not supported".
- Each verdict stands alone; neither is read as confirming the other.

## A5.4 Secondary (reported; none carries the headline; 95% CIs)
- **S1** W for both P1 and P2 contrasts (is a READY-ward part present?).
- **S2** prose − filler A and W at k = 1 alone; A4 showed A −0.93, W −0.55 (descriptive, no verdict).
- **S3** A and W at every k for drift − filler, prose − filler, drift − prose.
- **S4** A4's S1 statistic for continuity: mean Δ = mean(Y_drift − Y_filler), k ∈ {4..32}, band 0.234.
- **S5** by mode (M1 / M3) and by position (early / late): P1's and P2's A.
- **S6** target-family word counts in the prose passages, as A4 (same passages, so same counts).

## A5.5 Cost and order
- A4's logged rate: ≈ $0.0032 per transcript × item for 4 arms → ≈ $0.0024 for 3. 96 × 120 × $0.0024 ≈ $28,
  + repro gate ≈ $1.5, + boot ≈ $1 → **≈ $30–31, ≈ 9.5 h** (60-item option, A5.6 O1: ≈ $16, ≈ 5 h).
- Order, each step on its own go: lock (sha into LOG) → draw → build (runner stage + analysis + self-tests incl.
  planted A and W) → FAKE / DRY / red-team → fire. Cap $40.

## A5.6 Choices (SETTLED at lock, Nate "go" 2026-11-04 = the recommendations: O1 120 items · O2 drop "none" · O3 reuse the 96)
- **O1 Size:** 2 + 2 per template = 120 items, ≈ $31 (recommended; A4's 63-item version gave half-widths
  ≈ 0.6 at 95%, P1 / P2's A4 values are ≈ 1.1–1.2) · or 1 + 1 = 60 items, ≈ $16 (wider; P1 at risk).
- **O2 Drop "none":** yes (recommended; neither primary uses it) · or keep (≈ +33% cost, S4-style m_none only).
- **O3 Transcripts:** reuse the 96 B-b (recommended; no generation, the cost above) · or generate fresh
  transcripts (new seeds; removes the carry-over, roughly + B-b's $9.76 and a generation step).
