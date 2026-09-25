# PREREG — PRV-01h-r: does PRV-01h's existential result survive reparameterization?

**Locked before run. Chained to PRV-01h.** Llama-3.1-8B-Instruct. the reviewer spec (relayed by the lead researcher, approved). ROBUSTNESS SWEEP, not
a new question: run the deflation loop under three parameterizations and test whether the existential (necessity ~0 with
decodability reduced/killed) generalizes, or diverges (an empirical instance of 2608.10566's non-invariance on our data).

- chained_to_PRV01H_sha256: `fdd4b552c3be0bfb1da50e46773ed4d27b58d25cbb703181a9a493993f2ef075`
- runner: `run/prv01e/prv01hr.py` sha256 `76ac0838465e47a7b4b5d7810068823ae26dff5581fce7229e45d9a7f1a63a8b` (re-locked 2026-09-24 after a SMOKE-caught tuple-unpack bug on the Y(H) pass-1 call; fix folded the redundant extra H forward into the hidden-state call; NO design/prediction change, no results existed. Prior sha `897636c1…`.)
- battery: `stimuli_tool_contested_true_false.jsonl` sha256 `49856c3da27b3da9cb6e592e94c1b12c9a333086972a4b17900a51336fa6517f` (unchanged)

## §1 Why
2608.10566: the stopping count and cumulative removed rank change under an information-preserving invertible reparameterization,
so what PRV-01h removed is procedure-relative in *content*, not only *size*. PRV-01h ran one parameterization (StandardScaler +
Euclidean projection). If necessity stays ~0 across several defensible parameterizations, the **existential** generalizes
empirically without an invariance theorem; if it diverges, the paper's concern is operative here — itself a reportable result.

## §2 Parameterizations (each: fit → project → refit; stop at held-out acc ≤ 0.55; **cap 40** — raised from 25 so decodability
can actually reach chance, since PRV-01h censored at 25 @ 0.579)
- **P1** — StandardScaler + Euclidean projection in raw coords. **EXACTLY PRV-01h. Reproduction arm.**
- **P2** — no scaler, raw residual coordinates, Euclidean projection.
- **P3** — ZCA whitening on the residual covariance (train-items only, fold-internal, +1e-3 ridge), deflate + project in whitened
  coordinates, mapped back before the forward pass. Causal removal in raw coords = `Winv·U·Uᵀ·W·(h−μ)`; verified pre-lock that
  this equals projecting U out in whitened space (`W(h'−μ) = (I−UUᵀ)W(h−μ)`, exact).

## §3 Measurements (per parameterization)
- **k\*_P** — stopping count (censored at 40 if decodability never ≤0.55). PROCEDURE-DEFINED depth, never a dimension.
- **necessity_P = [Y(H) − Y(H⊥{k\*_P})] / [Y(H) − Y(U)]**, causal forward pass at the stopping point, random-rank control at the
  **matched rank** k\*_P (per item). (P1 also measured at k=25 for the reproduction gate.) Bootstrap CI, twin-grouped.
- **Subspace overlap** — principal angles (full spectrum, deg) between the raw-coords removed subspaces: P1↔P2, P1↔P3, P2↔P3.
  Directly measures whether the non-invariance bites here or is merely theoretical.

## §4 Gates
- **REPRODUCTION.** P1 necessity at k=25 reproduces PRV-01h's −0.07345 within ±0.02, else pipeline drift → stop. (P1 uses
  identical seed/split/estimator/CAP_POS to PRV-01h; row-order of pooled reps differs but the fit is order-invariant.)
- **G-DECODABILITY-KILLED (per P, the premise).** At the stopping point, held-out channel acc ≤ 0.55. If still readable
  (censored at cap), nothing about "removing the code" was achieved in that P; its necessity is reported but the P is not counted
  toward ROBUST-EXISTENTIAL. (This was assumed, not gated, in PRV-01h — now explicit.)
- **G-DYNAMIC-RANGE (per P, at matched rank).** Random-rank control moves Y < 0.597 nats; failing P excluded, never averaged.
- **G-COHERENCE.** mass ≥ 0.10 at the measured arm of every P.
- **ANCHOR.** Y(U)=−3.191, Y(H)=−0.805 within ±0.15 (levels; denom is a contrast). Twin VOID, counterbalance split, per-item
  persistence of Y/m/decodability + all removed bases for every P.

## §5 Outcome coding
- **necessity <0.15 in all three AND decodability killed in all three AND controls pass → ROBUST-EXISTENTIAL.** Strongest form
  without an invariance theorem: destroying linear decodability leaves resistance intact across three geometries.
- **necessity differs materially (>0.15 spread) across valid parameterizations → PARAMETERIZATION-DEPENDENT.** State per-P; the
  divergence is a finding — an empirical instance of 2608.10566.
- **no P reaches chance by cap 40 → DECODABILITY-NOT-KILLED.** The clean existential-with-kill is not establishable this way;
  report per-P decodability floors (still shows necessity ~0 at the reduced-decodability point, the PRV-01h-level claim).
- **mixed gate failures → MIXED**, per-P, no pooled headline.

## §6 Scope — binding
Three parameterizations is not invariance. ROBUST-EXISTENTIAL licenses "across the geometries tested," never "the
linearly-decodable code." The universal claim stays unavailable regardless of outcome. `k\*_P` are **deflation depths, never
dimensions**, in every arm of the write-up (standing rule, ref-erasure-count-not-a-dimension). No projection is a mitigation.
Single model (Llama-3.1-8B). Do not extend across models.

## §7 Predictions — regime, not midpoint
- k\*_P differ across parameterizations (the paper says they can; this shows whether they do here).
- Principal angles: substantial overlap P1↔P3, less P1↔P2.
- **ROBUST-EXISTENTIAL** — necessity ~0 in all three (decodability/causality split more likely real than a geometry artifact).
- Explicitly predicted AGAINST: an intermediate necessity value in any arm. (Process predictions have held; magnitude has not —
  recorded weight.)

## §8 Compute / cost
720 items; pass 1 (3 fwd/item) + 3 deflation loops (≤40 LR fits each, CPU) + necessity forwards at k\*_P (+k=25 for P1). Est
~$1.0–1.5 (CPU-fit-bound), a100/a10, WD_FULL=7200, watchdog armed before run, SMOKE→FULL, terminate in finally, ledger. SMOKE
caps deflation at 6 and ANCHOR-FAILs on the 40-item subsample; FULL is the real check.

## §9 User additions
(none)
