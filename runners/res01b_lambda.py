#!/usr/bin/env python
# RES-01b -- is RES-01a provenance or POSITION? Cached, no forwards. PREREG_RES01B.md, chained RES-01a 7a098124...
# Per layer: reproduce KDR k=50 role-deflation (repro-gated) -> Xdef; then
#   Arm P: MLP decode abs_pos bucket from Xdef (is position non-linearly available)
#   Arm M (DECISIVE): role MLP on a position-MATCHED subset (roles balanced within 5-tok abs_pos bins -> position
#          role-uninformative by construction). matched acc near 0.9 -> provenance real & position-independent.
#   Arm R: role MLP after linear position-deflation of Xdef (brackets from the other side)
# abs_pos = span_start_index (prompts.jsonl) + within-span offset. role=trusted/untrusted. Split group-disjoint.
import os, json, time, csv
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
import torch, torch.nn as nn, torch.nn.functional as F

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
SMOKE = os.environ.get("SMOKE", "0") == "1"
LAYERS = [8, 24, 31, 16]
SATURATED = {8, 24, 31}
KCAP = 5 if SMOKE else 50
PE_STOP = 0.45
SEED = 20260914
NULLN = 10 if SMOKE else 100
BOOT = 200 if SMOKE else 1000
POS_BINS = 10          # Arm P buckets
BINW = 5               # Arm M abs_pos bin width
MINPB = 10             # Arm M min per role per bin
POS_DEFL_CAP = 20; POS_DEFL_STOP = 0.05
def log(*a): print(*a, flush=True)
dev = "cuda" if torch.cuda.is_available() else "cpu"

def build_subspace(Xr, y, tr, te, kcap, pe_stop):
    basis = []; curve = []; Xdef = Xr.copy()
    for i in range(kcap + 1):
        sc = StandardScaler().fit(Xdef[tr])
        clf = LogisticRegression(C=1.0, max_iter=300, solver="lbfgs").fit(sc.transform(Xdef[tr]), y[tr])
        pe = 1.0 - float(clf.score(sc.transform(Xdef[te]), y[te])); curve.append(pe)
        if pe >= pe_stop or len(basis) >= kcap: break
        scale = sc.scale_.copy(); scale[~np.isfinite(scale) | (scale == 0)] = 1.0
        w = clf.coef_[0] / scale
        for b in basis: w = w - (w @ b) * b
        nw = np.linalg.norm(w)
        if nw < 1e-8: break
        w = w / nw; basis.append(w); Bm = np.array(basis).T; Xdef = Xr - (Xr @ Bm) @ Bm.T
    B = np.array(basis).T if basis else np.zeros((Xr.shape[1], 0), np.float32)
    return B.astype(np.float32), len(basis), curve

def pos_deflate(X, pos, tr, cap, stop):
    """Iteratively remove linear abs_pos structure. Returns deflated X and directions removed."""
    Xd = X.copy(); pz = (pos - pos[tr].mean()) / (pos[tr].std() + 1e-8); nb = 0
    for _ in range(cap):
        sc = StandardScaler().fit(Xd[tr]); lr = LinearRegression().fit(sc.transform(Xd[tr]), pz[tr])
        r2 = lr.score(sc.transform(Xd[tr]), pz[tr])
        if r2 < stop: break
        scale = sc.scale_.copy(); scale[~np.isfinite(scale) | (scale == 0)] = 1.0
        w = lr.coef_ / scale; nw = np.linalg.norm(w)
        if nw < 1e-8: break
        w = w / nw; Xd = Xd - np.outer(Xd @ w, w); nb += 1
    return Xd, nb

def fit_eval(Xtr, ytr, Xte, kind, nout, epochs, seed):
    torch.manual_seed(seed); d = Xtr.shape[1]
    net = (nn.Linear(d, nout) if kind == "linear" else
           nn.Sequential(nn.Linear(d, 128), nn.ReLU(), nn.Dropout(0.1), nn.Linear(128, nout))).to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3, weight_decay=1e-4)
    Xt = torch.tensor(Xtr, dtype=torch.float32, device=dev); yt = torch.tensor(ytr, dtype=torch.long, device=dev)
    net.train()
    for ep in range(epochs):
        perm = torch.randperm(len(Xt), device=dev)
        for i in range(0, len(perm), 8192):
            idx = perm[i:i + 8192]; opt.zero_grad(); F.cross_entropy(net(Xt[idx]), yt[idx]).backward(); opt.step()
    net.eval()
    with torch.no_grad():
        pred = net(torch.tensor(Xte, dtype=torch.float32, device=dev)).argmax(1).cpu().numpy()
    del Xt, yt
    if dev == "cuda": torch.cuda.empty_cache()
    return pred

