# VERDICT — OPX-05: joint strip — is the role-dominance asymmetry a redundant lexical code or outside the lexical enumeration?

**Verdict (mechanical): TEXTUAL-EXHAUSTED.** Removing every lexical difference between the two blocks at once — role-word marker →
`info`, system preamble stripped, and filler removed, so both blocks are `[info-header][\n\n][imperative]` (identical save order and
the imperative's counterbalanced target word) — leaves **90% of the asymmetry intact** (r = asym_JOINT/asym_BASE = **0.904
[0.843, 0.964]** > 0.75). Per the pre-committed bands the lexical enumeration is genuinely **exhausted**: the carrier is **not any
lexical feature of the blocks** (no word or wrapper carries it). Fork (a) fires → the next probe class is **positional/slot.** Both
callers predicted REDUNDANT-TEXTUAL-CODE (collapse) — **5th consecutive OPX prediction miss**, and the miss is the finding: it rules
out the entire lexical enumeration in one construction check.

**⚠ Wording (binding): "outside the lexical enumeration," NOT "non-textual."** Nothing is outside the prompt. The remaining
block-distinguishing features are block order and the counterbalanced target, and position is realized through token index, which the
text determines. OPX-05 shows the carrier is not *lexical* (no word/wrapper); it does not show it is "non-textual." Use "not lexical
/ outside the lexical enumeration" everywhere this reaches a page — "non-textual" invites a reading the data does not support.

- prereg: `PREREG_OPX05.md` sha256 `e110307e317778e9ae9a3cd2f81c6dd9a5ce49ad8bb436ac7ae01b7eb890079c` (chained OPX-04
  `356ca526…`); runner sha256 `634c2ecf0efe4798ee7d4a0e7b9ec7d48f9adfc7c7a65b35786d47687a1c4b6c`
- run: gh200-class @ Lambda, FULL n=720, $0.31, terminated clean, no orphan. `run/opx05/results/opx05.json` + `_arms.csv` +
  `_peritem.npz`.

## Raw ΔY (nats) per arm — primary (B varies/collapses per arm; raw dY is the discriminator)
| arm | dY_sys | dY_usr | raw asym | frac of BASE | B | mass |
|---|---|---|---|---|---|---|
| BASE (native) | −7.21 | +14.76 | **+21.97 [19.48, 24.29]** | 1.00 | −3.90 | 0.63 |
| PM (marker→info + preamble stripped, filler kept) | −11.86 | +8.72 | **+20.58 [18.67, 22.32]** | **0.937** | +1.32 | 0.65 |
| STRIP (filler removed, marker+preamble native) | −5.91 | +19.58 | **+25.48 [21.01, 29.68]** | **1.160** | −7.10 | 0.79 |
| JOINT (all three at once) | −9.65 | +10.20 | **+19.85 [17.26, 22.38]** | **0.904** | −0.72 | 0.71 |

- **r = asym_JOINT / asym_BASE = 0.904 [0.843, 0.964]** → **TEXTUAL-EXHAUSTED** (§3: r > 0.75).
- **In-run reproductions (independent-reproduction check):** PM = **93.7%** reproduces OPX-03's PM (94%, raw +20.57 → here +20.58);
  STRIP = **116.0%** reproduces OPX-04's STRIP (116%, +25.48 both). Two prior results reproduced in one fresh run — they could have
  failed independently and did not.

## Gates
- **ANCHOR ✓** BASE reproduces OPX-01 in M units: M_A_sys −0.924, M_A_usr +1.892 (= OPX-01 −0.93/+1.90); raw asym +21.97 =
  M-asym +2.816 × (−2·B). anchor=True.
- **LENGTH CHECK (carried from OPX-04)** corr(JOINT effect, total removed) = **−0.097 [−0.163, −0.032]**, corr(differential) =
  **+0.168 [+0.095, +0.244]** — both CIs exclude 0 but small (r² ≤ ~6%). They attach to the small JOINT *effect* (the ~10% drop,
  −2.1 nats), not to the 90% that survives; the survival is not a length artifact.
- **MASS ✓** 0.63–0.79 all arms. **B note:** PM's B flips to +1.32 and JOINT's collapses to −0.72 — precisely why raw ΔY, not M,
  is primary here (normalized-effect-needs-a-stable-denominator).

## Counterbalance split — is the asymmetry target-bound? (free re-analysis, the reviewer) — NO
The standing counterbalance gate validates the *estimator*; it never asked whether the *asymmetry itself* holds with the same sign
in both halves. If the −0.93/+1.90 lived in one counterbalance half, it would be a **target** asymmetry (DONE-vs-READY) wearing a
role label — and the target word is the one thing no arm ever removed. Split of asym (Yu−Ys, obeys-system units) by counterbalance,
same persisted per-item Y:

