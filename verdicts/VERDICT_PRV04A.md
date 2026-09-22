# VERDICT — PRV-04a: constructed block-swap on ATT-01c survivors

**Verdict: INSTRUMENT-FAILURE (pre-committed gate).** The bookkeeper control moved (M_att=+0.228), which by
PREREG §6 (inherited from PRV-04 §6) renders the tracking-specific arms uninterpretable. Ran 2026-09-18, Lambda
a100_sxm4, FULL n=720 (B=−3.8713), terminated clean, $0.43 (+SMOKE in the same run). PREREG_PRV04A.md sha256
`07d708224e827d2a119355cbb27d281ec3959e64e65143aea293549b6c3a3962`, chained to ATT-01c `c99fdaa9…`. Supersedes
PRV-04 (twin-swap). Artifacts: `prv04a_phaseA.json`, `prv04a_arms.csv`.

## Arm table (from prv04a_arms.csv)
| arm | n | M_att | CI95 | M_att(+) | M_att(−) | swap_tv | plumb | floor | VOID |
|---|---|---|---|---|---|---|---|---|---|
| survivor_blk_3 | 3 | +0.0059 | [0.0044,0.0079] | +0.007 | +0.004 | 0.191 | 1.00 | 0.983 | no |
| survivor_blk_10 | 10 | +0.0077 | [0.0062,0.0096] | +0.004 | +0.015 | 0.135 | 1.00 | 0.983 | no |
| survivor_blk_25 | 25 | +0.0034 | [0.0013,0.0057] | +0.001 | +0.009 | 0.137 | 0.97 | 0.983 | no |
| survivor_imp_10 | 10 | −0.0005 | [−0.0018,0.0007] | −0.001 | +0.002 | **0.036** | 1.00 | 0.983 | no |
| random_layermatched | 25 | +0.0108 | [0.0076,0.0146] | +0.009 | +0.014 | 0.129 | 0.99 | 0.979 | no |
| **bookkeeper_25** | 25 | **+0.2278** | [0.2015,0.2519] | +0.143 | +0.393 | 0.285 | 0.44 | 0.946 | no |
| defeater_allsurv | 173 | −0.1288 | [−0.1669,−0.1028] | −0.110 | −0.165 | 0.157 | 0.60 | 0.975 | no |

## Reading (the lead researcher's step; mechanical facts above)
- **The ATT-01c tracking survivors get NO causal leg.** survivor_blk M_att = 0.003–0.008, ~30–60× below the
  0.20 REAL cut — and NOT because the swap was a no-op (swap_tv 0.13–0.19, well above the 0.05 gate). We
  genuinely exchanged their block-attention mass at the readout position and behavior barely moved.
- **Causal influence follows block-attention MAGNITUDE, not tracking-ness.** Bookkeepers (strong consistent
  block-allocators that do NOT predict the winner) move arbitration most (+0.228) and have the largest swap
  magnitude (0.285). Random heads (no allocation) don't move it (0.011). The 173-head defeater moves it
  (−0.129) only in aggregate. Swap enough total block mass and arbitration shifts — independent of whether the
  heads track the outcome.
- **⇒ The instrument cannot isolate tracking-specific routing:** a non-tracking allocator does it as well or
  better, so M_att entangles "these heads route it" with "these heads carry a lot of swappable block mass."
  ATT-01c's surviving within-level correlation is NOT what carries the causal effect.
- **Not VOID:** all floors 0.94–0.98 vs 0.98 unsteered. The model is not globally broken; the bookkeeper effect
  is a targeted shift of the CONTESTED arbitration, not breakage of uncontested compliance.

## Confounds on record (neither rescues a ROUTED reading)
- **swap magnitude unnormalized:** M_att and swap_tv are entangled; bookkeepers move most AND carry most mass.
  This is the core reason the instrument is unclean. A clean test needs swap-magnitude matching between the
  survivor and bookkeeper arms (new design; not pre-registered here).
- **plumbing <1.0 on multi-layer arms** (bookkeeper 0.44, defeater 0.60, survivor_blk_25 0.97): a KNOWN design
  limit, ZERO inferential weight. The check compares post-swap masses against a clean forward, but once upstream
  layers are patched the masses legitimately differ. It does not touch M_att (measured end-to-end): had the swap
  not applied, M_att would be ~0, not 0.228. The swap applied; the check baseline is wrong for stacked layers.
- **survivor_imp_10 swap_tv=0.036 < 0.05:** the imp (imperative-span, not block) heads attend ~symmetrically by
  ROLE BLOCK, so the block-swap is a no-op there — correctly flagged, not read as a null.

## Consequence for the arc (my reading — the lead researcher's call)
- **The structural-anchor hypothesis did NOT get its causal leg.** ATT-01c's clean tracking core shows ~0 causal
  effect under generation-position block-mass swap. RDV-01 + KDR-01 still stand (untouched); the ATT line is now
  down to: correlational (ATT-01), ~85% artifact with a small real core (ATT-01c), and that core is causally
  inert under this intervention (PRV-04a).
- **This is not a clean "not routed" either.** The intervention is magnitude-confounded and tests only ONE form
  of routing (generation-position, block-total mass). Positional / within-block / upstream-position routing is
  untested, and the bookkeeper result shows block allocation DOES matter causally — just generically, not via
  identifiable tracker heads.
- **Two forks for the lead researcher/a second reviewer:**
  1. **Salvage the tracking question** with a swap-magnitude-matched design (match swap_tv across survivor vs
     bookkeeper vs random arms; ask whether tracking heads move behavior MORE per unit attention moved). New
     pre-reg.
  2. **Accept the negative** and read it as: at the readout position, block-attention routing is a generic,
     magnitude-driven causal input, and the tracking correlation is epiphenomenal to causation — a real (if
     negative) result closing the ATT/routing line, sending the unexplained ~53% to composition / non-generation
     positions (KDR-01's "non-linear or non-residual" remainder).

## Method lesson
A swap/patch intervention whose magnitude varies across arms cannot attribute an effect to a head PROPERTY
(tracking) when a confounding property (allocation magnitude) co-varies. Magnitude-match the intervention across
arms, or normalize M_att by swap_tv, before attributing. anchor_shape analog for interventions: match the
control on the intervention's active variable, not just its head count.
