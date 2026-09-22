#!/usr/bin/env python
# H4 -- downstream re-derivation control ("all-layers, all-positions swap"). Self-contained Lambda runner.
# PREREG_H4.md (sha folded at lock). Six the lead researcher rulings folded:
#  0. POSITION SET = the FULL role block (headers+markers+content) at every layer, both system & user
#     blocks -- so layer L's attention can only read already-swapped L-1 residuals; in-context source gone.
#  1. LAYER RANGE = L8->L31 contiguous (primary). [L1->L31 is a conditional 2nd arm, run offline only if
#     primary is FLAT -- NOT in this script; pre-registered so a null can't be waved off as "too late".]
#  2. Per-layer subspace refit (own geometry) + PRINCIPAL ANGLES between consecutive bases (H3/H4 discriminator).
#  3. k per layer via held-out P_e>=0.45 stop, cap 25 -> k-vs-layer curve is a free 2nd dimensionality result.
#  4. Verdict cuts RE-SET: REAL |M|>=0.20 & CI excl0 ; PARTIAL 0.05<=|M|<0.20 & CI excl0 ; EPIPHENOMENAL else.
#  5. Sanity = plumbing (zero inferential weight) + VOID GUARD: steered uncontested floor-compliance rate
#     < 0.90 * unsteered voids the arm (guards against lobotomizing the model and calling flat-M a finding).
# Swap = projection-EXCHANGE (additive class-mean-diff restricted to per-layer subspace): system -Delta_L,
# user +Delta_L, applied to EVERY position in each role block, at EVERY layer. Control = per-layer random
# k_L-dim orthonormal subspace, projection-norm matched, same all-position all-layer exchange.
# M = -(dYw - dYc)/(2B); Y=logP(DONE)-logP(READY) @ first assistant token, Y_signed counterbalanced.
# Whole-ratio paired template-cluster bootstrap (30 templates). Uploaded alongside: prompts.jsonl, setup.json,
# stimuli_contested.jsonl, stimuli_uncontested.jsonl, make_stimuli.py.
import os, json, time
import numpy as np, torch
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
LAYERS = list(range(8, 32))            # L8..L31 inclusive, contiguous (ruling 1)
DONE, READY = 71496, 46678
NTMPL = 30
KCAP = 5 if SMOKE else 25
PE_STOP = 0.45
BOOT = 300 if SMOKE else 5000
SEED = 20260914
# Llama-3.1 special tokens for role-block segmentation (ruling 0)
SH, EOT = 128006, 128009               # <|start_header_id|>, <|eot_id|>
FLOOR_STRIDE = 12 if SMOKE else 6      # subsample uncontested for the floor VOID guard

def log(*a): print(*a, flush=True)

def build_subspace(Xr, role, tr, te, kcap, pe_stop):
    """Iterative deflation subspace + held-out P_e curve. Returns (B[4096,k], k, curve, clf0, sc0).
    v3 RE-LOCK (2026-09-15, the lead researcher "full 80k. Not 20k"): LR fit + scaler on the FULL train split (tr) —
    IDENTICAL to Phase B in every way (pool, deflation, k, stop). Only the LAYER SPAN differs from Phase B.
    This is the only configuration under which M~+0.22 vs Phase B's +0.010 can carry the 'instrument
    limitation' claim. ACCEPTANCE (pre-committed): L8 curve must reproduce Phase B P_e->~0.398 @ k=25; M read
    against locked tiers (>=0.20 REAL / 0.05-0.20 PARTIAL / <0.05 or CI-incl EPIPHENOMENAL); NO third run."""
    basis = []; curve = []; clf0 = sc0 = None
    Xdef = Xr.copy()
    for i in range(kcap + 1):
        sc = StandardScaler().fit(Xdef[tr])
        clf = LogisticRegression(C=1.0, max_iter=300, solver="lbfgs").fit(sc.transform(Xdef[tr]), role[tr])
        pe = 1.0 - float(clf.score(sc.transform(Xdef[te]), role[te])); curve.append(pe)
        if i == 0: clf0, sc0 = clf, sc
        if pe >= pe_stop or len(basis) >= kcap: break
        scale = sc.scale_.copy(); scale[~np.isfinite(scale) | (scale == 0)] = 1.0
        w = clf.coef_[0] / scale
        for b in basis: w = w - (w @ b) * b
        nw = np.linalg.norm(w)
        if nw < 1e-8: break
        w = w / nw; basis.append(w)
        Bm = np.array(basis).T; Xdef = Xr - (Xr @ Bm) @ Bm.T
    B = np.array(basis).T if basis else np.zeros((Xr.shape[1], 0), np.float32)
    return B.astype(np.float32), len(basis), curve, clf0, sc0

