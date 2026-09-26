# OPX-06 — Does removing the marker make block order matter? (marker × order, 2×2 completion)

**LOCKED before run; chained to OPX-05.** The reviewer's spec (relayed by the lead researcher). Composes OPX-05's JOINT surgery
with OPX-02/ORD-01's block-order flip.

**Frame.** After the joint strip there is no slot identity independent of order, so "order vs slot" has no second hypothesis. This
is framed as the **fourth cell of a marker × order 2×2**: (marker+, normal) = OPX-01/05 BASE; (marker+, reversed) = OPX-02
flipped; (marker−, normal) = OPX-05 JOINT; **(marker−, reversed) = the one new cell.**

- chained_to_OPX05_sha256: `e110307e317778e9ae9a3cd2f81c6dd9a5ce49ad8bb436ac7ae01b7eb890079c`
- runner: `run/opx06/opx06_lambda.py` sha256 `6d2db0e4667669384fb6744772a4ca05428b990ab2bae567c32780256524076d`
- model **Llama-3.1-8B-Instruct**; battery **`stimuli_contested.jsonl`**; spans = imperative; layers **L8–31**; DONE/READY;
  one-sided same-index span patch (A_sys, A_usr) from the cb-flip twin. NEUTRAL role word = `info`.

## 1. Cells (2×2 = MODE {BASE, JOINT} × ORDER {normal, reversed}); asym = dY_usr − dY_sys (raw)
- **BASE normal** — native anchor (reproduces OPX-01/05 BASE).
- **JOINT normal** — marker→`info` + preamble stripped + filler stripped (reproduces OPX-05 JOINT; the q-denominator + anchor).
- **JOINT reversed** — JOINT under reversed block order (ORD-01 flip: pre + user-blk + system-blk + assistant, spans remapped by
  o2n). **The one new cell.**
- **BASE reversed** — native under reversed order (reproduces OPX-02's flip; the marker-present reference). *Judgment call: included
  to complete the literal 2×2 and reproduce OPX-02 in-run (independent corroboration); the spec named only the new cell + JOINT-n
  anchor. Flagged; cheap.*

## 2. Primary quantity — raw ΔY MANDATORY (B collapsed to −0.72 at JOINT; M uninterpretable)
**`q = asym_JOINT_reversed / asym_JOINT_normal`.** B reported per cell as a diagnostic. Template-cluster bootstrap CIs (NTMPL=30,
BOOT=5000).

## 3. Mechanical verdict — PRE-REGISTERED BANDS on q (the reviewer)
- **ANCHOR** — asym_JOINT_normal / asym_BASE_normal reproduces OPX-05's 0.904 within ±0.05. Miss ⇒ harness diverged.
- **q ≤ −0.50 → MARKER-MEDIATED POSITION.** With the marker present the asymmetry pinned to the block (OPX-02); strip it and the
  asymmetry falls back to position (reversal inverts it). Clean, and it reconciles OPX-02 with OPX-05.
- **|q| ≤ 0.50 → ORDER-DESTROYS.** Reversal kills the asymmetry without inverting it — a third thing. Report the curve, no headline.
- **q > 0.50 → NO-FLIP.** Neither marker nor position, and the counterbalance split already excluded the target. **Nothing in the
  PROMPT distinguishes the two blocks**, so the asymmetry is a property of the **patching operation** — how A_sys and A_usr are
  constructed, not what they act on.

## 4. The NO-FLIP branch points at the DESIGN, not a slot prior (pre-registered so the reading isn't negotiated after the number)
If q > 0.50 there is **no slot left** to be a prior — the joint strip removed everything textual and the counterbalance split
removed the target. The honest consequence is that **the OPX chain's subject needs renaming**: "role asymmetry" would be a property
of the *contrast's construction* (an instrument), and the five runs would have been characterising that instrument. It must **not**
be read as "a slot prior." If NO-FLIP lands, the next probe is not another prompt feature — it is the operation itself, starting
with whether A_sys and A_usr are symmetric in what they **source** and where they **write**.

## 5. Disambiguating a flip (q ≤ −0.50): position vs target × position
A flip is ambiguous because position and target are yoked at JOINT. **Compute q within each counterbalance half separately**
(persisted per-item Y, cb label). Holds in both halves → **position**. Appears in one half only → **target × position interaction**,
and the verdict says so.

## 6. Gates
- **CONSTRUCTION (tokenizer-only, pre-lock, done):** the reversed JOINT render is token-identical to normal under permutation of the
  two blocks — multiset-identical **720/720**, the two JOINT blocks equal length (clean symmetric swap) **720/720**, span remap
  exact **720/720**. All 4 cells build + span-align to twin **720/720**. NEUTRAL `info` = 1 token. (BASE blocks are asymmetric
  40 vs 26 — the OPX-02 reordering case — as expected; JOINT is 12==12.)
- **RAW-ΔY MANDATORY** — B per cell diagnostic; no M (normalized-effect-needs-a-stable-denominator).
- **MASS** — m ≥ 0.10 per cell; runtime forced-readout target if not.
- **TWIN VOID** inherited; counterbalance split within each order; per-item ΔY/m/B persisted; SMOKE(40)→FULL(720).

## 7. Scope — binding
Property of these spans/layers/model/battery. q with pre-registered bands; NO-FLIP points at the patching operation
(design/instrument), never a slot prior (no slot survives the joint strip). Flip disambiguated position-vs-target×position by
per-counterbalance-half q. BASE-n/JOINT-n reproduce OPX-01/05; BASE-f reproduces OPX-02 (role-keep) in-run.

## 8. Prediction (regime, from the degeneracy analysis, not elimination — the reviewer)
**NO-FLIP (q > 0.50).** Reasoning: OPX-02 showed position doesn't govern with markers present, and at JOINT the blocks are
token-symmetric apart from the target, which is already excluded. A ~20-nat asymmetry between two near-identical blocks, unmoved by
every prompt feature, is more consistent with the construction of A_sys/A_usr than with anything in the text. **Predicted against: a
clean inversion (MARKER-MEDIATED POSITION).** (Note: five straight OPX predictions have missed; this one is reasoned from the
degeneracy, not elimination, but is logged with the same honesty — the bands make PARTIAL/DESTROYS outcomes score cleanly.)
