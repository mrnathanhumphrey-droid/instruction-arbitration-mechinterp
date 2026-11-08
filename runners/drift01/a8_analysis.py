"""HUNT-DRIFT-01 A8 analysis (EXPLORATORY; Amendment 8 6bc527cd…, locked). Local, numpy only.
  python a8_analysis.py --selftest
  python a8_analysis.py <pulled A8 folder> [TAG] [--a5 <pulled A5 folder> --bb <pulled B-b folder>]
Writes <A8 folder>/<TAG>A8_ANALYSIS.md + <TAG>A8_analysis.json. Estimator = A5.2's via a6_analysis.py (imported
unchanged): per item, cell and seed, the mean over that seed's pairs of Δ = Y(drift) − Y(filler) at k = 1; a contrast is
a weight vector over the four cells (M1.M1, M3.M3, M1.M3, M3.M1); template-balanced aligned A and READY part W; two-way
cluster bootstrap over TEMPLATES × SEEDS (2,000, SEED_BOOT 7101001).
PRIMARY (A8.3, 95%): P1 reply effect R = ½[(M1.M3 − M1.M1) + (M3.M3 − M3.M1)], predicted −.
Secondary (A8.4): S1 user-turn effect U · S2 interaction · S3 each cell's Δ (+ A5's k = 1 M1 / M3 with --a5 --bb) ·
S4 R by persona and by temperature · S5 P1 on the no-space readout · S6 the re-read vs A5's a5_q0 (with --a5)."""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
_argv, sys.argv = sys.argv, sys.argv[:1]          # a6_analysis runs its own self-test on import when argv says so
import a6_analysis as A
sys.argv = _argv
import drift01_core as D
sys.stdout.reconfigure(encoding="utf-8")
C, f2, ci = A.C, A.f2, A.ci
f3 = lambda x: "n/a" if x is None else f"{x:.3f}"
CELLS = ("M1.M1", "M3.M3", "M1.M3", "M3.M1")      # user turn . assistant turn
CON = {"R  reply effect (answer − clarification)": (-0.5, 0.5, 0.5, -0.5),
       "U  user-turn effect (question − 'Continue.')": (-0.5, 0.5, -0.5, 0.5),
       "R × U interaction": (1.0, 1.0, -1.0, -1.0)}
PRIM = "R  reply effect (answer − clarification)"

class Data8:
    """Y[item, seed, cell] = mean over the seed's (selected) pairs of Y(drift) − Y(filler); exposes what a6_analysis'
    aw / resamples / est read (items, draws, tu, tix, rdy, pos, per_draw)."""
    def __init__(self, q, pair_seed, keep_pairs=None, lp=(4, 5)):
        keep = set(range(len(pair_seed))) if keep_pairs is None else set(keep_pairs)
        q = q[np.isin(q[:, 0], sorted(keep))]
        self.items = sorted({int(x) for x in q[:, 3]}); ii = {x: n for n, x in enumerate(self.items)}
        self.draws = sorted({int(pair_seed[j]) for j in keep}); si = {s: n for n, s in enumerate(self.draws)}
        y = D.y_signed(q[:, lp[0]], q[:, lp[1]], [C[int(i)]["target_sys"] for i in q[:, 3]])
        cells = {}
        for r, v in zip(q, y): cells[(int(r[0]), int(r[1]), int(r[3]), int(r[2]))] = v
        S = np.zeros((len(self.items), len(self.draws), len(CELLS))); N = np.zeros_like(S)
        for j in keep:
            for c in range(len(CELLS)):
                for i in self.items:
                    d, f = cells.get((j, c, i, 0), np.nan), cells.get((j, c, i, 1), np.nan)
                    S[ii[i], si[int(pair_seed[j])], c] += d - f; N[ii[i], si[int(pair_seed[j])], c] += 1
        if not np.isfinite(S).all(): raise SystemExit("a (pair, cell, item) is missing drift or filler, or not finite — not a complete A8 grid")
        if len(set(N.ravel())) != 1: raise SystemExit("pairs per seed differ across cells / items — not a complete A8 grid")
        self.Y = S / N
        self.rdy = np.array([C[i]["counterbalance"] == "READYsys" for i in self.items])
        tm = [C[i]["template_idx"] for i in self.items]; self.tu = sorted(set(tm)); self.tix = np.array([self.tu.index(x) for x in tm])
        self.pos = np.array([C[i]["cell"].split("|")[1] for i in self.items])
    def per_draw(self, w, ns=None, minus_anchor=False):
        return np.tensordot(self.Y, np.asarray(w, float), axes=([2], [0]))

