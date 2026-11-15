# VERDICT — PIHOL-01 (block-role frame field on the layer × block-order square)

**Status: CLOSED 2026-11-09. Verdict: INDETERMINATE (power gate failed in both gauges).**
Prereg: `PREREG_PIHOL01_V4.md` (held, not published: it carries run-cost lines; hash in `prereg/PIHOL01_LOCKED_HELD.sha256`), sha256 `3535dc6e5a18abb451d4fdebae9532a2cbf2d4734179405f6919e2a08ad4d704` (matches `.sha256` and `pihol01.json:3`).

## What it asked
On the square formed by layer (L8..L31) and block order (normal vs OPX-02 flip), does carrying the role frame up the layers commute with switching order (FLAT) or not (CURVED)? (PREREG v4 l.9–10.) Holonomy h = ‖M − I‖_F of the rectangle loop operator, read against a calibrated flat-world null, at primary k=5 in two fitting gauges; FLAT requires below-band in both gauges AND a passed power gate (l.30, l.34, l.38–45).

## What ran
- 2026-10-16, 89 min on one cloud A100.
- meta-llama/Llama-3.1-8B-Instruct; 720 two-block items (`prv02/setup/stimuli_contested.jsonl`), 9192 span tokens per order (`pihol01.json:5–6`).
- Gauges: g1 = StandardScaler + Euclidean; g2 = ZCA-whitened (PREREG l.21). k ∈ {3, 5, 10}, primary k=5.

## Mechanical verdict (locked rule)
- Verdict field: "INDETERMINATE (below band but the power gate FAILED: no power on this data)" (`pihol01.json:1183`).
- Gates 1–5 passed (`pihol01.json:15–25`; gate 2 min role accuracy 0.964 g1 / 0.935 g2 vs 0.90 threshold). Power gate g1 = false, g2 = false (`pihol01.json:26–29`).
- h / flat-world band95 (`pihol01.json:526–750`):

| gauge | k3 | k5 (primary) | k10 |
|---|---|---|---|
| g1 | 0.166 / 0.591 | 2.023 / 2.275 | 3.601 / 4.033 |
| g2 | 2.003 / 2.729 | 2.400 / 3.267 | 4.436 / 4.516 |

- All six cells below band. Under PREREG l.41 and l.45, below-band without the power gate is INDETERMINATE, never FLAT.
- Power sweep: planted h stays at ~2.3–3.1 for every δ; g1 calls flip FLAT/CURVED without trend (its "MDC 2.0×φ̄" rests on one CURVED at δ ≈ 2π, i.e. near identity); g2 never detects (`pihol01.json:627–675, 780–828`). φ̄ ≈ π (3.15 / 3.55 rad), so φ̄-scaled plants wrap.
- Local null check reproduced every band; observed h sits at the 13.2 / 49.4 / 53.4 (g1 k3/k5/k10) and 60.4 / 21.3 / 88.6 (g2) null percentiles (`results/pihol01_nullcheck.log:1–6`).

## What this does and does not say
- INDETERMINATE is not a finding. It does not say the frame field is flat, and it does not say it is curved. The instrument had no demonstrated power on this data.
- The g1 k3 cell (0.17 vs band 0.59; 13th null percentile) is UNCLAIMED and is not a result: the power gate ran at k5 only, and 13th percentile is unremarkable under the null (Connection_Program `STATE.md:1061–1062`).
- g2's fiber is effectively 1-D (directions 1–9 flagged past P_e 0.45 at every layer; `pihol01.json:256–520`), so g2 holonomy is close to trivial (`STATE.md:1062`).
- k5 h sits at random-subspace level (PCA median 2.95, Haar 3.19; `pihol01.json:831–840`): per-layer Procrustes on independent fits is noise past the top directions (`STATE.md:1059–1061`).
- No cross-arm claim with the IC fused task-subspace sibling (PREREG l.7). No outside packet was sent (`STATE.md:1068`).

## Closure
- Thread CLOSED 2026-11-09 (the lead researcher).
- PIHOL v5 KILLED. It was never drafted (`STATE.md:1065`, parked at `STATE.md:1953` "waits on A1's estimator question"). Reason: its estimator question (map thread T3, `CROSSOVER_MAP.md:19`, SUSPECT) is unresolved, and its sibling FUSED01 is VOID (`STATE.md:1073–1074`).
- Reopen only if a T3 estimator check (cross-layer probe transfer) passes.

## Files
- Prereg: held; lock hash `prereg/PIHOL01_LOCKED_HELD.sha256`
- Results: `results/pihol01/pihol01.json`
- Null check: `results/pihol01/pihol01_nullcheck.json`; script `runners/pihol01_nullcheck.py`
