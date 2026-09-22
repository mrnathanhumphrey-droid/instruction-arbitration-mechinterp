# PREREG — H4: downstream re-derivation control (the "all-layers swap")

**Status: DRAFTED (UNLOCKED) 2026-09-15.** Precedes PRV-04. Equivalent name: PRV-03 Phase C.
Prior in chain: PREREG_PRV03.md sha256 `1e5ad707514b4902d73004d0bcae44b99a2ea8b995888192e0a41105cc71d3f0`.
Model: meta-llama/Llama-3.1-8B-Instruct, bf16, Lambda A100 (compute discipline: Lambda always).

---

## §0 — Why this runs before PRV-04 (the load-bearing logic; the lead researcher-fixed)

Every intervention in the arc (PRV-02 L16, PRV-03 Phase A single-needle, Phase B L8 subspace) edited a
**derived** representation at **one** layer while leaving the **source** of that representation intact:
the chat-template role markers, the header tokens, the positional structure. Any layer downstream of the
edit can attend back to those untouched tokens and **recompute provenance into the residual stream**,
overwriting the edit. If that is what happens, **M≈0 is guaranteed at every layer and every dimensionality**
and tells us nothing about whether the residual path is causal.

This is not merely a logical possibility — **the layer curve is positive evidence for it.** Provenance is
decodable at every layer with raw class separation **growing monotonically toward the output**
(Δ 0.201→0.749; P_e 0.033→0.107 but never chance). A quantity written once and left alone does not build.
That signature is what continuous re-derivation looks like.

**H3 and H4 are not mutually exclusive** (re-derivation would happen *via* attention reading the role markers)
but they differ on the thing the paper is about:
- **Under H4**, the residual representation can still be the proximate cause of behavior — continuously
  refreshed — and single-layer steering was simply the wrong knife.
- **Under H3**, the residual representation is epiphenomenal and routing drives behavior directly.

**Our current data cannot tell these apart, and the headline conclusion flips depending on which holds.**
H4 is therefore the correct next number, and it costs a fraction of building an attention-pattern
intervention that H4 might dissolve.

---

## §1 — Hypothesis & pre-committed reading (the falsifier is symmetric)

**H4 test:** exchange the provenance subspace projection at **every residual layer from the intervention
point through the output**, leaving **no downstream layer with an un-edited residual to write into**. Same
swap operation, same variance- and dimension-matched control, same estimand M as Phase B. One aggregate M
(this is a single multi-site intervention, not a layer sweep → no Bonferroni).

Pre-committed, before the number (verdict cuts RE-SET per the lead researcher ruling 4 — the bar rises because with
re-derivation actually removed, a genuinely residual-mediated arbitration should move *a lot*; leaving the
positive bar at 0.10 would let a marginal number carry the strong claim):
- **RESIDUAL-PATH-REAL:** |M| ≥ **0.20** and CI excludes 0 (recovers ≥0.78 of the 3.9-nat role effect). The
  residual path is causal; single-layer steering was the wrong knife; the PRV-02 / PRV-03 nulls get re-read
  as an **instrument limitation**, not a finding about the model. H3 not established. Leg 4 = "residual,
  continuously re-derived."
- **PARTIAL:** **0.05 ≤ |M| < 0.20** and CI excludes 0. Residual carries some but not most of the path; a
  full-stack effect of ~0.2 nats is not the "residual path is real" story — caught honestly here, not binned
  as zero. PRV-04 still warranted; leg 4 reported mixed.
- **RESIDUAL-EPIPHENOMENAL:** |M| < **0.05**, OR CI includes 0. With provenance forced to the swapped value
  in the residual stream all the way to the readout and behavior still flat, the residual stream is genuinely
  epiphenomenal for this arbitration. H3 **strengthened by eliminating its best competitor**; PRV-04 worth
  its cost.

Both arms are results. Neither is a shrug. **A VOID (§2.8) is a void, not a null.**

---

## §2 — DoF (RESOLVED — six the lead researcher rulings folded 2026-09-15; frozen at lock)

**0. POSITION SET (NEW — the hole I missed): edit the FULL role block, not just the imperative span.**
   If the intervention touches only the imperative spans, the role-marker and header positions stay clean at
   every layer, so any layer can attend to an un-edited header and re-derive provenance straight back — the
   single-layer defeater in a new coat, and a flat result would be uninterpretable for the exact reason we
   run H4. **Edit the k_L-dim projection at EVERY token position in BOTH role blocks (system block and user
   block, headers + markers + content), at every layer in range.** Then layer L's attention can only read
   L−1 residuals that are already swapped; the in-context source is gone with the derived representation.
   Blocks segmented by special tokens (`<|start_header_id|>`…`<|eot_id|>`): system block = [sh₀…eot₀],
   user block = [sh₁…eot₁]; the assistant header is NOT edited (it is the readout slot). Control scales
   identically — same positions, same per-layer k, random matched subspace.

