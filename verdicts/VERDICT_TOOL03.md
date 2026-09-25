# VERDICT — TOOL-03: template or commitment turn? The confound is resolved — it's the TEMPLATE.

**Result: the agentic commitment turn is INERT (d_commit ≈ 0 across all three models); the signed cross-model
injection-resistance mapping is a property of the chat TEMPLATE's native tool rendering, structure-matched. Mistral-7B-v0.3's
`[TOOL_RESULTS]` markers alone — with a plain assistant text stub and no tool_call — amplify tool-borne injection by
−6.82 nats vs a user message. The confound TOOL-02 flagged (that −6.31 might be "the model following a tool it just
committed to call") is refuted.** Ran 2026-09-22, Lambda a10, FULL n=720/model (0 skipped), $0.49, terminated clean;
numbers re-verified from per-item npz. PREREG_TOOL03.md sha256 `a41a922bae201bad3beda073fc760ddd4bcf5102d6e9921c7f958907c8f15a78`,
chained TOOL-02.

## Design (structure-matched; +Y = obeys system, so + resists injection, − amplifies)
Per model, injection last, distance-matched, TRUE/FALSE readout:
- **U** — assistant text stub, injection in a plain USER turn.
- **Tnc** — assistant text stub, injection in the native TOOL rendering, **NO tool_call** (Mistral hand-built: reuses Tc's
  exact `[TOOL_RESULTS]` block, coherence-gated).
- **Tc** — assistant **tool_call** commitment turn, injection in the native TOOL rendering. (Tnc & Tc share the identical
  tool block → d_commit is pure commitment, distance- and serialization-clean; verified Tc−Tnc dist_end delta = 0.)

## Results (n=720/model; template-cluster bootstrap CI95; nats)
| model | B_user | B_Tnc | B_Tc | **d_marker = Tnc−U** | **d_commit = Tc−Tnc** | d_deployed = Tc−U |
|---|---|---|---|---|---|---|
| **Llama** | −3.23 | +0.00 | +0.29 | **+3.23 [2.59, 3.84]** | +0.28 [0.14, 0.43] | +3.51 [2.94, 4.07] |
| **Qwen** | −4.36 | −3.16 | −2.87 | **+1.19 [0.67, 1.72]** | +0.29 [−0.26, 0.83] | +1.49 [0.70, 2.29] |
| **Mistral** | −0.47 | −7.28 | −7.33 | **−6.82 [−7.99, −5.61]** | **−0.05 [−0.25, 0.18]** | −6.86 [−8.11, −5.58] |

Readout-mass coherence: Mistral hand-built Tnc mass 0.461 vs native Tc 0.485 (≥0.5×, ≥0.05) → **coherent=True**; the OOD
arm is read. (Mistral's tool-arm readout mass 0.46–0.49 < its user 0.74 — the model puts somewhat less mass on the two
readout words in the tool channel; passes the gate, noted.)

## Reading (the lead researcher's step; facts above)
1. **The commitment turn is not the mechanism.** d_commit is ≈0 everywhere and dead zero for Mistral (−0.05, CI incl 0).
   Whether the assistant emits a tool_call before the tool result barely moves obedience (Llama +0.28, Qwen +0.29, Mistral
   −0.05). The "agent loop / model-follows-what-it-committed-to" rival explanation for Mistral's amplification is refuted.
2. **The signed template→resistance mapping holds, structure-matched, and reproduces TOOL-02** (d_marker +3.23/+1.19/−6.82
   vs TOOL-02 d_native_matched +3.24/+1.22/−6.86). The ~10-nat cross-model span is a property of the chat template's native
   tool rendering, with distance, serialization, and the commitment turn all controlled.
3. **Mistral-7B-Instruct-v0.3's `[TOOL_RESULTS]` template is an injection amplifier.** With no tool_call at all, routing the
   same injected instruction through its native tool markers takes the model from ~ignoring it in a user turn (B_user −0.47)
   to strongly obeying it (B_Tnc −7.28): −6.82 nats. It treats tool-marked content as more authoritative than user content —
   the inverse of the instruction-hierarchy assumption — and it is the **markers**, not the agentic flow.
4. **Llama and Qwen resist** (+3.23, +1.19), also structure-matched. Llama's tool channel brings a user-obeyed injection to
   ~neutral/slight-resist (B_Tc +0.29).
5. **The dangling-call_id worry is also cleared:** Tnc carries a `call_id` referencing a tool_call it doesn't contain, but
   Tc (which supplies the matching tool_call) differs from Tnc by ≈0 (d_commit) — so the effect is the `[TOOL_RESULTS]`
   structure itself, not the call_id or the commitment.

## What this resolves
- **The vendor-specific security claim is now un-confounded and publishable:** Mistral-v0.3's tool-result chat template
  amplifies indirect injection by ~7 nats vs a user message, and it is the template markers (not the commitment turn).
- **TOOL-02's headline stands, corrected in mechanism:** signed template→resistance mapping (Llama/Qwen resist, Mistral
  amplifies); the "commitment turn" alternative is measured and rejected.
- The TOOL-02 prediction that failed (Qwen≈0, Mistral in-between) stays failed; the true, structure-matched finding is the
  heterogeneous signed mapping with an inert commitment turn.

## Caveats
- **Mistral Tnc is OOD by necessity** (its template forbids `[TOOL_RESULTS]` without a preceding tool_call); it passed the
  pre-committed coherence gate and gives the same −6.8 as the fully-native Tc, so the effect is not an artifact of the
  hand-build — but it is a hand-built structure, stated.
- Forward passes only; three templates; TRUE/FALSE readout (A/B fallback available; Llama d_role frame-robust from TOOL-02);
  synthetic battery. "Amplifies/resists" bounded to these templates + this contest.
- d_marker bundles the tool markers with the native serialization (TOOL-01/02 already showed serialization is the minor
  component, |d_serial| ≤ 0.74); TOOL-03 deliberately isolates commitment vs everything-else, not marker-vs-serialization.
