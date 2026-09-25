# VERDICT — PRV-01h: INFORMATION-NOT-NECESSARY (to deflation depth 25; k* censored). Ablating the top-25 linearly-decodable provenance directions out of the resistant condition at every layer — which drives decodability from 0.999 to 0.579 — destroys NONE of the header's resistance (necessity flat-to-slightly-negative across all 25 rungs; −0.073 at k=25, CI [−0.124, −0.034]). Per-k dynamic-range and mass controls pass throughout; REPRODUCTION of PRV-01g holds at k=1 (0.0079 vs 0.0093). EXISTENTIAL (invariance-safe): there exists a 25-direction subspace whose removal drives channel decodability down (0.999→0.579) and leaves the header's resistance intact — a constructive demonstration that decodability and causal role come apart, NOT a universal "the entire code" claim (2608.10566 forbids it: the deflation subspace is procedure-relative). Deflation did not exhaust the decodable code in 25 Euclidean steps (decodability 0.579, not chance) — a PROCEDURE-RELATIVE stopping count under StandardScaler+LR, NOT an intrinsic dimension (2608.10566, fetched: erasure count changes under an information-preserving invertible reparameterization; StandardScaler is itself such an affine map). Consistent with distributed coding; the redundancy signature at a fourth level, stated as a procedure-defined estimand.

**Result: the well-posed successor to PRV-01g's single-axis null. ANCHOR exact on FULL (Y(U)=−3.191, Y(H)=−0.805, denom
+2.386 — the raw-column header effect, 4th replication). REPRODUCTION gate PASSES: k=1 necessity 0.00786 reproduces PRV-01g's
0.00932 within ±0.01 (pipeline validated). Iterative deflation (INLP) ran to the cap of 25: held-out decodability fell 0.999 →
0.579 but never reached the ≤0.55 stopping bar, so k* is CENSORED AT 25 — the decodable code was not exhausted by 25 Euclidean
deflation steps under this estimator (a procedure-relative stopping count, NOT an intrinsic dimension — see the 2608.10566
section below). The per-k G-DYNAMIC-RANGE control held at EVERY k (random-rank-k projection moved Y 0.010 → 0.084 nats, all far
below the 0.597 bar), and mass stayed ~0.45, so all 25 rungs are interpretable — the run is not depth-limited by its controls,
only by the deflation cap. Across that entire interpretable range the necessity curve is flat-to-negative: 0.008 (k=1) → peak
0.077 (k=11) → −0.073 (k=25). Removing the top-25 decodable "provenance" directions does not reduce the header's resistance; at
high k it slightly INCREASES it (Y(H⊥v)=−0.630 vs Y(H)=−0.805). → INFORMATION-NOT-NECESSARY over the swept subspace.** Ran
2026-09-24, Lambda a100_sxm4, FULL n=720, $1.18 (+$0.86 on a prior unhealthy a10, terminated clean, no orphan; $2.04 total),
terminated clean; re-verified from json. PREREG_PRV01H.md sha256 `fdd4b552...` (chained PRV-01g `d815b111...`). (SMOKE
ANCHOR-FAIL Y(U)=−4.617 was the 40-item biased subsample; FULL is the real check.)

## ⚠ Correction to the runner's auto-outcome string
The runner logged "resistance routes around the ENTIRE linearly-decodable provenance code." That OVERCLAIMS — k* is censored at
25, decodability was 0.579 (not chance), so the code was NOT fully exhausted. Licensed claim: **the top-25 decodable directions
are jointly not necessary; necessity is flat-to-negative across them with controls passing, giving no indication it would climb
with further deflation.** (rule_zero: the labelled outcome checked against what the run actually removed.)

## Numbers (copied from results/prv01h.json)
| quantity | value |
|---|---|
| Y(U) / Y(H) / denom | −3.191 / −0.805 / +2.386 (anchor ±0.15 ✅; 4th raw-column replication) |
| REPRODUCTION k=1 necessity | 0.00786 (target 0.00932, ✅ within ±0.01) |
| decodability k=1 → k=25 | 0.999 → 0.579 (never ≤0.55 → **k\* censored at 25**) |
| G-DYNAMIC-RANGE rand-move k=1 → k=25 | 0.010 → 0.084 (all < 0.597 → held throughout) |
| necessity k=1 / k=11(peak) / k=25 | +0.008 / +0.077 / **−0.073** [−0.124, −0.034] |
| mass_v across k | ~0.443–0.456 (coherence ✅) |
| range_limit / mass_limit | none / none (interpretable to k=25) |

## Reading (the lead researcher's step; facts above)
1. **Existential, invariance-safe (reframed — the universal is forbidden).** State the finding as: **there exists a 25-direction
   subspace whose removal drives linear decodability of the channel down (0.999 → 0.579) and leaves the header's resistance
   intact** (necessity ≈ 0, drifting negative). That is a constructive demonstration that **decodability and causal role come
   apart** — you can strip most of the model's readable provenance signal without touching what provenance does. Two bindings from
   2608.10566: **(a)** it must be EXISTENTIAL, not universal — "the entire linearly-decodable code" / "the escape hatch is closed"
   is exactly the inference the paper forbids, just relocated from *how big* to *what was removed*: the deflation procedure is not
   affine-invariant, so the subspace it selects isn't either, and a different parameterization erases different content. **(b)**
   decodability here was REDUCED to 0.579, **not killed to chance**, so the clean existential ("removal DESTROYS decodability and
   leaves resistance intact") is one step short — establishing it needs a run that actually reaches chance (PRV-01h-r's
   G-DECODABILITY-KILLED gate + a higher cap). What is NOT licensed either way: that no linear subspace carrying the channel is
   necessary (untested).
