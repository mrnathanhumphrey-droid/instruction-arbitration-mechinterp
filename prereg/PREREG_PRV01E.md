# PREREG — PRV-01e: does role-header provenance propagate downstream of the header?

**Locked before run. Chained to PRV-01c-r2 (VOID).** Llama-3.1-8B-Instruct, NON-CAUSAL representation probe. New contrast
(not a revision of r2). the reviewer spec.

- chained_to_PRV01C_R2_sha256: `2f58285c622a0aac35f06c56d3067cd34fdc57aea4380b15fe0d74863ff529f3`
- runner: `run/prv01e/prv01e.py` sha256 `cfb6c7d36df406da0ecfb5aff7499b50d83af175e94f189f5d29af3da3780dc8`
- battery: `run/prv01e/stimuli_prv01e.jsonl` sha256 `d7d271051dfa4d4a6eef4837641561ec20fa411951b736cc4d7872dcd6ba4250` (300 synthetic neutral paragraphs, all ≥64 content tokens, quote/imperative/readout-free)
- FORWARD ONLY; §8 scope binding (recoverable ≠ used; no causal verb).

## §1 Why the contrast changed
PRV-01c/r2 fit tool-vs-user where the arms differ in header, wrapper, and turn structure at once; the probe learns the
wrapper (r2 G0b saturation 32/33). The fix: remove every surface difference except the one whose propagation is in question —
the role header.

## §2 Arms — two, byte-identical except the role header (verified)
- **A (genuine):** content in the native `tool` role, payload `{"output": "<content>"}` via tojson.
- **B (perfect forgery):** the EXACT same payload token sequence in a `user` turn (user content = `json.dumps({"output": content})`).
- **G-CONSTRUCT (hard, tokenizer-only, done before spend):** tokens from the content-block header-end to end-of-prompt are
  IDENTICAL A vs B — **verified 300/300**; header length differs by **k=1** (`ipython` vs `user`). Post-header identity means
  the arms' only difference is the header tokens — exactly what a real forgery cannot copy. Drop threshold >2% → would VOID
  before launch; 0 dropped.

## §3 Battery
300 synthetic neutral paragraphs (5 declarative sentences, distinct subjects, no subject-set reuse across items → grouped-CV
clean), 64–71 content tokens (median 65), all ≥64 so d=64 reads exist. Quote-free (JSON embedding), imperative-free,
readout-free.

## §4 Read positions — a curve, not a point
d ∈ {1, 4, 8, 16, 32, 64} downstream from the content-block header-end, clipped per item (all 300 support all d; verified).
By G-CONSTRUCT the token ids at every d ≥ 1 are identical A vs B → **L0 must be at chance by construction** (G0 has real teeth).

## §5 Probe
StandardScaler + LogisticRegression(C=1.0, lbfgs). Binary A-vs-B, 5-fold grouped by content item, fold-internal. Full
accuracy SURFACE (layer × d) persisted.

## §6 Gates
- **G0 EMBEDDING-CHANCE:** L0 balanced acc ≤ 0.55 at every d ≥ 1 (tokens identical there). Above → G-CONSTRUCT lied / indexing
  off → VOID + debug.
- **G-POSITION (pad-swap counterbalance):** header lengths differ by k=1. Run both pad assignments — k pad tokens in A's
  preceding region (surface padA = A_pad vs B_nat) vs in B's (surface padB = A_nat vs B_pad) — and require the full accuracy
  surfaces to agree within 0.05. Disagreement → position proxy → VOID. (This replaces r2's mis-specified G6, which tested
  whether the probe can see pad text; this tests whether it can see position.)
- **G-SHUFFLE:** label-permuted null within folds → 0.50 ± 0.08. Outside → CV leak → VOID.
- **G-VALIDITY:** acc at d=1 (adjacent to header) ≥ 0.80. Below → estimator broken → VOID.
- No G0b: saturation across the stack would now be a FINDING (perfect propagation), not a confound — no surface difference
  left to launder.

## §7 Outcome coding (curve vs d at the peak layer, all gates passed)
- **PROPAGATED:** acc > 0.70 at d ≥ 32. Provenance survives a perfect payload forgery downstream; PRV-01d becomes well-posed.
- **DECAYING:** falls between the bars; headline = the half-distance (d where acc reaches the midpoint between d=1 and chance).
- **LOCAL:** acc ≤ 0.60 by d = 16. Provenance does not leave the header region → mechanistically explains SPOOF-01's marker
  inertness and makes PRV-01d unnecessary (no downstream direction to patch). LOCAL is a null and the strongest available
  result — written as a finding, not a failure.

## §8 Scope (binding)
Decodability ≠ use. No "uses/checks/relies on/ignores." Permitted: "recoverable at depth d," "propagates to," "not
recoverable above chance beyond d." **PRV-01d is CONDITIONAL on PROPAGATED or DECAYING**, patch site = the (layer, d) cell
this run identifies; not specced until then.

## §9 Predictions recorded before launch
- G-CONSTRUCT passes >98% (done: 300/300).
- G0 at chance (≤0.55) at all d ≥ 1.
- d=1 accuracy > 0.95.
- DECAYING or LOCAL, half-distance under 16 tokens.
- If LOCAL: lines up with SPOOF-01 and ASIDE's premise that vanilla instruction-tuned models don't maintain channel separation.

## §10 Compute / cost
2 (×2 pad) arms × 300 × short forward w/ output_hidden_states = 1,200 forwards + CPU probe surfaces. Est ≤ $0.40, a100-first
(a10 ok). Watchdog armed; SMOKE then FULL; terminate in finally; ledger. Llama-only, internal rep — no deployed claim moves.

## §11 User additions
(none)
