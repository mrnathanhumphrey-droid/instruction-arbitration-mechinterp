# HUNT-DRIFT-01 — spec as given by Nate (2026-10-24, pasted). Saved verbatim for the record; plan in PLAN.md.

# HUNT-DRIFT-01 — Instruction persistence under free drift (Track A side hunt)

## Status and fences (read first)
- Exploratory side hunt. NOT part of the Track A stage-1 preregistration. All outputs are labelled exploratory. Nothing here may be used to revise the stage-1 prereg.
- Separate folder: `trackA/hunts/drift01/`. Separate instance, separate cost ledger. Do not touch, import from, or alter any stage-1 file, input, runner, seal, STATE entry, instance or ledger.
- BLINDING:
  - Every drift context is system-first with correct headers (ORIG-style).
  - No user-first, symmetric, or block-swapped builds until the stage-1 gate verdict is in STATE and §3–§5 are unsealed. A role-vs-position extension of this hunt is registered separately after the unseal.
- Items: use only material already open, i.e. the pilot / RDV-01 old battery's contested items, rendered ORIG-style. No stage-1 templates.
- Read-only first: read this spec and the relevant pilot/RDV-01 code. Show the full plan, with every seed, count and threshold filled in, plus a cost projection, before anything runs. Nathan fires every launch.

## Question
When a system instruction is followed by a long stretch of free, task-less drift, does the system instruction keep its authority over a later contested user instruction?
If authority decays, is that decay caused by distance (tokens between instruction and conflict) or by the content of the drift?

## Model and versions
- Llama-3.1-8B-Instruct, pinned to the stage-1 §7 versions (torch 2.7.0, transformers 4.46.0).
- Same chat template and same SDPA attention path as stage-1 readouts.

## Phase 1 — Generate drift transcripts (sampling), then freeze them
- **Drift modes:**
  - M1 **solo:** the agent continues on its own. Each user turn is the fixed minimal string "Continue."
  - M2 **pair:** two agents, A and B. Each sees its own messages as assistant and the other's as user. A carries the system instruction; B carries a neutral system message.
  - M3 **think/math:** solo, seeded with one open-ended math prompt, fixed in the plan.
- **Opening prompts** (the persona confound control):
  - P-none: no persona;
  - P-neutral: a plain neutral assistant message;
  - P-curious: a "naturally curious" persona, mirroring the MIT setup.
- **Sampling:** temperature in {0.7, 1.0}; a fixed seed list, with the seed count set in the plan; max turns fixed in the plan, up to the context budget.
- **System instructions:** the system imperatives from the open old-battery contested items. Each transcript is generated under one item's system instruction.
- **Freeze:** every transcript is saved, hashed, and listed in a manifest. All later phases are teacher-forced on the frozen transcripts. No re-generation.

## Phase 2 — Probe authority at drift depth k (teacher-forced, no generation)
- **Probe insertion:** after k drift turns, insert the item's contested user instruction as the next user turn. Read the answer position.
  - k ∈ {0, 1, 2, 4, 8, 16, 32, 64}, capped by transcript length.
  - Record each probe's distance both in turns and in tokens.
- **Readout:** Y_signed and log P(compliant), with the same definitions as Track A. Re-implement them here and check they match the pilot's own values bit-for-bit on a sample.
- **Conditions at each k:**
  - C-drift: the real frozen drift transcript.
  - C-filler: drift replaced by length-matched neutral filler that is not conversation, matched in tokens. **This is the distance-vs-content contrast.** Set the filler source in the plan; reuse the stage-1 word-pool pipeline if it can run without touching stage-1 files.
  - C-shuffled: drift turns taken from a different seed's transcript of the same mode. This tests whether it is the agent's own history or just drift-like text.
  - C-refresh: the real drift, with the system instruction restated immediately before the probe. Positive control: it should restore authority.
  - C-none: no system instruction at all. This is the floor.
- **Authority fraction at k:** A(k) = (Y(k) − Y_none) / (Y(0) − Y_none), per item, then pooled.

## Phase 3 — Analysis (fixed in the plan before Phase 2 runs)
- **Primary:** A(k) curves per mode, persona and temperature, with a bootstrap clustered on item and seed (seed fixed in the plan).
- **Primary contrast:** C-drift vs C-filler at matched token distance.
  - Drift < filler → decay is content-driven.
  - Drift ≈ filler → decay is distance-driven.
  - Fix the equivalence band in the plan; start from Track A's JITTER floor in Y_signed units.
- **k_half:** the smallest k at which pooled A(k) ≤ 0.5. Report "not reached" if it never does.
- **Secondary:** persona effect (P-curious vs P-none); mode effect (M1, M2, M3); and whether C-refresh restores A to within the band of 1.

## Phase 4 — Drift geometry (arc 2, riding on the same frozen transcripts)
- **Convergence:** per mode and persona, the pairwise distance between seeds' transcripts over turns, using mean-pooled L16 residuals of each turn from the same model. No new embedding dependency.
- **Attractors and loops:**
  - per-turn n-gram repetition rate;
  - self-similarity between turn t and turn t−j for j up to a lag fixed in the plan;
  - a pre-stated rule for flagging a periodic loop.
- **Internals over turns:** the HUNT-GEO-01 dissipation estimates (D1, D2) at the last token of each turn, across layers.
  - This depends on HUNT-GEO-01's estimator validation passing first. If it hasn't passed, Phase 4's internal measures wait. Behaviour-level measures don't.
- Descriptive only. Any attractor claim needs agreement across seeds, under a pre-stated rule.

## Deliverables
- The plan (all seeds, counts, thresholds and bands filled in) and the cost projection, shown before any run.
- The transcript manifest with hashes; the Phase 2 readout table; A(k) curves; the drift-vs-filler contrast; k_half; the Phase 4 tables; the cost ledger.
- STATE-style hunt log in `trackA/hunts/drift01/LOG.md`, kept separate from stage-1 STATE.

## User additions
(Nate, 2026-10-24: "this can run in parallel or jump the line potentially"; "a convergence angle worth chasing".)
