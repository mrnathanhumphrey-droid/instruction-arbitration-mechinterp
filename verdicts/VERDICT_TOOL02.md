# VERDICT — TOOL-02: does any model's native chat-template formatting resist tool-borne injection?

**Result: the pre-committed prediction (§6) FAILED, and the true finding is bigger and more security-relevant. Chat-template
design maps to injection resistance in nats — but HETEROGENEOUSLY, spanning ~9 nats across three deployed models, and one
model's native tool channel is an injection AMPLIFIER, not a defense.** Distance-matched role/channel effect (d_role,
+Y = obeys system, so + = resists injection, − = amplifies it):
- **Llama-3.1-8B: d_role = +2.49 [2.02, 2.96]** — the `ipython` role header RESISTS (+2.5 nats). Reproduces TOOL-01's
  +2.51 under a different readout → **frame-robust**.
- **Qwen2.5-7B: d_role = +1.22 [0.67, 1.74]** — the `<tool_response>` tags RESIST (+1.2 nats), CI excludes 0.
  **Prediction (≈0) FAILED** — the cosmetic tags in a user turn DO act as a marker.
- **Mistral-7B-v0.3: d_role = −6.31 [−7.42, −5.26]** — the `[TOOL_RESULTS]` tool channel **AMPLIFIES** injection by
  ~6 nats, CI excludes 0. **Prediction ("in between 0 and +2.5") FAILED — opposite sign, largest magnitude.**

Predicted ordering was llama > mistral > qwen ≈ 0. Actual: **llama (+2.49) > qwen (+1.22) ≫ mistral (−6.31).** Ran
2026-09-22, Lambda a10, FULL n=720 per model (0 skipped), $0.28 total, terminated clean; numbers re-verified from the
per-item npz. PREREG_TOOL02.md sha256 `348608042a6ebbf5f83afc2050e6d4e92113a29ea88efd7d90f717d0c96221e0`, chained TOOL-01.

## Results (n=720/model; template-cluster bootstrap CI95; nats; +Y = obeys system)
| model | native serialization | B_user | B_tool_native | **d_role (matched)** | d_serial | pad_only (d=K) |
|---|---|---|---|---|---|---|
| **Llama** | `ipython` + `{"output":X}` | −3.19 | **+0.01** | **+2.49 [2.02, 2.96]** | +0.74 [0.26, 1.25] | −0.03 [−0.16, 0.09] (K=1) |
| **Qwen** | `user` + `<tool_response>` tags | −4.64 | −3.19 | **+1.22 [0.67, 1.74]** | N/A | +0.22 [−0.10, 0.52] (K=4) |
| **Mistral** | `[TOOL_RESULTS]{"content":X}` | −0.72 | **−7.32** | **−6.31 [−7.42, −5.26]** | −0.54 [−0.91, −0.16] | +0.26 [0.07, 0.43] (K=13) |

(d_role for Qwen ≡ d_native_matched — tags are the marker, not separable. d_native_matched: Llama +3.24, Qwen +1.22,
Mistral −6.86.)

## Reading (the lead researcher's step; facts above)
1. **The prediction failed — that is the pre-registration working.** We publicly pre-committed d_role ≈0/+2.5/in-between
   *before* the run (public commit `c9a48f4`). Qwen's tags are not inert (+1.2), and Mistral is not "in between" — it is a
   strong amplifier (−6.3). Reporting the miss is the point of locking it first.
2. **The real finding is a TEMPLATE-DESIGN → INJECTION-RESISTANCE MAPPING, and it is heterogeneous and signed.** The same
   untrusted-tool-result attack ranges from **+2.5 nats of resistance (Llama) to −6.3 nats of amplification (Mistral)**,
   ~9 nats apart, driven by chat-template design alone — an inspectable, mechanistic explanation for why models differ in
   susceptibility. This is a *stronger* and more actionable result than the "no model resists" ecosystem null we were about
   to elevate: two models resist (Llama strongly, Qwen mildly), one severely amplifies.
3. **Mistral's tool channel is a security liability.** In a plain user turn Mistral roughly ignores the injection
   (B_user −0.72, near neutral); routed through its native `[TOOL_RESULTS]` tool channel it strongly obeys the injected
   instruction (B_tool_native −7.32). Mistral treats tool-result content as highly authoritative — the opposite of the
   instruction-hierarchy assumption that tool outputs are low-privilege.
4. **Serialization (the `tojson`/JSON wrapper) is a MINOR effect everywhere** (|d_serial| ≤ 0.74), never the driver — this
   generalizes TOOL-01's core point (the marker/channel does the work, not the wrapper). Its exact sign is small and
   frame-sensitive (Llama d_serial +0.74 here vs −0.47 in TOOL-01/DONE-READY).
5. **Frame-robustness (Llama re-run):** d_role is frame-invariant (+2.49 vs TOOL-01's +2.51). But **absolute obedience is
   frame-sensitive** — under TRUE/FALSE Llama's native-tool injection is ~neutral (B_native +0.01) vs net-obeyed under
   DONE/READY (−1.97). So TOOL-01's "injection net-obeyed in every condition" is frame-dependent for the absolute level,
   though the *role effect* is not. Serialization sub-effect is also frame-sensitive (§4).

## What this overturns / rescopes
- **Overturns the framing we were about to elevate.** "Three serializations, all inert / no model provides resistance for
  free" is REFUTED: Llama and Qwen resist, and serialization is not the axis — role/channel design is, and it can amplify.
  Good that this ran before the elevated public statement (which was held).
- **Strengthens TOOL-01's mechanism claim** (role marker, not serialization) and confirms it is frame-robust for Llama.
- **New, cross-model:** injection resistance is a *property of the chat template*, heterogeneous and signed; Mistral-v0.3's
  tool channel amplifies.

## Caveats
- **Mistral confound (flagged in the prereg, §note):** Mistral's tool flow requires an assistant `tool_call` turn, which
  the user comparator lacks (text stub). So d_role/d_native for Mistral include that assistant-turn difference — the −6.3
  is the full cost of routing through the *native tool flow* vs a plain user turn (the deployment-relevant quantity), not a
  pure `[TOOL_RESULTS]`-marker effect. The clean, shared-prefix contrast d_serial (−0.54) shows the JSON wrapper is not the
  driver; the marker-vs-flow split is unresolved and is the obvious TOOL-03 follow-up.
- **Frame-sensitivity:** absolute obedience levels and the small serialization effect shift between DONE/READY and
  TRUE/FALSE; d_role does not. A/B fallback re-run available if the truth-frame is suspected to be special (not required —
  d_role reproduced).
- **Distance controlled** by matched comparators (per-item exact, max|Δ|=0); pad-only controls are ≤0.26 nats
  (Mistral's +0.26 CI-excludes-0 but is negligible vs −6.3). Pad-only points at d=1/4/13 persisted for the dose-response.
- Forward passes only; single readout family; three templates; synthetic battery. "Amplifies/resists" is bounded to these
  three templates + this contest.
