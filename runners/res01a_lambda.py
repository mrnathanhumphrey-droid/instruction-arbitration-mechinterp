#!/usr/bin/env python
# RES-01a Arm A -- non-linear provenance after k=50 linear deflation, on CACHED residuals (no forwards).
# PREREG_RES01A.md, chained PRV-04c e33230a7... For each cached layer: reproduce KDR's k=50 iterative linear
# deflation (sklearn, exact build_subspace), verify k/P_e vs kdr01_k50.json (reproduction gate), then fit a
# small MLP for role (provenance) on the k=50-DEFLATED residual and test if it beats chance + the linear probe
# + a shuffled-label null on the held-out group-disjoint split. Saturated layers {8,24,31}; L16 cap-bound control.
import os, json, time, csv
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import torch, torch.nn as nn, torch.nn.functional as F

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
SMOKE = os.environ.get("SMOKE", "0") == "1"
LAYERS = [8, 24, 31, 16]                 # 8,24,31 saturated; 16 cap-bound control
SATURATED = {8, 24, 31}
KCAP = 5 if SMOKE else 50
PE_STOP = 0.45
SEED = 20260914
MLP_NULL = 10 if SMOKE else 100
LIN_NULL = 20 if SMOKE else 200
BOOT = 200 if SMOKE else 1000
PASS_FLOOR = 0.55
def log(*a): print(*a, flush=True)

def build_subspace(Xr, role, tr, te, kcap, pe_stop):
    """EXACT KDR build_subspace (kdr01_lambda.py): iterative deflation, held-out P_e curve, stop>=pe_stop|cap."""
    basis = []; curve = []
    Xdef = Xr.copy()
    for i in range(kcap + 1):
        sc = StandardScaler().fit(Xdef[tr])
        clf = LogisticRegression(C=1.0, max_iter=300, solver="lbfgs").fit(sc.transform(Xdef[tr]), role[tr])
        pe = 1.0 - float(clf.score(sc.transform(Xdef[te]), role[te])); curve.append(pe)
        if pe >= pe_stop or len(basis) >= kcap: break
        scale = sc.scale_.copy(); scale[~np.isfinite(scale) | (scale == 0)] = 1.0
        w = clf.coef_[0] / scale
        for b in basis: w = w - (w @ b) * b
        nw = np.linalg.norm(w)
        if nw < 1e-8: break
        w = w / nw; basis.append(w)
        Bm = np.array(basis).T; Xdef = Xr - (Xr @ Bm) @ Bm.T
    B = np.array(basis).T if basis else np.zeros((Xr.shape[1], 0), np.float32)
    return B.astype(np.float32), len(basis), curve

dev = "cuda" if torch.cuda.is_available() else "cpu"

def fit_eval(Xtr, ytr, Xte, kind, epochs, seed):
    """Torch probe on GPU. Returns per-row held-out predictions (np)."""
    torch.manual_seed(seed); d = Xtr.shape[1]
    net = (nn.Linear(d, 2) if kind == "linear" else
           nn.Sequential(nn.Linear(d, 128), nn.ReLU(), nn.Dropout(0.1), nn.Linear(128, 2))).to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3, weight_decay=1e-4)
    Xt = torch.tensor(Xtr, dtype=torch.float32, device=dev); yt = torch.tensor(ytr, dtype=torch.long, device=dev)
    net.train()
    for ep in range(epochs):
        perm = torch.randperm(len(Xt), device=dev)
        for i in range(0, len(perm), 8192):
            idx = perm[i:i + 8192]; opt.zero_grad()
            F.cross_entropy(net(Xt[idx]), yt[idx]).backward(); opt.step()
    net.eval()
    with torch.no_grad():
        Xe = torch.tensor(Xte, dtype=torch.float32, device=dev)
        pred = net(Xe).argmax(1).cpu().numpy()
    del Xt, yt; torch.cuda.empty_cache() if dev == "cuda" else None
    return pred

