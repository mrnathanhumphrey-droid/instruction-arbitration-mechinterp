"""HUNT-DRIFT-01 A10 analysis (EXPLORATORY; Amendment 10 cec4ef76…, locked). Local, numpy only.
  python a10_analysis.py --selftest
  python a10_analysis.py <pulled A10 folder> [TAG]
Writes <A10 folder>/<TAG>A10_ANALYSIS.md + <TAG>A10_analysis.json. Estimator = A6.2's (a6_analysis.py, imported
unchanged): per rendering (native / headers / quoted / stated), Y[item, draw, arm, n] and the shared n = 0 anchor;
template-balanced aligned A and READY part W; bootstrap over TEMPLATES × DRAWS (2,000, SEED_BOOT 7101001), the same
resamples for every rendering; differences between renderings taken per item × draw × arm × n (paired) before the bootstrap.
PRIMARY (A10.3, 97.5%, Bonferroni over two): P1 D_rel = I_native − I_headers, predicted + · P2 I_stated, predicted −.
Secondary (A10.4, 95%): S1 I per rendering + retained share · S2 I_quoted, D_quoted · S3 I at each n, intercept + slope
in log2 n per rendering · S4 copy (assistant-word) and user-word main effects per rendering · S5 each arm − anchor per
rendering and n · S6 P1, P2 on the no-space readout + cell r · S7 the repro gate."""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
_argv, sys.argv = sys.argv, sys.argv[:1]          # a6_analysis runs its own self-test on import when argv says so
import a6_analysis as A
sys.argv = _argv
import drift01_core as D
sys.stdout.reconfigure(encoding="utf-8")
C, ARMS, NS, CON, PRIM, f2, ci = A.C, A.ARMS, A.NS, A.CON, A.PRIM, A.f2, A.ci
RENDERS = ("native", "headers", "quoted", "stated")
MAIN = ("assistant word (system − competing)", "user word (asked competing − asked system)")
LX = np.log2(np.array(NS, float)); LXC = LX - LX.mean()

def split(q, lp=(4, 5)):
    """{rendering: Data}; each rendering's rows + the shared anchors (render −1)."""
    anc = q[q[:, 9] == -1]; out = {}
    for r, name in enumerate(RENDERS):
        out[name] = A.Data(np.vstack([q[q[:, 9] == r], anc]), lp)
    a = out["native"]
    assert all(x.items == a.items and x.draws == a.draws for x in out.values())
    return out

def diff(Da, Db):
    """A Data-like object with Y = Da.Y − Db.Y (paired cells), anchor 0."""
    class _D: pass
    x = _D(); x.__dict__.update(Da.__dict__); x.Y = Da.Y - Db.Y; x.Y0 = np.zeros_like(Da.Y0)
    x.per_draw = A.Data.per_draw.__get__(x); return x

def boot(D_, RS, w, ns):
    """(point A, bootstrap A over RS) for one contrast and n set."""
    V = D_.per_draw(w, ns); one = lambda n: np.ones((n, 1))
    a, _, _ = A.aw(D_, V, one(len(D_.draws)), one(len(D_.tu))); b, _, _ = A.aw(D_, V, *RS)
    return float(a[0]), b

def dose(D_, RS):
    """Intercept (at n = 1) and slope per doubling of n, from I at each n (OLS on log2 n), with 95% CIs."""
    P, B = zip(*(boot(D_, RS, CON[PRIM], (n,)) for n in NS)); P, B = np.array(P), np.array(B)
    sl = lambda Y: (LXC @ Y) / (LXC @ LXC); ic = lambda Y: Y.mean(0) - sl(Y) * LX.mean()
    q = lambda v: (float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5)))
    return {"slope": float(sl(P)), "slope_ci": q(sl(B)), "intercept_n1": float(ic(P)), "intercept_ci": q(ic(B))}

