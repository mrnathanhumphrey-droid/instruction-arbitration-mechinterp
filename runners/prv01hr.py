#!/usr/bin/env python
# PRV-01h-r -- does PRV-01h's existential result survive reparameterization? Llama-3.1-8B-Instruct.
# PREREG_PRV01HR.md, chained PRV-01h. ROBUSTNESS SWEEP (not a new question): run the deflation loop under THREE
# parameterizations and ask whether necessity stays ~0 (existential generalizes) or diverges (2608.10566's non-invariance is
# operative on our data). k*_P is a PROCEDURE-DEFINED deflation depth, NEVER a dimension (binding).
#   P1: StandardScaler + Euclidean projection (EXACTLY PRV-01h; reproduction arm).
#   P2: no scaler, raw residual coords, Euclidean projection.
#   P3: ZCA whitening (train-cov, fold-internal), deflate+project in whitened coords, map back before the forward pass.
# necessity_P = [Y(H) - Y(H_perp{k*_P})]/[Y(H)-Y(U)] at each P's stopping point, random-rank control at the MATCHED rank.
# Gates: REPRODUCTION (P1 necessity@25 within +-0.02 of PRV-01h -0.0734), G-DECODABILITY-KILLED (held-out acc <=0.55 at stop,
# else that P depth-limited/excluded), G-DYNAMIC-RANGE (random-rank move <0.597), G-COHERENCE (mass>=0.10). Cap raised to 40 so
# decodability can actually reach chance (PRV-01h censored at 25 @ 0.579).
import os, json, time
import numpy as np, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
NTMPL = 30; BOOT = 300 if SMOKE else 5000; SEED = 20260924
IPY_HDR = "<|start_header_id|>ipython<|end_header_id|>"; USR_HDR = "<|start_header_id|>user<|end_header_id|>"
EOH = 128007; EOT = 128009
ANCHOR_U = -3.191; ANCHOR_H = -0.805; ANCHOR_TOL = 0.15
MASS_FLOOR = 0.10; DYNRANGE_BAR = 0.5965935601749355
DEFLATE_STOP_ACC = 0.55; DEFLATE_CAP = 40; MAXIT = 200
REPRO_TARGET_K25 = -0.07344781735535909; REPRO_TOL = 0.02   # PRV-01h necessity at k=25
CAP_POS = 64
def log(*a): print(*a, flush=True)


def base3(it):
    return [{"role": "system", "content": it["system"]},
            {"role": "user", "content": it["user_trigger"]},
            {"role": "assistant", "content": it["assistant_stub"]}]


def render_raw(tok, it):
    m = base3(it) + [{"role": "user", "content": it["tool_text"]}]
    textU = tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True)
    idx = textU.rfind(USR_HDR)
    textH = textU[:idx] + IPY_HDR + textU[idx + len(USR_HDR):]
    return textU, textH


def content_span(ids):
    e = [k for k, t in enumerate(ids) if t == EOH][-2]
    eot = [k for k, t in enumerate(ids) if t == EOT and k > e][0]
    return e, list(range(e + 1, eot))


