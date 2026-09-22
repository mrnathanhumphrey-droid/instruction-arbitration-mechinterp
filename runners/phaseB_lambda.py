#!/usr/bin/env python
# PRV-03 PHASE B -- self-contained Lambda runner (PREREG_PRV03.md sha 1e5ad707...d3f0).
# Subspace intervention at L8 (WEAK@L8 from Phase A). Build subspace by ITERATIVE DEFLATION
# (fit w, deflate perp, refit; stop refit P_e>=0.45, cap k=25 -> deflation curve is a result).
# Intervention = full-subspace SWAP by projection EXCHANGE: shift each span's subspace projection
# by the pool class-mean difference restricted to the subspace (sys -delta_vec, usr +delta_vec).
# Control = random k-dim subspace, projection-norm matched, same exchange. Manip = SANITY ONLY.
# M = -(dYw - dYc)/(2B), paired template-cluster bootstrap, single site (alpha=0.05, 2.5/97.5).
# Uploaded alongside: prompts.jsonl, setup.json, stimuli_contested.jsonl, make_stimuli.py.
import os, json, time
import numpy as np, torch
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
LAYER = 8
DONE, READY = 71496, 46678
NTMPL = 30
KCAP = 5 if SMOKE else 25
PE_STOP = 0.45
BOOT = 300 if SMOKE else 5000
SEED = 20260914

def log(*a): print(*a, flush=True)

