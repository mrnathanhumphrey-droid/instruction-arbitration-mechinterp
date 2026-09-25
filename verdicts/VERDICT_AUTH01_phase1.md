# VERDICT — AUTH-01 Phase 1: the authority curve. RECENCY IS ORDINAL, not metric.

**Result: across a 16,384-token gap, recency does not weaken and role does not erode — B_recency(16k) = −2.85 ≈ B_recency(0)
= −2.75, and B_role stays flat at ~−0.5 at every distance. The pre-committed §2 reading that fires is "neither moves across
16k → recency is ORDINAL, not metric": the last block wins regardless of how far the competitor is pushed away. This kills
the padding attack — verbosity buys an attacker nothing — and the practical advice inverts.** Ran 2026-09-22, Lambda a100,
Llama-3.1-8B-Instruct, system-vs-user contest, FULL n=720 (n=180 at 16k), $1.53, terminated clean; curve re-verified from
the per-item npz. PREREG_AUTH01.md sha256 `b2d1cc09d924470bb9d03e31ac988f13667c6437b49653e911e388ab09289f42`.

## The curve (primary placement = filler between competitors, varies the recency gap; +Y = obeys system)
| d (gap tokens) | B_role [CI95] | B_recency [CI95] | floor | floor ratio |
|---|---|---|---|---|
| 0    | −0.67 [−0.97, −0.39] | −2.75 [−3.33, −2.19] | 0.49 | 1.00 |
| 256  | −0.40 [−0.64, −0.17] | −2.41 [−3.02, −1.81] | 0.48 | 0.97 |
| 1024 | −0.70 [−1.01, −0.42] | −1.74 [−2.34, −1.20] | **0.26** | **0.52** |
| 4096 | −0.44 [−0.63, −0.25] | −1.91 [−2.59, −1.28] | 0.46 | 0.93 |
| 16384| −0.47 [−0.79, −0.17] | −2.85 [−3.59, −2.14] | 0.49 | 1.00 |

`B_role(d)=(B_normal+B_flipped)/2`, `B_recency(d)=(B_normal−B_flipped)/2` from the order flip, per distance. Distance
verified per cell tokenizer-only (gap grows 14→16,400 tokens in primary; late-imperative→readout held ~13–19).

## Reading (the lead researcher's step; facts above)
1. **Recency is ORDINAL.** At the clean endpoints (d=0 and d=16k, both with a healthy floor ~0.49), B_recency is
   statistically unchanged (−2.75 vs −2.85, CIs heavily overlapping). Putting 16,384 tokens between the two competing
   instructions does not weaken "obey the last one" at all. Recency is last-block-wins, not a function of the gap.
2. **Role authority is distance-invariant and small.** B_role sits at ~−0.5 across all five distances (a mild net
   user-preference beyond position, weaker in the TRUE/FALSE frame than ORD-01's DONE/READY −1.12). It neither grows nor
   decays with d.
3. **Instruction authority does NOT erode with context length (to 16k).** The "both decay" security-worry reading is not
   supported: at 16k both components are at full strength. What matters is ordinal position, not how buried an instruction is.
4. **Security consequence (the inversion):** if recency is ordinal, an attacker gains nothing by padding a tool result or a
   document to push the legitimate instruction "far away" — distance is not the lever, ordinal lastness is. Defensive advice
   that says "keep the system prompt close to the query" is measuring the wrong axis; what matters is which block is last.

## Caveats (stated)
- **Mid-context floor anomaly at d=1024** (floor 0.255, ratio 0.52 — barely clears the 0.5 degradation cut). It is
  non-monotonic (1k sags, 4k and 16k are healthy at ~0.46–0.49) and rests on a small floor subsample (NFLOOR≈30 system-slot
  items), so it is most likely floor-measurement noise rather than a real mid-context collapse. The recency dip at 1k–4k
  (−1.74, −1.91) coincides with it and is plausibly floor-contaminated. **The ordinal finding rests on the d=0 vs d=16k
  comparison, where the floor is fully healthy in both** — not on the noisy middle. A floor re-measure with larger n would
  firm up the middle if it matters.
- **Secondary placement (holds gap ~17, pushes both blocks far from the readout):** B_recency = −3.19 at d=1k, −2.07 at
  d=4k. Adjacent competitors (secondary) show recency at least as strong as far-apart ones (primary) — consistent with
  ordinal, not gap-metric. Only two points, and 4k may be floor-touched; reported, not leaned on.
- Single model (Llama), TRUE/FALSE readout, synthetic battery, ≤16k. Forward passes only; the operative coherence gate is
  the per-cell uncontested floor (twin-VOID N/A here).

## What this sets up
Phase 2 (Mistral, buying authority back with restatement/delimiter) and Phase 3 (does a valid mitigation survive distance)
are next. The ordinal result sharpens Phase 3: since the *attack* does not decay with distance, a mitigation that decays
loses ground on a fixed threat — its shelf life is the whole question.
