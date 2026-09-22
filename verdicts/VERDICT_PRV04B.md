# VERDICT — PRV-04b: swap-magnitude-matched block-swap

**BOTH runs (τ=0.10 and τ=0.05) INVALID by the match gate — but directionally NOTHING-ROUTES, robust across two
magnitude regimes.** See "## RE-RUN v2" at the bottom for the τ=0.05 result and the combined conclusion. The
v1 detail below stands.

---

**Verdict (v1, τ=0.10): INVALID (magnitude match failed) — directionally NOTHING-ROUTES.** The pre-registered match gate
(§4: delivered swap_tv ∈ [0.08,0.12] per arm) fired: survivor_blk delivered only ~0.059 vs bookkeeper 0.081,
so the arms are NOT at equal magnitude and the Δ comparison is not a valid matched test. Ran 2026-09-18, Lambda
a100_sxm4, FULL n=720 (B=−3.8713), terminated clean, $0.34. PREREG_PRV04B.md sha256
`909748fbcf25c8732ef73044d82dcffb1c58971f9310a00aa2c7aaa299d9df05`, chained to PRV-04a `07d70822…`. Artifacts:
`prv04b.json`, `prv04b_arms.csv`.

## Why the match failed
τ=0.10 was set (PREREG §2b) from PRV-04a's survivor swap_tv=0.137 — which was the CONFOUNDED multi-layer
reconstruction (TV between two separate forwards with upstream layers already patched). PRV-04b measures
delivered TV cleanly IN the forward: survivor_blk full-swap capacity is only **~0.06**. Survivor (tracking)
heads are far more block-symmetric than PRV-04a implied — they cannot be pushed to τ=0.10, so t=1 delivered only
their capacity (~0.06), below the [0.08,0.12] window. Bookkeepers (higher block asymmetry) throttled to 0.081.

## Arm table (from prv04b_arms.csv, tau=0.10)
| arm | n | M_att | CI95 | delivered_tv | match_ok | VOID |
|---|---|---|---|---|---|---|
| survivor_blk_10 | 10 | +0.0031 | [0.0021,0.0042] | 0.0596 | no | no |
| survivor_blk_25 | 25 | −0.0001 | [−0.0013,0.0010] | 0.0591 | no | no |
| bookkeeper_25 | 25 | −0.0052 | [−0.0168,0.0034] | 0.0808 | **yes** | no |
| random_layermatched | 25 | +0.0065 | [0.0040,0.0091] | 0.0627 | no | no |
| survivor_imp_10 | 10 | −0.0004 | [−0.0015,0.0005] | 0.0339 | no | no |
| defeater_allsurv | 173 | −0.0511 | [−0.0668,−0.0411] | 0.0615 | no | no |

Δ survivor_blk_25 − bookkeeper_25 = +0.0052, CI[−0.0032,+0.0163], excl0=**False** (indistinguishable).
Δ survivor_blk_25 − random = −0.0065, CI[−0.0090,−0.0043], excl0=True (both trivially small, <0.01; noise-level).

## What is already unambiguous (despite the invalid match)
1. **The bookkeeper effect collapsed with magnitude: +0.228 (PRV-04a, deliv≈0.29) → −0.005 (PRV-04b, deliv
   0.081).** Throttling the swap killed it. This confirms PRV-04a's only "routing" signal was swap MAGNITUDE,
   not anything special about those heads.
2. **At every magnitude survivors can deliver (~0.06), nothing routes:** survivor_blk (−0.0001 / +0.003),
   bookkeeper (−0.005), random (+0.006) are all indistinguishable from zero. Δ(survivor−bookkeeper) CI ∋ 0.
3. **Tracking heads carry LESS swappable block asymmetry than bookkeepers** (capacity ~0.06 vs 0.081), which is
   itself consistent with tracking-by-fine-correlation, not by large block bias.

## Reading (my framing; the lead researcher's call)
The instrument cannot be validly matched at τ=0.10 because survivor capacity is lower than assumed. The
DIRECTION is NOTHING-ROUTES / tracking-inert, but per the pre-registered gate it is not a locked verdict. To
close it cleanly, re-run at **τ=0.05** (achievable by both — throttles bookkeeper to survivor capacity, valid
match) + recentre the match window to [0.04,0.06]. This is a τ re-lock (superseding §2b), the lead researcher's call. Cheap
($0.34). Alternative: accept the direction (bookkeeper collapse + universal ~0 at low magnitude) as the answer.

