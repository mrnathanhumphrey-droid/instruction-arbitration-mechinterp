# CORRECTION (DRAFT — not published) — TPL-02, mistral bC anchor measured system-absent

**Status: draft for the lead researcher's review. Nothing published or altered yet.** Drafted 2026-09-26 after a TPL-03 pre-spend
dry-run surfaced the mechanism. This note proposes what to correct in the public `VERDICT_TPL02.md`; the lead researcher decides
whether/how it goes out.

## What was found
Mistral-v0.3's chat template emits the system message **only on a conversation whose last message is a user turn**
(`{%- if loop.last and system_message is defined %}`). Every probe in this program ends on a **tool-result** turn (the injection is
the final message), so `apply_chat_template` **silently dropped mistral's system directive** from every rendered prompt — no error,
the string simply contained no system instruction. Verified directly: the TPL-02 mistral native render is
`<s>[INST] {user}[/INST][TOOL_CALLS]…[/TOOL_RESULTS]{injection}` with the system string (`"Reply with exactly the word TRUE…"`)
absent. llama, qwen, gemma are unaffected — their templates emit the system regardless of which turn is last.

## Which published TPL-02 claims are affected
1. **`bC(mistral) = +0.89 [0.60, 1.21]`** (per-host table + the "C sign is host-dependent" reading). This was measured with the
   system directive absent from the prompt, so for mistral `Y_signed` was not "resist the injection *in favour of the system
   directive present in the prompt*" — the directive was not present. mistral's bC therefore measures a **different construct** than
   the other hosts' bC (collision-around-injection with **no** system present vs **with** one) and is not comparable to them.
2. **Anchor `Mistral native−rawuser = −6.53` (reproduces TPL-01 −6.53).** This contrast conflates the intended native-vs-rawuser
   difference with a **system-presence gap**: the native render drops the system, while the rawuser render (phi/gemma-style, ending
   on a user turn) surfaces it. The −6.53 reproduced TPL-01 exactly because TPL-01 used the identical message structure and so
   carried the **same** drop — the anchor faithfully reproduced the bug, it did not certify against it.
3. **The reading sentence** listing "mistral (+0.89), qwen (+0.94), gemma (+0.12)" as positive-bC hosts — mistral's membership in
   that set rests on the non-comparable construct above.

## Audit scope (how far this correction reached)
The same template-drop defect was checked for **every host whose anchor is still in use**, against **TPL-02's own renderer** (the run
that produced the anchors, tokenizer/render only, no forward): system-directive presence per host across all TPL-02 cells (native,
rawuser, W00, W00s, W10, W01, W11) and the native−rawuser system-presence gap.
- **llama, qwen, gemma, phi: system PRESENT in every cell; no native−rawuser gap.** Their bC and anchors are valid.
- **mistral: system DROPPED in every cell; native−rawuser GAP present.** Its bC and anchor are the corrected quantities here.
- gemma bC CI (from persisted `tpl02.json`): +0.121 [0.071, 0.171], excludes 0 (retained; phi's [−0.60, 0.03] includes 0, correctly
  excluded on a separate rule).

## What is NOT affected (headline stands)
- **The mechanical verdict RULE-DEAD — 1/5 (llama only) is untouched.** mistral was a *failing* host either way (bC sign wrong),
  and the pass count is driven by llama passing and the rest failing. Removing mistral leaves **RULE-DEAD 1/4** (llama passes;
  qwen, gemma fail on C sign; phi fails). The rule still does not transfer out of sample.
- **The qualitative conclusion — "the dominant term C has a host-dependent sign OOS" — survives on the clean hosts:** llama
  bC −0.52 vs qwen +0.94 and gemma +0.12 (both system-present, valid). mistral was corroborating, not load-bearing, for that claim.
- **llama, qwen, gemma, phi bC values and anchors are valid** (system present in their renders).

## Proposed correction (minimal, factual)
Add a dated note to `VERDICT_TPL02.md` stating: mistral's chat template drops the system on tool-final turns; mistral's bC and its
native−rawuser anchor were therefore measured system-absent and are **withdrawn as comparable per-host quantities**; the headline
(RULE-DEAD) and the host-dependent-C-sign conclusion are unchanged and now rest on the clean hosts (llama/qwen/gemma). Mark mistral
in the per-host table as ⚠ system-absent. Do **not** silently edit the table numbers — strike-through/annotate so the record shows
what was superseded (per the "record the retractions" / canon rules).

## Follow-on to check (not part of this note)
- **TPL-01 mistral** used the same structure → its mistral anchor/effects likely carry the same drop. Worth a separate check before
  any TPL-01 mistral number is re-cited.
- Any other published probe that rendered mistral with a tool-final conversation.
