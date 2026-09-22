# PREREG — PRV-01: The Provenance Meter
**Program:** Prompt_Injection · corpus ``
**Status:** 🔒 **LOCKED 2026-09-13** on the lead researcher's explicit call, before any model load. sha256 in sidecar `PREREG_PRV01.md.sha256`. Any edit supersedes this lock and requires a new PRV-##.
**Target:** arXiv 2606.27567 Theorem 3 + Assumption 3.
**Pool:** BIPIA. **Model:** Llama-3.1-8B (matches the paper's M2). **Cost class:** inference only, gate at $5.

---

## REV NOTES (delete before lock if you want a clean doc)
**Fold 1 (post-review):** 2×2 factorial replacing counterbalancing; bound scoped to residual/M2 object; verdict vocabulary pre-committed; G0 shape+ratio; LR-only; positive control; per-token primary; constructed-provenance caveat; layer-0 calibration.
**Fold 2 (this rev):**
- **Length window data-determined** — IQR of BIPIA's native data-field token lengths, clipped [16,256]; realized window reported, not pre-stamped (§4).
- **G3 sizes for the INTERACTION, not the main effect** (~4× n); reports minimum detectable interaction effect (MDIE) so "no interaction" cannot be a cell that never fails (§5-G3).
- **Pool = BIPIA** (text-native spans sit in either role; cleaner G5 category; ASIDE BIPIA-text gives §8 a comparable-ground target) (§4, §8).
- **Perplexity → FLAG, never exclude** (dropping a cell kills the interaction term = the confound returns); all 4 cells in the primary factorial, dropped-cell is a robustness check only (§4).
- **Bootstrap resamples SPANS, not tokens** (unit of independence is the span; token resampling narrows CIs by ~√(tokens/span) and makes G3 fiction) (§4-+A, §5-G3).
- **Position-only probe → A-class build-verification assertion** (cannot fail on science under a balanced factorial; only catches wiring); G2's scientific content is now the position main effect + interaction (§5).

---

## 1. What this probe is for

2606.27567's Theorem 3 states the Bayes-optimal provenance-recovery error as

    P_e = ½ ( 1 − TV( P_{Z|trusted} , P_{Z|untrusted} ) )

and its main impossibility (Theorem 6) rests on **Assumption 3**: that trusted and
untrusted contextual representations at control-relevant nodes are *not disjoint*,
i.e. TV < 1, i.e. P_e > 0.

**The paper never measures TV.** Its empirical section (M2) reports **MMD** between
instruction-origin and user-origin hidden states in Llama-3.1-8B — peaking 0.908 at
layer 8, declining to 0.755 at layer 31. MMD is not TV. A Bayes error cannot be read
off an MMD. No public code computes the theorem's quantity (B3 verdict, Q3b: NOT PRESENT).

This probe measures **achievable provenance recovery** on real activations and asks
whether Assumption 3 is merely true or actually *binding*.

## 2. The logical asymmetry — state this in the writeup, do not blur it

A trained probe yields a **bound**, not the value:

- probe accuracy `a` ⟹ `TV ≥ 2a − 1` ⟹ `P_e ≤ 1 − a`
- A probe that FAILS is **uninformative** about TV — the failure may be the probe's (partially
  bought back by the positive control, §5-G5).
- A probe that SUCCEEDS bounds P_e from above and is informative.

So this design can only ever show provenance is *more* recoverable than assumed. It cannot
confirm Assumption 3 and must never be written as if it could.

**Scope of the bound (load-bearing).** We probe the **residual-stream hidden states** at the
paper's own layers — the *same object M2 measured by MMD*, the paper's operationalization of
`Z`. This is NOT the theorem's abstract "control-relevant node" (the attention value-
aggregation feeding the action decision, Theorem 4's `α_cj` over untrusted positions).
Residual-stream decodability can exceed recoverability at the node the control path consumes.
PRV-01 therefore bounds **recoverability from the representations the paper itself uses (M2)**
— it upgrades M2 from MMD to a Bayes-error bound — and the utilization inference (§3) holds
only insofar as that residual is what the control path reads. Do not write "we bounded
Theorem 3's P_e."

## 3. Pre-registered hypothesis and kill conditions

