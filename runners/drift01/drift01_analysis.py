"""HUNT-DRIFT-01 analysis (EXPLORATORY; PLAN v0.3 + Amendments 1, 2 — §5–§8). Local, numpy only.
  python drift01_analysis.py <pulled run folder> [TAG]        (TAG default: REAL_; FAKE runs: FAKE_)
Writes <folder>/<TAG>ANALYSIS.md (tables) + <TAG>analysis.json. Every number is descriptive of this run; no claim beyond
the plan's pre-stated rules (bands, k_half, loop / attractor rules) is made here."""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D
F = Path(sys.argv[1]); TAG = sys.argv[2] if len(sys.argv) > 2 else "REAL_"
C = [json.loads(l) for l in open(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl", encoding="utf-8")]
man = json.loads((F / f"{TAG}transcripts_manifest.json").read_text(encoding="utf-8")); CELLS = [tuple(c) for c in man["cells"]]
TR = [json.loads(l) for l in open(F / f"{TAG}transcripts.jsonl", encoding="utf-8")]
MAIN = {t["tid"]: t for t in TR if "tid" in t}; WITH = [t for t in TR if "with_instruction" in t]
q0, q1, qf = (np.load(F / f"{TAG}{x}.npz")["rows"] for x in ("q0", "q1", "q1_full"))
GAP = json.loads((F / f"{TAG}gap_report.json").read_text(encoding="utf-8"))
tsys = lambda items: np.array([C[int(i)]["target_sys"] for i in items])
tmpl = lambda items: np.array([C[int(i)]["template_idx"] for i in items])
OUT, J = [], {}
def md(*a): OUT.append(" ".join(str(x) for x in a))
f2 = lambda x: "n/a" if x is None or not np.isfinite(x) else f"{x:+.2f}"
ci = lambda c: f"[{f2(c[0])}, {f2(c[1])}]"

# ------------------------------------------------------------------ tidy Q0: Y[(tid, item, cond, k)]
Y0r = D.y_signed(q0[:, 4], q0[:, 5], tsys(q0[:, 1]))
Y = {(int(r[0]), int(r[1]), int(r[2]), int(r[3])): y for r, y in zip(q0, Y0r)}
DIST = {(int(r[0]), int(r[1]), int(r[2]), int(r[3])): r[6] for r in q0}
KS = sorted({int(r[3]) for r in q0}); ITEMS = sorted({int(r[1]) for r in q0}); TIDS = sorted(MAIN)
cell = lambda t: CELLS[t]; seed_of = lambda t: CELLS[t][3]
MODES = sorted({c[0] for c in CELLS}); PERS = [p for p in D.PERSONAS if p in {c[1] for c in CELLS}]; TEMPS = sorted({c[2] for c in CELLS})
ci_ = D.Q0_CONDS.index

def units(sel, k, cond):
    """(num, den, item, seed) over the (t, i) of the selection that reach k: num = Y_cond(k) − Y_none(k), den = Y_drift(0) − Y_none(0)."""
    N, Dn, It, Sd = [], [], [], []
    for t in sel:
        for i in ITEMS:
            a, b, c0, d0 = (t, i, ci_(cond), k), (t, i, ci_("none"), k), (t, i, ci_("drift"), 0), (t, i, ci_("none"), 0)
            if a in Y and b in Y: N.append(Y[a] - Y[b]); Dn.append(Y[c0] - Y[d0]); It.append(i); Sd.append(seed_of(t))
    return np.array(N), np.array(Dn), np.array(It), np.array(Sd)
def A_of(sel, k, cond="drift"):
    N, Dn, It, Sd = units(sel, k, cond)
    if not len(N): return None, (None, None), 0
    return float(N.sum() / Dn.sum()) if Dn.sum() else float("nan"), D.boot2(N, Dn, It, Sd), len(N)

md(f"# HUNT-DRIFT-01 — analysis of `{F.name}` ({TAG.strip('_')}) — EXPLORATORY")
md(f"\nTranscripts {len(MAIN)} (+ {len(WITH)} with-instruction) · panel items {len(ITEMS)} · k ∈ {KS} · band δ = {D.BAND} Y_signed · "
   f"bootstrap {D.BOOT} two-way (items × seeds), seed {D.SEED_BOOT}.")
md(f"\nBranched-vs-fresh bf16 gap (A1.1, reported): max {GAP['max']:.3f}, median {GAP['median']:.3f} nats over {GAP['n']} picks "
   f"(pilot JITTER SD {GAP['jitter_sd_pilot']}). Drift and filler are token-matched → computed in identical shapes at each k.")

# ------------------------------------------------------------------ §5 A(k) per mode × persona × temperature
md("\n## A(k) — authority fraction, C-drift (ratio of means; 95% two-way CI)")
J["A"] = {}
for m in MODES:
    md(f"\n### {m}\n\n| persona | T | " + " | ".join(f"k={k}" for k in KS) + " | k_half |\n|" + "---|" * (len(KS) + 3))
    for p in PERS:
        for T in TEMPS:
            sel = [t for t in TIDS if cell(t)[:3] == (m, p, T)]; row, Ak = [], {}
            for k in KS:
                a, c, n = A_of(sel, k); Ak[k] = a if a is not None else np.nan
                row.append(f"{f2(a)} {ci(c)}" if a is not None else "—")
            kh = D.k_half(Ak); J["A"][f"{m}|{p}|{T}"] = {"A": Ak, "k_half": kh}
            md(f"| {p} | {T} | " + " | ".join(row) + f" | {kh if kh is not None else 'not reached'} |")

# ------------------------------------------------------------------ drift vs filler (the primary contrast)
md("\n## Drift vs filler at matched tokens — Δ = mean(Y_drift − Y_filler), verdict by the band rule")
J["drift_vs_filler"] = {}
md("\n| mode | persona | " + " | ".join(f"k={k}" for k in KS if k > 0) + " |\n|" + "---|" * (len([k for k in KS if k > 0]) + 2))
for m in MODES:
    for p in PERS:
        sel = [t for t in TIDS if cell(t)[:2] == (m, p)]; cells_ = []
        for k in [k for k in KS if k > 0]:
            d, It, Sd = [], [], []
            for t in sel:
                for i in ITEMS:
                    a, b = (t, i, ci_("drift"), k), (t, i, ci_("filler"), k)
                    if a in Y and b in Y: d.append(Y[a] - Y[b]); It.append(i); Sd.append(seed_of(t))
            if not d: cells_.append("—"); continue
            pt = float(np.mean(d)); c = D.boot2(np.array(d), None, np.array(It), np.array(Sd)); v = D.band_verdict(pt, c)
            J["drift_vs_filler"][f"{m}|{p}|{k}"] = {"delta": pt, "ci": c, "verdict": v}; cells_.append(f"{f2(pt)} {ci(c)} **{v}**")
        md(f"| {m} | {p} | " + " | ".join(cells_) + " |")

# ------------------------------------------------------------------ C-cross, C-refresh, persona / mode
md("\n## C-cross (A2.1: next-persona history under the own system message) — Δ = mean(Y_cross − Y_drift)")
md("\n| mode | persona ← history of | " + " | ".join(f"k={k}" for k in KS if k > 0) + " |\n|" + "---|" * (len([k for k in KS if k > 0]) + 2))
J["cross"] = {}
for m in MODES:
    for p in PERS:
        nxt = PERS[(PERS.index(p) + 1) % len(PERS)]; sel = [t for t in TIDS if cell(t)[:2] == (m, p)]; cells_ = []
        for k in [k for k in KS if k > 0]:
            d, It, Sd = [], [], []
            for t in sel:
                for i in ITEMS:
                    a, b = (t, i, ci_("cross"), k), (t, i, ci_("drift"), k)
                    if a in Y and b in Y: d.append(Y[a] - Y[b]); It.append(i); Sd.append(seed_of(t))
            if not d: cells_.append("—"); continue
            pt = float(np.mean(d)); c = D.boot2(np.array(d), None, np.array(It), np.array(Sd)); J["cross"][f"{m}|{p}|{k}"] = {"delta": pt, "ci": c}
            cells_.append(f"{f2(pt)} {ci(c)}")
        md(f"| {m} | {p} ← {nxt} | " + " | ".join(cells_) + " |")
md("\n## C-refresh — A_refresh(k) (restores if its CI − 1 lies inside ±δ in A units)")
md("\n| mode | " + " | ".join(f"k={k}" for k in KS) + " |\n|" + "---|" * (len(KS) + 1))
for m in MODES:
    sel = [t for t in TIDS if cell(t)[0] == m]; row = []
    for k in KS:
        a, c, n = A_of(sel, k, "refresh"); _, Dn, _, _ = units(sel, k, "refresh"); bandA = D.BAND / abs(Dn.mean()) if len(Dn) and Dn.mean() else np.nan
        ok = c[0] is not None and (c[0] - 1) > -bandA and (c[1] - 1) < bandA
        row.append(f"{f2(a)} {ci(c)}{' ✔' if ok else ''}")
    md(f"| {m} | " + " | ".join(row) + " |")
md("\n## Persona and mode (pooled over temperature): A(k), C-drift")
md("\n| group | " + " | ".join(f"k={k}" for k in KS) + " |\n|" + "---|" * (len(KS) + 1))
for lab, sel in [(f"mode {m}", [t for t in TIDS if cell(t)[0] == m]) for m in MODES] + [(f"persona {p}", [t for t in TIDS if cell(t)[1] == p]) for p in PERS]:
    md(f"| {lab} | " + " | ".join(f"{f2(A_of(sel, k)[0])} {ci(A_of(sel, k)[1])}" for k in KS) + " |")
md("\n**Pre-stated prediction (PLAN §5, from Li et al. 2024):** A_M1(k) ≥ A_M2(k) at matched tokens. " + " · ".join(
    f"k={k}: M1 {f2(A_of([t for t in TIDS if cell(t)[0] == 'M1'], k)[0])} vs M2 {f2(A_of([t for t in TIDS if cell(t)[0] == 'M2'], k)[0])}"
    for k in KS if k > 0 and "M1" in MODES and "M2" in MODES))

# ------------------------------------------------------------------ Q1 self-injection (panel by k; full battery depth 0)
def q1_tables(rows, has_k, title, clusters):
    Yq = D.y_signed(rows[:, -2], rows[:, -1], tsys(rows[:, 1 if has_k else 0]))
    key = (lambda r: (int(r[0]), int(r[1]), int(r[3]))) if has_k else (lambda r: (int(r[0]),))
    cond_col = 2 if has_k else 1; it_col = 1 if has_k else 0
    by = {}
    for r, y in zip(rows, Yq): by.setdefault(key(r), {})[D.Q1_CONDS[int(r[cond_col])]] = (y, int(r[it_col]), seed_of(int(r[0])) if has_k else 0)
    ks = sorted({int(r[3]) for r in rows}) if has_k else [0]
    md(f"\n## {title}\n\n| k | " + " | ".join(D.Q1_CONDS) + " |\n|" + "---|" * (len(D.Q1_CONDS) + 1))
    res = {}
    for k in ks:
        sub = {u: v for u, v in by.items() if not has_k or u[2] == k}
        md(f"| {k} | " + " | ".join(f"{np.mean([v[c][0] for v in sub.values()]):+.2f} ({np.mean([v[c][0] < 0 for v in sub.values()]):.0%})"
                                     for c in D.Q1_CONDS) + " |")
    md("\nmean Y_signed (share of units where the competing target wins, Y < 0). Contrasts (paired; 95% CI; + = the first moves the readout LESS toward the plant):")
    contr = [("plant authority, own imperative: inert − asst_imp", "inert", "asst_imp"), ("plant authority, own intention: inert − asst_int", "inert", "asst_int"),
             ("SLOT imperative: user_imp − asst_imp", "user_imp", "asst_imp"), ("SLOT intention: user_int − asst_int", "user_int", "asst_int"),
             ("FORM own turn: asst_int − asst_imp", "asst_int", "asst_imp"),
             ("**PROMISE vs MENTION: quot_int − asst_int**", "quot_int", "asst_int"), ("mention vs use, imperative: quot_imp − asst_imp", "quot_imp", "asst_imp")]
    for drop in (False, True):
        md(f"\n{'Sensitivity — non-minimal templates {5, 7, 16, 20} DROPPED' if drop else 'All templates'}:\n\n| contrast | " +
           " | ".join(f"k={k}" for k in ks) + " |\n|" + "---|" * (len(ks) + 1))
        for name, a, b in contr:
            cells_ = []
            for k in ks:
                sub = [v for u, v in by.items() if (not has_k or u[2] == k) and not (drop and C[v["inert"][1]]["template_idx"] in D.NON_MINIMAL)]
                d = np.array([v[a][0] - v[b][0] for v in sub]); it = np.array([v[a][1] for v in sub]); sd = np.array([v[a][2] for v in sub])
                if not len(d): cells_.append("—"); continue
                c = D.boot2(d, None, it, sd) if clusters == "two-way" else D.boot_template(d, tmpl(it))
                res[f"{name}|k{k}|{'drop' if drop else 'all'}"] = {"mean": float(d.mean()), "ci": c}; cells_.append(f"{d.mean():+.2f} {ci(c)}")
            md(f"| {name} | " + " | ".join(cells_) + " |")
    return res
J["q1_panel"] = q1_tables(q1, True, "Q1 self-injection — panel (transcript × item × k; drift prefix)", "two-way")
J["q1_full"] = q1_tables(qf, False, "Q1 self-injection — FULL BATTERY, depth 0, P-none (template-clustered CI)", "template")

# ------------------------------------------------------------------ Q2 self-directives (descriptive)
md("\n## Q2 — self-directive tags (descriptive; no causal claim)")
tags = {t: np.array([D.tag_count(x["assistant"]) for x in MAIN[t]["turns"]]) for t in TIDS}
md("\n| mode | persona | tags / turn | turns with ≥ 1 tag |\n|---|---|---|---|")
for m in MODES:
    for p in PERS:
        tt = [tags[t] for t in TIDS if cell(t)[:2] == (m, p)]; allt = np.concatenate(tt) if tt else np.zeros(0)
        md(f"| {m} | {p} | {allt.mean():.2f} | {(allt > 0).mean():.0%} |")
rank = lambda x: np.argsort(np.argsort(x)).astype(float)
xs, ys = [], []
for t in TIDS:
    for k in [k for k in KS if k > 0]:
        v = [(Y[(t, i, 0, k)] - Y[(t, i, 4, k)]) - (Y[(t, i, 0, 0)] - Y[(t, i, 4, 0)]) for i in ITEMS if (t, i, 0, k) in Y]
        if v: xs.append(tags[t][:k].sum()); ys.append(np.mean(v))
rho = float(np.corrcoef(rank(np.array(xs)), rank(np.array(ys)))[0, 1]) if len(xs) > 2 and np.std(xs) > 0 else float("nan")
J["q2_spearman"] = rho; md(f"\nSpearman(cumulative tags to k, change in Y_drift − Y_none since k = 0) over transcript × k: **{f2(rho)}** (n = {len(xs)}; descriptive).")

# ------------------------------------------------------------------ Q3 role trajectory + Phase 4 geometry
P4 = np.load(F / f"{TAG}phase4.npz")
md("\n## Q3 — role-axis trajectory of the agent's own turns (L8; relative to turn 1 and minus filler)")
try:
    pil = HERE.parents[1] / "pilot"; probe = D.fit_role_probe(np.load(pil / "out" / "pilot_acts_open.npz"), np.load(pil / "pilot_inputs.npz"))
    if probe["w"].shape[0] != P4[f"t{TIDS[0]}_drift_L8"].shape[1]: raise ValueError("probe / activation dimensions differ (FAKE run)")
    md("\n+ = toward the SYSTEM side. The probe never saw assistant tokens and partly reads position; later tokens would look MORE "
       "user-like from position alone, so a + slide runs against the confound.\n\n| mode | persona | turn 8 | turn 16 | turn 32 | minus filler @32 |\n|---|---|---|---|---|---|")
    J["q3"] = {}
    for m in MODES:
        for p in PERS:
            R = [D.role_trajectory(probe, P4[f"t{t}_drift_L8"].astype(np.float64), P4[f"t{t}_filler_L8"].astype(np.float64)) for t in TIDS if cell(t)[:2] == (m, p)]
            at = lambda key, j: np.mean([r[key][j - 1] for r in R if len(r[key]) >= j]) if any(len(r[key]) >= j for r in R) else np.nan
            J["q3"][f"{m}|{p}"] = {j: at("rel_turn1", j) for j in (8, 16, 32)}
            md(f"| {m} | {p} | {f2(at('rel_turn1', 8))} | {f2(at('rel_turn1', 16))} | {f2(at('rel_turn1', 32))} | {f2(at('rel_turn1_minus_filler', 32))} |")
except Exception as e:
    md(f"\nQ3 skipped: {e}")
md("\n## Phase 4 — drift geometry (L16; descriptive; loop + attractor rules as pre-stated)")
md("\n| mode | persona | T | conv. dist turn 1 → last | 4-gram repetition (mean) | short turns | looping seeds | attractor |\n|---|---|---|---|---|---|---|---|")
Zt = np.load(F / f"{TAG}transcripts.npz"); ids_of = {}
for q in range(len(Zt["tid"])):
    if Zt["role"][q] == 1: ids_of.setdefault(int(Zt["tid"][q]), []).append(Zt["ids"][Zt["off"][q]:Zt["off"][q + 1]].tolist())
J["phase4"] = {}
for m in MODES:
    for p in PERS:
        for T in TEMPS:
            sel = [t for t in TIDS if cell(t)[:3] == (m, p, T)]
            if not sel: continue
            V = [P4[f"t{t}_drift_L16"].astype(np.float64) for t in sel]; cv = D.convergence(V)
            rep = np.nanmean(np.concatenate([D.repetition(ids_of[t]) for t in sel]))
            sh = np.mean([D.short_turn(x["assistant"], i) for t in sel for x, i in zip(MAIN[t]["turns"], ids_of[t])])
            lp = [D.loops(D.selfsim(v)) for v in V]; at, why = D.attractor(lp, [v[-1] for v in V])
            J["phase4"][f"{m}|{p}|{T}"] = {"conv_first": float(cv[0]), "conv_last": float(cv[-1]), "rep": float(rep), "short": float(sh),
                                          "loops": sum(o for o, _ in lp), "attractor": [bool(at), why]}
            md(f"| {m} | {p} | {T} | {cv[0]:.3f} → {cv[-1]:.3f} | {rep:.2f} | {sh:.0%} | {sum(o for o, _ in lp)}/{len(sel)} | {why or 'no'} |")

# ------------------------------------------------------------------ with-instruction check (A1.4)
md("\n## With-instruction transcripts (generated WITH the item instruction; A1.4)")
md("\n| item | persona | seed | turns that are the bare target word |\n|---|---|---|---|")
for w in WITH:
    it = next(c for c in C if c["id"] == w["item"]); tgt = it["target_sys"]
    bare = np.mean([x["assistant"].strip().strip(".").upper() == tgt for x in w["turns"]]) if w["turns"] else np.nan
    md(f"| {w['item']} ({tgt}) | {w['cell'][1]} | {w['cell'][3]} | {bare:.0%} |")
(F / f"{TAG}ANALYSIS.md").write_text("\n".join(OUT) + "\n", encoding="utf-8")
(F / f"{TAG}analysis.json").write_text(json.dumps(J, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)), encoding="utf-8")
print(f"wrote {F / (TAG + 'ANALYSIS.md')} ({len(OUT)} lines)")
