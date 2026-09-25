#!/usr/bin/env python
# PRV-01h -- is the provenance INFORMATION necessary, or only the single direction? Llama-3.1-8B-Instruct.
# PREREG_PRV01H.md, chained PRV-01g. Subspace ablation by ITERATIVE DEFLATION (INLP-style): fit v_k -> project out -> refit,
# accumulate the linearly-decodable provenance subspace, then project the whole subspace out of the resistant condition H at
# every layer and ask whether the header's +2.386 nats survive.
#
# PRV-01g showed the single direction v_hat is not INDIVIDUALLY necessary -- expected under redundant coding whether or not the
# info is causal (removing 1 axis of ~4096 spares a redundant code). This removes the code IN FULL (to decodability chance).
#
# Controls carry the run: random-rank-k projection at every k (redrawn per item), and G-DYNAMIC-RANGE PER k -- find the k where
# random-rank-k stops being inert (< 0.597 nats), that is the ceiling on interpretable depth; do NOT read deflation past it.
# REPRODUCTION gate: necessity(k=1) must reproduce PRV-01g's 0.009 within +-0.01, else pipeline drift -> stop.
# k* is a DEFLATION DEPTH, never a dimension (binding, per 2608.10566); censored-at-25 if capped.
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
MASS_FLOOR = 0.10; DYNRANGE_BAR = 0.5965935601749355          # 0.25 * denom(2.386), from PRV-01g (fixed, comparable)
DEFLATE_STOP_ACC = 0.55; DEFLATE_CAP = 25                     # stop when held-out acc <= 0.55; cap 25
REPRO_TARGET = 0.00931539611234836; REPRO_TOL = 0.01         # PRV-01g necessity(k=1)
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


