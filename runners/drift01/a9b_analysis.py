"""HUNT-DRIFT-01 A9b analysis (EXPLORATORY; Amendment 9b 87eae7d9…, locked). Local, numpy only.
  python a9b_analysis.py --selftest
  python a9b_analysis.py <pulled A9b folder> [TAG]
Reads <TAG>a9b_q0.npz, a9b_h.npy, a9b_e0.npy (PHASEB=k) and a9b_enc.npy (a9b_encode.py); writes <TAG>A9B_ANALYSIS.md +
<TAG>A9B_analysis.json.
Representations: Llama layer L ∈ a9b_core.LAYERS · Control 1 (pooled layer-0 embeddings) · Control 2 (Qwen3-Embedding-8B;
A10 rows only). Labels: flip = defer, defy · copy = obey, agree (A6 arms).
A9b.2, fixed: direction d = mean(flip) − mean(copy) over the NATIVE probe-C rows (all n) of the fit templates, unit norm;
s = h · d. 3 folds of 10 templates (seed 7101901); every row of a held-out template (any rendering, probe N, anchors) is
scored with the fold's direction. Llama layer per fold: the highest inner leave-one-fold-out AUROC (mean of the two inner
splits) on native rows; ties → the deeper layer. AUROC CI: bootstrap over templates (the template draws of a6_analysis'
resamples, 2,000, SEED_BOOT 7101001); shuffled null: flip / copy permuted within template × item over the native rows,
the whole pipeline incl. layer choice, 200 permutations (seed 7101902), its 97.5th percentile. G = template-balanced
aligned part (a6_analysis.aw) of [mean s(flip) − mean s(copy)] per item × draw, averaged over n, divided by the pooled
within-class SD of s on held-out native rows of the same representation (point value, held fixed across resamples);
two-way bootstrap templates × draws. DD = (G_L,native − G_L,headers) − (G_enc,native − G_enc,headers), paired per
item × draw × n. A8: d fit on ALL native rows at the layer chosen most often across folds (ties → deeper); R_s on
Δs = s(drift) − s(filler) via a8_analysis.Data8 (templates × seeds).
PRIMARY (98.33%, Bonferroni over three): P1 native AUROC > 0.5 (lower bound > 0.5 AND point > the null's 97.5th
percentile AND point > Control 1's upper bound; Llama − Control 2 paired difference reported beside it) · P2 DD > 0 ·
P3 R_s < 0. Secondary S1–S8 at 95%."""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
_argv, sys.argv = sys.argv, sys.argv[:1]          # a6_analysis / a8_analysis run their own self-tests on import when argv says so
import a6_analysis as A
import a8_analysis as A8
sys.argv = _argv
import drift01_core as D
import a9b_core as A9B
sys.stdout.reconfigure(encoding="utf-8")
C, f2, ci = A.C, A.f2, A.ci
ARMS, NS, LAYERS = A.ARMS, A.NS, A9B.LAYERS
LP = 100 - 5 / 3                                  # 98.33%
FLIP = np.array([0, 1, 0, 1], bool)               # obey, defer, agree, defy → flip = defer, defy
ASKS = np.array([0, 0, 1, 1], bool)               # demo user asks for the SYSTEM word (A6.ASK_SYS)
SAYS = np.array([0, 1, 1, 0], bool)               # demo assistant says the SYSTEM word (A6.SAY_SYS)
W_FC = (-0.5, 0.5, -0.5, 0.5)                     # mean(flip) − mean(copy) over (obey, defer, agree, defy)
RENDERS = ("native", "headers", "quoted", "stated")
NPERM, PERM_SEED = 200, 7101902
f3 = lambda x: "n/a" if x is None or not np.isfinite(x) else f"{x:.3f}"
ci3 = lambda c: f"[{f3(c[0])}, {f3(c[1])}]"

def folds(tu):
    D.check_seed(A9B.FOLD_SEED); p = np.random.default_rng(A9B.FOLD_SEED).permutation(len(tu))
    return [set(np.array(tu)[p[k * 10:(k + 1) * 10]].tolist()) for k in range(3)]

def auc_cols(S, y):
    """AUROC per column of S (rows × cols), y bool (positive = flip); average ranks (ties → ½)."""
    S = np.atleast_2d(S.T).T; o = np.argsort(S, axis=0, kind="stable"); R = np.empty_like(o, dtype=float)
    np.put_along_axis(R, o, np.arange(1, len(S) + 1, dtype=float)[:, None].repeat(S.shape[1], 1), axis=0)
    for j in range(S.shape[1]):                   # tie correction (rare for continuous scores)
        s = S[:, j]; u, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
        if (cnt > 1).any(): R[:, j] = (np.cumsum(cnt) - (cnt - 1) / 2)[inv]
    npos, nneg = y.sum(), (~y).sum()
    return (R[y].sum(0) - npos * (npos + 1) / 2) / (npos * nneg)

