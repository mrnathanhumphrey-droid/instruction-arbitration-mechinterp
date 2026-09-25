# PREREG — PRV-01h: is the provenance INFORMATION necessary, or only the single direction?

**Locked before run. Chained to PRV-01g.** Llama-3.1-8B-Instruct, native chat flow. the reviewer spec (relayed by the lead researcher, approved).
CAUSAL probe by SUBSPACE ablation (iterative deflation). Successor to PRV-01g, which showed the single direction v̂ is not
INDIVIDUALLY necessary — the expected result under redundant coding whether or not the information is causal.

- chained_to_PRV01G_sha256: `d815b111dee33c45917848677bdacebecf6a8b55e4b4659582d3e87185ab9d5c`
- runner: `run/prv01e/prv01h.py` sha256 `6c68f1c5621224770088809796444fcd3a1ce769c6ed812b8c81ba1a5575f607`
- battery: `stimuli_tool_contested_true_false.jsonl` sha256 `49856c3da27b3da9cb6e592e94c1b12c9a333086972a4b17900a51336fa6517f` (unchanged)

## §1 Why
PRV-01g: v̂ not individually necessary. In a redundantly-coded system that is the expected result whether or not the information
is causal — one axis of ~4096 can always be spared. This program has now found redundancy at THREE levels (RES-06 Σ=2.48;
role/serialization TOOL 2×2 saturation; PRV-01g single-axis null); assume it here, don't rediscover it. **This run removes the
linearly-decodable provenance code IN FULL and asks whether the header's +2.386 nats survive.**

## §2 Method — reuse the deflation machinery
StandardScaler + LogisticRegression (C=1.0, lbfgs, max_iter=200), item-grouped train/test split, same estimator as the RES-01a
lineage / PRV-01d/g so results are comparable. On the raw contrast (H = `ipython`, U = header-substituted `user`), L1 read
position, projections applied at **all layers** across the injected-span positions (single-layer is repaired — PRV-01g's L1≈0
confirmed it). Loop:
1. Fit probe on TRAIN reps → v̂_k (raw-space weight, unit-normalized).
2. Held-out (TEST) accuracy = decodability_k.
3. Project v̂_k out of ALL reps.
4. Stop when held-out acc ≤ **0.55** (error ≥ 0.45); cap at **25**.
5. Record decodability, and (pass 2) Y(H⊥{v̂_1..v̂_k}) and mass at every k.

## §3 Controls — the run's whole validity
- **Random-rank-k control at every k.** Project out k random orthonormal directions (redrawn per item), measure Y. Removing k
  dims gets more disruptive as k grows; the comparison at each k is deflation-k vs random-rank-k, never vs k=0.
- **G-DYNAMIC-RANGE per k, checked as the loop runs.** Random-rank-k must move Y by < **0.597** nats (0.25 × 2.386, the PRV-01g
  bar — fixed for comparability). **Find and report the k at which it stops being inert** = the ceiling on interpretable depth;
  the loop must not read deflation results past it (hard break in the runner). Do NOT assume the range holds at large k because
  it held at k=1.

## §4 Metrics
- **k\*** — deflation depth at which held-out decodability reaches ≤0.55.
- **necessity(k) = [Y(H) − Y(H⊥{k})] / [Y(H) − Y(U)]**, reported as a CURVE in k with the random-rank-k floor alongside, not a
  single number. Template-cluster bootstrap CI, twin-grouped.
- Headline = necessity at **min(k\*, range-limit)**, with which bound stated explicitly.

## §5 k\* is a deflation depth, not a dimension — binding
This program already narrowed a "dimension ≥25" claim once, and [2608.10566] (*Iterative Erasure Count Is Not an Affine-Invariant
Concept Dimension*, listing-confirmed, fetch owed) is directly about this inference. **No verdict sentence may call k\* a
dimension, concept dimension, or the size of the provenance code.** Permitted: "deflation depth," "iterations to chance under this
estimator." If k\* hits the cap 25 → report as **censored at 25**, never as a value.

## §6 Gates
- **ANCHOR.** Y(U) = −3.191, Y(H) = −0.805 within ±0.15. **Level-vs-contrast (pre-lock): Y(U)/Y(H) are LEVELS; denom is a
  CONTRAST.**
- **G-DYNAMIC-RANGE per k** (§3). Hard; bounds the interpretable range.
- **G-COHERENCE.** m ≥ 0.10 at every k; the k where mass breaks is reported and bounds the readable range.
- **REPRODUCTION.** k=1 necessity must reproduce PRV-01g's 0.00932 within ±0.01, else pipeline drift → stop (no claim).
- Twin VOID, counterbalance split, per-item persistence of Y/m/decodability at every k, plus all v̂_k (basis persisted).

## §7 Outcome coding — at min(k\*, range limit), controls passing
- **necessity ≥ 0.50 → INFORMATION-NECESSARY.** The provenance code carries the resistance; PRV-01g's null was a single-axis
  artifact and redundant coding is the reason. Makes the external-monitor path well-founded; reopens subspace steering.
- **0.15 – 0.50 → PARTIALLY-NECESSARY**, report the curve.
- **< 0.15 → INFORMATION-NOT-NECESSARY.** Resistance routes around the entire linearly-decodable provenance code — carried
  non-linearly, or by something this probe family cannot see. Strong and surprising; write it as the finding.
- **Range or mass limit reached before k\* → DEPTH-LIMITED.** Report max interpretable k and necessity there as a **BOUND**, not
  a point estimate.

## §8 Scope — binding
Subspace ablation establishes necessity of the linearly-decodable code under this estimator. Says nothing about non-linear
encodings, nothing about other layers' read positions, nothing deployable. No projection is a mitigation. Single model
(Llama-3.1-8B). Do not extend across models.

## §9 Predictions — REGIME, not midpoint (new standing rule predictions-name-a-regime-not-a-midpoint)
- **INFORMATION-NECESSARY or DEPTH-LIMITED** — explicitly predicting AGAINST an intermediate value: three redundancy findings +
  a near-zero single-axis result next to a real +2.386 input effect is the distributed-coding signature, so necessity stays ~0
  until enough of the subspace is gone and then moves sharply — OR the random control breaks first.
- k\* > 1 (if it were 1, PRV-01g would already have found the effect).
- Process predictions (where our calls hold): REPRODUCTION passes at k=1; random-rank-k inertness degrades monotonically in k.

## §10 Compute / cost
720 items × [pass 1: 2 forwards] + [pass 2: 2 forwards × k-sweep to min(k\*,25)] + CPU deflation (≤25 LR fits). Est ~$0.60,
a100/a10, WD_FULL=5400 (sweep may reach k=25), watchdog armed before run, SMOKE→FULL, terminate in finally, ledger. (SMOKE
ANCHOR-FAILs on the 40-item subsample as in 01d/f/g; FULL is the real check.)

## §11 User additions
(none)
