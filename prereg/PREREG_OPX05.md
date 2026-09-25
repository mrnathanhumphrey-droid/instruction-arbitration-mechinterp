# OPX-05 — The JOINT STRIP: is the role-dominance asymmetry a redundant textual code, or genuinely non-textual?

**LOCKED before run; chained to OPX-04.** The reviewer's spec (relayed by the lead researcher). First genuine construction check of
the whole textual enumeration.

**Why.** OPX-03 ruled out the marker (~0%) and preamble (~6%); OPX-04 ruled out the filler (BODY-NULL). But each probe neutralized
its feature **separately, never jointly** — OPX-04's STRIP kept marker+preamble native, OPX-03's PM kept the filler. A **redundant
textual code** (≥2 of {marker, preamble, filler} each independently sufficient) survives every single-feature neutralization *and*
survives STRIP, exactly as observed, yet collapses only when all are removed **at once**. Separate survivals do not compose into
joint survival. So the individually-not-the-carrier results do NOT establish the "non-textual" fork; only the joint strip does.

- chained_to_OPX04_sha256: `356ca526d60fe1aa1026d988c778456b2c0cff932486c3eb22c80dc50bbd6248`
- runner: `run/opx05/opx05_lambda.py` sha256 `634c2ecf0efe4798ee7d4a0e7b9ec7d48f9adfc7c7a65b35786d47687a1c4b6c`
- model **Llama-3.1-8B-Instruct**; battery **`stimuli_contested.jsonl`**; spans = imperative; layers **L8–31**; DONE/READY;
  normal block order. One-sided same-index span patch from the cb-flip twin (OPX-01's A_sys/A_usr). NEUTRAL role word = `info`
  (single token, matches OPX-03).

## Units note (reconciled from OPX-04, binding)
The headline asymmetry is **raw ΔY** (`asym = dY_usr − dY_sys`, nats). OPX-01's −0.93/+1.90 were **M** = −ΔY/2B. They are the same
object: `raw_asym / (−2·B_BASE) = M_usr − M_sys` (verified in OPX-04: 21.97/7.80 = +2.816 = 1.892 − (−0.924), and −0.924/+1.892
are OPX-01's values). All OPX-05 bands are unit-free **ratios** to BASE, so the chain identity holds.

## 1. Arms (normal order; markers/preamble/filler surgeries per arm; twin surged the SAME way per arm)
- **BASE** — native. Anchor; reproduce OPX-01 (in M) / OPX-03 BASE (+21.94 raw).
- **PM** — marker → `info` (both headers) + system preamble stripped, **filler kept.** Reproduces **OPX-03 PM in-run.**
- **STRIP** — filler removed (block = imperative only), **markers + preamble native.** Reproduces **OPX-04 STRIP in-run.**
- **JOINT** — marker → `info` + preamble stripped + filler removed, all at once (= PM ∪ STRIP). Both blocks become
  `[info-header][\n\n][imperative]`, identical save order and the imperative's target word. **All textual differences gone.**

## 2. Quantities — raw ΔY PRIMARY (surgeries change B; the OPX-02/03 lesson)
`dY_sys(arm)=mean(Y_Asys−Y_base)`, `dY_usr(arm)=mean(Y_Ausr−Y_base)`, `raw_asym(arm)=dY_usr−dY_sys`. **B reported per arm.** M
for BASE only (advisory). **KEY = r = asym_JOINT / asym_BASE.** Secondary/reproduction: `asym_PM/asym_BASE` (vs OPX-03's PM 94%),
`asym_STRIP/asym_BASE` (vs OPX-04's STRIP 116%). Template-cluster bootstrap CIs (NTMPL=30, BOOT=5000).

**Length check (carried from OPX-04):** JOINT removes filler + preamble, so tokens/offsets move most here. Report the correlation
of the per-item JOINT effect (`asym_JOINT_i − asym_BASE_i`) with removed-token counts (total fsys+fusr; differential fusr−fsys),
template-cluster bootstrapped. Interpret r only after seeing whether length explains it.

## 3. Mechanical verdict — PRE-REGISTERED BANDS on r = asym_JOINT / asym_BASE (the reviewer)
- **ANCHOR (BASE)** reproduces OPX-01 (dY_sys −7.2 ± 2.5, dY_usr +14.8 ± 3.0). Miss ⇒ harness diverged.
- **r ≤ 0.25 → REDUNDANT-TEXTUAL-CODE.** Joint strip collapses it; marker/preamble/filler are a redundant textual code (≥2 each
  sufficient); each single neutralization survived only because the others remained. Enumeration was **redundant, not exhausted**
  → the non-textual fork does **not** fire.
- **0.25 < r ≤ 0.75 → PARTIAL.** Some of the asymmetry is jointly textual; a residual survives all textual neutralization and is
  the part that goes to the non-textual/positional class. (Keeps both branches alive.)
- **r > 0.75 → TEXTUAL-EXHAUSTED.** Survives the joint strip → textual enumeration genuinely exhausted → fork (a) fires →
  non-textual / positional-slot probe class.

## 4. What a collapse would mean (context, not a gate)
If REDUNDANT-TEXTUAL-CODE, redundancy has now appeared at a **fourth** level of this system — regional (RES-06), role/serialization
saturation (TOOL 2×2), deflation subspaces (PRV-01h-r), and now the block's textual features. Four independent levels, same
structure ⇒ redundancy becomes the most robust cross-level regularity in the program, a larger claim than the locus hunt. (Stated
so the reading isn't invented in the moment; it is not a gate.)

## 5. Gates
- **G-SEGMENT (tokenizer-only, pre-lock, done):** 720/720 build all 4 arms for item AND twin; spans locate + same-index align; 0
  failures. NEUTRAL `info` = 1 token. Structural check (item 0): BASE [sys-marker, filler, preamble], PM [info-marker, filler, no
  preamble], STRIP [sys-marker, no filler, preamble], JOINT [info-marker, no filler, no preamble, 29 tok]. ✓
- **MASS** — m ≥ 0.10 per cell per arm; JOINT/STRIP renders are the most OOD → report per-arm mass + B; forced-readout target at
  runtime if any falls below.
- Counterbalance sign-folded; per-item Y persisted per arm (`opx05_peritem.npz`); SMOKE(40)→FULL(720).

## 6. Scope — binding
Property of these spans/layers/model/battery, normal order, under residual overwrite. JOINT is the first genuine construction
check of the textual enumeration; its collapse means "redundant textual code," its survival means "non-textual," per the bands.
PM/STRIP reproduce OPX-03/04 in-run (independent-reproduction check). Single model.

## 7. Predictions (labeled by bias-direction honestly — predict-integration-get-separability)
- Anchor reproduces; PM ≈ 94% and STRIP ≈ 116% reproduce OPX-03/04.
- **Both callers: REDUNDANT-TEXTUAL-CODE (collapse).** Flagged: this is the **same elimination-flavored reasoning that has missed
  four straight** — the enumerated features keep individually failing. The reviewer's least-surprising outcome is **PARTIAL**, which
  keeps both branches alive. Recorded so PARTIAL scores as a partial hit and TEXTUAL-EXHAUSTED as a clean miss.
