# OPX-07 — Does the role MARKER mediate the ANCHORING (not the magnitude)?

**DRAFT — NOT YET SEALED (no sidecar).** Design ratified by the reviewer (4th arm added, two gates added, all four attacks closed at
step-zero). Bring to seal. Chains to TPL-02 Phase-1 once sealed.

**The gap.** OPX-02: *with* role markers the span-flip asymmetry is **block-anchored** (keeps sign under order reversal). OPX-03: the
marker carries **~0% of the normal-order magnitude**. OPX-06: tried the no-marker order test but was **degenerate** (full strip → flip
= twin). Untested: **does the marker mediate the *anchoring* — the order-reversal invariance — even though it carries ~none of the
magnitude?** Magnitude ≠ anchoring; that dissociation is the finding-shaped question.

- runner: `run/opx07/opx07_lambda.py` sha256 `8af333744d6843a7a2b0d250b15df9fc0300072181e5696f94f71943eb700fc4`
- model **Llama-3.1-8B-Instruct**; battery `stimuli_contested.jsonl`; spans = imperative; layers **L8–31**; DONE/READY; one-sided
  same-index A_sys/A_usr span patch from the cb-flip twin; normal + flipped block order.

## 1. Arms (content + filler KEPT in all → blocks stay distinguishable → flip ≠ twin → NON-DEGENERATE)
- **ROLE** — native `system`/`user` (reproduce OPX-02; expect keep).
- **NSAME** — both role words → `info` (marker distinctness removed; content + preamble still distinguish).
- **NDIST** — `system`→`alpha`, `user`→`beta` (distinct but role-agnostic labels).
- **NSTRIP** — NSAME **+ system preamble stripped**, content kept. *Required (the reviewer): without it, preamble-mediated and
  content-mediated are the identical row (keep,keep,keep) and a NSAME-keeps result is uninterpretable. NSTRIP is the cell that
  falsifies "content binds."*

## 2. Discrimination matrix (PRE-LOCK GATE — 4 rows distinct across arms; verified PASS)
| mechanism | ROLE | NSAME | NDIST | NSTRIP |
|---|---|---|---|---|
| role-semantic (role words specifically) | keep | swap | swap | swap |
| symmetry-breaking (any distinct label) | keep | swap | keep | swap |
| preamble-mediated (system preamble) | keep | keep | keep | **swap** |
| content-mediated (block content/filler; marker irrelevant) | keep | keep | keep | **keep** |

## 3. Quantities & discriminator — raw ΔY (B flips with order)
Per arm/order: `dY_sys = mean(Y_Asys − Y_base)`, `dY_usr = mean(Y_Ausr − Y_base)`; `asym = dY_usr − dY_sys`. B reported per arm/order.
Per arm: **signs_keep** = sign(dY_sys) and sign(dY_usr) unchanged across orders (**block-anchored**); **signs_swap** = they exchange
(system-effect@flipped ≈ user-effect@normal etc.) = **position-follow**. Template-cluster bootstrap CIs (NTMPL=30, BOOT=5000).

## 4. SIGN-DETERMINACY gate (the reviewer) — an arm is readable only if its signs are determinate
For each arm: **|dY_sys| and |dY_usr| CIs (both orders) exclude 0, AND each |dY| ≥ 3 × nuisance**, where
`nuisance = 0.06 × |asym_ROLE_normal|` (the OPX-03 offset/preamble share). An arm failing this reports **INDETERMINATE**, not
keep/swap — this catches a neutralized marker collapsing an arm's magnitude toward zero and turning sign into noise (the real risk a
keep/swap table would otherwise hide).

## 5. Gates (step-zero, tokenizer-only — DONE, all pass)
- **NON-DEGENERACY (the OPX-06 trap, checked first)** — `flip(item) == twin(normal)` in **0/720** for all four arms; non-degenerate
  *because* content is kept. **NEAR-MISS** — `flip(item) == normal(item)` in **0/720** (A_sys@flipped and A_usr@normal patch the same
  position but are token-distinct). **OFFSET (attack 3 closed)** — `system/user/info/alpha/beta` all single-token → marker surgery
  shifts the span start by **0/720** (NSAME/NDIST vs ROLE); NSTRIP shifts intentionally (preamble removed). **SPAN-ALIGN** 720/720 all
  arms; **discrimination matrix** 4 rows distinct → PASS.
- **ANCHOR (at run)** — ROLE reproduces OPX-02 (outcome = keep). Miss ⇒ harness diverged, flagged.
- **MASS** — m ≥ 0.10 per cell; runtime forced-readout target if not.
- No metric is construction-fixed: the keep/swap outcome is four independently measured signs with no summation identity (OPX-01
  additivity was a finding, gap 0.032, not an identity).

## 6. Scope — binding
Property of these spans/layers/model/battery, single model. Tests whether the marker mediates *anchoring*; does not relocate
arbitration. INDETERMINATE arms are reported as such, never forced to keep/swap.

## 7. Prediction (labeled by bias-direction; 7th call after six misses, weighted lightly — predict-integration-get-separability)
- **My call: CONTENT-MEDIATED (NSTRIP keeps)** — marker at ~0% of magnitude (OPX-03) and content is present in every arm, so I bet the
  anchoring rides on content, not the marker. (This is the diffuse/"marker doesn't matter" direction, against my usual clean-carrier bias.)
- **The reviewer's least-surprising alternative: PREAMBLE-MEDIATED (NSTRIP swaps)** — the preamble is the only asymmetric structural
  feature and the only lexical feature with a **non-zero** share in the whole enumeration (~6%, OPX-03), so if any single feature
  mediates, it has the prior. NSTRIP is what makes both branches readable.
- Against: ROLE-SEMANTIC (would need NSAME to swap).
