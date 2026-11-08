"""HUNT-DRIFT-01 B-b analysis (EXPLORATORY; PLAN_PHASE_B.md B5, locked 1a660770…). Local, numpy only.
  python b5_analysis.py --selftest
  python b5_analysis.py <pulled B-b folder> [TAG]          (TAG default REAL_; DRY: FAKE_)
Writes <folder>/<TAG>B5_ANALYSIS.md + <TAG>B5_analysis.json.
  PRIMARY (one test): pooled Δ = mean(Y_drift − Y_filler) over every main (transcript, item, k) with k ∈ {4, 8, 16, 32};
  two-way bootstrap (items × generation seeds, 2,000, SEED_BOOT 7101001); verdict by drift01_core.band_verdict
  (δ = 0.234): content-driven / distance-driven / drift protects / indeterminate.
  Secondary (no verdict carries the headline): Δ per mode, per k, per mode × k.
  §3 with-instruction: A(k) = (Y_drift(k) − Y_none(k)) / (Y_drift(0) − Y_none(0)), ratio of means, for the 12
  with-instruction transcripts vs their matched main transcripts (same mode M1, persona, T 1.0, seed, item), paired;
  reported per k, descriptive (2 items × 2 seeds: no CI). Plus each with-instruction transcript's bare-target rate.
  The single-pass + crop vs fresh gap (b5_gap_report) is reported split by condition."""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D
