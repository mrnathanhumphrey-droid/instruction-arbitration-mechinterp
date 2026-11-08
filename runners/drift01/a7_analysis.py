"""HUNT-DRIFT-01 A7 analysis (EXPLORATORY; Amendment 7 a66ef98b…, locked). Local, numpy only.
  python a7_analysis.py --selftest
  python a7_analysis.py <pulled A7 folder> [TAG]
Writes <A7 folder>/<TAG>A7_ANALYSIS.md + <TAG>A7_analysis.json. Estimator = A6.2's (a6_analysis.py, imported unchanged):
per probe type (C = the item's user turn, N = the same turn asking for the system word), Y[item, draw, arm, n] and the
anchor; template-balanced aligned A and READY part W; bootstrap over TEMPLATES × DRAWS (2,000, SEED_BOOT 7101001), the
same resamples for C and N.
PRIMARY (A7.3, 97.5%, Bonferroni over two): P1 I_C pooled over n, predicted + · P2 I_N pooled over n, predicted −.
Secondary (A7.4, 95%): S1 each arm − anchor at every n, C and N, + the N anchor's level · S2 word main effects on N ·
S3 I_N at each n · S4 on N: defer − defy, obey − agree · S5 P1 / P2 on the no-space readout · S6 I_C, I_N by position
and counterbalance · S7 I_C vs A6's +10.41."""
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
A6_I = 10.41
S4C = {"defer − defy (both against the user; defer shows the system word)": (0, 1, 0, -1), "obey − agree (both do what the user asks)": (1, 0, -1, 0)}

def split(q, lp=(4, 5)):
    """(Data for C, Data for N) from a7_q0 rows; probe column 9."""
    return A.Data(q[q[:, 9] == 0], lp), A.Data(q[q[:, 9] == 1], lp)

def sys_lp(Dd, q, probe):
    """Mean lp of the system word at the anchor, raw (headroom check, A7.6 risk)."""
    r = q[(q[:, 9] == probe) & (q[:, 2] == len(ARMS))]
    v = np.array([x[4] if C[int(x[0])]["target_sys"] == "DONE" else x[5] for x in r])
    return float(v.mean()), float((v > -0.1).mean())