def analyze(q):
    R = split(q); a = R["native"]; RS = A.resamples(a); OUT, J = [], {}; md = OUT.append
    md(f"Items {len(a.items)} ({int((~a.rdy).sum())} DONEsys · {int(a.rdy.sum())} READYsys) from {len(a.tu)} templates · draws "
       f"{len(a.draws)} · arms {', '.join(ARMS)} · n ∈ {list(NS)} · probe C · renderings {', '.join(RENDERS)} · bootstrap {D.BOOT} "
       f"over templates × draws, seed {D.SEED_BOOT}, the same resamples for every rendering; differences paired per cell.")
    p1 = A.est(diff(R["native"], R["headers"]), RS, CON[PRIM], NS, level=97.5); p2 = A.est(R["stated"], RS, CON[PRIM], NS, level=97.5)
    J["P1"] = {**p1, "verdict": A.verdict(p1, +1)}; J["P2"] = {**p2, "verdict": A.verdict(p2, -1)}
    md("\n## PRIMARY (97.5% CIs, Bonferroni over the two)\n")
    md(f"**P1 — D_rel = I_native − I_headers (role headers → Sam / Alex), A over n ∈ {{1, 2, 4, 8}}, predicted +: A = {f2(p1['A'])} {ci(p1['A_ci'])} → "
       f"{J['P1']['verdict']}** ({p1['templates']} templates; W = {f2(p1['W'])} {ci(p1['W_ci'])})")
    md(f"\n**P2 — I_stated (every demo user turn asks for the other word), predicted −: A = {f2(p2['A'])} {ci(p2['A_ci'])} → {J['P2']['verdict']}** "
       f"({p2['templates']} templates; W = {f2(p2['W'])} {ci(p2['W_ci'])})")
    md("\n## S1 / S2 — I per rendering and differences from native (A, 95%)\n\n| rendering | I | 95% CI | share of native | native − this | 95% CI |\n|---|---|---|---|---|---|")
    J["S1"], J["S2"] = {}, {}
    for r in RENDERS:
        x = A.est(R[r], RS, CON[PRIM], NS); J["S1"][r] = x
        if r == "native": md(f"| {r} | {f2(x['A'])} | {ci(x['A_ci'])} | 1 | — | — |"); continue
        dd = A.est(diff(R["native"], R[r]), RS, CON[PRIM], NS); J["S2"][f"native − {r}"] = dd
        md(f"| {r} | {f2(x['A'])} | {ci(x['A_ci'])} | {x['A'] / J['S1']['native']['A']:.2f} | {f2(dd['A'])} | {ci(dd['A_ci'])} |")
    md("\nThe quoted log removes the chat form as well as the roles: a drop there can be format, not role (A10.4 S2).")
    md("\n## S3 — dose: I at each n, and intercept (n = 1) + slope per doubling of n (A, 95%)\n\n| rendering | " + " | ".join(f"n={n}" for n in NS) + " | intercept | slope / doubling |\n|" + "---|" * (len(NS) + 3))
    J["S3"] = {}
    for r in RENDERS:
        cells = []
        for n in NS:
            x = A.est(R[r], RS, CON[PRIM], (n,)); J["S3"][f"{r} n={n}"] = x; cells.append(f"{f2(x['A'])} {ci(x['A_ci'])}")
        dz = dose(R[r], RS); J["S3"][f"{r} dose"] = dz
        md(f"| {r} | " + " | ".join(cells) + f" | {f2(dz['intercept_n1'])} {ci(dz['intercept_ci'])} | {f2(dz['slope'])} {ci(dz['slope_ci'])} |")
    md("\n## S4 — disruption check: word main effects per rendering, pooled over n (A, 95%)\n\n| rendering | " + " | ".join(MAIN) + " |\n|---|---|---|")
    J["S4"] = {}
    for r in RENDERS:
        cells = []
        for m in MAIN:
            x = A.est(R[r], RS, CON[m], NS); J["S4"][f"{r} {m}"] = x; cells.append(f"{f2(x['A'])} {ci(x['A_ci'])}")
        md(f"| {r} | " + " | ".join(cells) + " |")
    J["S5"] = {}
    for r in RENDERS:
        md(f"\n## S5 — each arm minus the n = 0 anchor, {r} (A, 95%)\n\n| arm | " + " | ".join(f"n={n}" for n in NS) + " |\n|" + "---|" * (len(NS) + 1))
        for k, arm in enumerate(ARMS):
            w = [1.0 if b == k else 0.0 for b in range(len(ARMS))]; cells = []
            for n in NS:
                x = A.est(R[r], RS, w, (n,), minus_anchor=True); J["S5"][f"{r} {arm} n={n}"] = x; cells.append(f"{f2(x['A'])} {ci(x['A_ci'])}")
            md(f"| {arm} | " + " | ".join(cells) + " |")
    y0 = float(np.mean([(a.Y0[(a.tix == t) & ~a.rdy].mean() + a.Y0[(a.tix == t) & a.rdy].mean()) / 2 for t in range(len(a.tu))]))
    md(f"\nAnchor (n = 0, shared): mean aligned Y {f2(y0)}."); J["S5"]["anchor_aligned_Y"] = y0
    E = split(q, (7, 8)); J["S6"] = {}
    md("\n## S6 — the no-space readout (\"DONE\" / \"READY\", the demo replies' tokens), 97.5%\n")
    for lab, Dd, Dl, sign in (("P1 D_rel", diff(E["native"], E["headers"]), diff(R["native"], R["headers"]), +1), ("P2 I_stated", E["stated"], R["stated"], -1)):
        x = A.est(Dd, RS, CON[PRIM], NS, level=97.5); J["S6"][lab] = {**x, "verdict_by_rule": A.verdict(x, sign)}
        md(f"- {lab}: A = {f2(x['A'])} {ci(x['A_ci'])} ({A.verdict(x, sign)} by the same rule; reported)")
    r = float(np.corrcoef(np.concatenate([R[k].Y.ravel() for k in RENDERS]), np.concatenate([E[k].Y.ravel() for k in RENDERS]))[0, 1])
    J["S6"]["r_cells"] = r; md(f"- cell-level r, locked vs no-space readout, all renderings: {r:+.3f}")
    return OUT, J

