# PREREG — PRV-01e v2: re-run with substitution-B construction + multi-permutation G-SHUFFLE

**Locked before run. Chained to PRV-01e (VOID on an under-powered single-permutation G-SHUFFLE).** Same contrast, same
battery; two methodology amendments (the reviewer-ruled). Llama-3.1-8B-Instruct, NON-CAUSAL probe, FORWARD ONLY.

- chained_to_PRV01E_sha256: `efd4d2f600af1b00147c85ccb7a2f80d995316125239d3fffefb1e1fc469bbb0`
- runner: `run/prv01e/prv01e.py` sha256 `84970f987e46b6727a6b26591784a16dc948888f204765e2dd0ce8dc14caf88e`
- battery: `run/prv01e/stimuli_prv01e.jsonl` sha256 `d7d271051dfa4d4a6eef4837641561ec20fa411951b736cc4d7872dcd6ba4250` (unchanged)

## Why v2 (two amendments; everything else identical to PRV-01e)
PRV-01e's substantive result was clean and strong (G0 exactly at chance, G-POSITION pass, propagation curve → PROPAGATED,
acc 0.89 at d=64), but it VOIDed on G-SHUFFLE (0.20). That gate used a SINGLE permutation on a perfectly-separable probe — a
high-variance null, and 0.20 < 0.5 is the opposite of the CV-leak signature. Two fixes:

1. **B by STRING SUBSTITUTION (the reviewer build note).** Construct B by rendering A (tool role, tojson) then replacing the tool
   header substring `<|start_header_id|>ipython<|end_header_id|>` → `<|start_header_id|>user<|end_header_id|>` on the rendered
   string, NOT by re-rendering a user turn (the tojson vs user-turn paths differ in quoting/escaping/whitespace and would
   fail G-CONSTRUCT on a naive build). This makes post-header byte-identity GUARANTEED by construction (G-CONSTRUCT becomes a
   verification). B is thus a prompt that *claims* user-channel framing around a byte-identical tool payload; any
   template-legality objection is recorded, not fixed (fixing it reintroduces a surface difference). Verified 300/300
   tokenizer-only. (PRV-01e's re-render happened to match because json.dumps==tojson here; substitution removes that dependency.)
2. **G-SHUFFLE → MULTI-PERMUTATION null.** n_perm = 25 at (peak layer, d=1). Report null mean / std / p95. **Pass iff null
   mean ∈ [0.42, 0.58] (no CV leak — shuffled labels cannot classify) AND real-acc(d=1) > null p95 (signal exceeds the null).**
   Replaces the single-draw ±0.08 gate.

## §2–§8 unchanged from PRV-01e (`efd4d2f6`)
Arms A (tool `{"output":content}`) vs B (substitution → user header, byte-identical payload). G-CONSTRUCT hard (300/300 verified,
k=1). Read d ∈ {1,4,8,16,32,64} downstream of the content-block header; L0 at chance by construction. Probe SS+LR C=1.0,
5-fold grouped by item, fold-internal. Gates: G0 (L0≤0.55 all d) · G-POSITION (pad-swap counterbalance, maxdiff ≤0.05) ·
G-SHUFFLE (multi-perm, above) · G-VALIDITY (d1 acc ≥0.80). Outcome: PROPAGATED (acc>0.70 @ d≥32) / DECAYING (half-distance) /
LOCAL (≤0.60 @ d16). §8 scope binding (recoverable ≠ used; no causal verb). PRV-01d conditional on PROPAGATED/DECAYING,
patch site = the (layer,d) cell.

## Predictions (carried; PRV-01e already showed the shape)
- G-CONSTRUCT 300/300 (verified). G0 = 0.500 at all d. G-POSITION pass. G-VALIDITY d1 = 1.0.
- G-SHUFFLE: null mean ≈ 0.5, real-acc(1.0) > p95 → PASS (the single-perm 0.20 was noise).
- Outcome: **PROPAGATED** (PRV-01e curve: 1.0/1.0/1.0/0.995/0.908/0.893).

## Cost
Same shape as PRV-01e (~$0.49), + 25 CPU shuffle refits (negligible). a100/a10, watchdog, SMOKE→FULL, terminate in finally.

## User additions
(none)