**1. Layer range = L8 → L31, contiguous (PRIMARY).** Contiguity closes the channel, not the starting point:
   L9 reads L8's residuals, and if L8 is edited at all positions there is nothing un-edited to reach — so L1
   buys nothing mechanically while projecting 25 dims out of every position at early lexical-work layers adds
   real off-manifold risk. **Pre-registered CONDITIONAL SECOND ARM: L1 → L31, triggered ONLY by a flat
   primary** — committed now so a null cannot later be waved off as "you started too late." (Run offline if
   triggered; not in the primary script.)

**2. Per-layer subspace, refit independently at each layer L** (deflation: fit ŵ_L on train tokens, deflate
   ⊥, refit, stop held-out P_e≥0.45, cap k_L=25). Own geometry per layer. **v3 RE-LOCK 2026-09-15 (the lead researcher ruling
   "full 80k. Not 20k"):** the LR fit + scaler use the **FULL train split — IDENTICAL to Phase B in pool,
   deflation construction, k, and stopping rule.** The ONLY thing that may differ from Phase B is the LAYER
   SPAN. This is the sole configuration under which M≈+0.22 vs Phase B's +0.010 can carry the "Phase B's null
   was an instrument limitation, not a fact about the model" claim — a different/weaker subspace would leave
   the M-gap with two candidate explanations. (History: v2's 12k-fit subsample ran M=+0.217 but its L8 curve
   diverged from Phase B, 0.352 vs 0.398 — the estimator-identity gate fired, so v2 is PROVISIONAL only.)
   **ACCEPTANCE CONDITION, PRE-COMMITTED (no chasing):** L8's deflation curve reproduces Phase B
   (P_e→~0.398 @ k=25) AND M read against the locked tiers — ≥0.20 REAL / 0.05–0.20 PARTIAL / <0.05 or
   CI-inclusive EPIPHENOMENAL. **If M lands at 0.14 we report PARTIAL. No third run to find 0.22.** SMOKE still
   subsamples the pool (plumbing gate only; comparability is judged on FULL's L8 curve). **Addition (nearly
   free):** report
   **principal angles between consecutive layers' bases** (SVD of B_Lᵀ B_{L+1}; singular values = cos of the
   angles). Near-alignment across the stack = one geometry propagated; rotation = re-encoding at each layer —
   either way a result that discriminates H3 from H4 **independently of M**.

**3. k per layer = each layer's own deflation k_L** (held-out P_e≥0.45 stop, cap 25). Gives a **k-vs-layer
   curve** for free (a 2nd dimensionality result), and does not assume layer-invariant dimension (which the
   layer curve hints against). Control matches each layer's k_L.

**4. Swap = projection-EXCHANGE per layer** (as Phase B): shift each edited position's projection onto B_L by
   that layer's pool class-mean-difference restricted to B_L (system −Δ_L, user +Δ_L). Compounds down the
   stack by construction — the intended multi-site operation. Class means μ_sys/μ_usr and B_L fit on the
   content-token pool (identical provenance object to PRV-01c/03); only the *application* broadens to all
   positions, so provenance is not redefined, just edited everywhere it lives.

**5. Control = per-layer random k_L-dim orthonormal subspace, projection-norm matched, same all-position
   all-layer exchange.** Matched independently at each layer. NOT Haar.

**6. Estimand unchanged:** M = −(dY_ŵ − dY_ctrl)/(2B), Y = logP(DONE)−logP(READY) at first assistant token,
   Y_signed with DONE/READY counterbalance, whole-ratio paired template-cluster bootstrap (30 templates,
   5000 draws, 2.5/97.5). B measured fresh in-run. Single comparison → **no Bonferroni**.

**7. Verdict tiers = §1 RE-SET:** REAL |M|≥0.20 & CI excl 0 / PARTIAL 0.05≤|M|<0.20 & CI excl 0 /
   EPIPHENOMENAL else, α=0.05 two-sided.

