# VERDICT — PRV-01g: v̂ is NOT INDIVIDUALLY NECESSARY (with a PASSING dynamic-range gate). Projecting the single readable provenance direction v̂ out of the resistant condition at every layer destroys ~1% of the header's resistance (necessity 0.009, CI [0.003, 0.017] — a BOUNDED null: rules out a single-direction contribution above ~1.7%). The random-ablation control is inert (moves Y 0.012 vs a 0.597 bar), so unlike PRV-01d this run is well-posed. ⚠**SCOPE NARROWED (the lead researcher/the reviewer, 2026-09-24): "correlate, not the causal carrier" OVERCLAIMS. Single-direction ablation cannot distinguish "v̂ doesn't carry it" from "v̂ carries it redundantly alongside other axes." Licensed claim: v̂ is not INDIVIDUALLY necessary; whether the provenance INFORMATION is necessary is UNTESTED → PRV-01h (subspace ablation).**

**Result: this is the well-posed successor to PRV-01d's method-limited additive test. All gates in the right order:
G-CONSTRUCT 720/720; ANCHOR reproduces on FULL (Y(U)=−3.191, Y(H)=−0.805, denom +2.386 — the raw-column header effect, replicated
a third time); and — run FIRST as a hard pre-launch gate — G-DYNAMIC-RANGE PASSES: projecting a RANDOM unit direction out of H at
every layer moves Y only 0.012 nats, far below the 0.25·denom = 0.597 bar. The null control is inert, so ablation HAS the dynamic
range that addition lacked, and the H⊥v arm is interpretable. Removing v̂ itself (all-layer projection at the injected span) moves
Y by 0.022 nats → necessity = (Y(H)−Y(H⊥v))/denom = 0.009, CI [0.003, 0.017]: barely above zero, far below the 0.15 floor →
NOT-NECESSARY. v̂-projection (0.022) is only marginally more disruptive than random-projection (0.012), i.e. removing "the
provenance direction" is barely different from removing a random direction. The single-layer diagnostic H⊥v(L1) moves Y ≈ 0
(necessity_L1 = −0.001), exactly the self-repair prediction (single-layer ablation rebuilt downstream). And the secondary
additive-window probe shows NO inert rung even at α=0.05 (random did 33% of v̂'s effect) — confirming PRV-01d's additive test was
fundamentally method-limited, not merely mis-laddered.** Ran 2026-09-24, Lambda a100_sxm4, FULL n=720, $0.25, terminated clean;
re-verified from json. PREREG_PRV01G.md sha256 `d815b111...` (chained PRV-01d `06eeb097...`). (SMOKE ANCHOR-FAIL Y(U)=−4.617 was
the 40-item biased subsample, as in PRV-01d/f; FULL is the real check and passes.)

## Numbers (copied from results/prv01g.json)
| quantity | value |
|---|---|
| Y(U) / Y(H) | −3.191 / −0.805 (anchor ±0.15 ✅ exact) |
| denom Y(H)−Y(U) | +2.386 (raw-column header effect, 3rd replication) |
| **G-DYNAMIC-RANGE** Y(H⊥r,all), move / bar | −0.793, **0.012 / 0.597 → PASS** (null inert) |
| Y(H⊥v,all) | −0.827 |
| **necessity = (Y(H)−Y(H⊥v))/denom** | **+0.009 [0.003, 0.017]** → NOT-NECESSARY |
| necessity (sysTRUE / sysFALSE) | 0.011 / 0.008 (both ≈0, counterbalance-consistent) |
| H⊥v(L1) diagnostic necessity | −0.001 (≈0: self-repair, as predicted) |
| mass U/H/H⊥v(all)/H⊥r(all) | 0.477 / 0.452 / 0.453 / 0.452 (coherence ✅; ablation barely moves mass) |
| addition window α=0.05 / 0.10 (rand/v ratio) | 0.33 / 0.39 → NO inert additive window exists |

## Reading (the lead researcher's step; facts above)
1. **The single direction v̂ is not individually necessary — and this half IS earned.** With a null control that passed (random
   projection inert), removing v̂ from the resistant condition at every layer leaves the header's resistance essentially intact
   (~1% removed, CI rules out >1.7%). That is a clean, well-posed single-direction necessity result — the thing PRV-01d's
   method-failed run could not deliver.
2. ⚠**But "correlate, not carrier" is NOT licensed — it overclaims (scope narrowed).** Projecting one direction out of a ~4096-d
   residual removes ~0.02% of the space. If the provenance information is coded REDUNDANTLY across a subspace v̂ is one axis of,
   removing any single axis destroys nothing *regardless of how causal the information is*. So single-direction ablation cannot
   distinguish "v̂ doesn't carry it" from "v̂ carries it alongside other axes that also do." **Licensed: v̂ is not INDIVIDUALLY
   necessary. Whether the provenance INFORMATION is necessary is UNTESTED.** The concrete alternative is redundant subspace
   coding — and this program has now hit redundancy THREE times (RES-06 regional Σ=2.48; role/serialization saturation in the
   TOOL 2×2; and this single-axis null), three independent levels, same structure → redundancy is the **working hypothesis**,
   not a recurring surprise. The header effect is real (+2.386, thrice-replicated); its carrier is a subspace question → PRV-01h.
3. **Self-repair confirmed as a design fact, not a nuisance.** H⊥v(L1) ≈ 0 while H⊥v(all) ≈ 0 too — the single-layer null would
   have been uninterpretable, and making all-layer projection primary was the right call. The two agreeing is the pipeline check.
4. **Closes PRV-01d's open question:** there is no inert additive window (random did 33–39% of v̂ at α=0.05–0.10), so PRV-01d
   could never have had a clean additive rung. Addition was the wrong method here; ablation was right. That is the sixth
   design-error lesson made concrete → intervention-window-before-run.
5. **Pre-registered prediction was WRONG again (recorded) — and the miss is itself a finding.** §8 predicted PARTIALLY-NECESSARY
   (0.2–0.5); actual 0.009. That's the THIRD magnitude call in a row (mine and the lead researcher's) to predict an intermediate value and get
   ~0. Across the arc — PRV-01e 1.000, PRV-01f +0.13, role-at-raw +2.47, role-at-tojson +0.13, necessity 0.009, the 2×2
   saturating — **effects in this system are near-zero or near-saturated; the middle is sparsely populated.** The two PROCESS
   predictions (gate passes, H⊥v(L1)≈0) were right both times. Standing rule adopted: **pre-registered predictions name a REGIME
   {vanishing, saturated}, not a midpoint** → predictions-name-a-regime-not-a-midpoint.

## Scope (binding)
"v̂ is not INDIVIDUALLY necessary" is scoped to **this single L1 linear direction**, projected out at the injected span across all
32 layers. It does **NOT** license "correlate, not carrier" and does NOT test whether the provenance INFORMATION is necessary —
if the code is redundant across a subspace, single-axis ablation is null by construction. Single model (Llama-3.1-8B), forward +
residual hooks, one direction. **A residual-stream projection is not a deployable defense; no sentence here calls it one** (§7).
Do not extend across models.

## What this closes — and what it opens
**PRV-01 on the role header — three axes, two closed and one narrowed:** encoded + propagates to d=64 (PRV-01e) · used at the
INPUT level when it is the only signal, redundant with serialization (PRV-01f + TOOL-02 2×2, re-replicated in 01d/01g) · **the
single readable direction v̂ is not individually necessary (PRV-01g, well-posed).** The INTERNAL-carrier question is **NOT
closed** — information-necessity is open, and redundant subspace coding is the working hypothesis → **PRV-01h** (subspace ablation
by iterative deflation, with per-k dynamic-range gates). Representational headline stays REDUNDANCY at the input. Phase 3b still
parked. Nothing ships; public still held.
