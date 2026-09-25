#!/usr/bin/env python
# PRV-01d -- is the encoded ROLE DIRECTION the pathway to the resistance the header produces? Llama-3.1-8B-Instruct.
# PREREG_PRV01D.md, chained PRV-01f. CAUSAL: refit v_hat in the RAW contrast, patch alpha*v_hat at L1 across the
# injected content span of a bare (user-role) injection, measure how far Y moves toward the ipython-role level.
#
# Withdrawal context (2026-09-23): the "encoded-but-unused" dissociation is WITHDRAWN. In the RAW (un-serialized) condition
# the header moves Y by +2.47 nats (TOOL-02 2x2: user+raw -3.2 vs ipython+raw -0.73). So the header IS used, and the sharp
# causal question is whether the direction PRV-01e reads is the PATHWAY by which the header does what it already does.
#
# Arms: U(raw/user, Y~-3.2) | H(raw/ipython=markeronly, Y~-0.73, THE TARGET) | U+v(a) | U+v(-a) | U+r(a norm-matched).
# closure(a) = [Y(U+v(a)) - Y(U)] / [Y(H) - Y(U)],  denom ~ +2.47 measured in-run.
# Direction v_hat refit HERE in the raw contrast (PRV-01e's v_hat was fit with tojson present = off-distribution). PERSIST v_hat.
# ANCHOR: Y(U) and Y(H) are LEVELS (reproduce -3.2 / -0.73 within +-0.30). denom is a CONTRAST.
import os, json, time
import numpy as np, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
NTMPL = 30; BOOT = 300 if SMOKE else 5000; SEED = 20260923
IPY_HDR = "<|start_header_id|>ipython<|end_header_id|>"; USR_HDR = "<|start_header_id|>user<|end_header_id|>"
EOH = 128007; EOT = 128009
PATCH_L = 0          # add to the OUTPUT of decoder layer index 0 == the L1 residual (hidden_states[1])
CAP_POS = 64         # cap content-span positions used for the FIT at d<=64 (the certified range); patch uses full span
ALPHAS = [0.25, 0.5, 1.0, 2.0]                 # ||patch|| / mean L1 residual norm
ANCHOR_U = -3.2; ANCHOR_H = -0.73; ANCHOR_TOL = 0.30   # LEVELS (TOOL-02 raw row)
MASS_FLOOR = 0.10; NULL_FRAC = 0.25; SIGN_FRAC = 0.25   # G-NULL-DIRECTION / G-SIGN thresholds
def log(*a): print(*a, flush=True)


def base3(it):
    return [{"role": "system", "content": it["system"]},
            {"role": "user", "content": it["user_trigger"]},
            {"role": "assistant", "content": it["assistant_stub"]}]


def render_raw(tok, it):
    # U = plain user turn carrying the RAW injection text (TOOL-02 render_user, unpadded). H = U with the INJECTION turn's
    # header (only) swapped to ipython. USR_HDR occurs twice (trigger turn + injection turn) -> swap the LAST occurrence
    # only, else the user_trigger turn would also flip. Byte-identical post-header (guarantees G-CONSTRUCT + L0 chance).
    m = base3(it) + [{"role": "user", "content": it["tool_text"]}]
    textU = tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True)
    idx = textU.rfind(USR_HDR)
    textH = textU[:idx] + IPY_HDR + textU[idx + len(USR_HDR):]
    return textU, textH


def content_span(ids):
    # injected turn's header-end is the SECOND-TO-LAST EOH (last is the empty assistant generation prompt).
    e = [k for k, t in enumerate(ids) if t == EOH][-2]
    eot = [k for k, t in enumerate(ids) if t == EOT and k > e][0]
    return e, list(range(e + 1, eot))   # header_end index, content-token positions


