"""HUNT-DRIFT-01 B6 analysis (EXPLORATORY; Amendment 4 569919b6…, locked). Local, numpy only.
  python b6_analysis.py --selftest
  python b6_analysis.py <pulled B6 folder> <pulled B-b folder> [TAG]       (TAG default REAL_; DRY: FAKE_)
Writes <B6 folder>/<TAG>B6_ANALYSIS.md + <TAG>B6_analysis.json.
Per fresh item i (main transcripts, k ∈ K = {4, 8, 16, 32}):
  Δ_i  = mean over transcripts × K of (Y_drift − Y_filler)       Y0_i = mean over transcripts of Y_drift(0)
  h_i  = mean over transcripts of (Y_drift(0) − Y_none(0))
  m_X,i = sign(Y0_i) · mean over transcripts × K of (Y_X(k) − Y_X(0)),  X ∈ drift / filler / prose / none
PRIMARY H1: Spearman ρ(Δ_i, Y0_i), predicted +; two-way cluster bootstrap over TEMPLATES × generation SEEDS (2,000,
SEED_BOOT 7101001): every per-item quantity is recomputed inside each resample (seed weights), items enter with their
template's weight. supported = CI lower > 0 · contradicted = CI upper < 0 · otherwise not supported.
Secondary: S1 mean Δ + band verdict (template × seed; items × seed beside it) · S2 sign rule vs a permutation null
(2,000, seed 7101303; |Δ_i| < δ = tie) · S3 ρ(Δ, h) predicted −, + partial ρ given Y0 (correlated with H1) · S4
amplification vs compression (A4.3 rule; "both" = drift's amplification condition AND filler's compression condition)
· S5 prose contrasts · S6 by mode / k / counterbalance · S7 the B-b 8 items (repro check + their Δ_i, apart)."""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D
import phaseb_core as B
sys.stdout.reconfigure(encoding="utf-8")
C = [json.loads(l) for l in open(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl", encoding="utf-8")]
KP = (4, 8, 16, 32)
DR, FI, NO, PR = (B.B6_CONDS.index(x) for x in ("drift", "filler", "none", "prose"))
SEED_PERM = D.check_seed(7101303)
f2 = lambda x: "n/a" if x is None or not np.isfinite(x) else f"{x:+.2f}"
ci = lambda c: f"[{f2(c[0])}, {f2(c[1])}]"

def ranks(x):
    """Average ranks (ties share their mean rank)."""
    x = np.asarray(x, float); o = np.argsort(x, kind="mergesort"); r = np.empty(len(x)); xs = x[o]; i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]: j += 1
        r[o[i:j + 1]] = (i + j) / 2; i = j + 1
    return r

def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0: return float("nan")
    return float(np.corrcoef(ranks(a), ranks(b))[0, 1])

def partial_spearman(a, b, z):
    r = lambda x, y: spearman(x, y)
    ab, az, bz = r(a, b), r(a, z), r(b, z)
    den = np.sqrt((1 - az ** 2) * (1 - bz ** 2))
    return float((ab - az * bz) / den) if den > 0 else float("nan")

class Grid:
    """Sums + counts per (item, seed) cell for every per-item quantity, so a template × seed resample recomputes each
    item's value from the seeds it drew (balanced or not)."""
    def __init__(self, Y, items, seeds, seed_of, tids):
        self.items, self.seeds = list(items), list(seeds); I, S = len(items), len(seeds)
        ii = {x: n for n, x in enumerate(items)}; si = {x: n for n, x in enumerate(seeds)}
        Z = lambda: (np.zeros((I, S)), np.zeros((I, S)))
        self.d, self.y0, self.h = Z(), Z(), Z(); self.mv = {X: Z() for X in (DR, FI, PR, NO)}
        self.dp, self.dc = Z(), Z()                              # drift − prose, prose − filler
        def add(acc, i, s, v): acc[0][i, s] += v; acc[1][i, s] += 1
        for t in tids:
            s = si[seed_of(t)]
            for it in items:
                i = ii[it]
                if (t, it, DR, 0) not in Y: continue
                add(self.y0, i, s, Y[(t, it, DR, 0)]); add(self.h, i, s, Y[(t, it, DR, 0)] - Y[(t, it, NO, 0)])
                for k in KP:
                    if (t, it, DR, k) not in Y: continue
                    add(self.d, i, s, Y[(t, it, DR, k)] - Y[(t, it, FI, k)])
                    add(self.dp, i, s, Y[(t, it, DR, k)] - Y[(t, it, PR, k)]); add(self.dc, i, s, Y[(t, it, PR, k)] - Y[(t, it, FI, k)])
                    for X in self.mv: add(self.mv[X], i, s, Y[(t, it, X, k)] - Y[(t, it, X, 0)])
    @staticmethod
    def per_item(acc, ws):
        n = acc[1] @ ws; return np.where(n > 0, (acc[0] @ ws) / np.where(n > 0, n, 1), np.nan)
    def stats(self, ws, wi):
        """Every quantity at seed weights ws (len S) and item weights wi (len I; 0 = not drawn)."""
        d, y0, h = (self.per_item(a, ws) for a in (self.d, self.y0, self.h))
        keep = (wi > 0) & np.isfinite(d) & np.isfinite(y0); rep = lambda v: np.repeat(v[keep], wi[keep].astype(int))
        sg = np.sign(y0); out = {"rho_h1": spearman(rep(d), rep(y0)), "rho_h2": spearman(rep(d), rep(h)),
                                 "prho_h2": partial_spearman(rep(d), rep(h), rep(y0))}
        W = lambda v: float(np.sum((v * wi)[keep]) / np.sum(wi[keep])) if np.sum(wi[keep]) else float("nan")
        for X, nm in ((DR, "drift"), (FI, "filler"), (PR, "prose"), (NO, "none")): out[f"m_{nm}"] = W(sg * self.per_item(self.mv[X], ws))
        dp, dc = self.per_item(self.dp, ws), self.per_item(self.dc, ws)
        out.update(d_prose=W(dp), d_coh=W(dc), rho_dprose=spearman(rep(dp), rep(y0)), rho_dcoh=spearman(rep(dc), rep(y0)))
        return out

def boot_stats(G, tmpl_of, boot=D.BOOT, rs=D.SEED_BOOT):
    """Point stats + percentile 95% CIs; templates × seeds resampled independently."""
    D.check_seed(rs); I, S = len(G.items), len(G.seeds)
    tu = sorted({tmpl_of[i] for i in G.items}); ti = np.array([tu.index(tmpl_of[i]) for i in G.items])
    pt = G.stats(np.ones(S), np.ones(I)); rng = np.random.default_rng(rs); est = {k: np.empty(boot) for k in pt}
    for b in range(boot):
        wt = np.bincount(rng.integers(0, len(tu), len(tu)), minlength=len(tu)); ws = np.bincount(rng.integers(0, S, S), minlength=S).astype(float)
        st = G.stats(ws, wt[ti].astype(float))
        for k in pt: est[k][b] = st[k]
    return pt, {k: tuple(float(x) for x in np.nanpercentile(est[k], [2.5, 97.5])) for k in pt}

def h1_verdict(c):
    lo, hi = c
    return "supported" if lo > 0 else "contradicted" if hi < 0 else "not supported"

def s4_reading(pt, c, band=D.BAND):
    amp_d = c["m_drift"][0] > 0 and pt["m_drift"] > band
    cmp_f = c["m_filler"][1] < 0 and pt["m_filler"] < -band
    if amp_d and cmp_f: return "both"
    if amp_d and not c["m_filler"][1] < 0: return "amplification"
    if cmp_f and c["m_drift"][0] <= 0 <= c["m_drift"][1]: return "compression"
    return "neither"

def analyze(q6, cells, repro=None, prose=None, gap=None, bb_q0=None):
    """q6 = b6_q0 rows (tid, item, cond, k, lpD, lpR, dist); cells = B-b main (mode, persona, T, seed) by tid."""
    Yr = D.y_signed(q6[:, 4], q6[:, 5], [C[int(i)]["target_sys"] for i in q6[:, 1]])
    Y = {(int(r[0]), int(r[1]), int(r[2]), int(r[3])): y for r, y in zip(q6, Yr)}
    DIST = {(int(r[0]), int(r[1]), int(r[2]), int(r[3])): r[6] for r in q6}
    tids = sorted({int(r[0]) for r in q6}); items = sorted({int(r[1]) for r in q6}); KS = sorted({int(r[3]) for r in q6})
    seed_of = lambda t: cells[t][3]; seeds = sorted({seed_of(t) for t in tids}); tmpl_of = {i: C[i]["template_idx"] for i in items}
    OUT, J = [], {}
    md = lambda *a: OUT.append(" ".join(str(x) for x in a))
    mism = sum(1 for (t, i, c, k), v in DIST.items() if c in (FI, PR) and DIST.get((t, i, DR, k)) != v)
    J["distance_mismatch"] = mism
    G = Grid(Y, items, seeds, seed_of, tids); pt, CI = boot_stats(G, tmpl_of)
    S, I = len(seeds), len(items); one_s, one_i = np.ones(S), np.ones(I)
    d_i, y0_i, h_i = (G.per_item(a, one_s) for a in (G.d, G.y0, G.h))
    md(f"# HUNT-DRIFT-01 B6 — Amendment 4 (569919b6…) — fresh items × drift / filler / none / prose — EXPLORATORY")
    md(f"\nTranscripts {len(tids)} · fresh items {I} from {len(set(tmpl_of.values()))} templates · k ∈ {KS} · δ = {D.BAND} · "
       f"bootstrap {D.BOOT} over templates × seeds, seed {D.SEED_BOOT}. Filler / prose distance mismatches vs drift: {mism} (must be 0).")
    # Y0 spread (A4.1)
    q = np.percentile(y0_i, [0, 25, 50, 75, 100])
    J["y0_spread"] = {"pos": int((y0_i > 0).sum()), "neg": int((y0_i < 0).sum()), "zero": int((y0_i == 0).sum()), "quartiles": q.tolist()}
    md(f"\nY_drift(0) spread over the {I} drawn items: {J['y0_spread']['pos']} > 0 · {J['y0_spread']['neg']} < 0 · "
       f"min / Q1 / median / Q3 / max = {' / '.join(f2(x) for x in q)}.")
    # PRIMARY
    v = h1_verdict(CI["rho_h1"]); J["primary"] = {"rho": pt["rho_h1"], "ci": CI["rho_h1"], "verdict": v, "n_items": I}
    md(f"\n## PRIMARY — H1: Spearman ρ(Δ_i, Y_drift(0)_i), predicted +\n\n**ρ = {f2(pt['rho_h1'])} {ci(CI['rho_h1'])} (n = {I} items) → {v}**")
    # S1 mean Δ
    dd, it_, sd_ = [], [], []
    for (t, i, c, k), y in Y.items():
        if c == DR and k in KP: dd.append(y - Y[(t, i, FI, k)]); it_.append(i); sd_.append(seed_of(t))
    dd = np.array(dd); p1 = float(dd.mean())
    c_t = D.boot2(dd, None, np.array([tmpl_of[i] for i in it_]), np.array(sd_)); c_i = D.boot2(dd, None, np.array(it_), np.array(sd_))
    J["s1"] = {"delta": p1, "ci_template_seed": c_t, "verdict": D.band_verdict(p1, c_t), "ci_item_seed": c_i, "verdict_item_seed": D.band_verdict(p1, c_i), "n": len(dd)}
    md(f"\n## S1 — mean Δ = mean(Y_drift − Y_filler), k ∈ {{4..32}}\n\nΔ = {f2(p1)} {ci(c_t)} templates × seeds → **{J['s1']['verdict']}** · "
       f"items × seeds {ci(c_i)} → {J['s1']['verdict_item_seed']} (n = {len(dd)})")
    # S2 sign rule
    def share(d, y):
        m = np.abs(d) >= D.BAND; return (float(np.mean(np.sign(d[m]) == np.sign(y[m]))) if m.any() else float("nan")), int((~m).sum())
    sh, ties = share(d_i, y0_i); rng = np.random.default_rng(SEED_PERM)
    null = np.array([share(d_i, rng.permutation(y0_i))[0] for _ in range(D.BOOT)])
    pv = float(np.mean(null >= sh)); J["s2"] = {"share": sh, "ties": ties, "null_mean": float(np.nanmean(null)), "p_perm": pv}
    md(f"\n## S2 — sign rule: sign(Δ_i) = sign(Y0_i) on {sh:.0%} of {I - ties} items (ties |Δ_i| < δ: {ties}); "
       f"permutation null mean {np.nanmean(null):.0%}, p = {pv:.3f}")
    # S3
    J["s3"] = {"rho": pt["rho_h2"], "ci": CI["rho_h2"], "partial_given_y0": pt["prho_h2"], "partial_ci": CI["prho_h2"]}
    md(f"\n## S3 — H2 (CORRELATED WITH H1): ρ(Δ_i, headroom_i), predicted −\n\nρ = {f2(pt['rho_h2'])} {ci(CI['rho_h2'])} · "
       f"partial ρ given Y0 = {f2(pt['prho_h2'])} {ci(CI['prho_h2'])} · ρ(headroom, Y0) = {f2(spearman(h_i, y0_i))}")
    # S4
    rd = s4_reading(pt, CI); J["s4"] = {nm: {"m": pt[f"m_{nm}"], "ci": CI[f"m_{nm}"]} for nm in ("drift", "filler", "prose", "none")}; J["s4"]["reading"] = rd
    md("\n## S4 — amplification vs compression: signed move m_X = sign(Y0) · (Y_X(k) − Y_X(0)), pooled\n\n| arm | m | 95% CI |\n|---|---|---|")
    for nm in ("drift", "filler", "prose", "none"): md(f"| {nm} | {f2(pt[f'm_{nm}'])} | {ci(CI[f'm_{nm}'])} |")
    md(f"\nReading (A4.3 rule): **{rd}**")
    # S5
    J["s5"] = {k: {"value": pt[k], "ci": CI[k]} for k in ("d_prose", "d_coh", "rho_dprose", "rho_dcoh")}
    md(f"\n## S5 — prose contrasts (descriptive)\n\nΔ_prose = Y_drift − Y_prose = {f2(pt['d_prose'])} {ci(CI['d_prose'])} · ρ vs Y0 {f2(pt['rho_dprose'])} {ci(CI['rho_dprose'])}\n\n"
       f"Δ_coh = Y_prose − Y_filler = {f2(pt['d_coh'])} {ci(CI['d_coh'])} · ρ vs Y0 {f2(pt['rho_dcoh'])} {ci(CI['rho_dcoh'])}")
    # S6
    md("\n## S6 — by mode, counterbalance, k\n\n| subset | items | ρ(Δ, Y0) | 95% CI | mean Δ |\n|---|---|---|---|---|"); J["s6"] = {}
    subsets = [(f"mode {m}", [t for t in tids if cells[t][0] == m], items) for m in B.B5_MODES] + \
              [(f"cell {cb}", tids, [i for i in items if C[i]["counterbalance"] == cb]) for cb in ("DONEsys", "READYsys")]
    for nm, ts, its in subsets:
        if len(its) < 3: md(f"| {nm} | {len(its)} | n/a | | |"); continue
        Gs = Grid(Y, its, seeds, seed_of, ts); p_, c_ = boot_stats(Gs, tmpl_of)
        md_ = float(np.nanmean(Gs.per_item(Gs.d, np.ones(S)))); J["s6"][nm] = {"rho": p_["rho_h1"], "ci": c_["rho_h1"], "mean_delta": md_, "items": len(its)}
        md(f"| {nm} | {len(its)} | {f2(p_['rho_h1'])} | {ci(c_['rho_h1'])} | {f2(md_)} |")
    md("\n| k | " + " | ".join(str(k) for k in KS if k > 0) + " |\n|" + "---|" * (len(KS)))
    byk = {k: float(np.mean([Y[(t, i, DR, k)] - Y[(t, i, FI, k)] for t in tids for i in items if (t, i, DR, k) in Y])) for k in KS if k > 0}
    J["s6"]["by_k"] = byk; md("| mean Δ | " + " | ".join(f2(byk[k]) for k in byk) + " |")
    # S7 + reported checks
    if repro is not None:
        md(f"\n## S7 — the B-b 8 items (apart; never pooled)\n\nRepro vs B-b's b5_q0: {repro['n']} rows, bitwise {repro['bitwise']}, "
           f"max |Δ| {repro['max']:.3g} nats (stop above {repro['tol']}).")
        J["s7"] = {"repro": repro}
        if bb_q0 is not None:
            Yb = D.y_signed(bb_q0[:, 4], bb_q0[:, 5], [C[int(i)]["target_sys"] for i in bb_q0[:, 1]])
            Yb = {(int(r[0]), int(r[1]), int(r[2]), int(r[3])): y for r, y in zip(bb_q0, Yb) if r[0] < B.WI_TID0}
            md("\n| item | Δ_i | Y0_i | Δ at k = 1 |\n|---|---|---|---|"); J["s7"]["items"] = {}
            for i in sorted({k[1] for k in Yb}):
                dv = np.mean([Yb[(t, i, 0, k)] - Yb[(t, i, 1, k)] for t in tids for k in KP if (t, i, 0, k) in Yb])
                y0 = np.mean([Yb[(t, i, 0, 0)] for t in tids if (t, i, 0, 0) in Yb])
                k1 = np.mean([Yb[(t, i, 0, 1)] - Yb[(t, i, 1, 1)] for t in tids if (t, i, 0, 1) in Yb])
                J["s7"]["items"][C[i]["id"]] = {"delta": float(dv), "y0": float(y0), "delta_k1": float(k1)}
                md(f"| {C[i]['id']} | {f2(dv)} | {f2(y0)} | {f2(k1)} |")
            md("\nObservation only (A4.4): c0668's k = 1 value is in the last column; not tested.")
    if prose is not None:
        v_ = list(prose.values()); J["prose"] = {"transcripts": len(v_), "DONE": sum(x["DONE"] for x in v_), "READY": sum(x["READY"] for x in v_), "tokens": sum(x["ntok"] for x in v_)}
        md(f"\nProse passages: {len(v_)} transcripts, {J['prose']['tokens']:,} tokens; target-family words DONE {J['prose']['DONE']} · READY {J['prose']['READY']} (reported, not filtered).")
    if gap is not None:
        J["gap"] = {"max": gap["max"], "median": gap["median"], "n": gap["n"]}
        md(f"\nSingle-pass + crop vs fresh pass (A3.3, reported): n {gap['n']}, max {gap['max']:.3f}, median {gap['median']:.3f} nats.")
    md("\n## Per item (fresh)\n\n| item | template | cell | Δ_i | Y0_i | headroom |\n|---|---|---|---|---|---|")
    for n_, i in sorted(enumerate(items), key=lambda x: y0_i[x[0]]):
        md(f"| {C[i]['id']} | {C[i]['template_idx']} | {C[i]['cell']} | {f2(d_i[n_])} | {f2(y0_i[n_])} | {f2(h_i[n_])} |")
    J["per_item"] = {C[i]["id"]: {"delta": float(d_i[n_]), "y0": float(y0_i[n_]), "headroom": float(h_i[n_])} for n_, i in enumerate(items)}
    return OUT, J

if sys.argv[1:] == ["--selftest"]:
    fails = []
    def check(n, ok): print(("PASS " if ok else "FAIL ") + n, flush=True); fails.append(n) if not ok else None
    FRESH = [x["item"] for x in json.loads((HERE / "fresh_items.json").read_text(encoding="utf-8"))["items"]]
    CELLS = [(m, p, t, s) for m in B.B5_MODES for p in ("P-none", "P-neutral", "P-curious") for t in (0.7, 1.0) for s in B.B5_SEEDS]
    def synth(y0f, dfn, mv=lambda X, y0: 0.0, noise=0.05, gs=1, items=FRESH, tids=None):
        """Y_X(0) = y0f(i) for every arm except none (Y_none(0) = 0); Y_X(k) = Y_X(0) + mv(X, y0) + noise;
        Y_filler(k) additionally − dfn(i, y0) so Δ_i ≈ dfn."""
        g = np.random.default_rng(gs); R = []
        for t in (tids if tids is not None else range(len(CELLS))):
            for i in items:
                y0 = y0f(i)
                for k in D.K_Q0:
                    for X in (DR, FI, NO, PR):
                        y = (0.0 if X == NO else y0) if k == 0 else (0.0 if X == NO else y0) + mv(X, y0) + noise * g.normal()
                        if X == FI and k > 0: y -= dfn(i, y0)
                        R.append((t, i, X, k, y if C[i]["target_sys"] == "DONE" else -y, 0.0, 100 + k))
        return np.array(R, float)
    Y0 = {i: float(np.random.default_rng([5, i]).normal(0, 3)) for i in FRESH}
    _, J = analyze(synth(lambda i: Y0[i], lambda i, y0: 0.3 * y0), CELLS)
    check(f"Δ = 0.3·Y0 → H1 supported (ρ {J['primary']['rho']:+.2f} {J['primary']['ci']})", J["primary"]["verdict"] == "supported")
    _, J = analyze(synth(lambda i: Y0[i], lambda i, y0: -0.3 * y0), CELLS)
    check(f"Δ = −0.3·Y0 → H1 contradicted", J["primary"]["verdict"] == "contradicted")
    Z = {i: float(np.random.default_rng([6, i]).normal(0, 1)) for i in FRESH}
    _, J = analyze(synth(lambda i: Y0[i], lambda i, y0: Z[i]), CELLS)
    check(f"Δ independent of Y0 → H1 not supported (ρ {J['primary']['rho']:+.2f} {ci(J['primary']['ci'])})", J["primary"]["verdict"] == "not supported")
    check(f"  … and the sign rule sits near its null (share {J['s2']['share']:.0%}, p {J['s2']['p_perm']:.2f})", J["s2"]["p_perm"] > 0.01)
    _, J = analyze(synth(lambda i: Y0[i], lambda i, y0: np.sign(y0) * 1.0), CELLS)
    check(f"sign(Δ) = sign(Y0) by construction → share 100%, p < 0.01 ({J['s2']['p_perm']:.3f})", J["s2"]["share"] == 1.0 and J["s2"]["p_perm"] < 0.01)
    _, J = analyze(synth(lambda i: Y0[i], lambda i, y0: -1.0), CELLS)
    check(f"Δ −1 everywhere → S1 content-driven ({J['s1']['verdict']})", J["s1"]["verdict"] == "content-driven")
    _, J = analyze(synth(lambda i: Y0[i], lambda i, y0: 0.0), CELLS)
    check(f"Δ 0 → S1 distance-driven ({J['s1']['verdict']})", J["s1"]["verdict"] == "distance-driven")
    amp = lambda X, y0: np.sign(y0) * 1.0 if X == DR else 0.0          # drift pushes away from 0, filler still
    _, J = analyze(synth(lambda i: Y0[i], lambda i, y0: 0.0, amp), CELLS)
    check(f"drift +1 toward the leader, filler 0 → S4 amplification ({J['s4']['reading']}; m_drift {J['s4']['drift']['m']:+.2f})", J["s4"]["reading"] == "amplification")
    cmp_ = lambda X, y0: -np.sign(y0) * 1.0 if X == FI else 0.0
    _, J = analyze(synth(lambda i: Y0[i], lambda i, y0: 0.0, cmp_), CELLS)
    check(f"filler −1 toward 0, drift 0 → S4 compression ({J['s4']['reading']})", J["s4"]["reading"] == "compression")
    both = lambda X, y0: np.sign(y0) * (1.0 if X == DR else -1.0 if X == FI else 0.0)
    _, J = analyze(synth(lambda i: Y0[i], lambda i, y0: 0.0, both), CELLS)
    check(f"drift +1, filler −1 → S4 both ({J['s4']['reading']})", J["s4"]["reading"] == "both")
    pr = lambda X, y0: 0.7 if X == PR else 0.0
    _, J = analyze(synth(lambda i: Y0[i], lambda i, y0: 0.0, pr), CELLS)
    check(f"prose +0.7 → Δ_prose −0.7, Δ_coh +0.7 ({J['s5']['d_prose']['value']:+.2f}, {J['s5']['d_coh']['value']:+.2f})",
          abs(J["s5"]["d_prose"]["value"] + 0.7) < 0.05 and abs(J["s5"]["d_coh"]["value"] - 0.7) < 0.05)
    # template clustering: Δ shared WITHIN a template (template effect) → template × seed CI wider than items × seed
    TE = {tp: float(np.random.default_rng([7, tp]).normal(0, 2)) for tp in range(30)}
    _, J = analyze(synth(lambda i: Y0[i], lambda i, y0: TE[C[i]["template_idx"]]), CELLS)
    w_t = np.diff(J["s1"]["ci_template_seed"])[0]; w_i = np.diff(J["s1"]["ci_item_seed"])[0]
    check(f"template-level Δ → template × seed CI wider than items × seed ({w_t:.2f} vs {w_i:.2f})", w_t > w_i)
    q = synth(lambda i: Y0[i], lambda i, y0: 0.0); q[(q[:, 2] == PR) & (q[:, 3] == 8), 6] += 1
    _, J = analyze(q, CELLS); check(f"prose distance mismatch planted → counted ({J['distance_mismatch']})", J["distance_mismatch"] > 0)
    _, J = analyze(synth(lambda i: Y0[i], lambda i, y0: 0.3 * y0, tids=[t for t in range(len(CELLS)) if CELLS[t][0] == "M1"]), CELLS)
    check("M1-only rows → S6 mode M3 has no transcripts and is skipped, M1 present", "mode M1" in J["s6"])
    check("ranks: ties averaged", list(ranks([3, 1, 3, 2])) == [2.5, 0.0, 2.5, 1.0])
    print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails)); sys.exit(1 if fails else 0)

F, FB = Path(sys.argv[1]), Path(sys.argv[2]); TAG = sys.argv[3] if len(sys.argv) > 3 else "REAL_"
q6 = np.load(F / f"{TAG}b6_q0.npz")["rows"]
cells = [tuple(c) for c in json.loads((FB / f"{TAG}b5_transcripts_manifest.json").read_text(encoding="utf-8"))["cells"]]
rd = lambda n: json.loads((F / f"{TAG}{n}").read_text(encoding="utf-8"))
OUT, J = analyze(q6, cells, rd("b6_repro.json"), rd("b6_prose.json"), rd("b6_gap_report.json"), np.load(FB / f"{TAG}b5_q0.npz")["rows"])
(F / f"{TAG}B6_ANALYSIS.md").write_text("\n".join(OUT) + "\n", encoding="utf-8")
(F / f"{TAG}B6_analysis.json").write_text(json.dumps(J, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)), encoding="utf-8")
print(f"wrote {F / (TAG + 'B6_ANALYSIS.md')} ({len(OUT)} lines)")
