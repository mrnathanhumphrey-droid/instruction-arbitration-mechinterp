# PREREG — PRV-04a: is the arbitration routed? (constructed block-swap on ATT-01c survivors)

**Status: LOCKED 2026-09-18.** SUPERSEDES PREREG_PRV04.md §2 (twin-swap) — the lead researcher ruled "go as planned" on the
(a) fork after ATT-01c returned PARTIAL. Reason for supersession: the counterbalanced-twin swap is a near-no-op
(swap_tv≈0.02; PRV-04 Phase A INVALID) because twins are content-matched, so the tracking heads' attention is
~invariant to the DONE↔READY flip → nothing to swap. (a) replaces the twin source with a CONSTRUCTED
intervention that is non-trivial by construction. Same estimand/normalization as the residual work → M_att
directly comparable to M. Chained to PREREG_ATT01C.md sha256
`c99fdaa9ccea199d5e2cd3709cfacafb3ffd00f67499c6081337df6f26800a84`. Model Llama-3.1-8B-Instruct, bf16, eager
attention, Lambda. Everything in PREREG_PRV04.md §1, §4, §5, §7 is INHERITED; only §2 (intervention), §3 (arms),
§6 (readings) are restated below.

## §2 Intervention — CONSTRUCTED BLOCK-SWAP (supersedes twin-swap)
For each contested item i and each target head, at the **generation-position query row** (last row of the
attention matrix — where Y is read and where ATT-01/ATT-01c located tracking), **exchange the total attention
mass between the two role blocks**, shape-preserving:
- `m_sys = Σ α[sys_block]`, `m_usr = Σ α[usr_block]` (blocks = headers+markers included, as A_blk).
- new α[sys_block] = α[sys_block] · (m_usr / m_sys); new α[usr_block] = α[usr_block] · (m_sys / m_usr).
  (If a block's mass < 1e-4, distribute the incoming mass uniformly over that block — no shape to preserve.)
- All non-block keys (BOS, generation prompt, tokens outside both role spans) are **untouched**. Total mass is
  preserved (still sums to 1). Non-generation query rows are left as the plain forward → the intervention is
  isolated to the readout position.
This is the attention analog of H4's residual projection-EXCHANGE: it forces the head to route to the OTHER
role block. It is a no-op only for a head that already splits mass equally between blocks (m_sys≈m_usr) — such a
head does not route by block asymmetry, and the swap-magnitude gate will flag it. `M_att = −ΔY/(2B)`,
ΔY = Y_patched − Y_baseline signed by counterbalance, template-cluster bootstrapped, exactly as M. B measured
fresh (baseline, no patch). Ablation remains excluded. **No twin.**

## §2b Shared-sign guard (ATT-01c lesson, mandatory)
Report M_att SEPARATELY per counterbalance level (s=+1, s=−1) for every arm. A real causal effect appears in
BOTH levels with consistent sign; an effect visible only in the pooled/signed number is suspect. The pooled M_att
is the headline; the two per-level M_atts are the guard.

## §3 Arms (from ATT-01c `att01c_withinlevel.csv`, the CLEAN set)
- **survivor-blk {3, 10, 25}** — heads with `pass_blk_010==True` (both counterbalance levels, same-sign, CI
  excl 0, |r|≥0.10), ranked by robust within-level magnitude min(|blk_r_p|,|blk_r_m|). PRIMARY. n_pool=173.
- **survivor-imp {10}** — `pass_imp_010==True`, ranked by min(|imp_r_p|,|imp_r_m|). The clean text-ish set, for
  the marker-vs-content causal contrast. n_pool=56.
- **layer-matched random** — same count + per-layer distribution as survivor-blk-25, drawn from heads that pass
  NEITHER control (else "these heads" confounds with "deep heads"). Negative control.
- **bookkeeper-25** — from att01_heads.csv (alloc-significant, ¬tracking): generic-disruption detector.
- **defeater — all-survivors-every-layer** — all 173 blk-passers patched at once (INHERITED §4 defeater, now on
  the clean set): heads outside the patched subset can re-route and rebuild; an all-survivor null is required
  before concluding routing isn't the path.

## §5 Guards (inherited + adapted)
- **VOID:** apply the SAME block-swap to uncontested items; per-arm compliance ≥ 90% of unsteered floor. A swap
  that breaks the model on uncontested (where the role isn't contested) gives a flat M_att that reads like a null.
- **Plumbing:** post-inject generation-row equals the constructed target (per arm). Zero inferential weight.
- **Swap-magnitude gate:** mean TV(swapped generation-row, own generation-row) over patched heads ≥ 0.05, per
  arm. Below → the swap is a no-op (symmetric heads); the arm's M_att is uninterpretable and flagged INVALID —
  exactly the gate that correctly caught the twin-swap failure.

## §6 Readings (pre-committed)
- **survivor-blk M_att ≥ 0.20 (CI excl 0), random & bookkeeper ≈ 0, BOTH per-level M_atts same-signed & nonzero**
  → ROUTED: generation-position block-attention through the clean tracking heads causally carries a substantial
  share of the arbitration. The structural-anchor account gets its first causal leg.
- **survivor-blk ≫ survivor-imp** → the anchor is the role-marker block, not instruction content; ATT-01c's
  surviving marker-vs-text asymmetry becomes causal.
- **All arms ≈ 0 INCLUDING the defeater** → block-attention routing at the readout position isn't the path; the
  ~53% sits where neither instrument reaches (composition, or non-generation positions) → a real finding.
- **random or bookkeeper moves, or VOID** → generic disruption / instrument failure; other arms uninterpretable.
- **survivor-blk swap_tv < 0.05** → survivors attend ~symmetrically by block; block-mass swap is a no-op →
  routing, if any, is not via block-mass asymmetry (would need a within-block/positional intervention). Flagged,
  not read as a null.
Effect only in the pooled M_att but not within either level (per §2b) → treat as a residual shared-sign artifact,
do NOT read as ROUTED.

## §7 (inherited, verbatim intent) Do NOT sum M and M_att
Same mechanism at two measurement points, not independent channels. Only the combined arm (Phase B) tests
additivity. Nothing else licenses it.

## §8 Execution (staging)
- **PHASE A (now):** all §3 block-swap arms + defeater. Cheap (eager forwards, no deflation ≈ ATT-01/PRV-04),
  ~$1–3. Answers §1/§6 core.
- **PHASE B (gated):** combined arm = survivor-blk-25 block-swap **+ the k=50 residual swap** — run iff Phase A's
  survivor-blk M_att ≥ 0.20 (else additivity is moot). Needs deflation rebuilt (~7h/~$15).

## §9 Artifacts
`prv04a_arms.csv` (arm, n, M_att, CI, M_att_pos, M_att_neg, floor_compliance, VOID, plumbing_rate, swap_tv),
`prv04a_phaseA.json`, `VERDICT_PRV04A.md`. SMOKE-gated, on-instance watchdog armed before the run
(watchdog_always), auto-terminate, ledger, instance named prompt-inj-prv04a.

---
## LOCK
**LOCKED 2026-09-18.** Estimand, block-swap intervention (§2), per-level guard (§2b), arms (§3), guards (§5),
readings (§6) fixed above; §1/§4/§7 inherited from PREREG_PRV04.md. Executor specifics (block-index extraction,
mass-swap plumbing, arm mapping from att01c_withinlevel.csv) in the runner. sha256 in sidecar
`PREREG_PRV04A.md.sha256`, chained to ATT-01c `c99fdaa9…`. No edit after this line without a superseding ruling
+ re-lock.
