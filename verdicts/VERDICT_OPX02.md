# VERDICT — OPX-02: does the one-sided span asymmetry follow recency or role?

**Verdict (mechanical): ROLE — the OPX-01 asymmetry is role-bound, and recency and role dissociate at the span level.**
Under block-order reversal the role-labeled one-sided effects **keep their signs** (A_sys negative, A_usr positive in both
orders); recency-swap is decisively rejected. Yet the baseline B **flips sign** with order (recency-dominant). So the default
arbitration follows recency while the per-span causal asymmetry follows role — a dissociation nothing in the ledger predicted.

- prereg: `PREREG_OPX02.md` sha256 `bce394380057a6811512d84dbcdf5634c5e7590c816cfe303299df1b99db0d82` (chained OPX-01
  `bd3604ac…`); runner sha256 `78778a56e80a1c9535c9c912e8708ccffd7f61e2317065ff84eb3ac85288f1a3`
- run: a100_sxm4 @ us-east-1, FULL n=720, $0.28 (+$0.51 prior dead-boot, clean no-orphan; $0.79 total). B_normal −3.8792,
  B_flipped +1.6392. `run/opx02/results/opx02.json` + `opx02_arms.csv` + `opx02_peritem.npz`.

## Gates
- **ANCHOR (normal) ✓** reproduces OPX-01: M(A_sys) −0.930, M(A_usr) +1.899, M(EXCH) 0.462, M(CONSTR) 0.997.
- **CONSTRUCTION/COHERENCE ✓** M(CONSTR) = 0.997 (normal) / 1.000 (flipped) — the flipped-order patch faithfully reconstructs
  the twin, so it is coherent, not lobotomizing (the twin-VOID concern; uncontested VOID inherited from OPX-01).
- **B PER ORDER ✓ flips sign** as expected: −3.879 (normal, obeys last=user) → +1.639 (flipped, obeys last=system) —
  recency-dominant baseline. This is why raw ΔY, not M, is the discriminator.

## Raw ΔY per cell per order (primary)
| cell | dY normal | dY flipped |
|---|---|---|
| A_sys (system span, same-index flip) | **−7.22** | **−12.10** |
| A_usr (user span, same-index flip) | **+14.73** | **+9.36** |
| EXCH (cross two-sided) | +3.58 | −0.66 |
| CONSTR (become-the-twin) | +7.73 | −3.28 |

## Discriminator (raw ΔY)
- **signs_keep = True, signs_swap = False.** sign(dYf_sys) = − = sign(dYn_sys); sign(dYf_usr) = + = sign(dYn_usr).
- **swap_sys = dYf_sys − dYn_usr = −26.8 [−29.8, −23.6]** — under recency this would be ≈0; it is ~27 nats off. Recency-swap
  decisively rejected.
- keep_sys = dYf_sys − dYn_sys = −4.88 [−6.23, −3.54]; keep_usr = dYf_usr − dYn_usr = −5.37 [−6.88, −3.83]. Both exclude 0: a
  real **position component in the magnitudes** (each effect shifts ~−5 nats in flipped order), but it never flips the
  qualitative sign structure.

## Reading (the lead researcher's step; facts above)
- **The asymmetry is role-bound.** The **user span is always the dominant lever** (large |dY|), the **system span always the
  weak/counteracting one** (negative dY) — in both block orders. Mechanically (with `ysig`: +Y = obeys system): patching the
  user span to agree with the system boosts system-obedience strongly (+14.7); patching the system span to agree with the user
  only weakly moves, and backfires. The user role dominates the causal-flip response regardless of recency.
- **Recency and role come apart.** Baseline arbitration is recency-dominant (B flips toward the last block); the span-flip
  causal asymmetry is role-anchored (user-dominant) and does not follow the last block. These are two different things — the
  program had them fused ("recency-dominant" as a single story). OPX-01's competition/renormalization is now **role-anchored**,
  not position-anchored: the contest's *weighting* is by role (user > system), while the *baseline tilt* is by recency.
- Position still matters to **magnitude** (the ~−5 nat shift when order reverses), just not to the **structure**. A full
  mechanism would explain both the role-anchored signs and the recency-modulated magnitudes.

## Free consistency check — B reproduces ORD-01's 71/29 split (the reviewer)
B is not symmetric under reversal (−3.879 → +1.639). Model it as a flipping recency term plus a constant role term,
B = ∓R + ρ: **ρ = (Bn+Bf)/2 = −1.120, R = (Bf−Bn)/2 = 2.759** → **recency share R/(R+|ρ|) = 71.1%, role share = 28.9%.**
ORD-01 (entirely different arms) reported ~71% recency / 29% role. **Independent reproduction from two numbers already in this
run** — the two runs measure the same object, which makes the recency/role dissociation considerably harder to attack (the
same 71/29 recency/role split shows up in the baseline *and* the dissociation is between that baseline and the span-flip
weighting).

## Prediction outcome
- Anchors reproduce, CONSTR ≈ 1.0 both orders, B flips — **HIT.**
- **RECENCY (reversal swaps which span overshoots) — MISSED.** Mechanistic prediction, so the miss is the finding: the
  asymmetry is **role-bound**, and recency/role dissociate at the span level. (Recorded as a miss — second consecutive
  mechanistic OPX prediction to miss, both informative: OPX-01 "comparison" and OPX-02 "recency" were both wrong, and the
  truth — role-anchored competition on a recency-tilted baseline — is more specific than either.)

## Scope (binding)
Property of these spans/layers/model/battery under residual overwrite; single model. CONSTR ≈ 1.0 is a construction identity,
never evidence. The dissociation is between the *baseline* (recency) and the *span-flip causal asymmetry* (role); it does not
relocate arbitration, and "role-bound" here means the span-level flip response, not a claim about where arbitration is
computed.
