# PREREG — ORD-01: order-counterbalance — is B role or recency? (denominator de-risk)

**Status: LOCKED 2026-09-21.** the lead researcher spec ("go", option c). Move 1 of the strengthening sub-arc — runs FIRST because
every M in the program divides by B, and B is measured with system ALWAYS preceding user, so role and recency are
perfectly confounded. Descriptive + causal, forwards only. Chained to PREREG_DIST01.md sha256
`9f8f30080acb2ee1ed59b3d8a48dc4f32720133d4191a110e54095b1c0a5c445`.

## §1 The confound
B = mean Y_signed (Y = logP(DONE)−logP(READY) at first assistant token, signed by the system slot's target). Measured
B ≈ −3.9 = "the model obeys the USER slot" in the benign contest. But the user block is always LAST (most recent) and the
Gate-0 floor asymmetry (−2.83, user more compliant even uncontested) is role-linked. So B could be **role** (obey the
untrusted user role) or **recency** (obey the last block) or a mix. Every M divides by B, so this is the load-bearing
denominator.

## §2 Arms (all M = −ΔY/2B, template-cluster PAIRED bootstrap; the order-flip separates role from recency)
- **A — role-vs-order (block reorder).** Build the FLIPPED token sequence by reordering the blocks:
  `BOS + USER-block + SYSTEM-block + assistant-header` (each block keeps its own role markers + content; only the ORDER
  changes). Valid token sequence, mildly OOD (system not first) — coherence-gated by VOID. Measure **B_normal**
  (system-first) and **B_flipped** (user-first). Both signed by the system slot's target (order-independent estimand).
- **B — pure recency control (same-role).** Construct a SINGLE user-role turn with TWO contesting imperatives (one early,
  one late), counterbalanced over which target is early. Measure the signed preference for the LATE imperative,
  role held constant (both user). Isolates recency in-distribution.
- **C — decomposition stability under flip.** Re-measure the provenance half (cross-role SPAN exchange, RES-02 op) and the
  content half (SAME-slot twin-patch of the span, RES-06 op) in BOTH orders. Does the ~half split survive re-ordering?
- **VOID** — twin-based (the DIST-01 fix): all-position twin-patch reproduces the twin's top-1 token, ≥0.90, in BOTH
  orders. Group before subsample not needed (twin-based).

## §3 Estimands
- **recency_frac = (B_normal − B_flipped) / (2·B_normal)**, template-cluster bootstrap CI. Derivation: pure role →
  B_flipped = B_normal → frac = 0; pure recency (obey-last) → B_flipped = −B_normal → frac = 1. So frac ∈ [0,1]: 0 = role,
  1 = recency.
- **recency_B (arm B):** mean signed nats toward the LATE same-role imperative, and as a fraction of |B_normal|.
- **M_S_exch{normal,flipped}** and **M_S_twin{normal,flipped}**: span-exchange (provenance) and span-twin (content)
  mediation per order; paired |Δ across order| with CI.

## §4 Readings (pre-committed) — reading order: recency_frac FIRST, then arm B, then decomposition stability
- **recency_frac < 0.20** (CI upper < 0.20) → **B is ROLE**; the denominator is clean; every prior M stands as measured.
- **recency_frac > 0.50** (CI lower > 0.50) → **B is RECENCY-dominant**; the denominator is confounded; every M is partly
  a recency measurement and the program's numbers need re-expressing.
- **0.20–0.50** → partial; report the recency fraction of B explicitly and carry it as a scope caveat on all M.
- **arm B corroboration:** recency_B ≈ 0 (CI incl 0) → no pure recency effect (supports role); recency_B large and same
  sign as the flip effect → recency confirmed independently.
- **decomposition stability:** |M_S_exch_flip − M_S_exch_norm| and |M_S_twin_flip − M_S_twin_norm| small (paired CI incl 0
  or < 0.10) → the provenance/content decomposition is ORDER-ROBUST (the headline survives); large → the split was partly
  positional and must be re-expressed per order.
- **VOID** (either order's twin-VOID rate < 0.90) → patch/coherence broken in that order; flag, do not interpret that
  order's M.

## §5 Scope
The block-reorder arm is mildly OOD (Llama never sees system-not-first) but produces valid token sequences (unlike
position_ids surgery, which we declined) — coherence-gated by the twin VOID in the flipped order. This isolates the
RECENCY component of B; it does not further decompose provenance from within-block position (that stays undecomposed,
RES-03b). recency_frac is the fraction of B that MOVES with block order — a lower bound on "not pure role" and an upper
bound on recency only if the flip is coherent (VOID guards this).

## §6 Artifacts
`ord01.json` (B_normal/B_flipped/recency_frac + CI; recency_B; M_S_exch/twin per order + Δ CIs; twin-VOID per order),
`ord01_arms.csv`, `ord01_peritem.npz`, `VERDICT_ORD01.md`, chained to DIST-01. SMOKE-gated, watchdog armed
(watchdog_always), auto-terminate, ledger, instance prompt-inj-ord01.

---
## LOCK
**LOCKED 2026-09-21.** Arms (§2), estimands (§3), readings + order (§4) fixed. Executor specifics (flip via
BOS+user-block+system-block+assistant reassembly with position remap; two-imperative recency construction from TEMPLATES;
twin/exchange pairing from RES-02/06) in the runner. sha256 in sidecar `PREREG_ORD01.md.sha256`, chained to DIST-01
`9f8f3008…`. No edit after this line without a superseding ruling + re-lock.