def auc_boot(s, y, t, WT, tix):
    """Template-weighted AUROC for each bootstrap column of WT (templates × B); t = row template ids → tix map."""
    o = np.argsort(s, kind="stable"); yp, tt = y[o], np.array([tix[x] for x in t[o]]); out = []
    for b0 in range(0, WT.shape[1], 250):
        w = WT[tt, b0:b0 + 250]; wn = w * (~yp)[:, None]; cn = np.cumsum(wn, 0) - wn
        out.append((w * yp[:, None] * cn).sum(0) / ((w * yp[:, None]).sum(0) * wn.sum(0)))
    return np.concatenate(out)

class SD:
    """a6_analysis-compatible container: Y[item, draw, arm, n] = s / scale for one rendering (or a difference of them)."""
    def __init__(self, items, draws, Y):
        self.items, self.draws, self.Y = items, draws, Y
        self.rdy = np.array([C[i]["counterbalance"] == "READYsys" for i in items])
        tm = [C[i]["template_idx"] for i in items]; self.tu = sorted(set(tm)); self.tix = np.array([self.tu.index(x) for x in tm])
        self.pos = np.array([C[i]["cell"].split("|")[1] for i in items])
    def per_draw(self, w, ns, minus_anchor=False):
        kk = [NS.index(n) for n in ns]; return np.tensordot(self.Y[:, :, :, kk].mean(axis=3), np.asarray(w, float), axes=([2], [0]))

class Run:
    """All rows of one A9b run, with loaders per representation."""
    def __init__(self, Q, blocks, H, E0, ENC, meta):
        self.Q, self.H, self.E0, self.ENC, self.meta = Q, H, E0, ENC, meta
        self.n10, self.n7, self.n8 = (int(x) for x in blocks)
        q = Q; self.src = q[:, 0].astype(int); self.item = q[:, 1].astype(int); self.draw = q[:, 2].astype(int); self.arm = q[:, 3].astype(int)
        self.n = q[:, 4].astype(int); self.render = q[:, 5].astype(int)
        self.tmpl = np.array([C[i]["template_idx"] for i in self.item])
        self.body = (self.src < 2) & (self.arm < 4)
        self.nat = np.where((self.src == 0) & (self.render == 0) & self.body)[0]     # fit rows
        self.items = sorted({int(x) for x in self.item[self.nat]}); self.draws = sorted({int(x) for x in self.draw[self.nat]})
        self.tu = sorted({C[i]["template_idx"] for i in self.items}); self.F = folds(self.tu)
        self.fold = np.array([next((k for k, f in enumerate(self.F) if t in f), -1) for t in self.tmpl])
        self.y = lambda idx, lab=FLIP: lab[np.clip(self.arm[idx], 0, 3)]
    def X(self, rep, idx):
        if rep == "C1": return np.asarray(self.E0[idx], np.float32)
        if rep == "C2":
            assert (idx < self.n10).all(); return np.asarray(self.ENC[idx], np.float32)
        return np.asarray(self.H[idx, LAYERS.index(rep)], np.float32)

def fit_dirs(Xn, Wt):
    """Unit directions (d × P) from fit-row features Xn and signed class weights Wt (rows × P)."""
    Dm = Xn.T @ Wt; return Dm / np.maximum(np.linalg.norm(Dm, axis=0, keepdims=True), 1e-30)

def class_w(y, keep):
    """Signed weights: +1/n_flip on flip rows in keep, −1/n_copy on copy rows (y: rows × P bool)."""
    k = keep[:, None]; pos, neg = y & k, ~y & k
    return pos / np.maximum(pos.sum(0), 1) - neg / np.maximum(neg.sum(0), 1)

def layer_pass(R, rep, ylab_nat, extra_idx):
    """One representation: per outer fold the fit direction (labels ylab_nat: nat rows × P) → held-out scores of the
    native rows (nat × P) and of extra_idx rows (first label column only) + inner AUROC (3 folds × P)."""
    Xn = R.X(rep, R.nat); fn = R.fold[R.nat]; P = ylab_nat.shape[1]
    S_nat = np.full((len(R.nat), P), np.nan); inner = np.zeros((3, P)); dirs = []
    for f in range(3):
        fit = fn != f; inn = [g for g in range(3) if g != f]; a = []
        for g, h in ((inn[0], inn[1]), (inn[1], inn[0])):
            d = fit_dirs(Xn, class_w(ylab_nat, fn == h)); m = fn == g
            a.append(np.array([auc_cols((Xn[m] @ d[:, j])[:, None], ylab_nat[m, j])[0] for j in range(P)]))
        inner[f] = np.mean(a, 0)
        d = fit_dirs(Xn, class_w(ylab_nat, fit)); dirs.append(d[:, 0]); S_nat[fn == f] = Xn[fn == f] @ d
    S_ex = np.full(len(extra_idx), np.nan)
    if len(extra_idx):
        fe = R.fold[extra_idx]
        for f in range(3):
            m = fe == f
            if m.any(): S_ex[m] = R.X(rep, extra_idx[m]) @ dirs[f]
    return S_nat, S_ex, inner, dirs

