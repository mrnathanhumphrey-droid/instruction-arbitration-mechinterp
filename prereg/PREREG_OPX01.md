# OPX-01 (revised) — Do the two imperative spans additively determine Y, or is the remainder interactional?

**Operation decomposition + additivity test.** the reviewer spec (revised, relayed by the lead researcher) after two construct corrections
confirmed from artifacts (below). **Locked before run; chained to EXT-01.**

- chained_to_EXT01_sha256: `86b066c70025e518f16abf009e752235b42b96997df209b27376e0d38962b9fe`
- runner: `run/opx01/opx01_lambda.py` sha256 `ba5de4e13ae41fa7254667dfe4767a55df90e55376dca761ceadf01ef115ec74`
- model: **meta-llama/Llama-3.1-8B-Instruct**; battery **`stimuli_contested.jsonl`** (+ uncontested for VOID); positions =
  imperative spans; layers **L8–31**; DONE/READY readout — all confirmed from `run/res02/` + `run/res06/`.

## 0. Why the original factor table died (confirmed from artifacts)
Both anchor operations are **twin-sourced**; they differ only in cross-index vs same-index mapping. On cb-flip twins the
twin's usr-span content is byte-identical to the item's sys-span content, so `source` (self/twin) and `region` (cross/same)
are the **same lever** — non-identifiable. And same-region two-sided twin-patch is **become-the-twin**, M≈1.0 **by
construction** (RES-06 flagged this in its own verdict; a value that is 1.0 under the null construction is not evidence — the
discipline that catches it is the level-vs-contrast one applied to constructions).

## 1. Cells — four new, one-sided, none tautological (twin activations, span positions)
| cell | mapping | patched region |
|---|---|---|
| **A_sys** | same-index | system span only (item si ← twin si) |
| **A_usr** | same-index | user span only (item ui ← twin ui) |
| **B_sys** | cross-index | system span only (item si ← twin ui) |
| **B_usr** | cross-index | user span only (item ui ← twin si) |
| **EXCH** | cross, two-sided | RES-02 Arm1 anchor (item si←twin ui, ui←twin si) |
| **CONSTR** | same, two-sided | become-the-twin, ~1.0 BY CONSTRUCTION — **pipeline check only, never evidence** |

From the ledger (cited, not re-run unless noted): exchange 0.462 (reproduced here as EXCH anchor); RES-02 Arm2 disruption
floor (independent-source, same-region) **0.040** — the genuinely-independent-source point the cb-flip twins can't provide.

## 2. Primary quantity — the additivity gap
`gap = 1.0 − [ M(A_sys) + M(A_usr) ]`, bootstrap CI (template-cluster, NTMPL=30, BOOT=5000 — the **same estimator** as
RES-02/06 so the 0.462 anchor is comparable; twin-pairs nested within templates).
- **gap ≈ 0** → the two spans **additively determine Y**; nothing is missing; exchange's 0.46 is an **operator deficit**,
  now demonstrated not assumed → every "0.47 ceiling" number gets re-scoped to the operator.
- **gap large (> 0.10)** → spans jointly carry only part; the remainder is **interactional** — carried by the comparison
  *between* blocks, not either block. That is the missing half, properly located, and it explains why every single-component
  intervention has come back null: there is no component.

## 3. Secondary contrasts
- **A vs B, per region** (M(A_sys)−M(B_sys), M(A_usr)−M(B_usr)) → region-mapping effect, sidedness held.
- **B_sys + B_usr vs EXCH** → sidedness/simultaneity (if two one-sided cross patches sum to more than the two-sided swap,
  simultaneity is lossy).

## 4. Gates
- **ANCHOR-EXCHANGE** — M(EXCH) reproduces **0.462 ± 0.03** (RES-02 Arm1; +0.462 is the raw exchange **LEVEL**, not the
  disruption-netted Arm1−Arm2 = +0.422). Hard: a miss means the harness diverged and nothing downstream is readable.
- **CONSTRUCTION-CHECK** — M(CONSTR) ≥ 0.97. Passing means the harness works; **passing is not evidence for anything.**
- **MASS** — m ≥ 0.10 per cell; runtime-derived forced-readout target if any falls below (forced-readout-target-after-prefix).
- **VOID** — inherited RES-02 (uncontested same-content replacement keeps ≥90% compliance).
- **G-SEGMENT** (tokenizer-only, pre-lock) — spans non-empty and same+cross length-aligned to the twin for all items, 0 failures.
- Counterbalance sign-folded; per-item ΔY, m per cell persisted (`opx01_peritem.npz`); SMOKE(40)→FULL(720).

## 5. Scope — binding
Explains the exchange **operator**, not the model (RES-06: the span positions suffice; this does not relocate arbitration).
CONSTR's ~1.0 is a construction identity, never evidence. Single model; property of these span positions/layers under residual
overwrite.

## 6. Predictions (regime, not midpoint)
- Both gates pass (EXCH ≈ 0.462, CONSTR ≈ 1.0).
- **SUB-ADDITIVE: gap clearly > 0.** Mechanistic (not base-rate): role arbitration is a **comparison** between two blocks; a
  comparison should not be recoverable from either side alone. This would make the six prior single-component nulls **one
  coherent result** (there is no single component because the carrier is the relation).
- Region-mapping (A vs B) carries a real effect; sidedness carries less.
- Explicitly **against**: clean additivity (gap ≈ 0).

## 7. Cost / ops
a100/a10-first, SMOKE(40)→FULL(720), watchdog armed pre-run, terminate in finally, ledger. 7 forwards/item (baseline + 6
cells, each capturing the twin) → ~$0.4.

## User additions
- **Confirmed from artifacts (do-not-assume):** EXCH = RES-02 `build_repl_cross` (twin activations, cross-index, two-sided);
  CONSTR = RES-06 twin-patch on the span (same-index); both L8–31; DONE/READY 71496/46678; twin = same
  template/filler/position, cb-flipped. Single-token targets ⇒ si/ui and their twin counterparts are equal length ⇒ same- and
  cross-index both alignable (G-SEGMENT verifies).
- **Bootstrap = template-cluster** (not per-item) to match the anchor's estimator (probe-upstream: same rows, same
  estimator); noted twin-pairs nest in templates.
- **CONSTR is logged as a construction check in JSON + verdict and is never quoted as evidence** — the null-construction
  discipline that the O2=0.997 error violated.
