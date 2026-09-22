# PREREG — ATT-01c: within-level control for the shared-sign artifact

**Status: LOCKED 2026-09-18** (the lead researcher "c yes"; PRV-04 §2 fork option (c)). This is the gate on whether ATT-01's
tracking result — and the marker-vs-text split, and the head list PRV-04's arms are built from — is real or an
artifact of signing attention and behavior by the same counterbalance. Chained to PREREG_PRV04.md sha256
`a71824cfe2924a22098c194433c0ffea5f78ae83b83c93a6712c97d33ab6a458`. Model Llama-3.1-8B-Instruct, bf16, eager
attention, Lambda.

## §1 The concern (mine, introduced at ATT-01 spec time)
ATT-01 sets `A_signed = s·A_raw` and `Y_signed = s·Y_raw`, s = +1 if target_sys==DONE else −1, and reports
`track_r = corr(A_signed, Y_signed)` **pooled over both counterbalance levels**
([att01_lambda.py:79,84,90](run/att01/att01_lambda.py)). If a head carries a roughly constant positional
attention bias (attends more to one role block regardless of content), then `A_raw ≈ c`, `A_signed = s·c`, and
signing Y by the same s correlates the two **by construction, with no content-following anywhere in the
picture**. PRV-04 Phase A measured `swap_tv ≈ 0.02` at the tracking heads — raw attention is nearly invariant
to the DONE↔READY flip — which is exactly the signature that would produce this artifact. The pooled `track_r`
cannot be decomposed from the aggregates ATT-01 saved; the per-item raw arrays were discarded. So ATT-01c
re-runs the identical forward pass, persists the per-item raw arrays, and splits the correlation by level.

## §2 Identity that makes the split decisive
Within a fixed level, s is constant, so `corr(A_signed, Y_signed) = corr(A_raw, Y_raw)` — the within-level
correlation IS the content-following signal, stripped of the sign. The pooled `track_r` = within-level
covariance + a between-level mean-shift term. The mean-shift term is the artifact. Splitting by level isolates
it: a real tracker keeps a same-sign correlation inside **both** levels; a positional-bias head keeps a large
pooled r but collapses to ~0 within each level.

## §3 Procedure
Re-run ATT-01's forward pass verbatim (same stimuli `stimuli_contested.jsonl` n=720, same 30 templates, same
A_imp / A_blk / Y = logP(DONE)−logP(READY) definitions, eager attention, all 32×32 = 1024 heads). Capture and
PERSIST per item: `imp_raw (N,1024)`, `blk_raw (N,1024)`, `R (N,)`, `s (N,)`, `tmpl (N,)` to `att01c_peritem.npz`.
Then, per head:
- **Reproduction check** (sanity, zero inferential weight): recompute pooled `corr(s·A_raw, s·R)` and confirm
  it reproduces att01_heads.csv `track_imp_r` / `track_blk_r` within tolerance. If it does not reproduce, the
  re-run is not measuring the same thing → HALT, do not read the control.
- **Within-level** for level ∈ {+1, −1} separately: `corr(A_raw, R)` for imp and blk lenses; template-cluster
  bootstrap 95% CI (30 clusters within level, 5000 draws, SEED=20260914); within-level SD(A_raw) and
  mean(A_raw). Report both levels.

## §4 Pass criterion (pre-committed, per head)
A head **PASSES** the within-level control iff, in **BOTH** levels, the template-cluster bootstrap 95% CI on
`corr(A_raw, R)` excludes 0 with the **same sign**, AND within-level `|r| ≥ 0.10` in both levels. (The 0.10
floor is "meaningful magnitude"; survivorship is also reported at 0.05 and 0.15 so the collapse shape is
visible, but 0.10 + both-level same-sign CI-excl-0 is the lock.) Lens = blk for the primary (ATT-01's money
lens), imp reported alongside.

## §5 Readings (pre-committed)
Primary metric **P = fraction of ATT-01 blk-survivors (surv_blk==True in att01_heads.csv) that PASS**.
- **TRACKING-REAL** — P ≥ 0.50 → the head list stands, the split is content-following not positional bias,
  ATT-01's leg of the three-probe convergence is restored, and PRV-04 (a) (constructed block-swap) is worth
  building on the surviving head set.
- **TRACKING-ARTIFACT** — P < 0.10 (or the top-10 trackers collapse: within-level |r| < 0.10 in ≥1 level for
  the majority) → ATT-01 measured positional bias × shared sign. The head list, the marker-vs-text split, and
  ATT-01's convergence leg are **retracted**. PRV-04 (a) is not built — there is no target.
- **PARTIAL** — 0.10 ≤ P < 0.50 → report the surviving subset; (a) is built only on heads that pass, if any.
Secondary (reported, non-gating): same P for imp-survivors, the marker-reader arm (surv_blk & ¬surv_imp),
the text-reader arm (surv_imp & ¬surv_blk), and the top-10 by |track_r|.

## §6 What is NOT touched
RDV-01 (fixed reference probe, no shared sign) and KDR-01 (residual deflation, no shared sign) are independent
instruments and stand regardless of this outcome. Only ATT-01's leg is under test. PRV-04 Phase A remains
INVALID (swap-magnitude gate), not a null.

## §7 Artifacts
`att01c_peritem.npz` (raw per-item arrays — the persistence fix), `att01c.json` (reproduction deltas, per-arm
survivorship P at floors {0.05,0.10,0.15}, verdict), `att01c_withinlevel.csv` (per head: pooled r, within-level
r/CI/SD/mean per level, pass flag), `VERDICT_ATT01C.md`. SMOKE-gated, on-instance watchdog armed before the run
(watchdog_always), auto-terminate, ledger.

---
## LOCK
**LOCKED 2026-09-18.** Estimand, within-level split, pass criterion (§4), and readings (§5) fixed above.
Executor specifics (npz layout, bootstrap plumbing, arm mapping from att01_heads.csv) in the runner. sha256 in
sidecar `PREREG_ATT01C.md.sha256`, chained to PRV-04 `a71824cf…`. No edit after this line without a superseding
ruling + re-lock.
