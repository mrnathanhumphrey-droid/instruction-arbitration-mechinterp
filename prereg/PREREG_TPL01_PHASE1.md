# PREREG — TPL-01 Phase 1: template classification, LOCKED BLIND (before any Phase 2/3 measurement)

**Locked before Phase 2 is built. Chained to PRV-01h-r.** Classification of seven published chat templates by the corrected
R/S/C/N rule, pinned to the exact template artifacts (sha256 below). A classification changed after any measurement invalidates
the arm. the reviewer spec + amendments (relayed by the lead researcher, approved).

- chained_to_PRV01HR_sha256: `b5b9faa8286fe63aef40ce35b20d97ebcde8bf52dac4444f7ba35cb25b458d3b`
- templates pinned in `run/tpl01/` (captured tokenizer-only, no GPU): shas —
  llama `118bacd5…`, mistral `79f7471e…`, qwen `8aa40ce1…`, qwen3 `51fa65c7…`, mistralnemo `e79cbc01…`, gemma `f2bced8f…`,
  phi `e935669d…`.

## §1 Feature definitions (CORRECTED — R and C independent)
- **R (role-distinct) = 1 iff the tool result occupies its OWN role token in the template's role vocabulary.** Decided from the
  role vocabulary ALONE. Citing delimiter collision while setting R is a scoring error (it double-charges one property) — R is
  re-derived here on "is it a role token," full stop.
- **S (structured escape) = 1 iff the template serializes/escapes the PAYLOAD (tojson or equivalent) rather than inserting it raw.**
- **C (delimiter-family collision) = 1 iff the delimiter wrapping tool content is in the same lexical family as the delimiter
  wrapping system/user INSTRUCTIONS.** Decided from delimiter lexical family ALONE, independently of R.
- **N (no native tool channel)** — the template has no tool role and no tool-result rendering. **N models are NOT scored on
  R/S/C and NOT placed in the ranking.** Prediction is categorical: the injection arrives as plain user text → native resistance
  at the raw-user-text floor.

Score `R + 0.5·S − 2·C` is retained as BOOKKEEPING ONLY. **Predictions are made on ordering and category, never on the score
value** — the weights were fit to three points and affect only tie-breaks.

## §1b Standing honesty clause (must appear in the verdict, verbatim intent)
The R/S/C rule was constructed from three anchored models (Llama, Mistral-v0.3, Qwen2.5). **Qwen3 shares Qwen2.5's template
family and Mistral-Nemo shares Mistral-v0.3's, so neither is an out-of-sample test of the rule's RANKING — both are
within-family reproducibility checks. This design contains NO discriminative out-of-sample test of R/S/C.** The rule is a
hypothesis about what distinguishes these templates and is never described as validated. Phase 3 (template swap) carries the
evidential weight.

## §2 Classification of the seven (from the pinned templates)
| model | model_id | R | S | C | score | category | evidence (tool-result rendering) |
|---|---|---|---|---|---|---|---|
| Llama-3.1 | meta-llama/Llama-3.1-8B-Instruct | 1 | 1 | 0 | +1.5 | scored (anchor) | `<|start_header_id|>ipython<|end_header_id|>` (own role token → R1); `content \| tojson` (S1); header-word `ipython` ≠ system/user family (C0) |
| Mistral-v0.3 | mistralai/Mistral-7B-Instruct-v0.3 | 0 | 1⚠ | 1 | −1.5 | scored (anchor) | `[TOOL_RESULTS]{"content": …}[/TOOL_RESULTS]` — not a role token (R0); `[TOOL_RESULTS]` ∈ `[INST]` bracket-caps family (C1); **S FLAGGED** (see below) |
| Qwen2.5 | Qwen/Qwen2.5-7B-Instruct | 0 | 0 | 0 | 0 | scored (anchor) | tool result in a `user` turn + `<tool_response>` tags → not own role (R0); content raw, no tojson (S0); `<tool_response>` tag ≠ `<|im_start|>` family (C0) |
| Qwen3 | Qwen/Qwen3-8B | 0 | 0 | 0 | 0 | scored (within-family repro of Qwen) | same `<tool_response>`-in-user-turn template family as Qwen2.5 → identical by construction |
| Mistral-Nemo | mistralai/Mistral-Nemo-Instruct-2407 | 0 | 1⚠ | 1 | −1.5 | scored (within-family repro of Mistral) | same `[TOOL_RESULTS]{"content": … \| string …}` rendering as Mistral-v0.3 |
| Gemma-2 | google/gemma-2-9b-it | — | — | — | — | **N** | no tool role; template raises on `system`; only user/model turns → injection becomes raw user text |
| Phi-3.5 | microsoft/Phi-3.5-mini-instruct | — | — | — | — | **N** | no tool role; a `tool` message is silently dropped by the template → injection becomes raw user text |

