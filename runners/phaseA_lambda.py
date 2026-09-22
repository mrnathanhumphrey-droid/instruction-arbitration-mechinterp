#!/usr/bin/env python
# PRV-03 PHASE A -- self-contained Lambda runner (PREREG_PRV03.md sha 1e5ad707...d3f0).
# Layer sweep {4,8,12,16,24,31}: extract PRV-01c pool reps -> per-layer w-hat refit + P_e curve ->
# contested SWAP intervention per layer -> M_L (paired template bootstrap, Bonferroni a=0.05/6) ->
# 3-tier verdict. Uploaded alongside: prompts.jsonl, setup.json, stimuli_contested.jsonl.
# ENV: HF_TOKEN, OUTDIR (default .), SMOKE=1 (fast self-test: L16 only, 60 stimuli, small boot).
import os, json, time, sys
import numpy as np, torch
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
LAYERS = [16] if SMOKE else [4, 8, 12, 16, 24, 31]
DONE, READY = 71496, 46678
TRUNC = 2048
NTMPL = 30
BOOT = 300 if SMOKE else 5000
FAMILY = 6                          # Bonferroni family size (locked layer set)
ALPHA = 0.05 / FAMILY
PCT = [100 * ALPHA / 2, 100 * (1 - ALPHA / 2)]   # 0.417 / 99.583
SEED = 20260914

def log(*a): print(*a, flush=True)