def main():
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_tool_contested_true_false.jsonl"), encoding="utf-8")]
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    POS = stim[0]["readout_pos"]; NEG = stim[0]["readout_neg"]
    TPOS = tok(POS, add_special_tokens=False)["input_ids"][0]; TNEG = tok(NEG, add_special_tokens=False)["input_ids"][0]
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16, device_map={"": 0}).eval()
    dev = next(model.parameters()).device; import transformers
    log(f"[D1] {MODEL_ID} on {dev}; tf {transformers.__version__} n={len(stim)} readout={POS}/{NEG} ({time.time()-t0:.0f}s)")

    # ---- patch hook on decoder layer PATCH_L: adds patch_state['vec'] at patch_state['pos'] to that layer's output ----
    patch_state = {"active": False, "pos": None, "vec": None}
    def hook(module, inp, out):
        if not patch_state["active"]:
            return out
        hs = out[0] if isinstance(out, tuple) else out
        hs[:, patch_state["pos"], :] = hs[:, patch_state["pos"], :] + patch_state["vec"]
        return (hs,) + tuple(out[1:]) if isinstance(out, tuple) else hs
    model.model.layers[PATCH_L].register_forward_hook(hook)

    def Y_of(ids, pos=None, vec=None):
        patch_state.update(active=(vec is not None), pos=pos, vec=vec)
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lg = model(input_ids=t, use_cache=False).logits[0, -1, :].float()
        patch_state["active"] = False
        lp = torch.log_softmax(lg, -1)
        R = float(lp[TPOS] - lp[TNEG]); M = float(torch.exp(lp[TPOS]) + torch.exp(lp[TNEG]))
        return R, M

    def hidden_at(ids, pos):
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            o = model(input_ids=t, use_cache=False, output_hidden_states=True)
        h0 = o.hidden_states[0][0, pos, :].float().cpu().numpy()          # L0 (embeddings)
        h1 = o.hidden_states[PATCH_L + 1][0, pos, :].float().cpu().numpy()  # L1
        R = float(torch.log_softmax(o.logits[0, -1, :].float(), -1)[TPOS]
                  - torch.log_softmax(o.logits[0, -1, :].float(), -1)[TNEG])
        lp = torch.log_softmax(o.logits[0, -1, :].float(), -1)
        M = float(torch.exp(lp[TPOS]) + torch.exp(lp[TNEG]))
        return h0, h1, R, M

    use = list(range(0, len(stim), len(stim) // 40))[:40] if SMOKE else list(range(len(stim)))
    N = len(use); tmpl = np.array([stim[i]["template_idx"] for i in use])
    tgt_pos = np.array([1 if stim[i]["target_sys"] == POS else 0 for i in use])

    # ---- PASS 1: fit forwards (U,H) -> collect L0/L1 content vecs, clean Y(U)/Y(H), residual norms, spans ----
    X0 = []; X1 = []; ylab = []; item_of = []; pos_ord = []   # pooled content vectors for the probe fit
    YU = np.zeros(N); YH = np.zeros(N); MU = np.zeros(N); MH = np.zeros(N)
    spans = [None] * N; gconstruct = 0; resid_norms = []
    for n, i in enumerate(use):
        it = stim[i]; wpos = it["target_sys"] == POS
        tU, tH = render_raw(tok, it)
        iU = tok(tU, add_special_tokens=False)["input_ids"]; iH = tok(tH, add_special_tokens=False)["input_ids"]
        eU, pU = content_span(iU); eH, pH = content_span(iH)
        if iU[eU + 1:] == iH[eH + 1:]: gconstruct += 1        # post-header byte-identical
        spans[n] = pU
        h0U, h1U, rU, mU = hidden_at(iU, pU); h0H, h1H, rH, mH = hidden_at(iH, pH)
        YU[n] = rU if wpos else -rU; MU[n] = mU
        YH[n] = rH if wpos else -rH; MH[n] = mH
        resid_norms.append(np.linalg.norm(h1U, axis=1))       # L1 residual norms at U content positions
        keep = list(range(min(CAP_POS, len(pU))))
        for pi in keep:
            X0.append(h0U[pi]); X1.append(h1U[pi]); ylab.append(0); item_of.append(n); pos_ord.append(pi)
            X0.append(h0H[pi]); X1.append(h1H[pi]); ylab.append(1); item_of.append(n); pos_ord.append(pi)
        if (n + 1) % 120 == 0: log(f"[D1] fit-pass {n+1}/{N} ({time.time()-t0:.0f}s)")
    X0 = np.array(X0); X1 = np.array(X1); ylab = np.array(ylab)
    item_of = np.array(item_of); pos_ord = np.array(pos_ord)
    mean_resid_norm = float(np.mean(np.concatenate(resid_norms)))

    # ---- fit the probe: item-held-out split for G-VALIDITY/G0; FULL fit -> v_hat (persisted) ----
    rng = np.random.default_rng(SEED)
    perm = rng.permutation(N); tr_items = set(perm[:N // 2].tolist())
    tr = np.array([it_ in tr_items for it_ in item_of]); te = ~tr
    def fit_acc(X):
        sc = StandardScaler().fit(X[tr]); clf = LogisticRegression(C=1.0, max_iter=500).fit(sc.transform(X[tr]), ylab[tr])
        acc = float((clf.predict(sc.transform(X[te])) == ylab[te]).mean())
        d1 = (pos_ord == 0)
        acc_d1 = float((clf.predict(sc.transform(X[te & d1])) == ylab[te & d1]).mean()) if (te & d1).any() else float("nan")
        return acc, acc_d1
    G0_acc, _ = fit_acc(X0)                    # L0 -> chance by construction
    GVAL_acc, GVAL_d1 = fit_acc(X1)            # L1 -> should separate
    scF = StandardScaler().fit(X1); clfF = LogisticRegression(C=1.0, max_iter=500).fit(scF.transform(X1), ylab)
    w_raw = clfF.coef_[0] / scF.scale_; v_hat = (w_raw / np.linalg.norm(w_raw)).astype(np.float32)  # raw L1 space, ->ipython
    np.save(os.path.join(OUT, "prv01d_vhat" + ("_smoke" if SMOKE else "") + ".npy"), v_hat)
    log(f"[D1] FIT G0(L0)={G0_acc:.3f} G-VALIDITY(L1)={GVAL_acc:.3f} d1={GVAL_d1:.3f} mean_resid_norm={mean_resid_norm:.2f}")

    vt = torch.tensor(v_hat, dtype=torch.bfloat16, device=dev)

    # ---- PASS 2: patched arms. U+v(a), U+v(-a), U+r(a) at each alpha. r redrawn per item, norm-matched. ----
    Yv = {a: np.zeros(N) for a in ALPHAS}; Yvn = {a: np.zeros(N) for a in ALPHAS}; Yr = {a: np.zeros(N) for a in ALPHAS}
    Mv = {a: np.zeros(N) for a in ALPHAS}
    rr = np.random.default_rng(SEED + 1)
    for n, i in enumerate(use):
        it = stim[i]; wpos = it["target_sys"] == POS
        tU, _ = render_raw(tok, it); iU = tok(tU, add_special_tokens=False)["input_ids"]; pos = spans[n]
        rvec = rr.standard_normal(v_hat.shape[0]).astype(np.float32); rvec /= np.linalg.norm(rvec)
        rt = torch.tensor(rvec, dtype=torch.bfloat16, device=dev)
        for a in ALPHAS:
            c = a * mean_resid_norm
            rp, mp = Y_of(iU, pos, vt * c); Yv[a][n] = rp if wpos else -rp; Mv[a][n] = mp
            rn, _ = Y_of(iU, pos, vt * (-c)); Yvn[a][n] = rn if wpos else -rn
            rq, _ = Y_of(iU, pos, rt * c); Yr[a][n] = rq if wpos else -rq
        if (n + 1) % 120 == 0: log(f"[D1] patch-pass {n+1}/{N} ({time.time()-t0:.0f}s)")

    # ---- closure + gates ----
    yU = float(YU.mean()); yH = float(YH.mean()); denom = yH - yU
    def per_t(x): return np.array([x[tmpl == t].mean() if (tmpl == t).any() else np.nan for t in range(NTMPL)])
    ptU = per_t(YU); ptH = per_t(YH); bd_rng = np.random.default_rng(SEED)
    res = {}
    for a in ALPHAS:
        eff_v = float((Yv[a] - YU).mean()); eff_vn = float((Yvn[a] - YU).mean()); eff_r = float((Yr[a] - YU).mean())
        clo = eff_v / denom if denom != 0 else float("nan")
        # bootstrap closure over templates
        ptv = per_t(Yv[a]); bd = np.empty(BOOT)
        for bi in range(BOOT):
            pk = bd_rng.integers(0, NTMPL, NTMPL)
            num = np.nanmean(ptv[pk]) - np.nanmean(ptU[pk]); den = np.nanmean(ptH[pk]) - np.nanmean(ptU[pk])
            bd[bi] = num / den if den != 0 else np.nan
        clo_ci = [float(np.nanpercentile(bd, 2.5)), float(np.nanpercentile(bd, 97.5))]
        g_null = abs(eff_r) < NULL_FRAC * abs(eff_v) if eff_v != 0 else False
        g_sign = not (np.sign(eff_vn) == np.sign(eff_v) and abs(eff_vn) > SIGN_FRAC * abs(eff_v))
        g_coh = float(Mv[a].mean()) >= MASS_FLOOR
        # counterbalance split of the v-effect
        def spl(m): return float((Yv[a][m] - YU[m]).mean())
        res[str(a)] = {"eff_v": eff_v, "eff_vneg": eff_vn, "eff_rand": eff_r, "closure": clo, "closure_ci": clo_ci,
                       "mass_v": float(Mv[a].mean()), "g_null_direction": bool(g_null), "g_sign": bool(g_sign),
                       "g_coherence": bool(g_coh), "passes_controls": bool(g_null and g_sign and g_coh),
                       "closure_sysTRUE": spl(tgt_pos == 1), "closure_sysFALSE": spl(tgt_pos == 0)}

    anchor_ok = abs(yU - ANCHOR_U) <= ANCHOR_TOL and abs(yH - ANCHOR_H) <= ANCHOR_TOL
    gconstruct_ok = gconstruct == N
    fit_ok = (G0_acc <= 0.55) and (GVAL_acc >= 0.80)
    passing = [a for a in ALPHAS if res[str(a)]["passes_controls"]]
    if not gconstruct_ok:
        outcome = f"VOID-CONSTRUCT ({gconstruct}/{N} post-header identical)"
    elif not anchor_ok:
        outcome = f"ANCHOR-FAIL (Y(U)={yU:+.3f} want {ANCHOR_U}, Y(H)={yH:+.3f} want {ANCHOR_H}; +-{ANCHOR_TOL})"
    elif not fit_ok:
        outcome = f"FIT-FAIL (G0={G0_acc:.3f} must <=0.55, G-VALIDITY={GVAL_acc:.3f} must >=0.80)"
    elif not passing:
        outcome = "NOT-THE-PATHWAY (controls fail at every alpha; the direction does not carry the effect cleanly)"
    else:
        amax = max(passing); clo = res[str(amax)]["closure"]
        if clo >= 0.50:
            outcome = f"PATHWAY (closure={clo:.2f} at alpha={amax}: the direction PRV-01e reads is causally connected to the header's resistance)"
        elif clo >= 0.15:
            outcome = f"PARTIAL-PATHWAY (closure={clo:.2f} at alpha={amax}: the direction carries some of the effect, something else carries the rest)"
        else:
            outcome = f"NOT-THE-PATHWAY (closure={clo:.2f} at alpha={amax} < 0.15: header effect routes elsewhere; readable direction is a correlate)"

    np.savez(os.path.join(OUT, "prv01d_peritem" + ("_smoke" if SMOKE else "") + ".npz"),
             use=np.array(use), tmpl=tmpl, tgt_pos=tgt_pos, YU=YU, YH=YH, MU=MU, MH=MH,
             **{f"Yv_{a}": Yv[a] for a in ALPHAS}, **{f"Yvn_{a}": Yvn[a] for a in ALPHAS},
             **{f"Yr_{a}": Yr[a] for a in ALPHAS}, **{f"Mv_{a}": Mv[a] for a in ALPHAS})
    out = {"prereg": "PREREG_PRV01D.md", "probe": "PRV-01d", "SMOKE": SMOKE, "model_id": MODEL_ID,
           "chained_to_PRV01F": "0ba39250c77dd6ebad211558bd765542c44d160ca7da03b632f7752f3e3a07c4",
           "transformers": transformers.__version__, "n": N, "readout": [POS, NEG],
           "gconstruct_identical": gconstruct, "anchor_ok": anchor_ok, "Y_U": yU, "Y_H": yH, "denom": denom,
           "anchor_want": [ANCHOR_U, ANCHOR_H], "G0_L0_acc": G0_acc, "G_VALIDITY_L1_acc": GVAL_acc,
           "G_VALIDITY_d1_acc": GVAL_d1, "fit_ok": fit_ok, "mean_resid_norm": mean_resid_norm,
           "mass_U": float(MU.mean()), "mass_H": float(MH.mean()), "alphas": ALPHAS, "by_alpha": res,
           "passing_alphas": [float(a) for a in passing], "outcome": outcome, "runtime_s": round(time.time() - t0, 1)}
    fn = os.path.join(OUT, "prv01d" + ("_smoke" if SMOKE else "") + ".json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[D1] G-CONSTRUCT {gconstruct}/{N} | Y(U)={yU:+.3f} Y(H)={yH:+.3f} denom={denom:+.3f} | "
        f"G0={G0_acc:.3f} GVAL={GVAL_acc:.3f}")
    for a in ALPHAS:
        r = res[str(a)]
        log(f"[D1] a={a}: closure={r['closure']:+.3f}{r['closure_ci']} eff_v={r['eff_v']:+.3f} "
            f"rand={r['eff_rand']:+.3f} neg={r['eff_vneg']:+.3f} mass={r['mass_v']:.2f} "
            f"null={r['g_null_direction']} sign={r['g_sign']} coh={r['g_coherence']}")
    log(f"[D1] OUTCOME: {outcome}")
    log(f"[D1] wrote {fn}")


if __name__ == "__main__":
    main()
