# PREREG — PRV-03: WHERE is the provenance→behavior path, if it exists? (layer × dimension, layer first)
**Program:** Prompt_Injection · corpus ``
**Status:** 🔒 **LOCKED 2026-09-15** on the lead researcher's explicit call ("Lock it and run Phase A"), before any model load. sha256 in sidecar `PREREG_PRV03.md.sha256`. All §1 parameters ruled by the lead researcher: layer set {4,8,12,16,24,31}, three-tier Bonferroni verdict, deflation-built subspace with projection-exchange, Lambda venue.
**Target:** the causal locus of the model's behavioral role-arbitration (own behavior), following PRV-02's row-3 result.
**Provenance:** PRV-01c → RECOVERED (TV≥0.91 @ L16). MMD-01 → NON-REPRODUCTION. PRV-02 → **CORRELATE-NOT-CONTROL**: steering ŵ at L16 flipped the probe ~99% and moved behavior ≈ a random push (M=−0.0004, CI [−0.003,+0.002]). PRV-03 asks whether the provenance→behavior path exists **elsewhere** than the single L16 direction we poked.
**Cost class:** ⚠ **ALWAYS LAMBDA** (the lead researcher 2026-09-15: *"always default to lambda now, don't want runs crashing"*; post-2026-09-14 hub crash — feedback_no_heavy_local_compute_without_greenlight). No local runs for this prereg.

---

## 0. The question and the THREE hypotheses PRV-03 must separate (the lead researcher-fixed)
PRV-02 showed the L16 direction is a correlate, not the control path. M≈0 there has **three** non-nested explanations. PRV-03 is built to tell them apart, and to make a **null a finding, not a shrug.**

- **H1 — subspace (DIMENSION axis).** Provenance drives arbitration, but through a subspace of the 9–17-dim concept cone; a single needle misses it even as the linear probe flips. Resolved by a full-subspace intervention.
- **H2 — wrong layer (LAYER axis).** L16 is *downstream* of the arbitration — a trace written after the decision. Steering a record moves nothing at any dimensionality. Resolved by steering *other* layers. **NOT nested in H1.**
- **H3 — not a residual feature at all (ROUTING).** Arbitration lives in attention routing (which positions attend where); the residual-stream provenance signal is a byproduct. Consistent with every number on the table: linearly recoverable 95.5%, behaviorally role-sensitive 3.9 nats, causally inert to every residual direction we can push.

**Pre-committed:** if PRV-03 exhausts the residual-stream story (layer sweep flat AND full subspace null), that **establishes H3** — the causal path is in the attention pattern — which is a **positive result** (kin to the ARA line the B1 band mapped, and a stronger paper than "we found the direction"), NOT a failed run. → hands off to PRV-04 (attention-pattern intervention).

## 0.5 Layer-curve input (read-only, `run/prv03/setup/layer_curve.json`, 2026-09-15) — and why it sets NO steer-the-peak prior
PRV-01c per-layer role recoverability (frozen split): P_e L8 0.033 < L16 0.045 < L24 0.104 < L31 0.105 (L0 0.500 degenerate). **BUT the role-separation Δ GROWS with depth (0.201 → 0.242 → 0.362 → 0.749) while P_e worsens** ⇒ within-class spread grows faster than between-class separation: the provenance signal is **swamped by accumulating content-processing variance, NOT consumed** — its raw magnitude *builds* toward late layers. So "a trace would build late, this fades, look early" does NOT hold: raw separation does build late. **And decodability is weak evidence of causal location — exactly the lesson PRV-02 taught at L16.** The curve justifies putting L8 IN the sweep; it does NOT license an early/peak prior. **Sweep the layers because we don't know, not because the curve pointed.**

## 1. Design — layer first, subspace second (conditional). EXECUTOR-PROPOSED params, open until lock.

