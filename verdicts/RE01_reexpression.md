# RE-01 — re-expression forced by ORD-01: retire normalized M, report raw ΔY (order-tagged)

**Trigger:** ORD-01 showed the baseline B is recency-dominant (B flips sign with block order), so M = −ΔY/2B divides by a
denominator whose composition changes with order. A ratio to such a denominator can't be fixed by re-normalizing — it is
replaced by the quantity actually measured: **raw ΔY in nats, order-tagged, with B reported per order as its own
descriptive number.** No re-runs — ΔY is persisted per-item from RES-02 on, and recoverable elsewhere as ΔY = −2·M·B at
normal order.

## Baseline decomposition (ORD-01)
B_normal = −3.879, B_flipped = +1.639. Order-symmetric split: **role = (Bn+Bf)/2 = −1.12 nats**, **recency = (Bn−Bf)/2 =
−2.76 nats**. So the benign contest baseline is ~71% recency (obey the last block) / ~29% role. **2·|role| = 2.24 nats.**

## Raw ΔY (nats), order-tagged  [ΔY = −2·M·B]
| operation | ΔY normal | ΔY flipped | note |
|---|---|---|---|
| cross-role **exchange** (span) | **+3.58** | **−0.66** | order-asymmetric 5× → rides recency |
| **twin-patch** (span) | +7.73 | −3.28 | content flip, position-matched |
| twin-patch (all positions) | +7.76 (=2\|B\|) | — | = run the twin (construction) |
| marker cross-role (RES-04) | +0.71 | — | |
| twin-patch marker K (RES-06) | +3.98 | — | |
| same-role disruption floor (RES-02) | +0.31 | — | |

## The inconsistency that forced the re-expression, and its resolution
- **Exchange moves +3.58 nats > 2·|role| = 2.24.** An intervention can't move more of the role component than exists, so
  cross-role exchange was never isolating role/provenance. Second, independent tell: exchange is **order-asymmetric**
  (+3.58 normal vs −0.66 flipped) — a pure-provenance edit would be order-invariant.
- **Mechanism (verified against `data/make_stimuli.py`):** each item's system and user blocks carry the SAME imperative
  phrasing, differing only in the target word and which slot holds it. RES-02 exchange installs the twin's *opposite-slot*
  span — the SAME imperative text — so it does NOT change which imperative sits in which block. What it swaps is the
  residual's **block-context / positional / recency signature**. Because behavior is recency-dominated (ORD-01), that is
  the channel exchange's ΔY rides — which is why it exceeds the role budget. Content (the imperative text) is preserved;
  the recency signature is what moved.
- **Twin-patch is a different counterfactual:** it installs the twin's *same-slot* span (a different imperative text,
  system-span DONE→READY) at the matched position — a *content flip*, not a signature swap. So exchange and twin-patch
  vary different things and share no controlled variable. **The "arbitration is ~half provenance-movable, ~half
  content-bound" 50/50 split loses its premise** (not just its denominator): "content half = twin − exchange" was never a
  valid subtraction.

## Headline (what this program's cleanest result now is)
- **Recency beats role** (ORD-01): flip the block order and the sign of B flips; role ≈ −1.12 nats, recency ≈ −2.76 nats,
  on a content-matched battery, in nats. A security-relevant fact about the instruction hierarchy in this model.
- **Representation is position-independent; behavior is position-dominated.** RES-01b decoded provenance at 0.89–0.95 with
  absolute position matched; ORD-01 flips the order and ~71% of the behavioral effect goes with it. Same model, same
  battery, opposite answers depending on whether you ask the probe or the output — the **third and cleanest instance of
  representation ≠ causation** in the program, and the only one that needs no normalized ratio to state.

## What survives / what is retracted
- **Survives:** provenance richly represented + position-independent (RES-01); estimator unbiased (CAL-01); exchange
  operation coherent (DIST-01); the measured ΔY pair (order-tagged, above); twin-patch content flip ≈ 2|B|; recency-beats-
  role.
- **Retracted / rescoped:** normalized M as a cross-order "fraction of the arbitration"; the 50/50 provenance/content
  split (premise gone); any statement of a single provenance fraction.

## Going-forward rule
Raw ΔY in nats, **order-tagged**, is the primary quantity. B is reported per order as a descriptive baseline, never as a
universal denominator. M may appear only as a within-order descriptive convenience, always with its order and B stated.
Every effect names its order. feedback_the_numbers_resolution_must_match_the_decisions / unit_of_independence.
