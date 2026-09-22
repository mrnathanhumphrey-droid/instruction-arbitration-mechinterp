# PREREG — MMD-01: Is M2's MMD shape reproducible, or sample-specific?
**Program:** Prompt_Injection · corpus ``
**Status:** 🔒 **LOCKED 2026-09-14** on the lead researcher's explicit call ("A, go"), before any model load. sha256 in sidecar `PREREG_MMD01.md.sha256`.
**Target:** arXiv 2606.27567 **§M2** (the empirical MMD curve that is the paper's only grounding for Assumption 3), NOT the theorem.
**Provenance:** escalated FINDING from PRV-01c (`PREREG_PRV01c.md`, `3c88ba7d…2da5`): our G0a peaked **L16, not M2's L8**, ~2–3× low in magnitude. **Cost class:** inference only, one 8B model; gate at $10 (sweep = many MMD passes over cached residuals, but weights load once).

---

## 1. What this measures — and the trap it must not fall into

PRV-01c measured a property of a model. MMD-01 measures **whether someone else's measurement reproduces** — a different epistemic object with a nasty property: **there is no clean non-reproduction without a search over the unstated degrees of freedom.** M2's stated method leaves free, at minimum: which documents from the four repos, how many, how sampled; preprocessing (truncation, dedup, length filters); MMD vs MMD²; biased vs unbiased estimator; bandwidth on pooled or per-class; quantization implementation; padding/mask handling.

**Pick one config, miss, and we've only learned that *our* config misses** — an unexplored space wearing a result's clothes (the same error as accepting a null before showing the instrument could find the thing). Therefore **MMD-01 is a pre-committed SWEEP, not a point.** The question is not "does our run match" but **"does any reasonable configuration of the unstated parameters produce M2's shape?"** — and the verdict attaches to the **fraction of a pre-committed grid** that reproduces, never to whether some single cell does.

## 2. The reproduction criterion — shape-only, peak location binding

Magnitude carries ≥3 free conventions (MMD vs MMD², biased vs unbiased, normalization); any one rescales the whole curve. We already have the empirical tell: **in PRV-01c the L8/L31 ratio landed in-band (1.27 ∈ 1.20±0.15) while the shape failed** — magnitude is the less informative axis, not just in principle. Peak location is invariant to every monotone transform and is exactly where the curves disagree (our L16 vs M2's L8).

- **PRIMARY (binding):** peak of the MMD-by-layer curve at **L8** (over layers {0,8,16,24,31}).
- **SECONDARY:** monotone non-increasing from the peak through L31.
- **TERTIARY (descriptive only, NO pass/fail):** magnitude and L8/L31 ratio.

M2 reference (verbatim, `lit/B3/inseparability/text.txt`): L0 0.606, **L8 0.908 (peak)**, L16 0.885, L24 0.805, L31 0.755.

## 3. The gate — is peak location even estimable at N=300? (M10, one rerun, runs FIRST)

Before any sweep: **is peak location a stable statistic at M2's stated N=300?** Take our current PRV-01c G0a configuration and, over **B_gate = 200 bootstrap resamples** of the N=300-per-corpus draw, compute the distribution of **which layer is the peak**.

- **Pre-committed estimability criterion:** peak location is *estimable* iff a single layer is the modal peak in **≥ 80%** of resamples. (Report the full peak-layer histogram regardless.)
- **If NOT estimable** (peak-layer spread, no layer ≥80%): **FINDING — "M2's shape is not estimable at its stated sample size"**, which is *bigger* than either reproduction outcome and costs one rerun. **The sweep is then moot and does not run.** Neither our L16 nor M2's L8 means anything if the statistic itself is unstable at N=300.
- **If estimable:** record the modal peak layer + its stability %, and proceed to the sweep.

This is M10 pointed at someone else's statistic: prove it's estimable before treating it as a target.

**Two resampling roles, kept distinct in the artifact (ruling A, 2026-09-14):**
- **RECON (pre-lock, informational — NOT the gate):** `gate10.py`, 2026-09-14 — 10 seeds resampling *which* 300 are drawn from the full cached 8-bit pools (`work/pool_8bit_full.npz`), recomputing the exact G0a MMD. Result: peak **L16 in 10/10 (100% modal)**. This resamples the **document draw (which-300)** and is what informed the decision to commit to the sweep at all. It ran before lock, so it is recon, not the registered gate.
- **REGISTERED CONFIRMATORY GATE (this §3, runs post-lock):** B_gate=200 bootstrap resamples **within** the drawn 300, modal-layer ≥80%. This resamples **within-sample** variation and is the pre-registered pass/fail.
- The two cover **different variation sources**; both are recorded in `mmd01_gate.json`. The recon (which-300) is the stronger test of sampling stability and already passed 10/10; the bootstrap (within-300) is the one that was registered, so it decides the gate. Registering the gate as A avoids ratifying a test after seeing its result (the aggregation-ruling degree of freedom — feedback_prereg_multisite_aggregation — not repeated).

## 4. The sweep — pre-committed grid over the unstated DoF

Grid axes and locked levels (the four repos are FIXED — corpus identity is ruled out; sampling *within* them is the sweep):

| Axis | Levels |
|---|---|
| A. Repo document sampling | 5 independent N=300 draws (seeds 0–4), stratified across the 4 repos by their natural size |
| B. Preprocessing | {as-PRV-01c (frontmatter-stripped, ≤2048 trunc)} × {+dedup near-duplicates} × {+drop <16 tok} → 3 |
| C. Estimator | {MMD² unbiased, MMD² biased, MMD (=√ of MMD²+)} → 3 |
| D. Bandwidth | {median-heuristic pooled, median-heuristic per-class} → 2 |
| E. Precision | {8-bit (M2's stated), bf16} → 2 |

Grid = 5×3×3×2×2 = **180 cells** (each cell = one MMD-by-layer curve; weights load once, residuals for each of the 5 draws extracted once and reused across B–E — so 5 model passes + 180 cheap MMD computations). Pooling mask/padding handling is held fixed (mean-pool over real tokens only) and noted as a residual unswept DoF.

**Report EVERY cell's peak layer** (a 180-row table) — not just matching ones. This is the anti-forking-paths artifact.

## 5. Verdict structure (mechanical)

- **Gate fails** (§3): `NOT-ESTIMABLE` — terminal FINDING, sweep does not run.
- **Gate passes → sweep:**
  - Reported quantity = **fraction of the 180 cells whose peak is at L8** (the reducer is pre-committed = fraction, honoring feedback_prereg_multisite_aggregation).
  - **fraction = 0** → `NON-REPRODUCTION` — strong, *because it was searched*: no reasonable configuration recovers M2's peak.
  - **fraction > 0** → `REPRODUCES-UNDER(config set X)` — list the exact cells; finding = "M2's shape reproduces only under configuration(s) unstated in the paper" (mild reproducibility finding). Also report which axis is decisive (does L8-peak track one axis level, e.g. a specific estimator or precision?).
  - Secondary (monotone-decline) and tertiary (magnitude/ratio) reported per cell, descriptive.
- No post-hoc cell selection; the verdict is the fraction, full stop.

## 6. Scope — what MMD-01 does NOT claim
- Does not bear on whether Assumption 3 is true (that was PRV-01c → RECOVERED). MMD-01 is about the reproducibility of M2's *empirical curve*, the paper's only grounding for it.
- Does not measure TV.
- One model (Llama-3.1-8B-Instruct), the four named repos + UltraChat (identity fixed). A non-reproduction here = "M2's shape does not reproduce from its own named corpora under a 180-cell sweep of its unstated DoF," not "M2 is wrong about the world."
- Padding/mask and the exact UltraChat user-turn selection are held fixed and named as residual unswept DoF (a follow-up axis if fraction=0 and we want to harden it).

## 7. Artifacts
- `results/mmd01_gate.json` — peak-layer histogram over B_gate resamples; estimable {bool} + modal layer + stability %.
- `results/mmd01_sweep.json` — 180-row table: (seed, preproc, estimator, bandwidth, precision) → full MMD-by-layer curve + peak layer + monotone {bool} + ratio.
- `results/mmd01_curves.json` — per-cell curves for plotting.
- `VERDICT_MMD01_<date>.md` — mechanical: gate outcome; if run, the L8-peak fraction and the verdict {NON-REPRODUCTION / REPRODUCES-UNDER(X)}; decisive axis; nothing beyond.

---

## User additions
**Lock-time rulings (the lead researcher, 2026-09-14, "A, go"):**
- **Gate = option A.** Keep the registered 200-boot / ≥80% gate; the 10-seed recon is recorded as recon, NOT ratified as the gate — registering a gate after seeing its result is the aggregation-ruling degree of freedom, not to be repeated deliberately when A costs seconds off the cached pool.
- **Items 1–3 ratified explicitly** (not by silence): name → MMD-01; N=300 fixed, *which*-300 is the swept axis; peak@L8 binding, verdict = fraction of 180 cells, monotone secondary, magnitude tertiary.
- **Recon vs confirmatory** distinguished in §3: recon resampled which-300 (stronger sampling-stability test, passed 10/10); registered gate resamples within-300. Both in the artifact.
- **a second reviewer phase-2: do NOT wait.** If a second reviewer's Q3 adds an axis, supersede → MMD-02 runs only the *new* cells; the 180 cached results stand under identical config (a supersede does not invalidate results the new document does not change).

## LOCK
🔒 **LOCKED 2026-09-14** on the lead researcher's explicit call ("A, go"), before any model load. sha256 of this file recorded in sidecar `PREREG_MMD01.md.sha256`, kept out of the file so it re-verifies without self-reference. Supersede (never patch) via MMD-02 if new axes are added; the existing 180 cells stand under identical config and a supersede only adds the new cells.
