# Instruction–Arbitration Mechanistic Interpretability

A pre-registered mechanistic-interpretability program on **how an instruction-tuned language model decides which
instruction to obey when instructions conflict** — the mechanism underneath prompt injection and the "instruction
hierarchy." It runs two joined threads:

1. **Internally**, in a single model, *where and how* does the arbitration happen — is the role an instruction came from
   (its "provenance") represented, and is that representation what actually drives which instruction wins?
2. **Externally**, across models, does that mechanism surface in the **chat template a vendor ships** — well enough that you
   could inspect a template and rank a model's injection resistance before deploying it?

The program probes, empirically and causally, the separation of *instructions* from *data* — the setting of the
impossibility results in [*On the Inseparability of Instructions and Data in Shared-Embedding Sequence
Models*](https://arxiv.org/abs/2606.27567) (Assumption 3 / Theorem 3: provenance-recovery is impossible under
distributional overlap).

Model scope: **Llama-3.1-8B-Instruct** (bf16) for the internal causal program; the tool-template arm (TOOL-02/03, TPL-01)
spans six open-weight families — Llama-3.1, Qwen2.5, Mistral-v0.3, Mistral-Nemo, Gemma-2, Phi-3.5.

> **Status: active, living record.** Every probe is pre-registered and sha256-locked *before* the model is run; the verdict
> is written after, its mechanical result computed from the locked criteria and its interpretation a separate, labeled step.
> Findings — and their corrections — are updated as the program continues. The current throughline: *a readable structural
> feature that correlates with the arbitration is not the same as the thing that causes it.* Released for reproducibility and
> the public good.

## Method

- **Pre-registration + hash chain.** Each probe has a `PREREG_*.md` whose sha256 is committed (`*.sha256`) *before* the
  run, chained to the previous probe's hash. Thresholds and readings are fixed in advance; the mechanical verdict follows
  from the locked criteria; the reading is separate and labeled.
- **Readout.** `Y = logP(POS) − logP(NEG)` at the first assistant token, signed by which role holds the target
  (`+Y` = obeys the system slot). The internal program uses a DONE/READY readout; the cross-model tool arm uses TRUE/FALSE.
  A per-cell probability-mass gate guards against reading logprobs off a collapsed distribution.
- **Causal mediation (internal).** The estimand is `M = −ΔY / (2·B)`; interventions overwrite residual-stream activations
  at chosen spans/layers (exchange, twin-patch, subspace ablation, INLP deflation) and measure the behavioral change.
- **Resistance measurement (cross-model).** The tool arm contrasts an instruction injected in a model's **native tool
  template** against the same bytes as plain user text (the resistance "anchor"), then **transplants the serialization
  between templates while holding the host's role slot fixed** to ask whether the effect travels with the template or the
  model. Ordering agreement across hosts is scored with **Kendall's W**.
- **Uncertainty.** Template-cluster bootstrap (the template is the unit of independence); paired where the contrast is
  within-item.
- **Controls the program insists on.** A same-condition floor for every treatment; a VOID guard (a patch that lobotomizes
  the model cannot be read as a null); a dynamic-range guard (a random intervention of matched size must be inert before a
  targeted one is read); an estimator calibration against hand-built ground truth (CAL-01); an operation-coherence check
  (DIST-01); and a denominator / order-counterbalance check (ORD-01).

## The findings, honestly

### The internal mechanism (Llama-3.1-8B)

- **Provenance is richly represented.** Which role an instruction came from is decodable from the residual stream at high
  accuracy (~95%), non-linearly, and independently of token position (RES-01).