def main():
    t0 = time.time()
    prompts = [json.loads(l) for l in open(os.path.join(HERE, "prompts.jsonl"), encoding="utf-8")]
    setup = json.load(open(os.path.join(HERE, "setup.json"), encoding="utf-8"))
    train_ids = set(setup["split_manifest"]["train_span_ids"])
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_contested.jsonl"), encoding="utf-8")]
    if SMOKE:
        stim = stim[:60]
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import transformers
    log(f"[A] model on {dev}; torch {torch.__version__} tf {transformers.__version__} ({time.time()-t0:.0f}s); layers={LAYERS}")

    # ---- 1. extract PRV-01c pool per-token residuals at all LAYERS (one fwd/prompt) ----
    resid = {L: [] for L in LAYERS}; role_all = []; split_all = []
    with torch.inference_mode():
        for pi, p in enumerate(prompts):
            ids = torch.tensor([p["input_ids", dtype=torch.long, device=dev)
            lo, hi = p["span_content_token_range"]
            hs = model(input_ids=ids, output_hidden_states=True, use_cache=False).hidden_states
            n = hi - lo
            for L in LAYERS:
                resid[L].append(hs[L][0, lo:hi, :].float().cpu().numpy())
            role_all.append(np.full(n, 1 if p["role"] == "trusted" else 0, np.int8))
            split_all.append(np.full(n, 1 if p["span_id"] in train_ids else 0, np.int8))
            if (pi + 1) % 200 == 0:
                log(f"[A] pool extract {pi+1}/{len(prompts)} ({time.time()-t0:.0f}s)")
    role = np.concatenate(role_all); split = np.concatenate(split_all)
    tr, te = split == 1, split == 0

    # ---- 2. per-layer probe refit -> P_e, w_raw, delta, control v ----
    W = {}; curve = {}
    rng = np.random.default_rng(SEED)
    for L in LAYERS:
        X = np.concatenate(resid[L], 0).astype(np.float32)
        sc = StandardScaler().fit(X[tr])
        clf = LogisticRegression(C=1.0, max_iter=300, solver="lbfgs").fit(sc.transform(X[tr]), role[tr])
        P_e = 1.0 - float(clf.score(sc.transform(X[te]), role[te]))
        scale = sc.scale_.copy(); scale[~np.isfinite(scale) | (scale == 0)] = 1.0
        w_raw = clf.coef_[0] / scale; w_raw /= np.linalg.norm(w_raw)
        proj = X @ w_raw
        delta = float(proj[role == 1].mean() - proj[role == 0].mean())
        if delta < 0:                       # orient +w = system/trusted
            w_raw = -w_raw; delta = -delta; proj = -proj
        sd = float(proj.std())
        # variance-matched control: perp to w, unit-norm, pool-proj SD closest to w's
        best = None
        for _ in range(64):
            v = rng.standard_normal(4096).astype(np.float32); v -= (v @ w_raw) * w_raw; v /= np.linalg.norm(v)
            sdv = float((X @ v).std())
            if best is None or abs(sdv - sd) < abs(best[2] - sd): best = (v, None, sdv)
        v_raw = best[0]; sdv = best[2]
        W[L] = {"w": w_raw, "delta": delta, "sc_mean": sc.mean_.astype(np.float32),
                "sc_scale": sc.scale_.astype(np.float32), "w_std": clf.coef_[0].astype(np.float32),
                "b": float(clf.intercept_[0]), "v": v_raw}
        curve[L] = {"P_e": P_e, "delta": delta, "sd_proj": sd, "sd_proj_ctrl": sdv}
        log(f"[A] L{L}: P_e={P_e:.4f} delta={delta:+.4f} ctrlSD={sdv:.4f}/{sd:.4f}")
    del resid

    # ---- 3. contested intervention ----
    tmpl_idx = np.array([it["template_idx"] for it in stim])
    from make_stimuli import TEMPLATES   # exact frozen imperatives (uploaded alongside)

    STEER = {"ops": None, "cap": None}
    def hook(mod, inp, out):
        h = out[0] if isinstance(out, tuple) else out
        if STEER["ops"]:
            for pos, vec in STEER["ops"]:
                h[0, pos, :] += vec
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
        lp = torch.log_softmax(lg, -1)
        return float(lp[DONE] - lp[READY])

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

    # self-check on first item at first layer
    L0 = LAYERS[0]
    hh = model.model.layers[L0 - 1].register_forward_hook(hook)
    ids0, ss0, su0 = lay[0]; w0 = W[L0]["w"]; d0 = W[L0]["delta"]
    wt = torch.tensor(w0, dtype=torch.bfloat16, device=dev)
    cap = {"spans": {"s": ss0, "u": su0}, "reps": {}}; run(ids0, None, cap=cap)
    b_s = cap["reps"]["s"] @ w0; b_u = cap["reps"]["u"] @ w0
    cap = {"spans": {"s": ss0, "u": su0}, "reps": {}}
    run(ids0, [(ss0, (-d0) * wt), (su0, (d0) * wt)], cap=cap)
    if not ((cap["reps"]["s"] @ w0 - b_s) < -0.5 * d0 and (cap["reps"]["u"] @ w0 - b_u) > 0.5 * d0):
        hh.remove(); raise SystemExit("SELFCHECK FAILED: hook did not move projection")
    log(f"[A] SELFCHECK ok (L{L0})")
    hh.remove()

    # baseline once (layer-independent)
    Ybase = np.array([ysig(run(ids, None), it) for (ids, _, _), it in zip(lay, stim)])
    B = float(Ybase.mean())
    log(f"[A] baseline B={B:+.4f} ({time.time()-t0:.0f}s)")

    def per_t(a): return np.array([a[tmpl_idx == t].mean() for t in range(NTMPL)])
    ptB = per_t(Ybase)
    results = {}
    for L in LAYERS:
        hh = model.model.layers[L - 1].register_forward_hook(hook)
        w = W[L]["w"]; d = W[L]["delta"]; v = W[L]["v"]
        wt = torch.tensor(w, dtype=torch.bfloat16, device=dev); vt = torch.tensor(v, dtype=torch.bfloat16, device=dev)
        sm, ss_, ws, bb = W[L]["sc_mean"], W[L]["sc_scale"], W[L]["w_std"], W[L]["b"]
        def pred(rep):
            z = (rep - sm) / ss_
            return 1 if (z @ ws + bb) > 0 else 0
        Yw = np.zeros(len(stim)); Yc = np.zeros(len(stim)); msf = []; muf = []
        for i, ((ids, sp_s, sp_u), it) in enumerate(zip(lay, stim)):
            cap = {"spans": {"s": sp_s, "u": sp_u}, "reps": {}}
            Yw[i] = ysig(run(ids, [(sp_s, (-d) * wt), (sp_u, (d) * wt)], cap=cap), it)
            msf.append(pred(cap["reps"]["s"]) == 0); muf.append(pred(cap["reps"]["u"]) == 1)
            Yc[i] = ysig(run(ids, [(sp_s, (-d) * vt), (sp_u, (d) * vt)]), it)
        hh.remove()
        dYw = Yw - Ybase; dYc = Yc - Ybase
        ptw = per_t(dYw); ptc = per_t(dYc)
        M = float(-(ptw.mean() - ptc.mean()) / (2 * ptB.mean()))
        Ms = np.empty(BOOT); rng2 = np.random.default_rng(SEED)
        for b in range(BOOT):
            pk = rng2.integers(0, NTMPL, NTMPL)
            Ms[b] = -(ptw[pk].mean() - ptc[pk].mean()) / (2 * ptB[pk].mean())
        lo, hi = np.percentile(Ms, PCT)
        excl0 = bool(lo > 0 or hi < 0)
        msr = float(np.mean(msf)); mur = float(np.mean(muf))
        aM = abs(M)
        tier = ("LOCALIZED" if (aM >= 0.10 and excl0) else
                "WEAK" if (aM >= 0.02 and excl0) else "FLAT")
        results[f"L{L}"] = {"M": M, "ci_bonf": [float(lo), float(hi)], "ci_excl0": excl0,
                            "dYw": float(dYw.mean()), "dYc": float(dYc.mean()),
                            "manip_sys2usr": msr, "manip_usr2sys": mur, "manip_ok": bool(msr >= .8 and mur >= .8),
                            "tier": tier, "P_e": curve[L]["P_e"], "delta": curve[L]["delta"]}
        log(f"[A] L{L}: M={M:+.5f} CI[{lo:+.5f},{hi:+.5f}] excl0={excl0} tier={tier} manip {msr:.2f}/{mur:.2f}")

    localized = [L for L in LAYERS if results[f"L{L}"]["tier"] == "LOCALIZED"]
    weak = [L for L in LAYERS if results[f"L{L}"]["tier"] == "WEAK"]
    out = {"prereg_sha256": "1e5ad707514b4902d73004d0bcae44b99a2ea8b995888192e0a41105cc71d3f0",
           "SMOKE": SMOKE, "layers": LAYERS, "alpha_bonferroni": ALPHA, "B": B,
           "torch": torch.__version__, "transformers": transformers.__version__,
           "P_e_curve": {f"L{L}": curve[L]["P_e"] for L in LAYERS},
           "per_layer": results,
           "phaseA_outcome": ("LOCALIZED@" + ",".join(f"L{L}" for L in localized)) if localized
                             else ("WEAK@" + ",".join(f"L{L}" for L in weak)) if weak else "ALL-FLAT",
           "next": ("Phase B subspace @ localized layer" if localized else
                    "Phase B subspace @ argmax-|M| (partial)" if weak else
                    "Phase B subspace @ L8 (H1 live)"),
           "runtime_s": round(time.time() - t0, 1)}
    fn = os.path.join(OUT, "prv03_phaseA_smoke.json" if SMOKE else "prv03_phaseA.json")
    json.dump(out, open(fn, "w"), indent=2)
    log("[A] OUTCOME: " + out["phaseA_outcome"] + "  wrote " + fn)

if __name__ == "__main__":
    main()