def main():
    t0 = time.time()
    prompts = [json.loads(l) for l in open(os.path.join(HERE, "prompts.jsonl"), encoding="utf-8")]
    setup = json.load(open(os.path.join(HERE, "setup.json"), encoding="utf-8"))
    train_ids = set(setup["split_manifest"]["train_span_ids"])
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_contested.jsonl"), encoding="utf-8")]
    if SMOKE: stim = stim[:60]
    from make_stimuli import TEMPLATES
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import transformers
    log(f"[B] model on {dev}; tf {transformers.__version__} ({time.time()-t0:.0f}s); L{LAYER} kcap={KCAP}")

    # ---- pool residuals at L8 (per-token, span content) ----
    reps = []; role_all = []; split_all = []
    with torch.inference_mode():
        for pi, p in enumerate(prompts):
            ids = torch.tensor([p["input_ids", dtype=torch.long, device=dev)
            lo, hi = p["span_content_token_range"]
            hs = model(input_ids=ids, output_hidden_states=True, use_cache=False).hidden_states[LAYER]
            reps.append(hs[0, lo:hi, :].float().cpu().numpy())
            n = hi - lo
            role_all.append(np.full(n, 1 if p["role"] == "trusted" else 0, np.int8))
            split_all.append(np.full(n, 1 if p["span_id"] in train_ids else 0, np.int8))
            if (pi + 1) % 200 == 0: log(f"[B] pool {pi+1}/{len(prompts)} ({time.time()-t0:.0f}s)")
    Xr = np.concatenate(reps, 0).astype(np.float32); del reps
    role = np.concatenate(role_all); split = np.concatenate(split_all)
    tr, te = split == 1, split == 0

    # ---- iterative deflation subspace ----
    basis = []; pe_curve = []; clf1 = sc1 = None
    Xdef = Xr.copy()
    for i in range(KCAP + 1):
        sc = StandardScaler().fit(Xdef[tr])
        clf = LogisticRegression(C=1.0, max_iter=300, solver="lbfgs").fit(sc.transform(Xdef[tr]), role[tr])
        pe = 1.0 - float(clf.score(sc.transform(Xdef[te]), role[te]))
        pe_curve.append(pe)
        log(f"[B] deflate step {i}: refit P_e={pe:.4f} (k so far={len(basis)})")
        if i == 0: clf1, sc1 = clf, sc          # original L8 probe (for sanity manip-check)
        if pe >= PE_STOP or len(basis) >= KCAP:
            break
        scale = sc.scale_.copy(); scale[~np.isfinite(scale) | (scale == 0)] = 1.0
        w = clf.coef_[0] / scale
        for b in basis: w = w - (w @ b) * b     # Gram-Schmidt vs existing basis
        nw = np.linalg.norm(w)
        if nw < 1e-8: log("[B] deflation direction degenerate; stop"); break
        w = w / nw; basis.append(w)
        Xdef = Xr.copy()                          # re-deflate from raw against full basis (stable)
        Bm = np.array(basis).T                     # (4096,k)
        Xdef = Xr - (Xr @ Bm) @ Bm.T
    k = len(basis)
    B = np.array(basis).T                          # (4096, k) orthonormal
    log(f"[B] subspace k={k}; deflation curve {[round(x,3) for x in pe_curve]}")

    # class-mean difference restricted to the subspace -> swap vector (raw space)
    diff = Xr[role == 1].mean(0) - Xr[role == 0].mean(0)         # system - user
    delta_vec = B @ (B.T @ diff)                                  # (4096,) in span(B)
    dnorm = float(np.linalg.norm(delta_vec))
    # control: random k-dim orthonormal subspace, projection-norm matched, same exchange
    rng = np.random.default_rng(SEED)
    G = rng.standard_normal((4096, k)).astype(np.float32)
    Bctrl, _ = np.linalg.qr(G)                                    # (4096,k) orthonormal
    dvec_ctrl = Bctrl @ (Bctrl.T @ diff)
    dvec_ctrl = dvec_ctrl * (dnorm / (np.linalg.norm(dvec_ctrl) + 1e-12))
    log(f"[B] |delta_vec|={dnorm:.4f} (needle Delta was ~0.179); control matched norm")
    del Xr, Xdef

    # ---- intervention ----
    tmpl_idx = np.array([it["template_idx"] for it in stim])
    STEER = {"ops": None, "cap": None}
    def hook(mod, inp, out):
        h = out[0] if isinstance(out, tuple) else out
        if STEER["ops"]:
            for pos, vec in STEER["ops"]: h[0, pos, :] += vec
        if STEER["cap"] is not None:
            for nm, pos in STEER["cap"]["spans"].items():
                STEER["cap"]["reps"][nm] = h[0, pos, :].float().mean(0).detach().cpu().numpy()
        return out
    def run(ids, ops, cap=None):
        STEER["ops"] = ops; STEER["cap"] = cap
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lg = model(input_ids=t, use_cache=False).logits[0, -1, :].float()
        STEER["ops"] = None; STEER["cap"] = None
        lp = torch.log_softmax(lg, -1); return float(lp[DONE] - lp[READY])
    def locate(it):
        imp_s = TEMPLATES[it["template_idx".format(T=it["target_sys"])
        imp_u = TEMPLATES[it["template_idx".format(T=it["target_usr"])
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False); offs = enc["offset_mapping"]
        def sp(imp):
            cs = text.index(imp); ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        return enc["input_ids"], sp(imp_s), sp(imp_u)
    lay = [locate(it) for it in stim]
    def ysig(R, it): return R if it["target_sys"] == "DONE" else -R

    dv = torch.tensor(delta_vec, dtype=torch.bfloat16, device=dev)
    dvc = torch.tensor(dvec_ctrl, dtype=torch.bfloat16, device=dev)
    smean, sscale, wstd, bint = sc1.mean_.astype(np.float32), sc1.scale_.astype(np.float32), clf1.coef_[0].astype(np.float32), float(clf1.intercept_[0])
    def pred(rep):
        z = (rep - smean) / sscale
        return 1 if (z @ wstd + bint) > 0 else 0

    hh = model.model.layers[LAYER - 1].register_forward_hook(hook)
    # self-check: exchange must move the L8 probe classification of both spans
    ids0, ss0, su0 = lay[0]
    cap = {"spans": {"s": ss0, "u": su0}, "reps": {}}
    run(ids0, [(ss0, -dv), (su0, dv)], cap=cap)
    if not (pred(cap["reps"]["s"]) == 0 and pred(cap["reps"]["u"]) == 1):
        hh.remove(); raise SystemExit("SELFCHECK FAILED: subspace exchange did not flip probe")
    log("[B] SELFCHECK ok")
    hh.remove()

    Ybase = np.array([ysig(run(ids, None), it) for (ids, _, _), it in zip(lay, stim)])
    Bmean = float(Ybase.mean()); log(f"[B] baseline B={Bmean:+.4f} ({time.time()-t0:.0f}s)")

    hh = model.model.layers[LAYER - 1].register_forward_hook(hook)
    Yw = np.zeros(len(stim)); Yc = np.zeros(len(stim)); msf = []; muf = []
    for i, ((ids, ss, su), it) in enumerate(zip(lay, stim)):
        cap = {"spans": {"s": ss, "u": su}, "reps": {}}
        Yw[i] = ysig(run(ids, [(ss, -dv), (su, dv)], cap=cap), it)
        msf.append(pred(cap["reps"]["s"]) == 0); muf.append(pred(cap["reps"]["u"]) == 1)
        Yc[i] = ysig(run(ids, [(ss, -dvc), (su, dvc)]), it)
        if (i + 1) % 120 == 0: log(f"[B] {i+1}/{len(stim)} ({time.time()-t0:.0f}s)")
    hh.remove()

    def per_t(a): return np.array([a[tmpl_idx == t].mean() for t in range(NTMPL)])
    ptB = per_t(Ybase); dYw = Yw - Ybase; dYc = Yc - Ybase; ptw = per_t(dYw); ptc = per_t(dYc)
    M = float(-(ptw.mean() - ptc.mean()) / (2 * ptB.mean()))
    rng2 = np.random.default_rng(SEED); Ms = np.empty(BOOT)
    for b in range(BOOT):
        pk = rng2.integers(0, NTMPL, NTMPL)
        Ms[b] = -(ptw[pk].mean() - ptc[pk].mean()) / (2 * ptB[pk].mean())
    lo, hi = np.percentile(Ms, [2.5, 97.5]); excl0 = bool(lo > 0 or hi < 0)
    verdict = "USES-VIA-SUBSPACE" if (abs(M) >= 0.10 and excl0) else \
              ("SUBSPACE-PARTIAL" if excl0 else "RESIDUAL-STREAM-CLOSED->H3(attention)")
    out = {"prereg_sha256": "1e5ad707514b4902d73004d0bcae44b99a2ea8b995888192e0a41105cc71d3f0",
           "SMOKE": SMOKE, "layer": LAYER, "k": k, "deflation_pe_curve": pe_curve,
           "delta_vec_norm": dnorm, "B": Bmean, "transformers": transformers.__version__,
           "dYw": float(dYw.mean()), "dYc": float(dYc.mean()),
           "M_subspace": M, "ci95": [float(lo), float(hi)], "ci_excl0": excl0,
           "M_needle_L8_phaseA": -0.02841810344926437,
           "manip_sanity_sys2usr": float(np.mean(msf)), "manip_sanity_usr2sys": float(np.mean(muf)),
           "manip_note": "SANITY ONLY, zero inferential weight (projection set by construction)",
           "verdict": verdict, "runtime_s": round(time.time() - t0, 1)}
    fn = os.path.join(OUT, "prv03_phaseB_smoke.json" if SMOKE else "prv03_phaseB.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[B] k={k} M_subspace={M:+.5f} CI[{lo:+.5f},{hi:+.5f}] vs needle -0.0284 -> {verdict}; wrote {fn}")

if __name__ == "__main__":
    main()