**H1 (primary, directional).** At control-relevant layers, provenance is highly recoverable
from contextual representations: **P_e ≤ 0.10** under the matched factorial, with a **nonzero
role main effect** (§4), all assertions and gates passing.

**Why it matters if H1 holds:** Theorem 3 is *true but non-binding*. If provenance is
recoverable at ~95%+ while defenses still leak (ASIDE's BIPIA-text 14.7%→4.9%, same-model
caveat §8), the failure mode is **not recoverability — it is utilization.** The model can
tell; it does not act on it. That relocates the problem and is the finding.

**FALSIFIER (pre-committed).** If **P_e > 0.25** at control-relevant layers with all gates
passed, Assumption 3 is binding, H1 is dead (verdict **POSITIVE**, §7). No reinterpretation,
no post-hoc layer selection.

**BOUNDARY.** 0.10 < P_e ≤ 0.25 → BOUNDARY, report the curve.

**Layer set** locked to the paper's own: **{0, 8, 16, 24, 31}**. **"Control-relevant"** for
the primary test locked to **{16, 24, 31}** (late-band). **Layer 0** is a **calibration line,
not a discard**: residual ≈ embedding, so it shows what "token identity fully available"
scores here; every late-layer P_e is reported against it.

**Primary metric:** **per-token** role-probe accuracy over the content tokens of `s`
(position-balanced), `P_e = 1 − a`, per control-relevant layer, **with CIs bootstrapped by
resampling spans** (§4-+A). Mean-pooled span representation is **secondary**.

### Verdict vocabulary (pre-committed)

| Outcome | Condition |
|---|---|
| **RECOVERED** | `P_e ≤ 0.10`, nonzero role main effect, all pass — provenance highly recoverable, Theorem 3 non-binding |
| **POSITIVE** | `P_e > 0.25`, all pass — Assumption 3 binds; H1 dead, a real result about the substrate |
| **BOUNDARY** | `0.10 < P_e ≤ 0.25`, OR role main effect ≈ 0 (G2 ceiling) |
| **VOID** | any A-class assertion, or G1/G4, fails — design/wiring broken; no verdict |
| **FINDING (separate)** | G0 non-reproduction — escalates out of PRV-01 |

REFUSE is deliberately **not** here: in this corpus REFUSE means the measurement could not be
constructed (DEC-01/DEC-02, gate-refused at $0). The falsifier firing is a positive claim
about the world → **POSITIVE**.

**Assertion/gate → consequence, explicit:** **A1/A2 → VOID (wiring); G0 → FINDING (escalate);
G1 → VOID; G2 → BOUNDARY ceiling; G3 → fix-before-lock; G4 → VOID; G5 → interpretive floor.**

## 4. Design — content-matched 2×2 factorial (role × position)

For each span `s`, build **four** prompts, identical in content, varying two factors:

- **role ∈ {trusted, untrusted}** — `s` in the system/instruction slot vs the tool-output/
  retrieved-data slot (semantically).
- **position ∈ {early, late}** — `s` near the start vs later in the sequence.

Cells: trusted-early, trusted-late, untrusted-early, untrusted-late. The same `s` populates
all four; extract hidden states at **the content tokens of `s` only** — strip every
role/delimiter/chat-template token. Token identity is uninformative by construction
(asserted, §5-G1), so any separation is contextual — the theorem's quantity.

**Why factorial, not counterbalanced.** Counterbalancing cancels position; a factor
*measures* it, same compute. Decompose role-probe performance into a **role main effect**, a
**position main effect**, and their **interaction**. If the role main effect is ~0 and
position explains the separation, that is a **finding** — "the provenance signal is positional
and nothing more, so any defense relying on role marking is relying on position" — not a
failed run. Counterbalancing would average that away.

**Off-distribution cells (trusted-late, untrusted-early): built from multi-turn scaffolds,**
not reordered single-turn prompts — in real multi-turn dialogue, instructions and tool
results interleave at varying positions, so both cells stay on-distribution. (AgentDojo's
native multi-turn structure is *not* a reason to prefer it — the scaffold is ours either way.)
**Distribution check (flag, do not exclude):** per-cell prompt perplexity under the model; if
any cell's mean perplexity > **2×** the on-distribution cells' mean, **flag** it in the
verdict and report the ratios — but **all four cells stay in the primary factorial.** Dropping
a cell kills the interaction term and collapses the design back to the confounded two-cell
case the factorial exists to prevent. A dropped-cell re-estimate is a **robustness check
only**, never the primary estimate. Report the actual perplexity ratios regardless so a reader
sees whether the threshold bound at all.

