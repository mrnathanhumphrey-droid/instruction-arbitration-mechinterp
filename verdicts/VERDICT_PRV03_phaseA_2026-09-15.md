# VERDICT PRV-03 PHASE A (2026-09-15)

## OUTCOME: WEAK@L8 → Phase B subspace at L8 (partial mediation)
Mechanical, from PREREG_PRV03.md sha256 `1e5ad707514b4902d73004d0bcae44b99a2ea8b995888192e0a41105cc71d3f0`. Ran on Lambda (A100, torch 2.7.0 / transformers 4.46.0). Single-needle swap ±1·Δ_L per layer, ŵ+Δ refit per layer, three-tier Bonferroni (α=0.05/6). B = −3.879 nats.

## Env cross-check — PASS
On-instance P_e curve reproduces local at every shared layer: L8 0.0346 (local 0.033), L16 0.0454 (0.0452), L24 0.1054 (0.104), L31 0.1068 (0.105). L4 0.137, L12 0.034 (new points). Residuals + ŵ refit faithful across env.

## Per-layer M (manip-gated)
| layer | P_e | manip s→u / u→s | manip_ok | M | Bonf CI | tier |
|---|---|---|---|---|---|---|
| L4  | 0.137 | 0.61 / 0.05 | **FALSE** | −0.0019 | [−0.0053,+0.0020] | **UNINFORMATIVE** (steer didn't land; Δ_L4=0.030) |
| L8  | 0.035 | 0.99 / 1.00 | True | **−0.0284** | [−0.0440,−0.0172] | **WEAK** |
| L12 | 0.034 | 0.98 / 1.00 | True | +0.0162 | [+0.0100,+0.0237] | FLAT-tier (CI≠0) |
| L16 | 0.045 | 0.99 / 1.00 | True | +0.0026 | [−0.0013,+0.0061] | FLAT (reproduces PRV-02 null) |
| L24 | 0.105 | 0.94 / 1.00 | True | −0.0028 | [−0.0052,−0.0013] | FLAT-tier (CI≠0) |
| L31 | 0.107 | 0.83 / 1.00 | True | −0.0001 | [−0.0006,+0.0005] | FLAT (dead) |

## Mechanical reads
1. **L16 independently replicates PRV-02** (M≈0, CI incl 0; PRV-02 local M=−0.0004). Different env, fresh run, same null → row-3 holds.
2. **Residual path is NOT perfectly inert.** L8 carries a **real small** single-needle mediation: M=−0.0284 (≈2.8% of B), CI excludes 0 at Bonferroni, manip landed 99%/100%. This is the case the WEAK tier was built for — without it, 0.028 bins FLAT and "all-flat / H1 live" is falsely declared.
3. L12 (+0.016) and L24 (−0.003) show CI-excludes-0 effects **below the 0.02 WEAK floor with inconsistent signs** — edge-of-detection, not a coherent single direction.
4. **L4 uninformative, not flat:** Δ_L4=0.030 ⇒ ±1·Δ under-steers, manip fails (u→s 0.05). The sub-L8 input-proximal region is untestable at this dose; L4 is also the least-decodable informative layer (P_e 0.137). The "look early" prior is doubly dead (P_e worst at L4; steer can't land there).

## Verdict → Phase B
Per the locked three-tier rule, **WEAK → Phase B subspace at the argmax-|M| layer = L8** (partial mediation). The single ŵ needle catches a ~3% sliver at the peak-recoverability layer; Phase B (deflation-built subspace, projection-exchange) tests whether the full subspace multiplies it (→ H1, provenance drives arbitration via a subspace) or it stays a sliver (→ leaning H3, arbitration is mostly non-residual / attention routing).

Cost: $0.52 total (2 SMOKE catches + full run); instance terminated clean. Artifacts: `prv03_phaseA.json`, `prv03_full.log`, `prv03_phaseA_smoke.json`.

---
## HUMAN RULING & READING — (reserved for the lead researcher; mechanical outcome above stands)
*(the reading is the lead researcher's separate step)*