def analyze(q):
    Dc, Dn = split(q); RS = A.resamples(Dc); OUT, J = [], {}; md = OUT.append
    assert Dc.items == Dn.items and Dc.draws == Dn.draws
    md(f"Items {len(Dc.items)} ({int((~Dc.rdy).sum())} DONEsys · {int(Dc.rdy.sum())} READYsys) from {len(Dc.tu)} templates · draws "
       f"{len(Dc.draws)} · arms {', '.join(ARMS)} · n ∈ {list(NS)} · probes C (asks the competing word) and N (asks the system "
       f"word) · bootstrap {D.BOOT} over templates × draws, seed {D.SEED_BOOT}, the same resamples for C and N.")
    p1 = A.est(Dc, RS, CON[PRIM], NS, level=97.5); p2 = A.est(Dn, RS, CON[PRIM], NS, level=97.5)
    J["P1"] = {**p1, "verdict": A.verdict(p1, +1)}; J["P2"] = {**p2, "verdict": A.verdict(p2, -1)}
    md("\n## PRIMARY (97.5% CIs, Bonferroni over the two)\n")
    md(f"**P1 — I_C, {PRIM} on the conflict probe, A over n ∈ {{1, 2, 4, 8}}, predicted +: A = {f2(p1['A'])} {ci(p1['A_ci'])} → {J['P1']['verdict']}** "
       f"({p1['templates']} templates; W = {f2(p1['W'])} {ci(p1['W_ci'])})")
    md(f"\n**P2 — I_N, the same contrast on the no-conflict probe, predicted −: A = {f2(p2['A'])} {ci(p2['A_ci'])} → {J['P2']['verdict']}** "
       f"({p2['templates']} templates; W = {f2(p2['W'])} {ci(p2['W_ci'])})")
    J["S1"] = {}
    for lab, Dd, pr in (("C", Dc, 0), ("N", Dn, 1)):
        md(f"\n## S1 — each arm minus the n = 0 anchor, probe {lab} (A, 95%)\n\n| arm | " + " | ".join(f"n={n}" for n in NS) + " |\n|" + "---|" * (len(NS) + 1))
        for a, arm in enumerate(ARMS):
            w = [1.0 if b == a else 0.0 for b in range(len(ARMS))]; cells = []
            for n in NS:
                x = A.est(Dd, RS, w, (n,), minus_anchor=True); J["S1"][f"{lab} {arm} n={n}"] = x; cells.append(f"{f2(x['A'])} {ci(x['A_ci'])}")
            md(f"| {arm} | " + " | ".join(cells) + " |")
        y0 = float(np.mean([(Dd.Y0[(Dd.tix == t) & ~Dd.rdy].mean() + Dd.Y0[(Dd.tix == t) & Dd.rdy].mean()) / 2 for t in range(len(Dd.tu))]))
        m, frac = sys_lp(Dd, q, pr); J["S1"][f"{lab} anchor"] = {"aligned_Y": y0, "mean_lp_system_word": m, "frac_lp_above_-0.1": frac}
        md(f"\nAnchor (n = 0), probe {lab}: mean aligned Y {f2(y0)}; mean lp(system word) {m:.2f}, {100 * frac:.0f}% of probes above −0.1 (headroom).")
    md("\n## S2 / S4 — on N: word main effects and pairwise contrasts, pooled over n (95%)\n\n| contrast | A | 95% CI | W | 95% CI |\n|---|---|---|---|---|")
    J["S2_S4"] = {}
    for name, w in [(k, CON[k]) for k in ("assistant word (system − competing)", "user word (asked competing − asked system)")] + list(S4C.items()):
        x = A.est(Dn, RS, w, NS); J["S2_S4"][name] = x; md(f"| {name} | {f2(x['A'])} | {ci(x['A_ci'])} | {f2(x['W'])} | {ci(x['W_ci'])} |")
    md("\n## S3 — I_N at each n (95%)\n\n| n | A | 95% CI | W | 95% CI |\n|---|---|---|---|---|")
    J["S3"] = {}
    for n in NS:
        x = A.est(Dn, RS, CON[PRIM], (n,)); J["S3"][n] = x; md(f"| {n} | {f2(x['A'])} | {ci(x['A_ci'])} | {f2(x['W'])} | {ci(x['W_ci'])} |")
    Ec, En = split(q, (7, 8)); J["S5"] = {}
    md("\n## S5 — the no-space readout (\"DONE\" / \"READY\", the demo replies' tokens), 97.5%\n")
    for lab, Dd, Dl, sign in (("P1 I_C", Ec, Dc, +1), ("P2 I_N", En, Dn, -1)):
        x = A.est(Dd, RS, CON[PRIM], NS, level=97.5); r = float(np.corrcoef(Dl.Y.ravel(), Dd.Y.ravel())[0, 1])
        J["S5"][lab] = {**x, "verdict_by_rule": A.verdict(x, sign), "r_cells": r}
        md(f"- {lab}: A = {f2(x['A'])} {ci(x['A_ci'])} ({A.verdict(x, sign)} by the same rule; reported); cell-level r with the locked readout {r:+.3f}")
    md("\n## S6 — I by position and by counterbalance (A, 95%)\n")
    J["S6"] = {}
    for lab, Dd in (("C", Dc), ("N", Dn)):
        for pl, sel in (("position early", Dd.pos == "early"), ("position late", Dd.pos == "late")):
            x = A.est(Dd, RS, CON[PRIM], NS, isel=sel); J["S6"][f"{lab} {pl}"] = x; md(f"- {lab}, {pl}: A = {f2(x['A'])} {ci(x['A_ci'])} ({x['templates']} templates)")
        V = Dd.per_draw(CON[PRIM], NS).mean(1)
        for cl, sel in (("DONEsys items", ~Dd.rdy), ("READYsys items", Dd.rdy)):   # one cell per template: the plain item mean
            J["S6"][f"{lab} {cl}"] = float(V[sel].mean()); md(f"- {lab}, {cl}: mean I = {f2(float(V[sel].mean()))} (n {int(sel.sum())} items; descriptive)")
    md(f"\n## S7 — I_C here vs Amendment 6\n\nI_C = {f2(p1['A'])} on 120 fresh items vs A6's +10.41 on the A5 items (different items; descriptive).")
    J["S7"] = {"I_C": p1["A"], "A6_I": A6_I}
    return OUT, J

