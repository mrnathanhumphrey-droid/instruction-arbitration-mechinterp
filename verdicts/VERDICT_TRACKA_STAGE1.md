# VERDICT — Track A, Stage 1: the instruction-hierarchy gate (Llama-3.1-8B-Instruct)

> Every number below is **conditional on a gate that did not pass (INDETERMINATE)**. Calls are per-readout at 90%,
> uncorrected (a Holm column is reported beside them, descriptive).
>
> **Update (reference check).** Our implementation of the IHDec metric (§2's last bullet, the only Stage 1 readout that
> uses it) has been validated against the reference recipe in fp32: max |Δ| 1.3e-5 over 300 items, both run on the
> same machine, against a pre-stated 1e-3 bar. An earlier bf16 comparison had shown a gap (188/300 items within 0.01); that
> gap matches each implementation's own bf16 rounding, which is unbiased (signed mean bf16 − fp32 within ±6e-4, every
> interval containing zero). The earlier label "implementation not validated against reference" is withdrawn.

## What Stage 1 is
A pre-registered study (prereg manifest `c5c4f7c2…`, gate control locked `3e82eb0d…`; amendments locked before each
step's data were read, hashes below) on Llama-3.1-8B-Instruct @ `0e9e39f2`: when a system message and a user message give
conflicting instructions, what decides which one the model follows — **which role** the message came from, or **which
came last** — and where in the forward pass is that decision represented and carried? One full run on a single H100
(bf16, SDPA, deterministic kernels); the run is bit-reproducible (2,000 / 2,000 repeat rows bit-identical) and every
later analysis box regenerated its rows and checked them bit-exact against the saved outputs before reading anything.

## 1. The gate: INDETERMINATE
The locked gate compared the shift caused by a symmetric role re-render (SYM-A) against the shifts caused by eight
matched text fragments, on four legs (behaviour, an internal L16 probe, the system- and user-slot log-probabilities):
PASS iff the interval for SYM-A's excess lies inside ±SESOI, FAIL iff wholly outside, else INDETERMINATE (93% intervals,
templates as clusters). Leg 1 (behaviour) INDETERMINATE (−0.42 [−0.80, −0.05], SESOI 0.50),
leg 2 (internal probe at L16) PASS, leg 3 system-slot INDETERMINATE, leg 3 user-slot PASS. No leg FAILED; by the locked
precedence the gate is INDETERMINATE. Everything below is read under that label.

