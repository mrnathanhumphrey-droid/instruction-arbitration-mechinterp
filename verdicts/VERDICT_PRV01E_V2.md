# VERDICT — PRV-01e v2: PROPAGATED (all gates pass). Role-header provenance is linearly recoverable ~89% at 64 tokens past a perfect payload forgery. The representational question is answered: the model ENCODES true-channel provenance and carries it downstream. Supersedes the PRV-01e VOID.

**Result: with the two amendments in place — B built by string substitution (guaranteed byte-identical payload) and a
multi-permutation G-SHUFFLE null — PRV-01e passes every gate and lands PROPAGATED. G-CONSTRUCT 300/300; G0 = 0.500 at every d
(embedding at chance by construction); G-POSITION 0.042 (not a position proxy); G-VALIDITY d1 = 1.000; G-SHUFFLE null mean
0.472 [std 0.232], real-acc(d1) 1.000 > p95 0.880 → PASS (the earlier single-draw 0.20 was ~1σ noise on a high-variance
null). The propagation curve at the peak layer (L1) is 1.000 / 1.000 / 1.000 / 0.995 / 0.908 / 0.893 at d = 1/4/8/16/32/64:
role-header provenance is ~89% linearly recoverable a full 64 tokens past a byte-identical (forged) payload — strongest at
layer 1 and carried forward, consistent with attention copying the header identity downstream within one layer.** Ran
2026-09-23, Lambda a100, FULL N=300, $0.50, terminated clean; re-verified from json. PREREG_PRV01E_V2.md sha256 `9350d4f2...`
(chained PRV-01e `efd4d2f6`).

## Gates (all pass)
| gate | value | pass |
|---|---|---|
| G-CONSTRUCT | 300/300 identical (substitution), k=1 | ✅ |
| G0 embedding-chance | L0 = 0.500 at all d | ✅ (by construction) |
| G-POSITION (pad-swap) | maxdiff 0.042 | ✅ (not a position proxy) |
| G-SHUFFLE (multi-perm, n=25) | null mean 0.472, real 1.000 > p95 0.880 | ✅ (no CV leak) |
| G-VALIDITY | d1 acc 1.000 | ✅ |

## Propagation curve (peak layer L1)
| d | 1 | 4 | 8 | 16 | 32 | 64 |
|---|---|---|---|---|---|---|
| acc | 1.000 | 1.000 | 1.000 | 0.995 | 0.908 | 0.893 |
→ **PROPAGATED** (acc > 0.70 at d ≥ 32).

## Full layer × d surface (from the persisted npz — the L1 slice UNDER-reports)
peakL=1 was an arbitrary tie-break (the earliest layer with a 1.0 cell). Read off the whole surface, propagation is much
stronger and does NOT decay with depth:
- **d=64 accuracy by layer:** 0.50 (L0) → 0.893 (L1) → 0.98 (L2) → ~0.99–1.00 across L7–L20 (max 1.000 at L13) → 0.997 (L32, top).
- **d=32:** 0.908 (L1) → 1.000 (L12–L20) → 0.990 (L32).
- **d≤16:** 1.000 at essentially every layer.
So provenance is present early and RETAINED/strengthened through the stack — not progressively discarded. PROPAGATED is robust
read off the surface (d=64 ≥ 0.98 across the whole mid-and-late stack), far above any shuffle null there; only the L1 point
was thin. **This also argues against pure L1 token-smear** (a static smear set at L1 would be flat or decay with depth; d=64
instead RISES L1→mid-stack) — partial, pending the cosine check (needs the L1 probe weight, which was NOT persisted; bundled
into the PRV-01f run).

## ⚠ RETRACTION — the dissociation is NOT established *from this run alone* (the reviewer, correct) — RESOLVED by PRV-01f
**[UPDATE 2026-09-23: PRV-01f (`0ba39250`) ran the missing cell — HEADER-INERT (ΔY=+0.13) BUT the dissociation is WITHDRAWN.
PRV-01f measured the header swap with tojson present in both arms (the +0.13 masked cell); in the RAW condition the same swap
moves Y +2.47 nats (TOOL-02 2×2), so the header is USED. The retraction below therefore STANDS as a retraction — the
replacement finding is REDUNDANCY (role and serialization each ≈ do the job alone; saturate together). The encoding half of
THIS run (encoded + propagates to d=64) is unaffected and stands on its own. See VERDICT_PRV01F.md.]**

My earlier headline ("the model represents where text came from and does not act on it") was a COMPOUND claim assembled from
two DIFFERENT objects, and only one half is measured on each:

| object | encoded? | behaviorally consequential? |
|---|---|---|
| payload markers (forged `[SYSTEM REMINDER]` in tool text) | unknown | **no** (SPOOF-01) |
| role header (`ipython` vs `user`) | **yes, propagates** (PRV-01e) | **UNTESTED** |

There is no cell where both halves are measured on the SAME object. "Encoded-but-unused" borrowed the encoding from the header
row and the inertness from the payload-marker row — different manipulations. **It is withdrawn until the missing cell is run.**
The header's behavioral consequence has never been measured, precisely because you can't forge a role header from inside a
user turn — which is what makes it the honest provenance signal. That missing cell = **PRV-01f** (behavioral arm of THIS
contrast: substitute the header on the injection battery, read Y), which goes BEFORE PRV-01d because it determines what
PRV-01d is testing.

## Reading (the lead researcher's step; facts above)
1. **The role header is encoded and propagates** (recoverable ≥0.98 at d=64 across mid/late stack). The information a forgery
   cannot copy is present in the residual stream and carried the length of the context. This half is solid.
2. **What that licenses, and only that:** "true-channel provenance is linearly recoverable and propagates." NOT "the model
   uses it," NOT "the model ignores it," NOT "encoded-but-unused." The behavioral half of THIS object is unmeasured.
3. **The PRV-01c-line instrument problem is resolved** (boundary confound / position proxy / saturation all cleared); what's
   measured is provenance, not wrapper/position/tokenization.

## Scope (binding, §8)
Recoverable ≠ used. No causal verb. The dissociation claim is retracted; the encoding claim stands. Single model
(Llama-3.1-8B), synthetic battery, one head-swap contrast.

## What this sets up
- **PRV-01f (behavioral arm of this contrast) is next** — the missing cell; measures whether the header is behaviorally
  consequential on the injection battery (same substitution, read Y). It determines PRV-01d's design (HEADER-USED → patch to
  test pathway; HEADER-INERT → amplify to test defense-construction).
- **PRV-01d stays unspecced until PRV-01f lands.** Phase 3b parked.
