# VERDICT PRV-01c (2026-09-14)

## VERDICT: AGGREGATION-UNDEFINED
## + FINDING (separate): G0a shape non-reproduction

Mechanical, from locked thresholds only (prereg PREREG_PRV01c.md, sha256 3c88ba7d...2da5).

### P_e (per-token role probe, 1-accuracy) at control-relevant layers + L0
| layer | P_e | 95% CI | band |
|---|---|---|---|
| L0 (calibration) | 0.5000 | [0.5000,0.5000] | - |
| L16 | 0.0452 | [0.0314,0.0604] | LOW |
| L24 | 0.1044 | [0.0814,0.1258] | MID |
| L31 | 0.1047 | [0.0790,0.1292] | MID |

Thresholds: RECOVERED all<=0.10 ; POSITIVE all>0.25 ; BOUNDARY all 0.10-0.25 ; mixed=AGGREGATION-UNDEFINED.

### Factorial (control-relevant layers; outcome = fraction predicted trusted; contrasts = locked G3 basis)
| layer | role ME [CI] nonzero | position ME [CI] | interaction [CI] |
|---|---|---|---|
| L16 | 0.9136 [0.8834,0.9398] True | 0.0033 [-0.0103,0.0173] | -0.0649 [-0.0950,-0.0406] |
| L24 | 0.7985 [0.7562,0.8414] True | 0.0071 [-0.0074,0.0203] | -0.0784 [-0.1013,-0.0540] |
| L31 | 0.7999 [0.7519,0.8460] True | 0.0063 [-0.0011,0.0130] | -0.0512 [-0.0695,-0.0332] |

role main effect nonzero at all control-relevant layers: True
MDIE interaction (carried from G3, powered on 166-span pool): 0.0376 pp

### G0a (8-bit primary) MMD reproduction
- curve mmd2: L0=0.2252, L8=0.3225, L16=0.3370, L24=0.2456, L31=0.2532
- L8/L31 = 1.2738 (target 1.20+/-0.15; in-band=True)
- shape peak-L8 monotone-decline = False; PASS=False
- M2 reference: {'L0': 0.606, 'L8': 0.908, 'L16': 0.885, 'L24': 0.805, 'L31': 0.755, 'L8_over_L31': 1.203}

### G0b role fraction (MMD_G0b / MMD_G0a per layer; DESCRIPTIVE, no verdict)
- L0=-0.0157, L8=0.0706, L16=0.1082, L24=0.0826, L31=0.0428

### Gates
- A1 role-from-position acc = 0.5000 (pass=True)
- A2 cell integrity: equal cells + every span all four = True
- G1 bag-of-tokens->role acc = 0.5000 (pass=True)
- L0 role decoding (1-token-shift diagnostic) = 0.5000 (inert=True)
- G4 label-shuffle chance at all layers = True
- G5 topic floor: activation(best ctrl)=1.0000, bag-of-tokens=1.0000, gap=0.0000 -> WEAK
- per-cell perplexity 2x flags: {'trusted-early': False, 'untrusted-late': False, 'untrusted-early': False, 'trusted-late': False}

---

## HUMAN RULING & READING — the lead researcher, 2026-09-14 (post-mechanical; the mechanical verdict above stands as computed)

**Aggregation ruling → RECOVERED.** Rule: **minimum P_e over control-relevant layers** (the tightest available bound is operative). Derived from locked §2's asymmetry — a succeeding probe is informative and bounds P_e from above; a failing one is uninformative — which applies across layers as across probe classes. To show the theorem's bound is loose you need ONE readout where it is nearly recovered (constructive existence proof); demanding all three answers a question nobody asked. min P_e = **0.0452 @ L16 → RECOVERED**.
⚠ **Degree of freedom logged: aggregation ruled POST-HOC, after seeing data, derived from locked §2, PERMISSIVE direction.** Robustness: the **FALSIFIER did not fire under ANY aggregation rule** — nothing is within 0.15 of the 0.25 line; only the RECOVERED/BOUNDARY boundary depends on the choice.

**Reading (headline, scoped):** at L16 a linear probe recovers provenance at **95.5%** on a content-matched design where token identity = 0.500, position-only = 0.500, and the L0 embedding = 0.500 → a measured floor **TV ≥ 0.91** on the quantity Assumption 3 only ever assumed was < 1. The theorem survives in the sliver **0.91–1.0**: true, and at this readout operationally near-empty.

**Gate quality:** L0 = 0.5000 with zero-width CI = match **degenerate-BY-CONSTRUCTION** (byte-identical content ⇒ identical embedding points; the probe has nothing), not merely "at chance" — and the 1-token shift is retired with a number. Position ME CIs include 0 at all three layers → the position confound (which killed the original tool-slot design) is **measured and absent**. Small negative interaction (CIs exclude 0) → role decodability depends slightly on position — one writeup sentence, no more. G5 WEAK floor is moot (its job was to rescue a null; none occurred).

**Scope corrections (forced by the G0a FINDING):**
1. **DROP the M2 tie.** G0a was the evidence for §2's scoping to "the representations the paper uses (M2)," and it failed shape reproduction. Honest scope = *provenance recoverability from Llama-3.1-8B-Instruct residual states at layers {16,24,31}.* Do NOT write "we upgraded M2."
2. **Role fraction is uninterpretable as a fraction** (denominator didn't reproduce). Report the G0b content-matched MMD curve RAW, not as a fraction of anything.

**Spine status:** Leg 1 (wrong quantity — TV stated, MMD measured): **stands**, now with our number opposite it. Leg 2 (wrong contrast — cross-corpus vs content-matched): **stands structurally**; quantification needs a working denominator. Leg 3 (non-reproduction): **CANDIDATE, unestablished, ESCALATED**.

**G0a non-reproduction — escalated, not concluded.** Magnitude 2–3× low could be estimator/bandwidth/MMD-vs-MMD²/quantization; but **a monotone transform cannot move a peak** — our L16 peak vs M2's L8 is structural, not scaling. Corpus identity is off the table (4 named repos used); sampling/preprocessing within them are not. Highest-value open question in the program now: **is M2's shape reproducible at all under its stated method, or is it sample-specific?** One attempt with unknown sampling details ≠ a non-reproduction result. **NEXT PROBE = G0a reproduction (not PRV-02); utilization stays gated behind it.**