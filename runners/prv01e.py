#!/usr/bin/env python
# PRV-01e -- does role-header provenance propagate downstream of the header? Llama-3.1-8B-Instruct, NON-CAUSAL probe.
# PREREG_PRV01E.md, chained PRV-01c-r2. FORWARD ONLY. New contrast (supersedes r2 VOID): arms differ ONLY in the content
# block's role header (ipython vs user); everything from the header-end onward is BYTE-IDENTICAL (G-CONSTRUCT, verified
# 300/300 tokenizer-only, header diff k=1). Read at d downstream from the content-block header; measure the accuracy
# SURFACE layer x d. L0 is at chance BY CONSTRUCTION (identical tokens). G-POSITION = pad-swap counterbalance (k pad in A's
# vs B's preceding region; surfaces must agree) -- the intended position test (replaces r2's mis-specified G6).
import os, json, time
import numpy as np, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
SYS = "You are a helpful assistant."; TRIG = "Please retrieve the note."; STUB = "Let me look that up for you."
PAD = " and"; K = 1                                  # header diff ipython-user = 1 token (verified)
SH, EOH, EOT = 128006, 128007, 128009
DS = [1, 4, 8, 16, 32, 64]
NFOLD = 5; SEED = 20260923
G0_MAX = 0.55; GPOS_TOL = 0.05; GVAL_MIN = 0.80
def log(*a): print(*a, flush=True)


IPY_HDR = "<|start_header_id|>ipython<|end_header_id|>"
USR_HDR = "<|start_header_id|>user<|end_header_id|>"
def render_ids(tok, content, arm, pad=False):
    # the reviewer build note: construct B by STRING SUBSTITUTION on A's rendered prompt (swap ONLY the tool header),
    # not by re-rendering a user turn (tojson vs user-turn paths differ). Guarantees post-header byte-identity.
    stub = STUB + (PAD * K if pad else "")
    base = [{"role": "system", "content": SYS}, {"role": "user", "content": TRIG}, {"role": "assistant", "content": stub},
            {"role": "tool", "content": {"output": content}}]
    textA = tok.apply_chat_template(base, tokenize=False, add_generation_prompt=True)
    text = textA if arm == "A" else textA.replace(IPY_HDR, USR_HDR)   # B claims user framing around a byte-identical tool payload
    return tok(text, add_special_tokens=False)["input_ids"]


def content_eoh(ids):
    eohs = [i for i, t in enumerate(ids) if t == EOH]; return eohs[-2]   # content block header (last is gen-prompt)