def point_A(items, vals):
    """Template-balanced aligned A of one value per item (point estimate; descriptive)."""
    rdy = np.array([C[i]["counterbalance"] == "READYsys" for i in items]); tm = np.array([C[i]["template_idx"] for i in items]); v = np.asarray(vals)
    ts = [t for t in sorted(set(tm)) if ((tm == t) & rdy).any() and ((tm == t) & ~rdy).any()]
    return float(np.mean([(v[(tm == t) & ~rdy].mean() + v[(tm == t) & rdy].mean()) / 2 for t in ts]))

def analyze(q, meta, a5=None, cells_bb=None, reread=None):
    seed, pers, temp = meta["pair_seed"], meta["pair_persona"], meta["pair_temp"]
    Dd = Data8(q, seed); RS = A.resamples(Dd); OUT, J = [], {}; md = OUT.append
    md(f"Items {len(Dd.items)} ({int((~Dd.rdy).sum())} DONEsys · {int(Dd.rdy.sum())} READYsys) from {len(Dd.tu)} templates · {len(seed)} M1 / M3 pairs "
       f"({len(Dd.draws)} seeds) · cells {', '.join(CELLS)} (user turn . reply) · Δ = drift − filler at k = 1 · bootstrap {D.BOOT} over templates × seeds, seed {D.SEED_BOOT}.")
    e = A.est(Dd, RS, CON[PRIM], None); J["P1"] = {**e, "verdict": A.verdict(e, -1)}
    md(f"\n## PRIMARY (95% CI)\n\n**P1 — {PRIM}, aligned part A, predicted −: A = {f2(e['A'])} {ci(e['A_ci'])} → {J['P1']['verdict']}** "
       f"({e['templates']} templates; W = {f2(e['W'])} {ci(e['W_ci'])})")
    md("\n## S1 / S2 — user-turn effect and interaction (95%)\n\n| contrast | A | 95% CI | W | 95% CI |\n|---|---|---|---|---|")
    J["S1_S2"] = {}
    for name, w in CON.items():
        if name == PRIM: continue
        x = A.est(Dd, RS, w, None); J["S1_S2"][name] = x; md(f"| {name} | {f2(x['A'])} | {ci(x['A_ci'])} | {f2(x['W'])} | {ci(x['W_ci'])} |")
    md("\n## S3 — each cell's Δ (drift − filler, k = 1; 95%)\n\n| cell | A | 95% CI | W | 95% CI |\n|---|---|---|---|---|")
    J["S3"] = {}
    for c, lab in enumerate(CELLS):
        x = A.est(Dd, RS, [1.0 if b == c else 0.0 for b in range(len(CELLS))], None); J["S3"][lab] = x
        md(f"| {lab} | {f2(x['A'])} | {ci(x['A_ci'])} | {f2(x['W'])} | {ci(x['W_ci'])} |")
    if a5 is not None and cells_bb is not None:          # A5's k = 1 drift − filler by mode (its 120 items; descriptive)
        Y5 = D.y_signed(a5[:, 4], a5[:, 5], [C[int(i)]["target_sys"] for i in a5[:, 1]]); k1 = {}
        for r, v in zip(a5, Y5):
            if int(r[3]) == 1 and int(r[2]) in (0, 1) and int(r[0]) < len(cells_bb): k1[(int(r[0]), int(r[1]), int(r[2]))] = v
        its = sorted({k[1] for k in k1})
        for m in ("M1", "M3"):
            ts = [t for t in range(len(cells_bb)) if cells_bb[t][0] == m]
            vals = [np.mean([k1[(t, i, 0)] - k1[(t, i, 1)] for t in ts]) for i in its]
            J["S3"][f"A5 {m} k=1"] = point_A(its, vals); md(f"\nA5's own k = 1 Δ, {m} transcripts (its 120 items, point estimate): A = {f2(J['S3'][f'A5 {m} k=1'])}.")
    md("\n## S4 — R by persona and by temperature (95%)\n")
    J["S4"] = {}
    for lab, keep in [(f"persona {p}", [j for j in range(len(seed)) if pers[j] == p]) for p in sorted(set(pers))] + \
                     [(f"temperature {t}", [j for j in range(len(seed)) if temp[j] == t]) for t in sorted(set(temp))]:
        Ds = Data8(q, seed, keep); x = A.est(Ds, RS, CON[PRIM], None); J["S4"][lab] = x
        md(f"- {lab} ({len(keep)} pairs): R = {f2(x['A'])} {ci(x['A_ci'])}")
    Dn = Data8(q, seed, lp=(7, 8)); x = A.est(Dn, RS, CON[PRIM], None); r = float(np.corrcoef(Dd.Y.ravel(), Dn.Y.ravel())[0, 1])
    J["S5"] = {**x, "verdict_by_rule": A.verdict(x, -1), "r_cells": r}
    md(f"\n## S5 — the no-space readout\n\nR = {f2(x['A'])} {ci(x['A_ci'])} ({A.verdict(x, -1)} by the same rule; reported); cell-level r with the locked readout {r:+.3f}.")
    if reread is not None and a5 is not None:
        ref = {(int(r_[0]), int(r_[1]), int(r_[2])): (r_[4], r_[5]) for r_ in a5 if int(r_[3]) == 1}
        dy, same = [], 0
        for r_ in reread:
            k = (int(r_[0]), int(r_[1]), int(r_[2]))
            if k in ref:
                same += int((r_[3], r_[4]) == ref[k]); dy.append(abs((r_[3] - r_[4]) - (ref[k][0] - ref[k][1])))
        J["S6"] = {"n": len(dy), "bitwise": same, "dY_median": float(np.median(dy)) if dy else None, "dY_max": float(max(dy)) if dy else None}
        md(f"\n## S6 — re-read of {len({int(x[1]) for x in reread})} A5 items, unspliced, vs A5's a5_q0 at k = 1\n\n{len(dy)} rows matched; bitwise {same}; "
           f"|ΔY| median {f3(J['S6']['dY_median'])}, max {f3(J['S6']['dY_max'])} nats (A5 reached k = 1 by cropping a 32-turn prefill; reported).")
    return OUT, J