def main():
    t0 = time.time()
    meta = np.load(os.path.join(HERE, "tok_meta.npz"))
    role = meta["role"].astype(np.int64); split = meta["split"].astype(np.int64); pidx = meta["prompt_idx"]
    L = [json.loads(l) for l in open(os.path.join(HERE, "prompts.jsonl"), encoding="utf-8")]
    ssi = np.array([r["span_start_index"] for r in L])
    abs_pos = np.zeros(len(pidx), dtype=np.int64)
    for p in range(len(L)):
        idx = np.where(pidx == p)[0]; abs_pos[idx] = ssi[p] + np.arange(len(idx))
    counts = {int(v): int((split == v).sum()) for v in np.unique(split)}
    train_val = max(counts, key=counts.get)
    tr = np.where(split == train_val)[0]; te = np.where(split != train_val)[0]
    kdr = json.load(open(os.path.join(HERE, "kdr01_k50.json")))
    kdr_k = {int(k): int(v) for k, v in kdr["k_per_layer"].items()}
    kdr_pe = {int(k): v for k, v in kdr["deflation_pe_curves"].items()}
    # global 10 quantile bins for Arm P
    qedges = np.quantile(abs_pos, np.linspace(0, 1, POS_BINS + 1)); qedges[-1] += 1
    posbin = np.clip(np.digitize(abs_pos, qedges[1:-1]), 0, POS_BINS - 1)
    log(f"[Rb] dev={dev} train={train_val} n_tr={len(tr)} n_te={len(te)} role_bal={role.mean():.3f} "
        f"abs_pos[{abs_pos.min()},{abs_pos.max()}] ({time.time()-t0:.0f}s)")

    def std_fit(Xtr_idx, Xall):
        mu = Xall[Xtr_idx].mean(0); sd = Xall[Xtr_idx].std(0); sd[sd == 0] = 1.0
        return ((Xall - mu) / sd).astype(np.float32)

    def probe(Xall, tr_i, te_i, y, nout, tag, layer, arm, matched_n=None):
        Xs = std_fit(tr_i, Xall)
        pred = fit_eval(Xs[tr_i], y[tr_i], Xs[te_i], "mlp", nout, 40, SEED)
        yte = y[te_i]; acc = float((pred == yte).mean())
        pte = pidx[te_i]; uq = np.unique(pte); rng = np.random.default_rng(SEED); correct = (pred == yte); accs = np.empty(BOOT)
        for b in range(BOOT):
            pk = rng.choice(uq, len(uq), replace=True); sel = np.concatenate([np.where(pte == p)[0] for p in pk]); accs[b] = correct[sel].mean()
        lo, hi = np.percentile(accs, [2.5, 97.5])
        rng2 = np.random.default_rng(SEED + 1); nul = np.empty(NULLN)
        for j in range(NULLN):
            ysh = y[tr_i].copy(); rng2.shuffle(ysh); pj = fit_eval(Xs[tr_i], ysh, Xs[te_i], "mlp", nout, 40, SEED + 100 + j); nul[j] = (pj == yte).mean()
        chance = 1.0 / nout
        rows.append([layer, arm, tag, round(acc, 4), round(lo, 4), round(hi, 4), round(float(np.percentile(nul, 95)), 4),
                     round(chance, 4), (matched_n if matched_n is not None else len(tr_i) + len(te_i))])
        log(f"[Rb] L{layer} {arm}: acc={acc:.3f} CI[{lo:.3f},{hi:.3f}] null_p95={np.percentile(nul,95):.3f} chance={chance:.3f} n_te={len(te_i)} ({time.time()-t0:.0f}s)")
        return {"acc": acc, "ci": [float(lo), float(hi)], "null_p95": float(np.percentile(nul, 95)), "chance": chance}

    rows = []; verdicts = {}
    for Lyr in LAYERS:
        Xr = np.load(os.path.join(HERE, f"tok_resid_L{Lyr}.npy")).astype(np.float32)
        if SMOKE:
            keep = np.concatenate([tr[:4000], te[:2000); mk = np.zeros(len(Xr), bool); mk[keep] = True
            trL = np.where(mk & (split == train_val))[0]; teL = np.where(mk & (split != train_val))[0]
        else:
            trL, teL = tr, te
        B, k, curve = build_subspace(Xr, role, trL, teL, KCAP, PE_STOP)
        pe_final = curve[-1] if curve else float("nan")
        rk = kdr_k.get(Lyr); rpe = (kdr_pe.get(Lyr) or [None])[-1] if kdr_pe.get(Lyr) else None
        repro_ok = bool(((rk is None) or abs(k - rk) <= 2 or SMOKE) and ((rpe is None) or abs(pe_final - rpe) <= 0.05 or SMOKE))
        log(f"[Rb] L{Lyr}: refit k={k} pe={pe_final:.3f} | KDR k={rk} pe={rpe} repro_ok={repro_ok} ({time.time()-t0:.0f}s)")
        Xdef = (Xr - (Xr @ B) @ B.T) if B.shape[1] > 0 else Xr.copy()

        # Arm P: position bucket from Xdef
        P = probe(Xdef, trL, teL, posbin, POS_BINS, "post_deflation", Lyr, "P_position_bucket")
        # Arm M: position-matched role decoding
        rng = np.random.default_rng(SEED); binid = abs_pos // BINW; keep = []
        for b in np.unique(binid):
            m0 = np.where((binid == b) & (role == 0))[0]; m1 = np.where((binid == b) & (role == 1))[0]
            n = min(len(m0), len(m1))
            if n < MINPB: continue
            rng.shuffle(m0); rng.shuffle(m1); keep.extend(m0[:n].tolist() + m1[:n].tolist())
        keep = np.array(sorted(keep)); kset = set(keep.tolist())
        trM = np.array([i for i in trL if i in kset]); teM = np.array([i for i in teL if i in kset])
        thin = len(teM) < (200 if SMOKE else 2000)
        if thin or len(trM) < 100:
            log(f"[Rb] L{Lyr} Arm M THIN: matched tr={len(trM)} te={len(teM)} -- not read")
            M = {"acc": None, "thin": True}
            rows.append([Lyr, "M_matched_role", "post_deflation", None, None, None, None, 0.5, len(keep)])
        else:
            M = probe(Xdef, trM, teM, role, 2, "post_deflation", Lyr, "M_matched_role", matched_n=len(keep))
            M["thin"] = False
        # Arm R: role after position-deflation
        Xpd, nb = pos_deflate(Xdef, abs_pos, trL, POS_DEFL_CAP, POS_DEFL_STOP)
        R = probe(Xpd, trL, teL, role, 2, "post_posdeflation", Lyr, "R_role_after_posdefl")
        # reference: unmatched role on Xdef (reproduces RES-01a)
        REF = probe(Xdef, trL, teL, role, 2, "post_deflation", Lyr, "ref_role_unmatched")

        # verdict (PREREG §4) on Arm M
        if M.get("thin"):
            vv = "THIN-NOT-READ"
        elif M["acc"] >= 0.80 and M["ci"][0] > 0.65:
            vv = "PROVENANCE-REAL-POSITION-INDEPENDENT"
        elif M["acc"] <= 0.60 and M["ci"][1] < 0.65:
            vv = "POSITION-DECODED-RETRACT-RES01A"
        else:
            vv = "BOTH-PRESENT"
        verdicts[Lyr] = {"saturated": Lyr in SATURATED, "repro_ok": repro_ok, "k": k,
                         "armP_pos_acc": P["acc"], "armP_chance": P["chance"],
                         "armM_matched_role_acc": M.get("acc"), "armM_ci": M.get("ci"), "armM_matched_n": len(keep),
                         "armR_role_after_posdefl_acc": R["acc"], "armR_ndir": nb,
                         "ref_unmatched_role_acc": REF["acc"], "verdict": vv}
        log(f"[Rb] L{Lyr} VERDICT {vv} (armM={M.get('acc')}, ref={REF['acc']}, armP={P['acc']}) ({time.time()-t0:.0f}s)")
        del Xr, Xdef, Xpd

    sat = [Lyr for Lyr in SATURATED if verdicts.get(Lyr, {}).get("repro_ok") and not verdicts.get(Lyr, {}).get("verdict") == "THIN-NOT-READ"]
    real = [Lyr for Lyr in sat if verdicts[Lyr]["verdict"] == "PROVENANCE-REAL-POSITION-INDEPENDENT"]
    pos_dec = [Lyr for Lyr in sat if verdicts[Lyr]["verdict"] == "POSITION-DECODED-RETRACT-RES01A"]
    both = [Lyr for Lyr in sat if verdicts[Lyr]["verdict"] == "BOTH-PRESENT"]
    if not sat:
        reading = "INVALID: no readable saturated layer"
    elif pos_dec and not real:
        reading = f"POSITION-DECODED at {pos_dec} -> RES-01a decoded position; RETRACT reframe; lesson inverts"
    elif real and not pos_dec:
        reading = f"PROVENANCE-REAL-POSITION-INDEPENDENT at {real} -> RES-01a stands; reframe stands; non-linear intervention earned"
    else:
        reading = f"MIXED: real={real} both={both} position={pos_dec} -- read per layer"
    out = {"prereg": "PREREG_RES01B.md", "SMOKE": SMOKE,
           "chained_to_RES01A": "7a098124afdae9ea3f6f7e06e996441675eccd13efe2b683eea42a239dcc7e37",
           "layers": LAYERS, "saturated": sorted(SATURATED), "train_split_val": train_val,
           "verdicts": verdicts, "reading": reading, "runtime_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "res01b_arms_smoke.csv" if SMOKE else "res01b_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["layer", "arm", "condition", "heldout_score", "ci_lo", "ci_hi", "null_p95", "chance", "n_or_matched"])
        for r in rows: w.writerow(r)
    fn = os.path.join(OUT, "res01b_smoke.json" if SMOKE else "res01b.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[Rb] reading: {reading}; wrote {fn}")

if __name__ == "__main__":
    main()