**Pool: BIPIA** (626,250 / 86,250 prompts). Chosen over AgentDojo because (i) BIPIA spans are
text-native and plausibly sit in *either* role, whereas AgentDojo tool outputs read strangely
in a system slot; (ii) BIPIA's native **5-scenario** category field is a cleaner G5 label than
task suites; (iii) AgentDojo's 97 tasks are thin for a group-disjoint 2×2; (iv) ASIDE reports
BIPIA-text (14.7%→4.9%), giving §8's same-model utilization remark a chance at comparable
ground later. Spans drawn from the data field, **length-matched**, held **group-disjoint** on
span identity across train/test — the same `s` never appears on both sides or in two cells of
one split. No hash splits (known program defect).

**Span length window (data-determined, not a magic number):** take BIPIA's native data-field
token-length distribution, use the **central 50% (IQR)**, clipped to **[16, 256]** content
tokens (floor: per-token probing needs material per span; ceiling: context budget across four
cells). **Report the realized window in the verdict.**

**Probe: logistic regression**, per layer. **Locked to LR** — no MLP, no probe-class
substitution after LR underperforms. Report accuracy, bootstrap CI (span-resampled), `P_e`.

**+A — per-token PRIMARY, mean-pooled SECONDARY; span-level bootstrap; length-matched.**
Theorem 3 is about representation instances `Z`, possibly per-token; pooling over
variable-length spans mixes a length signal in. Probe **per-token (primary)** and
**mean-pooled (secondary)**, length-match the pool. **The bootstrap resamples SPANS, not
tokens** — the unit of independence is the span; tokens within a span are correlated, and
resampling tokens narrows CIs by ~√(tokens/span), which would make G3's resolving check
fiction. (Same class as the pooled-population constraint already on the books.)

## 5. Assertions and gates

### Build-verification assertions (A-class) — cannot fail on science, only on wiring; failure = VOID
These verify the harness is built correctly. Under a balanced factorial they are true by
construction, so they carry **no scientific content** — they exist to catch silent build bugs.

- **A1 — Position-only orthogonality.** A position-index-only probe predicting *role* must sit
  at chance. With the factorial balanced, position ⊥ role by construction, so this is chance
  *regardless of the model* — it can only fail if cell counts are unequal or scaffold
  generation silently broke the balance. **Failure = VOID (wiring), not a finding.**
- **A2 — Cell-count / scaffold integrity.** Equal usable cell counts after extraction; every
  span present in all four cells; no cell dropped by silent generation failure. **Failure =
  VOID.**

*(G1 token-identity and G4 label-shuffle below are assertions of the same class, retained
under G-labels for the signed-off consequence map.)*

### Gates (G-class)

**G0 — MMD reproduction (cross-path check). → FINDING on failure.**
Compute MMD on the same activations and check **shape + ratio**, not absolute levels (paper
gives no kernel spec/code; an absolute band would manufacture failure):
- peak in the shallow band **{0, 8}**;
- monotone **non-increasing** from the peak through L31;
- **L8/L31 ratio = 1.20 ± 0.15** (their 0.908/0.755).
Shape holds + ratio lands → pass, pipeline tied to their object. Ratio off but **shape
intact** → bandwidth difference, reported as a caveat, not failure. **Shape breaks** (no
shallow peak, or MMD rises with depth) → escalate as a separate FINDING (contradicts M2,
outranks PRV-01). Record both curves.

**G1 — Token-identity assertion (wiring).** Bag-of-tokens probe on the span surface form must
sit at chance; if it beats chance the matching is broken → **VOID**. (Layer-0 full probe is
the calibration line, +C — expected near-trivial, never enters H1, and every late-layer
number is reported against it.)

**G2 — Position gate (scientific content = the factorial). → BOUNDARY ceiling.**
The scientific position content is the **position main effect and the role×position
interaction** estimated from the 2×2 — *not* the A1 probe. The primary claim requires a
**nonzero role main effect**: if the factorial shows role main effect ≈ 0 (role recovery not
above chance with position held fixed), provenance is not separable from position → verdict
**BOUNDARY at best**, with the positional-signal finding (§4) recorded.

