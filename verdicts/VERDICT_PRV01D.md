# VERDICT — PRV-01d: CONTROL-FAILED / METHOD-LIMITED (RETAG 2026-09-24, supersedes the WITHDRAWN "NOT-THE-PATHWAY"). G-NULL-DIRECTION failed at EVERY α (random norm-matched direction moves Y 48–116% as much as v̂), so by the prereg every α is VOID for the headline and this run measures NOTHING about whether v̂ is the pathway. The additive α-ladder (0.25–2.0× mean residual norm) started ABOVE the disruption threshold — the question was un-testable before the first forward pass. Narrow earned statement: v̂ is not a STRONG additive lever (α=0.25, least-disruptive rung, v̂ moves Y ~−0.10 nats vs a +2.386 target, random doing half). CREDIT (unplanned): the anchor independently replicated the redundancy 2×2's raw column on a separate run+pipeline.

**⛔ NOT-THE-PATHWAY WITHDRAWN (the lead researcher/the reviewer, correct — my over-claim). My own prereg makes a failed G-NULL-DIRECTION VOID for the
headline; it failed at all four α, so no α yields interpretable closure and no claim about v̂ is drawable. A random vector doing
50–116% of what v̂ does means the patch is dominated by GENERIC DISRUPTION — and both +v and −v moving Y downward is that exact
signature (perturbation degrades the computation irrespective of direction). closure=−0.399 at α=1.0 is NOT evidence that v̂
pushes toward injection-following; it is evidence that a large enough shove at L1 makes the model worse at the task, which any
vector would give. So the run is CONTROL-FAILED / METHOD-LIMITED, not a null about v̂.**

**What still holds (well-posed parts):** ANCHOR reproduces on FULL — Y(U) = −3.191 (want −3.2), Y(H) = −0.805 (want −0.73),
denom Y(H)−Y(U) = +2.386 nats measured in-run. This is an **unplanned independent replication of the redundancy 2×2's raw
column** (header produces ~+2.4 nats un-serialized) on a separate run and pipeline — it materially strengthens the redundancy
finding. Fit gates: G-CONSTRUCT 720/720, G0(L0) = 0.500 (chance by construction), G-VALIDITY(L1) = 0.999, d1 = 1.000 (v̂ is
almost perfectly readable). **What is NOT earned:** anything about whether v̂ is or isn't the causal switch — the additive test
with a non-separating null cannot address it. Ran 2026-09-24, Lambda a100_sxm4, FULL n=720, $0.37 (+$0.86 on a prior
boot-timed-out box, terminated clean, no orphan), terminated clean; re-verified from json. PREREG_PRV01D.md sha256 `06eeb097...`
(chained PRV-01f `0ba39250...`). (SMOKE ANCHOR-FAIL Y(U)=−4.617 was the 40-item biased subsample; FULL is the real check.)

## Numbers (copied from results/prv01d.json)
| quantity | value |
|---|---|
| Y(U) raw/user | −3.191 (anchor −3.2 ±0.30 ✅) |
| Y(H) raw/ipython | −0.805 (anchor −0.73 ±0.30 ✅) |
| denom Y(H)−Y(U) | **+2.386** (the target; re-confirms the raw-column header effect) |
| G0(L0) / G-VALIDITY(L1) / d1 | 0.500 / 0.999 / 1.000 (fit_ok ✅) |
| mean L1 residual norm | 1.033 |

| α | closure [CI] | eff_v | eff_rand | eff_(−v) | \|rand\|/\|eff_v\| | mass | G-NULL | G-SIGN | G-COH |
|---|---|---|---|---|---|---|---|---|---|
| 0.25 | −0.043 [−0.066, −0.022] | −0.103 | −0.049 | −0.019 | 0.48 | 0.49 | ❌ | ✅ | ✅ |
| 0.5 | −0.146 [−0.199, −0.097] | −0.349 | −0.222 | −0.142 | 0.64 | 0.52 | ❌ | ❌ | ✅ |
| 1.0 | −0.399 [−0.526, −0.299] | −0.952 | −0.505 | −0.204 | 0.53 | 0.56 | ❌ | ✅ | ✅ |
| 2.0 | +1.469 [+1.197, +1.792] | +3.507 | +4.074 | +3.326 | 1.16 | 0.15 | ❌ | ❌ | ✅ |

