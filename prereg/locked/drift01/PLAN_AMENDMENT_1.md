# HUNT-DRIFT-01 — PLAN AMENDMENT 1 (DRAFT 2026-10-24, not locked; EXPLORATORY)

Amends PLAN v0.3 (locked, sha256 fc6b89581178bdd0f4832dce1bd7060d3a7f2a8fa34cd3b172b44ed781d19b77). Everything not
named here stands. Evidence: LOG.md, REAL SMOKE #1 (2026-10-24, $1.13) and the local diagnosis (`kernel_diag.py`).

## Why
1. REAL SMOKE #1 stopped on §4.3's cache-branch check: max |Δlp| 0.398 nats > 0.02 (6 checks).
2. Diagnosis (Llama-3.2-1B, same architecture + vocabulary, the runner's own builders, the frozen smoke transcripts,
   48 readouts): bf16 fresh vs branched max 0.779 / median 0.147 nats under every SDPA kernel; **fp32 max 0.0001** →
   the branching logic is correct; the bf16 gap is rounding from computing the same math in different shapes. The
   0.02 tolerance assumed numerical equivalence in bf16 that does not hold.
3. The API price is $3.29 / h (the plan assumed $2.49). Measured smoke turn times project 64 turns past the cap.
4. M1 and M2 cells with the same persona + seed shared an identical turn 1 (the torch seed derived from the generation
   seed + turn only).
5. The with-instruction transcripts did not collapse to the target word; they drifted.

## Changes
**A1.1 — §4.3 cache-branch check replaced.**
- (a) REPEAT check (stop rule): 48 seeded readouts are computed TWICE on the branched path; every pair must be
  bitwise identical, else STOP (exit 3). This is what the branched path can guarantee in bf16.
- (b) GAP report (descriptive, not gated): the same 48 readouts also as fresh full passes; the distribution of
  |branched − fresh| (max, median, per condition) is reported beside the pilot's JITTER (SD 0.2342) as a measured noise
  floor of the branched readouts.
- (c) The logic validation is the fp32 diagnosis above (max 0.0001), recorded in LOG.md with its script hash.
- Stated in every output: branched readouts differ from fresh-pass values by bf16 rounding (median ≈ 0.15 nats on the
  1B). The primary contrast (drift vs filler) is token-matched, so at each k both are computed in identical shapes.
- The bit-check (fresh, the pilot's exact call) is unchanged.

**A1.2 — depth halved.** 32 drift turns (was 64). K_Q0 = {0, 1, 2, 4, 8, 16, 32}; K_Q1 = {0, 4, 16, 32}. Context budget,
256 tokens / turn, personas, modes, temperatures, seeds, panel unchanged. Phase 4 measures run over 32 turns; the
self-similarity lag (16), loop rule and attractor rule are unchanged. (Li et al. 2024 see drift within 8 rounds.)

**A1.3 — sampling seed.** The torch seed of a generation call = hash of (generation seed, mode index, temperature
index, turn, A/B role, sub-batch offset), so no two cells share a sampling stream. Generation seeds stay 7101101–7101108.

**A1.4 — finding recorded.** Generating under the item instruction does not collapse the drift (turn 1 already ignores
the one-word rule). PLAN §1's design (drift generated without the instruction, the instruction placed on top at probe
time) stands; the 12 with-instruction transcripts remain the comparison, now with a reason to look at them closely.

## Cost (API $3.29 / h; measured turn times; Phase 2 still a projection)
Phase 1 ≈ 1.8–2 h, Phase 2 ≈ 1.5–2.5 h, overhead ≈ 0.5 h → ≈ 4–5 h ≈ $13–16 against the $22 watchdog / $25 cap. The
runner's projection stops (exit 6) still guard it; REAL SMOKE #2 re-measures before any full run.
