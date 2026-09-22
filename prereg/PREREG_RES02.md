# PREREG — RES-02: the lens-free ceiling — full-residual cross-role exchange

**Status: LOCKED 2026-09-20.** the lead researcher spec ("exchange the whole residual"), authorized "price it and run it … good
unless flags go up" (no blocking flags raised). The earned non-linear step from RES-01a/b, done assumption-free:
no probe, no subspace, no linearity anywhere. Measures the CEILING on residual mediation, lens-free. Chained to
PREREG_RES01B.md sha256 `d00e885241a61246f9aabcd23abae9157488013d1b16e49b79bbe1eb9308d9b0`. Model
Llama-3.1-8B-Instruct, bf16, Lambda. Reuses H4's all-layer residual-edit harness (hooks L8–31, blocks_and_imp,
VOID, template-cluster bootstrap); the intervention changes from projection-exchange to full-span replacement.

## §1 Question
Every M so far is conditioned on a lens (k=25, k=50, linear). A full-residual exchange is lens-free. Patch the
item's imperative-span residual with the content-matched twin's, at every layer L8–31 (all-layer; single-layer
defeated by re-derivation, RDV-01). If M≈1, the residual at these spans carries the whole arbitration and the
linear/non-linear split was only about what each instrument could see. If M≈0.5, even complete residual exchange
gets half → the remainder is genuinely not in the residual stream at these positions.

## §2 Intervention — full-span residual EXCHANGE (no probe, no subspace)
Battery is content-matched: item i has imperative X in the system slot, its twin i′ (same template/filler/
position, counterbalance flipped) has the SAME imperative X in the user slot. At every layer L8–31, REPLACE
(overwrite, not add) i's system-imperative-span residual with i′'s USER-imperative-span residual (identical
content X, user-role context), and i's user-imperative-span residual with i′'s SYSTEM-imperative-span residual
(content Y, system-role context). Provenance exchanged, content held. Span lengths match by construction (same
imperative string); items whose spans mismatch after tokenization are skipped and counted. Captured from the
twin's clean forward (output_hidden_states). `M = −ΔY/(2B)`, ΔY = Y_patched − Y_baseline signed by
counterbalance, template-cluster bootstrap, exactly as H4/KDR. B measured fresh.

## §2b Named limitation (stated up front, per the lead researcher)
Cross-slot exchange imports the twin's POSITIONAL information along with provenance (H4's subspace swap avoided
this by moving only the provenance projection; the price of dropping the lens). So Arm 1 alone cannot separate
provenance from position-import. This is a named limitation, not a footnote. The CEILING reading (Arm 1 ≈ 1) is
robust to it; the decomposition reading is not.

## §3 Arms
1. **Cross-role exchange** (treatment) — §2.
2. **Same-role / same-position / same-target / different-filler exchange** (disruption control) — replace i's
   system-span with a DIFFERENT-filler same-(template,position,counterbalance) item's system-span (identical
   imperative string, different benign filler context), same for user-span. Provenance held, decision held, only
   filler-context foreign → any ΔY is generic full-span patching disruption. NOTE: this is a conservative
   (lower-bound) disruption floor — its swap magnitude is smaller than cross-role's, so Arm1−Arm2 may
   over-attribute; logged, and the ceiling does not depend on it.
3. **VOID floor** — on uncontested items, replace the instruction span with a same-target different-filler
   source (content preserved) at every layer; compliance must stay ≥ 90% of unsteered. A same-content
   replacement that breaks compliance means the patch mechanism itself lobotomizes the model → VOID.

## §4 Readings (pre-committed) — report Arm1−Arm2 FIRST, then Arm1
- **Arm 1 ≥ 0.80 (CI-lo > 0.70)** → CEILING-HIGH: complete residual exchange accounts for (most of) the
  arbitration; the residual at these spans carries it; which component (provenance vs position) did it is the
  NEXT question, not a flaw here. The linear/non-linear split was about instrument visibility.
- **Arm 1 ≤ 0.60** → CEILING-HALF-OR-LESS: even complete residual exchange gets ≈half → the remainder is not in
  the residual stream at these positions (generation-position, composition, or elsewhere). Decomposition becomes
  load-bearing; spec the position-import control before any provenance claim.
- **0.60 < Arm 1 < 0.80** → intermediate; report, decomposition load-bearing.
- **Arm 1 ≫ Arm 2 (M1−M2 CI > 0)** → cross-role exchange moves behavior beyond generic patching disruption
  (cannot alone separate provenance from position-import — §2b).
- **VOID** (arm floor < 0.90×unsteered) → patch lobotomizes the model; not a null.

## §5 Scope
Lens-free ceiling at the imperative spans, L8–31. Does not touch PRV-04c (attention) or RDV-01. The position
confound here is REAL and material (contested template is system-early/user-late, unlike the PRV-01c pool) — so
§2b is binding and a low Arm 1 triggers a proper position control, not a claim.

## §6 Artifacts
`res02_arms.csv` (arm, M, CI, dY, floor_compliance, VOID, n_pairs, n_skipped), `res02.json`, `VERDICT_RES02.md`,
sidecar chained to RES-01b. Needs forwards (contested battery). SMOKE-gated, on-instance watchdog armed
(watchdog_always), auto-terminate, ledger, instance named prompt-inj-res02.

---
## LOCK
**LOCKED 2026-09-20.** Intervention (§2), limitation (§2b), arms (§3), readings (§4) fixed. Executor specifics
(twin/source pairing, span-length handling, capture/replace hooks) in the runner. sha256 in sidecar
`PREREG_RES02.md.sha256`, chained to RES-01b `d00e8852…`. No edit after this line without a superseding ruling +
re-lock.
