# PREREG — PRV-04c: per-head-matched block-swap (the stampable version)

**Status: LOCKED 2026-09-19.** the lead researcher ruled "do a" — the per-head-matched design that PRV-04b v1/v2 could not
achieve (both INVALID: survivor MEAN delivered TV fell below the match window because survivor block-swap
capacity is heavy-tailed, so no single τ mean-matches a heterogeneous arm against a high-capacity one). PRV-04c
fixes it by RESTRICTING every arm to heads with capacity ≥ τ, so each compared head delivers EXACTLY τ — an
airtight head-for-head magnitude match. Chained to PREREG_PRV04B.md sha256
`49bbc89306355f4e139a266b6f81875097004dae92e4d08d670ce5cebd8dbeae`. Model Llama-3.1-8B-Instruct, bf16, eager
attention, Lambda. Inherits the interpolant intervention (PRV-04b §2), per-level guard (§2b), VOID, §7.

## §1 Question (unchanged)
At EQUAL delivered magnitude, do ATT-01c tracking survivors route the arbitration MORE than bookkeepers
(allocators that don't track) and random heads? PRV-04b established the direction (nothing routes; bookkeeper
effect is pure magnitude) but could not stamp it for lack of a valid match. PRV-04c delivers the valid match.

## §2 Capacity pre-pass (new)
Before any intervention, a MEASURE-ONLY forward pass over all n=720 items records each head's block-swap
capacity d_h = TV(α_full, α) at the generation-position row (α_full = the full block-mass exchange), WITHOUT
modifying attention (no upstream patching → clean per-head capacity). Aggregate mean d_h per head.

## §3 Arms — restricted to capacity ≥ τ (τ = 0.05)
- **survivor_matched** — blk-pass heads (ATT-01c pass_blk_010) with mean d_h ≥ τ, up to 25, ranked by robust
  within-level magnitude. PRIMARY. (These are the survivor heads that CAN be tested at τ; selecting them is the
  clean confirming case — they are the LEAST block-symmetric, most bookkeeper-like survivors, so a null here is
  decisive.)
- **bookkeeper_matched** — att01 bookkeeper heads with mean d_h ≥ τ, up to 25.
- **random_matched** — non-pass heads with mean d_h ≥ τ, layer-matched to survivor_matched count/layer-dist.
- **survivor_imp_matched** — imp-pass heads with mean d_h ≥ τ (likely few/none — block-symmetric; reported).
All arms then run the PRV-04b interpolant swap at τ=0.05: t_h = min(1, τ/d_h) → since d_h ≥ τ, delivered = τ
EXACTLY for every head. Arm-mean delivered TV must land in [0.04, 0.06] (validity), now by construction.

## §4 Validity gates
- **Match gate:** each compared arm's mean delivered TV ∈ [0.04, 0.06]. By construction (all heads cap ≥ τ) this
  passes; if runtime d (under co-patching) drops a head below τ it self-reports, and the gate still guards.
- **VOID** (inherited): per-arm uncontested compliance ≥ 90% of unsteered floor.
- **Non-empty gate:** if survivor_matched has < 3 heads (too few capacity-≥τ survivors to test), report
  CANNOT-TEST (tracking heads are too block-symmetric to be swapped at τ) — itself a finding, not a null.

## §5 Readings (pre-committed) — AT TRUE per-head matched magnitude
Primary: paired template-cluster bootstrap of Δ = M_att(survivor_matched) − M_att(bookkeeper_matched), and
survivor_matched − random_matched.
- **survivor_matched ≥ 0.20 AND Δ CI > 0 (survivor > bookkeeper) AND survivor > random** → TRACKING-ROUTES:
  tracking heads route more at equal per-head magnitude → tracking-specific; structural-anchor gets a causal leg.
- **survivor ≈ bookkeeper (Δ CI ∋ 0), both ≥ 0.10, both > random** → BLOCK-ROUTES-NOT-TRACKING-SPECIFIC.
- **bookkeeper ≥ 0.10 AND survivor < 0.05** → TRACKING-INERT: even at matched per-head magnitude tracking heads
  do nothing while allocators route → correlation anti-predictive of causal role. Strong negative.
- **all arms < 0.05 at matched τ** → NOTHING-ROUTES: block-attention routing at the readout isn't the path;
  ~53% → composition / non-generation positions. Clean negative. (Expected, given PRV-04b.)

## §6 Execution
Cheap (measure pass + swap arms, eager forwards, no deflation), ~$0.40. SMOKE-gated, on-instance watchdog armed
before the run (watchdog_always), auto-terminate, ledger, instance named prompt-inj-prv04c.

## §7 Artifacts
`prv04c_arms.csv`, `prv04c.json` (capacity histogram summary, per-arm n after cap filter, M_att, Δ CIs,
reading), `VERDICT_PRV04C.md`. §7 (never sum M+M_att) inherited.

---
## LOCK
**LOCKED 2026-09-19.** Capacity pre-pass (§2), cap≥τ arm restriction (§3, τ=0.05), gates (§4), readings (§5)
fixed above; intervention/per-level guard/VOID/§7 inherited from PRV-04b. Executor specifics in the runner.
sha256 in sidecar `PREREG_PRV04C.md.sha256`, chained to PRV-04b `49bbc893…`. No edit after this line without a
superseding ruling + re-lock.