def perm_labels(R):
    """NPERM within template × item permutations of the native rows' flip labels (nat × NPERM)."""
    rng = np.random.default_rng(PERM_SEED); y = R.y(R.nat); out = np.empty((len(R.nat), NPERM), bool)
    groups = {}
    for k, i in enumerate(R.item[R.nat]): groups.setdefault(int(i), []).append(k)
    for p in range(NPERM):
        z = y.copy()
        for g in groups.values(): g = np.array(g); z[g] = y[g][rng.permutation(len(g))]
        out[:, p] = z
    return out

def g_obj(R, s, rows_mask, scale):
    """SD object of s / scale over rows_mask (A10 body rows of one rendering, or probe N rows)."""
    ii = {x: k for k, x in enumerate(R.items)}; di = {x: k for k, x in enumerate(R.draws)}; ni = {n: j for j, n in enumerate(NS)}
    Y = np.full((len(R.items), len(R.draws), 4, len(NS)), np.nan)
    for k in np.where(rows_mask)[0]:
        Y[ii[R.item[k]], di[R.draw[k]], R.arm[k], ni[R.n[k]]] = s[k] / scale
    if np.isnan(Y).any(): raise SystemExit(f"{int(np.isnan(Y).sum())} item × draw × arm × n cells missing — not a complete A10 grid")
    return SD(R.items, R.draws, Y)

def pooled_sd(s, y):
    a, b = s[y], s[~y]; return float(np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2)))

def spearman_within(s, y, groups):
    """Pearson of within-group ranks, pooled (Spearman within arm × n)."""
    rs, ry = np.empty(len(s)), np.empty(len(s))
    for g in np.unique(groups):
        m = groups == g; rs[m] = np.argsort(np.argsort(s[m])); ry[m] = np.argsort(np.argsort(y[m]))
        rs[m] -= rs[m].mean(); ry[m] -= ry[m].mean()
    return float((rs * ry).sum() / np.sqrt((rs ** 2).sum() * (ry ** 2).sum()))