## Consequence for the arc (unchanged from PRV-04a direction, now reinforced)
Tracking heads (ATT-01c survivors) show NO causal routing of the arbitration via block-attention at the readout,
at any magnitude they can deliver. The PRV-04a bookkeeper effect was magnitude, not tracking. Structural-anchor
gets no causal leg. RDV-01 + KDR-01 stand. Caveat unchanged: only generation-position block-total mass tested;
positional/within-block/upstream routing untested.

## Method lesson
Setting a matched-magnitude target from a CONFOUNDED magnitude measurement makes the match infeasible. The
in-forward delivered-TV recording (added here) is the correct magnitude measurement; the two-forward
reconstruction (PRV-04a) inflated it. When matching interventions, calibrate the target from the CLEAN measure
of each arm's capacity FIRST. anchor_shape for interventions: the match target must be reachable by the
lowest-capacity arm being compared.

---
## RE-RUN v2 (τ=0.05, RE-LOCKED 2026-09-19; the lead researcher "yes do the rerun")
Prereg re-locked sha256 `49bbc89306355f4e139a266b6f81875097004dae92e4d08d670ce5cebd8dbeae` (only §2b τ and §4
window changed). Lambda a100_sxm4, FULL n=720 (B=−3.8713), terminated clean, $0.35. Artifacts overwrote
`prv04b.json` / `prv04b_arms.csv` (v2).

**Also INVALID** — survivor_blk_25 delivered 0.0357 (below the [0.04,0.06] window), bookkeeper 0.0448 (in),
random 0.0378 (below). Match failed AGAIN.

| arm | M_att (τ=0.05) | delivered_tv | match_ok |
|---|---|---|---|
| survivor_blk_10 | +0.0017 | 0.0351 | no |
| survivor_blk_25 | −0.0002 | 0.0357 | no |
| bookkeeper_25 | −0.0040 | 0.0448 | yes |
| random_layermatched | +0.0035 | 0.0378 | no |
| survivor_imp_10 | −0.0006 | 0.0256 | no |
| defeater_allsurv | −0.0288 | 0.0371 | no |

Δ survivor_blk_25 − bookkeeper_25 = +0.0039, CI[−0.0005,+0.0092], excl0=False (indistinguishable).
Δ survivor_blk_25 − random = −0.0037, CI[−0.0055,−0.0019], excl0=True (survivor slightly BELOW random; both tiny).

## Why the mean-match gate cannot be satisfied (structural, not a bad τ)
Survivor block-swap capacity is low and HEAVY-TAILED: mean full-capacity ~0.06 (v1), median well under 0.05. No
single τ lands survivor_blk_25's MEAN delivered in a window bookkeepers (capacity ~0.08+) also hit — lowering τ
throttles the few asymmetric survivors harder and drops the mean further (0.059 at τ=0.10 → 0.036 at τ=0.05).
Mean-matching is the wrong gate for heterogeneous-capacity arms. This failure is itself part of the finding:
**tracking heads carry too little block asymmetry to route; where anything routes (bookkeepers at high
magnitude) it is magnitude-driven, not tracking-driven.**

## Combined conclusion across three interventions (PRV-04a full-swap, PRV-04b τ=0.10, τ=0.05)
- **Bookkeeper dose-response collapse:** M_att +0.228 (deliv ~0.29) → −0.005 (0.081) → −0.004 (0.045). The only
  "routing" signal is pure swap MAGNITUDE.
- **Survivor (tracking) M_att ≈ 0 at every magnitude** (+0.005, −0.0001, −0.0002); Δ(survivor−random) negative
  (slightly below the random floor) in both matched runs.
- **⇒ NOTHING-ROUTES / tracking-inert** (direction, robust; not a locked verdict because no valid mean-match).

## To make it stampable (the lead researcher's call)
(a) One per-head-matched run: restrict survivor arm to capacity ≥ τ heads so every compared head delivers
exactly τ (airtight head-for-head match vs bookkeeper). ~$0.35, §3 arm re-lock. Selects the least
block-symmetric (most bookkeeper-like) survivors → a null there is the clean confirming case. OR (b) accept the
two-run direction. Either way: structural-anchor gets NO causal leg; RDV-01 + KDR-01 stand; only
generation-position block-total mass tested (positional/within-block/upstream untested).
