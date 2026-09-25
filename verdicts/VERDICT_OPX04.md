# VERDICT — OPX-04: does the block filler/body content carry the role-dominance asymmetry?

**Verdict (mechanical): BODY-NULL — the filler does NOT carry it.** Swapping the two blocks' fillers did not invert or shrink the
asymmetry (r = asym_SWAP/asym_BASE = **+1.06 [1.04, 1.09]**, > 0.5 — sign held, magnitude preserved, slightly grew); matching both
fillers did not collapse it (MATCH +20.56 = 94% of BASE); stripping the filler entirely did not collapse it (STRIP +25.48 = 116%).
The role-differentiated body content is not the carrier. **4th consecutive OPX prediction miss** — both callers predicted
BODY-CARRIES.

- prereg: `PREREG_OPX04.md` sha256 `356ca526d60fe1aa1026d988c778456b2c0cff932486c3eb22c80dc50bbd6248` (chained OPX-03
  `ef1e7eb6…`); runner sha256 `805f27464d4ea1c01674c2bbec647fa4d6825348860870bd60b861ca7524e764`
- run: gh200 @ us-east-3, FULL n=720, $0.30, terminated clean, no orphan (1st fire dead-boot $0.33 + a no-capacity $0 bail
  preceded it; poller caught fresh capacity). `run/opx04/results/opx04.json` + `_arms.csv` + `_peritem.npz`.

## Raw ΔY (nats) per arm — primary (B varies per arm; raw dY is the discriminator)
| arm | dY_sys | dY_usr | raw asym (usr−sys) | B | mass |
|---|---|---|---|---|---|
| BASE (native) | −7.21 | +14.76 | **+21.97 [19.48, 24.29]** | −3.90 | 0.63 |
| SWAP (fillers swapped) | −6.12 | +17.25 | **+23.37 [20.58, 25.96]** | −5.68 | 0.68 |
| MATCH (both → FN neutral) | −7.71 | +12.85 | **+20.56 [17.82, 23.06]** | −2.62 | 0.71 |
| STRIP (no filler) | −5.91 | +19.58 | **+25.48 [21.01, 29.68]** | −7.10 | 0.79 |

- **r = asym_SWAP / asym_BASE = +1.064 [1.041, 1.088]** → **BODY-NULL** (§4: r > 0.5). SWAP CI excludes 0.
- **strip survival = 1.16 [1.03, 1.27]** — survives; the growth is NOT clean (see STRIP length check below), so read only as "does not
  collapse," not as concentration.
- **match residual = +20.56 [17.82, 23.06]** — did NOT collapse. **⚠ MATCH is NOT a genuine construction check in this run**
  (correction): it made the two fillers identical but kept markers + preamble native, i.e. it removed one textual difference of
  three, so non-collapse is *expected*, not a tell. It corroborates filler-irrelevance (a second filler-manipulation arm alongside
  SWAP) but carries no enumeration information. The first genuine construction check of the whole textual enumeration is the
  joint strip (OPX-05).

## Gates
- **ANCHOR ✓ (units reconciled)** BASE reproduces OPX-01/03. The headline asym here is **raw ΔY** (+21.97); OPX-01's −0.93/+1.90
  were **M** (= −ΔY/2B). Reconciliation: raw_asym / (−2·B_BASE) = 21.97 / 7.7995 = **+2.816**, exactly M_A_usr − M_A_sys =
  1.892 − (−0.924); and the M components −0.924 / +1.892 **are** OPX-01's −0.93 / +1.90. So it is the *same object* measured across
  OPX-01→04 (raw = M × (−2B)) — the identity the joint-strip inference relies on. (Guards against the level-vs-contrast unit slip
  that broke PRV-01f's anchor.)
- **LENGTH CHECK ✓ (the reviewer's addition)** corr(per-item filler |delta|, swap move) = **+0.013 [−0.073, +0.090]** — CI spans 0,
  so the accepted filler-length delta does not explain the (negligible) swap effect. Padding was correctly declined; the confound
  is measured inert rather than engineered away.
- **FN-length record (the reviewer's addition)** FN = 9 tok; fsys mean 10.7, fusr mean 13.0 → FN shorter than both, yet MATCH did
  **not** collapse. So MATCH's non-collapse is not a "FN too short" artifact — it genuinely holds.
- **MASS ✓** 0.63–0.79 all arms.

## Reading (the lead researcher's step; facts above)
Every arm confirms the same thing from a different direction: the filler is irrelevant to the asymmetry (swap ≈ flat, match ≈
flat, strip ≈ flat/grows). Combined with OPX-03 (marker ~0%, preamble ~6%), **each of the enumerated textual differences —
marker, preamble/offset, filler — fails individually to account for the asymmetry.**

**Pre-committed fork (a) (the reviewer, before the run):** BODY-PARTIAL/NULL ⇒ "the enumeration of textual differences is
exhausted on this template; the next candidate is not another text feature but something non-textual about the two positions that
OPX-02's order reversal did not disturb (a slot/structural prior not keyed on visible tokens) — a different class of probe."

**⚠ FLAG (my catch, do not skip to 'non-textual' yet):** OPX-03 and OPX-04 each neutralized features **separately, never
jointly.** STRIP kept the markers + preamble native (removed only the filler); OPX-03's PM kept the filler. So we have shown each
of {marker, preamble, filler} is individually *not* the carrier — **not** that they are jointly not the carrier. A **redundant
textual code** (say the marker AND the filler each independently sufficient) would survive every single-feature neutralization
**and** survive STRIP, exactly as observed, yet collapse only under a **joint** neutralization. Separate survivals do not compose
into joint survival (same family as "two figures agreeing isn't corroboration unless they can fail independently"). **(Retracted:
an earlier draft read STRIP's growth to 116% as the role signal "concentrating on marker/structure." The STRIP length check — same
discipline as SWAP's — shows small but CI-excluding-0 correlations between the strip effect and the removed-token counts
(−0.067 [−0.108,−0.024] total; +0.116 [+0.067,+0.176] differential, r²≈1–3%), so part of the +3.5-nat growth tracks length/offset.
The growth is therefore not clean concentration; STRIP is read only as "does not collapse.")**

**Therefore the decisive next arm is the ALL-TEXTUAL-STRIPPED cell** (marker → neutral **and** preamble stripped **and** filler
stripped, simultaneously — OPX-03's PM ∪ OPX-04's STRIP, on the same harness, cheap):
- collapses → it was a **redundant textual code** distributed across marker/preamble/filler (any one sufficient); enumeration was
  never exhausted, it was *redundant*.
- survives → the textual enumeration is genuinely exhausted and fork (a) fires for real → **non-textual / positional-slot**
  probe class.

Only that arm licenses the "non-textual" reading. Recommend running it before reaching for a positional-structure probe.

## Prediction outcome
- ANCHOR reproduces — HIT.
- **BODY-CARRIES (both callers, MODULAR) — MISSED.** Got BODY-NULL (filler carries none). 4th consecutive OPX miss; flagged in the
  prereg as elimination reasoning, and it missed in the elimination direction — the enumerated features keep individually failing.
  The three-way band worked: this landed cleanly as NULL rather than being argued into a partial win.

## Scope (binding)
Property of these spans/layers/model/battery, normal order, residual overwrite, single model. SWAP/MATCH/STRIP manipulate the
filler with markers+preamble native; they establish the filler is not the individual carrier, **not** that no textual feature is.
The joint-strip arm is required before any non-textual conclusion.
