# PREREG — CAL-01: calibrate the estimator M̂ = −ΔY/2B against known ground truth

**Status: LOCKED 2026-09-21.** the lead researcher spec ("price it, lock it, run it"; "we good to run it"). Hand-built toy, real
harness, NO forwards on Llama. Runs on CPU (tiny hand-set transformer; the GPU/8B ban does not apply — no model
download, no GPU, no blast radius). Chained to PREREG_RES05.md sha256
`f0b75186bb0068442014cea854131c438183d10e78360eb9b1b157bd47ef3f3c`.

## §1 What is being tested
NOT the model — the ESTIMATOR. KDR, H4, RES-02, RES-04, RES-05 share M = −ΔY/2B, all-layer patching, the same battery
and bootstrap. Their agreement near half is as consistent with **estimator saturation** as with a **property of the
model**. This measures which.

## §2 Construction
A hand-built transformer — NOT trained, weights set by hand, so ground truth is by construction. It is hookable by the
EXISTING patch harness at the same points (torch `register_forward_hook` on `model.model.layers[i]`, overwrite
`out[0][0,pos,:]`), and the hook / run / capture / M_of / bootstrap code is copied VERBATIM from the RES-05 runner — a
reimplementation would test a story about the instrument, not the instrument.

Arbitration is a KNOWN convex mixture with weight w:
- **Channel A** — a role feature written into the residual at the imperative-span positions (residual dim 0). Reachable
  by the span exchange.
- **Channel B** — the readout position reads the header token's role (residual dim 1) directly, outside the spans.
  Unreachable by a span edit.
- Output logit difference D = K·[w·A + (1−w)·B], scaled so the toy's **baseline B (role effect) ≈ −3.9 nats** (K set so
  Y_signed baseline = −3.9, matching the real battery's regime; M is normalized by 2B, so an unmatched B would put the
  estimator in a different regime and the calibration would not transfer).
- Readout = first-token logP difference over two single tokens (DONE/READY analogs), same shape as the real battery.
- **An unbiased estimator returns M̂ = w** (proven by construction: cross-role span patch flips A only; ΔY = 7.8·w;
  M = −ΔY/2B = w).

## §3 Sweep — three knobs (20 cells)
- **w ∈ {0, 0.25, 0.5, 0.75, 1.0}**
- **Re-derivation {off, on}:** "on" recomputes Channel A at every non-aggregator block from the header token, so a
  layer-L edit is overwritten at L+1 UNLESS the harness re-patches after that block. H4's all-layer patching is supposed
  to defeat this. This checks whether it does (the patch is applied to each block's OUTPUT, after the block's internal
  re-derivation).
- **Depth {4 layers, 32 layers}:** partial purchase on the toy-isn't-8B problem. Patched layer set follows the real
  harness rule: `LAYERS = range(nlayers//4, nlayers)` (depth-32 → range(8,32), EXACTLY the real config; skips the first
  quarter and the final block's output, as the real runs do). Aggregator = final block; it reads its INPUT (the patched
  output of block nlayers−2), mirroring how the real last block sees patched spans.
- Report **bias = M̂ − w per cell with CI**, plus the **slope of M̂ on w** per (rederiv, depth) group.
- **Sensitivity control (diagnostic, outside the 20 cells):** one cell (w=1, rederiv on, depth 32) re-run with a
  DELIBERATELY inadequate patch set that skips the last re-deriving block — must collapse M̂→~0, proving the toy can
  DETECT an artifact (so "bias≈0 in the 20 cells" is a real negative, not insensitivity).

## §4 Readings (pre-committed)
- **Bias ≈ 0 everywhere** → no artifact found under any mechanism we could construct. The ~half survives (see §6 asymmetry).
- **M̂ pins near 0.5 regardless of w, in any cell** → the artifact is real and that cell names its mechanism. Every M in
  the arc is reinterpreted in one stroke.
- **Bias ≈ 0 at 4 layers, negative at 32** → depth-dependent attenuation. The real-model M's become FLOORS, not
  estimates, and the four-instrument agreement is explained by shared machinery.
- **Bias ≈ 0 with re-derivation off, negative with it on** → all-layer patching does NOT defeat re-derivation. Contradicts
  H4's founding premise; the biggest correction available here.

## §5 Validity gates (all must pass before any cell is read)
1. At w=1.0, verify by DIRECT INSPECTION that the span patch actually replaces Channel A in the hidden state (patched
   hs[L] at span == twin value) — a mechanically broken patch gives a false artifact. HALT if it fails.
2. ACTUAL harness code — same hook points, same run/capture, same bootstrap, same normalization, same VOID discipline
   (copied verbatim from RES-05).
3. Toy baseline B reproduces −3.9 (±0.2) before any cell is read. HALT otherwise.
4. Sensitivity control (§3) must collapse to ~0, else the toy is insensitive and the null is uninformative.

## §6 The asymmetry (write into the verdict, not the discussion)
This CAN kill the ~half. It CANNOT certify it. A clean curve licenses **"no artifact found under the constructed
mechanisms,"** NEVER **"the number is real."** This sentence goes in the verdict file.

## §7 Artifacts
`cal01.json` (per-cell M̂, bias, CI; slopes; sensitivity control; B; gate results), `cal01_arms.csv`,
`cal01_peritem.npz`, `VERDICT_CAL01.md`, chained to RES-05. CPU, deterministic (seeded), no watchdog/Lambda needed
(local toy). No ledger entry (no cloud spend).

---
## LOCK
**LOCKED 2026-09-21.** Construction (§2), sweep + knobs + sensitivity control (§3), readings (§4), validity gates (§5),
asymmetry (§6) fixed. Executor specifics (d_model, dim assignments, K/c constants, noise σ, NTMPL) in the runner. sha256
in sidecar `PREREG_CAL01.md.sha256`, chained to RES-05 `f0b75186…`. No edit after this line without a superseding ruling
+ re-lock.
