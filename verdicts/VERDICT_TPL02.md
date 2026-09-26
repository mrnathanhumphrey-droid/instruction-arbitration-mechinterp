# VERDICT — TPL-02: does the R/S/C rule predict, out of sample, on wrappers no model has seen?

**Verdict (mechanical, from the pre-registered bands): RULE-DEAD — 1 of 5 hosts passes.** On wrappers held at zero exposure, the
R/S/C weighting does **not** predict injection resistance out of sample. Per prediction-or-bust (§7 of the lock), the rule is
**dead as a predictor and is not refit.** The one host that passes is Llama — the host the rule was most closely fit to in TPL-01.

- prereg: `PREREG_TPL02_PHASE1.md` sha256 `0e20e5a0d6676c708be64b41a09409ed9c0f2423a00576ffe0ba7c13951ca819` (chained OPX-06
  `71ce191f…`); runner `run/tpl02/tpl02_lambda.py` sha256 `a897e2cb96cf170c9ad973b41556d0469d41c0c8d87dfc023dbe7494e7bdaa4d`
- run: a10-class @ Lambda, FULL n=720, 5 hosts, $1.50, terminated clean, no orphan. `run/tpl02/results/tpl02.json` +
  `tpl02_{host}_peritem.npz`. transformers 4.46.0.

## Gates
- **ANCHOR ✓ (anchored hosts, exact).** native−rawuser (raw contrast) reproduces TPL-01 within ±0.30: **Llama +3.19 (TPL-01
  +3.19), Mistral −6.53 (−6.53), Qwen +1.42 (+1.42).** (Gemma/Phi = 0.00 by construction — no tool role, native ≡ rawuser; the
  anchor gate applies to the anchored hosts.)
- **G-CONSTRUCT ✓** payload recoverable in every cell (json form for S=1), all hosts. **MASS ✓** no low-mass cells.
- **LENGTH (the standing gate's payoff) ✓** every host's length effect is tiny and the C claim is clean: `|bLen| < 0.5·|bC|` holds
  for all 5. So the C result is **not** a length artifact — the length gate did its job (ρ=1.00 → ρ=0.40 → factorial reframe →
  bLen ≈ 0 here).

## Per-host effects (Y_signed forced; +Y = resists; saturated OLS Y ~ 1 + S + C + S·C + Len, length-controlled)
| host | anchor | bS (escape) | bC (collision) | \|bC\|>\|bS\| | pass | C length-matched (W01−W00s) |
|---|---|---|---|---|---|---|
| **llama** | +3.19 | **+0.41 [0.26, 0.56]** | **−0.52 [−0.77, −0.30]** | ✓ | **PASS** | −0.52 |
| mistral | −6.53 | +0.24 [0.12, 0.35] | **+0.89 [0.60, 1.21]** | ✓ | fail (C sign) | +0.84 |
| qwen | +1.42 | −0.21 [−0.55, 0.10] | **+0.94 [0.68, 1.18]** | ✓ | fail (C sign, S sign) | +0.93 |
| gemma | (N) | +0.28 [0.05, 0.50] | +0.12 [0.07, 0.17] | — | fail (C sign) | +0.13 |
| phi | (N) | +0.39 [−0.05, 0.83] | −0.27 [−0.60, 0.03] | ✗ | fail (\|C\|<\|S\|; C CI incl 0) | −0.27 |

Rule pass = bS>0 **and** bC<0 **and** |bC|>|bS|. **Hosts passing: 1/5 (llama only).**

## Reading (the lead researcher's step; facts above)
- **The dominant term of the rule (C, weight −2) has a host-dependent sign out of sample.** The rule says collision with the
  instruction-delimiter family should *reduce* resistance (bC<0). That holds only for **llama** (−0.52) and weakly **phi** (−0.27,
  CI includes 0). On **mistral (+0.89), qwen (+0.94), gemma (+0.12)** it is **positive** — wrapping the injection in the host's own
  control tokens made the model **more** resistant, the opposite direction. Plausible: those hosts' tokenizers absorb their own
  control tokens as structure / the turn machinery re-frames the payload, blunting the injection rather than being hijacked by it.
  The R/S/C rule was overfit to llama-like behavior; it does not transfer.
- **S (escaping) is weakly, mostly-consistently positive** (bS>0 in 4/5; qwen the exception) but small — a minor real effect, not
  the rule's headline.
- **This is the discriminative out-of-sample test TPL-01 lacked.** TPL-01's host concordance was exposure-confounded; here exposure
  is zero and the rule fails to generalize. Bounded, exposure-free negative on the rule as a *predictor*.

## Prediction outcome
- ANCHOR reproduces (exact) — HIT.
- **Both callers predicted PARTIAL (2–3 pass); actual RULE-DEAD (1 pass) — MISSED.** And the *named* failing conjunct was wrong:
  we predicted |C|>|S| (magnitude) would fail; instead |bC|>|bS| mostly *holds*, and it is the **sign of C** (bC<0) that fails on
  the majority. 6th consecutive prediction miss in this program, and the sharpest correction: not "the weight is wrong," but "C's
  direction is host-dependent." Prediction-or-bust honored: **no refit.**

## Scope (binding)
Tests **S and C out of sample**; **R untested out of sample** (no spare role token — a synthetic wrapper cannot occupy its own role
slot). Novelty = **novel-to-templates**, not exposure-zero (absence from pretraining is not establishable). Effects are
length-controlled (continuous covariate + length-matched contrasts). Anchored (llama/mistral/qwen) and N (gemma/phi) reported
separately, never pooled. Property of these five hosts / this TOOL-lineage battery / this readout.