def main():
    t0 = time.time()
    prompts = [json.loads(l) for l in open(os.path.join(HERE, "prompts.jsonl"), encoding="utf-8")]
    setup = json.load(open(os.path.join(HERE, "setup.json"), encoding="utf-8"))
    train_ids = set(setup["split_manifest"]["train_span_ids"])
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_contested.jsonl"), encoding="utf-8")]
    unc = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_uncontested.jsonl"), encoding="utf-8")]
    if SMOKE: stim = stim[:60]; prompts = prompts[:120]   # SMOKE: subsample pool too so the gate is FAST
    unc = unc[::FLOOR_STRIDE]
    from make_stimuli import TEMPLATES
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import transformers
    log(f"[H4] model on {dev}; tf {transformers.__version__} ({time.time()-t0:.0f}s); "
        f"L{LAYERS[0]}..L{LAYERS[-1]} ({len(LAYERS)} sites) kcap={KCAP} n_stim={len(stim)} n_floor={len(unc)}")

    # ---- pool residuals at ALL target layers (single pass), span-content tokens ----
    per_layer_reps = {L: [] for L in LAYERS}; role_all = []; split_all = []
    with torch.inference_mode():
        for pi, p in enumerate(prompts):
            ids = torch.tensor([p["input_ids", dtype=torch.long, device=dev)
            lo, hi = p["span_content_token_range"]
            hs = model(input_ids=ids, output_hidden_states=True, use_cache=False).hidden_states
            for L in LAYERS:
                per_layer_reps[L].append(hs[L][0, lo:hi, :].float().cpu().numpy())
            n = hi - lo
            role_all.append(np.full(n, 1 if p["role"] == "trusted" else 0, np.int8))
            split_all.append(np.full(n, 1 if p["span_id"] in train_ids else 0, np.int8))
            if (pi + 1) % 200 == 0: log(f"[H4] pool {pi+1}/{len(prompts)} ({time.time()-t0:.0f}s)")
    role = np.concatenate(role_all); split = np.concatenate(split_all)
    tr, te = split == 1, split == 0
    # v3: FULL train-split fit, identical to Phase B (only layer span differs)
    log(f"[H4] pooled; tokens={len(role)} train={int(tr.sum())} test={int(te.sum())} "
        f"(FULL-fit, Phase-B-identical) ({time.time()-t0:.0f}s)")

    # ---- per-layer subspace + swap vector + matched control ----
    rng = np.random.default_rng(SEED)
    Bases = {}; k_vec = {}; curves = {}; dvecs = {}; dvecs_ctrl = {}; dnorms = {}; probe0 = {}
    for L in LAYERS:
        Xr = np.concatenate(per_layer_reps[L], 0).astype(np.float32); per_layer_reps[L] = None
        B, k, curve, clf0, sc0 = build_subspace(Xr, role, tr, te, KCAP, PE_STOP)
        Bases[L] = B; k_vec[L] = k; curves[L] = curve; probe0[L] = (clf0, sc0)
        if k == 0:
            dvecs[L] = np.zeros(Xr.shape[1], np.float32); dvecs_ctrl[L] = dvecs[L]; dnorms[L] = 0.0
            log(f"[H4] L{L}: k=0 (no subspace) -- layer contributes nothing"); del Xr; continue
        diff = Xr[role == 1].mean(0) - Xr[role == 0].mean(0)     # system - user
        dv = B @ (B.T @ diff); dn = float(np.linalg.norm(dv))
        G = rng.standard_normal((Xr.shape[1], k)).astype(np.float32)
        Bc, _ = np.linalg.qr(G)
        dvc = Bc @ (Bc.T @ diff); dvc = dvc * (dn / (np.linalg.norm(dvc) + 1e-12))
        dvecs[L] = dv.astype(np.float32); dvecs_ctrl[L] = dvc.astype(np.float32); dnorms[L] = dn
        log(f"[H4] L{L}: k={k} P_e[0]={curve[0]:.3f} P_e[-1]={curve[-1]:.3f} |dv|={dn:.4f}")
        del Xr

    # ---- principal angles between consecutive layers' bases (ruling 2) ----
    pang = {}
    for a, b in zip(LAYERS[:-1], LAYERS[1:]):
        Ba, Bb = Bases[a], Bases[b]
        if Ba.shape[1] == 0 or Bb.shape[1] == 0: pang[f"{a}-{b}"] = None; continue
        sv = np.linalg.svd(Ba.T @ Bb, compute_uv=False)     # singular values = cos(principal angles)
        sv = np.clip(sv, 0.0, 1.0)
        pang[f"{a}-{b}"] = {"cos_mean": float(sv.mean()), "cos_min": float(sv.min()),
                            "cos": [round(float(x), 4) for x in sv]}

    # ---- device tensors for the swap ----
    dv_t = {L: torch.tensor(dvecs[L], dtype=torch.bfloat16, device=dev) for L in LAYERS}
    dvc_t = {L: torch.tensor(dvecs_ctrl[L], dtype=torch.bfloat16, device=dev) for L in LAYERS}

    # ---- role-block segmentation via special tokens (ruling 0) ----
    def blocks_and_imp(it):
        imp_s = TEMPLATES[it["template_idx".format(T=it["target_sys"]) if it.get("target_sys") else None
        imp_u = TEMPLATES[it["template_idx".format(T=it["target_usr"]) if it.get("target_usr") else None
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]
        sh = [i for i, t in enumerate(ids) if t == SH]; eot = [i for i, t in enumerate(ids) if t == EOT]
        # sh[0]=system hdr, eot[0]=end system ; sh[1]=user hdr, eot[1]=end user ; sh[2]=assistant hdr
        sys_block = list(range(sh[0], eot[0] + 1))
        usr_block = list(range(sh[1], eot[1] + 1))
        def span(imp):
            if imp is None: return []
            cs = text.index(imp); ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        return ids, sys_block, usr_block, span(imp_s), span(imp_u)

    # ---- all-layer all-position hooks ----
    STATE = {"mode": None, "sys": None, "usr": None, "cap31": None}
    handles = []
    def make_hook(L):
        dv, dvc = dv_t[L], dvc_t[L]
        is31 = (L == LAYERS[-1])
        def hook(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            m = STATE["mode"]
            if m and (dv.abs().sum() > 0):
                vec = dv if m == "treat" else dvc
                if STATE["sys"]: h[0, STATE["sys"], :] += (-vec)
                if STATE["usr"]: h[0, STATE["usr"], :] += (vec)
            if is31 and STATE["cap31"] is not None:
                cap = STATE["cap31"]
                for nm, pos in cap["spans"].items():
                    if pos: cap["reps"][nm] = h[0, pos, :].float().mean(0).detach().cpu().numpy()
            return out
        return hook
    for L in LAYERS:
        handles.append(model.model.layers[L - 1].register_forward_hook(make_hook(L)))

    def run(ids, mode, sysb=None, usrb=None, cap31=None):
        STATE["mode"], STATE["sys"], STATE["usr"], STATE["cap31"] = mode, sysb, usrb, cap31
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lg = model(input_ids=t, use_cache=False).logits[0, -1, :].float()
        STATE["mode"] = STATE["sys"] = STATE["usr"] = STATE["cap31"] = None
        lp = torch.log_softmax(lg, -1); return float(lp[DONE] - lp[READY])

    # L31 probe (deflation step0) for the plumbing sanity check
    clf31, sc31 = probe0[LAYERS[-1
    def pred31(rep):
        z = (rep - sc31.mean_.astype(np.float32)) / sc31.scale_.astype(np.float32)
        return 1 if (z @ clf31.coef_[0].astype(np.float32) + float(clf31.intercept_[0])) > 0 else 0

    lay = [blocks_and_imp(it) for it in stim]
    def ysig(R, it): return R if it["target_sys"] == "DONE" else -R

    # ---- SELF-CHECK: all-layer treat must move item0 AND (plumbing) flip the L31 content probe both spans
    ids0, sb0, ub0, si0, ui0 = lay[0]
    y_base0 = run(ids0, None)
    cap = {"spans": {"s": si0, "u": ui0}, "reps": {}}
    y_tr0 = run(ids0, "treat", sb0, ub0, cap31=cap)
    if abs(y_tr0 - y_base0) < 1e-4:
        for h in handles: h.remove()
        raise SystemExit(f"SELFCHECK FAILED: all-layer treat did not move Y (base {y_base0:.4f} treat {y_tr0:.4f})")
    if si0 and ui0 and not (pred31(cap["reps"]["s"]) == 0 and pred31(cap["reps"]["u"]) == 1):
        for h in handles: h.remove()
        raise SystemExit("SELFCHECK FAILED: L31 content probe did not flip under all-layer swap")
    log(f"[H4] SELFCHECK ok (item0 base {y_base0:+.4f} -> treat {y_tr0:+.4f})")

    # ---- baseline B ----
    Ybase = np.array([ysig(run(ids, None), it) for (ids, sb, ub, si, ui), it in zip(lay, stim)])
    Bmean = float(Ybase.mean()); log(f"[H4] baseline B={Bmean:+.4f} ({time.time()-t0:.0f}s)")

    # ---- contested intervention (treat + control), + L31 plumbing tally ----
    Yw = np.zeros(len(stim)); Yc = np.zeros(len(stim)); p31s = []; p31u = []
    tmpl_idx = np.array([it["template_idx"] for it in stim])
    for i, ((ids, sb, ub, si, ui), it) in enumerate(zip(lay, stim)):
        cap = {"spans": {"s": si, "u": ui}, "reps": {}} if (i % 20 == 0) else None
        Yw[i] = ysig(run(ids, "treat", sb, ub, cap31=cap), it)
        Yc[i] = ysig(run(ids, "ctrl", sb, ub), it)
        if cap is not None and si and ui:
            p31s.append(pred31(cap["reps"]["s"]) == 0); p31u.append(pred31(cap["reps"]["u"]) == 1)
        if (i + 1) % 120 == 0: log(f"[H4] contested {i+1}/{len(stim)} ({time.time()-t0:.0f}s)")

    # ---- floor VOID guard (ruling 5): uncontested compliance rate, unsteered vs steered arms ----
    def comply_rate(mode):
        ok = 0
        for it in unc:
            ids, sb, ub, _, _ = blocks_and_imp(it)
            r = run(ids, mode, sb, ub) if mode else run(ids, None)
            ok += 1 if r > 0 else 0      # uncontested target=DONE, so logP(DONE)-logP(READY)>0 == complies
        return ok / max(1, len(unc))
    floor_uns = comply_rate(None)
    floor_tr = comply_rate("treat")
    floor_ct = comply_rate("ctrl")
    for h in handles: h.remove()
    thresh = 0.90 * floor_uns
    void_treat = bool(floor_tr < thresh); void_ctrl = bool(floor_ct < thresh)
    VOID = bool(void_treat or void_ctrl)
    log(f"[H4] floor: unsteered {floor_uns:.3f} treat {floor_tr:.3f} ctrl {floor_ct:.3f} thr {thresh:.3f} VOID={VOID}")

    # ---- M + paired template-cluster bootstrap ----
    def per_t(a): return np.array([a[tmpl_idx == t].mean() for t in range(NTMPL)])
    ptB = per_t(Ybase); dYw = Yw - Ybase; dYc = Yc - Ybase; ptw = per_t(dYw); ptc = per_t(dYc)
    M = float(-(ptw.mean() - ptc.mean()) / (2 * ptB.mean()))
    rng2 = np.random.default_rng(SEED); Ms = np.empty(BOOT)
    for b in range(BOOT):
        pk = rng2.integers(0, NTMPL, NTMPL)
        Ms[b] = -(ptw[pk].mean() - ptc[pk].mean()) / (2 * ptB[pk].mean())
    lo, hi = np.percentile(Ms, [2.5, 97.5]); excl0 = bool(lo > 0 or hi < 0)

    if VOID:
        verdict = "VOID (model damaged: steered floor-compliance < 0.90*unsteered) -- NOT a null"
    elif abs(M) >= 0.20 and excl0:
        verdict = "RESIDUAL-PATH-REAL (single-layer was the wrong knife; PRV-02/03 nulls = instrument limit)"
    elif 0.05 <= abs(M) < 0.20 and excl0:
        verdict = "PARTIAL (residual carries some, not most, of the path)"
    else:
        verdict = "RESIDUAL-EPIPHENOMENAL (H3 strengthened by eliminating its best competitor -> PRV-04)"

    out = {"prereg": "PREREG_H4.md", "SMOKE": SMOKE, "layers": LAYERS, "n_stim": len(stim),
           "transformers": transformers.__version__,
           "lr_fit": "FULL train split (Phase-B-identical; only layer span differs)",
           "train_tokens": int(tr.sum()),
           "L8_curve_vs_phaseB_note": "ACCEPTANCE GATE: deflation_pe_curves['8'] must reproduce Phase B ~0.398 @ k=25",
           "k_per_layer": {str(L): k_vec[L] for L in LAYERS},
           "deflation_pe_curves": {str(L): [round(x, 4) for x in curves[L for L in LAYERS},
           "delta_norms": {str(L): round(dnorms[L], 4) for L in LAYERS},
           "principal_angles_consecutive": pang,
           "B": Bmean, "dYw": float(dYw.mean()), "dYc": float(dYc.mean()),
           "M": M, "ci95": [float(lo), float(hi)], "ci_excl0": excl0,
           "floor_unsteered_rate": floor_uns, "floor_treat_rate": floor_tr, "floor_ctrl_rate": floor_ct,
           "void_threshold": thresh, "void_treat": void_treat, "void_ctrl": void_ctrl, "VOID": VOID,
           "L31_probe_sanity_sys2usr": float(np.mean(p31s)) if p31s else None,
           "L31_probe_sanity_usr2sys": float(np.mean(p31u)) if p31u else None,
           "sanity_note": "L31 probe flip is TAUTOLOGICAL (L31 edited) -- plumbing only, zero inferential weight",
           "verdict": verdict, "runtime_s": round(time.time() - t0, 1)}
    fn = os.path.join(OUT, "h4_smoke.json" if SMOKE else "h4.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[H4] M={M:+.5f} CI[{lo:+.5f},{hi:+.5f}] excl0={excl0} VOID={VOID} -> {verdict}; wrote {fn}")

if __name__ == "__main__":
    main()
