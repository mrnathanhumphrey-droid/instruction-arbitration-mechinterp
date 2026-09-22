#!/usr/bin/env python
# DIST-01 -- is the exchange ceiling content-bound (model) or operation-incoherence (instrument)? PREREG_DIST01.md,
# chained RES-06 076b2701... Descriptive, forwards only, no new intervention. Measures the model's RE-DERIVATION at the
# span positions (block output BEFORE the hook re-overwrites) for cross-role EXCHANGE vs TWIN-PATCH (coherent baseline).
# Per layer cos-dist: accept_exch (how much model alters the misplaced install), accept_tp (coherent baseline),
# Daccept=accept_exch-accept_tp (incoherence isolated), to_twin (exchange vs twin's same-slot state), revert (vs item).
# Decisive statistic: depth-slope of Daccept. Twin-based VOID: all-pos twin-patch reproduces twin's top-1 token.
import os, json, time, csv
import numpy as np, torch
from collections import defaultdict
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
LAYERS = list(range(8, 32))
DONE, READY = 71496, 46678
NTMPL = 30
BOOT = 300 if SMOKE else 5000
SEED = 20260914
def log(*a): print(*a, flush=True)

def main():
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_contested.jsonl"), encoding="utf-8")]
    from make_stimuli import TEMPLATES
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import transformers
    log(f"[D1] model on {dev}; tf {transformers.__version__} n={len(stim)} ({time.time()-t0:.0f}s)")

    def spans(it):
        imp_s = TEMPLATES[it["template_idx".format(T=it["target_sys"])
        imp_u = TEMPLATES[it["template_idx".format(T=it["target_usr"])
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]
        def sp(imp):
            cs = text.index(imp); ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        return ids, sp(imp_s), sp(imp_u)

    twin_g = defaultdict(dict)
    for i, it in enumerate(stim):
        twin_g[(it["template_idx"], it["filler_idx"], it["position"])][it["counterbalance" = i
    twin_of = {}
    for d in twin_g.values():
        if len(d) == 2: a, b = list(d.values()); twin_of[a] = b; twin_of[b] = a
    SEG = {i: spans(stim[i]) for i in range(len(stim))}

    def full_hs(ids):
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            out = model(input_ids=t, output_hidden_states=True, use_cache=False)
        return out.hidden_states, out.logits[0, -1, :].float()

    STATE = {"repl": None, "cap": None}; handles = []
    def make_hook(L):
        def hook(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            r = STATE["repl"]
            if r is not None and L in r:
                pos, val = r[L]
                if STATE["cap"] is not None:
                    STATE["cap"][L] = h[0, pos, :].detach().float().clone()   # model's re-derivation BEFORE overwrite
                h[0, pos, :] = val
            return out
        return hook
    for L in LAYERS: handles.append(model.model.layers[L - 1].register_forward_hook(make_hook(L)))

    def run_capture(ids, repl):
        STATE["repl"] = repl; STATE["cap"] = {}
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lg = model(input_ids=t, use_cache=False).logits[0, -1, :].float()
        cap = STATE["cap"]; STATE["repl"] = None; STATE["cap"] = None
        return cap, lg

    def cosd(a, b):   # mean cosine distance over rows [n,d]
        a = a.float(); b = b.float()
        num = (a * b).sum(-1)
        den = a.norm(dim=-1) * b.norm(dim=-1) + 1e-8
        return float((1 - num / den).mean())

    use = [i for i in range(len(stim)) if twin_of.get(i) is not None and len(SEG[i][0]) == len(SEG[twin_of[i[0])
           and SEG[i][1] and SEG[i][2
    if SMOKE: use = use[:40]
    log(f"[D1] usable={len(use)} skipped={len(stim)-len(use)} ({time.time()-t0:.0f}s)")

    tmpl = np.array([stim[i]["template_idx"] for i in use]); N = len(use)
    nL = len(LAYERS)
    acc_e = np.zeros((N, nL)); acc_t = np.zeros((N, nL)); to_tw = np.zeros((N, nL)); rev = np.zeros((N, nL))
    void_ok = np.zeros(N)
    for n, i in enumerate(use):
        it = stim[i]; ids, si, ui = SEG[i]; tw = twin_of[i]
        twinH, twin_lg = full_hs(SEG[tw][0])          # twin clean (installed values + coherent state + VOID target)
        itemH, _ = full_hs(ids)                        # item clean (reversion target)
        # exchange: si<-twin usr-span (twinH[L][ui]); ui<-twin sys-span (twinH[L][si])
        exch = {L: (torch.tensor(si + ui, dtype=torch.long, device=dev),
                    torch.cat([twinH[L][0, ui, :], twinH[L][0, si, :, 0).to(torch.bfloat16)) for L in LAYERS}
        cap_e, _ = run_capture(ids, exch)
        # twin-patch: si<-twin sys-span (twinH[L][si]); ui<-twin usr-span (twinH[L][ui])
        tp = {L: (torch.tensor(si + ui, dtype=torch.long, device=dev),
                  torch.cat([twinH[L][0, si, :], twinH[L][0, ui, :, 0).to(torch.bfloat16)) for L in LAYERS}
        cap_t, _ = run_capture(ids, tp)
        # twin-based VOID: all-position twin-patch reproduces twin's top-1 token
        allpos = list(range(len(ids)))
        allrepl = {L: (torch.tensor(allpos, dtype=torch.long, device=dev), twinH[L][0, allpos, :].to(torch.bfloat16)) for L in LAYERS}
        _, lg_all = run_capture(ids, allrepl)
        void_ok[n] = 1.0 if int(lg_all.argmax()) == int(twin_lg.argmax()) else 0.0
        ns = len(si)
        for j, L in enumerate(LAYERS):
            Re = cap_e[L]; Rt = cap_t[L]                 # [ns+nu, d] rows: first ns = si, rest = ui
            Re_s, Re_u = Re[:ns], Re[ns:]; Rt_s, Rt_u = Rt[:ns], Rt[ns:]
            inst_e_s = twinH[L][0, ui, :]; inst_e_u = twinH[L][0, si, :]   # exchange installed
            inst_t_s = twinH[L][0, si, :]; inst_t_u = twinH[L][0, ui, :]   # twin-patch installed
            acc_e[n, j] = 0.5 * (cosd(Re_s, inst_e_s) + cosd(Re_u, inst_e_u))
            acc_t[n, j] = 0.5 * (cosd(Rt_s, inst_t_s) + cosd(Rt_u, inst_t_u))
            to_tw[n, j] = 0.5 * (cosd(Re_s, twinH[L][0, si, :]) + cosd(Re_u, twinH[L][0, ui, :]))
            rev[n, j] = 0.5 * (cosd(Re_s, itemH[L][0, si, :]) + cosd(Re_u, itemH[L][0, ui, :]))
        if (n + 1) % 60 == 0: log(f"[D1] {n+1}/{N} ({time.time()-t0:.0f}s)")
    for h in handles: h.remove()
    void_rate = float(void_ok.mean())
    log(f"[D1] twin-VOID rate={void_rate:.3f} ({time.time()-t0:.0f}s)")

    np.savez(os.path.join(OUT, "dist01_peritem_smoke.npz" if SMOKE else "dist01_peritem.npz"),
             use=np.array(use), tmpl=tmpl, layers=np.array(LAYERS),
             acc_e=acc_e, acc_t=acc_t, to_tw=to_tw, rev=rev, void_ok=void_ok)

    # per-layer template-cluster means + bootstrap CI; depth-slope of Daccept (L>=9)
    def per_t(col):
        return np.array([col[tmpl == t].mean() if (tmpl == t).any() else np.nan for t in range(NTMPL)])
    dacc = acc_e - acc_t
    ptA = {j: per_t(acc_e[:, j]) for j in range(nL)}
    ptT = {j: per_t(acc_t[:, j]) for j in range(nL)}
    ptD = {j: per_t(dacc[:, j]) for j in range(nL)}
    ptTw = {j: per_t(to_tw[:, j]) for j in range(nL)}
    ptRv = {j: per_t(rev[:, j]) for j in range(nL)}
    accE = [float(np.nanmean(ptA[j])) for j in range(nL)]
    accT = [float(np.nanmean(ptT[j])) for j in range(nL)]
    dAcc = [float(np.nanmean(ptD[j])) for j in range(nL)]
    toTw = [float(np.nanmean(ptTw[j])) for j in range(nL)]
    revC = [float(np.nanmean(ptRv[j])) for j in range(nL)]
    Lj = [j for j, L in enumerate(LAYERS) if L >= 9]   # skip L8 (input not yet exchanged)
    Larr = np.array([LAYERS[j] for j in Lj])
    rng = np.random.default_rng(SEED)
    d_ci = []; slopes = np.empty(BOOT); meanD = np.empty(BOOT)
    for j in range(nL):
        col = np.array([np.nanmean(ptD[j][rng2]) for rng2 in [rng.integers(0, NTMPL, NTMPL) for _ in range(400))
        d_ci.append([float(np.nanpercentile(col, 2.5)), float(np.nanpercentile(col, 97.5))])
    rng = np.random.default_rng(SEED + 1)
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL)
        dvals = np.array([np.nanmean(ptD[j][pk]) for j in Lj])
        slopes[b] = float(np.polyfit(Larr, dvals, 1)[0])
        meanD[b] = float(np.nanmean(dvals))
    slope = float(np.polyfit(Larr, [dAcc[j] for j in Lj], 1)[0])
    slope_ci = [float(np.nanpercentile(slopes, 2.5)), float(np.nanpercentile(slopes, 97.5))]
    meanD_val = float(np.nanmean([dAcc[j] for j in Lj])); meanD_ci = [float(np.nanpercentile(meanD, 2.5)), float(np.nanpercentile(meanD, 97.5))]
    late = float(np.nanmean([dAcc[j] for j in Lj if LAYERS[j] >= 28]))

    if slope_ci[0] > 0 or meanD_val > 0.10 or late > 0.10:
        verdict = ("INCOHERENCE-REAL (exchange re-derived more than twin-patch; ceiling is an OPERATION limit -- "
                   "exchange numbers become floors)")
    elif meanD_val < 0.05 and slope_ci[0] <= 0 <= slope_ci[1]:
        verdict = ("COHERENT-EXCHANGE (exchange installed as coherently as twin-patch; CONTENT-BOUND reading STANDS -- "
                   "~half is a model property)")
    else:
        verdict = "PARTIAL (report band; Daccept intermediate)"

    out = {"prereg": "PREREG_DIST01.md", "SMOKE": SMOKE,
           "chained_to_RES06": "076b270179f52c37c4f569f738544747fea63e90b226c8c7e24225afa8e79409",
           "transformers": transformers.__version__, "n_pairs": N, "n_skipped": len(stim) - N, "layers": LAYERS,
           "accept_exch_by_L": accE, "accept_tp_by_L": accT, "Daccept_by_L": dAcc, "Daccept_ci_by_L": d_ci,
           "to_twin_exch_by_L": toTw, "revert_exch_by_L": revC,
           "Daccept_depth_slope": slope, "Daccept_slope_ci": slope_ci,
           "Daccept_mean_L9plus": meanD_val, "Daccept_mean_ci": meanD_ci, "Daccept_late_L28plus": late,
           "twin_void_rate": void_rate, "verdict": verdict, "runtime_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "dist01_curves_smoke.csv" if SMOKE else "dist01_curves.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["layer", "accept_exch", "accept_tp", "Daccept", "Dacc_ci_lo", "Dacc_ci_hi", "to_twin_exch", "revert_exch"])
        for j, L in enumerate(LAYERS):
            w.writerow([L, round(accE[j],5), round(accT[j],5), round(dAcc[j],5), round(d_ci[j][0],5), round(d_ci[j][1],5),
                        round(toTw[j],5), round(revC[j],5)])
    fn = os.path.join(OUT, "dist01_smoke.json" if SMOKE else "dist01.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[D1] Dacc mean(L>=9)={meanD_val:+.4f}{meanD_ci} slope={slope:+.5f}{slope_ci} late(L>=28)={late:+.4f} "
        f"twinVOID={void_rate:.3f} -> {verdict}; wrote {fn}")

if __name__ == "__main__":
    main()
