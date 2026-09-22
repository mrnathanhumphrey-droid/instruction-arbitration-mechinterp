# PREREG — RES-01b: is it provenance or position?

**Status: LOCKED 2026-09-20.** the lead researcher caught a live confound in RES-01a (same error family as ATT-01): absolute
token position is a structural covariate of role, the MLP may decode position not provenance, and the only
position control (PRV-01c pos-arm = 0.500) used a LINEAR probe — the instrument RES-01a proved blind. Cached,
same layers/deflated-residuals/MLP/split, NO forwards. Chained to PREREG_RES01A.md sha256
`7a098124afdae9ea3f6f7e06e996441675eccd13efe2b683eea42a239dcc7e37`.

## §0 Feasibility (checked before lock)
Absolute token position reconstructed per token = `span_start_index` (prompts.jsonl) + within-span offset.
role = trusted(0)/untrusted(1). The two roles' abs_pos distributions OVERLAP heavily (median 138 vs 145; ranges
43–281 vs 25–313) — PRV-01c placed provenance spans across overlapping positions, so the confound is weaker here
than a naive system-early/user-late layout. **89% of the pool falls in 5-token abs_pos bins containing ≥20 of
BOTH roles**, so Arm M has ~103k matched tokens. This linear-level overlap does NOT pre-decide the non-linear
control; run it.

## §1 Arm P — is position available non-linearly? (diagnostic)
MLP decodes absolute-position BUCKET (10 quantile bins, chance 0.10) from the k=50 role-deflated residual at
L8, L16, L24, L31. Held-out, group-disjoint. Tells us whether the confound is even on the table.

## §2 Arm M — position-matched role decoding (DECISIVE)
Build a subset balancing the two roles within each 5-token abs_pos bin (keep bins with ≥10 of each role;
subsample to equal role counts per bin → position is role-uninformative by construction). Refit the role MLP on
this subset alone (train on subset∩train, eval subset∩held-out, group-disjoint), SAME architecture/hyperparams
as RES-01a. Report matched-subset size per layer (train + held-out). If a layer's matched held-out < 2000
tokens or < 5 bins, report THIN and do not read that layer (do not loosen tolerance).

## §3 Arm R — role after position-deflation (brackets from the other side)
Iteratively linear-deflate the deflated residual against abs_pos (fit linear map residual→standardized abs_pos,
project out the direction, repeat until held-out position R² < 0.05 or k=20 cap). Then role MLP. Weaker than M
(linear position-deflation can't remove non-linear position), but nearly free.

## §4 Readings (pre-committed) — on Arm M point accuracy (held-out, matched), CI cluster-boot by prompt
- **Arm M ≥ 0.80 (CI-lo > 0.65)** → PROVENANCE-REAL-POSITION-INDEPENDENT: RES-01a stands, the reframe stands,
  the non-linear intervention is earned.
- **Arm M ≤ 0.60 (CI-hi < 0.65)** → POSITION-DECODED: RES-01a decoded position, RETRACT it. This is itself a
  substantive finding about what non-linear "provenance probes" measure, and the `linear_saturation_is_a_lens`
  lesson INVERTS to "a non-linear probe finds any covariate your linear control was too weak to rule out."
- **Arm M 0.60–0.80** → BOTH-PRESENT: report the split; non-linear provenance real but smaller than 0.95.
- **Arm P at chance (≤ 0.15)** → confound not available; Arms M/R belt-and-braces; RES-01a stands immediately.
Reference: RES-01a full (unmatched) role MLP reproduces (~0.90–0.95) as the anchor; the matched-vs-unmatched gap
IS the position share. Shuffled-role null (100 draws) for every arm.

## §5 Scope
Tests ONE confound (position). Passing makes the MLP result position-free, not content-free — content is handled
by PRV-01c's content-matched design and carries over. Reproduction gate on the role deflation (k, pe vs
kdr01_k50.json) required per layer or that layer is not read.

## §6 Artifacts
`res01b_arms.csv` (layer, arm, metric, held-out score, CI, null_p95, matched_n, repro_ok), `VERDICT_RES01B.md`,
sidecar chained to RES-01a. Cached (tok_resid L8,16,24,31 + tok_meta + prompts.jsonl + kdr01_k50.json); NO
model, NO HF, NO forwards. SMOKE-gated (pipeline only — RES-01a taught SMOKE under-deflates; the reproduction
gate validates FULL), on-instance watchdog (watchdog_always), auto-terminate, ledger, prompt-inj-res01b.

---
## LOCK
**LOCKED 2026-09-20.** Arms (§1–3), decisive metric + readings (§4), thin-subset rule (§2) fixed above.
Executor specifics in the runner. sha256 in sidecar `PREREG_RES01B.md.sha256`, chained to RES-01a `7a098124…`.
No edit after this line without a superseding ruling + re-lock.
