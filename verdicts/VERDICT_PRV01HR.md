# VERDICT — PRV-01h-r: ROBUST-EXISTENTIAL (on P1 and P3, the two clean geometries; P2 corroborates weakly). Reducing linear decodability of the provenance channel to the stopping bar (~0.53–0.55, within ~0.05 of chance) leaves the header's resistance intact — necessity is ZERO-TO-SLIGHTLY-NEGATIVE (P1 +0.023, P3 −0.088, P2 −0.017; all <0.15). P1 (StandardScaler) and P3 (ZCA) both start at 0.999 decodability, select largely orthogonal subspaces (angles 5.3°→89.6°), and give the same causal conclusion → decodability and causal role come apart, robustly to the coordinate system. ⚠**P2 is NOT a clean reparameterization** (its probe starts at 0.919 — a weaker, differently-regularized estimator, since L2 at fixed C=1.0 is not scale-equivariant), so it corroborates but does not carry the claim, and this is NOT a clean empirical instance of 2608.10566 (we varied the estimator, not only an invertible reparameterization).

**Result: the robustness successor to PRV-01h, and the clean form of its existential. ANCHOR exact (Y(U)=−3.191, Y(H)=−0.805,
denom +2.386). REPRODUCTION PASSES: P1 (StandardScaler+Euclidean, = PRV-01h) necessity@25 = −0.0616 reproduces PRV-01h's
−0.0734 within ±0.02 (pipeline validated). With the cap raised to 40, deflation reduced decodability **to the stopping bar**
(held-out ≤0.55, i.e. within ~0.05 of chance — the loop's first crossing of the 0.45-error bar, NOT driven to chance) in all
three parameterizations — P1 k*=37 (0.999→0.547), P2 k*=2 (0.919→0.525), P3 k*=18 (0.999→0.544) — improving on PRV-01h (censored
at 25 @ 0.579). At each stopping point, removing the decodable subspace leaves resistance intact: necessity **zero-to-slightly-
negative** — P1 +0.023 [−0.018,+0.059], P3 −0.088 [−0.129,−0.052], P2 −0.017 [−0.036,−0.001] — all below the 0.15 floor,
per-P dynamic-range (randmove 0.132/0.016/0.076 < 0.597) and coherence (mass ~0.445) passing. **The clean existential rests on
P1 and P3**: two geometries that BOTH start at 0.999 decodability (same instrument strength) but select largely orthogonal
subspaces (P1↔P3 principal angles 5.3°→89.6°) and give the same causal answer. ⚠**P2 is a weaker instrument, not a
reparameterization** — its probe starts at 0.919 because L2 at fixed C=1.0 is not scale-equivariant, so dropping the scaler
changes the estimator, not just the coordinates; it corroborates (necessity −0.017) but does not carry the claim. Because we
varied the estimator (not only an invertible reparameterization at a preserved prediction problem), this is **three procedures
disagreeing on what they remove with the causal conclusion holding across all three — NOT a clean empirical instance of
2608.10566** (claiming one would repeat the over-reach the fetch corrected). → ROBUST-EXISTENTIAL (P1+P3).** Ran 2026-09-25, Lambda a100_sxm4, FULL n=720, $0.58 (+$0.27 on a SMOKE-caught tuple-unpack bug box,
terminated clean, no orphan; $0.85 total), terminated clean; re-verified from json. PREREG_PRV01HR.md sha256 `b5b9faa8...`
(re-locked after the SMOKE-caught bug; runner `76ac0838...`; chained PRV-01h `fdd4b552...`). (SMOKE ANCHOR-FAIL Y(U)=−4.617 was
the 40-item subsample; FULL is the real check.)

## Numbers (copied from results/prv01hr.json)
| parameterization | k* | decod 1st→final | necessity [CI] | rand-move | decod-killed | dyn | coh |
|---|---|---|---|---|---|---|---|
| P1 StandardScaler+Euclid (=PRV-01h) | 37 | 0.999→0.547 | **+0.023** [−0.018,+0.059] | 0.132 | ✅ | ✅ | ✅ |
| P2 raw, no scaler, Euclid | **2** | 0.919→0.525 | **−0.017** [−0.036,−0.001] | 0.016 | ✅ | ✅ | ✅ |
| P3 ZCA-whitened, map-back | 18 | 0.999→0.544 | **−0.088** [−0.129,−0.052] | 0.076 | ✅ | ✅ | ✅ |

- REPRODUCTION: P1 necessity@25 = −0.0616 vs PRV-01h −0.0734 (|diff| 0.012 ≤ 0.02) ✅.
- Principal angles (deg): P1↔P2 [32.4, 88.2]; P1↔P3 [5.3, 13.6, 30.1, 36.6, 39.8, 47.7, 51.9, 57.8, 64.1, 71.3, 80.3, 84.8,
  86.0, 86.2, 88.2, 88.8, 89.1, 89.6]; P2↔P3 [20.9, 79.5].

## Reading (the lead researcher's step; facts above)
1. **The existential is robust across two clean geometries (P1, P3).** Both start at 0.999 decodability, reduce it to the stopping
   bar (~0.53–0.55, near but not at chance), select largely orthogonal subspaces, and leave the header's +2.386-nat resistance
   intact. Necessity is **zero-to-slightly-negative**, not "~0": P1 +0.023 (CI includes 0), P3 −0.088 [−0.129,−0.052] — P3
   *excludes* zero on the negative side, so removing that subspace made the model SLIGHTLY MORE resistant. The random-rank control
   was inert there (0.076 << 0.597), so this is not generic dimension loss — plausibly the removed subspace carried a little
   injection-following content too. Below the 0.15 bar, no threat to the conclusion, but it is a sign, not a zero. A constructive
   decodability-vs-causal-role dissociation: you can strip the linearly-readable provenance signal, in either geometry, without
   touching what provenance does.
2. **The procedures disagree on what they remove — but this is NOT a clean instance of 2608.10566.** k* differ (37/2/18) and the
   removed subspaces are largely different (angles up to ~90°). But we varied the ESTIMATOR (P2 dropped the scaler → weaker probe;
   even P1 vs P3 differ in whitening), not only an invertible reparameterization at a preserved prediction problem. So the honest
   statement is "three procedures disagree on what they remove, and the causal conclusion holds across all three" — operationally
   what we wanted, but claiming a clean theorem instance would repeat the over-reach the fetch corrected. Stating the result
   existentially (never "the code is X-dimensional") remains exactly right.
3. **P2 is the WEAKEST arm, not the sharpest — struck.** Its probe starts at 0.919 (vs 0.999), because L2 at fixed C=1.0 is not
   scale-equivariant: dropping the scaler changes the estimator's strength, not just the coordinates. So P2's k*=2 is "a weaker
   reader crosses the error bar after two directions," NOT "decodability collapses after two raw directions." It corroborates the
   existential (necessity −0.017) but is the least clean instrument; the claim rests on P1 and P3.
4. **Prediction HIT this time (recorded).** §7 predicted ROBUST-EXISTENTIAL, k* differ, against any intermediate necessity — all
   held. This is the first magnitude/regime call in the sub-arc to land, and it landed on the "~0" regime, consistent with the
   meta-finding (predictions-name-a-regime-not-a-midpoint: the base rate on "an internal readable feature is causal" ≈ 0
   here). ⚠**Calibration note (the lead researcher): one hit after three misses is a DATA POINT, not calibration** — it landed because it was a
   regime call, not a magnitude. Keep predicting regimes; keep recording the misses. The principal-angle sub-prediction ("P1↔P3
   more overlap than P1↔P2") was only partially right — P1↔P3 shares 2 aligned leading directions then diverges to orthogonal.

## Scope (binding)
ROBUST-EXISTENTIAL licenses "across the geometries tested (clean on P1+P3)," never "the linearly-decodable code" without
qualifier; three parameterizations is not invariance, and P2 is a weaker estimator not a reparameterization. It does NOT license
"no linear subspace carrying the channel is necessary" (untested), nor anything about non-linear encodings, other layers/read
positions, or deployment. Decodability was reduced to the stopping bar (~0.53–0.55), not driven to chance. **k*_P are
procedure-defined deflation depths, never dimensions** (ref-erasure-count-not-a-dimension). No projection is a mitigation.
Single model (Llama-3.1-8B). Do not extend across models.

## What this closes
**PRV-01 role-header internal-carrier axis is now closed as far as linear probing can reach, robustly:** v̂ not individually
necessary (01g) · the top-decodable subspace not necessary to deflation depth 25 (01h) · **and — reducing decodability to the
stopping bar across two clean geometries (P1, P3) that disagree on what they remove — resistance survives (01h-r).** The readable
provenance is a **correlate, not the carrier**, robust to the coordinate system. Representational headline stays REDUNDANCY at the
input. The resistance's internal locus is non-linear / outside this linear-probe family (named, untested — the only remaining
internal question). Phase 3b still parked. Nothing ships; public still held.
