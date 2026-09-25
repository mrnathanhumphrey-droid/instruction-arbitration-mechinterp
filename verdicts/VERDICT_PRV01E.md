# VERDICT — PRV-01e: mechanically VOID on G-SHUFFLE (an under-powered single-permutation gate), but the substantive result is a clean, strong PROPAGATED — role-header provenance survives a perfect payload forgery to d=64 (acc 0.89). The design impasse is resolved; the VOID is a gate-methodology artifact, not a broken result.

**Result: the contrast redesign WORKED. G-CONSTRUCT held 300/300 (arms byte-identical from the header on; only `ipython` vs
`user` differs), so G0 is EXACTLY at chance (0.500 at every d — the boundary confound that killed PRV-01c/r2 is gone by
construction), G-POSITION PASSES (pad-swap counterbalance maxdiff 0.042 ≤ 0.05 — not a position proxy, r2's confound
resolved), and G-VALIDITY passes (d=1 acc 1.0). The propagation curve at the peak layer (L1) is acc = 1.0 (d1) → 1.0 (d4) →
1.0 (d8) → 0.995 (d16) → 0.908 (d32) → 0.893 (d64): role-header provenance PROPAGATES strongly downstream — still ~89%
recoverable 64 tokens past the header, through a perfect payload forgery. By §7 that is PROPAGATED. HOWEVER the run is
mechanically VOID because G-SHUFFLE returned 0.200 (gate: 0.50 ± 0.08). That gate is under-powered: it uses a SINGLE
permutation on a probe whose real signal is perfectly separable, so its null is high-variance, and 0.200 is one noisy draw —
and crucially 0.200 < 0.5 is the OPPOSITE of the CV-leak signature the gate exists to catch (a leak would push shuffled
accuracy ABOVE 0.58, not below chance). So the VOID is a mis-specified-gate artifact; the substantive result stands pending a
proper multi-permutation shuffle null.** Ran 2026-09-23, Lambda a100, FULL N=300, $0.49, terminated clean; re-verified from
json. PREREG_PRV01E.md sha256 `efd4d2f6...` (chained PRV-01c-r2 `2f58285c`). (First launch boot-timed-out, $0.54, no orphan;
relaunched.)

## Gates
| gate | value | pass | note |
|---|---|---|---|
| G-CONSTRUCT | 300/300 identical, k=1 | ✅ | arms differ only in the header |
| G0 embedding-chance | L0 = 0.500 at all d | ✅ | by construction — the r2/PRV-01c fix, working |
| G-POSITION (pad-swap) | maxdiff 0.042 | ✅ | not a position proxy (replaces r2's mis-specified G6) |
| G-VALIDITY | d1 acc 1.000 | ✅ | header perfectly readable adjacent |
| **G-SHUFFLE** | **0.200** | **❌ VOID** | **under-powered: single permutation, high-variance null; 0.20 < 0.5 is anti-leak, not the failure it guards** |

## Propagation curve (peak layer L1; acc A-vs-B by downstream distance d)
| d | 1 | 4 | 8 | 16 | 32 | 64 |
|---|---|---|---|---|---|---|
| acc | 1.000 | 1.000 | 1.000 | 0.995 | 0.908 | 0.893 |
→ **PROPAGATED** (acc > 0.70 at d ≥ 32; here 0.91 / 0.89). Signal strongest at layer 1 and carried far downstream in position —
consistent with attention copying the header identity forward within a single layer.

## Reading (the lead researcher's step; facts above)
1. **The representational-provenance question is answerable now, and the answer looks like PROPAGATED.** The redesign removed
   every surface difference except the header (G-CONSTRUCT 300/300 → G0 exactly at chance), and neutralized position
   (G-POSITION pass). Under those clean conditions, header provenance is linearly recoverable ~89% a full 64 tokens
   downstream of a PERFECT payload forgery. The model encodes true-channel provenance and carries it forward.
2. **This is the H1 (encoded) direction, and it makes PRV-01d well-posed.** There IS a downstream direction to patch — at
   layer 1, persisting across d — so the causal follow-on (patch the provenance direction, measure ΔY) has a defined site.
3. **The VOID is my gate's fault, not the model's.** G-SHUFFLE with a single permutation on a strong-signal probe is a
   high-variance null; the correct test is a multi-permutation null (mean ≈ 0.5, or real-acc above the 95th percentile). The
   raw reps were not persisted, so this cannot be recomputed locally — it needs a cheap re-run with the fixed gate.

## Consequence — a gate-method amendment for the lead researcher/the reviewer (not mine to self-approve)
G-SHUFFLE should be re-specced to a multi-permutation null (n_perm ≥ 20: report the null mean/CI, pass if real-acc exceeds the
95th percentile and the null mean ≈ 0.5). Re-run PRV-01e with that gate (~$0.49) to convert this to a clean PROPAGATED stamp.
Same class as the Phase-2 degenerate validity gate and r2's mis-specified G6 — a pre-registered gate that, once run, proved
under-powered. Until then PROPAGATED is SUGGESTIVE-pending-gate-fix, not a stamped verdict.

## Scope (binding, §8)
Recoverable ≠ used. No causal verb. Permitted here: "recoverable at d," "propagates to d=64," "present at layer 1." PRV-01d
(causal) is now well-posed IF PROPAGATED is confirmed by the re-run; patch site = (layer 1, the d-range where acc stays high).
Not specced until the re-run confirms.
