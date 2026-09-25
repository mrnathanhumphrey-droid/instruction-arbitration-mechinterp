# VERDICT — OPX-01 (revised): do the two spans additively determine Y?

**Verdict (mechanical):** **The "missing half" is an EXCHANGE-OPERATOR DEFICIT; and no interaction is detectable in ΔY at
these spans (the SUM is additive) while the COMPONENT SIGNS are not what additivity predicts — the signature of competition
with renormalization.** M(A_sys) + M(A_usr) = **0.968**, additivity **gap = 1 − (A_sys+A_usr) = +0.032, CI [0.019, 0.047]** —
far below the 0.10 sub-additive bar (an interactional account needed ~0.53). Runner auto-tag "INTERMEDIATE" because the gap CI
excludes 0 by a hair.
**Two binding narrowings (the reviewer):** (1) additivity *in ΔY* is not additivity *in the mechanism* — what is ruled out is
**interaction in the difference measure at these spans**, not that the computation is non-interactional. (2) The headline is
the **component sign structure**, not the additive sum; a reader who sees only 0.968 misses the finding.

- prereg: `PREREG_OPX01.md` sha256 `bd3604acc00e29ce473b87481f604193406cc3fa28108247f481efb0325bb42a` (chained EXT-01
  `86b066c7…`); runner sha256 `ba5de4e13ae41fa7254667dfe4767a55df90e55376dca761ceadf01ef115ec74`
- run: a100_sxm4 @ us-east-1, FULL n=720, $0.29, terminated clean, no orphan. `run/opx01/results/opx01.json` +
  `opx01_arms.csv` + `opx01_peritem.npz`. B = −3.8792.

## Gates
- **ANCHOR-EXCHANGE ✓** M(EXCH) = **0.4617** [0.341, 0.563] vs RES-02 Arm1 0.462 — near-exact. Harness reproduced.
- **CONSTRUCTION-CHECK ✓** M(CONSTR) = **0.9966** [0.986, 1.006] ≥ 0.97 — same-index two-sided is become-the-twin, an
  identity. **Passing confirms the pipeline; it is not evidence for anything** (the null-construction discipline).
- **VOID false** (unsteered uncontested 1.000). **MASS** ok (0.35–0.70; B_sys lowest at 0.346, > floor).

## Cells (M = fraction of the full assignment-flip; template-cluster bootstrap CI)
| cell | mapping | M | CI95 |
|---|---|---|---|
| A_sys | same-index, sys only | **−0.930** | [−1.262, −0.724] |
| A_usr | same-index, usr only | **+1.899** | [1.695, 2.225] |
| B_sys | cross-index, sys only | −0.069 | [−0.202, +0.021] |
| B_usr | cross-index, usr only | +0.292 | [0.216, 0.352] |
| EXCH (cross, two-sided) | anchor | +0.462 | [0.341, 0.563] |
| CONSTR (same, two-sided) | identity, not evidence | +0.997 | [0.986, 1.006] |

- **Additivity:** A_sys + A_usr = 0.968 ≈ CONSTR 0.997 → the one-sided same-index patches, summed, reproduce the two-sided
  identity. **gap = +0.032 [0.019, 0.047].**
- **Region-mapping (A − B, sidedness held):** sys −0.861 [−1.094, −0.711]; usr +1.607 [1.378, 1.976]. Large — same-index vs
  cross-index matters enormously per region.
- **Sidedness (B_sys + B_usr − EXCH):** −0.239 [−0.371, −0.135] → the two-sided cross swap extracts MORE than the sum of the
  two one-sided cross patches (super-additive in the cross mapping).

## Reading (the lead researcher's step; facts above)
- **The missing half was an artifact of the exchange operator.** Cross-index two-sided exchange extracts 0.46; the span
  material additively carries ~0.97. There is no interactional remainder to find — which is why six single-component
  interventions came back small-or-null: the components ARE the carriers, exchange just under-reads them. **Every "≈0.47
  causal ceiling" number in the ledger should be re-scoped to "under exchange," not "in the residual."**
- **The component signs are the new finding: competition with renormalization, not a plain weighted readout.** A positive-weight
  additive readout predicts both one-sided flips move *partway toward* the twin. Instead one moves **away** (M_A_sys = −0.93)
  and the other **overshoots by nearly 2×** (M_A_usr = +1.90). That is the signature of the two blocks **contending for a
  bounded allocation**: flipping the system block raises the user block's effective dominance and drives Y *further in the
  original direction*, while flipping the user block both flips the dominant input and increases its dominance (overshoot).
  This is the attention-mass-conservation framing the program was named after — now with numbers. The **sum** is additive; the
  **components** are not what additivity predicts, and the sign structure is the physics.
- Consistent with ORD-01 recency-dominance (the model resolves the induced system-vs-user inconsistency toward the last/user
  block) — but "additive recency-weighted readout" **under-describes** it and is not the headline; the competition-renorm sign
  structure is. Whether the renormalization is literally attention-mass is the OPX-02 question.
- The 3% gap (CI excludes 0) is a small genuine sub-additivity in ΔY, mechanistically negligible against the 0.10 bar. Report
  it; don't build on it.

## Prediction outcome
- Both gates reproduce — **HIT.**
- **SUB-ADDITIVE / interactional (large gap) — MISSED** (gap 0.032). Mechanistic prediction, so informative — but the miss is
  narrow: the comparison framing failed **in ΔY**, while the component sign structure is itself **comparison-like**
  (competition + renormalization). So this is not "comparison wrong, additive right"; it is "no interaction detectable in ΔY at
  these spans, and the mechanism question is **open**, not closed." (Recorded as a miss.)

## Scope (binding)
Explains the exchange **operator** and the span-level readout, not a new locus (RES-06 already showed the spans suffice).
CONSTR = 1.0 is a construction identity, never evidence. Single model; property of **these span positions, these layers
(L8–31), this model (Llama-3.1-8B), this battery (contested)** under residual overwrite.

**Ledger rescope — explicit list, not blanket (the reviewer).** The demonstration (spans' one-sided effects sum to ~1 while the
two-sided cross-index swap gets 0.46) covers, and re-scopes to "≈half **under exchange**, not half in the residual":
- **RES-02** (Arm1 lens-free cross-role exchange, 0.462) — directly the same operator/positions/layers/model/battery.
- **RE-01** (re-expressed RES-02's exchange: +3.58 nats vs the role budget) — same operator.

It does **not** cover (different operators — do not sweep these in):
- **KDR-01** (0.471) and **H4** (0.347) — linear-residual-**subspace** exchange / mediation, not full-span overwrite. The
  0.462≈0.471 convergence is now *suggestive that they may share the deficit*, not established.
- **RES-06** — twin-patch, not exchange (and its 0.997 is a construction identity).
- Any exchange number at positions/layers this run did not touch.

**What is closed vs open:** the "missing half is a hidden carrier elsewhere" branch is **closed** (no ΔY-interaction at these
spans; the material is in the spans, exchange under-reads it). The **mechanism** — whether the −0.93/+1.90 competition is
literally recency-driven renormalization (attention-mass) or role-bound — is **open** and is OPX-02's question.
