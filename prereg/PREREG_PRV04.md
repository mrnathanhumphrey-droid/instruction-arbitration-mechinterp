# PREREG — PRV-04: is the arbitration routed? (causal intervention on attention)

**Status: LOCKED 2026-09-18** (the lead researcher/a second reviewer spec; "price it, SMOKE-gate it, lock it, run it"). Same estimand and
normalization as the residual work so M_att is directly comparable to M. Chained to prior: PREREG_KDR01.md
sha256 `e2b7887640630bd8c2710348cfb13e51ccca98c7858b15e1f535387d5d95ebd0`. Model Llama-3.1-8B-Instruct, bf16,
eager attention, Lambda.

## §1 Question
KDR-01 left ~53% of the role effect unexplained by linear residual mediation. ATT-01 says the heads whose
attention split predicts the winning instruction read the role marker. PRV-04 asks whether patching those
heads' routing moves behavior, and by how much on the same scale as M.

## §2 Intervention — SWAP, not ablate
For each item *i* and its counterbalanced twin *i′* (same template/filler/position, cb flipped → identical
token positions), **replace the target heads' attention distributions in i's forward pass with i′'s.** Position
alignment (why the battery was built content-matched) is what makes the swap possible. **Ablation excluded** —
exchange is the causally clean operation, destruction is not; do not reintroduce it. `M_att = −ΔY/(2B)`,
ΔY = Y_patched − Y_baseline signed by counterbalance, ratio bootstrapped over template clusters, paired,
exactly as before. B measured fresh (baseline, no patch).

## §3 Arms (head families from ATT-01's ranked table `att01_heads.csv`)
- **Marker-readers** (A_blk-only trackers: surv_blk & ¬surv_imp, by |track_blk_r|), n ∈ {3, 10, 25}
- **Text-readers** (A_imp-only trackers: surv_imp & ¬surv_blk, by |track_imp_r|), n ∈ {3, 10, 25}
- **Bookkeepers** (allocation-significant but NOT tracking: alloc CI≠0, ¬surv on either) — the control that
  matters: split by role, don't predict behavior → patching should do nothing; generic disruption shows here.
- **Layer-matched random** — same count + same per-layer distribution as the marker-25 arm (else "deep heads
  matter" confounds with "these heads matter").
- **Combined** [PHASE B] — one cell at the binding dose: marker-25 patch **+ the k=50 residual swap**. The only
  arm that can close the accounting.

## §4 The defeater we already know about
H4/RDV-01's lesson: heads OUTSIDE the patched set can route correctly and rebuild what we suppressed. A null
restricted to L24–31 is uninterpretable alone. **Pre-registered:** if the targeted (marker) arm nulls, an
**all-tracking-heads-at-every-layer** arm runs before any conclusion. Committed now (included as a Phase-A
cell), not a post-hoc rescue.

## §5 Guards
- **VOID:** uncontested floor compliance ≥ 90% of unsteered, PER ARM. Attention patching can break the model;
  a broken model gives a flat M_att that reads like a finding.
- **Plumbing check:** verify patched distributions equal the twin's (per arm). **Zero inferential weight.**

## §6 Readings (pre-committed)
- **Marker ≥ 0.20, bookkeepers & layer-matched random both ≈ 0** → routing carries a substantial share,
  specifically through the tracking heads. Structural-anchor account gets its first causal leg.
- **Marker ≫ text** → the anchor is the role marker, not the instruction content; ATT-01's correlational split
  becomes causal.
- **All arms ≈ 0, INCLUDING the all-layer defeater arm** → routing at these positions isn't the path either;
  the ~53% sits where neither instrument reaches → look at composition, not location. A real finding.
- **Bookkeepers move too** → generic attention disruption; VOID-adjacent, report as instrument failure.

## §7 One thing that must NOT happen in the record
**Do NOT sum M and M_att.** The residual provenance representation is *built by* these heads — plausibly the
same mechanism at two measurement points, not independent channels. Only the **combined arm** (§3, Phase B)
tests additivity; nothing else licenses it. If they came to ≈1 together, that's a question to chase, not an
identity.

## §8 Execution (staging — cost-driven, decision-relevance discipline)
Attention arms are cheap (eager forwards, no deflation ≈ ATT-01). The **combined arm alone needs the k=50
deflation rebuilt (~7h/~$15)** and dominates cost 5–10×, and it only matters if a marker effect exists.
- **PHASE A (now):** all §3 attention arms + the §4 defeater cell. ~$1–3. Answers §1/§6 core.
- **PHASE B (gated):** the combined arm — run iff Phase A's marker arm M_att ≥ 0.20 (else additivity is moot).
Staging is execution only; the estimand/arms/readings above are the lock.

## §9 Artifacts
`prv04_arms.csv` (arm, n, M_att, CI, floor_compliance, plumbing_rate), `VERDICT_PRV04.md`, sidecar chained to
KDR-01. SMOKE-gated, on-instance watchdog armed before the run (the watchdog_always fix), auto-terminate,
ledger.

---
## LOCK
**LOCKED 2026-09-18.** Design the lead researcher/a second reviewer (§1–§7 verbatim intent); executor specifics (arm definitions from
att01_heads.csv, twin pairing on template/filler/position, custom eager-attention forward for capture+inject,
M_att normalization, per-arm VOID + plumbing, Phase-A/B staging) in the runner. sha256 in sidecar
`PREREG_PRV04.md.sha256`, chained to KDR-01 `e2b78876…`. No edit after this line without a superseding ruling
+ re-lock.
