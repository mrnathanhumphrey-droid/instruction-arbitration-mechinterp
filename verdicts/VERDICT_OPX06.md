# VERDICT — OPX-06: does removing the marker make block order matter? — DEGENERATE (the intended test did not run)

**Verdict (mechanical): INVALID / DEGENERATE — NOT "NO-FLIP".** The JOINT order-flip is **token-identical to the counterbalance-twin
map**, so the primary quantity q = asym_JOINT_reversed / asym_JOINT_normal is **exactly 1.000 by construction**, carrying zero
information about position. The runner's headline "NO-FLIP → property of the patching operation" is an **artifact of this
degeneracy and must not be reported as a finding.** Self-caught from the exact q and the persisted per-item data.

- prereg: `PREREG_OPX06.md` sha256 `71ce191f2135d66b843d63750e44ae10c473d60cda6aa570880d961ee71e9cb7` (chained OPX-05
  `e110307e…`); runner sha256 `6d2db0e4667669384fb6744772a4ca05428b990ab2bae567c32780256524076d`
- run: a10 @ us-east-1, FULL n=720, $0.31, terminated clean, no orphan. `run/opx06/results/` (json/csv/npz retained for the record).

## The degeneracy (proof)
At JOINT both blocks are `[info-header][\n\n][imperative]`, identical **except the counterbalanced target token** (DONE vs READY).
The cb-flip twin is the same item with the targets swapped. Swapping block **order** (the flip) therefore produces a token sequence
**identical to the twin in normal order.** Consequence, verified on the persisted per-item Y:
- **`asym_JOINT_flipped[i] == asym_JOINT_normal[twin(i)]` exactly — all 720 items, max |diff| = 0.00e+00.**
- The battery is fully counterbalanced (360/360), so the *set* of flipped values is just the normal set reindexed item↔twin →
  **mean asym_flipped ≡ mean asym_normal → q ≡ 1.000** (CI [1.000, 1.000]). Likewise mean B_flipped = −mean B_normal
  (−0.72 / +0.72) is the same twin identity under `ysig`, not a recency signal.
- The CONSTRUCTION gate I ran as a clean PASS (reversed multiset-identical to normal, JOINT blocks equal length, 720/720) was in
  fact the **signature of this degeneracy** — token-identical-under-permutation blocks + a counterbalanced battery force flip = twin.
  It should have been caught at step-zero, before the spend. It was not. (Banked: a-construction-gate-can-certify-a-degeneracy.)

## What DID run (the BASE cells are not degenerate)
BASE blocks are **not** token-symmetric (system block 40 tok with preamble+filler vs user block 26), so the BASE flip is a genuine
reordering (the OPX-02 case), not the twin map. It reproduces OPX-02 in-run: asym_BASE_normal +21.94, asym_BASE_flipped +21.45 —
same sign, comparable magnitude → **role-keep confirmed** (the marker-present asymmetry stays with the block under reversal). And the
ANCHOR holds: asym_JOINT_normal / asym_BASE_normal = **0.904** (reproduces OPX-05). So the harness is correct; only the JOINT-flip
cell is void.

## Reading (the lead researcher's step; facts above)
- **The question OPX-06 was built to answer — does order/position govern at JOINT — is UNANSWERED.** The flip cannot test it here
  because, at JOINT, "reverse the order" and "relabel as the counterbalance twin" are the same operation.
- **Constructive reframe (hypothesis, not established).** At JOINT the two blocks are lexically identical, so the asymmetry
  `asym = dY_usr − dY_sys` is, by construction, the contrast **"patch the second-block span" − "patch the first-block span"** — a
  block-**position/index** contrast. That reframes what OPX-05's 90% survival is: once every lexical feature is stripped, the
  surviving ~20-nat asymmetry is *definitionally* an earlier-vs-later span-position effect. This is consistent with the OPX-05
  result but it is **baked into how A_sys/A_usr are defined**, so it is not independent confirmation — and it does not by itself
  distinguish "position governs" from "the patching operation is asymmetric in what it sources/writes," which was the whole point.
- **It does not overturn anything published.** OPX-04/05 stand (BASE reproduces OPX-02 and the OPX-05 anchor in-run). What is
  retracted is only OPX-06's NO-FLIP headline, which never had content.

## Fix direction (for the reviewer to re-spec; NOT locked)
Break the flip = twin identity. Candidates: (a) make the two blocks differ by something **other than** the counterbalanced target
(e.g. distinct imperative templates per block) so a reversal is not a twin map; (b) test position with an **independent** patch
source rather than the cb-twin; (c) attack the reframed question directly — is the A_sys/A_usr **operation** symmetric in source and
write-site (patch first-from-second and second-from-first, measure leverage by index with content held identical)? (c) is the
"is it the operation" probe the NO-FLIP branch was meant to motivate, reachable without the degeneracy.

## Prediction outcome
- Both callers predicted NO-FLIP. **The result is q=1.000 but by construction, so the prediction is neither confirmed nor
  refuted — it is untestable in this design.** Not scored as a hit. (The five-miss record is unchanged; this is a design void, not a
  sixth data point.)

## Scope (binding)
No positional/operation conclusion is licensed by OPX-06. BASE cells reproduce OPX-02 (role-keep) and the OPX-05 anchor; the
JOINT-flip cell is a construction identity. Do not publish. A re-spec that breaks flip = twin is required to answer the order/operation
question.