| arm | DONEsys asym | READYsys asym | diff (D−R) |
|---|---|---|---|
| BASE | +21.49 [18.99, 23.87] | +22.44 [19.95, 24.76] | −0.94 [−1.23, −0.67] |
| PM | +20.38 | +20.77 | −0.39 [−0.59, −0.19] |
| STRIP | +25.00 | +25.97 | −0.98 [−1.70, −0.27] |
| JOINT | +19.86 [17.27, 22.39] | +19.85 [17.24, 22.44] | **+0.01 [−0.63, +0.66]** |

**Same sign, comparable magnitude in both halves for every arm, and in JOINT the two halves are identical (diff +0.01, CI spans
0).** The asymmetry is **not target-bound** — target-bound is refuted. The small BASE/PM/STRIP diffs (~0.4–1.0 nats ≈ 2–4%,
CIs exclude 0) are a minor **target modulation of magnitude** that is present with lexical content and **vanishes under the joint
strip** — magnitude, not structure (the same "these features move magnitude, not the structural asymmetry" pattern as offset/length).
This clears the object for publication: what the five runs measured is a structural role/position asymmetry, not a renamed target
effect.

## Reading (the lead researcher's step; facts above)
- **The role-dominance asymmetry is not lexical (it is outside the lexical enumeration).** Every enumerated lexical difference —
  marker (OPX-03 ~0%), preamble (OPX-03 ~6%), filler (OPX-04 BODY-NULL) — removed *simultaneously* leaves 90% intact, and the
  counterbalance split rules out the target word too. This is not a redundant lexical code (that would have collapsed under the
  joint strip); the individually-survives results were not redundancy — the carrier sits outside the lexical enumeration.
- **The escaping thing may be a design feature, not a prompt feature (the reviewer).** Every enumeration this program has built has
  been of *prompt/lexical* features; the counterbalance check is the first look at a property of *how the contrast was constructed*.
  It came back clean (not the target), which leaves block **order/position** as the remaining constructed distinction — and that is
  what the next probe tests.
- **⚠ The tension to resolve (this is what the next probe is for).** After JOINT the two blocks are token-identical except (i)
  order and (ii) the imperative's target word (DONE/READY, counterbalanced + sign-folded, so it cancels). OPX-02 already showed
  the asymmetry is **not** simple position/recency — order reversal kept the signs with the roles. But OPX-02 had the role markers
  present. **With the markers gone (JOINT) the only surviving block-distinguishing feature is position/slot.** So the two results
  compose into a sharp hypothesis: the effect OPX-02 read as "role-bound" may be **marker-mediated position** — role marker present
  ⇒ tracks role; marker absent ⇒ falls back to the underlying positional/slot structure. Or there is a genuine slot prior in the
  KV/positional structure that survives both marker removal and order reversal. These are distinguishable.
- **Decisive next probe (fork a, positional/slot class): the JOINT strip under reversed block order** (OPX-05 arms × ORD-01
  flip). If dominance follows absolute position (later span dominant regardless of original assignment) → it was positional all
  along, marker-relabeled; reconcile OPX-02 accordingly. If it still tracks the original assignment with no marker and flipped
  order → a genuine structural slot prior. Either is a bigger result than a textual carrier.

## Prediction outcome
- ANCHOR reproduces; PM 94% and STRIP 116% reproduce OPX-03/04 in-run — HIT.
- **REDUNDANT-TEXTUAL-CODE (both callers, collapse) — MISSED.** Got TEXTUAL-EXHAUSTED (90% survives). 5th straight OPX miss, all
  in the elimination-of-enumerated-carriers direction; the pre-registered bands made the survival land cleanly as EXHAUSTED rather
  than being argued down. The cumulative truth: the carrier is neither the exchange operator, nor recency, nor the marker, nor the
  preamble, nor the filler, nor the target word — it is outside the lexical enumeration (positional/slot), and it is what every
  locus probe has been circling.

## Scope (binding)
Property of these spans/layers/model/battery, normal order, under residual overwrite, single model. JOINT is the first genuine
construction check of the lexical enumeration; its survival establishes non-lexical carriage on *this* template, not a mechanism.
The counterbalance split additionally rules out the target word. The positional-vs-slot question is open and is the next probe.
PM/STRIP reproduce OPX-03/04 in-run. The positional-vs-slot question is open and is the next probe.