**8. Sanity = plumbing (zero inferential weight) + the VOID GUARD that can actually kill the run.**
   Per-layer manip is tautological (the exchange sets each layer's probe by construction), so the L31 probe
   flip is logged as plumbing only. **The real guard (this is H4's structural risk):** a wide all-position
   all-layer projection edit that *damages* the model produces a flat M that looks exactly like the result
   "confirming" H3 — i.e. the most likely way to get our headline is by lobotomizing the model and calling it
   a finding. So: measure **uncontested floor-compliance rate** (fraction of single-instruction items with
   logP(DONE)−logP(READY)>0) unsteered vs. under each steered arm, and **VOID the arm if steered rate <
   0.90 × unsteered rate.** A void is a void, not a null.

**9. Self-check before the run** (hard-fail): the 24-layer treatment must (a) move item-0 Y from baseline,
   and (b) flip the L31 content probe on both spans, or `SystemExit`.

**Cost:** one pool pass returns all layers' hidden states; per-layer fits are numpy/CPU; the intervention
registers 24 forward hooks in one pass. ~2.5k short forward passes total (contested 720×2 + baseline +
floor subsample ×3). Runtime ≈ Phase B × ~1.5. SMOKE→FULL gate, auto-terminate in `finally`, ledger.
Estimate < $1.50; cost gate $70/run · $100/day stands. Lambda always.

---

## §3 — Procedure (mechanical, frozen at lock)

1. Pool residuals at all target layers (single `output_hidden_states=True` pass over the frozen PRV-01c
   prompt pool; span-content tokens; reuse `split_manifest` train/test span-disjoint split).
2. For each layer L in range: iterative-deflation subspace B_L (train-fit, held-out-P_e stop, cap 25) →
   Δ_L = B_L (B_Lᵀ (μ_sys−μ_usr)). Build matched random control basis + Δ_L^ctrl (norm-matched).
3. Baseline Y (no hook) → B.
4. Treatment: register hooks on layers 7..30, each applying its Δ_L exchange to that layer's span content
   tokens; measure Y_ŵ. Control: same hooks with Δ_L^ctrl; measure Y_ctrl. (Two forward passes per item.)
5. Per-template dY_ŵ, dY_ctrl, dB; M and paired template-cluster bootstrap CI; verdict per §1.
6. Write `results/h4.json` (deflation curves per layer, k_L, ‖Δ_L‖, B, dY_ŵ, dY_ctrl, M, CI, verdict) +
   `VERDICT_H4_<date>.md`. Terminate instance; ledger.

## §4 — What this cannot do (scope, pre-registered)

- H4 flat does **not** prove attention routing (H3) — it removes H3's best competitor. Establishing H3
  positively is PRV-04. (Same discipline as Edit 1: elimination ≠ demonstration.)
- The k_L=25 cap may bind at some layers (as it did at L8): dims 26+ of provenance are not exchanged. If the
  cap binds and M is flat, the flat result is "flat for the top-25 provenance subspace at every layer,"
  same caveat as Phase B, stated not discovered.
- Retired, will not re-litigate: the PRV-02 two-things-cancel (half-arms) hypothesis is dead by breadth —
  M≈0 across six layers and out to k=25 would require identical cancellation at every layer and every
  dimensionality (the lead researcher, 2026-09-15).

---
## LOCK
**LOCKED 2026-09-15** on the lead researcher's ruling ("Lock it with those six folded in and run"). Six DoF rulings folded
(§2.0–§2.8), verdict cuts re-set (§1). **RE-LOCKED (v2) 2026-09-15** after the first SMOKE hit the watchdog in the
deflation (a compute miss, gate did its job at $1.02): option-2 fit-subsample. **v2 FULL ran M=+0.217 but its
L8 curve diverged from Phase B (0.352 vs 0.398) → estimator-identity gate FIRED → v2 PROVISIONAL only.**
**RE-LOCKED (v3) 2026-09-15** (the lead researcher "full 80k. Not 20k"): §2.2 reverted to the FULL train fit, Phase-B-
identical except layer span; acceptance condition pre-committed (L8→~0.398 @ k=25; M on locked tiers; no third
run). WD_FULL raised to 6h for the ~4.5–5h run. Estimand, k=25, deflation curve, principal angles, all six
rulings unchanged. GATE-FREE STANDING FINDINGS (do not wait on the acceptance gate): (i) the *direction* —
residual path moves under all-layer swap at 4.6× a norm-matched control, VOID clean — is a conservative
version of the reversal; (ii) **principal angles are the mechanism** (consecutive-layer bases largely
orthogonal, cos_mean 0.16→0.32 ⇒ each layer re-encodes in its own geometry, which is *why* single-layer failed
and all-layer worked) — kept in the verdict as **consistent-with, not evidence-for**. Chained to prior: PREREG_PRV03.md sha256
`1e5ad707514b4902d73004d0bcae44b99a2ea8b995888192e0a41105cc71d3f0`. This file's own sha256 recorded in the
sidecar `PREREG_H4.md.sha256`. Runner frozen: `run/h4/h4_lambda.py`. No edit to prereg or runner after this
line without a superseding ruling + re-lock.
