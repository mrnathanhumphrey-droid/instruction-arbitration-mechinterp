# CORRECTION (2026-10-16): Mistral's system message was absent from every tool-final prompt (TOOL-02, TOOL-03, TPL-01)

## What was found
Mistral-7B-Instruct-v0.3's chat template attaches the system message only when the conversation's last turn is a user
turn. TPL-03 found this for TPL-02 (see `CORRECTION_TPL02_mistral_bC_2026-09-26.md`, which listed this check as owed).
Rendering TOOL-02, TOOL-03 and TPL-01 with each runner's own functions shows the same in every Mistral-family tool cell.

Prompts containing the item's system instruction, all 720 stimuli, tokenizers only:

| probe | model | user-turn baseline | tool cells |
|---|---|---|---|
| TOOL-02 | Mistral-7B-Instruct-v0.3 | 720/720 | native 0/720 · marker-only 0/720 |
| TOOL-03 | Mistral-7B-Instruct-v0.3 | 720/720 | Tnc 0/720 · Tc 0/720 |
| TPL-01 | Mistral-7B-Instruct-v0.3 | 720/720 | native 0/720 · host_llama 0/720 · host_qwen 0/720 |
| TPL-01 | Mistral-Nemo-Instruct-2407 | 720/720 | native 0/720 |
| all three | Llama-3.1-8B, Qwen2.5-7B | 720/720 | 720/720 in every cell |

## What this withdraws
In Mistral's tool cells the only instruction in the prompt is the injected one. TOOL-02's `d_role` (−6.31), TOOL-03's
`d_marker` (−6.82) and TPL-01's Mistral and Nemo native anchors (−6.53, −5.10) compare a prompt with the system instruction
against one without it. They do not measure the tool channel against a user turn. **"Mistral-v0.3's `[TOOL_RESULTS]`
template amplifies injection" is withdrawn**, as are the cross-model claims built on it: the "~10-nat signed spread" and
TPL-01's "~6.5-nat between-model gap."

## What stands
- Every Llama and Qwen number in TOOL-02, TOOL-03 and TPL-01.
- TOOL-03's commitment-turn null in all three models. Mistral's Tc and Tnc are both system-absent, so `d_commit` compares
  like with like.
- TPL-01's Llama-host cells, including sharp cell 1: Mistral's serialization inside Llama does not drag Llama toward
  Mistral's level. That now has an explanation: Mistral's level came from the missing system instruction, not its wrapper.
- TPL-01's within-Mistral-host ordering compares cells that are all system-absent. It describes obedience with no system
  instruction present, not resistance.
- TPL-02's RULE-DEAD verdict (already corrected for this on 2026-09-26).

## What the finding becomes
A defect in a shipped template. With the vendor's own `apply_chat_template`, any conversation that ends on a tool result
reaches Mistral-7B-Instruct-v0.3 with no system prompt, and Mistral-Nemo-Instruct-2407 behaves the same in TPL-01. An
instruction injected into a tool result competes with nothing.

**Not yet measured:** Mistral's real tool-vs-user effect with the system instruction present (needs a re-run).
**Not yet checked:** whether this template behaviour has been reported elsewhere.

## Reproduce
`python runners/check_system_presence.py` (tokenizers only, no GPU; needs HuggingFace access to the five models).

The original verdicts' numbers are not edited; each carries a banner pointing here.
