# VERDICT — OPX-03: which textual feature carries the role-dominance asymmetry?

**Verdict (mechanical): ENUMERATION-INCOMPLETE (construction check FAILED).** Neutralizing the role-word marker AND stripping
the system date preamble removes essentially none of the OPX-01 asymmetry — **94% survives at arm PM.** Marker share ≈ 0%,
preamble/offset share ≈ 6%. Per the pre-committed logic (arm PM is a construction check, not a candidate), survival means **an
unlisted distinguishing feature remains — most plausibly the block filler/body content — and this must NOT be read as a "slot
prior."** Go find the tell.

- prereg: `PREREG_OPX03.md` sha256 `ef1e7eb6e76db57e776bae49675ad8b7493df7ea098930ebd4167040a986c4ea` (chained OPX-02
  `bce39438…`); runner sha256 `6670794eff01d9ae0dbda92ce92ed066fd6505acf5c75f3bb2f779a29b4a0877`
- run: a10 @ us-west-1, FULL n=720, terminated clean, no orphan. `run/opx03/results/opx03.json` + `_arms.csv` +
  `_peritem.npz`. NEUTRAL = `info` (single token 2801, both headers).

## ⚠ Methodology correction (self-caught) — analyze on raw ΔY, not M
The runner's headline used M = −ΔY/(2B) per arm. **Neutralizing the markers drives the baseline B toward zero** (B: BASE
−3.909, NEUTRAL −0.886, PM +1.34), so M exploded and its CIs blew up (NEUTRAL asym M = +12.3, CI [6.4, **56.9**]). This is the
OPX-02 lesson repeating under a different surgery: **when an intervention moves the denominator B toward 0 or flips it, the
normalized quantity is uninterpretable — use the raw numerator.** The verdict below is re-derived from the persisted per-item Y
on **raw ΔY** (no re-run); the qualitative result is unchanged and the magnitudes are sane. (Banked:
normalized-effect-needs-a-stable-denominator.)

## Gates
- **ANCHOR (BASE) ✓** reproduces OPX-01: M(A_sys) −0.919, M(A_usr) +1.887 (BASE B −3.909 healthy, so its M is fine).
- **CONSTRUCTION CHECK (PM) FAIL** — asym does NOT collapse (raw residual +20.57 = 94% of BASE). By §4 this is ENUMERATION-
  INCOMPLETE, reported as such. Mass ok all arms (0.59–0.65).

## Raw ΔY (nats), B-independent — primary
| arm | dY_sys | dY_usr | raw asym (usr−sys) |
|---|---|---|---|
| BASE | −7.19 [−8.2,−6.2] | +14.75 [12.9,16.5] | **+21.94 [19.45, 24.26]** |
| NEUTRAL (marker→`info`) | −10.17 | +11.67 | **+21.84 [19.47, 24.08]** |
| PM (+ preamble stripped) | −11.87 | +8.70 | **+20.57 [18.67, 22.31]** |

- **marker share** = asym(BASE) − asym(NEUTRAL) = **+0.09 [−0.33, +0.51]** — CI includes 0 → the role-word marker carries
  **~none** of the asymmetry.
- **preamble/offset share** = asym(NEUTRAL) − asym(PM) = **+1.27 [+0.57, +1.93]** — small, real, ~6%.
- **residual at PM** = **+20.57 [+18.67, +22.31]** = **94%** survives.
- (Marker/preamble do modulate the individual magnitudes — dY_sys −7.2→−11.9, dY_usr +14.8→+8.7 — but the *difference* is
  invariant. Same shape as OPX-02: these features move magnitude, not structure.)

## Reading (the lead researcher's step; facts above)
- **The role-dominance asymmetry is not the marker (~0%) and not the preamble/offset (~6%).** It is carried by something the
  surgery left intact. After PM the two blocks are `[info-header][\n\n][content]` with matched within-block offset, so the
  remaining differences are **order** (block-1 vs block-2) and **block body/filler content** (system-framing text vs
  user-voice text). OPX-02 already showed the sign is role/content-bound, not position-bound (order reversal kept the signs), so
  the **leading candidate for the unenumerated tell is the filler/body content** — step zero matched only the imperative spans,
  not the surrounding filler.
- **This is exactly what a construction check is for.** It converts "the asymmetry is role-bound and we don't know why" into a
  concrete next probe (match/neutralize the block filler), rather than a hand-wave about a "slot prior." Nothing here licenses
  "the model has a deep user-slot prior."

## Prediction outcome
- ANCHOR reproduces — HIT.
- **COLLAPSE-by-PM, marker minority (a MODULAR call) — MISSED.** It survived (94%). Recorded as a miss. This is the third OPX
  prediction to miss; the construction check kept the miss honest (it flagged enumeration failure instead of letting a
  conclusion through). The truth so far: the carrier is neither the exchange operator, nor recency, nor the role marker, nor the
  preamble — it survives every neutralization tried, pointing at block content.

## Scope (binding)
Property of these spans/layers/model/battery, normal order, residual overwrite. PM is a construction check; its failure is a
pointer to a missing feature, not a finding about a prior. Next: a matched-filler (or filler-neutralized) sub-battery to test
the block-content candidate; if the asymmetry survives *that* too, the enumeration is still incomplete.