def main():
    t0 = time.time()
    meta = np.load(os.path.join(HERE, "tok_meta.npz"))
    role = meta["role"].astype(np.int64); split = meta["split"].astype(np.int64); pidx = meta["prompt_idx"]
    # KDR "full 80k" train: the larger split is train. verify by reproduction.
    counts = {int(v): int((split == v).sum()) for v in np.unique(split)}
    train_val = max(counts, key=counts.get)
    tr = np.where(split == train_val)[0]; te = np.where(split != train_val)[0]
    kdr = json.load(open(os.path.join(HERE, "kdr01_k50.json")))
    kdr_k = {int(k): int(v) for k, v in kdr["k_per_layer"].items()}
    kdr_pe = {int(k): v for k, v in kdr["deflation_pe_curves"].items()}
    log(f"[R] dev={dev} split counts={counts} train={train_val} n_tr={len(tr)} n_te={len(te)} "
        f"role balance={role.mean():.3f} ({time.time()-t0:.0f}s)")

    rows = []; verdicts = {}
    for L in LAYERS:
        Xr = np.load(os.path.join(HERE, f"tok_resid_L{L}.npy")).astype(np.float32)
        if SMOKE:  # subsample rows keeping split structure for a fast gate
            keep = np.concatenate([tr[:4000], te[:2000); mask = np.zeros(len(Xr), bool); mask[keep] = True
            trL = np.where(mask & (split == train_val))[0]; teL = np.where(mask & (split != train_val))[0]
        else:
            trL, teL = tr, te
        # ---- reproduce KDR deflation ----
        B, k, curve = build_subspace(Xr, role, trL, teL, KCAP, PE_STOP)
        pe_final = curve[-1] if curve else float("nan")
        repro_k = kdr_k.get(L); repro_pe = (kdr_pe.get(L) or [None])[-1] if kdr_pe.get(L) else None
        k_ok = (repro_k is None) or (abs(k - repro_k) <= 2) or SMOKE
        pe_ok = (repro_pe is None) or (abs(pe_final - repro_pe) <= 0.05) or SMOKE
        repro_ok = bool(k_ok and pe_ok)
        log(f"[R] L{L}: refit k={k} pe_final={pe_final:.3f} | KDR k={repro_k} pe={repro_pe} repro_ok={repro_ok} ({time.time()-t0:.0f}s)")
        # ---- deflated residual ----
        Xdef = Xr - (Xr @ B) @ B.T if B.shape[1] > 0 else Xr.copy()

        def standardize(Xtr_idx, Xall):
            mu = Xall[Xtr_idx].mean(0); sd = Xall[Xtr_idx].std(0); sd[sd == 0] = 1.0
            return (Xall - mu) / sd

        def probe_set(Xall, tag):
            Xs = standardize(trL, Xall).astype(np.float32)
            Xtr, ytr, Xte, yte = Xs[trL], role[trL], Xs[teL], role[teL]
            res = {}
            for kind, ep in (("linear", 60), ("mlp", 40)):
                pred = fit_eval(Xtr, ytr, Xte, kind, ep, SEED)
                acc = float((pred == yte).mean())
                # cluster bootstrap by prompt_idx over held-out
                pte = pidx[teL]; uq = np.unique(pte); rng = np.random.default_rng(SEED)
                accs = np.empty(BOOT)
                correct = (pred == yte)
                for b in range(BOOT):
                    pk = rng.choice(uq, len(uq), replace=True)
                    sel = np.concatenate([np.where(pte == p)[0] for p in pk])
                    accs[b] = correct[sel].mean()
                lo, hi = np.percentile(accs, [2.5, 97.5])
                # shuffled-train-label null
                nn_ = MLP_NULL if kind == "mlp" else LIN_NULL
                rng2 = np.random.default_rng(SEED + 1); null = np.empty(nn_)
                for j in range(nn_):
                    ysh = ytr.copy(); rng2.shuffle(ysh)
                    pj = fit_eval(Xtr, ysh, Xte, kind, ep, SEED + 100 + j)
                    null[j] = (pj == yte).mean()
                res[kind] = {"acc": acc, "ci": [float(lo), float(hi)], "null_p95": float(np.percentile(null, 95)),
                             "null_mean": float(null.mean())}
                rows.append([L, tag, kind, round(acc, 4), round(lo, 4), round(hi, 4),
                             round(float(np.percentile(null, 95)), 4), k, repro_ok])
                log(f"[R] L{L} {tag} {kind}: acc={acc:.3f} CI[{lo:.3f},{hi:.3f}] null_p95={np.percentile(null,95):.3f} ({time.time()-t0:.0f}s)")
            return res

        post = probe_set(Xdef, "post_deflation")
        pre = probe_set(Xr, "pre_deflation")   # positive control: probes decode when provenance present
        # ---- pass criterion (PREREG §3): MLP CI lower > max(0.55, linear_acc+0.03, null_p95) on deflated ----
        mlp = post["mlp"]; lin = post["linear"]
        thresh = max(PASS_FLOOR, lin["acc"] + 0.03, mlp["null_p95"])
        nonlinear = bool(repro_ok and mlp["ci"][0] > thresh)
        verdicts[L] = {"saturated": L in SATURATED, "repro_ok": repro_ok, "k": k, "pe_final": pe_final,
                       "post_mlp_acc": mlp["acc"], "post_mlp_ci": mlp["ci"], "post_lin_acc": lin["acc"],
                       "post_mlp_null_p95": mlp["null_p95"], "pre_mlp_acc": pre["mlp"]["acc"],
                       "pre_lin_acc": pre["linear"]["acc"], "pass_threshold": thresh,
                       "NONLINEAR_PROVENANCE": nonlinear}
        log(f"[R] L{L} VERDICT nonlinear_provenance={nonlinear} (mlp_ci_lo={mlp['ci'][0]:.3f} > thr={thresh:.3f}?) "
            f"pre_mlp={pre['mlp']['acc']:.3f} ({time.time()-t0:.0f}s)")
        del Xr, Xdef

    sat_pos = [L for L in SATURATED if verdicts.get(L, {}).get("NONLINEAR_PROVENANCE")]
    sat_tested = [L for L in SATURATED if verdicts.get(L, {}).get("repro_ok")]
    if not sat_tested:
        reading = "INVALID: no saturated layer reproduced KDR deflation"
    elif sat_pos:
        reading = (f"NON-LINEAR-PROVENANCE-EXISTS at saturated layers {sat_pos} -> 'linear' is load-bearing; "
                   "earned next = non-linear intervention (NOT Arm B)")
    else:
        reading = ("ALL-SATURATED-NULL (L8/L24/L31): no non-linear provenance in the deflated residual at cached "
                   "saturated layers -> earned next = Arm B (surviving OUTCOME info; needs forwards)")
    out = {"prereg": "PREREG_RES01A.md", "SMOKE": SMOKE,
           "chained_to_PRV04C": "e33230a7b02e475c152dfefd3a7346beee60c85994376559e29a89d70450545c",
           "layers": LAYERS, "saturated": sorted(SATURATED), "train_split_val": train_val,
           "n_tr": len(tr), "n_te": len(te), "verdicts": verdicts, "reading": reading,
           "runtime_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "res01a_arms_smoke.csv" if SMOKE else "res01a_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["layer", "condition", "probe", "heldout_acc", "ci_lo", "ci_hi", "null_p95", "refit_k", "repro_ok"])
        for r in rows: w.writerow(r)
    fn = os.path.join(OUT, "res01a_smoke.json" if SMOKE else "res01a.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[R] reading: {reading}; wrote {fn}")

if __name__ == "__main__":
    main()