- **…but the readable provenance code is a *correlate*, not the causal carrier (PRV-01d/f/g/h/h-r).** Ablating the decodable
  code does not remove the resistance. No single read direction is individually necessary (PRV-01g); iterative deflation
  drives decodability down to its stopping bar while resistance stays intact, and this **existential dissociation is robust
  across two independent whitening geometries** (PRV-01h-r), with the removed subspace's necessity zero-to-slightly-negative.
  Stated carefully — the removed subspace is procedure-relative, not a "dimension" ([arXiv 2608.10566](https://arxiv.org/abs/2608.10566)) —
  *decodability and causal role come apart.* And at the input level the role marker and the serialization are **redundant**
  "this-is-data" signals: either alone suffices, and once serialization marks content as data the role header adds nothing.
- **Attention is not the carrier at the readout row, under pattern-swap (PRV-04c).** Swapping the generation-position
  (readout-row) block-attention of role-tracking heads toward the counterfactual twin — including **all 110 testable tracking
  heads co-swapped at once, across all layers**, at matched per-head magnitude — moves the arbitration by only −0.026 nats
  against a 0.20 bar. That is a *bounded* null (co-ablated, so not a self-repair false null), but two qualifiers are
  load-bearing: it is the **readout row** and a **pattern-swap** operator. **Attention at non-generation positions (e.g. the
  instruction span) is untested and remains a live candidate locus** — RES-02/06 covered the *residual* there, not attention.
- **Representation is position-independent; behavior is position-dominated (RES-01b, ORD-01).** A cross-role exchange never
  isolated provenance — it rides recency (see *Corrections* below). The cleanest surviving pairing is stated without any
  ratio: what the model *represents* about role is not what *drives* its choice.
- **The behavioral effect is distributed, not localized** to any single site under provenance-preserving operations
  (RES-05, RES-06); the estimator is unbiased on a known-ground-truth toy (CAL-01) and the exchange operation is coherent
  (the model accepts the edited state rather than rejecting it — DIST-01).
- **The "half" was our instrument, not a missing account (OPX-01).** RES-02's cross-role *exchange* recovers ~0.46; but
  patching each span one-sided and same-index, the two spans sum to **M ≈ 0.97** (additivity gap +0.032). The material is all
  in the spans — the two-sided cross-index exchange simply under-reads it — so the RES-02 "≈half" is an **operator deficit**,
  re-scoped to "under exchange." The finding is the **component signs**: flipping only the system span moves *away* from the
  target (**−0.93**), flipping only the user span *overshoots* (**+1.90**). That is competition with renormalization — the two
  blocks contend for a bounded allocation — not a plain additive readout, and it is the attention-mass framing with numbers.
  (Narrow: this rules out interaction *in the difference measure at these spans*, not that the computation is
  non-interactional; whether the renormalization is recency- or role-bound is open.)
- **Recency and role dissociate — the "recency-dominant" story splits in two (OPX-02).** Re-running the one-sided flips under
  reversed block order (system last): the **baseline flips sign** (obeys whichever block is last — recency-dominant, as ORD-01
  found), but the **span-flip asymmetry keeps its signs with the roles** — the **user** span is the dominant lever and the
  **system** span the weak/counteracting one in *both* orders (recency-swap rejected by ~27 nats). So the default tilt is
  recency while the per-span causal weighting stays with the **block** (user-block > system-block): OPX-01's competition is
  block-anchored, not position-anchored. Position still modulates the *magnitude* (~5 nats on reversal), not the structure. The
  program had these two fused; they are distinct. (**Scope correction, forced by OPX-03:** block-order reversal moves a block's
  *body* along with its *label*, so this cannot isolate the label — "block-anchored" means label-and-body-together. OPX-03 below
  shows the label itself carries ≈0 of the asymmetry, so the carrier is the block's *content*, not the role word.)
- **The carrier is not the role word and not the preamble — 94% survives both (OPX-03).** Attributing the OPX-01/02 asymmetry to
  named textual features: neutralizing the role-word marker (`system`/`user` → `info`) removes **~0%** (share +0.09 nats, CI
  includes 0), and additionally stripping Llama's system-only date preamble removes **~6%**. **94% of the asymmetry survives**
  even when the two blocks are token-identical apart from order (which OPX-02 already ruled out). Per a pre-committed
  construction check, survival is **enumeration-incomplete**, not evidence of a "slot prior": an unlisted feature carries it, the
  leading candidate being the **block body/filler content** (never matched — step zero matched only the imperative spans). A
  methodology note is attached to the verdict: neutralizing the markers drives the normalization baseline toward zero, so the
  analysis is on raw ΔY, not the normalized effect. This is the third straight mechanistic prediction (exchange-operator,
  recency, marker) to miss — each miss narrowing the carrier toward block content.
- **It isn't the filler either (OPX-04).** Testing the block body/filler content directly — a *swap* design (matching can only
  collapse; swapping *inverts*, and inversion is the one signature no other cause produces): swapping the two blocks' fillers does
  not invert or shrink the asymmetry (ratio +1.06), matching them does not collapse it, and removing them entirely does not either
  (STRIP 116%). Verdict **BODY-NULL** — the filler carries none of it. A pre-registered filler-length correlation check comes back
  null, so the (accepted, unmatched) filler lengths do not explain the result. Fourth straight prediction miss.
- **The carrier is outside the lexical enumeration — 90% survives the joint strip (OPX-05).** The decisive construction check:
  remove the marker, the preamble, *and* the filler **simultaneously**, so the two blocks are token-identical apart from order and
  a counterbalanced target word. If the earlier single-feature survivals had been a *redundant lexical code* (any one of several
  features sufficient), the joint strip would collapse it. Instead **90% survives** (ratio 0.90 [0.84, 0.96]) — and the run
  reproduces OPX-03's PM (94%) and OPX-04's STRIP (116%) in-run, two figures that could have failed independently. A free
  counterbalance-split re-analysis rules out the remaining lexical suspect, the **target word**: the asymmetry is the same sign and
  magnitude in both counterbalance halves (identical under the joint strip), so it is not a target effect wearing a role label. The
  carrier is therefore **not lexical** — no word or wrapper carries it (stated precisely: outside the lexical enumeration, *not*
  "non-textual" — position is realized through token index, which the text still determines). What remains is block **order /
  position**, which OPX-02 constrained (reversal kept the signs) and which the next probe — the joint strip under reversed order —
  is built to resolve. Fifth straight miss, and the sharpest result: one construction check ruled out the entire lexical
  enumeration at once.

### At the real injection surface, across models

- **Indirect injection via a tool result still wins — and JSON-rendering it does not help (TOOL-01).** Where injection
  actually lives (an untrusted instruction in a tool/`ipython` result, arriving *last*), the model obeys the injected
  instruction on net (raw ΔY excludes zero in every layout). The tool role blunts the effect by ~2.5 nats versus the same
  instruction in a user turn — a genuine *role* effect, not a distance artifact (identical readout distance in both arms,
  delta 0.000 tokens over 720 items) — but that blunting is carried by the tool **role header**, not by Llama's `tojson`
  rendering, which is behaviorally **inert** (CI includes zero, point estimate the wrong sign). The "privilege bit" does not
  protect you; the only mitigation is a partial, role-header blunting that injection still overcomes.
- **Chat-template design maps to injection resistance — heterogeneously and with a sign (TOOL-02, TOOL-03).** Ported across
  three families, the tool-role effect is not a shared "tool distrust": **Llama +3.23 nats (resists), Qwen +1.19 (resists),
  Mistral-v0.3 −6.82 (amplifies)** — a ~10-nat signed spread. Mistral-v0.3's `[TOOL_RESULTS]` template makes an injected
  instruction *more* obeyed than the same text in a user turn, and TOOL-03 isolates the cause to the template **markers**
  themselves (a pure commitment / tool-call turn is inert, ≈0), not the agent-loop flow. This is a property of the template a
  vendor ships, and it is inspectable before deployment.
- **Can you rank a model's injection resistance by reading its template? The extreme, not the fine order — and partly by
  length (TPL-01).** A prospective, six-model test transplants each serialization between templates while holding the host's
  role slot. Across the three tool-role hosts the robust, CI-backed result is the **extreme contrast**: `<tool_response>`-style
  tags resist more than Mistral's `[TOOL_RESULTS]` in every host (paired differences +0.6 to +1.0 nats, all excluding zero).
  The full strict 3-way order (Kendall's *W* = 1.000 on the point estimates) is **not** individually resolved per host — one
  adjacent pair is CI-ambiguous in two of the three hosts — and the ordering **correlates with wrapper token length**
  (Spearman +0.5: `[TOOL_RESULTS]` is both the longest wrapper and the worst-resisting), so a semantic template property
  cannot be cleanly separated from a length effect. Length is not the whole story (`<tool_response>` wrappers are longer than
  Llama's `{"output":…}` yet resist more), but the honest claim is "the extremes order consistently," not "the template's
  semantics fix a full ranking." The **magnitude** is model-bound regardless: swapping the serialization moves each host
  <1 nat against a ~6.5-nat between-model gap, and neither pre-committed sharp cell moved — transplanting Mistral's
  serialization into Llama does *not* drag Llama toward Mistral's level. The resistance lives in the model / native
  role-slot, not the transplantable wrapper. (Separately: forcing a foreign serialization into Mistral's tool slot makes it
  stop answering — an availability effect, not a resistance gain.)

### The throughline

Repeatedly, at several levels, a **readable structural feature that correlates with the arbitration turns out to be, at
most, a minority of what carries it.** Internally, role provenance is decodable at 95% yet ablating it leaves resistance
intact. Across models, the serialization predicts the *coarse order* of injection-following (the extremes, and partly by
wrapper length) yet transplanting it moves almost none of the *magnitude*. And when we gave the readable feature its best
shot — directly swapping the role-word marker token in the residual, not just reading it (EXT-01) — it carried a **real but
small** slice: ~13% of what a content-flip recovers, specific to the role lexeme, with the other ~87% still elsewhere. The
honest actionable statement is narrower than "inspect the feature and you understand the behavior": the readable signal
mostly ranks rather than causes, its causal slice where it has one is minor, and the large effects live in the model and its
native template — including one template (Mistral-v0.3's `[TOOL_RESULTS]`) that measurably amplifies injection.

**A second throughline, cutting the other way (OPX-01/02).** The runs above are about a readable feature *not* carrying the
behavior; the exchange-operator work is the counterweight, and it is not a footnote. When the operator artifact is removed,
the causal structure at the imperative spans is **legible, modular, and additive**: the two spans additively determine the
answer (gap +0.03), with a **fixed role weighting** — the user span dominant, the system span weak — that stays with the roles
under block reversal, on a recency-tilted baseline (the same 71/29 recency/role split as ORD-01). So the same system that hides
its causal carrier behind readable *correlates* in one place exposes a clean, separable, role-weighted mechanism in another.
Both are true of it. Where the *arbitration's* bulk carrier lives remains open — a candidate is attention at non-generation
positions (the instruction span), untested.

### Corrections on the record

- **ORD-01 (rescope).** The baseline in this benign contest is **recency-dominant**: flipping the order of the role blocks
  flips the baseline's sign (~71% recency, ~29% role). Because every `M` divides by that baseline, the single-number "the
  arbitration is ~half provenance-movable" headline was **retracted pending re-expression**. Qualitative results unaffected;
  the quantitative fraction re-expressed. Exactly the confound the pre-registration + control discipline exists to catch —
  `verdicts/VERDICT_ORD01.md`.
- **RE-01 (re-expression).** Normalized `M` is retired as the primary quantity in favor of **raw ΔY in nats, order-tagged,
  baseline reported per order**. Cross-role *exchange* moves +3.58 nats at normal order — more than the whole role budget
  (2·|role| = 2.24) and 5× more than at flipped order — so it rides recency, not role. Exchange (a recency-signature swap)
  and twin-patch (a content flip) are different counterfactuals, so the "half provenance / half content" split loses its
  premise, not just its denominator — `verdicts/RE01_reexpression.md`.

## Repository layout

```
prereg/     PREREG_*.md + PREREG_*.md.sha256   — pre-registrations and their locked hashes (chained)
runners/    *_lambda.py, *_toy.py, watchdog.py — the experiment code (GPU/CPU runners; cloud launchers are not published)
verdicts/   VERDICT_*.md                        — the written verdict for each probe (facts; reading labeled separately)
results/    <probe>/*.json, *.csv              — the numeric results the verdicts are computed from
data/       make_*stimuli*.py, stimuli_*.jsonl — the constructed batteries
```

Probes, roughly in order: `PRV-01…04` (is provenance recoverable / used / routed) · `MMD-01` (reproduction of a prior
separability measurement) · `H4`, `RDV-01`, `KDR-01` (distributed mediation and re-derivation) · `ATT-01` (attention
observation) · `RES-01…06` (representation, causal ceiling, extent, decomposition) · `CAL-01` (estimator calibration) ·
`DIST-01` (operation coherence) · `ORD-01` (denominator / order-counterbalance) · `TOOL-01` (system-vs-tool contest:
recency vs the `tojson` privilege bit) · `FREE-01`/`AUTH-01`/`SPOOF-01` (authority and spoofed-role contests) ·
`READOUT-01` (forced-readout method check) · `TOOL-02`/`TOOL-03` (cross-model tool-template resistance; template markers vs
agent-loop flow) · `PRV-01d…h-r` (is the decodable provenance code the causal carrier — pathway, necessity, subspace
ablation, reparameterization robustness) · `TPL-01` (prospective: can you rank injection resistance by reading the template)
· `EXT-01` (does swapping the role-word marker token carry RES-02's residual "missing half" — a real but minor slice) ·
`OPX-01` (why does exchange extract 0.46 where the spans additively carry ~0.97 — operator deficit + a competition/renorm sign
structure) · `OPX-02` (does that asymmetry follow recency or the block — the block, and block-vs-recency dissociate) ·
`OPX-03` (which textual feature carries it — not the role-word marker (~0%) and not the preamble (~6%); 94% survives, carrier
still unenumerated, pointing at block content) · `OPX-04` (does the block filler carry it — swap/match/strip: BODY-NULL, it does
not) · `OPX-05` (the joint strip — remove marker+preamble+filler at once: 90% survives, plus a counterbalance split ruling out the
target word, so the carrier is outside the lexical enumeration; next is the joint strip under reversed order).

## Reproducing

- Runners target the model IDs named as constants at the top of each file, via `transformers`; set `HF_TOKEN` in the
  environment. Runners expect the stimuli from `data/` alongside them. The cloud launchers that provisioned GPUs and placed
  files are intentionally omitted — they are infrastructure, not method.
- `data/make_stimuli.py` generates the contested/uncontested battery (`stimuli_contested.jsonl` /
  `stimuli_uncontested.jsonl`). `data/make_tool_stimuli.py` generates the system-vs-tool battery for TOOL-01
  (`stimuli_tool_contested.jsonl`). `data/make_tool_stimuli_cross.py` generates the cross-model TRUE/FALSE tool battery
  (`stimuli_tool_contested_true_false.jsonl`) used by TOOL-02/03 and TPL-01.
- The tool-template runners (`tool02_lambda.py`, `tool03_lambda.py`, `tpl01_phase23.py`) load six model families
  sequentially; the model IDs are constants at the top of each runner, and `HF_TOKEN` gates the download.
- Verdicts quote the run that produced them; results JSON/CSV carry the numbers and confidence intervals. A public prereg's
  `.md` is a scrubbed rendering; its `.sha256` sidecar is the hash of the original locked file (so the sidecar, not the
  rendered `.md`, is the tamper-evident lock).

## Scope and caveats

- **One model for the internal causal program; six families for the tool-template arm.** The residual-stream causal work
  (RES/PRV/ORD/H4/etc.) is Llama-3.1-8B-Instruct on a two-token DONE/READY readout over a constructed imperative battery.
  The tool-template findings (TOOL-02/03, TPL-01) span Llama-3.1, Qwen2.5, Mistral-v0.3, Mistral-Nemo, Gemma-2, Phi-3.5 on a
  TRUE/FALSE readout. Within-family pairs (Nemo↔Mistral-v0.3) are reproducibility checks, **not** out-of-sample
  discriminative ranking tests; the prospective evidence is the within-model serialization swap (TPL-01).
- **Synthetic battery, log-probability readout.** Results are on a constructed imperative battery read at the first
  assistant token, not on free-form agentic traces. No serialization swap is a deployment configuration.
- **The internal baseline is recency-confounded** (ORD-01); treat any "fraction of the arbitration" statement as under
  re-expression.
- **Living record.** Findings, and their corrections, are updated as the program continues.

## License

MIT — see `LICENSE`.