2. **k\* censored at 25 is a finding — but a PROCEDURE-RELATIVE one, not an intrinsic dimension.** Removing 25 Euclidean-greedy
   directions under StandardScaler+LR only drops decodability to 0.579, i.e. the decodable signal is not concentrated in a few
   directions this procedure strips early — consistent with distributed coding. **2608.10566 (fetched) forbids reading k\*=25 as
   a dimension:** the cumulative Euclidean erasure count "can change under an information-preserving invertible reparameterization,
   so neither [stopping count nor cumulative removed rank] is intrinsically a concept dimension" — and StandardScaler is exactly
   such an affine map, so a different whitening/metric could exhaust the code in a different number of steps. So the honest claim
   is a procedure-defined estimand: "not exhausted in 25 Euclidean steps under this estimator," which is the redundancy signature
   at a fourth level (RES-06 Σ=2.48 · role/serialization TOOL 2×2 · PRV-01g single-axis · this) stated as such — NOT "≥25-d."
3. **Where the resistance actually lives (untested, named):** since the +2.386-nat effect survives removal of the linearly-decodable
   code *to the depth this procedure reached* (decodability 0.579, not chance), it is carried non-linearly, or in a
   geometry/read-position this linear-probe family
   at L1/injected-span does not capture, or outside the residual stream this projection touches. That is the next question if the
   internal locus matters; the defender-facing answer is unchanged (external surfacing works; internal steering on readable
   directions does not).
4. **Prediction missed AGAIN — 4th in a row, same direction (recorded).** §9 predicted INFORMATION-NECESSARY or DEPTH-LIMITED;
   actual is INFORMATION-NOT-NECESSARY. Even the regime call (informed by the new rule) over-predicted an effect. The PROCESS
   predictions held every time (REPRODUCTION passes; random-rank-k degrades monotonically; k*>1). The meta-finding deepens:
   causal/necessity effects on the readable provenance in this system are ~0 at every level tested — near-zero is the answer,
   repeatedly. predictions-name-a-regime-not-a-midpoint now has a corollary: in THIS system the base rate on "an internal
   readable feature is causal" is ~0; predict accordingly.

## 2608.10566 — why k* is not a dimension (fetched 2026-09-24, load-bearing)
*Iterative Erasure Count Is Not an Affine-Invariant Concept Dimension* (Jin, Dong, Li, Chou; arXiv 2608.10566, 11 Aug 2026).
Central result, verbatim: "How many directions does a neural representation use to encode a concept? A common answer repeatedly
erases probe directions and reports the stopping count or cumulative removed rank. We show that both quantities can change under
an information-preserving invertible reparameterization, so neither is intrinsically a concept dimension." An invertible **shear**
preserves the prediction problem and the population quantities "yet changes the cumulative Euclidean erasure count from one to
two," and this holds "for Moore–Penrose ordinary least squares and every finite nonnegative ridge weight." Conclusion: iterative
erasure "returns a procedure-relative estimand jointly determined by representation geometry and the full measurement procedure,
not a semantic dimension by itself." It separates **population quantities** (generating dimension, sufficient linear dimension,
minimum guarding rank) from **procedure-defined quantities** (stopping count, cumulative edit rank). **Direct bearing on
PRV-01h:** my pipeline is StandardScaler (a diagonal affine reparameterization) + LR + Euclidean projection — squarely the
non-invariant family. So k* (censored at 25) is a *stopping count*, a procedure-defined estimand; it may NOT be reported as a
dimension, concept dimension, or code size. The necessity finding is unaffected (it is a causal forward-pass measurement on the
procedure-defined subspace), but the "how big is the code" question is answered only relative to this procedure.

## Scope (binding)
INFORMATION-NOT-NECESSARY is scoped to the **linearly-decodable code under this estimator, to deflation depth 25** (where
decodability = 0.579, not chance — so not the full code), projected out at the injected span across all 32 layers, at the L1 read
geometry. It says nothing about non-linear encodings, other layers/read positions, or anything deployable. **k* is a
procedure-defined stopping count, censored at 25 — NOT a dimension, concept dimension, or code size** (binding, per 2608.10566
above). No projection is a mitigation. Single model (Llama-3.1-8B). Do not extend across models.

## What this closes
**PRV-01 role-header, internal-carrier axis — the EXISTENTIAL result as far as linear probing reaches:** v̂ not individually
necessary (01g) AND there exists a 25-direction subspace whose removal cuts decodability 0.999→0.579 with resistance intact (01h)
→ **decodability and causal role demonstrably come apart** for the readable provenance. NOT licensed: "the entire linearly-decodable
code is unnecessary" (universal, forbidden by 2608.10566) or "no linear subspace carrying the channel is necessary" (untested).
Two things remain open and go to PRV-01h-r: (i) does the existential survive across parameterizations (StandardScaler is one of
many); (ii) push deflation to *actually* kill decodability (≤0.55) so the clean "removal destroys decodability" existential is
established, not just "reduces to 0.579." Representational headline stays REDUNDANCY (input-level). The resistance's internal locus
is non-linear / outside this probe family (named, untested). Phase 3b still parked. Nothing ships; public still held.