**Phase A — single-needle LAYER SWEEP (decisive, cheap).** Same contested harness as PRV-02 (swap, content/position fixed), single needle at **±1·Δ_L**, **ŵ and Δ refit PER LAYER** on the frozen PRV-01c pool (per-layer w_raw = coef_/scale_, unit-norm; Δ_L cached for {8,16,24,31} = 0.201/0.242/0.362/0.749; measured in setup for {4,12}).
- Layers swept: **{4, 8, 12, 16, 24, 31}** — L4 = the untested input-proximal region below 8; L12 = the 8–16 shoulder; L0 degenerate, calibration only. **Report P_e at L4 and L12 from the same pool extraction** so the decodability curve and the causal (M) curve sit on the SAME six points (that comparison outweighs either alone). L16 re-run in-harness so M is comparable across the row.
- **ŵ+Δ refit per layer needs PRV-01c pool residuals at {4,8,12,16,24,31}: {8,16,24,31} cached; {4,12} freshly extracted on-instance (model run) as Phase-A setup.**
- **Intervention = swap at EVERY layer** (M comparable across layers and against PRV-02's L16 value).
- Per layer: baseline (shared, layer-independent, 720 once) + swap +1·Δ_L (ŵ) + variance-matched control +1·Δ_L + **per-layer, per-span manip-check ≥80% each** (the steer must land at that layer or its null is uninformative).
- **M per layer**, paired template-cluster bootstrap of the whole ratio (as PRV-02).

**Phase A verdict (mechanical) — three tiers, Bonferroni across the 6-layer family (α = 0.05/6; percentile CI at the 0.417 / 99.583 tails):**
- **LOCALIZED:** |M| ≥ 0.10 AND CI excludes 0 at α=0.05/6 → Phase B at that layer; H2 supported.
- **WEAK:** 0.02 ≤ |M| < 0.10 AND CI excludes 0 at α=0.05/6 → Phase B at the argmax-|M| layer, reported as partial mediation. (Exists so a clean 0.07 isn't mis-binned FLAT and H1 declared on a real effect — the row-3 error in reverse.)
- **FLAT:** everything else → H1 live → Phase B at L8. (|M|≥0.10 = 0.39 nats against the 3.9-nat B, reader-holdable; Bonferroni closes the ~26% family-wise error that bare "CI excludes 0" leaves at these ~0.003 half-widths.)

**Phase B — SUBSPACE intervention (conditional on Phase A FLAT or WEAK).** Subspace built by **iterative deflation, k MEASURED not assumed:** fit ŵ₁ (probe on residuals); project residuals ⊥ŵ₁; refit the probe on the deflated residuals → ŵ₂; repeat. **Stop when refit P_e ≥ 0.45 (chance), cap k = 25.** The **deflation curve (refit P_e vs # directions removed) is a result in its own right** — the first independent check on the concept-cone 9–17 estimate from a *different* instrument, turning that parameter into a tested prediction.
  - *Rejected bases (recorded):* PCA-of-per-class-residuals → top directions are content variance, so the treatment steers mostly content and the variance-matched control becomes indistinguishable from it by construction. LDA → between-class scatter has rank C−1 = 1 for two classes → hands back the single needle.
- **Intervention = full-subspace SWAP by projection EXCHANGE (NOT a scalar multiple of anything):** compute each span's projection onto the recovered k-dim subspace and **exchange the system-span and user-span projections.** Control: a random k-dim subspace matched on dimension AND projection-norm statistics, same exchange operation.
- **Manip-check (Phase B) is MORE tautological than Phase A** — the projection is set exactly, so the probe flips by construction. Run it as an implementation sanity check with **explicitly ZERO inferential weight** (same caveat as PRV-02's 99%).
- **Phase B verdict:** subspace-swap M CI excludes 0 → **USES-VIA-SUBSPACE (row 2, subspace)**; M≈0 (manip trivially passed) → **RESIDUAL-STREAM-CLOSED → H3 established** (causal path is attention routing) → PRV-04. Pre-committed positive-null.

## 2. Standalone finding to log in its own right
**B = −3.915 nats: the model obeys the USER slot over the system slot in a content-matched contested benign design** (PRV-02 Gate 0, template-cluster CI [−4.78,−3.04]). Independent of M. Set against M≈0 it is the sharpest sentence in the corpus: **strongly role-sensitive in behavior, near-perfect role representation in the residual stream, and nothing connects the two along any direction we can steer.** Record as its own line, not a footnote to M.

**Record (PRV-02 half-arms, confirmed from artifact 2026-09-15) — M≈0 is genuine, not a cancellation.** The one-sided half-arms DID run at ±1·Δ: sys-only (−1·Δ) dY = +0.00914, usr-only (+1·Δ) dY = +0.03755, sum 0.04669 ≈ swap 0.05060 (additive). Both moves are small and **same-sign** (largest ~1% of B) ⇒ the row-3 null is real "nothing moves," NOT two large opposite effects cancelling. PRV-03 builds on M≈0 on solid ground.

## 3. Scope / what a null means (pre-registered, not discovered)
A flat Phase A + null Phase B does not mean "no effect found" — it **closes the residual-stream hypothesis and establishes the attention-routing one (H3)**, which is the finding. Claim ceiling stays: this model, benign role-arbitration, the corpora and directions named. Does not claim provenance is never used; claims the residual-stream provenance representation is behaviorally inert and the causal path is elsewhere (routing).

## 4. Compute discipline (in force, feedback_no_heavy_local_compute_without_greenlight)
Phase A ≈ pool-extract L4/L12 + baseline(720) + {swap,ctrl}×720×6 layers + manip ≈ ~10k forwards; Phase B larger. **ALWAYS LAMBDA** (the lead researcher, 2026-09-15: *"Always default to lambda now. Don't want runs crashing."*) — sized, auto-terminating watchdog, cost stated before launch, results synced back. **No local runs for PRV-03** (the 2026-09-14 hub crash is why). Per-layer ŵ refit is CPU on the extracted pool reps (runs on-instance).

## 5. Artifacts
`run/prv03/setup/layer_curve.json` (done), `w_hat_L{8,16,24,31}.npz` (per-layer, refit), `results/prv03_phaseA.json` (per-layer M, manip rates, dose), `results/prv03_phaseB.json` (conditional), `VERDICT_PRV03_<date>.md`.

---

## User additions
**the lead researcher's scope (2026-09-15), fixed:** layer × dimension, LAYER FIRST. Three hypotheses (H1 subspace / H2 L16-downstream, NOT nested / H3 attention-routing). A null PRV-03 ESTABLISHES H3 as a positive finding, not a shrug. B=−3.9 logged standalone.

**the lead researcher's lock-time rulings (2026-09-15, "Lock it and run Phase A"):**
1. **Reading correction:** the Δ column grows with depth while P_e worsens ⇒ signal SWAMPED not consumed; raw separation builds late. **No steer-the-peak/early prior** — decodability is weak evidence of causal location (PRV-02's own lesson). Sweep agnostically. (§0.5 rewritten.)
2. **Layer set = {4, 8, 12, 16, 24, 31}** (+L4 input-proximal, +L12 shoulder); report P_e at all six from the same extraction so decodability + causal curves share the six points; swap at every layer; L16 re-run in-harness.
3. **Three-tier verdict, Bonferroni α=0.05/6:** LOCALIZED |M|≥0.10 & CI-excl-0; WEAK 0.02≤|M|<0.10 & CI-excl-0 (→ Phase B at argmax, partial); FLAT else (→ H1, Phase B at L8). WEAK tier prevents the reverse row-3 error.
4. **Phase-B subspace = iterative deflation, k MEASURED** (deflate ⊥ each ŵ, refit, stop at P_e≥0.45, cap 25; the deflation curve is a result / independent check on 9–17). **Intervention = projection EXCHANGE between spans (not scalar add); control = random k-dim matched on dim+proj-norm, same exchange; manip-check = sanity only, ZERO inferential weight.**
5. **Venue = Lambda, ALWAYS** ("don't want runs crashing").

## LOCK
🔒 **LOCKED 2026-09-15** on the lead researcher's explicit call ("Lock it and run Phase A"), before any model load. sha256 of this file in sidecar `PREREG_PRV03.md.sha256`, kept out of the file so it re-verifies without self-reference. Runs on Lambda (always). Supersede (never patch) via PRV-03b; PRV-04 = attention-pattern intervention (fired by an H3 result).
