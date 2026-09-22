# VERDICT — RES-03b: within-arm position dose-response (RES-03 Arm P)

**VERDICT (corrected 2026-09-20, the lead researcher): THE TEXT-BASED POSITION LEVER HAS NO USABLE DYNAMIC RANGE. Both
extrapolations — "provenance ≈ 0.41" and "position may dominate" — are unlicensed. The decomposition of RES-02's
0.46 into provenance vs position is PERMANENTLY UNDECOMPOSED (b declined on relevance; see below).**

The runner auto-verdict "STEEP-WITHIN-ARM → (b) warranted" was ITSELF the mirror over-extrapolation and is
corrected here: an 11–14-token window cannot speak to a 23-token effect. What survives clean is RES-02's
Arm1−Arm2 = +0.422 (vs 0.04 floor): cross-role exchange produces a large, specific behavioral effect. What is
undecomposed is WHY (provenance or RoPE offset), not WHETHER.

## (superseded framing kept for the record) ~~STEEP-WITHIN-ARM; decomposition unresolved~~ Ran 2026-09-20, Lambda a100,
FULL n=696, baseline + Arm P only, per-item PERSISTED (`res03b_peritem.npz`), terminated clean, $0.33. Chained to
RES-03 `befaa3ca…`.

## Why this was needed
RES-03 discarded per-item shift/ΔY (aggregate only) — the recurring discard bug. This re-ran to get the
within-arm dose-response the lead researcher asked for (M_P vs its OWN per-item position shift), replacing the single-point +
near-linearity assumption with a measured curve.

## Results (B=−3.869; M_P aggregate = 0.059, reproduces RES-03)
Within-arm position shift range is NARROW: min 11.0, median 11.5, max 14.0 tokens (2 populated bins).
| shift bin | M_P | CI95 | n |
|---|---|---|---|
| 11.0 | 0.020 | [−0.028, 0.069] | 348 |
| 12.7 | 0.099 | [0.048, 0.149] | 348 |
- OLS slope = **+0.031 / token**, CI [0.012, 0.050] (excludes 0). Intercept = −0.304.
- Extrapolated to the cross-role shift (23.3 tok): through-origin **0.716**, with-intercept **0.411** — either way
  position-import could account for all/most of RES-02's 0.46.

## Reading (the lead researcher's step; facts above)
- **Near-linearity is NOT supported.** M_P jumps 0.020 → 0.099 over 1.7 tokens; the slope is steep and CI excludes
  0. Extrapolated to 23.3 tokens, position-import is 0.41–0.72. Per the pre-committed logic, this is the STEEP
  case → RES-03's "provenance ≈ 0.41, position ≈ 0.06" is RETRACTED.
- **But this is NOT a clean position-dominant verdict either:**
  1. 4× extrapolation from an 11–14-token base. The intercept is −0.30 (position can't be negative at zero
     shift) — the tell that extrapolating a steep slope off this narrow base is unreliable in BOTH directions.
  2. The within-arm shift is confounded with template length (larger early/late shift ⇒ longer template/filler
     ⇒ ΔY differences from content, not just raw position). The "steep slope" is not guaranteed pure position.
- **⇒ DECOMPOSITION UNRESOLVED.** Position-import is non-negligible and possibly dominant; it cannot be bounded
  small. The in-text position lever (max ~14 tok, confounded) cannot reach the cross-role magnitude (23.3), so
  there is no safe text-based way to settle provenance vs position at the span level.

## What survives / what is retracted
- **SURVIVES:** RES-01a/b (provenance REPRESENTED — decodable, non-linear, position-independent; a representation
  result, untouched). RES-02 (lens-free residual-exchange CEILING ~0.46 ≈ KDR linear; solid but now UNDECOMPOSED).
  The other ~half not in these span residuals.
- **RETRACTED:** "the ~half ceiling is mostly provenance (~0.41)" and "residual causally carries ~0.41 of
  provenance." NOT established. RES-02's 0.46 is an undecomposed span-exchange ceiling.

## RULING (the lead researcher 2026-09-20): decline (b), decomposition PERMANENTLY UNDECOMPOSED, take the frontier
- **(b) position_ids surgery DECLINED — on RELEVANCE, not only fragility.** What changes downstream if the 0.46
  splits 0.40/0.06 vs 0.10/0.36? The ceiling is ~0.46 either way; the missing half is missing either way; the
  next real question (where the rest of the arbitration lives) does not depend on the split. This is the k=100
  decision again: precision on a decision-spent quantity isn't worth a fragile instrument (RoPE states the model
  has never seen → confident wrong numbers; class bitten 3×).
- **The uninformative measurement does NOT "ask for (b)."** A dead lever says the text-based instrument is
  exhausted; it does not license either extrapolation. Logged as permanently undecomposed.
- **Frontier = RES-04 (extent):** does the ceiling move when you widen the edit to the full block (headers
  included)? Orthogonal to the split — it LOCALIZES (block vs generation-position/composition), doesn't decompose.

## Method note
Two lessons: (1) the recurring discard bit again (per-item not persisted) — now fixed (`res03b_peritem.npz`).
(2) **A lever with no dynamic range produces a fit that extrapolates to whatever you point it at** — the mirror
of the provenance over-claim was the position over-claim, same 7× reach, opposite sign; the −0.30 intercept
(impossible at zero shift) was the misspecification tell. An extrapolation from a narrow base is an assumption
wearing a measurement's clothes. anchor_shape.
