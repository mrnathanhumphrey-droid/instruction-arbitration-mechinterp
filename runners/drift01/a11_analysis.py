"""HUNT-DRIFT-01 A11 analysis (EXPLORATORY; Amendment 11 9c4c627f…, locked). Local, numpy only.
  python a11_analysis.py --selftest
  python a11_analysis.py <pulled A11 folder> <pulled A5 folder> <pulled B-b folder> [TAG]   (TAG default REAL_; DRY: FAKE_)
Writes <A11 folder>/<TAG>A11_ANALYSIS.md + <TAG>A11_analysis.json.
Old arms (drift 0, filler 1, prose 3) come from A5's a5_q0 (REAL: the locked run's file, by hash); the new arm (diverse 4)
from a11_q0. Every contrast is paired per transcript × item × k. Estimator = A5.2 (a5_analysis.py, copied unchanged):
per item c_i = mean over transcripts and K of (Y_X − Y_F); per template D̄_t, R̄_t; A = mean_t (D̄_t + R̄_t)/2, W = mean_t
(R̄_t − D̄_t)/2; two-way cluster bootstrap templates × seeds, 2,000, SEED_BOOT 7101001, one set of resamples for all.
PRIMARY (A11.3, Bonferroni, 97.5%): P1 drift − diverse, A over k {1, 2, 4}, predicted −; P2 filler − diverse, A over
k {8, 16, 32}, predicted −. Secondary (95%): S1 each arm's Y(k) − Y(0), A and W at every k (descriptive) · S2 prose −
diverse, k 8–32 · S3 A, W at every k for drift / filler / prose − diverse · S4 W of both primaries · S5 P1 / P2 by mode
and position · S6 diverse target-family counts per book, and S2 split by the book of assistant turn k (the turn nearest
the probe; operationalization fixed at build, before any data) · S7 the repro gate."""
import hashlib, json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D
import phaseb_core as B
sys.stdout.reconfigure(encoding="utf-8")
C = [json.loads(l) for l in open(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl", encoding="utf-8")]
DR, FI, PR = (B.B6_CONDS.index(x) for x in ("drift", "filler", "prose")); DV = len(B.B6_CONDS)
NC = DV + 1
ARMS = {"drift": DR, "filler": FI, "prose": PR, "diverse": DV}
K_NEAR, K_FAR = (1, 2, 4), (8, 16, 32)
CON = {"drift − diverse": (DR, DV), "filler − diverse": (FI, DV), "prose − diverse": (PR, DV)}
for _a, _c in ARMS.items(): CON[f"{_a}: k − k0"] = (_c, "k0")
A5_REAL_Q0 = "012f407ea79e668bbc25d6a283a58797978ffa6b21ff6905cf8297965d0fff04"
BOOKS = ("fiction", "history", "essays", "travel", "science", "letters", "drama", "philosophy")
f2 = lambda x: "n/a" if x is None or not np.isfinite(x) else f"{x:+.2f}"
ci = lambda c: f"[{f2(c[0])}, {f2(c[1])}]"

class Data:
    """Y[t, i, cond, k] from a5_q0 (old arms) + a11_q0 (diverse); per (item, seed) sums for any contrast, k set, mask."""
    def __init__(self, q5, q11, cells):
        if not len(q11) or set(np.unique(q11[:, 2]).astype(int)) != {DV}: raise SystemExit("a11_q0: cond column is not all 4 (diverse)")
        q5 = q5[np.isin(q5[:, 2], [DR, FI, PR])]; q = np.vstack([q5, q11])
        self.tids = sorted({int(x) for x in q11[:, 0]}); self.items = sorted({int(x) for x in q11[:, 1]}); self.KS = sorted({int(x) for x in q11[:, 3]})
        q = q[np.isin(q[:, 0], self.tids) & np.isin(q[:, 1], self.items)]
        ti = {t: n for n, t in enumerate(self.tids)}; ii = {x: n for n, x in enumerate(self.items)}; self.ki = {k: n for n, k in enumerate(self.KS)}
        self.Y = np.full((len(self.tids), len(self.items), NC, len(self.KS)), np.nan)
        Yr = D.y_signed(q[:, 4], q[:, 5], [C[int(i)]["target_sys"] for i in q[:, 1]])
        for r, y in zip(q, Yr):
            if int(r[3]) in self.ki: self.Y[ti[int(r[0])], ii[int(r[1])], int(r[2]), self.ki[int(r[3])]] = y
        miss = int(np.isnan(self.Y[:, :, [DR, FI, PR, DV], :]).sum())
        if miss: raise SystemExit(f"{miss} (transcript, item, arm, k) cells missing — not a complete A5 × A11 grid")
        self.k0 = self.ki[0] if 0 in self.ki else None
        self.cells = [cells[t] for t in self.tids]; self.seeds = sorted({c[3] for c in self.cells}); S = len(self.seeds)
        self.Sm = np.zeros((len(self.tids), S)); self.Sm[np.arange(len(self.tids)), [self.seeds.index(c[3]) for c in self.cells]] = 1
        self.rdy = np.array([C[i]["counterbalance"] == "READYsys" for i in self.items])
        tm = [C[i]["template_idx"] for i in self.items]; self.tu = sorted(set(tm)); self.tix = np.array([self.tu.index(x) for x in tm])
        self.pos = np.array([C[i]["cell"].split("|")[1] for i in self.items])
    def sums(self, con, ks, tsel=None, tkmask=None):
        """Σ over (transcript, k) of the contrast, and the count, per (item, seed). tsel: transcripts; tkmask: T × |ks| weights."""
        a, b = CON[con]; kk = [self.ki[k] for k in ks]
        if b == "k0":
            if self.k0 is None: raise SystemExit("S1 needs the k = 0 rows")
            d = self.Y[:, :, a, :][:, :, kk] - self.Y[:, :, a, self.k0][:, :, None]
        else: d = (self.Y[:, :, a, :] - self.Y[:, :, b, :])[:, :, kk]
        m = np.ones((len(self.tids), len(kk))) if tkmask is None else np.asarray(tkmask, float)
        if tsel is not None: m = m * np.asarray(tsel, float)[:, None]
        s = (d * m[:, None, :]).sum(2) / len(kk); c = np.broadcast_to(m.sum(1)[:, None] / len(kk), s.shape)
        return s.T @ self.Sm, c.T @ self.Sm

def aw(D_, Ssum, cnt, WS, WT, isel=None):
    """A, W (arrays over columns) at seed weights WS (S × B) and template weights WT (templates × B); templates
    missing a cell among the kept items are left out (their count returned). — a5_analysis.py, unchanged."""
    keep = np.ones(len(D_.items), bool) if isel is None else np.asarray(isel)
    MD = np.array([keep & (D_.tix == t) & ~D_.rdy for t in range(len(D_.tu))], float)
    MR = np.array([keep & (D_.tix == t) & D_.rdy for t in range(len(D_.tu))], float)
    ok = (MD.sum(1) > 0) & (MR.sum(1) > 0); MD[ok] /= MD[ok].sum(1, keepdims=True); MR[ok] /= MR[ok].sum(1, keepdims=True)
    n = cnt @ WS; PI = (Ssum @ WS) / np.where(n > 0, n, np.nan)
    Db, Rb = MD[ok] @ np.nan_to_num(PI), MR[ok] @ np.nan_to_num(PI); w = WT[ok]; den = w.sum(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (w * (Db + Rb) / 2).sum(0) / den, (w * (Rb - Db) / 2).sum(0) / den, int(ok.sum())

def resamples(D_, boot=D.BOOT, rs=D.SEED_BOOT):
    D.check_seed(rs); rng = np.random.default_rng(rs); WS, WT = [], []
    for _ in range(boot):
        WT.append(np.bincount(rng.integers(0, len(D_.tu), len(D_.tu)), minlength=len(D_.tu)))
        WS.append(np.bincount(rng.integers(0, len(D_.seeds), len(D_.seeds)), minlength=len(D_.seeds)))
    return np.array(WS, float).T, np.array(WT, float).T

def est(D_, RS, con, ks, level=95.0, tsel=None, isel=None, tkmask=None):
    Ssum, cnt = D_.sums(con, ks, tsel, tkmask); one = lambda n: np.ones((n, 1))
    A, W, used = aw(D_, Ssum, cnt, one(len(D_.seeds)), one(len(D_.tu)), isel)
    bA, bW, _ = aw(D_, Ssum, cnt, *RS, isel); lo = (100 - level) / 2
    with np.errstate(invalid="ignore"):
        cA, cW = (np.nanpercentile(x, [lo, 100 - lo]) if np.isfinite(x).any() else np.array([np.nan, np.nan]) for x in (bA, bW))
    return {"A": float(A[0]), "A_ci": (float(cA[0]), float(cA[1])), "W": float(W[0]), "W_ci": (float(cW[0]), float(cW[1])), "templates": used, "level": level}

def verdict(c, sign):
    lo, hi = c
    if sign < 0: return "supported" if hi < 0 else "contradicted" if lo > 0 else "not supported"
    return "supported" if lo > 0 else "contradicted" if hi < 0 else "not supported"

def analyze(q5, q11, cells, repro=None, diverse=None, gap=None):
    D_ = Data(q5, q11, cells); RS = resamples(D_); OUT, J = [], {}
    md = lambda *a: OUT.append(" ".join(str(x) for x in a))
    md("# HUNT-DRIFT-01 A11 — Amendment 11 (9c4c627f…) — is word-pool filler a valid baseline? — EXPLORATORY")
    md(f"\nTranscripts {len(D_.tids)} · items {len(D_.items)} ({int((~D_.rdy).sum())} DONEsys · {int(D_.rdy.sum())} READYsys) from "
       f"{len(D_.tu)} templates · k ∈ {D_.KS} · old arms from A5's a5_q0, diverse from a11_q0, paired · bootstrap {D.BOOT} over templates × seeds, seed {D.SEED_BOOT}.")
    if repro is not None:
        J["S7"] = repro
        md(f"\nRepro gate (S7; first 8 A5 items × drift / filler / prose vs A5's a5_q0): {repro['n']} rows, bitwise {repro['bitwise']}, "
           f"max |Δ| {repro['max']:.3g} nats (stop above {repro['tol']}).")
    if D_.k0 is not None:
        same = int(np.sum(D_.Y[:, :, DV, D_.k0] == D_.Y[:, :, DR, D_.k0])); J["k0_identity"] = {"equal": same, "n": D_.Y[:, :, DV, D_.k0].size}
        md(f"\nk = 0 identity (no turns, every arm the same row): diverse = drift bitwise on {same} / {D_.Y[:, :, DV, D_.k0].size} (transcript, item).")
    p1 = est(D_, RS, "drift − diverse", K_NEAR, 97.5); p2 = est(D_, RS, "filler − diverse", K_FAR, 97.5)
    p1["verdict"] = verdict(p1["A_ci"], -1); p2["verdict"] = verdict(p2["A_ci"], -1); J["P1"], J["P2"] = p1, p2
    md("\n## PRIMARY (Bonferroni, 97.5% CIs)\n")
    md(f"**P1 — drift − diverse, aligned part A over k ∈ {{1, 2, 4}}, predicted −: A = {f2(p1['A'])} {ci(p1['A_ci'])} → {p1['verdict']}** ({p1['templates']} templates)")
    md(f"\n**P2 — filler − diverse, aligned part A over k ∈ {{8, 16, 32}}, predicted −: A = {f2(p2['A'])} {ci(p2['A_ci'])} → {p2['verdict']}** ({p2['templates']} templates)")
    md("\nReadings written before any data (A11.3): P1 supported → drift's short-distance damage is not a property of the word-pool "
       "baseline · P1 not supported / contradicted → A5's P1 is read as relative to word-pool filler only · P2 supported → part of "
       "A5's 'prose strengthens' is 'filler weakens' (S2 says how much is left for prose) · P2 not supported → A5's P2 stands as "
       "read · P2 contradicted → natural text weakens the target more than word-pool filler; no simple reading.")
    J["S1"] = {}
    md("\n## S1 — no-filler reference: each arm's Y(k) − Y(0) (95%; distance not matched, descriptive)\n\n| arm | k | A | 95% CI | W | 95% CI |\n|---|---|---|---|---|---|")
    for a in ARMS:
        for k in [k for k in D_.KS if k > 0]:
            e = est(D_, RS, f"{a}: k − k0", (k,)); J["S1"][f"{a} k={k}"] = e
            md(f"| {a} | {k} | {f2(e['A'])} | {ci(e['A_ci'])} | {f2(e['W'])} | {ci(e['W_ci'])} |")
    s2 = est(D_, RS, "prose − diverse", K_FAR); J["S2"] = s2
    md(f"\n## S2 — prose − diverse, k 8–32 (95%): is A5's prose effect specific to one coherent book?\n\nA = {f2(s2['A'])} {ci(s2['A_ci'])} · W = {f2(s2['W'])} {ci(s2['W_ci'])}")
    md("\n## S3 — A and W at every k (95%)\n\n| contrast | k | A | 95% CI | W | 95% CI |\n|---|---|---|---|---|---|"); J["S3"] = {}
    for con in ("drift − diverse", "filler − diverse", "prose − diverse"):
        for k in [k for k in D_.KS if k > 0]:
            e = est(D_, RS, con, (k,)); J["S3"][f"{con} k={k}"] = e
            md(f"| {con} | {k} | {f2(e['A'])} | {ci(e['A_ci'])} | {f2(e['W'])} | {ci(e['W_ci'])} |")
    s4 = {"P1": est(D_, RS, "drift − diverse", K_NEAR), "P2": est(D_, RS, "filler − diverse", K_FAR)}; J["S4"] = s4
    md(f"\n## S4 — READY part W of both primaries (95%)\n\ndrift − diverse, k 1–4: W = {f2(s4['P1']['W'])} {ci(s4['P1']['W_ci'])} · "
       f"filler − diverse, k 8–32: W = {f2(s4['P2']['W'])} {ci(s4['P2']['W_ci'])}")
    md("\n## S5 — P1 / P2 aligned part by subset (95%)\n\n| subset | templates | P1 A | 95% CI | P2 A | 95% CI |\n|---|---|---|---|---|---|"); J["S5"] = {}
    subs = [(f"mode {m}", np.array([c[0] == m for c in D_.cells]), None) for m in B.B5_MODES] + \
           [(f"position {p}", None, D_.pos == p) for p in ("early", "late")]
    for nm, ts, isel in subs:
        if ts is not None and not ts.any(): md(f"| {nm} | 0 | n/a | | n/a | |"); continue
        a = est(D_, RS, "drift − diverse", K_NEAR, tsel=ts, isel=isel); b = est(D_, RS, "filler − diverse", K_FAR, tsel=ts, isel=isel)
        J["S5"][nm] = {"P1": a, "P2": b}
        md(f"| {nm} | {a['templates']} | {f2(a['A'])} | {ci(a['A_ci'])} | {f2(b['A'])} | {ci(b['A_ci'])} |")
    if diverse is not None:
        v_ = [diverse[str(t)] if str(t) in diverse else diverse[t] for t in D_.tids]
        tot = {g: {w: sum(x["per_book"][g][w] for x in v_) for w in ("ntok", "turns", "DONE", "READY")} for g in BOOKS}
        J["S6"] = {"tokens": sum(x["ntok"] for x in v_), "DONE": sum(x["DONE"] for x in v_), "READY": sum(x["READY"] for x in v_), "per_book": tot, "split": {}}
        md(f"\n## S6 — diverse passages (reported, not filtered)\n\n{len(v_)} transcripts, {J['S6']['tokens']:,} tokens; target-family words DONE {J['S6']['DONE']} · READY {J['S6']['READY']}.")
        md("\nS2 (prose − diverse, k 8–32) split by the book of assistant turn k, the turn nearest the probe (95%, descriptive):\n\n"
           "| book | turns | tokens | DONE | READY | (t, k) cells | A | 95% CI | W | 95% CI |\n|---|---|---|---|---|---|---|---|---|---|")
        kk = list(K_FAR)
        for g in BOOKS:
            mask = np.array([[1.0 if 2 * k - 1 < len(x["books"]) and x["books"][2 * k - 1] == g else 0.0 for k in kk] for x in v_])
            e = est(D_, RS, "prose − diverse", K_FAR, tkmask=mask) if mask.sum() else {"A": np.nan, "A_ci": (np.nan, np.nan), "W": np.nan, "W_ci": (np.nan, np.nan)}
            e["cells"] = int(mask.sum()); J["S6"]["split"][g] = e
            md(f"| {g} | {tot[g]['turns']} | {tot[g]['ntok']:,} | {tot[g]['DONE']} | {tot[g]['READY']} | {e['cells']} | {f2(e['A'])} | {ci(e['A_ci'])} | {f2(e['W'])} | {ci(e['W_ci'])} |")
    if gap is not None:
        J["gap"] = {"max": gap["max"], "median": gap["median"], "n": gap["n"]}
        md(f"\nSingle-pass + crop vs fresh pass (reported): n {gap['n']}, max {gap['max']:.3f}, median {gap['median']:.3f} nats.")
    return OUT, J

if sys.argv[1:] == ["--selftest"]:
    fails = []
    def check(n, ok): print(("PASS " if ok else "FAIL ") + n, flush=True); fails.append(n) if not ok else None
    A5I = [x["item"] for x in json.loads((HERE / "a5_items.json").read_text(encoding="utf-8"))["items"]]
    CELLS = [(m, p, t, s) for m in B.B5_MODES for p in ("P-none", "P-neutral", "P-curious") for t in (0.7, 1.0) for s in B.B5_SEEDS]
    NT = len(CELLS)
    BK = {t: [BOOKS[int(x)] for x in np.random.default_rng([11, t]).integers(0, 8, 64)] for t in range(NT)}
    def synth(dr=lambda k, t: (0.0, 0.0), fi=lambda k, t: (0.0, 0.0), pr=lambda k, t: (0.0, 0.0), dv=lambda k, t: (0.0, 0.0), noise=0.3, gs=1, tids=None):
        """Y_base(k) = y0_i + noise; each arm = base + (A(k, t) + s_i·W(k, t)) + noise; all arms equal at k = 0. Returns (a5 rows, a11 rows)."""
        g = np.random.default_rng(gs); R5, R11 = [], []
        for t in (tids if tids is not None else range(NT)):
            for i in A5I:
                y0 = float(np.random.default_rng([5, i]).normal(0, 3)); s = 1.0 if C[i]["counterbalance"] == "READYsys" else -1.0
                sg = 1.0 if C[i]["target_sys"] == "DONE" else -1.0
                for k in D.K_Q0:
                    if k == 0:
                        y = y0 + noise * g.normal()
                        for c in (DR, FI, PR): R5.append((t, i, c, 0, sg * y, 0.0, 0))
                        R11.append((t, i, DV, 0, sg * y, 0.0, 0)); continue
                    yb = y0 + noise * g.normal()
                    for c, f in ((DR, dr), (FI, fi), (PR, pr), (DV, dv)):
                        a, w = f(k, t); y = yb + a + s * w + noise * g.normal()
                        (R11 if c == DV else R5).append((t, i, c, k, sg * y, 0.0, 100 + k))
        return np.array(R5, float), np.array(R11, float)
    DIV = {t: {"ntok": 1, "DONE": 0, "READY": 0, "books": BK[t], "per_book": {b: {"ntok": 1, "turns": 1, "DONE": 0, "READY": 0} for b in BOOKS}} for t in range(NT)}
    run = lambda **kw: analyze(*synth(**kw), CELLS, diverse=DIV)[1]
    J = run(dr=lambda k, t: (-1.0, 0.0) if k in K_NEAR else (0.0, 0.0))
    check(f"drift A −1 at k 1–4 → P1 supported (A {J['P1']['A']:+.2f} {ci(J['P1']['A_ci'])}); P2 not supported",
          J["P1"]["verdict"] == "supported" and abs(J["P1"]["A"] + 1) < 0.1 and J["P2"]["verdict"] == "not supported")
    J = run(dr=lambda k, t: (1.0, 0.0))
    check("drift A +1 → P1 contradicted", J["P1"]["verdict"] == "contradicted")
    J = run(dv=lambda k, t: (-1.0, 0.0))
    check(f"diverse A −1 everywhere (drift, filler at 0) → P1 contradicted, P2 contradicted (P2 A {J['P2']['A']:+.2f})",
          J["P1"]["verdict"] == "contradicted" and J["P2"]["verdict"] == "contradicted" and abs(J["P2"]["A"] - 1) < 0.1)
    J = run(fi=lambda k, t: (-1.0, 0.0) if k in K_FAR else (0.0, 0.0))
    check(f"filler A −1 at k 8–32 → P2 supported (A {J['P2']['A']:+.2f} {ci(J['P2']['A_ci'])}); P1 not supported",
          J["P2"]["verdict"] == "supported" and abs(J["P2"]["A"] + 1) < 0.1 and J["P1"]["verdict"] == "not supported")
    J = run(fi=lambda k, t: (1.0, 0.0))
    check("filler A +1 → P2 contradicted", J["P2"]["verdict"] == "contradicted")
    J = run(dr=lambda k, t: (0.0, 1.0))
    check(f"drift W +1 only → P1 not supported (A {J['P1']['A']:+.2f}); S4 W ≈ +1 ({J['S4']['P1']['W']:+.2f} {ci(J['S4']['P1']['W_ci'])})",
          J["P1"]["verdict"] == "not supported" and abs(J["S4"]["P1"]["W"] - 1) < 0.1 and J["S4"]["P1"]["W_ci"][0] > 0)
    J = run(dv=lambda k, t: (-0.5, 0.0), dr=lambda k, t: (-0.5, 0.0), fi=lambda k, t: (-0.5, 0.0), pr=lambda k, t: (-0.5, 0.0))
    check(f"every arm −0.5 vs k = 0 → S1 diverse k=8 A ≈ −0.5 ({J['S1']['diverse k=8']['A']:+.2f}), P1 / P2 not supported",
          abs(J["S1"]["diverse k=8"]["A"] + 0.5) < 0.1 and abs(J["S1"]["filler k=32"]["A"] + 0.5) < 0.1 and J["P1"]["verdict"] == J["P2"]["verdict"] == "not supported")
    J = run(pr=lambda k, t: (1.0, 0.0))
    check(f"prose A +1 → S2 A ≈ +1 ({J['S2']['A']:+.2f}); every book's split ≈ +1",
          abs(J["S2"]["A"] - 1) < 0.1 and all(abs(J["S6"]["split"][b]["A"] - 1) < 0.15 for b in BOOKS))
    dramak = lambda k, t: (-1.0, 0.0) if k in K_FAR and BK[t][2 * k - 1] == "drama" else (0.0, 0.0)
    J = run(dv=dramak)
    sp = J["S6"]["split"]
    check(f"diverse −1 only when turn k is from drama → drama split ≈ +1 ({sp['drama']['A']:+.2f}), others ≈ 0 (max |A| {max(abs(sp[b]['A']) for b in BOOKS if b != 'drama'):.2f})",
          abs(sp["drama"]["A"] - 1) < 0.15 and all(abs(sp[b]["A"]) < 0.15 for b in BOOKS if b != "drama"))
    q5, q11 = synth(fi=lambda k, t: (-0.5, 0.0), noise=2.0); D_ = Data(q5, q11, CELLS); RS_ = resamples(D_)
    w975 = np.diff(est(D_, RS_, "filler − diverse", K_FAR, 97.5)["A_ci"])[0]; w95 = np.diff(est(D_, RS_, "filler − diverse", K_FAR, 95.0)["A_ci"])[0]
    check(f"97.5% CI wider than 95% ({w975:.3f} vs {w95:.3f})", w975 > w95)
    J = analyze(*synth(dr=lambda k, t: (-1.0, 0.0), tids=[t for t in range(NT) if CELLS[t][0] == "M1"]), CELLS)[1]
    check("M1-only rows → no mode M3 row, P1 still estimated", "mode M3" not in J["S5"] and J["P1"]["verdict"] == "supported")
    J = run(); check(f"k = 0 identity read: {J['k0_identity']['equal']} / {J['k0_identity']['n']}", J["k0_identity"]["equal"] == J["k0_identity"]["n"])
    q5, q11 = synth(); q11 = q11[~((q11[:, 3] == 8) & (q11[:, 1] == A5I[0]) & (q11[:, 0] == 0))]
    try: analyze(q5, q11, CELLS); check("a missing diverse cell → refused", False)
    except SystemExit: check("a missing diverse cell → refused", True)
    q5, q11 = synth(); q5 = q5[~((q5[:, 2] == FI) & (q5[:, 3] == 16) & (q5[:, 1] == A5I[3]))]
    try: analyze(q5, q11, CELLS); check("a missing old-arm cell → refused", False)
    except SystemExit: check("a missing old-arm cell → refused", True)
    q5, q11 = synth(); q11[:, 2] = PR
    try: analyze(q5, q11, CELLS); check("a11_q0 with a wrong cond code → refused", False)
    except SystemExit: check("a11_q0 with a wrong cond code → refused", True)
    print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails)); sys.exit(1 if fails else 0)

if __name__ == "__main__":
    F, F5, FB = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]); TAG = sys.argv[4] if len(sys.argv) > 4 else "REAL_"
    p5 = F5 / f"{TAG}a5_q0.npz"
    if TAG == "REAL_" and hashlib.sha256(p5.read_bytes()).hexdigest() != A5_REAL_Q0: raise SystemExit(f"{p5} is not the locked A5 run's a5_q0")
    q5, q11 = np.load(p5)["rows"], np.load(F / f"{TAG}a11_q0.npz")["rows"]
    cells = [tuple(c) for c in json.loads((FB / f"{TAG}b5_transcripts_manifest.json").read_text(encoding="utf-8"))["cells"]]
    rd = lambda n: json.loads((F / f"{TAG}{n}").read_text(encoding="utf-8"))
    OUT, J = analyze(q5, q11, cells, rd("a11_repro.json"), rd("a11_diverse.json"), rd("a11_gap_report.json"))
    (F / f"{TAG}A11_ANALYSIS.md").write_text("\n".join(OUT) + "\n", encoding="utf-8")
    (F / f"{TAG}A11_analysis.json").write_text(json.dumps(J, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)), encoding="utf-8")
    print(f"wrote {F / (TAG + 'A11_ANALYSIS.md')} ({len(OUT)} lines)")