def synth(items, I_r, lex=2.0, slope=0.0, noise=0.3, seed=1):
    """a10_q0-shaped rows: Y = base + word copying + the planted interaction per rendering (+ slope × centred log2 n)."""
    g = np.random.default_rng(seed); rows = []
    for i in items:
        b = g.normal(-2, 1); put = lambda y: (y, 0.0) if C[i]["target_sys"] == "DONE" else (0.0, y)
        rows.append((i, -1, 4, 0, *put(b), 0, *put(b), -1))
        for d in range(8):
            for a, arm in enumerate(ARMS):
                for k, n in enumerate(NS):
                    for r, name in enumerate(RENDERS):
                        I_ = I_r[name] + slope * LXC[k]
                        y = b + lex * (1 if arm in ("defer", "agree") else -1) / 2 + (I_ / 4 if arm in ("defer", "defy") else -I_ / 4) + g.normal(0, noise)
                        rows.append((i, d, a, n, *put(y), 10 * n, *put(y), r))
    return np.array(rows, float)

if sys.argv[1:] == ["--selftest"]:
    fails = []
    def check(name, ok):
        print(("PASS " if ok else "FAIL ") + name); (None if ok else fails.append(name))
    rng = np.random.default_rng(7101099)
    items = sorted(int(i) for t in range(30) for cb in ("DONEsys", "READYsys")
                   for i in rng.choice([j for j in range(720) if C[j]["template_idx"] == t and C[j]["counterbalance"] == cb], 2, replace=False))
    _, J = analyze(synth(items, {"native": 2.0, "headers": 0.5, "quoted": 1.0, "stated": -1.0}))
    check(f"stance planted (native 2, headers 0.5, stated −1) → P1 supported ({J['P1']['A']:+.3f} ≈ 1.5), P2 supported ({J['P2']['A']:+.3f} ≈ −1)",
          abs(J["P1"]["A"] - 1.5) < 0.05 and abs(J["P2"]["A"] + 1) < 0.05 and J["P1"]["verdict"] == J["P2"]["verdict"] == "supported")
    check(f"quoted recovered (I {J['S1']['quoted']['A']:+.3f} ≈ 1; native − quoted {J['S2']['native − quoted']['A']:+.3f} ≈ 1)",
          abs(J["S1"]["quoted"]["A"] - 1) < 0.05 and abs(J["S2"]["native − quoted"]["A"] - 1) < 0.05)
    check(f"word copying +2 recovered on every rendering", all(abs(J["S4"][f"{r} {MAIN[0]}"]["A"] - 2) < 0.05 for r in RENDERS))
    _, J = analyze(synth(items, {"native": 2.0, "headers": 2.0, "quoted": 2.0, "stated": 2.0}))
    check(f"function planted (all renderings 2) → P1 not supported ({J['P1']['A']:+.3f}), P2 contradicted ({J['P2']['A']:+.3f})",
          J["P1"]["verdict"] == "not supported" and J["P2"]["verdict"] == "contradicted")
    _, J = analyze(synth(items, {"native": 2.0, "headers": 3.0, "quoted": 2.0, "stated": 0.0}))
    check(f"headers > native → P1 contradicted ({J['P1']['A']:+.3f}); stated 0 → P2 not supported ({J['P2']['A']:+.3f})",
          J["P1"]["verdict"] == "contradicted" and J["P2"]["verdict"] == "not supported")
    check(f"P1 / P2 CIs at 97.5% ({J['P1']['level']}, {J['P2']['level']})", J["P1"]["level"] == J["P2"]["level"] == 97.5)
    _, J = analyze(synth(items, {"native": 2.0, "headers": 1.0, "quoted": 1.0, "stated": -1.0}, slope=0.8))
    dz = J["S3"]["native dose"]
    check(f"planted slope 0.8 per doubling recovered (native {dz['slope']:+.3f}; intercept at n = 1 {dz['intercept_n1']:+.3f} ≈ 2 − 1.2)",
          abs(dz["slope"] - 0.8) < 0.05 and abs(dz["intercept_n1"] - (2 - 0.8 * 1.5)) < 0.05)
    q = synth(items, {"native": 2.0, "headers": 1.0, "quoted": 1.0, "stated": -1.0}); q = q[~((q[:, 0] == items[0]) & (q[:, 2] == 1) & (q[:, 3] == 4) & (q[:, 9] == 3))]
    try: analyze(q); check("a missing stated cell is refused", False)
    except SystemExit: check("a missing stated cell is refused", True)
    q = synth(items, {"native": 2.0, "headers": 0.0, "quoted": 1.0, "stated": -1.0}); s = q[:, 9].copy(); q[s == 0, 9], q[s == 1, 9] = 1, 0
    _, J = analyze(q); check(f"swapping the native / headers codes flips P1 ({J['P1']['A']:+.3f})", J["P1"]["A"] < 0)
    print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails)); sys.exit(1 if fails else 0)

