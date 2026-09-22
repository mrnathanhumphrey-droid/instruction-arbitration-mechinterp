# PREREG — RES-03: position-import control (decompose RES-02's 0.46)

**Status: LOCKED 2026-09-20.** the lead researcher "Yes run it" — the earned decomposition of RES-02's cross-role ceiling
(M1=0.46 = provenance + imported position, §2b). Isolates position-import with a same-provenance position-only
swap, and MEASURES the absolute-position shift each arm imports so the magnitude-match is a number, not an
assumption. Chained to PREREG_RES02.md sha256
`66ec4cee6f380fc9f33e308eb077fe73dbbc5eee94c163a21bc39a9809bb6cc5`. Reuses the RES-02 harness.

## §1 Question
RES-02's cross-role exchange imports the twin's position along with provenance. Is the 0.46 provenance, position,
or both? Swap position while holding provenance; measure how much position that imports vs how much the cross-role
swap imports; read the decomposition against both.

## §2 Arms (full-span residual replacement, all layers L8–31, as RES-02)
1. **Cross-role** (recap; provenance + position) — item's system-span ← twin's (cb-flip) user-span, and
   vice-versa. Same content, provenance AND position swapped.
2. **Position-only** (provenance held, position swapped) — item's system-span ← its POSITION-TWIN's system-span
   (same template/filler/counterbalance, position flipped: early↔late), user-span ← position-twin's user-span.
   Same role, SAME content (same targets), DIFFERENT absolute position. 360 position-twins, content-matched.
3. **Disruption** (same-role/same-target/different-filler) — RES-02 Arm 2, conservative disruption floor.
4. **VOID** — uncontested same-content replacement, compliance ≥ 90% of unsteered. FIX vs RES-02: group the
   source pool BEFORE subsampling (RES-02's VOID arm found 0 sources because it subsampled first).

## §2b Measured position shift (the magnitude-match, reported not assumed)
Per arm, report the mean absolute token-position shift the swap imports = mean over swapped span tokens of
|mean(source-span positions) − mean(injection-site positions)|. Arm 1's shift (system↔user) is the shift Arm P
must approach for its null to be conclusive. If Arm P's shift < Arm 1's shift materially, position is
UNDER-tested and a stronger position control is required before concluding.

## §3 Estimand
`M = −ΔY/(2B)`, ΔY signed by counterbalance, template-cluster bootstrap, as RES-02. Report M1 (cross-role),
M_P (position-only), M2 (disruption), and paired M1−M_P (provenance net of position) and M1−M2.

## §4 Readings (pre-committed)
- **M_P ≈ 0 (CI incl 0 or |M_P| < 0.05) AND shift_P ≥ shift_1** → position-import is NOT the driver; RES-02's
  0.46 is PROVENANCE (position-independent causal residual mediation ≈ half).
- **M_P ≈ M1** → the cross-role effect was position; provenance ≈ 0. RES-02's 0.46 was a position artifact.
- **0 < M_P < M1** → both; provenance ≈ M1 − M_P (paired CI); report the split.
- **shift_P < shift_1 materially (say < 0.6×)** → position UNDER-tested regardless of M_P; report and spec a
  magnitude-matched position control before any provenance claim.
- **VOID** (any arm floor < 0.90×unsteered) → patch lobotomizes; not a null.

## §5 Scope
Decomposes the RES-02 span-exchange ceiling only. The missing ~half of the arbitration (not in these span
residuals) is a separate question (generation-position vs composition), not addressed here.

## §6 Artifacts
`res03_arms.csv` (arm, M, CI, dY, pos_shift, floor, VOID), `res03.json` (+ M1−M_P, M1−M2, shifts),
`VERDICT_RES03.md`, chained to RES-02. Needs forwards. SMOKE-gated, watchdog armed (watchdog_always),
auto-terminate, ledger, instance prompt-inj-res03.

---
## LOCK
**LOCKED 2026-09-20.** Arms (§2), shift measurement (§2b), readings (§4) fixed. Executor specifics in the runner.
sha256 in sidecar `PREREG_RES03.md.sha256`, chained to RES-02 `66ec4cee…`. No edit after this line without a
superseding ruling + re-lock.
