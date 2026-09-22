# Instruction–Arbitration Mechanistic Interpretability

A pre-registered mechanistic-interpretability program studying **how an instruction-tuned language model decides which
instruction to obey when a system-role instruction and a user-role instruction conflict** — the mechanism underneath
prompt injection and the "instruction hierarchy."

Model under study: **Llama-3.1-8B-Instruct** (bf16). The program probes, empirically and causally, the separation of
*instructions* from *data* — the setting of the impossibility results in
[*On the Inseparability of Instructions and Data in Shared-Embedding Sequence Models*](https://arxiv.org/abs/2606.27567)
(Assumption 3 / Theorem 3: provenance-recovery is impossible under distributional overlap).

> **Status: active, living record.** Every probe is pre-registered and sha256-locked *before* the model is run; verdicts
> are written after. Findings are updated as the program continues — including corrections. The most recent correction
> (**ORD-01**) rescoped a quantitative headline; see *Current status* below. This repository is released for
> reproducibility and public good.

## Method

- **Pre-registration + hash chain.** Each probe has a `PREREG_*.md` whose sha256 is committed (`*.sha256`) *before* the
  run, chained to the previous probe's hash. Thresholds and readings are fixed in advance; the mechanical verdict is
  computed from the locked criteria, and the interpretation is a separate, labeled step.
- **Causal mediation by activation patching.** The core estimand is `M = −ΔY / (2·B)`, where `Y = logP(DONE) − logP(READY)`
  at the first assistant token (signed by which role holds the target), and `B` is the baseline effect. Interventions
  overwrite residual-stream activations at chosen token spans / layers and measure the behavioral change.
- **Uncertainty.** Template-cluster bootstrap (the template is the unit of independence); paired where the contrast is
  within-item.
- **Controls the program insists on.** A same-condition floor for every treatment; a VOID guard (a patch that lobotomizes
  the model cannot be read as a null); an estimator calibration against hand-built ground truth (CAL-01); an
  operation-coherence check (DIST-01); and a denominator check (ORD-01).

## The findings, honestly

**What stands:**

- **Provenance is richly represented.** Which role an instruction came from is decodable from the residual stream at high
  accuracy (~95%), non-linearly, and independently of token position (RES-01).
- **Per-head attention is not the causal router.** Patching individual role-tracking attention heads does not move the
  arbitration (PRV-04c). *Caveat:* this was measured one head at a time, the regime where self-repair / backup heads can
  manufacture a false null; a co-ablation retest is planned.
- **A residual exchange moves a large, specific fraction of behavior;** a counterfactual "twin" patch (which flips the
  literal instruction text) moves essentially all of it (RES-02, RES-06).
- **The effect is distributed, not localized** to any single site (markers, readout, intermediate content) under
  provenance-preserving operations (RES-05, RES-06).
- **The estimator is unbiased** on a hand-built toy with known ground truth (CAL-01), and **the exchange operation is
  coherent** — the model accepts the edited state rather than rejecting it (DIST-01).

**What is currently rescoped (ORD-01):**

- The model's baseline preference in this benign contest is **recency-dominant**: flipping the order of the role blocks
  flips the sign of the baseline (the model largely obeys the *last* block), so **~71%** of the baseline is recency and
  **~29%** is role. Because every `M` divides by that baseline, **the single-number "the arbitration is ~half
  provenance-movable, ~half content-bound" headline is retracted pending re-expression** (order-resolved `M` and raw ΔY).
  The *qualitative* results above are unaffected; the *quantitative fraction* is being re-expressed. This is exactly the
  kind of confound the pre-registration + control discipline exists to catch — see `verdicts/VERDICT_ORD01.md`.

**Re-expression (RE-01).** The program now retires *normalized* `M` as its primary quantity in favor of **raw ΔY in nats,
order-tagged, with the baseline reported per order**. The re-expression also shows cross-role *exchange* never isolated
provenance: it moves +3.58 nats at normal order — more than the whole role budget (2·|role| = 2.24 nats) and 5× more than
at flipped order — so it rides the recency channel, not role. Exchange (a context/recency-signature swap) and twin-patch
(a content flip) are *different counterfactuals*, so the earlier "half provenance / half content" split loses its premise,
not just its denominator. The cleanest surviving result is a pairing: **the representation is position-independent
(RES-01b) while the behavior is position-dominated (ORD-01)** — representation ≠ causation, stated without any ratio. See
`verdicts/RE01_reexpression.md`.

## Repository layout

```
prereg/     PREREG_*.md + PREREG_*.md.sha256   — pre-registrations and their locked hashes (chained)
runners/    *_lambda.py, *_toy.py, watchdog.py — the experiment code (GPU/CPU runners; cloud launchers are not published)
verdicts/   VERDICT_*.md                        — the written verdict for each probe (facts; reading labeled separately)
results/    <probe>/*.json, *.csv              — the numeric results the verdicts are computed from
data/       make_stimuli.py, stimuli_*.jsonl   — the constructed contested/uncontested battery
```

Probes, roughly in order: `PRV-01…04` (is provenance recoverable / used / routed) · `MMD-01` (reproduction of a prior
separability measurement) · `H4`, `RDV-01`, `KDR-01` (distributed mediation and re-derivation) · `ATT-01` (attention
observation) · `RES-01…06` (representation, causal ceiling, extent, decomposition) · `CAL-01` (estimator calibration) ·
`DIST-01` (operation coherence) · `ORD-01` (denominator / order-counterbalance).

## Reproducing

- The runners target Llama-3.1-8B-Instruct via `transformers`; set `HF_TOKEN` in the environment. `MODEL_ID` and layer
  ranges are constants at the top of each runner. Runners expect the stimuli from `data/` alongside them (the cloud
  launchers that placed files and provisioned GPUs are intentionally omitted — they are infrastructure, not method).
- `data/make_stimuli.py` generates the contested/uncontested battery; the exact battery used is included as
  `stimuli_contested.jsonl` / `stimuli_uncontested.jsonl`.
- Verdicts quote the run that produced them; results JSON/CSV carry the numbers and confidence intervals.

## Scope and caveats

- **Single model, single readout, synthetic battery.** All results are Llama-3.1-8B-Instruct on a two-token
  (DONE/READY) log-probability readout over a constructed imperative battery. Cross-model and cross-role (tool/data
  slot) replication are open.
- **The baseline is recency-confounded** (ORD-01) — see above; treat any "fraction of the arbitration" statement as under
  re-expression.
- **Living record.** Findings, and their corrections, are updated as the program continues.

## License

MIT — see `LICENSE`.