def analyze(R, extra=None):
    OUT, J = [], {}; md = OUT.append
    ALL = np.arange(len(R.Q)); ex_idx = ALL[(R.src < 2) & ~np.isin(ALL, R.nat)]          # every other A10 / A7-N row (renderings, N, anchors)
    ex10 = ex_idx[ex_idx < R.n10]
    yN = R.y(R.nat); PL = perm_labels(R); tix = {t: k for k, t in enumerate(R.tu)}
    LAB = {"flip": yN[:, None], "user word": R.y(R.nat, ASKS)[:, None], "assistant word": R.y(R.nat, SAYS)[:, None]}
    reps = list(LAYERS) + ["C1", "C2"]
    RES = {}
    for rep in reps:
        ex = ex10 if rep == "C2" else ex_idx
        Sn, Se, inner, dirs = layer_pass(R, rep, np.concatenate([yN[:, None], PL], 1), ex)
        s = np.full(len(R.Q), np.nan); s[R.nat] = Sn[:, 0]; s[ex] = Se
        main = {k: layer_pass(R, rep, v, np.array([], int))[0][:, 0] for k, v in LAB.items() if k != "flip"}
        RES[rep] = {"s": s, "null_S": Sn[:, 1:], "inner": inner, "main": main, "dirs": dirs}
        print(f"[A9B] {rep}: native held-out AUROC {auc_cols(Sn[:, :1], yN)[0]:.3f}", flush=True)
    # ---- layer choice per fold (inner rule, ties → deeper), for the real labels and for every permutation
    IN = np.stack([RES[l]["inner"] for l in LAYERS])            # layers × 3 folds × (1 + NPERM)
    choose = lambda v: len(LAYERS) - 1 - int(np.argmax(v[::-1]))  # highest; ties → deeper
    CH = np.array([[choose(IN[:, f, p]) for p in range(IN.shape[2])] for f in range(3)])   # 3 × (1 + NPERM)
    fn_nat, fo_all = R.fold[R.nat], R.fold
    sL = np.full(len(R.Q), np.nan)
    for f in range(3): m = fo_all == f; sL[m] = RES[LAYERS[CH[f, 0]]]["s"][m]
    J["chosen_layer_per_fold"] = [LAYERS[CH[f, 0]] for f in range(3)]
    nullA = []
    for p in range(1, IN.shape[2]):
        sp = np.empty(len(R.nat))
        for f in range(3): m = fn_nat == f; sp[m] = RES[LAYERS[CH[f, p]]]["null_S"][m, p - 1]
        nullA.append(auc_cols(sp[:, None], PL[:, p - 1])[0])
    nullA = np.array(nullA); q975 = float(np.percentile(nullA, 97.5))
    # ---- resamples (a6_analysis', two-way templates × draws) on a reference SD object
    REF = g_obj(R, np.zeros(len(R.Q)), (R.src == 0) & (R.render == 0) & R.body, 1.0); RS = A.resamples(REF); WT = RS[1]
    tN = R.tmpl[R.nat]
    def auc_full(s_nat, level):
        pt = auc_cols(s_nat[:, None], yN)[0]; b = auc_boot(s_nat, yN, tN, WT, tix); lo = (100 - level) / 2
        return pt, b, (float(np.nanpercentile(b, lo)), float(np.nanpercentile(b, 100 - lo)))
    aL, bL, cL = auc_full(sL[R.nat], LP); a1, b1, c1 = auc_full(RES["C1"]["s"][R.nat], LP); a2, b2, c2 = auc_full(RES["C2"]["s"][R.nat], LP)
    d12 = bL - b2; cD = (float(np.nanpercentile(d12, (100 - LP) / 2)), float(np.nanpercentile(d12, 100 - (100 - LP) / 2)))
    v1 = "supported" if (cL[0] > 0.5 and aL > q975 and aL > c1[1]) else "not supported"
    J["P1"] = {"auroc": aL, "ci": cL, "null_q975": q975, "null_median": float(np.median(nullA)), "C1": {"auroc": a1, "ci": c1},
               "C2": {"auroc": a2, "ci": c2}, "L_minus_C2": {"diff": aL - a2, "ci": cD}, "verdict": v1}
    md(f"Items {len(R.items)} from {len(R.tu)} templates · draws {len(R.draws)} · native probe-C fit rows {len(R.nat)} · folds (seed {A9B.FOLD_SEED}) "
       f"{[sorted(f) for f in R.F]} · layers {list(LAYERS)}; chosen per fold {J['chosen_layer_per_fold']} · bootstrap {D.BOOT} (seed {D.SEED_BOOT}) · null {NPERM} permutations.")
    md(f"\n## PRIMARY (98.33% CIs, Bonferroni over three)\n\n**P1 — held-out native AUROC, flip vs copy, predicted > 0.5: {f3(aL)} {ci3(cL)} → {v1}** "
       f"(shuffled null 97.5th pct {f3(q975)}, median {f3(J['P1']['null_median'])}; Control 1 {f3(a1)} {ci3(c1)}). "
       f"Pre-stated beside it: Control 2 (Qwen3-Embedding-8B) {f3(a2)} {ci3(c2)}; Llama − Control 2 {aL - a2:+.3f} {ci3(cD)}.")
    # ---- G and DD
    scale = {}
    for rep, s in (("L", sL), ("C1", RES["C1"]["s"]), ("C2", RES["C2"]["s"])): scale[rep] = pooled_sd(s[R.nat], yN)
    SR = {rep: s for rep, s in (("L", sL), ("C1", RES["C1"]["s"]), ("C2", RES["C2"]["s"]))}
    Gobj = {(rep, r): g_obj(R, SR[rep], (R.src == 0) & (R.render == k) & R.body, scale[rep]) for rep in SR for k, r in enumerate(RENDERS)}
    def est_obj(obj, level, ns=NS): return A.est(obj, RS, W_FC, ns, level)
    dd = SD(R.items, R.draws, (Gobj[("L", "native")].Y - Gobj[("L", "headers")].Y) - (Gobj[("C2", "native")].Y - Gobj[("C2", "headers")].Y))
    e2 = est_obj(dd, LP); J["P2"] = {**e2, "verdict": A.verdict(e2, +1)}
    md(f"\n**P2 — DD = (G_L,native − G_L,headers) − (G_enc,native − G_enc,headers), predicted +: {f2(e2['A'])} {ci(e2['A_ci'])} → {J['P2']['verdict']}** "
       f"({e2['templates']} templates; within-class SD scales: Llama {f3(scale['L'])}, Control 2 {f3(scale['C2'])}).")
    # ---- P3: A8 projection
    modal = max(range(len(LAYERS)), key=lambda k: (int((CH[:, 0] == k).sum()), k)); Lm = LAYERS[modal]
    Xn = R.X(Lm, R.nat); dA = fit_dirs(Xn, class_w(yN[:, None], np.ones(len(R.nat), bool)))[:, 0]
    i8 = np.where(R.src == 2)[0]; s8 = R.X(Lm, i8) @ dA; q = R.Q[i8]
    put = lambda i, v: (v, 0.0) if C[i]["target_sys"] == "DONE" else (0.0, v)
    rows8 = np.array([(q_[7], q_[8], q_[9], q_[1], *put(int(q_[1]), v), q_[12], *put(int(q_[1]), v)) for q_, v in zip(q, s8)], float)
    Dd = A8.Data8(rows8, R.meta["pair_seed"]); RS8 = A.resamples(Dd)
    e3 = A.est(Dd, RS8, A8.CON[A8.PRIM], None, LP); J["P3"] = {**e3, "layer": Lm, "verdict": A.verdict(e3, -1)}
    md(f"\n**P3 — A8 reply effect on the projection, R_s, predicted −: {f2(e3['A'])} {ci(e3['A_ci'])} → {J['P3']['verdict']}** "
       f"(layer {Lm}, the most chosen; {e3['templates']} templates; {len(Dd.draws)} seeds; s in raw projection units).")
    # ---- secondary (95%)
    md("\n## S1 — G per rendering (95%), share of native; per-rendering own-direction AUROC\n\n| rendering | G Llama | 95% CI | share | G Control 1 | G Control 2 | share C2 | own-direction AUROC (Llama) |\n|---|---|---|---|---|---|---|---|")
    J["S1"] = {}
    gn = {rep: est_obj(Gobj[(rep, "native")], 95.0) for rep in SR}
    for k, r in enumerate(RENDERS):
        g = {rep: est_obj(Gobj[(rep, r)], 95.0) for rep in SR}
        m = (R.src == 0) & (R.render == k) & R.body; idx = np.where(m)[0]
        own = np.nan
        if r != "native":                                       # cross-fit on this rendering's own rows at each fold's chosen layer
            so = np.empty(len(idx)); fo = R.fold[idx]; yo = R.y(idx)
            for f in range(3):
                Xo = R.X(LAYERS[CH[f, 0]], idx); d = fit_dirs(Xo[fo != f], class_w(yo[fo != f][:, None], np.ones((fo != f).sum(), bool)))[:, 0]
                so[fo == f] = Xo[fo == f] @ d
            own = auc_cols(so[:, None], yo)[0]
        else: own = aL
        J["S1"][r] = {"G": {rep: g[rep] for rep in g}, "own_auc": own}
        sh = lambda a, b: a / b if b else float("nan")
        md(f"| {r} | {f2(g['L']['A'])} | {ci(g['L']['A_ci'])} | {sh(g['L']['A'], gn['L']['A']):.2f} | {f2(g['C1']['A'])} | {f2(g['C2']['A'])} | "
           f"{sh(g['C2']['A'], gn['C2']['A']):.2f} | {f3(own)} |")
    dg = est_obj(SD(R.items, R.draws, Gobj[("L", "native")].Y - Gobj[("L", "headers")].Y), 95.0)
    ddq = est_obj(SD(R.items, R.draws, (Gobj[("L", "native")].Y - Gobj[("L", "quoted")].Y) - (Gobj[("C2", "native")].Y - Gobj[("C2", "quoted")].Y)), 95.0)
    J["S1"]["D_G_raw"], J["S1"]["DD_quoted"] = dg, ddq
    md(f"\nRaw D_G = G_L,native − G_L,headers {f2(dg['A'])} {ci(dg['A_ci'])} · quoted-log DD {f2(ddq['A'])} {ci(ddq['A_ci'])} · G_stated sign: "
       f"{'positive (word rule)' if J['S1']['stated']['G']['L']['A'] > 0 else 'negative (stance)'} ({f2(J['S1']['stated']['G']['L']['A'])}).")
    md("\n## S2 — layer profile (fixed layer, no choice)\n\n| representation | native AUROC | inner AUROC by fold | G native |\n|---|---|---|---|")
    J["S2"] = {}
    for rep in reps:
        sr = RES[rep]["s"]; a_ = auc_cols(sr[R.nat][:, None], yN)[0]; sc = pooled_sd(sr[R.nat], yN)
        g_ = A.est(g_obj(R, sr, (R.src == 0) & (R.render == 0) & R.body, sc), RS, W_FC, NS, 95.0)["A"]
        J["S2"][str(rep)] = {"auroc": a_, "inner": RES[rep]["inner"][:, 0].tolist(), "G": g_}
        md(f"| {rep if rep in ('C1', 'C2') else 'L' + str(rep)} | {f3(a_)} | {', '.join(f3(x) for x in RES[rep]['inner'][:, 0])} | {f2(g_)} |")
    md("\n## S3 — positive controls (held-out native AUROC of the single-word main effects) and probe N\n\n| representation | user word | assistant word |\n|---|---|---|")
    J["S3"] = {"main": {}}
    for rep in reps:
        u_ = auc_cols(RES[rep]["main"]["user word"][:, None], R.y(R.nat, ASKS))[0]; a_ = auc_cols(RES[rep]["main"]["assistant word"][:, None], R.y(R.nat, SAYS))[0]
        J["S3"]["main"][str(rep)] = {"user": u_, "assistant": a_}; md(f"| {rep if rep in ('C1', 'C2') else 'L' + str(rep)} | {f3(u_)} | {f3(a_)} |")
    mN = (R.src == 1) & R.body; iN = np.where(mN)[0]; aN = auc_cols(sL[iN][:, None], R.y(iN))[0]
    gN = est_obj(g_obj(R, sL, mN, scale["L"]), 95.0); J["S3"]["probe_N"] = {"auroc": aN, "G": gN}
    md(f"\nProbe N (native, directions fit on C): AUROC {f3(aN)}; G {f2(gN['A'])} {ci(gN['A_ci'])}.")
    md("\n## S4 — dose: G by n (Llama; Control 2), slope in log2 n\n\n| rendering | " + " | ".join(f"n = {n}" for n in NS) + " | slope | C2 slope |\n|---|" + "---|" * (len(NS) + 2))
    J["S4"] = {}; lx = np.log2(np.array(NS, float)); lx -= lx.mean()
    for r in RENDERS:
        v = [est_obj(Gobj[("L", r)], 95.0, (n,))["A"] for n in NS]; v2 = [est_obj(Gobj[("C2", r)], 95.0, (n,))["A"] for n in NS]
        sl, sl2 = float(lx @ np.array(v) / (lx @ lx)), float(lx @ np.array(v2) / (lx @ lx))
        J["S4"][r] = {"G_by_n": v, "slope": sl, "C2_G_by_n": v2, "C2_slope": sl2}
        md(f"| {r} | " + " | ".join(f2(x) for x in v) + f" | {f2(sl)} | {f2(sl2)} |")
    YC = D.y_signed(R.Q[:, 10], R.Q[:, 11], [C[i]["target_sys"] for i in R.item])
    J["S5"] = {}
    for lab, m in (("C", R.nat), ("N", iN)):
        J["S5"][lab] = spearman_within(sL[m], YC[m], R.arm[m] * 100 + R.n[m])
    md(f"\n## S5 — say–show: Spearman of s with the aligned readout Y within arm × n, pooled\n\nC {J['S5']['C']:+.3f} · N {J['S5']['N']:+.3f} (on N the stance and Y run opposite ways by A7).")
    md("\n## S6 — A8 cells on Δs (95%)\n\n| contrast / cell | A | 95% CI | W |\n|---|---|---|---|")
    J["S6"] = {}
    for name, w in list(A8.CON.items()) + [(f"cell {c}", [1.0 if b == k else 0.0 for b in range(4)]) for k, c in enumerate(A8.CELLS)]:
        x = A.est(Dd, RS8, w, None); J["S6"][name] = x; md(f"| {name} | {f2(x['A'])} | {ci(x['A_ci'])} | {f2(x['W'])} |")
    mf, mc = s8[q[:, 9] == 1].mean(), s8[q[:, 9] == 0].mean(); sn = Xn @ dA
    pos = lambda v: float((v - sn[~yN].mean()) / (sn[yN].mean() - sn[~yN].mean()))
    J["S6"]["filler_position"], J["S6"]["drift_position"] = pos(mf), pos(mc)
    md(f"\nPosition on the copy (0) → flip (1) axis of the native rows: A8 filler rows {pos(mf):+.2f}, drift rows {pos(mc):+.2f}.")
    ia = np.where((R.src == 0) & (R.arm == 4))[0]; iaN = np.where((R.src == 1) & (R.arm == 4))[0]
    posL = lambda v, ref: float((v - sL[ref][~R.y(ref)].mean()) / (sL[ref][R.y(ref)].mean() - sL[ref][~R.y(ref)].mean()))
    J["S7"] = {"anchor_C": posL(sL[ia].mean(), R.nat), "anchor_N": posL(sL[iaN].mean(), iN)}
    md(f"\n## S7 — anchors (n = 0) on the copy (0) → flip (1) axis\n\nC anchors {J['S7']['anchor_C']:+.2f} · N anchors {J['S7']['anchor_N']:+.2f}.")
    if extra:
        J["S8"] = extra; md(f"\n## S8 — gates\n\nRepro: {extra.get('repro')} · encoder determinism: {extra.get('enc')}")
    return OUT, J

