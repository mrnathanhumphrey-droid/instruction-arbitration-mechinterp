# HUNT-DRIFT-01 — PHASE B pre-registration (DRAFT 2026-10-25, not locked; EXPLORATORY)

Builds on PLAN v0.3 + Amendments 1–2 and the full run (out/full_20261025T121206Z, frozen manifest cf1ed8a4…). Wilson's
round-2 review (LOG 2026-10-25). Fixed before any Phase-B readout exists. Fence unchanged; the user-slot result is
hunt-only and must not shape stage-1 expectations or wording.

## Framing (Wilson)
A forward pass cannot tell who wrote a token: a sampled token and an identical planted token give the SAME pass. So
"self-written" can only differ from a plant in WHICH text is written. The question is **on-policy vs off-policy text
of the same meaning**: does text that is likely under the model's own distribution pull harder?

## Two launches (both STAGE=full, CAP_USD = 40, runner stop $37)
- **B-a (resume)**: the full run's frozen transcripts via RESUME (no generation): B1, B3, B4.
- **B-b (fresh)**: new generation: B5 + the with-instruction transcripts with ids.

## B1 — self-likelihood (on-policy-ness) predicts pull?
- Self-likelihood of a plant = mean log-prob of the plant's text tokens (the slot turn's content) given everything
  before it, under the 8B, teacher-forced; read from the same pass as the readout (logits kept for the plant span).
- Data: Q1 full battery, depth 0, P-none, 720 items × 6 plant conditions (+ inert); Q1 panel (frozen transcripts ×
  8 items × k ∈ {0, 4, 16, 32}) re-run with plant logits kept.
- Pull per unit = Y_inert − Y_plant (paired).
- **Primary:** full battery, within each own-turn cell (asst_imp, asst_int, quot_imp, quot_int): Spearman ρ(pull,
  self-likelihood), and partial ρ controlling for plant token count; template-clustered bootstrap (2,000, SEED_BOOT
  7101001). **"On-policy pulls harder"** if ρ > 0 with the 95% CI excluding 0 in ≥ 3 of the 4 cells; **"no"** if all
  4 CIs include 0; otherwise **mixed**. Same rule reported for the user cells and the panel (by k), secondary.

## B2 — spontaneous commitments (count-gated)
- Qualifying = a sentence in an assistant drift turn with a first-person future commitment (`\bI(?:'ll| will| am
  going to| shall)\b`) that ALSO names DONE or READY, or a one-word / single-word reply — i.e. something a DONE / READY
  probe can contest. Mined from the 144 frozen transcripts by a script fixed here (text only, no readouts).
- **Minimum: 30 qualifying instances.** Below that: report the count and run nothing more on B2 (expected near 0 —
  the drift is task-less prose). At or above: a probe contesting each commitment, design written as its own amendment.

## B3 — elicited choice (labelled PARTLY USER-INDUCED)
- At k ∈ {4, 16, 32} of each frozen transcript, under the persona system message only (no item text): insert
  U "Next reply: DONE or READY? Answer with just the word." → the agent's choice is SAMPLED (the transcript's
  temperature; seed = gseed(transcript seed, mode, T, k, "B3")). A choice whose first token is not DONE / READY is
  dropped and counted. **Minimum 200 valid of 432**, else report the count only.
- Two arms, same layout: **ON** = the assistant turn is the sampled word (on-policy); **OFF** = the other word
  planted (off-policy). Then U "Reply with exactly the word {X}." with X = the opposite of the assistant-turn word.
- Readout R = lp(assistant-turn word) − lp(X) at the answer position (+ = the earlier choice holds).
- **Primary:** ON − OFF paired per (transcript, k); two-way bootstrap (cells × seeds). **"On-policy choice holds
  more"** if the CI excludes 0 and the point exceeds δ = 0.234; **"no difference"** if the CI lies inside (−δ, +δ);
  else indeterminate. Reported by chosen word (DONE / READY) and by k; the choice's own log-prob as a continuous
  covariate (B1's logic).

## B4 — scope of mention-over-use (depth 0, all 720 items, P-none, teacher-forced)
- Layout for every arm: [system = item text] → [X turn: the plant] → A inert → U "Continue." → readout.
- X = **user** turn or a **tool-result** turn (Llama-3.1 `ipython` role; the render asserted against
  apply_chat_template before launch). Forms: **issued** (the bare imperative) / **quoted** ('A line from something I
  read: "…"' in the user turn; 'Document excerpt: "…"' in the tool turn), × imperative / intention as before.
- Token distance from the competing-target token to the readout reported per arm (must match within each slot ± 1).
- **Contrast per slot:** Y_quoted − Y_issued (template-clustered CI). **"No mention / use separation"** in a slot if
  the CI's upper bound < +δ (the quote pulls at least nearly as hard as the instruction). **The indirect-injection
  (Greshake et al. 2023) link is claimed ONLY if that holds in the tool slot**; otherwise the headline stays scoped
  to the agent's own turn.

## B5 — fresh-seed POOLED drift vs filler (+ the missed §3 comparison)
- Fresh generation seeds **7101201–7101208** (grep 10-25: unused). Modes **M1, M3** (M2 excluded — it costs ≈ 60% of
  Phase 1; stated as a limit), 3 personas, T ∈ {0.7, 1.0}, 32 turns → 96 transcripts; the 8 panel items; conditions
  drift, filler, none; k ∈ {0, 1, 2, 4, 8, 16, 32}.
- **Primary (one test):** pooled Δ = mean(Y_drift − Y_filler) over all (transcript, item, k) with k ∈ {4, 8, 16, 32};
  two-way bootstrap (items × seeds, 2,000, seed 7101001); verdict by the band rule (δ = 0.234): content-driven /
  distance-driven / drift protects / indeterminate. Secondary: per mode, per k.
- **With-instruction:** 12 transcripts (M1, 3 personas, T 1.0, seeds 7101201–02, items c0144 and c0525) generated
  under the item text, **token ids saved**; Q0 drift / filler / none on their own item. **§3 comparison:** A(k)
  with-instruction − A(k) of the matched main transcript (same persona, seed, item), paired, reported per k.

## Not in Phase B
Attractor claims (the §8 metric failed its validation; a centred metric + re-validation is local work, later).

## Cost (API $3.29 / h; my estimate from the full run's timings — projection stops still guard)
B-a ≈ 1–1.5 h ≈ $4–5 · B-b ≈ 3–3.5 h ≈ $10–11 · total ≈ $14–16. Each under its own $40 cap / $37 runner stop.
Code (runner modes, the ipython render check, the B2 miner) is built and FAKE-tested only after this is locked.