import phaseb_core as B
sys.stdout.reconfigure(encoding="utf-8")
C = [json.loads(l) for l in open(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl", encoding="utf-8")]
ID = {c["id"]: n for n, c in enumerate(C)}
K_PRIMARY = (4, 8, 16, 32)
DR, FI, NO = (B.B5_CONDS.index(x) for x in ("drift", "filler", "none"))
f2 = lambda x: "n/a" if x is None or not np.isfinite(x) else f"{x:+.2f}"
ci = lambda c: f"[{f2(c[0])}, {f2(c[1])}]"

def analyze(q0, cells, wi_cells, gap, wi_turns=None):
    """q0 rows (tid, item, cond, k, lpD, lpR, dist); cells = main (mode, persona, T, seed) by tid; wi_cells =
    (mode, persona, T, seed, item id) by with-instruction index. Returns (markdown lines, json dict)."""
    Yr = D.y_signed(q0[:, 4], q0[:, 5], [C[int(i)]["target_sys"] for i in q0[:, 1]])
    Y = {(int(r[0]), int(r[1]), int(r[2]), int(r[3])): y for r, y in zip(q0, Yr)}
    DIST = {(int(r[0]), int(r[1]), int(r[2]), int(r[3])): r[6] for r in q0}
    main = sorted({int(r[0]) for r in q0 if r[0] < B.WI_TID0}); KS = sorted({int(r[3]) for r in q0})
    seed_of = lambda t: cells[t][3] if t < B.WI_TID0 else wi_cells[t - B.WI_TID0][3]
    OUT, J = [], {}
    md = lambda *a: OUT.append(" ".join(str(x) for x in a))
    def delta(sel_t, ks):
        d, It, Sd = [], [], []
        for (t, i, c, k), y in Y.items():
            if c == DR and t in sel_t and k in ks and (t, i, FI, k) in Y:
                d.append(y - Y[(t, i, FI, k)]); It.append(i); Sd.append(seed_of(t))
        if not d: return None, (None, None), 0, None
        d = np.array(d); pt = float(d.mean()); c = D.boot2(d, None, np.array(It), np.array(Sd))
        return pt, c, len(d), D.band_verdict(pt, c)
    md(f"# HUNT-DRIFT-01 B-b — B5 pooled drift vs filler + §3 with-instruction — EXPLORATORY")
    md(f"\nMain transcripts {len(main)} · with-instruction {len(wi_cells)} · items {len({int(r[1]) for r in q0 if r[0] < B.WI_TID0})} · "
       f"k ∈ {KS} · δ = {D.BAND} Y_signed · two-way bootstrap {D.BOOT} (items × seeds), seed {D.SEED_BOOT}.")
    mism = sum(1 for (t, i, c, k), v in DIST.items() if c == DR and (t, i, FI, k) in DIST and DIST[(t, i, FI, k)] != v)
    md(f"\nDrift / filler token distance mismatches: {mism} (must be 0).")
    J["distance_mismatch"] = mism
    # ---------------------------------------------------------------- primary
    pt, c, n, v = delta(set(main), K_PRIMARY)
    J["primary"] = {"delta": pt, "ci": c, "n": n, "verdict": v, "k": list(K_PRIMARY)}
    md(f"\n## PRIMARY — pooled Δ = mean(Y_drift − Y_filler), k ∈ {{4, 8, 16, 32}}, all main transcripts\n\n"
       f"**Δ = {f2(pt)} {ci(c)} (n = {n}) → {v}**\n\n(− = drift pulls the readout further from the system target than "
       f"token-matched filler, i.e. content-driven decay; + = drift protects.)")
    # ---------------------------------------------------------------- secondary
    md("\n## Secondary — Δ per mode × k (band label shown; no verdict carries the headline)\n\n| mode | " +
       " | ".join(f"k={k}" for k in KS if k > 0) + " | pooled k ∈ {4..32} |\n|" + "---|" * (len([k for k in KS if k > 0]) + 2))
    J["secondary"] = {}
    for m in ("all",) + B.B5_MODES:
        sel = set(main) if m == "all" else {t for t in main if cells[t][0] == m}; row = []
        for k in [k for k in KS if k > 0]:
            p_, c_, n_, v_ = delta(sel, (k,)); J["secondary"][f"{m}|k{k}"] = {"delta": p_, "ci": c_, "n": n_, "label": v_}
            row.append(f"{f2(p_)} {ci(c_)} {v_}" if p_ is not None else "—")
        p_, c_, n_, v_ = delta(sel, K_PRIMARY); J["secondary"][f"{m}|pooled"] = {"delta": p_, "ci": c_, "n": n_, "label": v_}
        md(f"| {m} | " + " | ".join(row) + f" | {f2(p_)} {ci(c_)} {v_} |")
    # ---------------------------------------------------------------- §3 with-instruction vs matched main
    md("\n## §3 — A(k) with-instruction − A(k) matched main (same M1, persona, T 1.0, seed, item); ratio of means, paired, descriptive")
    pairs = []
    for w, (m, p, T, s, it) in enumerate(wi_cells):
        mt = [t for t in main if tuple(cells[t]) == (m, p, T, s)]
        if len(mt) != 1: raise SystemExit(f"with-instruction {w}: {len(mt)} matched main transcripts (need exactly 1)")
        pairs.append((B.WI_TID0 + w, mt[0], ID[it]))
    J["s3"] = {"pairs": [[a, b, C[i]["id"]] for a, b, i in pairs], "by_k": {}}
    md("\n| k | A with-instruction | A matched main | difference | pairs |\n|---|---|---|---|---|")
    def A(t_list, i_list, k):
        num = [Y[(t, i, DR, k)] - Y[(t, i, NO, k)] for t, i in zip(t_list, i_list) if (t, i, DR, k) in Y]
        den = [Y[(t, i, DR, 0)] - Y[(t, i, NO, 0)] for t, i in zip(t_list, i_list) if (t, i, DR, k) in Y]
        return (float(np.sum(num) / np.sum(den)) if len(num) and np.sum(den) else float("nan")), len(num)
    for k in KS:
        keep = [(a, b, i) for a, b, i in pairs if (a, i, DR, k) in Y and (b, i, DR, k) in Y]   # both reach k
        aw, n = A([a for a, _, _ in keep], [i for *_, i in keep], k); am, _ = A([b for _, b, _ in keep], [i for *_, i in keep], k)
        J["s3"]["by_k"][k] = {"A_with": aw, "A_main": am, "diff": aw - am, "pairs": n}
        md(f"| {k} | {f2(aw)} | {f2(am)} | {f2(aw - am)} | {n} |")
    if wi_turns is not None:
        md("\nBare-target rate of each with-instruction transcript (assistant turns that are just the system target word):\n\n"
           "| with-instruction | item (target) | persona | seed | bare-target turns |\n|---|---|---|---|---|")
        J["s3"]["bare"] = {}
        for w, (m, p, T, s, it) in enumerate(wi_cells):
            tgt = C[ID[it]]["target_sys"]; tt = wi_turns.get(B.WI_TID0 + w, [])
            r = float(np.mean([x.strip().strip(".").upper() == tgt for x in tt])) if tt else float("nan")
            J["s3"]["bare"][w] = r; md(f"| {w} | {it} ({tgt}) | {p} | {s} | {r:.0%} |")
    # ---------------------------------------------------------------- gap by condition
    md(f"\n## Single-pass + crop vs fresh pass (reported; A3.3) — n = {gap['n']}, max {gap['max']:.3f}, median {gap['median']:.3f} nats\n\n"
       "| condition | n | median | max |\n|---|---|---|---|")
    J["gap"] = {}
    for cond in B.B5_CONDS:
        g = [r["gap"] for r in gap["rows"] if r["cond"] == cond]
        J["gap"][cond] = {"n": len(g), "median": float(np.median(g)) if g else None, "max": float(max(g)) if g else None}
        md(f"| {cond} | {len(g)} | {np.median(g):.3f} | {max(g):.3f} |" if g else f"| {cond} | 0 | — | — |")
    md("\nDrift and filler are token-matched at every k, so both are computed in identical kernel shapes; the gap is a "
       "per-unit numeric error, not a bias by condition, unless the rows above differ by condition.")
    return OUT, J

def load(F, TAG):
    q0 = np.load(F / f"{TAG}b5_q0.npz")["rows"]; man = json.loads((F / f"{TAG}b5_transcripts_manifest.json").read_text(encoding="utf-8"))
    gap = json.loads((F / f"{TAG}b5_gap_report.json").read_text(encoding="utf-8"))
    tr = [json.loads(l) for l in open(F / f"{TAG}b5_transcripts.jsonl", encoding="utf-8")]
    wt = {t["tid"]: [x["assistant"] for x in t["turns"]] for t in tr if "with_instruction" in t}
    return q0, [tuple(c) for c in man["cells"]], [tuple(w) for w in man["with_instruction"]], gap, wt

if sys.argv[1:] == ["--selftest"]:
    fails = []
    def check(n, ok): print(("PASS " if ok else "FAIL ") + n); fails.append(n) if not ok else None
    PANEL = [p["item"] for p in json.loads((HERE / "panel.json").read_text(encoding="utf-8"))["panel"]]
    CELLS = [(m, p, t, s) for m in B.B5_MODES for p in ("P-none", "P-neutral", "P-curious") for t in (0.7, 1.0) for s in B.B5_SEEDS]
    WI = [("M1", p, 1.0, s, C[it]["id"]) for p in ("P-none", "P-neutral", "P-curious") for s in B.B5_SEEDS[:2] for it in (PANEL[0], PANEL[4])]
    G0 = {"n": 3, "max": 0.3, "median": 0.1, "rows": [{"cond": "drift", "k": 4, "gap": 0.1}, {"cond": "filler", "k": 4, "gap": 0.3}, {"cond": "none", "k": 0, "gap": 0.05}]}
    def synth(dfn, Aof=lambda t, k: 0.5, noise=0.05, gs=0):
        """Y_none = 0; Y_drift(k) = 4·A(t, k) (so Y_drift(0) − Y_none(0) = 4 when A(t, 0) = 1); Y_filler = Y_drift − dfn(t, k)."""
        g = np.random.default_rng(gs); R = []
        tids = list(range(len(CELLS))) + [B.WI_TID0 + w for w in range(len(WI))]
        for t in tids:
            its = PANEL if t < B.WI_TID0 else [ID[WI[t - B.WI_TID0][4]]]
            for i in its:
                for k in D.K_Q0:
                    yd = 4 * (1.0 if k == 0 else Aof(t, k)) + noise * g.normal(); ys = {DR: yd, FI: yd - dfn(t, k) + noise * g.normal(), NO: 0.0}
                    for c, y in ys.items():
                        lpD = y if C[i]["target_sys"] == "DONE" else -y
                        R.append((t, i, c, k, lpD, 0.0, 100 + k))
        return np.array(R, float)
    for name, dfn, want in (("Δ −1 (filler ahead) → content-driven", lambda t, k: -1.0, "content-driven"),
                            ("Δ 0 → distance-driven", lambda t, k: 0.0, "distance-driven"),
                            ("Δ +1 → drift protects", lambda t, k: 1.0, "drift protects"),
                            ("Δ −3 ONLY at k ∈ {1, 2} → primary (k ≥ 4) distance-driven", lambda t, k: -3.0 if k in (1, 2) else 0.0, "distance-driven")):
        _, J = analyze(synth(dfn), CELLS, WI, G0)
        check(f"{name}: Δ {J['primary']['delta']:+.2f} → {J['primary']['verdict']}", J["primary"]["verdict"] == want)
    _, J = analyze(synth(lambda t, k: -1.0 if t < B.WI_TID0 and CELLS[t][0] == "M3" else 0.0), CELLS, WI, G0)
    check(f"mode split: M3 Δ −1 / M1 Δ 0 → M3 {J['secondary']['M3|pooled']['label']}, M1 {J['secondary']['M1|pooled']['label']}",
          J["secondary"]["M3|pooled"]["label"] == "content-driven" and J["secondary"]["M1|pooled"]["label"] == "distance-driven")
    # §3: matched main (M1, T 1.0) A = 0.5; every other main cell 0.1 (a wrong match shows); with-instruction 0.9
    Aof = lambda t, k: 0.9 if t >= B.WI_TID0 else (0.5 if CELLS[t][0] == "M1" and CELLS[t][2] == 1.0 else 0.1)
    _, J = analyze(synth(lambda t, k: 0.0, Aof, noise=0.0), CELLS, WI, G0)
    d = [J["s3"]["by_k"][k]["diff"] for k in D.K_Q0 if k > 0]
    check(f"§3: planted with 0.9 vs matched main 0.5 (others 0.1) → diff {d[0]:+.2f} at every k, 12 pairs",
          all(abs(x - 0.4) < 1e-9 for x in d) and all(J["s3"]["by_k"][k]["pairs"] == 12 for k in D.K_Q0))
    check("§3 pairing: same persona + seed, M1, T 1.0", all(CELLS[b][:4] == WI[a - B.WI_TID0][:4] for a, b, _ in J["s3"]["pairs"]))
    q = synth(lambda t, k: 0.0); q[(q[:, 2] == FI) & (q[:, 3] == 8), 6] += 1
    _, J = analyze(q, CELLS, WI, G0); check(f"distance mismatch planted → counted ({J['distance_mismatch']})", J["distance_mismatch"] > 0)
    _, J = analyze(synth(lambda t, k: 0.0), CELLS, WI, G0); check("gap split by condition", J["gap"]["filler"]["max"] == 0.3 and J["gap"]["drift"]["n"] == 1)
    try: analyze(synth(lambda t, k: 0.0), CELLS, WI[:1] + [("M1", "P-none", 1.0, 7109999, WI[0][4])], G0); check("unmatched with-instruction → refused", False)
    except SystemExit: check("unmatched with-instruction → refused", True)
    print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails)); sys.exit(1 if fails else 0)

F = Path(sys.argv[1]); TAG = sys.argv[2] if len(sys.argv) > 2 else "REAL_"
OUT, J = analyze(*load(F, TAG))
(F / f"{TAG}B5_ANALYSIS.md").write_text("\n".join(OUT) + "\n", encoding="utf-8")
(F / f"{TAG}B5_analysis.json").write_text(json.dumps(J, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)), encoding="utf-8")
print(f"wrote {F / (TAG + 'B5_ANALYSIS.md')} ({len(OUT)} lines)")
