# PREREG — KDR-01: is it all residual? M as a function of k in the full-stack swap

**Status: LOCKED 2026-09-16** (the lead researcher: "k=50 only, and pre-commit the gate on k=100 now"). Chained to prior:
PREREG_H4.md v3 sha256 `23d169b02ea9c555d6e58179749b836a3c0d06d1ac35e1d0c84583ba706dad4d`. Partitions the
~65% of the role effect left unallocated by H4 (M=0.347 floor). Model Llama-3.1-8B-Instruct, bf16, Lambda.

## §1 Estimand
M as a function of k in the full-stack swap. k=25 is already in hand (**H4 v3, M = +0.347**). KDR-01 adds the
**k=50** point under the trusted H4 config.

## §2 Method
The trusted H4 v3 configuration — **IDENTICAL** in pool, full-train fit, deflation construction, stopping
rule, L8–31 all-position both-block projection-exchange, matched random control, estimand M, whole-ratio
paired template-cluster bootstrap, VOID guard — with the SINGLE change **KCAP = 50**. Everything else frozen;
control matched to k=50.

## §3 Pre-committed decision gate on k=100 (LOCKED BEFORE the k=50 number — no chasing)
Read k=50's M against these cuts, decided now so k=100 cannot be assumed into the plan and blow the $70 gate:
- **M(k=50) ≥ 0.50** → the trend supports **dimension-limitation** (the remainder is the cap); k=100 earns
  its cost and we pay it (~$60–90, its own instance near the gate ceiling).
- **M(k=50) ≤ 0.40** → the remaining ⅔ is **NOT the cap**; k=100 only confirms a plateau we can already see.
  Skip it; the budget goes to ATT-01's ranked heads.
- **0.40 < M(k=50) < 0.50** → **bring it back to the lead researcher.** No default.
(Verdict tiers from H4 still apply to the k=50 M itself: ≥0.20 REAL / 0.05–0.20 PARTIAL / <0.05|CI-incl
EPIPHENOMENAL — but the informative output here is the k-trend, not the tier.)

## §4 Cost (priced before quoting, per the lead researcher)
From H4 v3 (k=25, $10.19 / 307 min): the re-deflation matmul on the full 115k×4096 pool scales **k²** under
the Phase-B-identical full-recompute; LR fits scale k. k=50 ≈ LR 2× + matmul 4× ⇒ **~$20–27**, WD_FULL 7 h.
Under the $70/run gate. (k=100 ≈ $60–90 — gated by §3, NOT pre-authorized.)

## §5 Artifacts
`kdr01_k50.json` (M, CI, per-layer k, deflation curves, principal angles, VOID, dY), `VERDICT_KDR01_<date>.md`.
SMOKE-gated, auto-terminate, ledger. Runner frozen: `run/kdr01/kdr01_lambda.py` (H4 runner, KCAP=50).

---
## LOCK
**LOCKED 2026-09-16.** Config = H4 v3 with KCAP=50; k=100 gate pre-committed (§3) before the k=50 number.
sha256 in sidecar `PREREG_KDR01.md.sha256`, chained to H4 v3 `23d169b0…4d`. No edit after this line without a
superseding ruling + re-lock.
