"""Post-hoc (not pre-registered): split drift/prose/filler contrasts into an authority part (aligned to the system
target, cell-balanced mean of ΔY_signed) and a word-prior part (toward READY = (cell READYsys − cell DONEsys)/2).
Template × seed bootstrap, 2,000, seed 7101001, same resampling as b6_analysis.boot_stats. Read-only."""
import json, sys
from pathlib import Path
import numpy as np
H = Path(r"D:\Resolve Research\Connection_Program\trackA\hunts\drift01"); sys.path.insert(0, str(H))
import drift01_core as D, phaseb_core as B
sys.stdout.reconfigure(encoding="utf-8")
C = [json.loads(l) for l in open(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl", encoding="utf-8")]
F = H / "out/phaseBd_20261104T034908Z"; FB = H / "out/phaseBb_20261102T230350Z"
q = np.load(F / "REAL_b6_q0.npz")["rows"]
cells = [tuple(c) for c in json.loads((FB / "REAL_b5_transcripts_manifest.json").read_text(encoding="utf-8"))["cells"]]
DR, FI, NO, PR = (B.B6_CONDS.index(x) for x in ("drift", "filler", "none", "prose"))
tids = sorted({int(x) for x in q[:, 0]}); items = sorted({int(x) for x in q[:, 1]}); KS = sorted({int(x) for x in q[:, 3]})
ti = {t: n for n, t in enumerate(tids)}; ii = {x: n for n, x in enumerate(items)}; ki = {k: n for n, k in enumerate(KS)}
T, I, K = len(tids), len(items), len(KS)
Y = np.full((T, I, 4, K), np.nan)
Yr = D.y_signed(q[:, 4], q[:, 5], [C[int(i)]["target_sys"] for i in q[:, 1]])
for r, y in zip(q, Yr): Y[ti[int(r[0])], ii[int(r[1])], int(r[2]), ki[int(r[3])]] = y
assert np.isfinite(Y).all(), "missing rows"
# sanity: Y_signed = lp(sys) − lp(comp) → READYsys items have Y = lpR − lpD
cb = np.array([C[i]["counterbalance"] for i in items]); rdy = cb == "READYsys"
assert all((C[i]["target_sys"] == "READY") == (C[i]["counterbalance"] == "READYsys") for i in items)
tm = np.array([C[i]["template_idx"] for i in items]); tu = sorted(set(tm)); tix = np.array([tu.index(x) for x in tm])
print(f"items {I}: DONEsys {(~rdy).sum()} · READYsys {rdy.sum()} · templates {len(tu)}; "
      f"templates holding both cells: {sum(1 for t in tu if len(set(cb[tm == t])) == 2)}")
seeds = sorted({cells[t][3] for t in tids}); S = len(seeds); sx = np.array([seeds.index(cells[t][3]) for t in tids])
Sm = np.zeros((T, S)); Sm[np.arange(T), sx] = 1                     # tid → seed indicator
CON = {"drift − filler": (DR, FI), "prose − filler": (PR, FI), "drift − prose": (DR, PR)}
KP = [ki[k] for k in (4, 8, 16, 32)]
def sums(x):                                                       # x[T, I] → per (item, seed) sums
    return x.T @ Sm
targets = {}
for nm, (a, b) in CON.items():
    d = Y[:, :, a, :] - Y[:, :, b, :]                              # T, I, K
    targets[(nm, "k∈{4..32}")] = sums(d[:, :, KP].mean(axis=2))
    for k in KS:
        if k > 0: targets[(nm, f"k={k}")] = sums(d[:, :, ki[k]])
cnt = np.ones((T, I)).T @ Sm                                         # I, S
def decomp(Ssum, ws, wi):
    pi = (Ssum @ ws) / (cnt @ ws)
    m_d = np.sum((pi * wi)[~rdy]) / np.sum(wi[~rdy]); m_r = np.sum((pi * wi)[rdy]) / np.sum(wi[rdy])
    return m_d, m_r, (m_d + m_r) / 2, (m_r - m_d) / 2
rng = np.random.default_rng(D.check_seed(D.SEED_BOOT)); BOOT = D.BOOT
W = [(np.bincount(rng.integers(0, S, S), minlength=S).astype(float),
      np.bincount(rng.integers(0, len(tu), len(tu)), minlength=len(tu))[tix].astype(float)) for _ in range(BOOT)]
f2 = lambda x: f"{x:+.2f}"
print(f"\nbootstrap {BOOT} templates × seeds, seed {D.SEED_BOOT}; authority = (DONEsys + READYsys)/2 (− = drift erodes the system "
      f"target); word = (READYsys − DONEsys)/2 (+ = pull toward READY)\n")
print("| contrast | k | DONEsys | READYsys | authority | 95% CI | word→READY | 95% CI |\n|---|---|---|---|---|---|---|---|")
OUT = {}
for (nm, kl), Ssum in targets.items():
    pt = decomp(Ssum, np.ones(S), np.ones(I))
    bs = np.array([decomp(Ssum, ws, wi) for ws, wi in W])
    c = np.nanpercentile(bs, [2.5, 97.5], axis=0)
    OUT[f"{nm} {kl}"] = {"done": pt[0], "ready": pt[1], "auth": pt[2], "auth_ci": c[:, 2].tolist(), "word": pt[3], "word_ci": c[:, 3].tolist()}
    print(f"| {nm} | {kl} | {f2(pt[0])} | {f2(pt[1])} | {f2(pt[2])} | [{f2(c[0,2])}, {f2(c[1,2])}] | {f2(pt[3])} | [{f2(c[0,3])}, {f2(c[1,3])}] |")
(F / "POSTHOC_cb_decomp.json").write_text(json.dumps(OUT, indent=1), encoding="utf-8")
# within-template: only templates holding both cells; per template t, auth_t = (R̄_t + D̄_t)/2, word_t = (R̄_t − D̄_t)/2,
# averaged over templates (template bootstrap weights) — cell is no longer confounded with template
both = [n for n, t in enumerate(tu) if len(set(cb[tm == t])) == 2]; inb = np.isin(tix, both)
print(f"\nWITHIN-TEMPLATE: {len(both)} templates, {inb.sum()} items (DONEsys {(inb & ~rdy).sum()} · READYsys {(inb & rdy).sum()})\n")
def paired(Ssum, ws, wt):
    pi = (Ssum @ ws) / (cnt @ ws); a, w, n = 0.0, 0.0, 0.0
    for t in both:
        if wt[t] == 0: continue
        d = pi[(tix == t) & ~rdy].mean(); r = pi[(tix == t) & rdy].mean()
        a += wt[t] * (d + r) / 2; w += wt[t] * (r - d) / 2; n += wt[t]
    return (a / n, w / n) if n else (np.nan, np.nan)
WT = [(ws, np.bincount(np.random.default_rng([D.SEED_BOOT, b]).integers(0, len(tu), len(tu)), minlength=len(tu)))
      for b, (ws, _) in enumerate(W)]
print("| contrast | k | authority | 95% CI | word→READY | 95% CI |\n|---|---|---|---|---|---|")
for (nm, kl), Ssum in targets.items():
    pt = paired(Ssum, np.ones(S), np.ones(len(tu)))
    bs = np.array([paired(Ssum, ws, wt) for ws, wt in WT]); c = np.nanpercentile(bs, [2.5, 97.5], axis=0)
    OUT[f"WT {nm} {kl}"] = {"auth": pt[0], "auth_ci": c[:, 0].tolist(), "word": pt[1], "word_ci": c[:, 1].tolist()}
    print(f"| {nm} | {kl} | {f2(pt[0])} | [{f2(c[0,0])}, {f2(c[1,0])}] | {f2(pt[1])} | [{f2(c[0,1])}, {f2(c[1,1])}] |")
(F / "POSTHOC_cb_decomp.json").write_text(json.dumps(OUT, indent=1), encoding="utf-8")
