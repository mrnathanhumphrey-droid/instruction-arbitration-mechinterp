# VERDICT — RES-06-FLIP: the Σ=2.48 redundancy is order-STABLE in its load-bearing regions; the only order-sensitive piece is the inert intermediate-content region.

**Result: running RES-06's twin-patch decomposition at both orders (paired, one job), the super-additive redundancy is
essentially ORDER-INVARIANT where it matters. Σ_normal = 2.478 [2.42, 2.53] (reproduces the banked 2.479) vs Σ_flipped =
2.331 [2.23, 2.40]. dΣ = −0.147 [−0.232, −0.077] is statistically non-zero (mechanical label ORDER-DEPENDENT by the CI gate)
BUT small (~6% of Σ) and localized: the per-region shift is entirely the INTERMEDIATE-CONTENT region I (dM_I = −0.17
[−0.29, −0.11], flipping from inert +0.005 to mildly negative −0.164), while the load-bearing carriers are order-invariant —
spans S 0.996→0.997 (dM +0.001 [−0.02, +0.02]), markers K 0.512→0.511 (dM −0.002 [−0.07, +0.10]), readout R 0.965→0.988 (dM
+0.023 [+0.014, +0.039]). So the redundancy — assignment redundantly encoded by S (≈1.0), K (≈0.51), R (≈0.97) — holds in
BOTH orders; it is not an artifact of the system-then-user recency layout.** Ran 2026-09-23, Lambda a10, FULL n=720 both
orders (0 skipped), twin-VOID = 1.000 both, $0.43, terminated clean; re-verified from the json/npz. PREREG_RES06FLIP.md
sha256 `1ec3b2ab211a2fe1c04d95c7443b3ddedb767d43b26d2d2adb8a979770407365` (chained RES-06 `076b2701...`).

## Results (twin-patch, all layers L8–31; M_all = 1.000 both orders = construction identity holds)
| order | B | Σ (K+S+I+R) [CI] | Σ_KSI | twin-VOID |
|---|---|---|---|---|
| normal (system→user, user recent) | −3.909 | 2.478 [2.42, 2.53] | 1.513 | 1.000 |
| flipped (user→system, system recent) | +1.667 | 2.331 [2.23, 2.40] | 1.343 | 1.000 |
| **ΔΣ = flipped − normal** | — | **−0.147 [−0.232, −0.077]** | −0.170 | — |

| region | M normal | M flipped | dM [CI95] |
|---|---|---|---|
| K markers/headers | 0.512 | 0.511 | −0.002 [−0.071, +0.100] (unchanged) |
| S imperative spans | 0.996 | 0.997 | +0.001 [−0.021, +0.021] (unchanged) |
| I intermediate content | 0.005 | −0.164 | **−0.170 [−0.287, −0.108]** (the whole ΔΣ) |
| R readout | 0.965 | 0.988 | +0.023 [+0.014, +0.039] (tiny) |

## Reading (the lead researcher's step; facts above)
1. **The redundancy is structural, not an order artifact.** The three load-bearing regions (S primary ≈1.0, K ≈0.51,
   R ≈0.97) carry the same fractions of the assignment whether the user or the system block is recent. B flips sign as
   expected (−3.91 → +1.67, recency changes who wins), yet the *decomposition* is stable. RES-06's "regions redundantly
   re-encode the assignment" is a property of the content/structure, reproduced under an order flip.
2. **The one real order effect is in the inert region.** ΔΣ = −0.147 (CI excludes 0, so mechanically ORDER-DEPENDENT) is
   entirely the intermediate-content region I going from +0.005 (inert) to −0.164 under the flip. I is where the Llama
   date-preamble + benign filler live; under the flip that material sits in the now-recent system block, and patching it
   moves behavior slightly *against* the twin's assignment. It is small and in the region that carries none of the
   assignment in either order — a minor wobble, not a relocation of the redundancy.
3. **Honest label:** mechanically ORDER-DEPENDENT by the pre-committed CI gate, but the magnitude (−0.15 on Σ=2.48) and its
   confinement to the inert region mean the accurate one-liner is **"order-stable redundancy with a small order-sensitive
   wobble in the inert intermediate region."** The gate caught a real but minor effect; the reading must not oversell −0.15
   as "the redundancy is an order effect."

## Caveats
- M_all = 1.000 both orders is a construction identity (within-template twins), not independent validation; the coherence
  gate that DID execute here is twin-VOID = 1.000 both orders (all-position twin-patch reproduces the twin's argmax every
  item) — the gate RES-06 lacked, now passed.
- Single model (Llama), DONE/READY, one flip (ORD-01). The flip is a token permutation (0 position import between
  same-length twins); partition remapped through it, dry-checked 720/720 (readout stays last, regions disjoint).
