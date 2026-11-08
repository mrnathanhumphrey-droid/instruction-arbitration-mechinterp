# HUNT-DRIFT-01 — PLAN AMENDMENT 2 (DRAFT 2026-10-24, not locked; EXPLORATORY)

Amends PLAN v0.3 (fc6b8958…) as amended by Amendment 1 (53576192…). Everything not named here stands. Evidence:
REAL SMOKE #2 (instance 52f2f619…, $0.74, out/smoke_20261025T002107Z/), LOG.md.

## Why
1. **C-shuffled carries no information as specified.** "Drift turns from a different seed's transcript of the same
   mode" — under teacher forcing the probe context has the same system message for every seed of a cell, so the
   shuffled row of transcript t IS the drift row of transcript t' (smoke #2: pooled means identical at every k, 8 of 8
   transcripts distinct). The model has no record of which seed "it" was; any same-cell transcript is equally its
   own history.
2. **Cost.** At the API $3.29 / h, the smoke timings project the full run at ≈ 6.5–7 h ≈ $21–23 — at the $22
   watchdog, so a full run would likely stop part-way (projection, not measurement).

## Changes
**A2.1 — C-shuffled → C-cross (cross-persona history).** For transcript t = (mode, persona p, T, seed), C-cross
uses the drift pairs of transcript (mode, p′, T, seed) with p′ the next persona in the cycle P-none → P-neutral →
P-curious → P-none, under t's OWN probe-time system message (item text + persona p). Same mode, temperature, seed and
turn count; the history was written under a DIFFERENT system persona than the one now on top. Contrast: C-drift
(history consistent with the system persona) vs C-cross (foreign-persona history), at matched turns k; token distance
recorded (not matched) and used in the analysis as for C-shuffled before. Reported per (p, p′) pair. Descriptive.
For P-none the probe-time system message is the item text alone, so its C-cross row tests a P-neutral history under
no persona.

**A2.2 — panel 12 → 8.** Keep panel entries 1, 2, 4, 5, 7, 8, 10, 11 (the first two of each cell, in the seeded draw
order of `panel.json` 71873250…): **c0144 c0062 | c0315 c0239 | c0525 c0457 | c0550 c0668** (templates 24 10 | 22 9 |
27 16 | 1 21). Every filler still appears (0, 2, 3, 5, 3, 1, 4, 2). The with-instruction items (c0144, c0525) and the
non-minimal template 16 (c0457) stay in. The bit-check covers these 8. The full-battery depth-0 Q1 (720 items) is
unchanged.

## Smoke #2 record (descriptive, not results)
Repeat check PASS bitwise; branched-vs-fresh gap on the 8B max 0.259 / median 0.149 nats (pilot JITTER SD 0.234).
Q1 depth 0, P-none, 10 items, mean Y_signed: inert +1.08 · asst_imp −2.73 · asst_int −3.63 · quot_imp −2.51 ·
quot_int −2.54 · user_imp −6.01 · user_int +0.64.

## Cost (API $3.29 / h; projection from smoke timings)
≈ 5–5.5 h ≈ $16–18 against the $22 watchdog / $25 cap. The runner's projection stops (exit 6) still guard it.
