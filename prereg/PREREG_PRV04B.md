# PREREG — PRV-04b: swap-magnitude-matched block-swap (does tracking route MORE per unit attention?)

**Status: LOCKED 2026-09-18.** the lead researcher ruled "1 first" (the salvage fork) after PRV-04a returned INSTRUMENT-FAILURE
(bookkeeper control moved M_att=+0.228, but M_att was entangled with swap magnitude — bookkeepers moved most AND
carried the most swappable block mass). PRV-04b removes the magnitude confound by DELIVERING THE SAME SWAP
MAGNITUDE to every head, then compares M_att. Same estimand/normalization as the residual work. Chained to
PREREG_PRV04A.md sha256 `07d708224e827d2a119355cbb27d281ec3959e64e65143aea293549b6c3a3962`. Model
Llama-3.1-8B-Instruct, bf16, eager attention, Lambda. Inherits PRV-04a §1, §5 (VOID), §7 (never sum M+M_att).

## §1 Question
PRV-04a showed causal influence follows block-attention MAGNITUDE, not tracking-ness. But it could not tell
whether, AT EQUAL MAGNITUDE, a tracking head routes more than a non-tracking allocator. PRV-04b matches the
delivered swap magnitude across arms and asks: does the ATT-01c tracking survivor set move behavior MORE per
unit attention moved than (a) bookkeepers (allocators that don't track) and (b) layer-matched random heads?

## §2 Intervention — magnitude-matched partial block-swap
For each target head at the generation-position row: let α = own attention, α_full = the PRV-04a full block-mass
exchange (α_full[sys]=α[sys]·m_usr/m_sys, α_full[usr]=α[usr]·m_sys/m_usr, mass-preserving), and
d_h = TV(α_full, α). Apply the interpolant **α' = α + t_h·(α_full − α)** with **t_h = min(1, τ/d_h)**. Because
TV(α', α) = t_h·d_h, this delivers **swap magnitude min(τ, d_h) per head** — equalized at τ across all heads
whose capacity d_h ≥ τ. The delivered TV is RECORDED inside the forward (not reconstructed from a second
forward), which also removes PRV-04a's multi-layer plumbing baseline-mismatch artifact. `M_att = −ΔY/(2B)`,
ΔY signed by counterbalance, template-cluster bootstrapped, exactly as M. Per-level M_att reported (shared-sign
guard, ATT-01c lesson). No twin.

## §2b Target magnitude (pre-committed) — RE-LOCKED τ=0.05 (2026-09-19)
**τ = 0.05.** (v1 τ=0.10 was infeasible: it was set from PRV-04a's swap_tv=0.137, which was the CONFOUNDED
two-forward reconstruction. PRV-04b's clean in-forward measurement showed survivor_blk full-swap CAPACITY is
only ~0.06, so survivors delivered 0.059 vs bookkeeper 0.081 — match gate correctly voided v1.) τ=0.05 is
reachable by survivor_blk (cap ~0.06), bookkeeper (cap ~0.08+, throttled DOWN to 0.05), and random (cap ~0.063,
throttled to ~0.05): all three land in the re-centred window below, giving a valid equal-magnitude comparison.
Heads with d_h < τ (survivor_imp, d≈0.034 — block-symmetric) deliver only d_h; reported BELOW-MATCH, excluded
from the primary test.

## §3 Arms (from ATT-01c survivors + att01 bookkeeper, same sets as PRV-04a)
- **survivor_blk {10, 25}** — pass_blk_010 heads, robust within-level ranked. PRIMARY.
- **bookkeeper_25** — att01 alloc-significant ¬tracking. The key comparator (now magnitude-matched).
- **random_layermatched_25** — from the 817 non-passers, matched count/layer-dist to survivor_blk_25. Floor.
- **survivor_imp_10** — reported, flagged below-match (block-symmetric; cannot reach τ). Not in primary test.
- **defeater_allsurv (173)** — all survivors, magnitude-matched. Aggregate check.

## §4 Validity gates
- **Match gate:** mean delivered swap_tv per non-symmetric arm within **[0.04, 0.06]** (re-centred on τ=0.05).
  If an arm's delivered TV is outside → matching failed for that arm → its M_att not compared.
- **VOID** (inherited): per-arm uncontested compliance ≥ 90% of unsteered floor.
- **Delivery floor:** an arm's delivered swap_tv ≥ 0.05 (else the swap is a no-op, as survivor_imp will be).

## §5 Readings (pre-committed) — comparison AT MATCHED MAGNITUDE
Primary statistic: paired template-cluster bootstrap of Δ = M_att(survivor_blk_25) − M_att(bookkeeper_25), and
survivor_blk vs random. With magnitudes matched, M_att IS the "per unit attention moved" efficiency.
- **survivor_blk ≥ 0.20 AND Δ CI > 0 (survivor_blk > bookkeeper) AND survivor_blk > random** → TRACKING-ROUTES:
  tracking heads route MORE per unit attention. The salvage succeeds; structural-anchor gets a qualified causal
  leg (routing IS tracking-specific).
- **survivor_blk ≈ bookkeeper (Δ CI ∋ 0), both ≥ 0.10, both > random** → BLOCK-ROUTES-NOT-TRACKING-SPECIFIC:
  block-attention allocation routes arbitration, but tracking adds nothing causal. Real, partial.
- **bookkeeper ≥ 0.10 AND survivor_blk < 0.05** → TRACKING-INERT: at equal magnitude tracking heads do nothing
  while allocators route; the tracking correlation is anti-predictive of causal role. Strong negative for ATT.
- **all arms < 0.05 at matched τ** → NOTHING-ROUTES: PRV-04a's bookkeeper effect was pure excess magnitude;
  block-attention routing at the readout isn't the path. Clean negative → ~53% to composition / non-generation
  positions.
- **random ≈ bookkeeper** → the effect isn't even allocation-specific (positional); report as such.

## §6 Execution
Cheap (eager forwards, no deflation ≈ PRV-04a), ~$0.50. SMOKE-gated, on-instance watchdog armed before the run
(watchdog_always), auto-terminate, ledger, instance named prompt-inj-prv04b. No Phase B here (additivity is
moot unless tracking routes; revisit only on TRACKING-ROUTES).

## §7 Artifacts
`prv04b_arms.csv` (arm, n, M_att, CI, M_att_pos/neg, delivered_swap_tv, match_ok, floor_compliance, VOID),
`prv04b.json` (+ Δ survivor−bookkeeper CI, Δ survivor−random CI, reading), `VERDICT_PRV04B.md`.

---
## LOCK
**LOCKED 2026-09-18; RE-LOCKED 2026-09-19 (τ 0.10→0.05, window [0.08,0.12]→[0.04,0.06]; the lead researcher "yes do the
rerun").** Only §2b τ and §4 window changed — corrected to the feasible magnitude after v1's clean capacity
measurement; estimand, intervention (§2), arms (§3), comparison readings (§5) unchanged. §1/VOID/§7 inherited
from PRV-04a. Executor specifics in the runner. sha256 in sidecar `PREREG_PRV04B.md.sha256`, chained to PRV-04a
`07d70822…`. No edit after this line without a superseding ruling + re-lock.
