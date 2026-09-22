# PREREG — RES-01a: is there non-linear provenance? (Arm A, cached, staged)

**Status: LOCKED 2026-09-19.** the lead researcher ruled "yes 1 first, each next step needs to be earned" — the staged, cached
Arm A of RES-01. Tests whether provenance survives the k=50 LINEAR deflation in a form a linear probe
structurally cannot see. Observational, cached residuals, NO model forwards. Chained to PREREG_PRV04C.md sha256
`e33230a7b02e475c152dfefd3a7346beee60c85994376559e29a89d70450545c`.

## §0 Premise correction (why staged, why Arm A only)
RES-01's "cached residuals, no new forwards" holds ONLY for Arm A, and only on the layers PRV-01c cached:
residuals exist for L0,8,16,24,31 (token-level, 115504×4096, `tok_resid_L*.npy` + `tok_meta.npz` with role,
split). Of the 14 KDR-01 saturated layers (8,9,10,11,12,23,24,25,26,27,28,29,30,31), **L8, L24, L31 are cached**
(L16 cached but cap-bound → control). The k=50 deflation BASES were not saved, so deflation is REFIT from the
cached pool (no forwards). Arm B needs Y_signed on the contested battery (uncached, wrong task) → forwards →
DEFERRED, earned only if Arm A is null. The other 11 saturated layers need forwards → DEFERRED.

## §1 Question
At each cached saturated layer, after removing the k=50 linear provenance subspace, can a small MLP still decode
provenance (role: system vs user) above chance and above the linear probe? I.e., is there provenance a linear
probe structurally cannot see?

## §2 Procedure (per layer L ∈ {8, 24, 31 saturated; 16 cap-bound control})
On the cached pool (role labels, group-disjoint split: split==1 train ≈80k, split==0 held-out ≈35k):
1. **Refit KDR's k=50 linear deflation** on TRAIN: standardize; iterate {fit logistic ŵ for role, deflate
   residual ⊥ ŵ, refit} until held-out linear ERROR ≥ 0.45 (KDR stop) or k=50 cap. Apply to all rows.
   **Reproduction check:** refit k and final linear held-out error must match `kdr01_k50.json` k_per_layer /
   deflation_pe_curves per layer (bf16/impl jitter small). If they do not reproduce → the deflation is not KDR's
   → HALT that layer (report, do not read).
2. On the k=50-deflated residual, fit a small **MLP** (4096→128→2, ReLU, dropout, Adam, early-stop on a
   train-internal val slice) for role. Held-out (split==0) accuracy.
3. Baselines on the SAME deflated residual: **linear** probe held-out accuracy (≈chance by construction at
   saturated layers). **Pre-deflation** MLP + linear accuracy (positive control that probes decode when
   provenance is present).
4. **Nulls:** shuffled-train-label refit — linear 1000 draws, MLP 100 draws (cost); report null 95th pct.
   Cluster-bootstrap the held-out accuracies by prompt_idx (the group-disjoint unit), 1000 draws, percentile CI.

## §3 Metric & pass criterion (pre-committed)
Provenance accuracy on balanced role (chance = 0.50). A layer shows **NON-LINEAR PROVENANCE** iff, on the
k=50-deflated held-out residual: MLP accuracy CI lower bound > max(0.55, linear accuracy + 0.03, null 95th pct).
(0.55 = a 5-pt margin over chance; must also beat the linear probe on the same deflated features and its own
shuffled null.) The layer's reproduction check must pass first.

## §4 Readings (pre-committed; RES-01 §4 restricted to Arm A)
- **Any saturated layer NON-LINEAR-PROVENANCE positive** → non-linear residual provenance EXISTS; "linear" is
  load-bearing in every KDR/PRV claim; the earned next step is a NON-LINEAR intervention (not Arm B). §4-A.
- **All cached saturated layers null** (MLP ≈ linear ≈ chance on deflated residual) → no non-linear provenance
  at L8/L24/L31; this is a strong-positive-detector null but covers only 3 of 14 layers → the earned next step
  is Arm B (the "wrong variable" reframe: does the residual carry surviving OUTCOME info?), which needs forwards.
- L16 (cap-bound) is a control, not part of the saturated verdict: linear should still decode there (provenance
  not fully removed at k=50) → confirms the pipeline detects provenance when present.

## §5 Scope
Per-layer, per cached position-set (PRV-01c token spans). Cannot see cross-layer composition. A null here does
not rule out non-linear provenance at the 11 uncached saturated layers — it is a claim about L8/L24/L31 only,
and about what to earn next.

## §6 Artifacts
`res01a_arms.csv` (layer, condition {pre/post-deflation}, probe {linear/mlp}, held-out acc, CI, null_p95,
refit_k, repro_ok), `VERDICT_RES01A.md`, sidecar chained to PRV-04c. Cached residuals uploaded (L8,16,24,31 +
meta); NO model, NO HF, NO forwards. SMOKE-gated, on-instance watchdog armed (watchdog_always),
auto-terminate, ledger, instance named prompt-inj-res01a.

---
## LOCK
**LOCKED 2026-09-19.** Estimand, procedure (§2), pass criterion (§3), readings (§4) fixed above. Executor
specifics (MLP arch, deflation refit, bootstrap plumbing) in the runner. sha256 in sidecar
`PREREG_RES01A.md.sha256`, chained to PRV-04c `e33230a7…`. No edit after this line without a superseding ruling
+ re-lock.