# ---------------------------------------------------------------------------------------------------- self-test (synthetic)
def synth(a_flip=1.0, role=0.0, enc_flip=0.0, enc_role=0.0, tok=0.0, R_=0.0, best=2, d=24, seed=1):
    """A complete A9b-shaped run (A7's 120 probes, 8 draws, 2 pairs per seed × 8 seeds, the A8 subset) with planted signals:
    flip ± a_flip/2 along u in the Llama layers (layer `best` strongest), × (1 − role) on headers; Control 2 carries
    enc_flip with its own enc_role drop; Control 1 carries tok × the native signal; A8 drift rows move by the cell weights
    × R_ along u (filler 0)."""
    g = np.random.default_rng(seed); u = g.normal(0, 1, d); u /= np.linalg.norm(u)
    A7I = sorted(x["item"] for x in json.loads((HERE / "a7_items.json").read_text(encoding="utf-8"))["items"])
    A8I = [x["item"] for x in json.loads((HERE / "a8_items.json").read_text(encoding="utf-8"))["items"]]; A8S = A9B.a8_subset(C, A8I)
    rows = []
    for src, probe in ((0, 0), (1, 1)):
        for p in A7I:
            rows.append((src, p, -1, 4, 0, -1, probe, -9, -9, -9))
        for p in A7I:
            for dr in range(8):
                for a in range(4):
                    for r in (range(4) if src == 0 else (0,)):
                        for n in NS: rows.append((src, p, dr, a, n, r, probe, -9, -9, -9))
    NP = 16; seeds = np.array([7101201 + j // 2 for j in range(NP)])
    for i in A8S:
        for j in range(NP):
            for c in range(4):
                for cc in (0, 1): rows.append((2, i, -9, -9, 1, -9, 0, j, c, cc))
    K = np.array(rows, float); N = len(K)
    off = {i: g.normal(0, 1, d) for i in set(K[:, 1].astype(int))}
    base = np.array([off[int(i)] for i in K[:, 1]]) + g.normal(0, 1, (N, d))
    sign = np.where(np.isin(K[:, 3], (1, 3)), 1.0, np.where(np.isin(K[:, 3], (0, 2)), -1.0, 0.0)) / 2
    rf = np.select([K[:, 5] == 1], [1 - role], 1.0); ef = np.select([K[:, 5] == 1], [1 - enc_role], 1.0)
    sig = (sign * rf)[:, None] * u
    eff = np.zeros(4)
    w = np.asarray(A8.CON[A8.PRIM]); eff += R_ * w / (w @ w)
    a8m = K[:, 0] == 2; shift = np.where(a8m & (K[:, 9] == 0), eff[np.clip(K[:, 8].astype(int), 0, 3)], 0.0)[:, None] * u
    H = np.stack([base + (a_flip * (1.0 if l == best else 0.4)) * sig + shift + 0.1 * g.normal(0, 1, (N, d)) for l in range(len(LAYERS))], 1).astype(np.float16)
    E0 = (base + tok * a_flip * sig + 0.1 * g.normal(0, 1, (N, d))).astype(np.float16)
    n10 = int((K[:, 0] == 0).sum()); n7 = int((K[:, 0] == 1).sum())
    ENC = (base[:n10] + enc_flip * ((sign * ef)[:n10, None] * u) + 0.1 * g.normal(0, 1, (n10, d))).astype(np.float16)   # same noise as the planted layer
    lp = g.normal(-2, 1, (N, 2)); Q = np.c_[K, lp, np.zeros(N), lp]
    return Run(Q, (n10, n7, N - n10 - n7), H, E0, ENC, {"pair_seed": seeds})

if sys.argv[1:] == ["--selftest"]:
    fails = []
    def check(name, ok):
        print(("PASS " if ok else "FAIL ") + name, flush=True); (None if ok else fails.append(name))
    _, J = analyze(synth(a_flip=1.0, role=0.5, enc_flip=1.0, enc_role=0.0, R_=-1.0))
    check(f"planted flip → P1 supported (AUROC {J['P1']['auroc']:.3f} > null {J['P1']['null_q975']:.3f}, > C1 {J['P1']['C1']['ci'][1]:.3f})", J["P1"]["verdict"] == "supported")
    check(f"the planted layer is chosen in every fold ({J['chosen_layer_per_fold']})", J["chosen_layer_per_fold"] == [LAYERS[2]] * 3)
    check(f"null centred near 0.5 (median {J['P1']['null_median']:.3f})", abs(J["P1"]["null_median"] - 0.5) < 0.03)
    check(f"Llama drops 50% under headers, encoder 0% → DD > 0, supported ({J['P2']['A']:+.2f})", J["P2"]["verdict"] == "supported")
    check(f"planted R_s −1 → P3 supported ({J['P3']['A']:+.2f})", J["P3"]["verdict"] == "supported")
    check(f"positive controls: the single words are NOT planted → near 0.5 at L16 ({J['S3']['main'][str(LAYERS[2])]})",
          all(abs(v - 0.5) < 0.05 for v in J["S3"]["main"][str(LAYERS[2])].values()))
    _, J = analyze(synth(a_flip=0.0, R_=0.0))
    check(f"no signal → P1 not supported ({J['P1']['auroc']:.3f}), P3 not supported ({J['P3']['A']:+.2f})", J["P1"]["verdict"] == "not supported" and J["P3"]["verdict"] == "not supported")
    _, J = analyze(synth(a_flip=1.0, tok=1.0))
    check(f"token-only signal (Control 1 carries it as strongly) → P1 not supported (Llama {J['P1']['auroc']:.3f}, C1 {J['P1']['C1']['auroc']:.3f})",
          J["P1"]["verdict"] == "not supported" and J["P1"]["C1"]["auroc"] > 0.6)
    _, J = analyze(synth(a_flip=1.0, role=0.5, enc_flip=1.0, enc_role=0.5))
    check(f"text-level drop shared with the encoder → DD ≈ 0, not supported ({J['P2']['A']:+.2f}); raw D_G > 0 ({J['S1']['D_G_raw']['A']:+.2f})",
          J["P2"]["verdict"] == "not supported" and J["S1"]["D_G_raw"]["A_ci"][0] > 0)
    _, J = analyze(synth(a_flip=1.0, role=0.0, enc_flip=1.0, enc_role=0.6, R_=+1.0))
    check(f"encoder drops more → DD contradicted ({J['P2']['A']:+.2f}); planted R_s +1 → P3 contradicted ({J['P3']['A']:+.2f})",
          J["P2"]["verdict"] == "contradicted" and J["P3"]["verdict"] == "contradicted")
    R0 = synth(); k0 = int(R0.nat[0]); dl = lambda X: np.delete(np.asarray(X), k0, 0)
    R1 = Run(dl(R0.Q), (R0.n10 - 1, R0.n7, R0.n8), dl(R0.H), dl(R0.E0), dl(R0.ENC), R0.meta)
    try: analyze(R1); check("a missing native row is refused", False)
    except SystemExit as e: check(f"a missing native row is refused ({str(e)[:60]})", "missing" in str(e))
    print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails)); sys.exit(1 if fails else 0)