def deflate(X, tr, te, ylab, mode):
    """INLP under parameterization `mode`. Returns (decod list, info dict). Bases are unit vectors in the coords the
    parameterization projects in (raw for P1/P2, whitened for P3)."""
    decod = []
    if mode == "P3":
        mu = X[tr].mean(0).astype(np.float64)
        Xc = (X.astype(np.float64) - mu)
        Cov = np.cov(Xc[tr].T) + 1e-3 * np.eye(X.shape[1])
        vals, vecs = np.linalg.eigh(Cov); vals = np.clip(vals, 1e-6, None)
        W = (vecs * (vals ** -0.5)) @ vecs.T           # ZCA whitening  (D,D)
        Winv = (vecs * (vals ** 0.5)) @ vecs.T
        Z = Xc @ W.T                                    # whitened, all items
        Xd = Z.copy(); basis = []
        for k in range(1, DEFLATE_CAP + 1):
            clf = LogisticRegression(C=1.0, max_iter=MAXIT).fit(Xd[tr], ylab[tr])
            acc = float((clf.predict(Xd[te]) == ylab[te]).mean()); decod.append(acc)
            w = clf.coef_[0]; w = (w / np.linalg.norm(w)); basis.append(w)
            Xd = Xd - np.outer(Xd @ w, w)
            if acc <= DEFLATE_STOP_ACC: break
        return decod, {"type": "P3", "U": np.stack(basis, 1).astype(np.float32),
                       "W": W.astype(np.float32), "Winv": Winv.astype(np.float32), "mu": mu.astype(np.float32)}
    else:
        Xd = X.copy(); basis = []
        for k in range(1, DEFLATE_CAP + 1):
            if mode == "P1":
                sc = StandardScaler().fit(Xd[tr]); clf = LogisticRegression(C=1.0, max_iter=MAXIT).fit(sc.transform(Xd[tr]), ylab[tr])
                acc = float((clf.predict(sc.transform(Xd[te])) == ylab[te]).mean()); w = clf.coef_[0] / sc.scale_
            else:  # P2, no scaler
                clf = LogisticRegression(C=1.0, max_iter=MAXIT).fit(Xd[tr], ylab[tr])
                acc = float((clf.predict(Xd[te]) == ylab[te]).mean()); w = clf.coef_[0]
            decod.append(acc); w = (w / np.linalg.norm(w)).astype(np.float32); basis.append(w)
            Xd = Xd - np.outer(Xd @ w, w)
            if acc <= DEFLATE_STOP_ACC: break
        return decod, {"type": mode, "V": np.stack(basis, 1).astype(np.float32)}


def removed_raw_basis(info, k):
    """Orthonormal basis (raw coords) of the subspace removed at depth k, for principal-angle overlap."""
    if info["type"] == "P3":
        M = info["Winv"] @ info["U"][:, :k]            # directions removed in raw coords
        return np.linalg.qr(M)[0]
    return np.linalg.qr(info["V"][:, :k])[0]


