# VERDICT — EXT-01: does the role marker carry the RES-02 "missing half"?

**Verdict (mechanical, pre-committed §3):** **INTERMEDIATE.** The role-word header token is a **real but minority** causal
carrier of provenance under cross-role exchange: marker gain M(ROLE) − M(CTRL) = **+0.070, CI [0.043, 0.096]** (excludes 0,
but below the 0.10 "carries a real chunk" bar and above the 0.05 inert bar). The bulk of the missing half is not in the role
marker.

- prereg: `PREREG_EXT01.md` sha256 `86b066c70025e518f16abf009e752235b42b96997df209b27376e0d38962b9fe` (chained TPL-01
  Phase23 `08d2f082…`)
- runner: `run/ext01/ext01_lambda.py` sha256 `838799ffe141636bb314d7afc16c998c23eff613f9d7ba4d08be551d10aff3b0`
- run: a10 @ us-east-1, FULL n=720 (0 skipped), $0.23, terminated clean, no orphan. `run/ext01/results/ext01.json` +
  `ext01_arms.csv` + `ext01_peritem.npz`. B = −3.9086.
- sharp 2-level form (graded sweep not well-posed on Llama — see prereg §0; only one cross-role-swappable
  role-distinguishing marker token exists, the role word).

## Gates
- **ANCHOR ✓ (near-exact).** M_L0 = **+0.460** [0.342, 0.559] vs RES-02 Arm1 +0.462; L0−DISR = **+0.420** [0.259, 0.552] vs
  RES-02 Arm1−Arm2 +0.422; dY_L0 = 3.596 vs RES-02 dY1 +3.58. The RES-02 exchange harness reproduced.
- **VOID false** (unsteered uncontested compliance 1.000). **Mass healthy** (B/L0/ROLE = 0.626/0.638/0.658; no forced slot
  needed). **G-SEGMENT** passed pre-lock (720/720, role ids {882, 9125}).

## Arms (M, template-cluster bootstrap CI)
| arm | M | CI95 | dY |
|---|---|---|---|
| L0 (imperative span) | +0.460 | [0.342, 0.559] | 3.596 |
| ROLE (imp + role-word token) | +0.528 | [0.402, 0.633] | 4.126 |
| CTRL (imp + `<|end_header_id|>`, shared header token) | +0.458 | [0.339, 0.557] | 3.581 |
| **marker gain = ROLE − CTRL** | **+0.070** | **[0.043, 0.096]** | — |
| DISR (same-role disruption floor) | +0.040 | — | — |

## Reading (the lead researcher's step; facts above)
- **CTRL ≈ L0** (+0.458 vs +0.460): swapping a shared, non-role-distinguishing header-position residual recovers nothing
  over the imperative alone. The neutral control behaved exactly as predicted → the marker gain is specific to the **role
  lexeme**, not to adding/swapping a header-position residual.
- **The role marker is a real but minority carrier.** +0.070 M is **~13% of the exchange's deficit** toward the twin-patch
  ceiling (0.997 − 0.460 = 0.537) and ~7% of the total arbitration. Real (CI excludes 0), specific (CTRL null), small.
- **~87% of the missing half is still not in the role marker** — it remains in the named-but-untested candidates:
  non-generation-position attention (esp. the instruction span — the live locus scoped from PRV-04c), cross-position
  composition, or non-linear residual.
- **Fits redundancy better than pure-correlate.** Unlike PRV-01d/g/h and TPL-01's sharp cells (~0 causal), the role marker
  here is a genuine small carrier. Consistent with the input-level **redundancy** finding: the imperative and the role marker
  each carry some provenance; the marker's slice is real but minor, and removing/adding it moves only a little because the
  imperative already carries most.

## Prediction outcome (pre-committed §6)
- ANCHOR reproduces — **HIT.**
- CTRL ≈ L0 — **HIT.**
- **MARKER-INERT — MISSED.** Predicted a clean 6th readable-feature null; got small-but-real (marker gain CI excludes 0).
  The "readable feature = ~0 causal" streak is **broken, mildly**: the role marker is a minor causal carrier, not inert.
  Honest correction to the going-in prior — the base rate is "small," not "zero," for input-level role markers under
  exchange. (Regime call, per standing rule; recorded as a miss.)

## Scope (binding)
Everything is a property of the **exchange** operation (RES-06 twin-patch reached ~0.997 where exchange got 0.462 at
identical positions). No number here is "the ceiling on role arbitration," only "under exchange." Single model; the role word
is the only cross-role-swappable role marker in Llama's template, so this is the sharp form of the extent question, not a
graded curve. INTERMEDIATE names the role-word token as a minor carrier component, not a mechanism.