## 2. Behaviour: the later message wins, about 3× more than role decides
On contested items (Y = log-odds of the system's target; > 0 favours the system):
- **Order: −3.12 [−3.55, −2.70] nats** — the later message wins.
- **Role: −1.04 [−1.30, −0.78] nats** — where role matters at all, it slightly favours the **user**, not the system.
- Same sign in every item source; a bridge to the older ORD-01 battery agrees (difference +0.15 [−0.08, +0.39]).
- The paper metric of IHDec computed on our own twin stimuli tells the same story: a position term +0.164 [+0.134, +0.194]
  about 2.3× a role term +0.071 [+0.057, +0.085]. (IHDec's own published baseline was **not** reproduced on IHEval with our
  reconstruction of their pipeline. Our metric code matches theirs in fp32, so the code is not the cause; what remains is
  their unreleased data converter, the pass definition, generation settings and how the bars are pooled. IHEval outputs
  are not published here under its licence.)

## 3. Representation: the model knows who said what
Held-out decodability (19 held-out templates), layers 8–16: role 0.78–0.95 (mean-difference probe) / ≥ 0.994 (logistic);
order 0.97–0.99 / 1.00. The model represents both role and order almost perfectly — and the later message still wins.

## 4. Editing role at layer 8: what happens downstream
Role edits at L8 (a clamp of the ≤ 25-dimensional role subspace, 7 doses), measured downstream along each layer's own role
probe, both probes, in absolute units (Amendments 3–3.4, locked before these readouts):
- **The edit is carried forward, not repaired.** Measured along the layer's role readout in raw units, the edit's effect
  is 0.81 / 0.50 / 0.48 / 0.69 / 1.11 of its L8 size at L9 / 12 / 16 / 24 / 31 — back to about full size at the last
  layer. The standardized "fraction regrown" (≈ 0.92 at late layers) mostly reflects the within-class spread growing ≈ 16×
  with depth, not repair. The fraction is the same at every dose and in every prompt layout.
- **Why it persists is not specific to role.** Against random directions drawn at matched variance (1×, 9×, 38× an
  isotropic direction, and the role edit's own variance), retention rises with variance and the role edit sits on that
  curve. Role lives in high-variance directions; that is why its edits persist.
- **What is specific to role is where the edit goes.** A push along role keeps 54–64% of its displacement on the role
  readout at L9 and 14–15% at L31; every random, order, filler or variance-matched push puts 2–14% there. The edit turns
  with the role representation as it changes direction across layers.
- **Erasing role barely changes the answer.** Complete linear erasure of role at L8 on the instruction text (LEACE, rank-1,
  role cross-covariance erased to 2.5e-14) moves the model's answer by only −0.06 to +0.09 nats, against a −1.04 behavioural
  role effect. That erasure touched only the instruction text.
- **The role headers carry part of it.** Erasing role at the role-HEADER tokens at layer 8 (a separate rank-1 eraser)
  pulls every prompt layout's answer toward zero by 0.21–0.32 nats (≈ 5–15% of its size), weakening the decision in the
  direction of whichever message came later; erasing headers alone does as much as headers plus text. By layer 16 the
  headers no longer add anything. Most of the decision (2–4.7 nats) still comes from elsewhere.
- At L9 the two probes disagree (logistic sees 0.39 regrown where mean-difference sees 0.22): no call is made there.

## 5. Smaller readouts
- **Length ladder (§2):** inserted text shifts the answer by −0.10 nats per token on behaviour, with a step between 5 and
  10 inserted tokens; the internal readout drifts −0.024 per token.
- **Noise floor (§7):** kernel jitter SD 0.20 nats on behaviour (pilot 0.23), 0.005 on the internal readout.
- **Later insertion (§9):** where a neutral fragment is inserted matters, in a build-dependent way; no pre-declared pattern
  matched. Descriptive only.

## 6. Instrument findings (useful beyond this study)
- **numpy on the cloud hosts was wrong.** On Lambda H100 hosts (Intel Xeon Platinum 8480+), numpy 1.21.5 with its bundled
  OpenBLAS 0.3.20 (kernel "Cooperlake") returns wrong results for square dense matrix products (relative error 1.5 at
  n = 4,096, also single-threaded), QR and symmetric eigensolves; matrix–vector products and tall XᵀX are correct. It
  silently corrupted one analysis arm (a LEACE eraser came out with singular values 2.3e6, 4.5e4, … instead of rank 1). All
  dense linear algebra now runs in torch float64 on the GPU, and every check suite keeps a square-product test. Anyone
  running numpy linear algebra on these hosts should check.
- **Ratio readouts need large denominators.** A "fraction of the clean signal" readout failed its own positive control in
  the cells where the clean margin was small (≈ 0.09); an absolute-units readout passed in all of them.
- **Plants can be degenerate.** A planned known-answer plant was fixed by construction (linear probes read at the layer the
  plant was applied) and could not fail; it was replaced before running. A resampling plant that kept template effects
  fixed could not detect a wrong interval; it was rebuilt (two-stage resample) and validated on synthetic data first.
- Measured interval coverage (from those plants on the real data): 87.1–87.8% for nominal 90% intervals; the calls above
  are slightly anti-conservative by that amount.

## Process deviations, stated
§5 was first read before §4 (out of the locked order); it was re-read after §4 and the re-read is the record (identical
except one item scored differently by an unseeded scorer, since pinned). One analysis launched while a planted check was
still failing on a floating-point artefact of the plant (script unchanged).

## Locked files
Stage 1 prereg manifest `c5c4f7c2…` · gate control `3e82eb0d…` · §4 Amendment 3 `826b0284…`, 3.1 `dba68b34…`, 3.2 `012493ea…`,
3.3 `af2c6cb2…`, 3.4 `96b398c1…`. Code and the locked files: to be added to this repository.
