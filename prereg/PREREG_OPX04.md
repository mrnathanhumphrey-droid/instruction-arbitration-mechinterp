# OPX-04 — Does the block filler/body content carry the role-dominance asymmetry? (filler SWAP)

**LOCKED before run; chained to OPX-03.** Rulings applied (the reviewer, relayed by the lead researcher): length-match =
accept-as-is (a) + report per-item filler-delta vs effect correlation; MATCH filler string accepted + record FN token length;
three-way inversion threshold pre-registered (§4).

**Target.** OPX-01 found a role-dominance asymmetry (raw dY_sys ≈ −7.2, dY_usr ≈ +14.8; A_usr the dominant lever, A_sys weak/
counteracting). OPX-02 showed it is block-anchored, not position/recency (block-order reversal keeps the signs). OPX-03 ruled out
the two named textual features — the role-word **marker** (~0%, CI incl 0) and the system **preamble/offset** (~6%) — leaving
**94% carried by an unenumerated feature.** The one role-differentiated body content the battery never matched or moved is the
**filler**: `fsys` = system-voice framing ("You are assisting with routine office tasks.") vs `fusr` = user-voice content
("Here is a note from my calendar…"), paired by `filler_idx`. OPX-04 tests whether that filler carries the asymmetry.

- chained_to_OPX03_sha256: `ef1e7eb6e76db57e776bae49675ad8b7493df7ea098930ebd4167040a986c4ea`
- runner: `run/opx04/opx04_lambda.py` sha256 `805f27464d4ea1c01674c2bbec647fa4d6825348860870bd60b861ca7524e764`
- model **Llama-3.1-8B-Instruct**; battery **`stimuli_contested.jsonl`**; spans = imperative; layers **L8–31**; DONE/READY;
  normal block order (OPX-02 handled reversal). One-sided same-index span patch from the cb-flip twin (OPX-01's A_sys/A_usr).

## 0. Design principle (the reviewer) — SWAP, not match
A **match** can only *collapse* the asymmetry (it removes a difference), so it is a construction check, not a discriminator —
the lesson PRV-01e taught (perfect-forgery beat wrapper-subtraction). A **swap** *inverts*, and **inversion is a signature no
other cause produces**: OPX-02 established that within-block position/offset only shifts *magnitude* (~5 nats), never flips the
sign structure. So the primary arm swaps the fillers.

## 1. Arms (normal order; markers + imperatives NATIVE; twin surged the SAME way per arm)
- **BASE** — native (sys = imp_sys + fsys, usr = imp_usr + fusr). Anchor; reproduce OPX-01.
- **SWAP (PRIMARY)** — fillers swapped: sys = imp_sys + **fusr**, usr = imp_usr + **fsys**. Role-word markers and imperatives
  stay native. If the filler carries the dominance, the asymmetry **follows the body and inverts**.
- **MATCH (construction check)** — both fillers → one neutral filler `FN` (identical body in both blocks). Can only collapse;
  corroborates a body reading via a second route.
- **STRIP (high-upside)** — no filler (sys = imp_sys, usr = imp_usr; markers + spans only). With marker and preamble already
  ruled out (OPX-03), **survival here leaves almost nothing standing** → enumeration still incomplete, go deeper.

## 2. Discrimination matrix (PRE-LOCK GATE — body separable from every live row on the discriminating arms {SWAP, STRIP})
| candidate | BASE | SWAP | MATCH | STRIP |
|---|---|---|---|---|
| **body content (filler)** | + | **− (inverts)** | 0 (collapse) | 0 (collapse) |
| deeper unenumerated tell | + | ? (unpred.) | survives | **survives** |
| marker/preamble residual (OPX-03 says ~0; shown for completeness) | + | + (stays) | survives | survives |

Gate result (step-zero): body `(−, 0)` on {SWAP, STRIP} is **distinct** from deeper-tell `(?, S)` and residual `(+, S)` →
**PASS**. Inversion at SWAP is unique to body-content; STRIP separates body (collapse) from a deeper tell (survive). MATCH is
collapse-only, so it corroborates but does not discriminate (stated, not used as a discriminating column).

## 3. Quantities — raw ΔY PRIMARY (the gate that bit OPX-02/03)
Surgeries change the baseline B, so the normalized M is not comparable across arms (and can explode when B→0). **Primary = raw
dY** per arm: `dY_sys(arm) = mean(Y_Asys − Y_base)`, `dY_usr(arm) = mean(Y_Ausr − Y_base)`, `raw_asym(arm) = dY_usr − dY_sys`.
**B reported per arm.** M reported for BASE only (advisory; BASE's B is healthy). The three-way threshold key is the signed
ratio **`r = asym_SWAP / asym_BASE`** (BASE asym expected large positive). Secondary: `strip survival = asym_STRIP / asym_BASE`;
`match residual = asym_MATCH` (construction check → ≈ 0). Template-cluster bootstrap CIs (NTMPL=30, BOOT=5000) on all.

**Addition (length check, the reviewer):** with length-match declined, report the **per-item filler token-length |delta|** and its
correlation with the per-item swap move (`asym_BASE_i − asym_SWAP_i`), template-cluster bootstrapped. A near-zero, CI-spanning-0
correlation converts "6 tokens shouldn't matter" into "we checked." Also record fsys/fusr mean lengths and **FN's token length**
against them (§8).

## 4. Mechanical verdict (pre-committed THREE-WAY threshold — the reviewer)
- **ANCHOR (BASE)** reproduces OPX-01 (dY_sys −7.2 ± 2.5, dY_usr +14.8 ± 3.0). Miss ⇒ harness diverged.
- **BODY-CARRIES** — `r ≤ −0.5` (sign flips **and** |asym_SWAP| ≥ 0.5·|asym_BASE|). The filler carries the OPX-01 role-dominance;
  inversion is the unique signature. (SWAP CI-excludes-0 reported as inversion strength.)
- **BODY-PARTIAL** — `|r| ≤ 0.5` (the swap substantially shrinks the asymmetry, sign either way). The body carries a *share*; a
  residual is still unenumerated.
- **BODY-NULL** — `r > 0.5` (sign holds, magnitude preserved). The filler does not carry it; with marker+preamble already ruled
  out, enumeration is still incomplete → go deeper. (STRIP survival + MATCH residual reported as context in every band.)

## 5. Gates
- **G-SEGMENT (tokenizer-only, pre-lock, done):** 720/720 items build all 4 arms for item AND twin; imperative spans locate and
  same-index align in every arm; 0 failures. FN builds (9 tokens). SWAP keeps the within-block span-offset delta unchanged
  (usr−sys median 23 in both BASE and SWAP) → the swap is near offset-neutral.
- **MASS** — m ≥ 0.10 per cell per arm; STRIP renders (bare imperative) are mildly OOD → report per-arm mass + B; forced-readout
  target at runtime if any falls below.
- Counterbalance sign-folded; per-item Y persisted per arm (`opx04_peritem.npz`); SMOKE(40)→FULL(720).

## 6. Scope — binding
Property of these spans/layers/model/battery, normal order, under residual overwrite. SWAP is the discriminator; inversion is the
body signature (offset-robust per OPX-02). MATCH is a construction check. Single model.

## 7. Predictions (labeled by bias-direction honestly — predict-integration-get-separability)
- Anchor reproduces.
- **Both callers' prediction: BODY-CARRIES (SWAP inverts).** The **MODULAR** call (an identifiable textual feature carries it):
  the body is the only textual difference left after marker + preamble, and 94% is unaccounted. **Flagged honestly: this is
  *elimination* reasoning — the mode that has missed three straight OPX calls. The reviewer's least-surprising alternative is
  BODY-PARTIAL.** Recorded so that BODY-NULL (no inversion) counts as a clean miss and BODY-PARTIAL as a partial hit; the
  three-way band exists precisely so a 40% inversion isn't scored a win or a miss by whoever writes the verdict.

## 8. Judgment calls (RESOLVED at lock)
- **Filler length under SWAP → (a) ACCEPT as-is** (the reviewer). Step-zero: within-block span offset preserved 23→23, filler
  |delta| max 6 / mean 2.3; a 6-token max delta can shift magnitude but cannot flip a ~2.8-nat sign, and padding would inject
  tokens present in no natural prompt (we have been burned twice by interventions manufacturing what they measure). **Instead of
  padding: report the per-item filler-delta and check it does not correlate with the swap move** (§3, free from persisted data).
- **MATCH neutral filler `FN` = "The following is a short block of text." → ACCEPTED.** For a collapse-only check, identity is all
  that is required. **FN token length is recorded against fsys/fusr** (FN ≈ 9 tokens is likely shorter than both → MATCH differs
  from BASE in content-identity *and* length; fine if it collapses; if it does not, that record distinguishes a real tell from a
  length artifact instead of guessing).
