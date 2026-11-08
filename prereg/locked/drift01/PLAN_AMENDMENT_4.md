# HUNT-DRIFT-01 — AMENDMENT 4 (LOCKED 2026-11-03; EXPLORATORY)

Amends `PLAN_PHASE_B.md` (1a660770…, locked) and Amendment 3 (34a16542…, locked). Written AFTER the B-b readout
(`out/phaseBb_20261102T230350Z/`) and its post-hoc per-item breakdown (`REAL_B5_ITEMS.md`, ~5 predictors looked at on
n = 8). Everything here is fixed before any fresh-item data exist; it is NOT blind to B-b's 8 items, which is why
those 8 are excluded and every test below runs on fresh items only. Fence unchanged (hunt-only).

## A4.0 What it is for
B5's pooled Δ = −0.62 [−1.86, +0.72] was indeterminate, and 97% of its variance was between items. Post-hoc, the
sign of each item's Δ matched the sign of its k = 0 margin Y_drift(0) on 8 of 8: history (vs filler) seemed to
help whichever instruction already led. A4 tests that on fresh items, re-tests the mean Δ at a size that can
settle it, and adds arms that separate "history amplifies the leader" from "filler flattens toward zero", and
coherence from conversation.

## A4.1 Data — no new generation
- **Transcripts:** the 96 frozen B-b main transcripts (manifest sha 933a8123…), unchanged. With-instruction
  transcripts are not used.
- **Items:** a uniform random draw of **80** from the 720-item battery minus the 12 panel items (all 12 excluded,
  read or not), seed **7101301** (hunt namespace; grep 11-03: unused), drawn by a script before any GPU run. Not
  stratified on anything. The Y_drift(0) spread that results is reported (n > 0, n < 0, quartiles), with no
  re-draw.
- **Arms (per transcript × item):**
  - drift
  - filler (as B5)
  - none (as B5)
  - **prose (new)**: the same skeleton, turns and headers. Every turn's content is replaced by the same number
    of tokens of fluent, non-conversational prose. The prose is a contiguous run through the transcript (turn
    j's user text, then turn j's assistant text, …) taken from one pinned public-domain text (A4.6 O1), starting
    at a per-transcript offset (seed 7101302, tid). Spans are taken in token-id space, so counts match exactly;
    asserted every row, as for filler. Passages are not filtered for the target words; their counts are
    reported (B-b ruled out word overlap).
- k ∈ {0, 1, 2, 4, 8, 16, 32}. Single-pass prefill, probes in descending k (A3.3). Repeat check unchanged.

## A4.2 Primary test — H1 (one test, direction pre-stated)
- Per item i: Δ_i = mean over transcripts and k ∈ {4, 8, 16, 32} of (Y_drift − Y_filler), the B5 Δ.
  Y0_i = mean over transcripts of Y_drift(0).
- **H1: Spearman ρ(Δ_i, Y0_i) over the 80 items, predicted POSITIVE.**
- CI: two-way cluster bootstrap (2,000 resamples, SEED_BOOT 7101001) over **template × seed** (A4.6 O3).
- **Verdicts:**
  - "supported": the CI's lower bound is > 0.
  - "contradicted": the CI's upper bound is < 0.
  - "not supported": anything else. No claim about Y(0) is made in that case.

## A4.3 Secondary (reported; none carries the headline)
- **S1 Mean Δ, same Δ and band as B5:** pooled over the 80 items. Band δ = 0.234, same verdict rules
  (content-driven / distance-driven / drift protects / indeterminate), template × seed clusters. The B5-style
  items × seeds CI is reported beside it. Expected half-width ≈ 0.46 if items were independent; more if they
  cluster by template (the 80 items come from ≤ 30 templates).
- **S2 Sign rule:** the share of items with sign(Δ_i) = sign(Y0_i), against a permutation null (shuffle Y0
  across items 2,000 times, seed 7101303). Items with |Δ_i| < δ are counted as ties and reported separately.
- **S3 H2 headroom, CORRELATED WITH H1:** ρ(Δ_i, h_i) with h_i = mean(Y_drift(0) − Y_none(0)), predicted
  NEGATIVE. The partial ρ given Y0_i is also reported. It is not an independent confirmation of H1.
- **S4 Amplification vs compression:**
  - For each arm X ∈ {drift, filler, prose, none}, the signed move is
    m_X,i = sign(Y0_i) · mean_k∈{4..32} (Y_X(k) − Y_X(0)).
    It is positive when the arm pushes item i further toward the instruction that led at k = 0.
  - Each m_X is pooled over items, with a CI.
  - Pre-stated reading:
    - **"amplification"**: m_drift's CI lies above 0 with point > δ, and m_filler's does not lie below 0.
    - **"compression"**: m_filler's CI lies below 0 with point < −δ, and m_drift's CI includes 0.
    - **"both"**: both conditions hold.
    - **"neither"**: otherwise.
  - Y_X(0) is exact (teacher-forced, no sampling), so this is not regression to the mean from noise. It can
    still reflect an extreme Y0 having more room to move toward 0; the drift vs filler contrast is what reads
    on that.
- **S5 Coherence vs conversation (prose arm):**
  - Δ_prose = Y_drift − Y_prose. Δ_coh = Y_prose − Y_filler.
  - Both are pooled, then run through H1's ρ against Y0.
  - Reading: if drift ≈ prose and both differ from filler, coherent text is enough. If drift differs from
    prose, it is something about conversation.
  - A descriptive contrast with no verdict.
- **S6** By mode (M1 / M3), by k, by counterbalance cell (H1's ρ within DONEsys and within READYsys).
- **S7 The B-b 8 items** are re-read under the same code as a check: their numbers must reproduce
  REAL_b5_q0 on drift / filler / none. They are reported apart and never pooled into H1 or S1.

## A4.4 Observation only
- c0668's k = 1 dip (−5.25, then ≈ 0) is logged as an observation and not tested. The k = 1 profile of the fresh
  items is shown descriptively.

## A4.5 Cost and order (the estimate uses B-b's logged phase-2 rate of ≈ $0.0025 per transcript × item for 3 arms)
- 4 arms at every k: 96 × 80 × 4/3 × $0.0025 ≈ **$26 + ≈ $1.5 boot ≈ $27–28**.
- Option to fit ~$20 (A4.6 O2): "none" at k = 0 only. That covers S3 headroom but drops m_none at k > 0:
  ≈ **$20–21**.
- Order, each step on its own go:
  1. Lock this file (sha into LOG).
  2. Fetch and pin the prose source (sha into LOG).
  3. Draw the 80 items.
  4. Build the runner stage and analysis.
  5. FAKE test (prose plant, token match, a reproduced 8-item check), then DRY, then a red-team pass.
  6. Fire.
- Cap $40, as B-b.

## A4.6 Choices (SETTLED at lock, Nate "Go" 2026-11-03 = the recommendations)
- **O1 Prose source:** Darwin, *On the Origin of Species* (Project Gutenberg #1228), with the Gutenberg header
  and footer stripped. It is expository with few imperatives. Its sha256 goes into LOG.md before any GPU run.
- **O2 Cost:** "none" at every k (≈ $27). S4's m_none is the only read of where history pushes when no
  instruction is present.
- **O3 Clusters:** template × seed for H1, S1–S5. The items × seeds CI is reported beside S1 only.
