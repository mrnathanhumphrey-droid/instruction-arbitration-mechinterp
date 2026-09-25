# EXT-01 — Does the role marker carry the "missing half" RES-02 left in the residual?

**Sharp 2-level form (Llama).** the reviewer spec was a graded inclusion sweep; a tokenizer-only recon (below) showed Llama-3.1's
template does not support a graded curve, so on the lead researcher's ruling ("1 first") this runs the sharp form the
question reduces to. **Locked before run; chained to TPL-01 Phase 2/3.**

- chained_to_TPL01_PHASE23_sha256: `08d2f0827031b1f4707052b438ae111696b56eb3583c733d3f0483c3cbb661d6`
- runner: `run/ext01/ext01_lambda.py` sha256 `838799ffe141636bb314d7afc16c998c23eff613f9d7ba4d08be551d10aff3b0`
- model: **meta-llama/Llama-3.1-8B-Instruct** (bf16) — confirmed from `run/res02/res02_lambda.py`.
- battery: **`stimuli_contested.jsonl`** (+ `stimuli_uncontested.jsonl` for VOID), DONE/READY readout,
  `Y = logP(DONE) − logP(READY)` at first assistant token, signed by which role holds the target.
- mechanism: RES-02's cross-role residual overwrite at L8–31, twin = same template/filler/position, other counterbalance.

## 0. Recon that forced the sharp form (tokenizer-only, all 720 items, 0 failures)
In Llama-3.1's rendered template the **only cross-role-swappable, role-distinguishing marker token is the role word**
(`system` = 9125, `user` = 882 — each a single token). Every other structural token is **identical in both blocks**
(`<|start_header_id|>` 128006, `<|end_header_id|>` 128007, `\n\n` 271, `<|eot_id|>` 128009) → swapping them cross-role is a
no-op. The one asymmetric role signal (an auto-injected **system-only date preamble**) cannot be position-aligned. So a graded
"add more markers" curve is not well-posed here; there is exactly one marker to add. The graded sweep belongs on a
richer-template model (Mistral/Qwen) — noted, not run here.

## 1. Arms (cross-role residual exchange, L8–31, content-matched twin)
- **L0** — imperative span only. **Reproduces RES-02 Arm1 (anchor).**
- **ROLE** — imperative span **+ the role-word header token** (system↔user, the role marker).
- **CTRL** — imperative span **+ the `<|end_header_id|>` token** (128007, identical id in both blocks: a shared,
  NON-role-distinguishing header token, position-matched and token-matched to ROLE). The neutral control. Its residual still
  differs by context, so it tests "does swapping *a* header-position residual recover anything" without the role lexeme.
- **DISR** — same-role/diff-filler at L0 (RES-02 Arm2 disruption floor), for the L0 Arm1−Arm2 anchor.

**marker gain = M(ROLE) − M(CTRL)** — the role-word's contribution net of generic header-position-residual swapping.
G-TOKENMATCH is automatic: ROLE and CTRL each add exactly one token per block.

## 2. Metrics
Raw ΔY in nats primary (M reported too, normalized by the per-order baseline; M retired as *the* headline after ORD-01 but
kept here because the anchor is an M). Per-arm M + paired template-cluster bootstrap CI (NTMPL=30, BOOT=5000). Per-cell mass
m = P(DONE)+P(READY) reported (Llama contested readout has been high-mass; forced slot with runtime-derived target only if a
cell falls < 0.10 — forced-readout-target-after-prefix). **Reference line:** RES-06 twin-patch S ≈ 0.997 at these
positions (quote, not re-run) — the ceiling the exchange leaves unrecovered.

## 3. Discriminator (pre-registered)
- **MARKER-CARRIES** — marker gain ≥ 0.10 **and** its CI excludes 0 **and** M(ROLE) > M(L0): the role marker recovers a real
  chunk of the missing half → provenance is (partly) carried by the header role token, not only the imperative content.
- **MARKER-INERT** — marker-gain CI includes 0, or |gain| < 0.05: the role word does not carry the missing half either →
  the **6th** readable/manipulable feature to rank/represent the behavior without causing it.
- else **INTERMEDIATE** — report, no headline.

## 4. Gates
- **ANCHOR** — M(L0) reproduces RES-02 Arm1 within ±0.05 (RES-02 Arm1 M = **+0.462**; dY1 +3.58 at B −3.879, normal order).
  Level-vs-contrast (pre-lock): +0.462 is the raw exchange **LEVEL** (Arm1), not the netted Arm1−Arm2 = +0.422; L0
  reproduces Arm1, and L0−DISR reproduces Arm1−Arm2.
- **G-SEGMENT** (tokenizer-only, pre-lock) — **PASSED**: 720/720 usable, 0 meta/span/align failures; role-word ids exactly
  {882, 9125}; cross-role spans length-aligned; ROLE/CTRL add one matched token per block.
- **VOID** — inherited RES-02 (uncontested same-content replacement keeps ≥90% compliance).
- Counterbalance sign-folded in Y_signed; per-item ΔY, m persisted (`ext01_peritem.npz`); SMOKE(40)→FULL(720).

## 5. Scope — binding
Everything is a property of the **exchange** operation. RES-06 reached twin-patch ~0.997 where exchange got 0.462 at
identical positions; no number here is "the ceiling on role arbitration," only "under exchange." MARKER-CARRIES would name
the role-word token as a carrier component; it would not identify a mechanism. Single model; the graded/multi-marker version
is a separate cross-model probe.

## 6. Predictions (regime, not midpoint)
- ANCHOR reproduces (L0 ≈ +0.462).
- **MARKER-INERT** — predicted: the role word is another readable feature that does not carry the causal residual. Five prior
  instances (PRV-01d, PRV-01g, PRV-01h, TPL-01's two sharp cells) all came back small-or-null; base rate on "readable feature
  is causal" ≈ 0 in this program (predictions-name-a-regime-not-a-midpoint).
- CTRL ≈ L0 (a shared-header-token swap recovers nothing).
- Explicitly **against**: MARKER-CARRIES (a large role-word gain toward the twin-patch ceiling).

## 7. Cost / ops
a100-first, SMOKE(40, biased subsample — pipeline only)→FULL(720), watchdog armed pre-run, terminate in finally, ledger.
~5 forwards/item (baseline + L0 + ROLE + CTRL + DISR, each capturing the twin/source) → ~$0.5. Est ~$0.5.