def main():
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_prv01e.jsonl"), encoding="utf-8")]
    if SMOKE: stim = stim[:40]
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16, device_map={"": 0}).eval()
    dev = next(model.parameters()).device; import transformers
    nL = model.config.num_hidden_layers + 1; N = len(stim)
    log(f"[E] {MODEL_ID} on {dev}; tf {transformers.__version__} N={N} nL={nL} DS={DS} ({time.time()-t0:.0f}s)")

    CFG = ["A_nat", "A_pad", "B_nat", "B_pad"]
    X = {c: {d: np.zeros((N, nL, 4096), dtype=np.float16) for d in DS} for c in CFG}
    supp = {c: {d: np.zeros(N, dtype=bool) for d in DS} for c in CFG}
    gconstruct_ok = 0
    for n, it in enumerate(stim):
        c = it["content"]
        ids = {"A_nat": render_ids(tok, c, "A", False), "A_pad": render_ids(tok, c, "A", True),
               "B_nat": render_ids(tok, c, "B", False), "B_pad": render_ids(tok, c, "B", True)}
        # G-CONSTRUCT (nat): post-header identical A vs B
        ea = content_eoh(ids["A_nat"]); eb = content_eoh(ids["B_nat"])
        if ids["A_nat"][ea + 1:] == ids["B_nat"][eb + 1:]: gconstruct_ok += 1
        for cfg in CFG:
            iid = ids[cfg]; e = content_eoh(iid)
            t = torch.tensor([iid], dtype=torch.long, device=dev)
            with torch.inference_mode():
                hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
            for d in DS:
                pos = e + d
                if pos < len(iid):
                    supp[cfg][d][n] = True
                    for L in range(nL):
                        X[cfg][d][n, L] = hs[L][0, pos, :].float().cpu().numpy().astype(np.float16)
        if (n + 1) % 60 == 0: log(f"[E] extract {n+1}/{N} ({time.time()-t0:.0f}s)")
    log(f"[E] G-CONSTRUCT post-header identical {gconstruct_ok}/{N} ({time.time()-t0:.0f}s)")

    rng = np.random.default_rng(SEED)
    fold = np.array([k % NFOLD for k in rng.permutation(N)])

    def acc_at(cfgX, cfgY, L, d, shuffle=False):
        m = supp[cfgX][d] & supp[cfgY][d]
        idx = np.where(m)[0]
        if len(idx) < 20: return np.nan
        yhatall = []; ytruall = []
        for f in range(NFOLD):
            trI = idx[fold[idx] != f]; teI = idx[fold[idx] == f]
            if len(teI) == 0 or len(trI) < 10: continue
            Xtr = np.concatenate([X[cfgX][d][trI, L].astype(np.float32), X[cfgY][d][trI, L].astype(np.float32)], 0)
            ytr = np.concatenate([np.ones(len(trI)), np.zeros(len(trI))])
            if shuffle: rng.shuffle(ytr)
            sc = StandardScaler().fit(Xtr)
            clf = LogisticRegression(C=1.0, max_iter=500, solver="lbfgs").fit(sc.transform(Xtr), ytr)
            pX = clf.predict(sc.transform(X[cfgX][d][teI, L].astype(np.float32)))
            pY = clf.predict(sc.transform(X[cfgY][d][teI, L].astype(np.float32)))
            yhatall += list(pX) + list(pY); ytruall += [1] * len(teI) + [0] * len(teI)
        return balanced_accuracy_score(ytruall, yhatall) if ytruall else np.nan

    # surfaces: headline (A_nat vs B_nat), padA (A_pad vs B_nat), padB (A_nat vs B_pad)
    def surface(cx, cy):
        return np.array([[acc_at(cx, cy, L, d) for d in DS] for L in range(nL)])
    log(f"[E] computing surfaces ({time.time()-t0:.0f}s)...")
    S = surface("A_nat", "B_nat"); SpadA = surface("A_pad", "B_nat"); SpadB = surface("A_nat", "B_pad")
    log(f"[E] surfaces done ({time.time()-t0:.0f}s)")

    # peak layer = argmax over layers of max-over-d acc (strongest cell)
    peakL = int(np.nanargmax(np.nanmax(S, axis=1)))
    curve = {DS[j]: float(S[peakL, j]) for j in range(len(DS))}
    d1 = int(np.nanargmin([abs(dd - 1) for dd in DS]))  # index of d=1

    # gates
    g0_ok = bool(np.all([S[0, j] <= G0_MAX for j in range(len(DS)) if not np.isnan(S[0, j])]))
    gpos_maxdiff = float(np.nanmax(np.abs(SpadA - SpadB)))
    gpos_ok = bool(gpos_maxdiff <= GPOS_TOL)
    NPERM = 10 if SMOKE else 25
    null = np.array([acc_at("A_nat", "B_nat", peakL, DS[0], shuffle=True) for _ in range(NPERM)])
    null_mean = float(np.nanmean(null)); null_std = float(np.nanstd(null)); null_p95 = float(np.nanpercentile(null, 95))
    real_d1 = float(S[peakL, 0])
    gshuf_ok = bool(0.42 <= null_mean <= 0.58 and real_d1 > null_p95)   # multi-perm null: no leak (mean~chance) AND real signal exceeds it
    acc_shuf = null_mean
    gval = curve[1]; gval_ok = bool(gval >= GVAL_MIN)

    # outcome on curve vs d at peak layer
    def half_distance():
        base = curve[1]; mid = (base + 0.5) / 2
        for d in DS:
            if curve[d] <= mid: return d
        return None
    if not (g0_ok and gpos_ok and gshuf_ok and gval_ok):
        why = []
        if not g0_ok: why.append(f"G0 L0 {[round(S[0,j],3) for j in range(len(DS))]}>0.55")
        if not gpos_ok: why.append(f"G-POSITION maxdiff {gpos_maxdiff:.3f}>0.05")
        if not gshuf_ok: why.append(f"G-SHUFFLE null_mean={null_mean:.3f} p95={null_p95:.3f} real={real_d1:.3f}")
        if not gval_ok: why.append(f"G-VALIDITY d1 {gval:.3f}<0.80")
        outcome = "VOID (" + "; ".join(why) + ")"
    elif curve[32] > 0.70 and curve[64] > 0.70:
        outcome = f"PROPAGATED (acc>0.70 at d>=32: acc(d32)={curve[32]:.2f} acc(d64)={curve[64]:.2f}; true provenance survives a perfect payload forgery downstream -> PRV-01d well-posed)"
    elif curve[16] <= 0.60:
        outcome = f"LOCAL (acc<=0.60 by d=16: acc(d16)={curve[16]:.2f}; provenance does not leave the header region -> mechanistically explains SPOOF-01 marker inertness; PRV-01d unnecessary)"
    else:
        hd = half_distance()
        outcome = f"DECAYING (half-distance={hd} tokens; acc d1={curve[1]:.2f} d16={curve[16]:.2f} d64={curve[64]:.2f})"

    np.savez(os.path.join(OUT, "prv01e_surface" + ("_smoke" if SMOKE else "") + ".npz"),
             S=S, SpadA=SpadA, SpadB=SpadB, DS=np.array(DS), peakL=peakL, fold=fold)
    out = {"prereg": "PREREG_PRV01E.md", "probe": "PRV-01e", "SMOKE": SMOKE, "model_id": MODEL_ID,
           "chained_to_PRV01C_R2": "2f58285c622a0aac35f06c56d3067cd34fdc57aea4380b15fe0d74863ff529f3",
           "transformers": transformers.__version__, "N": N, "n_layers": nL, "DS": DS, "header_diff_k": K,
           "gconstruct_identical": gconstruct_ok, "peak_layer": peakL, "curve_vs_d_at_peak": curve,
           "gates": {"G0_embedding_chance": {"L0_by_d": [float(S[0, j]) for j in range(len(DS))], "pass": g0_ok},
                     "G_POSITION": {"maxdiff_padA_vs_padB": gpos_maxdiff, "pass": gpos_ok},
                     "G_SHUFFLE": {"null_mean": null_mean, "null_std": null_std, "null_p95": null_p95, "real_d1": real_d1, "n_perm": NPERM, "pass": gshuf_ok},
                     "G_VALIDITY": {"acc_d1": gval, "pass": gval_ok}},
           "outcome": outcome, "runtime_s": round(time.time() - t0, 1)}
    fn = os.path.join(OUT, "prv01e" + ("_smoke" if SMOKE else "") + ".json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[E] G-CONSTRUCT {gconstruct_ok}/{N} | peakL={peakL} curve={ {d: round(curve[d],3) for d in DS} }")
    log(f"[E] GATES G0={g0_ok}(L0 {[round(S[0,j],2) for j in range(len(DS))]}) G-POS={gpos_ok}({gpos_maxdiff:.3f}) G-SHUF={gshuf_ok}({acc_shuf:.2f}) G-VAL={gval_ok}({gval:.2f})")
    log(f"[E] OUTCOME: {outcome}")
    log(f"[E] wrote {fn}")


if __name__ == "__main__":
    main()
