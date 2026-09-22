# PREREG — RES-05: is the missing half SUMMARIZED at the generation position, or COMPOSED?

**Status: LOCKED 2026-09-21.** the lead researcher spec ("price it, lock it, run it"). RES-04 localized the missing ~half OUT of the
block (span + markers + dead attention all leave ~0.48 unrecovered). Two candidates remain: it is **summarized at the
generation (readout) position** by some layer, or it is a **distributed composition** with no single site that carries it.
Same harness, same estimand/normalization as RES-02/04 → everything stays on the 0.46 scale. Chained to PREREG_RES04.md
(re-lock) sha256 `e1f1c6ea6741ec5fa7d76726e02679d3cb697c184259187d6b3f9a6feeba842b`.

## §1 The asymmetry (why this is tractable) and the trap (the whole design problem)
Composition cannot be patched; the generation position can. If the arbitration is summarized at the readout position by
some layer, a single-position patch there recovers it. If nothing recovers it at any non-trivial layer, composition wins by
elimination.

**Trap:** patching the generation-position residual near the output SETS the logits — M → 1 by construction, meaning
nothing. Every layer closer to the output is more trivially decisive. So this is a **layer sweep read against a tautology
gradient**, and the floor arm does far more work here than in any prior run. The only interpretable quantity at each layer
is **arm net-of-floor**; raw M is reported only to show the gradient.

## §2 Arms (all M = −ΔY/(2B), signed by counterbalance, template-cluster PAIRED bootstrap)
Generation position = the last token index (the assistant-header readout; logits read at position −1). Single position.
- **G_cross(L) — cross-role generation-position patch, SINGLE layer**, L ∈ {8, 12, 16, 20, 24, 28, 31}: item's
  gen-position residual at layer L ← the counterbalanced twin's gen-position residual at layer L (twin = same
  template/filler/position, cb-flipped → opposite role assignment). Only that position, only that layer.
- **G_floor(L) — same-role generation-position patch, SINGLE layer**, same L set (THE FLOOR): item's gen-position residual
  ← a same-(template,position,counterbalance), different-filler SOURCE's gen-position residual at layer L. Identical
  tautology structure, NO provenance difference (same role → same target). **Report net_L = M[G_cross(L)] − M[G_floor(L)],
  NOT the raw.**
- **L31 calibration cell** — raw M[G_cross(31)], reported explicitly as the tautology anchor: should be ≈ 1 by
  construction. Proves the readout works and marks where the sweep stops meaning anything.
- **Combined cell** — RES-04's markers+span cross-role config (all layers L8–31, marker+span regions ← twin) PLUS a
  cross-role generation-position patch at L16. Its same-role analog (markers+span+genL16 from SOURCE) is the combined
  floor. Report raw M_comb and net M_comb − M_comb_floor. Does the accounting close toward 1?
- **In-run span-only reference (S)** — RES-02/04 cross-role span swap (all layers), so the comparator "the span-only
  baseline" is measured in THIS run, paired (M_S should reproduce ~0.462).
- **VOID** — uncontested, gen-position same-content replacement at L16, compliance ≥ 90% of unsteered. Group the source
  pool BEFORE subsampling (the RES-03 fix).

## §2b Reported, not used to decompose
Per-arm mean absolute gen-position shift (= |len(twin)−len(item)| for cross, |len(source)−len(item)| for floor). Logged;
NOT decomposed (RES-03b closed the provenance/position split).

## §3 Estimand & report order
`M = −ΔY/(2B)`, exactly as RES-02/04, paired template-cluster bootstrap. **Report net-of-floor M by layer FIRST, with the
L31 raw anchor beside it in the SAME table so the gradient is visible; also show M_S (span-only baseline) in that table.**
Then the combined cell (raw + net). Key paired contrast per layer: (net_L − M_S) with paired CI.

## §4 Readings (pre-committed)
- **Net M substantially above the span-only baseline at L ≤ 20** [∃ L∈{8,12,16,20}: (net_L − M_S) > 0.10 AND paired CI
  lower > 0] → the arbitration is **SUMMARIZED at the generation position by mid-stack**; the missing half is there and it
  is localized.
- **Net M flat across early/middle, rising only as the tautology gradient bites** [no L≤20 clears the above; the rise is
  concentrated at L∈{28,31} toward the L31 anchor] → **no single-position summary exists → COMPOSITION wins by
  elimination**: a distributed computation with no site that carries it. The harder, more interesting answer.
- **Combined cell ≈ 1** [net M_comb CI-lo > 0.80] → the accounting CLOSES; remaining work is decomposition, not location.
- **Combined cell materially below 1** [net M_comb CI-hi < 0.80] → something is carried by NEITHER the block NOR the
  readout position → intermediate positions we have never touched.
- **VOID** (L16 gen-position floor compliance < 0.90×unsteered) → patch lobotomizes; not a null.

## §5 Scope
Imports position (gen position sits at different absolute index across items of different length); logged, NOT decomposed.
Reads a tautology gradient — only net-of-floor is interpretable, and only the MID-layer (L≤20) region is diagnostic; the
late-layer rise is expected and non-informative on its own. Locates (gen-position summary vs composition); does not
decompose provenance from position.

## §6 Artifacts
`res05_arms.csv`, `res05.json` (per-layer M_cross, M_floor, net, net−M_S with CIs; M_S; L31 anchor; combined raw+net;
shifts; VOID), `res05_peritem.npz` (per-item Y for every arm — persisted), `VERDICT_RES05.md`, chained to RES-04.
SMOKE-gated, watchdog armed (watchdog_always), auto-terminate, ledger, instance prompt-inj-res05.

---
## LOCK
**LOCKED 2026-09-21.** Arms (§2), reported shift (§2b), report order (§3), readings (§4) fixed. Executor specifics
(gen position = index −1, single-layer repl = {L:(pos,val)}, twin/source pairing from RES-02/04, combined = res04 M repl +
gen at L16) in the runner. sha256 in sidecar `PREREG_RES05.md.sha256`, chained to RES-04 `e1f1c6ea…`. No edit after this
line without a superseding ruling + re-lock.
