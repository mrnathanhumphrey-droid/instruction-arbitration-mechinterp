"""HUNT-DRIFT-01 A6 analysis (EXPLORATORY; Amendment 6 1e6de4f1…, locked). Local, numpy only.
  python a6_analysis.py --selftest
  python a6_analysis.py <pulled A6 folder> [TAG] [--a5 <pulled A5 folder> --bb <pulled B-b folder>]
Writes <A6 folder>/<TAG>A6_ANALYSIS.md + <TAG>A6_analysis.json. With --a5 / --bb, the n = 0 anchors are compared
bitwise with A5's k = 0 rows of the P-none transcripts (reported).
A6.2 estimator = A5.2's. Y = Y_signed. A contrast is a weight vector over the four arms; per item, c_i = mean over draws
and the n set of the weighted arm sum. Per template t: D̄_t, R̄_t = mean c_i over its DONEsys, READYsys items; aligned
A = mean_t (D̄_t + R̄_t)/2 (+ = toward the system target); READY part W = mean_t (R̄_t − D̄_t)/2. Two-way cluster
bootstrap over TEMPLATES × DRAWS (2,000, SEED_BOOT 7101001).
PRIMARY (A6.3, 95%): P1 I = (defer − obey) − (agree − defy), A pooled over n ∈ {1, 2, 4, 8}, predicted +.
Secondary (A6.4): S1 each arm − anchor at every n · S2 assistant-word and user-word main effects · S3 I at each n ·
S4 I by position and by counterbalance · S5 defer − agree, obey − defy."""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D
sys.stdout.reconfigure(encoding="utf-8")
C = [json.loads(l) for l in open(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl", encoding="utf-8")]
ARMS, NS = ("obey", "defer", "agree", "defy"), (1, 2, 4, 8)
CON = {"I = (defer − obey) − (agree − defy)": (-1, 1, -1, 1),
       "assistant word (system − competing)": (-0.5, 0.5, 0.5, -0.5),
       "user word (asked competing − asked system)": (0.5, 0.5, -0.5, -0.5),
       "defer − agree": (0, 1, -1, 0), "obey − defy": (1, 0, 0, -1)}
PRIM = "I = (defer − obey) − (agree − defy)"
f2 = lambda x: "n/a" if x is None or not np.isfinite(x) else f"{x:+.2f}"
ci = lambda c: f"[{f2(c[0])}, {f2(c[1])}]"

class Data:
    """Y[item, draw, arm, n] and the anchor Y0[item] from a6_q0 rows (item, draw, arm, n, lpD, lpR, dist[, lpD_ns, lpR_ns]);
    lp = the (DONE, READY) columns read — (4, 5) locked, (7, 8) the no-space tokens (reported only)."""
    def __init__(self, q, lp=(4, 5)):
        self.items = sorted({int(x) for x in q[:, 0]}); ii = {x: n for n, x in enumerate(self.items)}
        self.draws = sorted({int(x) for x in q[:, 1] if x >= 0}); di = {x: n for n, x in enumerate(self.draws)}; ni = {n: j for j, n in enumerate(NS)}
        self.Y = np.full((len(self.items), len(self.draws), len(ARMS), len(NS)), np.nan); self.Y0 = np.full(len(self.items), np.nan)
        y = D.y_signed(q[:, lp[0]], q[:, lp[1]], [C[int(i)]["target_sys"] for i in q[:, 0]])
        for r, v in zip(q, y):
            if int(r[2]) == len(ARMS): self.Y0[ii[int(r[0])]] = v
            else: self.Y[ii[int(r[0])], di[int(r[1])], int(r[2]), ni[int(r[3])]] = v
        miss = int(np.isnan(self.Y).sum()) + int(np.isnan(self.Y0).sum())
        if miss: raise SystemExit(f"{miss} (item, draw, arm, n) / anchor cells missing — not a complete A6 grid")
        self.rdy = np.array([C[i]["counterbalance"] == "READYsys" for i in self.items])
        tm = [C[i]["template_idx"] for i in self.items]; self.tu = sorted(set(tm)); self.tix = np.array([self.tu.index(x) for x in tm])
        self.pos = np.array([C[i]["cell"].split("|")[1] for i in self.items])
    def per_draw(self, w, ns, minus_anchor=False):
        """items × draws: the contrast (weights w over ARMS) averaged over the n set."""
        kk = [NS.index(n) for n in ns]; v = np.tensordot(self.Y[:, :, :, kk].mean(axis=3), np.asarray(w, float), axes=([2], [0]))
        return v - (self.Y0[:, None] * float(np.sum(w)) if minus_anchor else 0)

def aw(D_, V, WS, WT, isel=None):
    """A, W over bootstrap columns: V items × draws; WS draws × B; WT templates × B."""
    keep = np.ones(len(D_.items), bool) if isel is None else np.asarray(isel)
    MD = np.array([keep & (D_.tix == t) & ~D_.rdy for t in range(len(D_.tu))], float)
    MR = np.array([keep & (D_.tix == t) & D_.rdy for t in range(len(D_.tu))], float)
    ok = (MD.sum(1) > 0) & (MR.sum(1) > 0); MD[ok] /= MD[ok].sum(1, keepdims=True); MR[ok] /= MR[ok].sum(1, keepdims=True)
    PI = (V @ WS) / WS.sum(0)                                            # items × B
    Db, Rb = MD[ok] @ PI, MR[ok] @ PI; w = WT[ok]; den = w.sum(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (w * (Db + Rb) / 2).sum(0) / den, (w * (Rb - Db) / 2).sum(0) / den, int(ok.sum())

def resamples(D_, boot=D.BOOT, rs=D.SEED_BOOT):
    D.check_seed(rs); rng = np.random.default_rng(rs); WS, WT = [], []
    for _ in range(boot):
        WT.append(np.bincount(rng.integers(0, len(D_.tu), len(D_.tu)), minlength=len(D_.tu)))
        WS.append(np.bincount(rng.integers(0, len(D_.draws), len(D_.draws)), minlength=len(D_.draws)))
    return np.array(WS, float).T, np.array(WT, float).T

def est(D_, RS, w, ns, level=95.0, isel=None, minus_anchor=False):
    V = D_.per_draw(w, ns, minus_anchor); one = lambda n: np.ones((n, 1))
    A, W, used = aw(D_, V, one(len(D_.draws)), one(len(D_.tu)), isel); bA, bW, _ = aw(D_, V, *RS, isel); lo = (100 - level) / 2
    cA, cW = (np.nanpercentile(x, [lo, 100 - lo]) for x in (bA, bW))
    return {"A": float(A[0]), "A_ci": (float(cA[0]), float(cA[1])), "W": float(W[0]), "W_ci": (float(cW[0]), float(cW[1])), "templates": used, "level": level}

def verdict(e, sign=+1):
    lo, hi = e["A_ci"]
    if (sign > 0 and lo > 0) or (sign < 0 and hi < 0): return "supported"
    if (sign > 0 and hi < 0) or (sign < 0 and lo > 0): return "contradicted"
    return "not supported"

def analyze(D_, RS):
    OUT, J = [], {}
    md = OUT.append
    md(f"Items {len(D_.items)} ({int((~D_.rdy).sum())} DONEsys · {int(D_.rdy.sum())} READYsys) from {len(D_.tu)} templates · draws {len(D_.draws)} · "
       f"arms {', '.join(ARMS)} · n ∈ {list(NS)} · bootstrap {D.BOOT} over templates × draws, seed {D.SEED_BOOT}.")
    e = est(D_, RS, CON[PRIM], NS); J["P1"] = {**e, "verdict": verdict(e)}
    md(f"\n## PRIMARY (95% CI)\n\n**P1 — {PRIM}, aligned part A over n ∈ {{1, 2, 4, 8}}, predicted +: A = {f2(e['A'])} {ci(e['A_ci'])} → {J['P1']['verdict']}** "
       f"({e['templates']} templates; W = {f2(e['W'])} {ci(e['W_ci'])})")
    md("\n## S1 — each arm minus the n = 0 anchor (A, 95%)\n\n| arm | " + " | ".join(f"n={n}" for n in NS) + " |\n|" + "---|" * (len(NS) + 1))
    J["S1"] = {}
    for a, arm in enumerate(ARMS):
        w = [1.0 if b == a else 0.0 for b in range(len(ARMS))]; cells = []
        for n in NS:
            x = est(D_, RS, w, (n,), minus_anchor=True); J["S1"][f"{arm} n={n}"] = x; cells.append(f"{f2(x['A'])} {ci(x['A_ci'])}")
        md(f"| {arm} | " + " | ".join(cells) + " |")
    md(f"\nAnchor (n = 0) mean aligned Y: {f2(float(np.mean([(D_.Y0[(D_.tix == t) & ~D_.rdy].mean() + D_.Y0[(D_.tix == t) & D_.rdy].mean()) / 2 for t in range(len(D_.tu))])))}.")
    md("\n## S2 / S5 — main effects and pairwise contrasts, pooled over n (95%)\n\n| contrast | A | 95% CI | W | 95% CI |\n|---|---|---|---|---|")
    J["S2_S5"] = {}
    for name, w in CON.items():
        if name == PRIM: continue
        x = est(D_, RS, w, NS); J["S2_S5"][name] = x; md(f"| {name} | {f2(x['A'])} | {ci(x['A_ci'])} | {f2(x['W'])} | {ci(x['W_ci'])} |")
    md("\n## S3 — I at each n (95%)\n\n| n | A | 95% CI | W | 95% CI |\n|---|---|---|---|---|")
    J["S3"] = {}
    for n in NS:
        x = est(D_, RS, CON[PRIM], (n,)); J["S3"][n] = x; md(f"| {n} | {f2(x['A'])} | {ci(x['A_ci'])} | {f2(x['W'])} | {ci(x['W_ci'])} |")
    md("\n## S4 — I by position and by counterbalance (A, 95%)\n")
    J["S4"] = {}
    for lab, sel in (("position early", D_.pos == "early"), ("position late", D_.pos == "late")):
        x = est(D_, RS, CON[PRIM], NS, isel=sel); J["S4"][lab] = x; md(f"- {lab}: A = {f2(x['A'])} {ci(x['A_ci'])} ({x['templates']} templates)")
    for lab, sel in (("DONEsys items", ~D_.rdy), ("READYsys items", D_.rdy)):   # one cell per template: report the plain item mean
        V = D_.per_draw(CON[PRIM], NS).mean(1); md(f"- {lab}: mean I = {f2(float(V[sel].mean()))} (n {int(sel.sum())} items; descriptive)")
        J["S4"][lab] = float(V[sel].mean())
    return OUT, J

if sys.argv[1:] == ["--selftest"]:
    fails = []
    def check(name, ok):
        print(("PASS " if ok else "FAIL ") + name); (None if ok else fails.append(name))
    rng = np.random.default_rng(7101599)
    items = sorted(int(i) for t in range(30) for cb in ("DONEsys", "READYsys")
                   for i in rng.choice([j for j in range(720) if C[j]["template_idx"] == t and C[j]["counterbalance"] == cb], 2, replace=False))
    def synth(I_true, lex, ready_lean, noise=0.3, seed=1):
        g = np.random.default_rng(seed); rows = []
        for i in items:
            base = g.normal(-2, 1); r = C[i]["counterbalance"] == "READYsys"
            rows.append((i, -1, 4, 0, *(lambda y: (y, 0.0) if C[i]["target_sys"] == "DONE" else (0.0, y))(base), 0))
            for d in range(8):
                for a, arm in enumerate(ARMS):
                    for n in NS:
                        say_sys = arm in ("defer", "agree"); y = base + lex * (1 if say_sys else -1) / 2 + (I_true / 4 if arm in ("defer", "defy") else -I_true / 4)
                        y += (ready_lean if r else -ready_lean) + g.normal(0, noise)       # + toward READY whichever word is the target
                        rows.append((i, d, a, n, *((y, 0.0) if C[i]["target_sys"] == "DONE" else (0.0, y)), 10 * n))
        return np.array(rows, float)
    D1 = Data(synth(1.0, 2.0, 0.0)); R1 = resamples(D1); e = est(D1, R1, CON[PRIM], NS)
    check(f"planted I = +1.0 under word copying +2.0 recovered (A {e['A']:+.3f}) and supported", abs(e["A"] - 1.0) < 0.05 and verdict(e) == "supported")
    e = est(D1, R1, CON["assistant word (system − competing)"], NS)
    check(f"planted word copying +2.0 recovered by the assistant-word main effect (A {e['A']:+.3f})", abs(e["A"] - 2.0) < 0.05)
    D2 = Data(synth(0.0, 2.0, 0.0)); e = est(D2, resamples(D2), CON[PRIM], NS)
    check(f"no I + word copying → I ≈ 0, not supported (A {e['A']:+.3f} {ci(e['A_ci'])})", abs(e["A"]) < 0.1 and verdict(e) == "not supported")
    D3 = Data(synth(0.0, 0.0, 0.8)); e = est(D3, resamples(D3), (1, 0, 0, 0), NS)
    check(f"planted READY lean 0.8 lands in W, not A (A {e['A']:+.3f}, W {e['W']:+.3f})", abs(e["A"] + 2.0) < 0.3 and abs(e["W"] - 0.8) < 0.05)
    D4 = Data(synth(-1.0, 0.0, 0.0)); e = est(D4, resamples(D4), CON[PRIM], NS)
    check(f"planted I = −1.0 → contradicted (A {e['A']:+.3f})", verdict(e) == "contradicted")
    q = synth(1.0, 0.0, 0.0); q = q[~((q[:, 0] == items[0]) & (q[:, 2] == 0) & (q[:, 3] == 8))]
    try: Data(q); check("a missing cell is refused", False)
    except SystemExit: check("a missing cell is refused", True)
    print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails)); sys.exit(1 if fails else 0)

if __name__ == "__main__":
    args = sys.argv[1:]; F = Path(args[0]); TAG = args[1] if len(args) > 1 and not args[1].startswith("--") else "REAL_"
    opt = {args[j]: args[j + 1] for j in range(len(args) - 1) if args[j].startswith("--")}
    q = np.load(F / f"{TAG}a6_q0.npz")["rows"]; D_ = Data(q); RS = resamples(D_)
    OUT, J = analyze(D_, RS)
    if q.shape[1] >= 9:   # REPORTED ONLY, post-lock (LOG 2026-11-05): Y on the no-space tokens the demo replies use
        Dn = Data(q, (7, 8)); J["no_space"] = {}
        OUT.append("\n## Reported only (post-lock, not in A6) — Y read on the no-space tokens \"DONE\" / \"READY\" (the demo replies' tokens)\n\n"
                   "| contrast, pooled over n | A | 95% CI | W | 95% CI |\n|---|---|---|---|---|")
        for name in (PRIM, "assistant word (system − competing)", "user word (asked competing − asked system)"):
            x = est(Dn, RS, CON[name], NS); J["no_space"][name] = x
            OUT.append(f"| {name} | {f2(x['A'])} | {ci(x['A_ci'])} | {f2(x['W'])} | {ci(x['W_ci'])} |")
        r = float(np.corrcoef(D_.Y.ravel(), Dn.Y.ravel())[0, 1]); J["no_space"]["r_cells"] = r
        OUT.append(f"\nCell-level Pearson r, locked Y vs no-space Y (all item × draw × arm × n): {r:+.3f}. Anchor mean aligned Y, no-space: "
                   f"{f2(float(np.mean([(Dn.Y0[(Dn.tix == t) & ~Dn.rdy].mean() + Dn.Y0[(Dn.tix == t) & Dn.rdy].mean()) / 2 for t in range(len(Dn.tu))])))}.")
    head =[f"# HUNT-DRIFT-01 A6 — Amendment 6 (1e6de4f1…) — demonstration factorial — EXPLORATORY", ""]
    G = json.loads((F / f"{TAG}a6_gap_report.json").read_text(encoding="utf-8")); RC = json.loads((F / f"{TAG}a6_rowcheck.json").read_text(encoding="utf-8"))
    head.append(f"Row checks: {RC['probe_draws']} probe × draw, arms token-identical but for the swaps; longest row {RC['row_tokens_max']} tokens. "
                f"Single-pass + crop vs fresh (reported): n {G['n']}, max {G['max']:.3f}, median {G['median']:.3f} nats.")
    if "--a5" in opt and "--bb" in opt:   # anchors vs A5's k = 0 rows of the P-none transcripts (reported)
        cells = json.loads((Path(opt["--bb"]) / f"{TAG}b5_transcripts_manifest.json").read_text(encoding="utf-8"))["cells"]
        q5 = np.load(Path(opt["--a5"]) / f"{TAG}a5_q0.npz")["rows"]; pn = {t for t, c in enumerate(cells) if c[1] == "P-none"}
        ref = {}
        for r in q5[(q5[:, 3] == 0) & (q5[:, 2] == 0)]:
            if int(r[0]) in pn: ref.setdefault(int(r[1]), set()).add((r[4], r[5]))
        anc = {int(r[0]): (r[4], r[5]) for r in q if int(r[2]) == len(ARMS)}
        same = sum(1 for i, v in anc.items() if ref.get(i) == {v}); J["anchor_vs_a5"] = {"bitwise": same, "n": len(anc)}
        head.append(f"Anchors (n = 0) vs A5's k = 0 rows of the P-none transcripts: bitwise on {same} / {len(anc)} probes (reported).")
    (F / f"{TAG}A6_ANALYSIS.md").write_text("\n".join(head + [""] + OUT) + "\n", encoding="utf-8")
    (F / f"{TAG}A6_analysis.json").write_text(json.dumps(J, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)), encoding="utf-8")
    print("\n".join(head + [""] + OUT))
