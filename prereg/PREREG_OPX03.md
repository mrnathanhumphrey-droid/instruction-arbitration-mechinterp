# OPX-03 — Which textual feature carries the role-dominance asymmetry: the marker, or the preamble/offset?

**Feature-attribution of the OPX-01/02 asymmetry (A_sys −0.93 / A_usr +1.90, shown role-bound not recency-bound by OPX-02).**
The reviewer's spec (relayed by the lead researcher). **Locked before run; chained to OPX-02.**

- chained_to_OPX02_sha256: `bce394380057a6811512d84dbcdf5634c5e7590c816cfe303299df1b99db0d82`
- runner: `run/opx03/opx03_lambda.py` sha256 `6670794eff01d9ae0dbda92ce92ed066fd6505acf5c75f3bb2f779a29b4a0877`
- model: **Llama-3.1-8B-Instruct**; battery **`stimuli_contested.jsonl`**; spans = imperative; layers **L8–31**; DONE/READY;
  normal block order only (OPX-02 handled reversal). One-sided same-index span patch from the cb-flip twin (OPX-01's A_sys/A_usr).

## 0. Candidates (textual features; "training prior" is the EXPLANATION for whichever wins, not a row — the reviewer)
- **marker** — the role-word header token (`system`/`user`).
- **preamble / within-block offset** — Llama-3.1 injects a date preamble into the **system block only**, which also pushes the
  system span **deeper into its block** than the user span (different within-block offset). One feature, two faces.
- (content-asymmetry KILLED by step-zero: phrasing identical, span len sys 6.40==usr 6.40, target counterbalanced 360/360;
  position-in-prompt KILLED by OPX-02 order-reversal.)

## 1. Arms (normal order; twin surged the SAME way per arm)
- **(i) BASE** — as OPX-01 (anchor; A_sys ≈ −0.93, A_usr ≈ +1.90).
- **(ii) NEUTRAL** — both role-word header tokens → a single neutral word (`info`, verified single-token pre-lock); markers
  indistinguishable between blocks.
- **(iii) PM** — NEUTRAL **plus the system date preamble stripped**, so both blocks are structurally identical
  (`[header][\n\n][content]`, matched within-block offset). **CONSTRUCTION CHECK** (the reviewer): once marker + preamble are gone the
  two blocks are token-identical save order (OPX-02-killed), so there is nothing left for a "prior" to key on. asym should
  collapse to ~0. **Survival at PM ⇒ the enumeration is incomplete (an unlisted tell), NOT a slot prior — go find the tell;
  failure does not license a conclusion.**

## 2. Discrimination matrix (PRE-LOCK GATE — no two rows identical across arms)
| feature | (i) BASE | (ii) NEUTRAL | (iii) PM |
|---|---|---|---|
| **marker** | asym present | **asym shrinks** (marker gone) | gone |
| **preamble / offset** | asym present | asym **persists** (marker gone, preamble remains) | **gone** (preamble stripped) |
Rows differ at column (ii) → **the arms discriminate marker from preamble** ✓. Arm (iii) is the construction check, not a
discriminating column.

## 3. Quantities
`asym(arm) = M(A_usr) − M(A_sys)` (M per arm uses that arm's own baseline B — surgery changes B). **marker share =
asym(BASE) − asym(NEUTRAL)**; **preamble/offset share = asym(NEUTRAL) − asym(PM)**; **residual = asym(PM)** (construction
check). Template-cluster bootstrap CIs on all three.

## 4. Gates
- **ANCHOR (BASE)** — M(A_sys) −0.93 ± 0.15, M(A_usr) +1.90 ± 0.20 (reproduce OPX-01). Miss ⇒ harness diverged.
- **CONSTRUCTION CHECK (PM)** — |residual asym| ≤ 0.30 (collapses toward symmetric). Failure ⇒ ENUMERATION-INCOMPLETE
  (reported as such; sends us to find the tell), never a "prior" conclusion.
- **G-SEGMENT / G-CONSTRUCT** (tokenizer-only, pre-lock) — NEUTRAL single-token; all 3 modes build for item AND twin; spans
  located and same-index aligned in every mode; markers become the identical token in both headers; preamble excised in PM. 0
  failures.
- **MASS** — m ≥ 0.10 per cell per arm (neutral/PM renders are mildly OOD; report per-arm mass and B; forced-readout target at
  runtime if any falls below).
- Counterbalance sign-folded; per-item Y persisted per arm (`opx03_peritem.npz`); SMOKE(40)→FULL(720).

## 5. Scope — binding
Property of these spans/layers/model/battery, normal order, under residual overwrite. PM is a construction check. NEUTRAL word
choice (`info`) is a judgment call (both headers identical is what matters, not the specific word); flagged.

## 6. Predictions (regime, not midpoint) — labeled by bias-direction honestly
- Anchor reproduces.
- **COLLAPSE by PM, with the marker carrying a MINORITY** — some asym removed at NEUTRAL (marker), the rest at PM
  (preamble/offset). This is a **MODULAR** call (identifiable textual features carry it); predicting *survival at PM* would be
  the **INTEGRATIVE** call, which I am **not** making. (Two prior OPX predictions were integrative-and-wrong; here the
  structural logic — nothing left to key on after PM — forces collapse, so modular is the reasoned call, not bias over-correction.)
- Marker minority rests on EXT-01's ~13% bound, flagged as a **different quantity** (marker's share of exchange recovery, not of
  this asymmetry) — a legitimate prior, not a measurement of the same thing.
- Explicitly **against**: MARKER-CARRIES-majority, and against survival at PM (which I'd read as enumeration failure).

## User additions
- **Surgery is string-level then re-tokenize** (not index deletion): NEUTRAL replaces the exact header strings
  `<|start_header_id|>{role}<|end_header_id|>`; PM excises the text between the (former-system) `<|end_header_id|>\n\n` and
  `it["system"]`. Spans re-located by offset mapping after each surgery (content untouched, imperatives still present).
- **discrimination-matrix-pre-lock-gate** applied (§2); **predict-integration-get-separability** applied to the
  prediction labeling (§6).