**G3 — Estimability / resolving power, sized for the INTERACTION. → fix before lock.**
The factorial's value is the interaction, and an interaction needs ≈**4× the n** of a main
effect of the same magnitude. Size n on the **interaction**, not the main effect — sizing on
the main effect leaves the interaction underpowered and would report "no role×position
interaction" when we simply could not see one (the derived-scoreability failure: a cell that
can never fail). **Report the minimum detectable interaction effect (MDIE) alongside n**, and
also confirm the main effect resolves 0.90 (P_e 0.10) from 0.75 (P_e 0.25). Resolving-power
computed with the **span-resampled** bootstrap. If n cannot meet the interaction requirement,
**raise n or revise thresholds before the run, never after.**

**G4 — Label shuffle (wiring). → VOID.** Shuffled-role labels must give chance.

**G5 — Positive control (interpretive floor). → sets the floor for a null.**
Train the same pipeline to recover a **known-present attribute: span topic**, pre-committed to
**BIPIA's 5-scenario category field** — NOT language (English-dominant pool, would not vary),
NOT a planted token (trivially decodable, calibrates nothing). Topic probe succeeds but role
probe fails → "pipeline works, provenance not linearly present" (informative). Topic probe
*also* fails → pipeline underpowered, a role-probe null is uninformative. G5 does not pass or
void H1; it sets the interpretive floor.

## 6. Null discipline

Any "provenance lives in subspace S" claim uses a **variance-matched top-r PCA subspace, NOT a
dimensionality-matched Haar subspace** (Haar overstates ~3×; a property of the method, not the
model). Subspace-dimensionality questions are **out of scope for PRV-01** — on record only if
a follow-up reaches for it.

## 7. Artifacts

- `results/prv01_mmd_repro.json` — our MMD curve vs theirs, per layer; shape/ratio verdict
- `results/prv01_probe.json` — per-layer per-token AND mean-pooled accuracy, span-resampled CI,
  P_e bound; factorial decomposition (role ME, position ME, interaction + MDIE); layer-0
  calibration line; per-cell perplexity ratios; realized length window; dropped-cell robustness
  re-estimate
- `results/prv01_gates.json` — A1–A2, G0–G5 outcomes with numbers
- `VERDICT_PRV01_<date>.md` — verdict in **{RECOVERED / POSITIVE / BOUNDARY / VOID}** (plus a
  separate escalation note if G0 fires FINDING), stating H1 against the pre-committed
  thresholds, the role main effect, and the interaction (with MDIE) — and nothing beyond them.

## 8. Scope — what this does NOT claim

- Does not measure TV. Bounds it from below via achievable recovery, **on the residual/M2
  object, not the theorem's control node** (§2).
- Does not refute Theorem 3 (a correct statement about a bound).
- **"Provenance" here is constructed by us** — trusted/untrusted assigned by placement in our
  scaffold, so we measure *positional-role-in-our-harness*, not an intrinsic property of the
  text. The manipulation working as intended; stated so the writeup does not drift into
  claiming something about provenance in general.
- Does not establish the model *uses* recoverable provenance. That is the next probe, gated on
  H1 holding. The "recoverable ~95% yet leaks 14.7%→4.9% (ASIDE BIPIA-text)" juxtaposition is
  a **same-model** target to reproduce on Llama-3.1-8B, or it is not made — a bounded remark,
  not a claim.
- One model, one family. No cross-architecture claim — architecture is confounded with
  tokenizer, alignment, and pretraining data (ARA's stated limitation, applies to us
  identically).

---

## User additions
*(reserved for the lead researcher — empty by default)*

---

## LOCK
🔒 **LOCKED 2026-09-13** on the lead researcher's explicit call ("lock and rock"), before any model was loaded.
The sha256 of this file is recorded in the sidecar `PREREG_PRV01.md.sha256` (verify with
`sha256sum -c PREREG_PRV01.md.sha256`). The hash is deliberately kept OUT of this file so it
re-verifies without self-reference. The design is frozen: any edit invalidates the hash,
supersedes the lock, and must open a new PRV-## with a note pointing back here. A model may now
load.
