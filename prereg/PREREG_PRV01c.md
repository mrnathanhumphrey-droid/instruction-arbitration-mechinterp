# PREREG — PRV-01c: The Provenance Meter (supersedes PRV-01b)
**Program:** Prompt_Injection · corpus ``
**Status:** 🔒 **LOCKED 2026-09-14** on the lead researcher's explicit call, before any model load. sha256 in sidecar `PREREG_PRV01c.md.sha256`. Any edit supersedes (→ PRV-01d).
**Supersedes:** PRV-01b (`PREREG_PRV01b.md`, sha256 `a6930e6f8b846c2cf0d0dc9b2970313db26b169ff1b0b14eb4640a06f11d1766`, LOCKED 2026-09-13) → which superseded PRV-01 (`4ccf2a52…549b`). Both remain frozen as predecessors; this is the one that runs.
**Target:** arXiv 2606.27567 Theorem 3 + Assumption 3.
**Pool:** BIPIA (benign `context`, 3 scenarios). **Model:** **Llama-3.1-8B-Instruct**. **Cost class:** inference only, gate at $5.

---

## REV NOTES (PRV-01b → PRV-01c; delete before lock for a clean doc)
**Why this supersession exists — recorded as a correction, not a retreat:** §4 of PRV-01b specified the untrusted role as the **tool-output/`ipython` slot**, which is *inconsistent with §2/§8's own scoping of the bound to "the representations the paper itself uses (M2)"* — M2's untrusted corpus is **UltraChat user turns (user-origin)**, a slot the tool-output spec never touched. Llama-3.1-Instruct's `chat_template` applies `{{ content | tojson }}` to tool-slot content (quotes + `\n`-escapes it), which would make the untrusted span's tokens differ from the trusted span's — breaking the content-matched core (§4) — and the template collision is what *surfaced* the pre-existing inconsistency. Fix: **untrusted role = `user` slot** (M2-faithful, rendered raw by the template → byte-identical spans natively, no hand-rolling, no tojson).

Three independent reasons B is required, not merely cleaner:
1. **A adds a directional confound on the primary hypothesis.** Raw content in the tool slot is OOD → distinctively "weird" representations the probe can separate on *instead of* provenance, inflating apparent recovery (H1 is "provenance highly recoverable"). Perplexity would flag "odd" without revealing the direction.
2. **B is faithful to our own §2/§8 scoping;** the tool-slot was drift.
3. **A invalidates G0b.** G0b decomposes M2's separation into content-vs-role by holding content fixed *at the same role contrast as G0a*. G0a is system-vs-user by construction. Under A, G0b would be system-vs-tool → the role fraction is a ratio of two different contrasts → the decomposition is meaningless. B keeps both arms on the identical system-vs-user contrast.

