# VERDICT — RES-01a: non-linear provenance after k=50 linear deflation (Arm A)

**VERDICT: NON-LINEAR-PROVENANCE-EXISTS (§4-A positive).** After removing all LINEAR provenance a linear probe
can find (k=50 iterative deflation → linear held-out ≈ chance, 0.54), an MLP still decodes provenance (role) at
0.90–0.95 on the held-out group-disjoint split, at all three cached saturated layers (+ the cap-bound control).
Ran 2026-09-19, Lambda a10, cached residuals, NO forwards, terminated clean, $2.49 (116 min). PREREG_RES01A.md
sha256 `7a098124afdae9ea3f6f7e06e996441675eccd13efe2b683eea42a239dcc7e37`, chained to PRV-04c `e33230a7…`.
Artifacts: `res01a.json`, `res01a_arms.csv`.

## Reproduction gate — PASSED all layers
Refit k / pe_final vs KDR-01 (kdr01_k50.json): L8 k=43 (KDR 44) pe 0.451 (0.454); L24 k=40 (42) pe 0.451
(0.451); L31 k=32 (32) pe 0.451 (0.451); L16 k=50 (50) pe 0.435 (0.434). The cached PRV-01c pool IS KDR's pool;
the deflation reproduces, so Arm A sits on KDR's actual deflation.

## Results (held-out split==0, n=34928; role balance 0.500; chance=0.50)
| layer | k | post-defl LINEAR | post-defl MLP (CI) | MLP null p95 | pre-defl MLP | NONLINEAR |
|---|---|---|---|---|---|---|
| L8 (sat) | 43 | 0.543 | **0.950** [0.937,0.963] | 0.508 | 0.972 | YES |
| L24 (sat) | 40 | 0.547 | **0.898** [0.876,0.917] | 0.507 | 0.923 | YES |
| L31 (sat) | 32 | 0.543 | **0.904** [0.886,0.922] | 0.507 | 0.928 | YES |
| L16 (cap ctrl) | 50 | 0.559 | **0.936** [0.919,0.951] | 0.511 | 0.967 | YES |

Pass criterion (§3): MLP CI-lo > max(0.55, linear+0.03, null_p95). Cleared by 30+ points at every layer.

## Reading (the lead researcher's step; facts above)
- **Provenance is overwhelmingly NON-LINEAR residual.** Linear deflation drives the linear probe to chance
  (0.54) but leaves provenance decodable non-linearly at 0.90–0.95. The linear probe/deflation structurally
  cannot see it.
- **"Linear" is load-bearing in every KDR/PRV claim.** KDR-01's "linear residual saturates near half; remainder
  non-linear OR non-residual" resolves to: **the remainder is largely non-linear RESIDUAL provenance.** The
  residual stream is NOT exhausted — the lens was.
- **KDR-01's M=0.471 is a floor on the LINEAR lens, not on residual mediation.** It deflated/measured only the
  linear provenance subspace. The true residual-mediation share is not measured by any linear-deflation M.
- **Does not touch PRV-04c or RDV-01.** Attention still isn't the router (PRV-04c); re-derivation stands
  (RDV-01). This reopens the RESIDUAL as far richer than the linear probes showed; it does NOT resurrect H3.
- **Scope:** the MLP decodes PROVENANCE (role), not the arbitration outcome — it proves non-linear provenance
  EXISTS, not yet that editing it moves behavior. That causal question is the earned next step.

## Earned next step (pre-committed §4-A)
A NON-LINEAR intervention — the non-linear analog of H4's linear-subspace exchange: edit/deflate the non-linear
provenance manifold (e.g. patch along the MLP-probe's learned representation, or an autoencoder/kernel subspace)
and measure M on the same estimand. NOT Arm B (provenance is clearly not the wrong variable). Needs forwards.

## Method lessons
1. **Linear "saturation/exhaustion" is a statement about the LINEAR lens, not the representation.** A variable a
   linear probe (and linear deflation) declares gone at chance can be recovered by an MLP at 0.90+. Never read a
   linear-deflation floor as "the information is gone." probe_upstream.
2. **A subsampled SMOKE can produce a FALSE NULL** when the sample changes the very quantity under test (here:
   deflation depth k). SMOKE stayed at k=5 (KCAP), under-deflated, and the MLP looked null; the FULL k=50 run
   flipped it to a strong positive. SMOKE is a pipeline check, not a scientific preview — the reproduction gate
   is what validated the FULL result.
3. **Persist intermediates.** This ran only because PRV-01c cached its residual pool; H4/KDR/ATT-01 discarded
   theirs, which is why only 3 of 14 saturated layers could be tested here.
