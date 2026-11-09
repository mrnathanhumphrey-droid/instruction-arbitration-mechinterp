# VERDICT — HUNT-DRIFT-01: does a system instruction keep its authority over a conversation?

Model: Llama-3.1-8B-Instruct @ `0e9e39f2`, bf16, SDPA, one H100 PCIe. Readout: `Y = lp(system target) − lp(competing
target)` at the first assistant position, on the DONE / READY battery (`data/stimuli_contested.jsonl`, 720 items, 30
templates). Every stage was sha256-locked before its run; the locked files and their hashes are in
`prereg/locked/drift01/` and `prereg/DRIFT01_LOCKED.sha256`. The locked plans for Amendments 9–11 are held privately;
their sha256 hashes, recorded at lock, are in `prereg/DRIFT01_LOCKED_HELD.sha256`, and the files can be checked against
them on request. Exploratory throughout: one model, one task family.

## The question
After a system instruction and a long, task-less conversation ("drift"), does the system instruction keep its authority
over a later user instruction that contradicts it — and is it distance or content that erodes it? A second question: can
an agent's own output gain instruction authority?

## Results by stage (pre-stated tests; verdicts by the locked rules)

| Stage | Pre-stated test | Result [CI] | Verdict |
|---|---|---|---|
| Full run (PLAN) | Q0 drift vs token-matched filler, per cell | 6 of 54 cells content-driven, none distance-driven | mostly indeterminate |
| Full run | Q1 the same planted line in the user vs the assistant turn (depth 0) | user − assistant −5.14 [−5.99, −4.29] | own turn weaker |
| B-a B1 | self-likely text pulls harder | 0 of 4 own-turn cells positive | mixed (no) |
| B-a B3 | the agent's own sampled choice "holds more" | +0.38 [+0.08, +0.64] | rule-passed; **design artifact** (see corrections) |
| Amendment 3 | own-turn quote discount − user-turn quote discount, layout and distance matched | +0.01 [−1.04, +1.10] | indeterminate (predicted −) |
| B-b (B5) | pooled drift − filler, fresh seeds, k 4–32 | −0.62 [−1.86, +0.72] | indeterminate |
| Amendment 4 | ρ(drift effect, the item's starting lean) | +0.13 [−0.11, +0.35] | not supported |
| Amendment 5 P1 | drift − filler, aligned part, k 1–4 (predicted −) | −1.32 [−1.79, −0.83] (97.5%) | **supported** |
| Amendment 5 P2 | prose − filler, aligned part, k 8–32 (predicted +) | +1.48 [+1.07, +1.95] (97.5%) | **supported** |
| Amendment 6 P1 | I = (defer − obey) − (agree − defy), one-word demonstrations (predicted +) | +10.41 [+9.36, +11.44] | **supported** |
| Amendment 7 P1 | the same I on 120 fresh items (predicted +) | +10.19 [+9.15, +11.14] (97.5%) | **supported** |
| Amendment 7 P2 | the same I when the user asks for the system word (predicted −) | −15.85 [−16.73, −14.99] (97.5%) | **supported** |
| Amendment 8 P1 | first-turn splice: compliant answer − clarification, user turn held fixed (predicted −) | −1.27 [−1.78, −0.78] | **supported** |
| Amendment 10 P1 | Amendment 7's I, native − renamed role headers (user / assistant → Sam / Alex), token-identical (predicted +) | +3.06 [+2.29, +3.82] (97.5%) | **supported** |
| Amendment 10 P2 | I when every demonstrated user asks for the other word (predicted −) | +4.12 [+2.97, +5.25] (97.5%) | **contradicted** |
| Amendment 11 P1 | drift − natural-text filler (8 books, one per turn), aligned part, k 1–4 (predicted −) | −1.21 [−1.80, −0.65] (97.5%) | **supported** |
| Amendment 11 P2 | word-pool filler − natural-text filler, aligned part, k 8–32 (predicted −) | −0.56 [−1.03, −0.08] (97.5%) | **supported** |

Amendment 9 (a read-only stance probe in the residual stream) was locked but not built; it will be re-locked before
any run.

Run folders: `results/drift01/<run>/REAL_*_ANALYSIS.md` (full run `full_20261025T121206Z`, B-a `phaseBa_…`, Amendment 3
`phaseBc_…`, B-b `phaseBb_…`, Amendment 4 `phaseBd_…`, Amendment 5 `phaseBe_…`, Amendment 6 `phaseBf_…`, Amendment 7
`phaseBg_…`, Amendment 8 `phaseBh_…`, Amendment 10 `phaseBi_…`, Amendment 11 `phaseBj_…`). Amendment 11's natural-text
filler is in `data/drift01/diverse/` (Project Gutenberg texts, editorial matter removed by `runners/drift01/diverse_build.py`).

## Amendment 10: re-rendering the demonstrations
Amendments 6–7's against-user replies are also "say the other word of DONE / READY", which gives their signs on its own.
Amendment 10 re-renders Amendment 7's 120 probes × 8 draws × 4 arms × n ∈ {1, 2, 4, 8} four ways (native, renamed headers,
a quoted log, a stated request for the other word), keeping the arms token-identical but for the DONE / READY swaps.
- Renaming the role headers cuts I by about 30% (P1 supported), so a role-dependent part remains.
- When every demonstrated user asks for the other word, I keeps its sign (P2 contradicted): most of the effect is a word
  rule learned in context, whoever asked. The stated request removes 60% of I and shrinks it further with more
  demonstrations (+1.74 [+0.20, +3.16] at n = 8) but never reverses it (secondary).
