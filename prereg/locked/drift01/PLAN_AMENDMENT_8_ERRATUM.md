# HUNT-DRIFT-01 — Amendment 8 ERRATUM 1 (pre-fire; no A8 data exists)

Applies to: PLAN_AMENDMENT_8.md, sha256 6bc527cdafdb8005dc963e30b6300eeb2296fcde0efd08400f098ce3320a6d47 (locked
2026-11-07; its text is left unchanged). Written 2026-11-07 on Nate's "go", after the A8 red-team and DRY and before any
A8 fire. No A8 row has been read on the real model.

## 1. The filler key (A8.1, wording)
A8.1 says the filler is word-pool text of the same token count per turn "keyed by the cell". The built runner keys it by
the transcript the cell's USER turn comes from (drift01_core.filler_pairs(…, tid = that transcript)), exactly as A5 keyed
each transcript's filler. Consequences:
- the unspliced cells (M1.M1, M3.M3) reproduce A5's own rows token for token (asserted on every unit);
- within each user-turn row of the 2 × 2, the cells' fillers have the same user-turn words and the same reply word
  stream, cut at the reply's length, so in R the fillers differ only in reply length — the thing Δ = drift − filler is
  meant to subtract.
The plan's intent (token-matched filler, lengths and distance cancelling within each cell) is unchanged.

## 2. "Never used as a probe" (A8.1, wording)
"never used as a probe" means never a drift probe in panel, Amendment 4, Amendment 5 or Amendment 7 — the exclusions
draw_a8.py applies. All 720 battery items were read once, with no transcript, in B-a's full battery and A3.

## What is NOT changed
The cells, k = 1, the items and their draw, the estimator, P1 (R, predicted negative, 95%), its readings in A8.3, the
verdict rule, every secondary, the seeds, and the runner code.
