# PREREG — ATT-01: locate role-sensitive attention

**Status: LOCKED 2026-09-15** ("DRAFT → lock and run. Lock and go."). **Observational only. No causal claim
leaves this probe.** Chained to prior: PREREG_H4.md sha256 `da688c1ec1194bd04cc147aa0aeadc1cc2d5407da8d59670943019abb63f9f75`.
Model: meta-llama/Llama-3.1-8B-Instruct, bf16, **eager attention** (SDPA/flash return no weights), Lambda A100.
Runner frozen: `run/att01/att01_lambda.py`. Runs NOW, parallel to H4, depends on nothing H4 returns.

## §1 Why now
Under H4-flat, attention is the surviving mechanism and we need targets. Under H4-moves, attention is what
does the re-deriving and we need targets. Either branch, this is the next number and it doesn't wait.

## §2 Estimand
For each layer ℓ and head h, at the generation position: does that head's allocation of attention between the
two role blocks track which instruction the model obeys?

## §3 Data
Frozen contested battery `stimuli_contested.jsonl` (`d4145f1a…`), 720 items across both counterbalance cells
(DONE-in-system / READY-in-system) × position. Same split manifest as PRV-01c/03. No new stimuli.

## §4 Measurement
One forward pass per item, attention weights retained (eager), no generation. Per item, per (ℓ,h), at the
final (generation) query position:
- **A_imp** = mass(system-imperative span) − mass(user-imperative span)
- **A_blk** = mass(all system-block tokens) − mass(all user-block tokens) — **headers and role markers
  included** (these may be what matters, not the imperative). Blocks segmented by special tokens
  (`<|start_header_id|>`…`<|eot_id|>`).

**Sign both by the counterbalance EXACTLY as Y_signed:** sign factor s = +1 if target_sys==DONE else −1;
A_signed = s·A, Y_signed = s·(logP(DONE)−logP(READY)) at first assistant token — so lexical and slot priors
cancel the same way they cancel in the readout.

## §5 The two quantities
1. **Allocation:** is mean A_signed ≠ 0 for this head? (Does it split attention by role at all.)
2. **Tracking:** does A_signed correlate (Pearson) with Y_signed across items? (Does its split predict which
   instruction wins.) **(2) is the money quantity** — a head that splits but doesn't track is a bookkeeper;
   a head whose split predicts the outcome is a candidate.

## §6 Statistics
Cluster-bootstrap by template (30 clusters), percentile CI (2.5/97.5), both quantities. Rank all
1024 (ℓ,h) by |tracking correlation| (max of the two lenses). Bonferroni across the head family
(α = 0.05/1024). Report the **full ranked table**, not just survivors.

## §7 Null
Shuffle Y_signed **within template**, recompute the tracking correlation, 1000 draws. Each head's observed r
is read against **its own** null distribution (two-sided empirical p), not against zero. A head "survives"
iff null-p < 0.05/1024 **and** its bootstrap CI excludes 0.

## §8 Falsifier (has teeth)
If no head's A_signed tracks Y_signed above the null under either lens, then attention allocation at the
readout position does not carry the arbitration either — which would weaken H3 as much as the residual nulls
weakened the residual story, and would say the arbitration lives somewhere **neither instrument is looking**.
That is a bigger finding than either branch we planned for. (`falsifier_fired_no_tracking_head` in the JSON.)

## §9 Pre-commitments
- Correlation is correlation. The ranked list is a **target list for a future patching probe**, not evidence
  of a causal path. **No causal verb in the verdict file.**
- Both A_imp and A_blk reported. If they disagree, that disagreement **is** the result — it localizes whether
  the model reads the instruction *text* or the role *marker*.
- No verdict cuts: this probe outputs a ranked table + a null, not a binary.

## §10 Artifacts
`att01_heads.csv` (layer, head, alloc + CI, tracking r + CI, null-p, survive flag — both lenses),
`att01.json` (survivor counts, falsifier flag, top-10), `VERDICT_ATT01.md`. Cost: 720 forwards attention-
retained (SMOKE-gated; SMOKE=60 items). Lambda, auto-terminate in `finally`, ledger.

---
## LOCK
**LOCKED 2026-09-15** on the lead researcher's ruling. Design §1–§10 his; executor specifics (eager attention, Pearson r,
5000 bootstrap / 1000 null draws, Bonferroni family=1024, sign factor s, CSV schema) fixed in the runner.
This file's sha256 in sidecar `PREREG_ATT01.md.sha256`, chained to PREREG_H4 `da688c1e…f9f75`. No edit to
prereg or runner after this line without a superseding ruling + re-lock.
