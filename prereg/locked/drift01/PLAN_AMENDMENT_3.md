# HUNT-DRIFT-01 — AMENDMENT 3 (DRAFT 2026-11-01, not locked; EXPLORATORY)

Amends `PLAN_PHASE_B.md` (1a660770…, locked). Written after the B-a readout (`out/phaseBa_20261101T190722Z/`) and
Wilson's round-3 review; it adds arms that test a result seen in that readout, so everything below is fixed before
its own data exist, but it is NOT blind to B-a. Fence unchanged (hunt-only; nothing here shapes stage-1).

## A3.0 What it is for
B-a + the full run suggest: the model discounts a quoted line, relative to the same line issued, in the user turn
(+1.44) and the tool turn (+1.79), but not in its own turn (quoted − issued −0.51 imperative, −0.76 intention).
The derived own − user interaction (imperative −3.06 [−3.72, −2.38]) compares rows that differ in layout and in
distance to the readout (14 vs 26 tokens), and the tool slot also differs in wrapper. A3.1 removes those three
confounds; A3.2 settles the panel readout gap; A3.3 pins prefill chunking from here on. B3's redesign is dropped
(Wilson: it would ask a different question, already answered by Q1). B-b stays as locked and fires separately,
after this, under A3.3.

## A3.1 Matched arm — one skeleton, slot × wrapper × form
- **Skeleton (every row):** [system = item text] → three turns, one per role — user, assistant (the agent's own
  turn), tool (`ipython`) — → U "Continue." → assistant header (readout). Depth 0, P-none, all 720 items,
  teacher-forced, fresh passes (no cache branching).
- **The plant sits in exactly one of the three turns, and that turn is always LAST** (directly before the probe);
  the other two keep the order user → assistant → tool. So the plant → readout distance does not depend on the slot
  by construction (it is the plant's own tail + the probe). The one inherent difference: the tool turn's content
  is JSON-encoded, as Llama-3.1's template renders that role (render asserted against apply_chat_template, as in
  piece 2) — it adds the escaped / closing quote tokens and cannot be moved. Distance is reported per arm and must
  match across slots within ± 2 tokens per item.
- **The two non-plant turns** carry inert text of the plant's token count (± 2; the tool one JSON-encoded like any
  tool content): "Okay, still thinking." + word-pool words, the B4 / Q1 inert. One inert set per item, shared by
  every arm (paired contrasts).
- **Arms:** slot {own, user, tool} × wrapper {issued (bare), W1 'A line from something I read: "…"', W2 'Document
  excerpt: "…"'} × form {imperative, intention} = 18 arms + 1 all-inert row per item = 13,680 rows. Both wrappers
  in all three slots (Wilson 2), so the wrapper is not confounded with the tool slot.
- **Δ(slot, wrapper, form) = Y_quoted − Y_issued** (+ = the quote pulls less than the instruction), per item.
- **PRIMARY (one test, direction pre-stated):** imperatives, wrapper W1: **I = Δ(own) − Δ(user)**, per item;
  template-clustered bootstrap (2,000, SEED_BOOT 7101001); **predicted NEGATIVE** (the own turn discounts quotes
  less). Band δ = 0.234 (the pilot's JITTER SD). Verdict: **"own-turn quotes are discounted less" if the CI's upper
  bound < 0 and the point < −δ; "no interaction" if the CI lies inside (−δ, +δ); otherwise "indeterminate".**
- **Secondary (reported, no verdict carries the headline):** intention forms (the user-turn intention cell barely
  separated in B4, +0.32 [−0.35, +0.96]); W2; own − tool; each slot's Δ by wrapper; Y_issued per slot minus the
  all-inert row (how hard an instruction pulls from each slot at matched distance).
- Two consecutive user turns arise when the plant is in the user slot (plant, then "Continue."): a stated limit
  of the skeleton, the price of matched distance.

## A3.2 Chunk test — the B-a panel gap
- 24 transcripts (8 per mode, drawn with seed 7101001) × the first 2 panel items × K_Q1 × the 7 Q1 conditions,
  each computed TWICE on one instance: (a) the full run's cache chunking (extend at every k ∈ K_Q0 ∪ K_Q1) and
  (b) B-a's (extend at k ∈ K_Q1 only).
- **Prediction: (a) reproduces the full run's q1 readouts bit-for-bit and (b) reproduces B-a's b1_panel readouts
  bit-for-bit, on every row.** Holds → "the gap is prefill chunking" (bf16 kernel shape; the free check found 0 of
  165 (transcript, k) exact when the smallest chunk was < 96 tokens, 95% when ≥ 256). Fails on any row → reported,
  the cause stays open.
- Reported numbers, stated: the hunt's Q0 / Q1 headlines are the full run's; B1's panel uses B-a's own readouts.

## A3.3 Prefill chunking is pinned from here on (every later run, B-b included)
Every prefix is prefilled in ONE pass (whole prefix; at most 24,576 tokens), never split at the k cut points.
Branched readouts at several k are taken by probing in DESCENDING k and cropping the cache between probes, so
every k reads the same cached values. (If one pass ever runs out of memory: a fixed 4,096-token grid from
position 0, logged — never boundaries that depend on k.) The runners carry this as code; the repeat check stays.
This changes B-b's execution path, not its design or rules.

## A3.4 Cost and order
One launch, STAGE=full: A3.1 (13,680 short fresh passes; B4's 5,760 took ≈ 5 min) + A3.2 (24 × 2 × 4 × 7 × 2
probes) ≈ 15–25 min ≈ $1–2 + boot. Built and FAKE-tested before launch (render check incl. the 3-role skeleton;
plants for slot, distance, wrapper); then B-b (≈ $10–11) under A3.3, fired separately.