passing_alphas = [] → by §6, controls fail at every α. **This does NOT read as NOT-THE-PATHWAY — a failed G-NULL-DIRECTION is
VOID for the headline, so [] means the run cannot address the hypothesis, not that the hypothesis is false.** v̂ persisted to
`prv01d_vhat.npy`.

## Reading (the lead researcher's step; facts above)
1. **The run measures nothing about v̂ as a pathway.** The additive α-ladder started above the disruption threshold: at the
   least-disruptive rung (α=0.25) the random control already moved Y half as much as v̂, and it only got worse up the ladder
   (random exceeds v̂ at α=2.0). There is no α with a clean, direction-specific signal, so no closure value is interpretable.
   CONTROL-FAILED / METHOD-LIMITED.
2. **What IS earned, and it is narrow:** across the coherent range, patching v̂ produced no positive movement toward the
   header's effect — at α=0.25, v̂ moves Y by ~−0.10 nats against a +2.386-nat target with random doing half. So **v̂ is not a
   strong additive lever.** That is a bounded statement about additive lever strength, NOT a statement about the pathway. If v̂
   were a strong additive lever its specific effect would dominate the generic floor somewhere on the ladder; it does not.
3. **Nothing is demonstrated about "the switch the model flips."** The earlier claim that "recoverable ≠ used now has a causal
   edge / demonstrably not the switch" is WITHDRAWN — a run where a random vector does the same work as the tested one
   demonstrates nothing about the switch. The external-surfacing recommendation stands on its OWN evidence (serialization,
   redundancy) and does not need this run.
4. **The α-ladder was a design error (mine), and it is the sixth of this arc's class:** a gate bar (G-NULL-DIRECTION) written
   as a post-hoc pass/fail without first mechanically establishing that a passing rung exists. §8 predicted PARTIAL-PATHWAY; the
   prediction was wrong AND the spec that produced it is why the run failed. Standing rule adopted: **an intervention probe must
   first demonstrate a magnitude at which its null control is inert; if no such window exists, the run does not launch.** (See
   the intervention-window-before-run method rule.)
5. **CREDIT (unplanned):** the anchor reproducing Y(U)=−3.191 / Y(H)=−0.805 is an independent replication of the 2×2's raw
   column on a separate run+pipeline — not asked for, and it strengthens the redundancy finding.

## Scope (binding)
CONTROL-FAILED / METHOD-LIMITED means **no claim about v̂'s causal role** is drawn from this run. The only substantive readings
are: (a) v̂ is not a strong ADDITIVE lever at L1 up to α=2.0 (mass decoheres to 0.15 beyond), and (b) the raw-column header
effect (+2.386) replicated. Single model (Llama-3.1-8B), forward + one residual hook, additive patch only. **A residual-stream
patch is not a deployable defense; no sentence here calls it one** (§7). Do not extend across models. The pathway/necessity
question is REOPENED and moves to PRV-01g (ablation).

## What this closes — and what it doesn't
PRV-01 stands on the role header for: **encoded + propagates** (PRV-01e), **used at the input level when it is the only signal,
redundant with serialization** (PRV-01f + TOOL-02 2×2, re-replicated here). The **causal-pathway question is NOT closed** —
PRV-01d's additive test was method-limited; **PRV-01g** (project v̂ out of the resistant condition, necessity not sufficiency,
with a G-DYNAMIC-RANGE gate run first) is the well-posed successor. Phase 3b still parked. Nothing ships; public still held.