def synth(items, R_, U_, I_, npairs=48, noise=0.3, seed=1):
    """a8_q0-shaped rows with planted cell effects (drift − filler) = the contrast weights × the planted values."""
    g = np.random.default_rng(seed); rows = []; eff = np.array([0.0] * 4)
    for w, v in ((CON[PRIM], R_), (CON["U  user-turn effect (question − 'Continue.')"], U_), (CON["R × U interaction"], I_)):
        w = np.asarray(w); eff += v * w / (w @ w)
    pers = np.array([("P-none", "P-neutral", "P-curious")[(j // 2) % 3] for j in range(npairs)]); temp = np.array([(0.7, 1.0)[j % 2] for j in range(npairs)], float)
    sd = np.array([7101201 + j // 6 for j in range(npairs)])
    for j in range(npairs):
        for i in items:
            base = g.normal(-2, 1); put = lambda y: (y, 0.0) if C[i]["target_sys"] == "DONE" else (0.0, y)
            for c in range(4):
                f = base + g.normal(0, noise); d = f + eff[c] + g.normal(0, noise)
                rows += [(j, c, 0, i, *put(d), 50, *put(d)), (j, c, 1, i, *put(f), 50, *put(f))]
    return np.array(rows, float), {"pair_seed": sd, "pair_persona": pers, "pair_temp": temp}

if sys.argv[1:] == ["--selftest"]:
    fails = []
    def check(name, ok):
        print(("PASS " if ok else "FAIL ") + name); (None if ok else fails.append(name))
    rng = np.random.default_rng(7101899)
    items = sorted(int(i) for t in range(30) for cb in ("DONEsys", "READYsys")
                   for i in rng.choice([j for j in range(720) if C[j]["template_idx"] == t and C[j]["counterbalance"] == cb], 2, replace=False))
    UL, IL = "U  user-turn effect (question − 'Continue.')", "R × U interaction"
    q, m = synth(items, -1.0, 0.0, 0.0); _, J = analyze(q, m)
    check(f"planted R −1 → recovered ({J['P1']['A']:+.3f}), supported; U ≈ 0 ({J['S1_S2'][UL]['A']:+.3f})", abs(J["P1"]["A"] + 1) < 0.05 and J["P1"]["verdict"] == "supported" and abs(J["S1_S2"][UL]["A"]) < 0.05)
    q, m = synth(items, 0.0, -1.5, 0.0); _, J = analyze(q, m)
    check(f"planted U −1.5 only → R ≈ 0, not supported ({J['P1']['A']:+.3f}); U recovered ({J['S1_S2'][UL]['A']:+.3f})", J["P1"]["verdict"] == "not supported" and abs(J["S1_S2"][UL]["A"] + 1.5) < 0.05)
    q, m = synth(items, 0.0, 0.0, 2.0); _, J = analyze(q, m)
    check(f"planted interaction +2 only → R ≈ 0 ({J['P1']['A']:+.3f}); interaction recovered ({J['S1_S2'][IL]['A']:+.3f})", abs(J["P1"]["A"]) < 0.05 and abs(J["S1_S2"][IL]["A"] - 2) < 0.1)
    q, m = synth(items, +1.0, 0.0, 0.0); _, J = analyze(q, m)
    check(f"planted R +1 → contradicted ({J['P1']['A']:+.3f})", J["P1"]["verdict"] == "contradicted")
    check(f"S4 has 3 personas + 2 temperatures ({len(J['S4'])})", len(J["S4"]) == 5)
    q, m = synth(items, -1.0, 0.0, 0.0); q = q[~((q[:, 0] == 3) & (q[:, 1] == 2) & (q[:, 2] == 1) & (q[:, 3] == items[0]))]
    try: analyze(q, m); check("a missing filler row is refused", False)
    except SystemExit: check("a missing filler row is refused", True)
    print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails)); sys.exit(1 if fails else 0)

if __name__ == "__main__":
    args = sys.argv[1:]; F = Path(args[0]); TAG = args[1] if len(args) > 1 and not args[1].startswith("--") else "REAL_"
    opt = {args[j]: args[j + 1] for j in range(len(args) - 1) if args[j].startswith("--")}
    z = np.load(F / f"{TAG}a8_q0.npz"); meta = {k: z[k] for k in ("pair_seed", "pair_persona", "pair_temp")}
    a5 = np.load(Path(opt["--a5"]) / f"{TAG}a5_q0.npz")["rows"] if "--a5" in opt else None
    cbb = json.loads((Path(opt["--bb"]) / f"{TAG}b5_transcripts_manifest.json").read_text(encoding="utf-8"))["cells"] if "--bb" in opt else None
    OUT, J = analyze(z["rows"], meta, a5, cbb, np.load(F / f"{TAG}a8_reread.npz")["rows"])
    G = json.loads((F / f"{TAG}a8_gap_report.json").read_text(encoding="utf-8")); RC = json.loads((F / f"{TAG}a8_rowcheck.json").read_text(encoding="utf-8"))
    head = ["# HUNT-DRIFT-01 A8 — Amendment 8 (6bc527cd…) — the k = 1 splice — EXPLORATORY", "",
            f"Row checks: {RC['units']} pair × cell × item (spliced turns = their sources' ids; filler token-matched; unspliced = A5's rows); longest row "
            f"{RC['row_tokens_max']} tokens. Prefill + probe vs a fresh pass (reported): n {G['n']}, max {G['max']:.3f}, median {G['median']:.3f} nats."]
    (F / f"{TAG}A8_ANALYSIS.md").write_text("\n".join(head + [""] + OUT) + "\n", encoding="utf-8")
    (F / f"{TAG}A8_analysis.json").write_text(json.dumps(J, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)), encoding="utf-8")
    print("\n".join(head + [""] + OUT))