- Renaming does not kill every effect (user-word main effect +1.25 [+0.82, +1.66]), so the P1 drop is not unfamiliar
  formatting alone. Native rows matched Amendment 7's locked rows bit for bit (1,032 / 1,032).

## Amendment 11: is word-pool filler a valid baseline?
Amendment 5's results were measured against word-pool filler. Amendment 11 adds a natural-text arm on the same 96
transcripts × 120 items: each turn a token-matched passage from a different book of an 8-book pool across genres
(fiction, history, essays, travel, science, letters, drama, philosophy), no book twice in a row.
- P1 supported: drift's short-distance damage is not a property of the word-pool baseline.
- P2 supported: part of Amendment 5's "prose strengthens" is "word-pool filler weakens". P2 rests on k = 32 (−1.36
  [−1.90, −0.88]); at k = 8 and 16 the difference is not distinguishable from zero, and at k = 1 word-pool filler does
  less damage than natural text (+0.55 [+0.17, +0.90]) (secondary, not pre-stated).
- A prose effect remains: the single coherent book (Darwin) − natural text at k 8–32 is +0.91 [+0.60, +1.23]; split by the
  book nearest the probe, all 8 books give a positive difference (+0.65 to +1.17) (secondary).
- Amendment 5's rows were reproduced bit for bit (16,128 / 16,128) before the new arm ran.

## Reading (separate from the verdicts)
One candidate account joins the supported parts; the account as a whole is not itself tested.
- The agent's own **words** carry little authority: the same line pulls about 5 nats less from its own turn than from
  the user turn, and a quote is discounted in every slot once layout and distance are matched.
- What the agent has **done about the user's requests** carries a lot. Demonstrations in which the assistant went against
  the user strengthen the system target by ≈ 10 nats; when the user asks for the system word, the same demonstrations push
  the readout away from it (−15.85). The lesson is "go against the user", not "follow the system" — a follow-the-system
  lesson is orthogonal to I and would have read ≈ 0 (Amendment 7 erratum). Copying the demonstrated word is small (+0.5 to
  +0.7). Amendment 10 narrows this: most of it is a word rule learned in context ("say the other word"), whoever asked;
  about 30% depends on the turns being labelled user and assistant.
- Drift's short-distance damage runs through the **first reply**: a compliant answer weakens the system target more than
  a clarification request, most of all when it answers the request that asked for it (interaction −0.95 [−1.35, −0.59],
  secondary).
- So the model appears to read its history partly as evidence of what kind of assistant it is toward this user; after
  Amendment 10 the larger part is a word rule learned in context, and the role-dependent part is the smaller one.

Limits: one model; one task family (one-word DONE / READY rules); shifts in log-odds, not flipped answers (after one
defer demonstration on a no-conflict probe the model still mostly gives the system word: median p 0.30 vs 0.05); intervals
speak for the 12 conversation types and 30 templates sampled; no causal internals yet.

## Corrections on the record
- **B-a's own-turn exemption from the quote discount was layout.** The full-run comparison mixed slot with layout and
  plant-to-readout distance (14 vs 26 tokens); with both matched (Amendment 3) the own turn also discounts a quote
  (+1.12 [+0.53, +1.70]) and differs from the user turn by +0.01 [−1.04, +1.10].
- **B3's pre-registered yes is a design artifact.** Both arms share one context, so ON − OFF equals the context's lean
  toward the sampled word, which sampling selects for (chose DONE +1.70, chose READY −1.21).
- **The full run's attractor / loop flags are withdrawn.** Token-matched word-pool filler is flagged 144 of 144 by the same
  metric (mean-pooled residuals share a large common component). Its 144 MB residual file (`REAL_phase4.npz`) is not
  published.
- **Amendment 4's starting-lean hypothesis did not replicate** on fresh items (it came from an 8-item post-hoc fit).
- **Amendment 5's prose effect was partly the baseline.** Against natural text from mixed books, word-pool filler weakens
  the system target at k = 32 (Amendment 11), so part of "prose strengthens" was "filler weakens"; prose still beats
  natural text (+0.91).
- **Readout token.** One-word demonstration replies are the no-space tokens "DONE" / "READY"; the locked readout, shared by
  every stage, reads " DONE" / " READY". Amendments 6–8 store both: cell-level r +0.970 to +0.988; the no-space readout
  gives the same verdicts with larger effects.
- **Pre-fire errata** (before any data existed; tests unchanged): Amendment 7 — the lock's reading of a "contradicted" P2
  was wrong; Amendment 8 — the filler is keyed by the user turn's source transcript, not "by the cell".
- **bf16 prefill shape.** Readouts depend on how a prefix is chunked into the cache (single-pass vs fresh: median ≈ 0.1,
  max ≈ 0.5–0.7 nats); every later stage prefills each prefix in one pass, and the gap is reported per run.