### Flagged judgment calls (NOT resolved toward the expected value)
1. **Mistral / Mistral-Nemo S.** The template renders `[TOOL_RESULTS] {"content": ' + content|string + ", …`. The payload is
   `content|string` (Python str(), **inserted RAW/unescaped**), placed inside a hand-written `{"content": …, "call_id": …}`
   structure. Two readings: **§2/the lead researcher = S1** (the wrapper is structured JSON) vs **literal criterion = S0** (the PAYLOAD is not
   tojson/escaped — an attacker's text in the payload is not escaped). **Locked at S=1 per §2, flagged for ratification.**
   Ordering/category are IDENTICAL under either (Mistral stays most-negative: −1.5 or −2.0), so no prediction depends on it.
2. **C "lexical family" reading.** Llama C=0 rests on `ipython` being a distinct role WORD inside the shared
   `<|start_header_id|>…<|end_header_id|>` wrapper; Mistral C=1 rests on `[TOOL_RESULTS]` being the same `[CAPS]` bracket TYPE as
   `[INST]`. This is a judgment about what "lexical family" means (distinguishing marker word/bracket-type, not the shared
   wrapper mechanism). Applied consistently across all scored models.
3. **Mistral R=0** is on "not a role token" (inline content inside the `[INST]`/assistant stream), independent of the C
   collision — per the corrected §1.

## §3 Predictions LOCKED (ordering + category only; score is bookkeeping)
- **Scored ordering:** Llama (+1.5) > { Qwen2.5 = Qwen3 (0) } > { Mistral-v0.3 = Mistral-Nemo (−1.5) }.
- **Category N:** Gemma-2 and Phi-3.5 native resistance sits at the raw-user-text floor (no tool channel).
- **Within-family reproducibility:** Qwen3 tracks Qwen2.5; Mistral-Nemo tracks Mistral-v0.3 (amplification, same sign, magnitude
  within ~2×). These are reproducibility checks, NOT ranking tests (§1b).
- **Anchored measured ordering (reproduced by the rule, NOT evidence):** Llama +3.23 > Qwen +1.19 > Mistral −6.82.

## §4 Phase 3 (primary arm; built only after this is locked + the lead researcher signs off)
Serializations transplanted as literal text (PRV-01e substitution move): Llama-style, Mistral-style, Qwen-style, each rendered in
the position the HOST template puts message content. Hosts: the three anchors **plus Gemma-2 and Phi-3.5** (N hosts — every cell
foreign, no native-vs-foreign asymmetry). G-CONSTRUCT: payload byte-identical across all cells per item, tokenizer-verified.
Variance decomposition (serialization vs host) reported over anchor hosts and over N hosts **separately, never pooled**. Two
sharp cells: (1) Llama hosting Mistral-style — does C-collision degrade a resistant model? (2) Gemma or Phi hosting Llama-style —
does a serialization confer resistance on a model that never had a tool role (strongest template-over-model evidence)?

## §5 Scope
Seven models is not a survey. The R/S/C rule stays a hypothesis fit to three points; this design has no discriminative OOS test
of it. TEMPLATE-PREDICTIVE (if Phase 3 lands) licenses "across the templates tested." Disclosure: Mistral-specific results
already went out; if a sharp cell shows `[TOOL_RESULTS]`-style serialization degrading a DIFFERENT model, that generalizes the
vendor finding beyond Mistral and is the lead researcher's to send or not.

## §6 Predictions recorded before Phase 3 (regime, not midpoint)
- Phase 3 dominates Phase 2 in evidential weight (by design).
- TEMPLATE-PREDICTIVE, serialization carrying the majority of between-cell variance (the arc says the action is at this layer).
- Sharp cell 1 (Llama+Mistral-serialization) moves LARGE; sharp cell 2 (N host + Llama-serialization) moves LARGE.
- Explicitly against: an intermediate variance split, or either sharp cell moving intermediate.

## §7 Status
Phase 1 LOCKED. Phase 2/3 NOT built — await the lead researcher's sign-off (loop_me_in: 7 models, phase progression). Nothing on Lambda; public
held; Phase 3b + PRV-04c parked.
