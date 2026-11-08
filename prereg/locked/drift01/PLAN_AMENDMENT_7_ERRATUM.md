# HUNT-DRIFT-01 — Amendment 7 ERRATUM 1 (pre-fire; no A7 data exists)

Applies to: PLAN_AMENDMENT_7.md, sha256 a66ef98b7550d2d26668e36a161e30faf83e0c7d3215a73d505685a95cf5b833 (locked
2026-11-06; its text is left unchanged). Written 2026-11-07 on Nate's "1", after the A7 red-team and before any A7 fire.
No A7 row has been read on the real model.

## What is corrected: the reading of P2's outcomes only
A7.3 reads P2 "contradicted" (I_N lower bound > 0) as "following the system (or the user, who now agree with it) wins".
That reading is wrong. In the four arms the demo assistant says the system word exactly when it follows the system
(defer, agree), so a "follow the system" lesson is the assistant-word contrast, weights (−½, +½, +½, −½) over
(obey, defer, agree, defy). It is orthogonal to I's weights (−1, +1, −1, +1): ½ + ½ − ½ − ½ = 0. A pure follow-the-system
lesson therefore gives I_N ≈ 0.

Corrected readings of P2 (A6 having shown I_C ≈ +10 on the conflict probe):
- **supported** (upper bound < 0): demos that went against the user teach going against what the user asks, even when
  the user asks for the system word.
- **not supported** (CI includes 0): consistent with demos that went against the user teaching "ignore the user / fall
  back on the system word" whatever the user asks; a follow-the-system lesson in the assistant-word form also lands here
  (read it from S2's assistant-word effect on N, which also carries word copying).
- **contradicted** (lower bound > 0): demos that went against the user push toward the system word more when the user
  agrees with it; no simple reading.

## What is NOT changed
The test (I_N, A pooled over n ∈ {1, 2, 4, 8}), its predicted direction (negative), the 97.5% level and Bonferroni over
the two primaries, the verdict rule, P1, every secondary, the seeds, the items, the code and the readout.

## Wording note
"never probed before" in A7.1 means never used as a probe in panel, Amendment 4 or Amendment 5. All 720 battery items,
the A7 probes included, were read once with no demonstrations in B-a's full battery.
