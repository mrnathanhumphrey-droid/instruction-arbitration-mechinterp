# VERDICT — RES-01b: provenance or position? (RES-01a confound control)

**VERDICT: PROVENANCE-REAL-POSITION-INDEPENDENT (all layers).** RES-01a is confirmed: the non-linear provenance
it found is not an absolute-position artifact. The confound was genuinely available (an MLP decodes position from
the deflated residual at 0.62–0.72 vs 0.10 chance), but role decoding on a position-matched subset equals
unmatched (gaps ≤ 0.008). Ran 2026-09-20, Lambda a10, cached, NO forwards, terminated clean, $3.56 (166 min).
PREREG_RES01B.md sha256 `d00e885241a61246f9aabcd23abae9157488013d1b16e49b79bbe1eb9308d9b0`, chained to RES-01a
`7a098124…`. Artifacts: `res01b.json`, `res01b_arms.csv`.

## Reproduction gate — PASSED all layers
Role deflation refit k / pe_final vs KDR: L8 43/0.451 (44/0.454); L24 40/0.451 (42/0.451); L31 32/0.451
(32/0.451); L16 50/0.435 (50/0.434). Same pool, same deflation as RES-01a.

## Results (held-out group-disjoint; role chance 0.50; position-bucket chance 0.10)
| layer | Arm P position (chance .10) | Arm M matched role (CI) | ref unmatched role | Arm R role after pos-deflation |
|---|---|---|---|---|
| L8 | 0.723 | **0.949** [0.935,0.962] | 0.950 | 0.950 (20 dirs) |
| L24 | 0.625 | **0.890** [0.866,0.910] | 0.898 | 0.897 |
| L31 | 0.629 | **0.897** [0.878,0.916] | 0.904 | 0.904 |
| L16 (cap ctrl) | 0.681 | **0.931** [0.913,0.947] | 0.936 | 0.936 |

Arm M matched pool = 102,948 tokens (89% of pool; roles balanced within 5-token abs_pos bins). Nulls (shuffled
role) ~0.51 everywhere.

## Reading (the lead researcher's step; facts above)
- **The confound was real and on the table.** Arm P: an MLP reads absolute-position bucket from the deflated
  residual at 0.62–0.72 (chance 0.10) — exactly the RoPE-mixed position a linear probe misses. The PRV-01c linear
  position control (0.500) was blind to it. the lead researcher's catch was correct to demand this control.
- **Role decoding does NOT use position.** Arm M (position made role-uninformative by per-bin balancing) equals
  the unmatched reference within ≤0.008 at every layer (0.949 vs 0.950; 0.890 vs 0.898; 0.897 vs 0.904; 0.931 vs
  0.936). Arm R (linear position-deflation) agrees — unchanged. Provenance is real, non-linear, and
  position-independent.
- **Why the confound is weak here despite being available:** PRV-01c placed trusted/untrusted spans across
  overlapping absolute positions (medians 138 vs 145), so position and role are only loosely coupled — position
  is decodable but does not proxy role. (This is a property of the PRV-01c provenance pool, not the contested
  arbitration template; see scope.)
- **SMOKE was again a false/weak read** (BOTH-PRESENT, armM 0.68–0.77) because it under-deflates (k=5) and
  subsamples; the FULL run + reproduction gate is the result.

## Consequences (records graduate from provisional)
- **RES-01a STANDS.** Non-linear residual provenance exists at the saturated layers and is not position.
- **The KDR reframe stands (un-held):** KDR-01's "linear residual saturates near half; remainder non-linear OR
  non-residual" resolves to → the remainder is largely non-linear RESIDUAL provenance; the residual is not
  exhausted, the linear lens was. KDR M=0.471 is a floor on the linear lens.
- **`linear_saturation_is_a_lens` confirmed** (un-provisional).
- **Earned next step (RES-01a §4-A):** the non-linear intervention — non-linear analog of H4's subspace
  exchange (edit/deflate the non-linear provenance manifold, measure M on the same estimand). Needs forwards.
- Does not touch PRV-04c (attention not the router) or RDV-01.

## Scope
Tests the position confound only. Content is handled by PRV-01c's content-matched design and carries over. The
weak position-role coupling is specific to the PRV-01c provenance pool; a non-linear intervention on the
CONTESTED battery would need its own position check (the chat-template layout there is system-early/user-late).

## Method note
The decisive control (Arm M) had to be the SAME non-linear instrument as the result it audits — a linear
position control (PRV-01c 0.500) cannot rule out a confound for a non-linear probe. Audit a non-linear finding
with a non-linear control. probe_upstream.
