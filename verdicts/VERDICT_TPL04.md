# VERDICT — TPL-04 (double-wrap dose response on the system turn)

**Date fired/landed:** 2026-11-10 · **Verdict (mechanical, pre-registered): IDEMPOTENT**

- Prereg `prereg/PREREG_TPL04_PHASE1.md` sha256 `75e7e9083a2bff94f347e4861e80d3139d3dc154758d493b0e1bcc2afe7ceb6a` (sidecar written; chained TPL-03 `bf778543`).
- Runner `runners/tpl04_lambda.py` sha256 `17798b1a1e782176e288375a6d88aff3eedfecefad2e05263bb5464543fb8662` (matches sidecar at fire time).
- Results `results/tpl04/tpl04.json` sha256 `25a1271ecc4d4e2e206d57fcd8525701e7a35a9b6ea34d09858a479ad137df91`; full n=720, seed 20260927, 5000 template-bootstrap, transformers 4.46.0. SMOKE passed first.
- **Provenance note:** the result JSON's `phase1_lock` field reads `PENDING_SEAL`. Unlike TPL-03, the lock hash was not stamped into the runner before hashing. The binding is the runner and prereg sha256 sidecars above, which match. This is a cosmetic gap, not a lock break.

## Primary: same-family dose G = (own2 − own1) − (inert2 − inert1) @ injection absent, forced Y_signed

| host | role | G | 95% CI | excl 0 |
|---|---|---|---|---|
| llama | anchored (bC −0.52) | +0.000 | [−0.014, +0.015] | no |
| qwen | anchored (bC +0.94) | −0.052 | [−0.160, +0.041] | no |
| gemma | magnitude only | +0.023 | [−0.010, +0.059] | no |

Both anchored CIs include 0, so the verdict is **IDEMPOTENT**. dosing = [], malformed = [], sign recovered at dose 2 = no on all three hosts, and |D_own| does not grow with depth on any host. The gc and realized gates are clean on all three. The minimum candidate mass is 0.27 (llama), above the 0.10 malformed floor.

## Secondary

- D_own1 / D_own2 (own − inert at the same depth):
  - llama −0.017 / −0.017;
  - qwen +0.047 / −0.005;
  - gemma −0.078 / −0.055.
  - Every value is at most 0.08, an order of magnitude below |bC|, the same as TPL-03.
- Raw dose (depth 1 to depth 2) does move on qwen and gemma, but it moves equally for own and inert:
  - qwen: own +0.12, inert +0.18;
  - gemma: own −0.08, inert −0.10.
  - So any second token shifts these hosts (length or dilution). The host's own delimiter adds nothing beyond that.
- Cell pattern matches TPL-03: the system instruction is obeyed when the injection is absent and the injection wins when present, whatever the wrap.

## Reading (per the prereg bands)

TPL-03's near-null was idempotence, not a lack of power. Nesting the host's own delimiter around the system content is a dead operator for testing delimiter type. Design B (a cross-family delimiter or a naked-span wrap) is deferred. It is **not** auto-funded and needs its own ruling.

This is not a delimiter-type verdict. It does not refute the boundary-vs-authority property; it removes this way of testing it.

**Prediction:** IDEMPOTENT (the lead researcher's pre-registered prediction) was a **HIT**. The prediction class now stands at 2 hits / 7 misses.

Instance terminated in the launcher's finally block.
