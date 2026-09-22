# PREREG — RES-04: extent — is the missing half in the block? (RE-LOCKED, markers+span)

**Status: RE-LOCKED 2026-09-21.** SUPERSEDES the 2026-09-20 lock (sha `3cea2712be34cf988ae6b514a83066f3283d4857729d89861d1f9ec843235cc4`),
which specified a full-BLOCK (header+marker+content) cross-role swap. That is **infeasible**: the contested battery's blocks
are NOT content-matched — the imperative span matches cross-role (why RES-02's span swap worked) but the role FILLER is
role-specific ("You are assisting with routine office tasks." vs "Here is a note from my calendar…"), so full blocks differ
in content AND length. A forced full-block swap would import mismatched filler (a confound), not extent. SMOKE confirmed
0/720 usable. the lead researcher ruling 2026-09-21: re-lock to a **markers+span** design at three token-alignable extents. Chained to
PREREG_RES02.md sha256 `66ec4cee6f380fc9f33e308eb077fe73dbbc5eee94c163a21bc39a9809bb6cc5`. RES-02 harness, same
estimand/normalization → everything stays on the 0.46 scale.

## §1 Question
RES-02 swapped only the imperative SPAN and hit a ceiling of 0.462. The role MARKERS/headers (system header vs user header) are the one piece of role-bearing material every intervention so
far (RES-02 spans, PRV-04c attention, KDR-01 subspace) left untouched, and they are the ONE piece that IS token-alignable
cross-role (headers differ only in the role word, 1 token each → fixed-length marker region). Does adding the role markers to
the cross-role exchange move the ceiling above 0.46? And does the marker contribution combine additively with the span's, or
only when the span agrees with it?

## §2 Arms (full-residual replacement, all layers L8–31, as RES-02). Three EXTENTS, cross-role + a same-role floor at each.
Marker region K(role) = the header token span `<|start_header_id|> … <|end_header_id|>` for that role (bounded by SH=128006
and EOH=128007; role word = 1 token both roles → fixed length, cross-alignable). Span = RES-02 imperative span.
- **S — span-only cross-role** (RES-02 recap, WITHIN-RUN reference): item's imperative-span ← twin's opposite-slot span.
- **K — markers-only cross-role** (the new direct arm): item's system marker-region ← twin's user marker-region, and vice
  versa. Span left untouched.
- **M — markers+span cross-role** (the widest): item's {system marker + system span} ← twin's {user marker + user span},
  and vice versa. Both channels swapped together.
- **S2 / K2 / M2 — same-role disruption floor at each extent**: same-(template,position,counterbalance), different-filler
  source; item's regions ← source's SAME-role regions. K2 swaps identical marker tokens from a different context/position —
  NOT a no-op at the residual level (context + absolute position differ), so it is a real control and is reported.
- **VOID** — uncontested, same-content M-extent (marker+span) replacement, compliance ≥ 90% of unsteered. Group the source
  pool BEFORE subsampling (the RES-03 fix that worked).

All six treatment/floor arms run on ONE paired item set (twin + source present, span cross- and same-length matches, marker
cross-length match) so every contrast is within-run and paired by item — the increment is the quantity, and cross-run CIs
must not eat it.

## §2b Reported, not used to decompose
Per-arm mean absolute token-position shift (as RES-03), for S, K, M. The marker region sits at DIFFERENT absolute positions
across roles, so every cross-role arm here imports position exactly like RES-02 did — logged, NOT decomposed (RES-03b closed
that). This localizes; it does not split provenance from position.

## §3 Estimand
`M = −ΔY/(2B)`, ΔY signed by counterbalance, template-cluster PAIRED bootstrap, exactly as RES-02. Reporting order (the lead researcher):
1. **M_M − M_S with its paired CI FIRST** — the extent effect (markers+span over span-only 0.462).
2. **M_K** — the direct marker effect.
3. **Additivity:** M_M − (M_K + M_S), paired CI.
4. Per-arm floors reported: M_S−M_S2, M_K−M_K2, M_M−M_M2 (specificity, each net of same-role disruption).

## §4 Readings (pre-committed)
Extent (primary):
- **M_M − M_S > 0.10, paired CI > 0** → the missing half RIDES ON THE ROLE MARKERS; the block matters, specifically its
  markers; the 0.462≈0.471 (RES-02≈KDR) agreement was a shared-EXTENT artifact, not a lens fact.
- **|M_M − M_S| ≤ 0.08, paired CI incl 0** → markers add nothing beyond the span → the missing half is NOT in the block →
  remaining candidates = generation position and cross-position composition. Harder, more interesting.
- **M_M ≥ 0.85, CI-lo > 0.75** → markers+span account for ~the whole arbitration; everything after is decomposition, not
  location.

Additivity (mechanism — the most interesting thing this run can find):
- **M_K + M_S ≈ M_M** (additivity CI incl 0) → markers and span are INDEPENDENT CHANNELS; the marker contribution is M_K.
- **M_M ≫ M_K + M_S** (additivity CI > 0) → INTERACTION: the marker only does work when the span agrees with it. A real
  mechanism nothing in this arc predicted.
- **M_K ≈ 0 and M_M ≈ M_S** → markers carry nothing; the structural-anchor story (hovering since ATT-01) gets a clean
  NEGATIVE; the missing half is at the generation position or in composition.

Specificity / validity:
- **each arm ≫ its same-role floor** (M_x − M_x2 CI > 0) → the effect is provenance-specific, not generic patch disruption.
- **VOID** (arm floor < 0.90×unsteered) → patch lobotomizes; not a null.

## §5 Scope (stated up front)
Imports strictly more position than RES-02 (the marker region moves across roles). It CANNOT decompose provenance from
position and is not trying to (RES-03b ruling). It LOCALIZES: is the missing half on the role markers, or elsewhere
(generation position / composition)? The provenance/position split remains permanently undecomposed.

## §6 Artifacts
`res04_arms.csv`, `res04.json` (M_S, M_K, M_M, M_S2, M_K2, M_M2, M_M−M_S, M_M−(M_K+M_S), floors, shifts, VOID),
`res04_peritem.npz` (PERSIST per-item Y for every arm — the recurring discard bug), `VERDICT_RES04.md`, chained to RES-02.
Needs forwards. SMOKE-gated, watchdog armed (watchdog_always), auto-terminate, ledger, instance prompt-inj-res04.

---
## LOCK
**RE-LOCKED 2026-09-21.** Arms (§2: S, K, M + S2, K2, M2 floors + VOID), reported shift (§2b), reporting order (§3),
readings (§4) fixed. Executor specifics (marker region = SH..EOH inclusive, span = RES-02 imperative span, twin/source
pairing, length-match gating so all arms share one paired item set) in the runner. Supersedes the 2026-09-20 full-block lock
`3cea2712…`. Parent chain unchanged: RES-02 (value copied from `PREREG_RES02.md.sha256` into the runner header). sha256 in
sidecar `PREREG_RES04.md.sha256`. No edit after this line without a superseding ruling + re-lock.
