# PREREG — RES-06-FLIP: is the Σ=2.48 super-additive redundancy ORDER-STRUCTURAL?

**Locked before run. Chained to RES-06.** Llama-3.1-8B-Instruct, twin-patch decomposition, run at BOTH orders paired in one
job. Cleanup/decomposition probe (item 2 of the the reviewer cleanup queue), not a new-finding hunt.

- chained_to_RES06_sha256: `076b270179f52c37c4f569f738544747fea63e90b226c8c7e24225afa8e79409`
- runner: `run/res06/res06_flip.py` sha256 `8040c4eec650537b6a5c6c71408664e255aeb08fc937e8b3fbe1698b16b69535`
- battery: `stimuli_contested.jsonl` sha256 `d4145f1add05ec293d210ce40fe2ad3b858cc6abc2a4b86761e6f04573e629b4`; `stimuli_uncontested.jsonl` sha256 `183e59efcfbd411541152fecc1bf0de7c8ceb7385bb2d0404c0141cdafc053d6` (prv02/setup, DONE/READY, n=720)
- readout: R = logP(DONE) − logP(READY) at first assistant token; Y_signed = +R if target_sys==DONE else −R (+Y = obeys system slot). FORWARD ONLY (hooks for twin-patch, no grad).

## §1 What it answers
RES-06 found Σ(K+S+I+R) = 2.479 ≫ M_all = 1 (gap +1.48) at NORMAL order (system-then-user, recency favors user): the four
regions redundantly re-encode the counterfactual assignment (S≈1.0, R≈0.97, K≈0.51, I≈0.004). **Is that redundancy a property
of ORDER, or of content/structure?** Re-run the identical twin-patch decomposition under the ORD-01 flip (user-block first,
system-block last → recency now favors the system) and compare Σ paired.

## §2 Design (one operation throughout = twin-patch; both orders, paired)
- **normal** = RES-06 order (system→user). Serves as the **replication anchor**.
- **flipped** = ORD-01 `flip_perm`: old-index order BOS/pre + user-block + system-block + assistant. Verified on Llama's SH/EOT.
- Partition into K (markers/headers/BOS/EOT + post-header `\n\n`), S (imperative spans), I (intermediate content, incl. the
  Llama date-preamble), R (readout=last) is computed on the NORMAL sequence (RES-06's validated partition), then the flip is a
  token PERMUTATION and region indices are remapped through it. **Dry-checked tokenizer-only, local, 720/720:** partition ok,
  flipped partition complete+disjoint, readout stays last (R=[T−1]), length preserved, reorder confirmed (system moves after
  user), twins same-length. No partition-remap bug (the AUTH-01 Phase-1 class).
- Twin-patch: item residual ← counterbalanced twin's, aligned same-index; twins are same-length cb-flips (0 position import),
  and the flip perm is identical for item and twin (same header structure), so alignment holds in both orders.
- Arms per order: each region alone (M_K,M_S,M_I,M_R), all-together (M_all anchor ~1 by construction), per-region floors
  (same-slot diff-filler source, region-order aligned). M = −ΔY/(2B), signed by counterbalance, template-cluster paired
  bootstrap (NTMPL=30, BOOT=5000, SEED=20260914 — RES-06 seed for comparability).

## §3 Gates
- **REPLICATION (hard).** Σ_normal must reproduce banked 2.479 to ±0.10, else `HARNESS-DRIFT` → do not interpret, halt the
  reading. (Same battery/seed/estimator as RES-06 → deterministic; this catches environment drift.)
- **M_all ≈ 1 both orders** (|M_all−1| ≤ 0.15). It is a construction identity (within-template twins ⇒ ΔY=−2B), so it must
  hold in both orders; if not, `HARNESS-PROBLEM`.
- **TWIN-BASED VOID** (the coherence gate RES-06 lacked — its uncontested VOID was non-executed): all-position twin-patch must
  reproduce the twin's argmax token. Report per-order hit rate, group-before-subsample; ≥0.95 is healthy on-manifold.
- Distance: the flip is a permutation (0 position import between same-length twins), reported.

## §4 Mechanical verdict (pre-committed on paired ΔΣ = Σ_flipped − Σ_normal)
- **|ΔΣ| ≤ 0.25 AND CI includes 0 → ORDER-INVARIANT**: the super-additive redundancy is NOT a property of order — it is
  structural to content/decomposition (the assignment is redundantly readable regardless of which block is recent).
- **ΔΣ CI excludes 0 → ORDER-DEPENDENT**: redundancy tracks order; the per-region ΔM (reported for K/S/I/R) says where the
  shift lives (e.g., if the now-recent block's region gains).
- Else `INCONCLUSIVE` (wide CI). Σ_KSI (readout excluded) reported alongside as in RES-06.

## §5 Compute / cost
Cost driver (anchor_shape): 8B forwards with `output_hidden_states` (twin-patch region sweep), **×2 orders** + twin-argmax.
Anchor: RES-06 one order = $0.35 on a100_sxm4. Paired (both orders) + twin-VOID ≈ **$0.70–1.00** — above the $0.35 single-order
estimate, on purpose: running both orders in ONE job makes ΔΣ a same-rows/same-estimator paired comparison (probe_upstream)
rather than a cross-run comparison to a 2-day-old number. Well under $70/run · $100/day. a100-first (memory for hidden states);
watchdog armed; SMOKE (40 pairs) then FULL; terminate in finally; ledger.

## §6 Disclosure
Llama-only, decomposition of an internal quantity. No deployed-model claim moves. §6 trip-wire N/A.

## §7 User additions
(none)
