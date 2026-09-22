# VERDICT — RES-03: position-import control (decompose RES-02's 0.46)

**Mechanical verdict: POSITION-UNDER-TESTED (pre-committed guard fired). Directional conclusion:
PROVENANCE-DOMINANT.** The ~half residual-mediation ceiling (RES-02) decomposes into provenance ≈ 0.41 and a
small position-import ≈ 0.06; the guard fires only because the position-only lever (early/late) imports half the
position shift the cross-role swap does. Ran 2026-09-20, Lambda a100, FULL n=696 (24 skipped for span mismatch),
terminated clean, $0.35. PREREG_RES03.md sha256
`befaa3ca84c50f9a67031808314f5322c0ded026a8304ac06040a4b3c939be5b`, chained to RES-02 `66ec4cee…`. Artifacts:
`res03.json`, `res03_arms.csv`.

## Results (B=−3.869)
| arm | M | CI95 | pos shift (tok) |
|---|---|---|---|
| cross-role (M1) | 0.473 | [0.355, 0.571] | 23.3 |
| position-only (M_P) | 0.059 | [0.017, 0.100] | 11.8 |
| disruption (M2) | 0.038 | [−0.017, 0.099] | 2.0 |
| provenance = M1−M_P | 0.414 | [0.298, 0.510] | — |
| M1−M2 | 0.436 | [0.276, 0.566] | — |

M1 reproduces RES-02 (0.473 vs 0.462). VOID FIX worked: steered floor 1.000 (n=120), not VOID — patch confirmed
coherent (RES-02's VOID arm hadn't executed; this one did).

## Reading (the lead researcher's step; facts above)
- **Guard (§4): POSITION-UNDER-TESTED.** pos-only shift 11.8 < 0.6 × cross shift 23.3 (=13.98). The position-twin
  (early/late) can only move the span ~half as far as the system↔user swap does at fixed content, so the exact
  position number is not cleanly pinned.
- **Direction is provenance-dominant:**
  - Position-import is real but small: M_P = 0.059 at 11.8 tokens (CI just off 0).
  - **One CLEAN position point** (M_P=0.059 @ 11.8) + origin. (RETRACTED: the earlier "slope" used M2 @ shift 2
    as a low anchor — M2 is same-role different-FILLER, i.e. content-disruption, NOT a position manipulation;
    conflating the two was wrong.) Linear-through-origin → ~0.12 @ 23.3 tokens; reaching 0.41 needs ~7× that.
    Big ask from a single point + a near-linearity assumption → **RES-03b re-analysis replaces the assumption with
    a within-arm dose-response** (templates differ in length, so the early/late shift varies item-to-item; fit
    M_P vs its own shift on data already collected — the per-item slope earns or breaks the extrapolation).
  - Provenance (M1−M_P) = 0.414, CI [0.30, 0.51], excludes 0.
- **So the ~half residual-mediation ceiling is provenance (~0.41) + minor position-import (~0.06).**

## What "position" can and cannot mean here (narrows the asterisk, per the lead researcher)
The cross-role swap does not merely move ~23 tokens — it crosses a role-header BOUNDARY. But crossing that
boundary IS the provenance change. In TEXT there is no way to import boundary-crossing without changing
provenance; only position_ids surgery separates them. So "position" in the sense Arm P can test is the **raw RoPE
offset**, and that is the thing measuring 0.059. The asterisk is therefore narrow, not gaping.

## Decision (the lead researcher 2026-09-20): (a) accepted, conditional on RES-03b; (b) declined
- **(a) Accept provenance-dominant** — on MEASUREMENT (RES-03b within-arm dose-response), not on the single-point
  assumption.
- **(b) position_ids magnitude-matched control — DECLINED.** It puts the model in RoPE states it has never seen;
  a botched version returns a confident wrong number. This program has been bitten by exactly that class three
  times (shared-sign artifact, no-op twin swap, false-null SMOKE). A flagged asterisk beats a clean-looking
  number from a fragile instrument.

## PERMANENT ASTERISK — SUPERSEDED by RES-03b (2026-09-20)
The provenance-dominant reading below was RETRACTED by RES-03b. Its within-arm dose-response showed a STEEP
position slope (+0.031/tok, CI[0.012,0.050]) over the narrow tested range (11–14 tok): M_P 0.020@11.0 →
0.099@12.7, extrapolating to 0.41–0.72 at the 23.3-tok cross-role shift. So position-import is non-negligible and
possibly dominant; the "~7× implausible" argument does not hold. **The decomposition of RES-02's 0.46 into
provenance vs position is UNRESOLVED** (extrapolation from a 3-tok base is unreliable AND confounded with template
length, so it is not clean position-dominance either). RES-02's 0.46 stands as an UNDECOMPOSED span-exchange
ceiling. See `run/res03b/results/VERDICT_RES03b.md`.
~~*Provenance ≈ 0.41 [0.30, 0.51] after subtracting a position-import of 0.059 at 11.8 tokens…*~~ (retracted)

## Consequence for the arc (conditional on accepting the direction)
- **The lens-free residual-mediation ceiling (~half, RES-02) is mostly PROVENANCE (~0.41), not imported position
  (~0.06).** Combined with RES-01a/b (provenance richly represented, non-linear, position-independent), the
  residual at these spans carries provenance both in representation AND in ~0.41 of the causal arbitration.
- **The other ~half of the arbitration is still not in these span residuals** — generation position, cross-position
  composition, or block/header context. That locus is the next open question, separate from this one.
- Does not touch PRV-04c (attention not router) or RDV-01 (re-derivation). KDR's linear M≈0.47 ≈ the causal
  ceiling here, of which ~0.41 is provenance.

## Method note
§2b was handled by MEASURING the position shift per arm rather than assuming a match — which is exactly why the
guard could fire honestly instead of a false provenance stamp. anchor_shape for interventions: match (or at
least measure) the confound's active variable, here absolute position.