if __name__ == "__main__":
    F = Path(sys.argv[1]); TAG = sys.argv[2] if len(sys.argv) > 2 else "REAL_"
    Z = np.load(F / f"{TAG}a9b_q0.npz")
    if not Z["filled"].all(): raise SystemExit("a9b_q0: not every row filled (partial run)")
    if list(Z["layers"]) != list(LAYERS) or list(Z["cols"]) != list(A9B.COLS): raise SystemExit("a9b_q0: layers / columns are not a9b_core's")
    H = np.load(F / f"{TAG}a9b_h.npy", mmap_mode="r"); E0 = np.load(F / f"{TAG}a9b_e0.npy", mmap_mode="r"); ENC = np.load(F / f"{TAG}a9b_enc.npy", mmap_mode="r")
    if len(ENC) != int(Z["blocks"][0]): raise SystemExit("a9b_enc: not one vector per A10 row")
    rep = json.loads((F / f"{TAG}a9b_repro.json").read_text(encoding="utf-8")); enc = json.loads((F / f"{TAG}a9b_enc.json").read_text(encoding="utf-8"))
    extra = {"repro": f"{rep['n']} rows, bitwise {rep['bitwise']}, max |Δ| {rep['max']:.4f} nats ({ {k: v['n'] for k, v in rep['by_src'].items()} })",
             "enc": f"{enc['determinism']['bitwise']} / {enc['determinism']['rows']} bitwise; tokens max {enc['tokens']['max']}; truncated {enc['truncated']}"}
    OUT, J = analyze(Run(Z["rows"], Z["blocks"], H, E0, ENC, {"pair_seed": Z["pair_seed"]}), extra)
    G = json.loads((F / f"{TAG}a9b_gap_report.json").read_text(encoding="utf-8")); RC = json.loads((F / f"{TAG}a9b_rowcheck.json").read_text(encoding="utf-8"))
    head = ["# HUNT-DRIFT-01 A9b — Amendment 9b (87eae7d9…) — what the readout-position state encodes — EXPLORATORY", "",
            f"Row checks: {RC['a10_probe_draws']} probe × draw × 4 renderings (+ N), {RC['a8_units']} A8 units; longest rows {RC['row_tokens_max']}. "
            f"Prefill + probe_h vs a fresh pass (reported): n {G['n']}, max {G['max']:.3f}, median {G['median']:.3f} nats."]
    (F / f"{TAG}A9B_ANALYSIS.md").write_text("\n".join(head + [""] + OUT) + "\n", encoding="utf-8")
    (F / f"{TAG}A9B_analysis.json").write_text(json.dumps(J, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)), encoding="utf-8")
    print("\n".join(head + [""] + OUT))