def main():
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_tool_contested_true_false.jsonl"), encoding="utf-8")]
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    POS = stim[0]["readout_pos"]; NEG = stim[0]["readout_neg"]
    TPOS = tok(POS, add_special_tokens=False)["input_ids"][0]; TNEG = tok(NEG, add_special_tokens=False)["input_ids"][0]
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16, device_map={"": 0}).eval()
    dev = next(model.parameters()).device; import transformers
    NL = model.config.num_hidden_layers; D = model.config.hidden_size
    log(f"[HR] {MODEL_ID} on {dev}; tf {transformers.__version__} NL={NL} D={D} n={len(stim)} ({time.time()-t0:.0f}s)")

    # ---- hook: "orth" (subtract (h@V)V^T) or "mat" (subtract (h-mean)@Msub^T, Msub=Winv U U^T W) ----
    pst = {"active": False, "pos": None, "mode": None, "V": None, "M": None, "mean": None}
    def make_hook():
        def hook(module, inp, out):
            if not pst["active"]:
                return out
            hs = out[0] if isinstance(out, tuple) else out
            p = pst["pos"]; sub = hs[:, p, :]
            if pst["mode"] == "orth":
                hs[:, p, :] = sub - (sub @ pst["V"]) @ pst["V"].t()
            else:
                hs[:, p, :] = sub - ((sub - pst["mean"]) @ pst["M"].t())
            return (hs,) + tuple(out[1:]) if isinstance(out, tuple) else hs
        return hook
    for layer in model.model.layers:
        layer.register_forward_hook(make_hook())

    def Y_of(ids, pos, mode=None, V=None, M=None, mean=None, want_hidden=False):
        pst.update(active=(mode is not None), pos=pos, mode=mode, V=V, M=M, mean=mean)
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            o = model(input_ids=t, use_cache=False, output_hidden_states=want_hidden)
            lp = torch.log_softmax(o.logits[0, -1, :].float(), -1)
            h1 = o.hidden_states[1][0, pos, :].float().cpu().numpy() if want_hidden else None
        pst["active"] = False
        R = float(lp[TPOS] - lp[TNEG]); M_ = float(torch.exp(lp[TPOS]) + torch.exp(lp[TNEG]))
        return (R, M_, h1) if want_hidden else (R, M_)

    use = list(range(0, len(stim), len(stim) // 40))[:40] if SMOKE else list(range(len(stim)))
    N = len(use); tmpl = np.array([stim[i]["template_idx"] for i in use])
    tgt_pos = np.array([1 if stim[i]["target_sys"] == POS else 0 for i in use])
    cap = min(DEFLATE_CAP, 6) if SMOKE else DEFLATE_CAP
    globals()["DEFLATE_CAP"] = cap

    # ---- PASS 1: clean Y(U),Y(H); collect reps ----
    YU = np.zeros(N); YH = np.zeros(N); MU = np.zeros(N); MH = np.zeros(N)
    ids_cache = [None] * N; span_cache = [None] * N; gconstruct = 0
    X = []; ylab = []; item_of = []
    for n, i in enumerate(use):
        it = stim[i]; wpos = it["target_sys"] == POS
        tU, tH = render_raw(tok, it)
        iU = tok(tU, add_special_tokens=False)["input_ids"]; iH = tok(tH, add_special_tokens=False)["input_ids"]
        eU, pU = content_span(iU); eH, pH = content_span(iH)
        if iU[eU + 1:] == iH[eH + 1:]: gconstruct += 1
        ids_cache[n] = (iU, iH); span_cache[n] = (pU, pH)
        ru, mu_, h1u = Y_of(iU, pU, want_hidden=True); YU[n] = ru if wpos else -ru; MU[n] = mu_
        rh, mh_, h1h = Y_of(iH, pH, want_hidden=True); YH[n] = rh if wpos else -rh; MH[n] = mh_
        for pi in range(min(CAP_POS, len(pU))):
            X.append(h1u[pi]); ylab.append(0); item_of.append(n)
        for pi in range(min(CAP_POS, len(pH))):
            X.append(h1h[pi]); ylab.append(1); item_of.append(n)
        if (n + 1) % 120 == 0: log(f"[HR] pass1 {n+1}/{N} ({time.time()-t0:.0f}s)")
    X = np.array(X, dtype=np.float32); ylab = np.array(ylab); item_of = np.array(item_of)
    yU = float(YU.mean()); yH = float(YH.mean()); denom = yH - yU
    anchor_ok = abs(yU - ANCHOR_U) <= ANCHOR_TOL and abs(yH - ANCHOR_H) <= ANCHOR_TOL
    gconstruct_ok = gconstruct == N
    log(f"[HR] PASS1 Y(U)={yU:+.3f} Y(H)={yH:+.3f} denom={denom:+.3f} anchor={anchor_ok} X={X.shape}")

    rng = np.random.default_rng(SEED); perm = rng.permutation(N); tr_items = set(perm[:N // 2].tolist())
    tr = np.array([it_ in tr_items for it_ in item_of]); te = ~tr

    def per_t(x): return np.array([x[tmpl == t].mean() if (tmpl == t).any() else np.nan for t in range(NTMPL)])
    ptH = per_t(YH); ptU = per_t(YU)

    def necessity_at(info, k):
        """Forward-pass necessity of removing the depth-k subspace of `info`, + random-rank-k control (per item)."""
        if info["type"] == "P3":
            U = np.linalg.qr(info["U"][:, :k])[0].astype(np.float32)
            Msub = (info["Winv"] @ U @ U.T @ info["W"]).astype(np.float32)
            Mt = torch.tensor(Msub, dtype=torch.bfloat16, device=dev)
            meant = torch.tensor(info["mu"], dtype=torch.bfloat16, device=dev)
            vmode = ("mat", None, Mt, meant)
        else:
            V = np.linalg.qr(info["V"][:, :k])[0].astype(np.float32)
            Vt = torch.tensor(V, dtype=torch.bfloat16, device=dev)
            vmode = ("orth", Vt, None, None)
        Yv = np.zeros(N); Yr = np.zeros(N); Mv = np.zeros(N)
        for n, i in enumerate(use):
            wpos = stim[i]["target_sys"] == POS; (iU, iH) = ids_cache[n]; (pU, pH) = span_cache[n]
            rv, mv = Y_of(iH, pH, mode=vmode[0], V=vmode[1], M=vmode[2], mean=vmode[3])
            Yv[n] = rv if wpos else -rv; Mv[n] = mv
            R = np.linalg.qr(np.random.default_rng(SEED + 1000 + n).standard_normal((D, DEFLATE_CAP)).astype(np.float32))[0][:, :k]
            Rt = torch.tensor(np.ascontiguousarray(R), dtype=torch.bfloat16, device=dev)
            rr, _ = Y_of(iH, pH, mode="orth", V=Rt); Yr[n] = rr if wpos else -rr
        yv = float(Yv.mean()); yr = float(Yr.mean())
        nec = (yH - yv) / denom if denom != 0 else float("nan")
        ptv = per_t(Yv); bd_rng = np.random.default_rng(SEED); bd = np.empty(BOOT)
        for bi in range(BOOT):
            pk = bd_rng.integers(0, NTMPL, NTMPL)
            num = np.nanmean(ptH[pk]) - np.nanmean(ptv[pk]); den = np.nanmean(ptH[pk]) - np.nanmean(ptU[pk])
            bd[bi] = num / den if den != 0 else np.nan
        return {"necessity": nec, "necessity_ci": [float(np.nanpercentile(bd, 2.5)), float(np.nanpercentile(bd, 97.5))],
                "Y_Hperp": yv, "Y_Hperp_rand": yr, "rand_move": abs(yr - yH), "dynrange_ok": bool(abs(yr - yH) < DYNRANGE_BAR),
                "mass_v": float(Mv.mean()), "coherence_ok": bool(float(Mv.mean()) >= MASS_FLOOR)}

    results = {}; infos = {}; k_stops = {}; angles = {}
    top_outcome = None
    if not gconstruct_ok:
        top_outcome = f"VOID-CONSTRUCT ({gconstruct}/{N})"
    elif not anchor_ok:
        top_outcome = f"ANCHOR-FAIL (Y(U)={yU:+.3f}/Y(H)={yH:+.3f} want {ANCHOR_U}/{ANCHOR_H} +-{ANCHOR_TOL})"
    else:
        for mode in ("P1", "P2", "P3"):
            decod, info = deflate(X, tr, te, ylab, mode); infos[mode] = info
            kstar = next((j + 1 for j, a in enumerate(decod) if a <= DEFLATE_STOP_ACC), None)
            censored = kstar is None; k_stop = kstar if kstar else len(decod); k_stops[mode] = k_stop
            decod_killed = (not censored) and decod[k_stop - 1] <= DEFLATE_STOP_ACC
            nec = necessity_at(info, k_stop)
            entry = {"kstar": kstar, "censored": censored, "k_stop": k_stop, "decod_final": decod[-1],
                     "decod_killed": bool(decod_killed), "decodability": decod, **nec}
            if mode == "P1":
                nec25 = necessity_at(info, min(25, k_stop))
                entry["necessity_k25"] = nec25["necessity"]; entry["k25_used"] = min(25, k_stop)
            results[mode] = {"info_type": info["type"], **entry}
            log(f"[HR] {mode} kstar={kstar} censored={censored} decod_final={decod[-1]:.3f} killed={decod_killed} "
                f"nec@stop={nec['necessity']:+.3f}{nec['necessity_ci']} randmove={nec['rand_move']:.3f} "
                f"dyn={nec['dynrange_ok']} coh={nec['coherence_ok']}")
        # principal angles (deg) between raw-coords removed subspaces at each P's k_stop; report full spectrum
        def ang(a, b):
            kk = min(a.shape[1], b.shape[1])
            s = np.linalg.svd(a[:, :kk].T @ b[:, :kk], compute_uv=False)
            return [round(float(x), 2) for x in np.degrees(np.arccos(np.clip(s, -1, 1)))]
        rb = {m: removed_raw_basis(infos[m], k_stops[m]) for m in ("P1", "P2", "P3")}
        angles = {"P1_vs_P2": ang(rb["P1"], rb["P2"]), "P1_vs_P3": ang(rb["P1"], rb["P3"]),
                  "P2_vs_P3": ang(rb["P2"], rb["P3"])}
        log(f"[HR] principal-angles(deg) P1vP2={angles['P1_vs_P2']}")
        log(f"[HR] principal-angles(deg) P1vP3={angles['P1_vs_P3']}")

    # ---- REPRODUCTION + top-level outcome ----
    repro_ok = None
    if results:
        repro_val = results["P1"].get("necessity_k25")
        repro_ok = abs(repro_val - REPRO_TARGET_K25) <= REPRO_TOL if repro_val is not None else None

    if top_outcome is None:
        valid = {m: r for m, r in results.items() if r["decod_killed"] and r["dynrange_ok"] and r["coherence_ok"]}
        if repro_ok is False:
            top_outcome = f"REPRODUCTION-FAIL (P1 necessity@25={results['P1'].get('necessity_k25'):+.4f} vs PRV-01h {REPRO_TARGET_K25:+.4f}, |diff|>{REPRO_TOL})"
        elif len(valid) == 3 and all(abs(r["necessity"]) < 0.15 for r in valid.values()):
            top_outcome = "ROBUST-EXISTENTIAL (necessity <0.15 with decodability KILLED and controls passing in all 3 parameterizations)"
        elif len([m for m in results if results[m]["decod_killed"]]) == 0:
            top_outcome = f"DECODABILITY-NOT-KILLED (no parameterization reached chance by cap {DEFLATE_CAP}; existential-with-kill not established; report per-P decodability floors)"
        elif len(valid) >= 2 and max(abs(r["necessity"]) for r in valid.values()) - min(abs(r["necessity"]) for r in valid.values()) > 0.15:
            top_outcome = "PARAMETERIZATION-DEPENDENT (necessity differs materially across valid parameterizations; state per-P; empirical instance of 2608.10566)"
        else:
            top_outcome = "MIXED (per-parameterization gate outcomes differ; no pooled headline; see per-P table)"

    out = {"prereg": "PREREG_PRV01HR.md", "probe": "PRV-01h-r", "SMOKE": SMOKE, "model_id": MODEL_ID,
           "chained_to_PRV01H": "fdd4b552c3be0bfb1da50e46773ed4d27b58d25cbb703181a9a493993f2ef075",
           "transformers": transformers.__version__, "n": N, "num_layers": NL, "gconstruct_identical": gconstruct,
           "Y_U": yU, "Y_H": yH, "denom": denom, "anchor_ok": anchor_ok, "anchor_want": [ANCHOR_U, ANCHOR_H],
           "deflate_cap": DEFLATE_CAP, "reproduction_target_k25": REPRO_TARGET_K25, "reproduction_ok": repro_ok,
           "principal_angles_deg": angles, "per_parameterization": results, "outcome": top_outcome,
           "runtime_s": round(time.time() - t0, 1)}
    fn = os.path.join(OUT, "prv01hr" + ("_smoke" if SMOKE else "") + ".json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[HR] G-CONSTRUCT {gconstruct}/{N} anchor={anchor_ok} repro_ok={repro_ok}")
    log(f"[HR] OUTCOME: {top_outcome}")
    log(f"[HR] wrote {fn}")


if __name__ == "__main__":
    main()