Also folded:
- **§4 heading fixed:** the rule is **clip → IQR** (the binding sentence; the PRV-01b heading's "clip→balance→IQR" contradicted its own decisive clause — the reproduction correctly followed clip→IQR).
- **Tool-slot version named as a FOLLOW-UP probe** (§8), not an abandoned arm: indirect injection through tool output is a real, distinct threat model deserving its own prereg with the OOD rendering handled deliberately.
- Carried unchanged and already VALIDATED under PRV-01b (slot-independent): window **[114,222]**, **n=166** (reproduced exact, tokenizer pinned in `run/prv01b/ENV_LOCK.md`); **G3 interaction powered** (MDIE 3.76 pp @ σ=0.10, no PRV-01c-from-power); Step 2 **G0a ratio BINDING** (4 repos named, corpora acquired).

---

## 1. What this probe is for — and the two mismatches in the target

2606.27567's Theorem 3: Bayes-optimal provenance-recovery error `P_e = ½(1 − TV(P_{Z|trusted}, P_{Z|untrusted}))`;
main impossibility (Theorem 6) rests on **Assumption 3** — trusted/untrusted contextual representations at
control-relevant nodes are *not disjoint* (TV<1, P_e>0). Empirical support = M2: **MMD** between
instruction-origin and **user-origin** hidden states in **Llama-3.1-8B-Instruct (8-bit)**, mean-pooled,
layers {0,8,16,24,31}, RBF/median-bandwidth, N=300, B=1000 → L0≈0.61, peak **L8≈0.91**, decline to
**L31≈0.76**. Instruction corpus = 4 public system-prompt repos; user corpus = UltraChat-200K user turns
(verified, `lit/B3/inseparability/text.txt`).

**Mismatch 1 — wrong quantity.** MMD ≠ TV; a Bayes error can't be read off MMD; no public code computes the
theorem's quantity. PRV-01c measures achievable recovery, bounding TV from below.

**Mismatch 2 — wrong contrast (a result, not a repair).** M2's corpora differ in topic/register/length/style
/function **and** role, so its 0.91 is dominated by **content** separation (different text). Assumption 3 is
about the **computation**: same content, different **role**. And the threat model makes it binding — prompt
injection *is* untrusted content written to resemble trusted content, so **the adversarial condition is the
content-matched condition.** M2 measured the benign cross-content distribution; the theorem is about the
adversarial content-matched one. PRV-01c is content-matched by construction (§4); **G0b** quantifies how much
of M2's headline is content vs role, on the identical system-vs-user role contrast as G0a.

## 2. The logical asymmetry — state, do not blur

`a` ⟹ `TV ≥ 2a−1` ⟹ `P_e ≤ 1−a`. A failing probe is uninformative (partially bought back by G5). A
succeeding probe bounds P_e from above. This design can only show provenance is *more* recoverable than
assumed; it cannot confirm Assumption 3.

**Scope of the bound.** We probe **residual-stream hidden states** (the M2 object), NOT the theorem's abstract
control-relevant node; residual decodability can exceed recoverability at the node the control path consumes.
PRV-01c bounds recoverability from the M2 representations — upgrading M2 from MMD→Bayes-bound and from the
wrong contrast to the right one. The utilization inference (§3) holds only insofar as that residual is what the
control path reads.

## 3. Hypothesis and kill conditions

**Roles:** trusted = **system** slot; untrusted = **user** slot (both rendered raw by the Instruct
`chat_template`; = M2's instruction-origin / user-origin contrast).

**H1 (primary, directional).** At control-relevant layers {16,24,31}, provenance is highly recoverable from
**content-matched** representations: **P_e ≤ 0.10**, nonzero role main effect, all assertions/gates passing.

**Why it matters if H1 holds:** Theorem 3 true-but-non-binding and M2's support largely content, not role. If
recovery ~95%+ content-matched while defenses leak (ASIDE BIPIA-text 14.7%→4.9%, same-model caveat §8), the
failure mode is **utilization, not recoverability.**

**FALSIFIER.** `P_e > 0.25`, all gates passed → Assumption 3 binds in the adversarial (content-matched) regime;
H1 dead (verdict **POSITIVE**). No reinterpretation, no post-hoc layer selection.

**BOUNDARY.** 0.10 < P_e ≤ 0.25.

**Layers** {0,8,16,24,31}; **control-relevant** {16,24,31}; **layer 0** = calibration line, reported against,
never in H1. **Primary metric:** per-token role-probe accuracy over span content tokens (position-balanced),
`P_e = 1−a`, CIs **bootstrapped by resampling SPANS**; mean-pooled = secondary.

### Verdict vocabulary
| Outcome | Condition |
|---|---|
| **RECOVERED** | `P_e ≤ 0.10`, nonzero role main effect, all pass — provenance highly recoverable content-matched; Theorem 3 non-binding, M2 support largely content |
| **POSITIVE** | `P_e > 0.25`, all pass — Assumption 3 binds in the adversarial regime; H1 dead, a real result |
| **BOUNDARY** | `0.10 < P_e ≤ 0.25`, OR role main effect ≈ 0 (G2 ceiling) |
| **VOID** | any A-class assertion, or G1/G4, fails |
| **FINDING (separate)** | G0a shape non-reproduction |

REFUSE reserved for "could not be built"; falsifier firing = **POSITIVE**.

**Assertion/gate → consequence:** A1/A2 → VOID; G0a → FINDING(shape)/caveat(ratio); G0b → descriptive readout;
G1 → VOID; G2 → BOUNDARY ceiling; G3 → fix-before-run; G4 → VOID; G5 → interpretive floor.

## Model & precision (locked invariants)
- **Model = Llama-3.1-8B-Instruct.**
- **Probe precision = bf16, LOCKED. nf4 / any 4-bit forbidden for the primary measurement** (perturbs the probed
  residuals; confounds P_e and G0). Design invariant.
- **G0a primary = 8-bit** (matches M2 → ratio binding); **G0a-δ = bf16** (labeled precision arm).

## 4. Design — content-matched 2×2 factorial (role × position)

Per span `s`, four prompts, identical content, two factors: **role ∈ {trusted = system slot, untrusted = user
slot}** × **position ∈ {early, late}**. Same `s` in all four cells; both roles rendered **raw** by the Instruct
`chat_template` (no tojson, no hand-rolled headers) → span content tokens **byte-identical across cells** by
construction. Extract hidden states at the **content tokens of `s` only** (role/delimiter/template tokens
excluded). Token identity uninformative (asserted, G1) → any separation is contextual.

**Why factorial:** decompose into role main effect, position main effect, interaction. Role ME ≈ 0 with position
explaining the separation = the finding "provenance is merely positional." Off-distribution cells (system-late,
user-early) via multi-turn message lists passed through the template; on-distribution cells single-pass.

**Perplexity check = FLAG, never exclude** (dropping a cell kills the interaction term); all four cells in the
primary factorial; dropped-cell = robustness check; report ratios; flag threshold 2× on-distribution mean.

**Pool = BIPIA** benign `context` (passage attacks embed into, WITHOUT the injected instruction). 3 scenarios
ship benign context: Email, Table, Code (WebQA/NewsQA + Summarization/XSum license-gated, excluded).
Group-disjoint on span identity, stratified by scenario; no hash splits.

**Span length window — rule = clip → IQR** (deterministic given rule+pool+tokenizer build; tokenizer pinned,
`run/prv01b/ENV_LOCK.md`). Clip candidate spans to [16,256] content tokens; take the central-50% IQR of the
in-band subset → **realized window [114,222], n=166** (email 48 / table 86 / code 32; length ratio 1.95×),
reproduced exact under PRV-01b. The IQR is the *mechanism* for **length-matching**, which controls (i) the
mean-pooled secondary metric, (ii) positions a span occupies, (iii) the per-cell perplexity check; the tighter
1.95× in-band-subset spread beats balance-then-IQR's 2.45×, and the full [16,256] band (15×) is not
length-matched at all. **Report the realized window + per-cell n in the verdict.**

**Probe = logistic regression, LOCKED** — no MLP, no probe-class substitution. Report accuracy, span-resampled
bootstrap CI, `P_e`. **Per-token PRIMARY, mean-pooled SECONDARY; bootstrap resamples SPANS** (unit of
independence; token resampling narrows CIs by ~√(tokens/span) and makes G3 fiction).

## 5. Assertions and gates

### A-class build-verification (wiring only; failure = VOID)
- **A1 — Position-only orthogonality (balanced-factor).** A position-*factor* probe predicting role must sit at
  chance under the balanced factorial. Fails only on unequal cells / broken scaffold balance. (The raw span-start
  *index* partially tracks role within a position band — a model-phase check, not A1.)
- **A2 — Cell-count / scaffold integrity.** Equal usable cell counts; every span in all four cells.

### G-class gates
**G0 — MMD reproduction + content/role decomposition (three arms, identical system-vs-user contrast):**
- **G0a (cross-corpus, reproduces M2) — PRIMARY 8-bit.** MMD on system-prompt-repos vs UltraChat user turns,
  mean-pooled, RBF median-bandwidth, N≈300, B=1000, layers {0,8,16,24,31}, 8-bit. Pass = **shape** (peak L8,
  monotone decline) AND **L8/L31 = 1.20 ± 0.15**. Shape break → **FINDING**. All 4 repos named+acquired →
  **ratio BINDING** (Step 2, zero proxies).
- **G0a-δ (precision arm) — bf16, same data, LABELED.** Quantifies the bf16 probe choice's cost. Descriptive.
- **G0b (content-matched — the number nobody has).** Same pipeline, MMD on our BIPIA 2×2 **system-vs-user**
  content-matched spans (identical role contrast to G0a). **Pre-committed descriptive readout: role fraction =
  MMD_matched / MMD_cross per layer, NO threshold, NO verdict.** Decomposes M2's 0.91 into content vs role.

**G1 — Token-identity assertion (wiring).** Bag-of-tokens probe on span surface form must sit at chance; else
VOID. (Layer-0 full probe = calibration line.)

**G2 — Position gate (scientific = the factorial). → BOUNDARY ceiling.** Scientific content = position main
effect + interaction from the 2×2 (not the A1 probe). Requires nonzero role main effect; role ME ≈ 0 → BOUNDARY
+ positional-signal finding.

**G3 — Estimability, sized for the INTERACTION. → fix-before-run.** Interaction ≈4× a main effect's n. Via
span-resampled simulation: MDIE at 80% power, main effect resolves 0.90 vs 0.75. **Validated under PRV-01b on
the realized 166-span pool: MDIE 3.76 pp @ σ=0.10, main-effect resolvable = True, interaction powered = True.**

**G4 — Label shuffle (wiring). → VOID.** Shuffled role labels must give chance.

**G5 — Positive control (interpretive floor).** Recover span topic = BIPIA scenario (3-way Email/Table/Code) on
the **same stripped content-token representations**, **with the bag-of-tokens topic baseline reported alongside**.
topic-from-activations ≈ bag-of-tokens → lexical check, floor WEAK (say so); substantially exceeds → floor REAL.
Verdict states which. (Not language — English-dominant pool; not a planted token — trivially decodable.)

## 6. Null discipline
Any "provenance lives in subspace S" claim uses a **variance-matched top-r PCA subspace, NOT a
dimensionality-matched Haar subspace** (Haar overstates ~3×). Subspace-dimensionality out of scope for PRV-01c.

## 7. Artifacts
- `results/prv01c_g0.json` — G0a (8-bit) vs M2; G0a-δ (bf16); **G0b system-vs-user content-matched curve +
  per-layer role fraction**; ratio_binding=true.
- `results/prv01c_probe.json` — per-layer per-token + mean-pooled accuracy, span-resampled CI, P_e; factorial
  decomposition (role ME, position ME, interaction + MDIE); layer-0 calibration; per-cell perplexity ratios;
  realized window; dropped-cell robustness.
- `results/prv01c_gates.json` — A1–A2, G0a/G0a-δ/G0b, G1–G5 with numbers; G5 activation-vs-bag-of-tokens gap.
- `VERDICT_PRV01c_<date>.md` — {RECOVERED / POSITIVE / BOUNDARY / VOID} (+ escalation if G0a shape FINDING),
  stating H1 vs thresholds, role main effect, interaction (with MDIE), and the G0b role fraction.

## 8. Scope — what this does NOT claim
- Does not measure TV; bounds it from below on the residual/M2 object, not the theorem's control node.
- Does not refute Theorem 3 (correct statement about a bound); it re-scopes M2's *evidence* for Assumption 3 as
  the wrong contrast (§1).
- **"Provenance" here is constructed by us** (system-vs-user placement in our scaffold) — we measure
  positional-role-in-our-harness, not an intrinsic property of the text.
- **Both roles here (system, user) render raw**, so the template's `tojson` tool-content marker does not enter
  this experiment. (That marker — the template makes tool content machine-distinguishable from user content
  before layer 0, a weak textual "privilege bit" upstream of the model — is a **paper note**, and it is exactly
  what the tool-slot follow-up must handle deliberately.)
- **Follow-up probe (separate prereg):** indirect injection via the tool-output slot is a real, distinct threat
  model; it gets its own prereg with the OOD tool-rendering handled deliberately, not worked around.
- Does not establish the model *uses* recoverable provenance (next probe, gated on H1). The "recoverable ~95%
  yet leaks 14.7%→4.9% (ASIDE BIPIA-text)" line is a **same-model** target to reproduce, or not made.
- One model, one family. No cross-architecture claim (ARA's limitation, ours identically).

---

## User additions
*(reserved for the lead researcher — empty by default)*

---

## LOCK
🔒 **LOCKED 2026-09-14** on the lead researcher's explicit call ("cut PRV-01c, lock it, bring me the hash"), before any model
was loaded. sha256 of this file recorded in the sidecar `PREREG_PRV01c.md.sha256` (verify:
`sha256sum -c PREREG_PRV01c.md.sha256`); kept out of this file so it re-verifies without self-reference. The
design is frozen: any edit invalidates the hash, supersedes the lock (→ PRV-01d), and must point back here.
PRV-01b (`a6930e6f…1766`) and PRV-01 (`4ccf2a52…549b`) remain frozen predecessors. A model may now load —
after the lead researcher's explicit weights go.
