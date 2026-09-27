# VERDICT — TPL-03: is a host's instruction delimiter a BOUNDARY or an AUTHORITY marker?

**Verdict (mechanical, from the pre-registered bands): SIGN-IDENTITY-DEAD-AS-TESTED — 0 of 2 anchored hosts' `D_own` sign matches
`−sign(bC)` (llama a determinate miss, qwen indeterminate). Per SCOPE-F this negative is ONE-SIDED: own-wrap on the system turn is a
nested, redundant same-family delimiter, not bC's novel wrap of a naked span, so a mismatch is consistent with either no
delimiter-type effect OR the two operations being different operators. The result does NOT cleanly kill boundary-vs-authority as a
delimiter property.**

- prereg: `PREREG_TPL03_PHASE1.md` sha256 `bf7785437de54e4e9c06e4520ab2bdc732ed3cee31bf64ba27f0add6ba39d7b9` (chained OPX-07
  `32c0364c…`); runner `run/tpl03/tpl03_lambda.py` sha256 `133cb7992be7cbef288878ec1f836825f4212eb8f3ae5d25494fe83689998ac6`.
- run: gpu_1x_a100_sxm4 @ asia-south-1, FULL n=720, 3 hosts (llama/qwen anchored, gemma magnitude falsifier), $0.87, terminated
  clean, no orphan. transformers 4.46.0. `run/tpl03/results/tpl03.json` + `tpl03_{host}_peritem.npz`.

## Gates
- **G-CONSTRUCT ✓** payload recoverable in every cell, all hosts. **COLLISION-REALIZED ✓** the own-wrap family delimiter tokenizes to
  real special ids inside the wrapped system, all cells incl injection-present, all hosts. **MASS ✓** no low-mass cells.
- **ANCHOR AUDIT (RULING A) ✓** the mistral system-drop confound was re-checked in TPL-02's own renderer (the run that produced bC):
  llama/qwen/gemma system-present in every cell, no native−rawuser gap; mistral drops everywhere. Anchors for the retained hosts are
  clean in their source run.

## Per-host effects (forced Y_signed; +Y = obeys system; PRIMARY `D_own` = own-wrap − neutral-wrap @ injection-absent)
| host | bC | pred sign (−sign bC) | **D_own** | 95% CI | sign match | CI excl 0 | D_dil (neutral−native) | control-suspect |
|---|---|---|---|---|---|---|---|---|
| **llama** | −0.519 | **+** | **−0.013** | [−0.026, −0.0004] | ✗ | yes → **MISS** | −0.121 | **yes** |
| **qwen** | +0.935 | **−** | **+0.023** | [−0.079, +0.140] | ✗ | no → **INDETERMINATE** | −0.261 | **yes** |
| gemma | +0.121 | (magnitude only) | **−0.083** | [−0.116, −0.045] | — | yes | +0.230 | **yes** |

Cell means (forced Y_signed): **injection-absent** llama native +2.679 / own +2.545 / neu +2.558 · qwen +6.716 / +6.478 / +6.455 ·
gemma +3.672 / +3.819 / +3.902. **injection-present** llama −1.614 / −1.782 / −1.776 · qwen −4.135 / −4.367 / −4.201 · gemma
−4.187 / −4.422 / −4.501. (own ≈ neu ≈ native everywhere; the system is fully obeyed absent, injection wins present, regardless of wrap.)

- **control-suspect on all 3 hosts** (|D_dil| > |D_own|): the inert reserved control token in the system turn perturbs Y *more* than
  the host's own delimiter does. `D_own` (the type effect) is an order of magnitude below bC (±0.5–0.9) on every host.
- **PROPORTIONAL-FORM DEAD (RULING E):** gemma |D_own| CI-low 0.045 > llama |D_own| point 0.013 — the smallest-|bC| host shows the
  *largest* |D_own|, anti-proportional. Kills magnitude-proportionality (not the sign identity).
- SMOKE (n=40) returned RUN INDETERMINATE (both anchored CIs included 0); FULL is the verdict.

## Reading (the lead researcher's step; facts above)
1. **The bC-anchored sign identity does not reproduce under nested same-family system-wrap, and the reason is visible in the numbers:
   the operation is near-idempotent.** Every `D_own` is ≤ 0.08 vs bC ±0.5–0.9, and an *inert* reserved token moves Y as much or more
   than the host's own delimiter (control-suspect ×3). Wrapping the already-delimited system in a redundant copy of its own family
   delimiter changes almost nothing — the model does not re-read a nested same-family delimiter as a fresh boundary.
2. **This is the SCOPE-F branch (ii), pre-registered.** The miss is one-sided: it says this *operationalization* (nested system-wrap)
   cannot test boundary-vs-authority, not that the delimiter has no type. bC wrapped a naked span in a novel delimiter; that operator
   is not reproduced here. Boundary-vs-authority as a *delimiter property* stands untested, not refuted.
3. **The live next move is the pre-registered follow-up:** double-wrap vs single-wrap on the system turn — a direct test of
   same-family nesting idempotence. If double-wrap also ≈ single-wrap, idempotence is confirmed and a different operator (e.g. a
   cross-family delimiter, or wrapping a naked span) is needed to test delimiter type at all.

## Prediction outcome
- Predicted **SPLIT 1/2** (qwen match, llama indeterminate/miss). Actual **DEAD-AS-TESTED** (llama determinate miss, qwen
  indeterminate) — **MISSED** (qwen did not match; it was indeterminate). 8th mechanistic prediction call (OPX-07 was the 7th and the
  only hit), miss; class now 1 hit / 7 miss. Held lightly and discounted in advance: SCOPE-F was pre-registered precisely because a
  miss here is cheap to explain, so this is a weak update on the boundary-vs-authority question.

## Scope (binding)
Property of these hosts / this TOOL-lineage battery / this readout. Content-agnosticism assumed, not tested. **SCOPE-F is the binding
limit: the negative is one-sided (nested same-family wrap ≠ bC's novel wrap).** n=2 anchored sign test (priced p=0.25 for a hit; N/A
here — no hit). mistral excluded (template drops system on tool-final turns; see `CORRECTION_TPL02_mistral_bC_2026-09-26.md`),
phi excluded (bC CI includes 0).