def main():
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_tool_contested_true_false.jsonl"), encoding="utf-8")]
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    POS = stim[0]["readout_pos"]; NEG = stim[0]["readout_neg"]
    TPOS = tok(POS, add_special_tokens=False)["input_ids"][0]; TNEG = tok(NEG, add_special_tokens=False)["input_ids"][0]
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16, device_map={"": 0}).eval()
    dev = next(model.parameters()).device; import transformers
    NL = model.config.num_hidden_layers; D = model.config.hidden_size
    log(f"[H1] {MODEL_ID} on {dev}; tf {transformers.__version__} NL={NL} D={D} n={len(stim)} readout={POS}/{NEG} ({time.time()-t0:.0f}s)")

    # ---- subspace-projection hook on every layer: h[:,pos,:] -= (h@V)@V.T  (V orthonormal [D,k]) ----
    pst = {"active": False, "pos": None, "V": None}
    def make_hook(idx):
        def hook(module, inp, out):
            if not pst["active"]:
                return out
            hs = out[0] if isinstance(out, tuple) else out
            p = pst["pos"]; V = pst["V"]
            sub = hs[:, p, :]
            hs[:, p, :] = sub - (sub @ V) @ V.t()
            return (hs,) + tuple(out[1:]) if isinstance(out, tuple) else hs
        return hook
    for layer in model.model.layers:
        layer.register_forward_hook(make_hook(0))

    def Y_of(ids, V=None, pos=None, want_hidden=False):
        pst.update(active=(V is not None), pos=pos, V=V)
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            o = model(input_ids=t, use_cache=False, output_hidden_states=want_hidden)
            lp = torch.log_softmax(o.logits[0, -1, :].float(), -1)
            h1 = o.hidden_states[1][0, pos, :].float().cpu().numpy() if want_hidden else None
        pst["active"] = False
        R = float(lp[TPOS] - lp[TNEG]); M = float(torch.exp(lp[TPOS]) + torch.exp(lp[TNEG]))
        return (R, M, h1) if want_hidden else (R, M)

    use = list(range(0, len(stim), len(stim) // 40))[:40] if SMOKE else list(range(len(stim)))
    N = len(use); tmpl = np.array([stim[i]["template_idx"] for i in use])
    tgt_pos = np.array([1 if stim[i]["target_sys"] == POS else 0 for i in use])

    # ============ PASS 1: clean Y(U), Y(H); collect L1 content reps for deflation =================================
    YU = np.zeros(N); YH = np.zeros(N); MU = np.zeros(N); MH = np.zeros(N)
    ids_cache = [None] * N; span_cache = [None] * N; gconstruct = 0
    X = []; ylab = []; item_of = []; pos0 = []
    for n, i in enumerate(use):
        it = stim[i]; wpos = it["target_sys"] == POS
        tU, tH = render_raw(tok, it)
        iU = tok(tU, add_special_tokens=False)["input_ids"]; iH = tok(tH, add_special_tokens=False)["input_ids"]
        eU, pU = content_span(iU); eH, pH = content_span(iH)
        if iU[eU + 1:] == iH[eH + 1:]: gconstruct += 1
        ids_cache[n] = (iU, iH); span_cache[n] = (pU, pH)
        ru, mu, h1u = Y_of(iU, pos=pU, want_hidden=True); YU[n] = ru if wpos else -ru; MU[n] = mu
        rh, mh, h1h = Y_of(iH, pos=pH, want_hidden=True); YH[n] = rh if wpos else -rh; MH[n] = mh
        keep = list(range(min(CAP_POS, len(pU))))
        for pi in keep:
            X.append(h1u[pi]); ylab.append(0); item_of.append(n); pos0.append(1 if pi == 0 else 0)
            X.append(h1h[pi]); ylab.append(1); item_of.append(n); pos0.append(1 if pi == 0 else 0)
        if (n + 1) % 120 == 0: log(f"[H1] pass1 {n+1}/{N} ({time.time()-t0:.0f}s)")
    X = np.array(X, dtype=np.float32); ylab = np.array(ylab); item_of = np.array(item_of)
    yU = float(YU.mean()); yH = float(YH.mean()); denom = yH - yU
    anchor_ok = abs(yU - ANCHOR_U) <= ANCHOR_TOL and abs(yH - ANCHOR_H) <= ANCHOR_TOL
    gconstruct_ok = gconstruct == N
    log(f"[H1] PASS1 Y(U)={yU:+.3f} Y(H)={yH:+.3f} denom={denom:+.3f} anchor={anchor_ok} X={X.shape}")

    # ============ DEFLATION (CPU): INLP -- fit on train items, held-out acc = decodability, project out, refit ======
    rng = np.random.default_rng(SEED)
    perm = rng.permutation(N); tr_items = set(perm[:N // 2].tolist())
    tr = np.array([it_ in tr_items for it_ in item_of]); te = ~tr
    Xd = X.copy(); basis = []; decod = []
    for k in range(1, DEFLATE_CAP + 1):
        sc = StandardScaler().fit(Xd[tr]); clf = LogisticRegression(C=1.0, max_iter=200).fit(sc.transform(Xd[tr]), ylab[tr])
        acc = float((clf.predict(sc.transform(Xd[te])) == ylab[te]).mean()); decod.append(acc)
        w = clf.coef_[0] / sc.scale_; w = (w / np.linalg.norm(w)).astype(np.float32)
        basis.append(w)
        Xd = Xd - np.outer(Xd @ w, w)     # project w out of all reps
        if acc <= DEFLATE_STOP_ACC:
            break
    basis = np.stack(basis, axis=1)       # [D, K]
    K = basis.shape[1]
    kstar = next((j + 1 for j, a in enumerate(decod) if a <= DEFLATE_STOP_ACC), None)
    kstar_censored = kstar is None
    ksweep_max = min(kstar if kstar else DEFLATE_CAP, DEFLATE_CAP)
    log(f"[H1] DEFLATION K={K} decod={['%.3f'%a for a in decod]} kstar={kstar} censored={kstar_censored}")

    # ============ PASS 2: necessity(k) = [Y(H)-Y(H_perp_{Vk})]/denom vs random-rank-k floor; per-k G-DYNAMIC-RANGE ===
    def per_t(x): return np.array([x[tmpl == t].mean() if (tmpl == t).any() else np.nan for t in range(NTMPL)])
    ptH = per_t(YH); ptU = per_t(YU); bd_rng = np.random.default_rng(SEED)
    curve = {}; range_limit = None; mass_limit = None
    result_stop = None
    if not gconstruct_ok:
        result_stop = f"VOID-CONSTRUCT ({gconstruct}/{N})"
    elif not anchor_ok:
        result_stop = f"ANCHOR-FAIL (Y(U)={yU:+.3f} want {ANCHOR_U}, Y(H)={yH:+.3f} want {ANCHOR_H}; +-{ANCHOR_TOL})"
    if result_stop is None:
        # per-item random orthonormal set (redrawn per item), computed ONCE and sliced first-k across the k-loop
        Rcache = [np.linalg.qr(np.random.default_rng(SEED + 1000 + n).standard_normal((D, DEFLATE_CAP)).astype(np.float32))[0]
                  for n in range(N)]
        for k in range(1, ksweep_max + 1):
            Vk = np.linalg.qr(basis[:, :k])[0].astype(np.float32)          # orthonormal [D,k]
            Vk_t = torch.tensor(Vk, dtype=torch.bfloat16, device=dev)
            Yv = np.zeros(N); Yr = np.zeros(N); Mv = np.zeros(N); Mr = np.zeros(N)
            for n, i in enumerate(use):
                it = stim[i]; wpos = it["target_sys"] == POS
                (iU, iH) = ids_cache[n]; (pU, pH) = span_cache[n]
                Rk_t = torch.tensor(np.ascontiguousarray(Rcache[n][:, :k]), dtype=torch.bfloat16, device=dev)
                rv, mv = Y_of(iH, V=Vk_t, pos=pH); Yv[n] = rv if wpos else -rv; Mv[n] = mv
                rr, mr = Y_of(iH, V=Rk_t, pos=pH); Yr[n] = rr if wpos else -rr; Mr[n] = mr
            yv = float(Yv.mean()); yr = float(Yr.mean())
            nec = (yH - yv) / denom if denom != 0 else float("nan")
            rand_move = abs(yr - yH)
            ptv = per_t(Yv); bd = np.empty(BOOT)
            for bi in range(BOOT):
                pk = bd_rng.integers(0, NTMPL, NTMPL)
                num = np.nanmean(ptH[pk]) - np.nanmean(ptv[pk]); den = np.nanmean(ptH[pk]) - np.nanmean(ptU[pk])
                bd[bi] = num / den if den != 0 else np.nan
            nec_ci = [float(np.nanpercentile(bd, 2.5)), float(np.nanpercentile(bd, 97.5))]
            dyn_ok = rand_move < DYNRANGE_BAR; coh_ok = float(Mv.mean()) >= MASS_FLOOR
            curve[str(k)] = {"necessity": nec, "necessity_ci": nec_ci, "Y_Hperp_v": yv, "Y_Hperp_rand": yr,
                             "rand_move": rand_move, "dynrange_ok": dyn_ok, "mass_v": float(Mv.mean()),
                             "mass_rand": float(Mr.mean()), "coherence_ok": coh_ok, "decodability": decod[k - 1] if k <= len(decod) else None}
            log(f"[H1] k={k} nec={nec:+.3f}{nec_ci} randmove={rand_move:.3f}(<{DYNRANGE_BAR:.3f}?{dyn_ok}) "
                f"decod={decod[k-1] if k<=len(decod) else None} mass_v={float(Mv.mean()):.2f}")
            if not coh_ok and mass_limit is None: mass_limit = k
            if not dyn_ok:
                range_limit = k; break

    # ---- REPRODUCTION gate + outcome ----
    repro_ok = None; repro_val = None
    if result_stop is None and "1" in curve:
        repro_val = curve["1"]["necessity"]; repro_ok = abs(repro_val - REPRO_TARGET) <= REPRO_TOL
    interpretable = [int(k) for k in curve if curve[k]["dynrange_ok"] and curve[k]["coherence_ok"]]
    k_report = max(interpretable) if interpretable else None
    if result_stop is not None:
        outcome = result_stop
    elif repro_ok is False:
        outcome = f"REPRODUCTION-FAIL (necessity(k=1)={repro_val:+.4f} vs PRV-01g {REPRO_TARGET:.4f}, |diff|>{REPRO_TOL}; pipeline drift)"
    elif k_report is None:
        outcome = "DEPTH-LIMITED (no k with a passing dynamic-range+coherence gate; not even k=1 interpretable)"
    else:
        nec_r = curve[str(k_report)]["necessity"]
        bound = (range_limit is not None or mass_limit is not None) and (kstar is None or k_report < kstar)
        tag = " [BOUND, depth-limited before k*]" if bound else ""
        if bound and nec_r < 0.50:
            outcome = (f"DEPTH-LIMITED (max interpretable k={k_report}, necessity there={nec_r:+.3f} as a BOUND; "
                       f"range_limit={range_limit} mass_limit={mass_limit} kstar={kstar}{' censored@25' if kstar_censored else ''})")
        elif nec_r >= 0.50:
            outcome = f"INFORMATION-NECESSARY (necessity={nec_r:+.3f} at k={k_report}{tag}: the provenance code carries the resistance; PRV-01g's null was a single-axis artifact of redundant coding)"
        elif nec_r >= 0.15:
            outcome = f"PARTIALLY-NECESSARY (necessity={nec_r:+.3f} at k={k_report}{tag}: the code carries some; something else carries the rest)"
        else:
            outcome = f"INFORMATION-NOT-NECESSARY (necessity={nec_r:+.3f} at k={k_report}{tag} < 0.15: resistance routes around the ENTIRE linearly-decodable provenance code; carried non-linearly or by something this probe family cannot see)"

    np.save(os.path.join(OUT, "prv01h_basis" + ("_smoke" if SMOKE else "") + ".npy"), basis)
    np.savez(os.path.join(OUT, "prv01h_peritem" + ("_smoke" if SMOKE else "") + ".npz"),
             use=np.array(use), tmpl=tmpl, tgt_pos=tgt_pos, YU=YU, YH=YH, MU=MU, MH=MH, decod=np.array(decod))
    out = {"prereg": "PREREG_PRV01H.md", "probe": "PRV-01h", "SMOKE": SMOKE, "model_id": MODEL_ID,
           "chained_to_PRV01G": "d815b111dee33c45917848677bdacebecf6a8b55e4b4659582d3e87185ab9d5c",
           "transformers": transformers.__version__, "n": N, "readout": [POS, NEG], "num_layers": NL,
           "gconstruct_identical": gconstruct, "Y_U": yU, "Y_H": yH, "denom": denom, "anchor_ok": anchor_ok,
           "anchor_want": [ANCHOR_U, ANCHOR_H], "mass_U": float(MU.mean()), "mass_H": float(MH.mean()),
           "decodability": decod, "kstar_deflation_depth": kstar, "kstar_censored_at_25": kstar_censored,
           "dynrange_bar": DYNRANGE_BAR, "range_limit_k": range_limit, "mass_limit_k": mass_limit,
           "reproduction_target": REPRO_TARGET, "reproduction_k1": repro_val, "reproduction_ok": repro_ok,
           "k_report": k_report, "necessity_curve": curve, "outcome": outcome, "runtime_s": round(time.time() - t0, 1)}
    fn = os.path.join(OUT, "prv01h" + ("_smoke" if SMOKE else "") + ".json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[H1] G-CONSTRUCT {gconstruct}/{N} | kstar={kstar}(censored={kstar_censored}) k_report={k_report} repro_ok={repro_ok}")
    log(f"[H1] OUTCOME: {outcome}")
    log(f"[H1] wrote {fn}")


if __name__ == "__main__":
    main()
