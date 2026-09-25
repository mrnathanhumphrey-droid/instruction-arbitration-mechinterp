# OPX-02 — Does the one-sided span asymmetry follow RECENCY or ROLE?

**Order-reversal test of the OPX-01 asymmetry (A_sys −0.93 / A_usr +1.90).** the reviewer spec (relayed by the lead researcher). Composes OPX-01's
one-sided same-index span patch with ORD-01's block-order flip. **Locked before run; chained to OPX-01.**

- chained_to_OPX01_sha256: `bd3604acc00e29ce473b87481f604193406cc3fa28108247f481efb0325bb42a`
- runner: `run/opx02/opx02_lambda.py` sha256 `78778a56e80a1c9535c9c912e8708ccffd7f61e2317065ff84eb3ac85288f1a3`
- model: **meta-llama/Llama-3.1-8B-Instruct**; battery **`stimuli_contested.jsonl`**; spans = imperative; layers **L8–31**;
  DONE/READY. Composability confirmed from artifacts: ORD-01's `flip(ids,sh,eot)` rebuilds `BOS+USER-blk+SYSTEM-blk+asst` and
  returns an old→new index map; **ORD-01 Arm C already ran span-exchange/twin in both orders** ("same ops in flipped index
  space") — span patching under reversed order is proven, not new.

## 1. Cells — per order (normal = system first / user last; flipped = user first / system last)
Twin activations, span positions, all layers. In flipped order the span indices are remapped through `o2n`, the twin captured
in flipped order.
- **A_sys** — item sys-span ← twin sys-span (same-index, sys only)
- **A_usr** — item usr-span ← twin usr-span (same-index, usr only)
- **EXCH** — cross two-sided (RES-02 Arm1 anchor; normal ≈ 0.462)
- **CONSTR** — same two-sided (become-the-twin ≈ 1.0 per order) — **construction / coherence check, NEVER evidence**

## 2. Primary quantity + discriminator
**Raw ΔY in nats per order is primary** — B flips sign with block order (ORD-01), so M normalized by B is not comparable
across orders; M reported per order with its own B as secondary. Signing is by role (`ysig`: +Y = obeys system), consistent
across orders.
- **RECENCY** — the twin-directed overshoot follows the **last** block: under reversal the role-labeled effects **swap sign**
  (flipped A_sys ≈ normal A_usr, flipped A_usr ≈ normal A_sys). Pre-committed test: `sign(dYf_sys)==sign(dYn_usr)` AND
  `sign(dYf_usr)==sign(dYn_sys)`, and not the keep pattern.
- **ROLE** — the asymmetry stays with the roles: `sign(dYf_sys)==sign(dYn_sys)` AND `sign(dYf_usr)==sign(dYn_usr)`. Recency and
  role come apart at the span level — nothing in the ledger predicts this.
- **MIXED** — neither clean swap nor keep; report the table.
Reported with template-cluster bootstrap CIs on keep (dYf_sys−dYn_sys), swap (dYf_sys−dYn_usr), and the usr analogues.

## 3. Gates
- **ANCHOR (normal order)** — reproduces OPX-01: M(EXCH) 0.462 ± 0.05, M(A_sys) −0.93 ± 0.15, M(A_usr) +1.90 ± 0.20. A miss
  means the harness diverged; nothing downstream readable. (Level-vs-contrast: these are raw exchange LEVELS, not netted.)
- **CONSTRUCTION / COHERENCE** — M(CONSTR) ≥ 0.95 in **both** orders. This is the coherence gate: a lobotomizing patch cannot
  reconstruct the twin's behavior to M≈1 in each order, so CONSTR-both-orders subsumes the twin-VOID concern; the uncontested
  VOID is additionally inherited from OPX-01 (same operator/battery, floor 1.000). ⚠**Judgment call flagged:** I use
  CONSTR-both-orders as the coherence gate rather than re-implementing the uncontested VOID in flipped order — say if you want
  the explicit uncontested VOID added.
- **B PER ORDER** — Bn and Bf reported; expected to flip sign (that is the recency baseline, and why raw dY is primary).
- **MASS** — m ≥ 0.10 per cell; runtime-derived forced-readout target if any falls below.
- **G-SEGMENT** (tokenizer-only, pre-lock) — spans located and same+cross aligned to twin in **both** orders (flip index remap
  valid), 0 failures.
- Counterbalance sign-folded; per-item ΔY per cell per order persisted (`opx02_peritem.npz`); SMOKE(40)→FULL(720).

## 4. Scope — binding
Property of these spans/layers/model/battery under residual overwrite. Tests whether the OPX-01 asymmetry is recency- or
role-bound; does not relocate arbitration. CONSTR ≈ 1.0 is a construction identity, never evidence.

## 5. Predictions (regime, not midpoint)
- Anchors reproduce (normal A_sys −0.93, A_usr +1.90, EXCH 0.462); CONSTR ≈ 1.0 both orders; **B flips sign**.
- **RECENCY** — reversal swaps which span overshoots. Mechanistic (competition/renormalization follows the last block), same
  class as the OPX-01 prediction that missed; stated as a regime. If it holds, ORD-01's ordinal recency result gets a span-level
  mechanism.
- Explicitly **against**: ROLE (asymmetry stays with roles → recency and role dissociate at the span level).

## User additions
- **Composition detail:** exact reuse of ORD-01 `flip`/`o2n`; twin captured separately per order (`capn`, `capf`); flipped span
  indices `fsi=[o2n[p] for p in si]` etc. This is ORD-01 Arm C's proven pattern, extended from two-sided to one-sided cells.
- **Why raw dY, not M, is the discriminator:** M divides by a per-order B of opposite sign, so a sign-swap in dY could be
  masked/flipped by the M normalization. The recency-vs-role call is made on raw dY signs; M is descriptive per order.