if __name__ == "__main__":
    args = sys.argv[1:]; F = Path(args[0]); TAG = args[1] if len(args) > 1 else "REAL_"
    q = np.load(F / f"{TAG}a10_q0.npz")["rows"]
    OUT, J = analyze(q)
    G = json.loads((F / f"{TAG}a10_gap_report.json").read_text(encoding="utf-8")); RC = json.loads((F / f"{TAG}a10_rowcheck.json").read_text(encoding="utf-8"))
    RP = json.loads((F / f"{TAG}a10_repro.json").read_text(encoding="utf-8")); J["S7"] = RP
    head = ["# HUNT-DRIFT-01 A10 — Amendment 10 (cec4ef76…) — stance toward the user, or a word function learned in context? — EXPLORATORY", "",
            f"Row checks: {RC['probe_draws']} probe × draw × {len(RC['renders'])} renderings, arms token-identical but for the swaps; longest rows "
            f"{RC['row_tokens_max']}. Prefill / crop vs fresh (reported): n {G['n']}, max {G['max']:.3f}, median {G['median']:.3f} nats.",
            f"S7 repro gate: native vs A7's C rows, {RP['n']} rows, bitwise {RP['bitwise']}, max |Δ| {RP['max']:.3f}, median {RP['median']:.3f} nats (tol {RP['tol']})."]
    (F / f"{TAG}A10_ANALYSIS.md").write_text("\n".join(head + [""] + OUT) + "\n", encoding="utf-8")
    (F / f"{TAG}A10_analysis.json").write_text(json.dumps(J, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)), encoding="utf-8")
    print("\n".join(head + [""] + OUT))