def synth(items, IC, IN, lex=2.0, noise=0.3, seed=1):
    """a7_q0-shaped rows: per probe type, Y = base + word copying + the planted interaction (no-space cols = locked)."""
    g = np.random.default_rng(seed); rows = []
    for i in items:
        b = {0: g.normal(-2, 1), 1: g.normal(3, 1)}
        put = lambda y: (y, 0.0) if C[i]["target_sys"] == "DONE" else (0.0, y)
        for pr in (0, 1):
            rows.append((i, -1, 4, 0, *put(b[pr]), 0, *put(b[pr]), pr))
        for d in range(8):
            for a, arm in enumerate(ARMS):
                for n in NS:
                    for pr, I_ in ((0, IC), (1, IN)):
                        y = b[pr] + lex * (1 if arm in ("defer", "agree") else -1) / 2 + (I_ / 4 if arm in ("defer", "defy") else -I_ / 4) + g.normal(0, noise)
                        rows.append((i, d, a, n, *put(y), 10 * n, *put(y), pr))
    return np.array(rows, float)

if sys.argv[1:] == ["--selftest"]:
    fails = []
    def check(name, ok):
        print(("PASS " if ok else "FAIL ") + name); (None if ok else fails.append(name))
    rng = np.random.default_rng(7101799)
    items = sorted(int(i) for t in range(30) for cb in ("DONEsys", "READYsys")
                   for i in rng.choice([j for j in range(720) if C[j]["template_idx"] == t and C[j]["counterbalance"] == cb], 2, replace=False))
    _, J = analyze(synth(items, +1.0, -1.0))
    check(f"planted I_C +1, I_N −1 (word copying +2) → P1 supported ({J['P1']['A']:+.3f}), P2 supported ({J['P2']['A']:+.3f})",
          abs(J["P1"]["A"] - 1) < 0.05 and abs(J["P2"]["A"] + 1) < 0.05 and J["P1"]["verdict"] == J["P2"]["verdict"] == "supported")
    check(f"word copying +2 recovered on N ({J['S2_S4']['assistant word (system − competing)']['A']:+.3f})", abs(J["S2_S4"]["assistant word (system − competing)"]["A"] - 2) < 0.05)
    _, J = analyze(synth(items, +1.0, +1.0))
    check(f"planted I_N +1 → P2 contradicted ({J['P2']['A']:+.3f})", J["P2"]["verdict"] == "contradicted")
    _, J = analyze(synth(items, 0.0, 0.0))
    check(f"no interaction → P1 and P2 not supported ({J['P1']['A']:+.3f}, {J['P2']['A']:+.3f})", J["P1"]["verdict"] == J["P2"]["verdict"] == "not supported")
    check(f"P1 / P2 CIs at 97.5% ({J['P1']['level']}, {J['P2']['level']})", J["P1"]["level"] == J["P2"]["level"] == 97.5)
    q = synth(items, 1.0, -1.0); q = q[~((q[:, 0] == items[0]) & (q[:, 2] == 1) & (q[:, 3] == 4) & (q[:, 9] == 1))]
    try: analyze(q); check("a missing N cell is refused", False)
    except SystemExit: check("a missing N cell is refused", True)
    q = synth(items, 1.0, -1.0); q[:, 9] = np.where(q[:, 9] == 0, 1, 0)
    _, J = analyze(q); check(f"swapping the probe codes swaps P1 / P2 ({J['P1']['A']:+.3f}, {J['P2']['A']:+.3f})", J["P1"]["A"] < 0 < J["P2"]["A"])
    print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails)); sys.exit(1 if fails else 0)

if __name__ == "__main__":
    args = sys.argv[1:]; F = Path(args[0]); TAG = args[1] if len(args) > 1 else "REAL_"
    q = np.load(F / f"{TAG}a7_q0.npz")["rows"]
    OUT, J = analyze(q)
    G = json.loads((F / f"{TAG}a7_gap_report.json").read_text(encoding="utf-8")); RC = json.loads((F / f"{TAG}a7_rowcheck.json").read_text(encoding="utf-8"))
    head = ["# HUNT-DRIFT-01 A7 — Amendment 7 (a66ef98b…) — follow the system, or go against the user? — EXPLORATORY", "",
            f"Row checks: {RC['probe_draws']} probe × draw, arms token-identical but for the swaps, N = C but the requested word; longest row "
            f"{RC['row_tokens_max']} tokens. Single-pass + crop vs fresh, C and N (reported): n {G['n']}, max {G['max']:.3f}, median {G['median']:.3f} nats."]
    (F / f"{TAG}A7_ANALYSIS.md").write_text("\n".join(head + [""] + OUT) + "\n", encoding="utf-8")
    (F / f"{TAG}A7_analysis.json").write_text(json.dumps(J, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)), encoding="utf-8")
    print("\n".join(head + [""] + OUT))
