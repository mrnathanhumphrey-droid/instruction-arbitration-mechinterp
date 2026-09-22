#!/usr/bin/env python
# RES-06 -- does the decomposition add up? PREREG_RES06.md, chained CAL-01 32cf270f... ONE operation throughout:
# TWIN-PATCH (item residual <- counterbalanced twin's, aligned same-index; twins are same-length cb-flips -> 0 pos
# import). Partition ALL token positions into K (markers/headers/BOS/EOT), S (imperative spans), I (intermediate
# content), R (readout=last). Arms: each region alone (M_K,M_S,M_I,M_R); ALL together (M_all, anchor ~1 by
# construction); per-region floors (same-slot diff-filler source, region-order aligned); VOID (all-layer readout
# twin-patch same-slot, group-before-subsample). Number: Sigma=M_K+M_S+M_I+M_R vs M_all (dev from 1 = validity).
# M=-dY/(2B) signed by counterbalance, template-cluster PAIRED bootstrap. Read M_all FIRST, then Sigma+gap, then table.
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
BOS, SH, EOH, EOT = 128000, 128006, 128007, 128009
NL = 271                            # "\n\n"
FLOOR_STRIDE = 12 if SMOKE else 6
def log(*a): print(*a, flush=True)

def main():
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_contested.jsonl"), encoding="utf-8")]
    unc = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_uncontested.jsonl"), encoding="utf-8")]
    from make_stimuli import TEMPLATES
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import transformers
    log(f"[R6] model on {dev}; tf {transformers.__version__} n={len(stim)} ({time.time()-t0:.0f}s)")

    def partition(it):
        """Return ids, dict of region->sorted position list (K,S,I,R). Assert complete+disjoint."""
        imp_s = TEMPLATES[it["template_idx".format(T=it["target_sys"])
        imp_u = TEMPLATES[it["template_idx".format(T=it["target_usr"])
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]; T = len(ids)
        sh = [i for i, t in enumerate(ids) if t == SH]; eoh = [i for i, t in enumerate(ids) if t == EOH]
        def span(imp):
            cs = text.index(imp); ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        si = span(imp_s); ui = span(imp_u)
        R = [T - 1]
        S = sorted(set(si) | set(ui))
        K = set()
        if ids[0] == BOS: K.add(0)
        for h in range(len(sh)):                       # system, user, assistant headers
            for p in range(sh[h], eoh[h] + 1): K.add(p)
        for i, t in enumerate(ids):
            if t == EOT: K.add(i)
        # the "\n\n" right after system & user headers (not the assistant one = readout)
        for h in (0, 1):
            p = eoh[h] + 1
            if p < T and ids[p] == NL: K.add(p)
        K.discard(T - 1)                               # readout is R, never K
        K = K - set(S)                                 # spans win over any overlap (shouldn't happen)
        assigned = set(K) | set(S) | set(R)
        I = [p for p in range(T) if p not in assigned]
        K = sorted(K)
        # hard gate: partition complete + disjoint
        allp = set(K) | set(S) | set(I) | set(R)
        ok = (len(allp) == T and
              len(set(K) & set(S)) == 0 and len(set(K) & set(I)) == 0 and len(set(K) & set(R)) == 0 and
              len(set(S) & set(I)) == 0 and len(set(S) & set(R)) == 0 and len(set(I) & set(R)) == 0)
        return ids, {"K": K, "S": S, "I": I, "R": R}, ok, si, ui

    twin_g = defaultdict(dict); src_g = defaultdict(list)
    for i, it in enumerate(stim):
        twin_g[(it["template_idx"], it["filler_idx"], it["position"])][it["counterbalance" = i
        src_g[(it["template_idx"], it["position"], it["counterbalance"])].append(i)
    twin_of = {}
    for d in twin_g.values():
        if len(d) == 2: a, b = list(d.values()); twin_of[a] = b; twin_of[b] = a
    def source_of(i):
        it = stim[i]; c = [j for j in src_g[(it["template_idx"], it["position"], it["counterbalance"])] if j != i]
        return c[0] if c else None
    SEG = {}
    for i in range(len(stim)):
        ids, reg, ok, si, ui = partition(stim[i]); SEG[i] = (ids, reg, ok, si, ui)

    def capture(i):
        ids = SEG[i][0]; t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        return {L: hs[L][0].detach().clone() for L in LAYERS}   # full [T,d] per layer

    STATE = {"repl": None}; handles = []
    def make_hook(L):
        def hook(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            r = STATE["repl"]
            if r is not None and L in r:
                pos, val = r[L]; h[0, pos, :] = val
            return out
        return hook
    for L in LAYERS: handles.append(model.model.layers[L - 1].register_forward_hook(make_hook(L)))
    def run(ids, repl=None):
        STATE["repl"] = repl; t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lg = model(input_ids=t, use_cache=False).logits[0, -1, :].float()
        STATE["repl"] = None
        lp = torch.log_softmax(lg, -1); return float(lp[DONE] - lp[READY])
    def ysig(R, it): return R if it["target_sys"] == "DONE" else -R

    def repl_from(item_pos, src_cap, src_pos):
        """patch item_pos <- src_cap at src_pos (aligned by order); requires equal count."""
        if len(item_pos) != len(src_pos) or len(item_pos) == 0: return None
        ip = torch.tensor(item_pos, dtype=torch.long, device=dev)
        sp = torch.tensor(src_pos, dtype=torch.long, device=dev)
        return {L: (ip, src_cap[L][sp].to(torch.bfloat16)) for L in LAYERS}

    # usable: twin present, same length (aligned twin-patch), partition ok for item & twin
    def usable(i):
        tw = twin_of.get(i)
        if tw is None: return False
        if len(SEG[i][0]) != len(SEG[tw][0]): return False
        return SEG[i][2] and SEG[tw][2]
    use = [i for i in range(len(stim)) if usable(i)]
    if SMOKE: use = use[:40]
    log(f"[R6] usable={len(use)} skipped={len(stim)-len(use)} ({time.time()-t0:.0f}s)")

    # self-check: M_all (all positions from twin) must move item0 strongly
    i0 = use[0]; c0 = capture(twin_of[i0]); ids0 = SEG[i0][0]
    allpos0 = list(range(len(ids0)))
    r0 = repl_from(allpos0, c0, allpos0)
    yb0 = run(ids0); ya0 = run(ids0, r0)
    if abs(ya0 - yb0) < 1e-4:
        for h in handles: h.remove()
        raise SystemExit("SELFCHECK FAILED: all-position twin-patch did not move Y")
    log(f"[R6] SELFCHECK ok (item0 {yb0:+.3f}->all {ya0:+.3f})")

    REGIONS = ["K", "S", "I", "R"]
    tmpl = np.array([stim[i]["template_idx"] for i in use]); N = len(use)
    Yb = np.zeros(N); Yall = np.zeros(N)
    Yreg = {g: np.zeros(N) for g in REGIONS}
    Yflo = {g: np.full(N, np.nan) for g in REGIONS}
    nfloor = {g: 0 for g in REGIONS}
    for n, i in enumerate(use):
        it = stim[i]; ids = SEG[i][0]; reg = SEG[i][1]
        tw = twin_of[i]; sc = source_of(i)
        capt = capture(tw)
        Yb[n] = ysig(run(ids), it)
        allpos = list(range(len(ids)))
        Yall[n] = ysig(run(ids, repl_from(allpos, capt, allpos)), it)
        for g in REGIONS:
            rp = repl_from(reg[g], capt, reg[g])
            Yreg[g][n] = ysig(run(ids, rp), it) if rp is not None else Yb[n]
        if sc is not None:
            caps = capture(sc); sreg = SEG[sc][1]
            for g in REGIONS:
                rp = repl_from(reg[g], caps, sreg[g])   # region-order aligned; needs equal count
                if rp is not None:
                    Yflo[g][n] = ysig(run(ids, rp), it); nfloor[g] += 1
        if (n + 1) % 60 == 0: log(f"[R6] {n+1}/{N} ({time.time()-t0:.0f}s)")
    B = float(Yb.mean())
    log(f"[R6] B={B:+.4f} floor n: " + " ".join(f"{g}:{nfloor[g]}" for g in REGIONS) + f" ({time.time()-t0:.0f}s)")

    np.savez(os.path.join(OUT, "res06_peritem_smoke.npz" if SMOKE else "res06_peritem.npz"),
             use=np.array(use), tmpl=tmpl, Yb=Yb, Yall=Yall, B=B,
             **{f"Y_{g}": Yreg[g] for g in REGIONS}, **{f"Yflo_{g}": Yflo[g] for g in REGIONS})

    # ---- VOID: all-layer readout twin-patch from same-slot source, group before subsample ----
    def unc_ids(it):
        try:
            msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
            text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            return tok(text, add_special_tokens=False)["input_ids"]
        except Exception:
            return None
    grp = defaultdict(list)
    for k, it in enumerate(unc): grp[(it["template_idx"], it["position"], it["slot"], it["target"])].append(k)
    def ucomply(ids, repl=None):
        STATE["repl"] = repl; t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lp = torch.log_softmax(model(input_ids=t, use_cache=False).logits[0, -1, :].float(), -1)
        STATE["repl"] = None
        return 1 if (lp[DONE] - lp[READY]) > 0 else 0
    uok = un = sok = sn = 0
    for k in range(0, len(unc), FLOOR_STRIDE):
        it = unc[k]; ids = unc_ids(it)
        if ids is None: continue
        un += 1; uok += ucomply(ids)
        cand = [m for m in grp[(it["template_idx"], it["position"], it["slot"], it["target"])] if m != k]
        if not cand: continue
        sids = unc_ids(unc[cand[0)
        if sids is None or len(sids) != len(ids): continue
        t = torch.tensor([sids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        rp = {L: (torch.tensor([len(ids) - 1], dtype=torch.long, device=dev), hs[L][0, -1:, :].to(torch.bfloat16)) for L in LAYERS}
        sn += 1; sok += ucomply(ids, rp)
    for h in handles: h.remove()
    floor_uns = uok / max(1, un); floor_steer = sok / max(1, sn) if sn else float("nan")
    VOID = bool(sn > 0 and floor_steer < 0.90 * floor_uns)
    log(f"[R6] VOID: unsteered {floor_uns:.3f}(n={un}) steered {floor_steer:.3f}(n={sn}) VOID={VOID}")

    # ---- M + paired template-cluster bootstrap ----
    def per_t(a):
        return np.array([np.nanmean(a[tmpl == t]) if np.any((tmpl == t) & ~np.isnan(a)) else 0.0 for t in range(NTMPL)])
    ptB = per_t(Yb)
    ptR = {g: per_t(Yreg[g] - Yb) for g in REGIONS}
    ptF = {g: per_t(Yflo[g] - Yb) for g in REGIONS}
    ptAll = per_t(Yall - Yb)
    def M_of(pt): return float(-pt.mean() / (2 * ptB.mean())) if abs(ptB.mean()) > 1e-9 else float("nan")
    Mreg = {g: M_of(ptR[g]) for g in REGIONS}; Mflo = {g: M_of(ptF[g]) for g in REGIONS}
    Mall = M_of(ptAll)
    Sigma = sum(Mreg[g] for g in REGIONS); Sigma_KSI = Mreg["K"] + Mreg["S"] + Mreg["I"]

    rng = np.random.default_rng(SEED)
    keys = REGIONS + [f"net_{g}" for g in REGIONS] + ["all", "Sigma", "Sigma_KSI", "gap", "gap_KSI"]
    boot = {k: np.empty(BOOT) for k in keys}
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL); den = 2 * ptB[pk].mean()
        if abs(den) < 1e-9:
            for k in keys: boot[k][b] = np.nan
            continue
        mr = {g: -ptR[g][pk].mean() / den for g in REGIONS}
        mf = {g: -ptF[g][pk].mean() / den for g in REGIONS}
        ma = -ptAll[pk].mean() / den
        sig = sum(mr[g] for g in REGIONS); sksi = mr["K"] + mr["S"] + mr["I"]
        for g in REGIONS: boot[g][b] = mr[g]; boot[f"net_{g}"][b] = mr[g] - mf[g]
        boot["all"][b] = ma; boot["Sigma"][b] = sig; boot["Sigma_KSI"][b] = sksi
        boot["gap"][b] = sig - ma; boot["gap_KSI"][b] = sksi - ma
    def ci(a): lo, hi = np.nanpercentile(a, [2.5, 97.5]); return [float(lo), float(hi)]
    C = {k: ci(boot[k]) for k in keys}
    Mnet = {g: Mreg[g] - Mflo[g] for g in REGIONS}
    gap = Sigma - Mall; gap_KSI = Sigma_KSI - Mall

    # ---- mechanical verdict (reading order: M_all gate first) ----
    if VOID:
        verdict = "VOID -- NOT a null"
    elif abs(Mall - 1.0) > 0.15:
        verdict = f"HARNESS-PROBLEM (M_all={Mall:.3f} materially off 1; do NOT interpret Sigma)"
    elif abs(gap) <= 0.15 and C["gap"][0] <= 0 <= C["gap"][1]:
        verdict = "ADDITIVE-DECOMPOSES (Sigma~M_all~1; missing half was a subset artifact)"
    elif gap < -0.15 and C["gap"][1] < 0:
        verdict = "INTERACTION (Sigma<<M_all; regions do little alone, work together = distributed composition)"
    elif gap > 0.15 and C["gap"][0] > 0:
        verdict = "REDUNDANT/SUPER-ADDITIVE (Sigma>>M_all; regions overlap, readout re-derives upstream; use Sigma_KSI)"
    else:
        verdict = "PARTIAL (report band)"
    MI_large = (Mnet["I"] > 0.25) and (C["net_I"][0] > 0)
    note = "M_I LARGE (missing half in intermediate content; composition softens)" if MI_large else "M_I not large"

    out = {"prereg": "PREREG_RES06.md", "SMOKE": SMOKE,
           "chained_to_CAL01": "32cf270f37672908bdd06f1d78b929ec9c4bb3119d2e35ef3c1e557903dcb91b",
           "transformers": transformers.__version__, "B": B, "n_pairs": N, "n_skipped": len(stim) - N,
           "M_all": Mall, "M_all_ci": C["all"], "M_all_dev_from_1": Mall - 1.0,
           "Sigma": Sigma, "Sigma_ci": C["Sigma"], "gap_Sigma_minus_Mall": gap, "gap_ci": C["gap"],
           "Sigma_KSI": Sigma_KSI, "Sigma_KSI_ci": C["Sigma_KSI"], "gap_KSI": gap_KSI, "gap_KSI_ci": C["gap_KSI"],
           "M_by_region": {g: Mreg[g] for g in REGIONS}, "M_ci_by_region": {g: C[g] for g in REGIONS},
           "floor_by_region": {g: Mflo[g] for g in REGIONS}, "net_by_region": {g: Mnet[g] for g in REGIONS},
           "net_ci_by_region": {g: C[f"net_{g}"] for g in REGIONS}, "floor_n_by_region": nfloor,
           "floor_unsteered": floor_uns, "floor_steered": floor_steer, "VOID": VOID,
           "verdict": verdict, "MI_note": note, "runtime_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "res06_arms_smoke.csv" if SMOKE else "res06_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["region", "M", "ci_lo", "ci_hi", "floor", "net", "net_ci_lo", "net_ci_hi", "floor_n"])
        for g in REGIONS:
            w.writerow([g, round(Mreg[g],5), round(C[g][0],5), round(C[g][1],5), round(Mflo[g],5),
                        round(Mnet[g],5), round(C[f"net_{g}"][0],5), round(C[f"net_{g}"][1],5), nfloor[g)
        w.writerow(["ALL(anchor)", round(Mall,5), round(C["all"][0],5), round(C["all"][1],5), "", "", "", "", N])
        w.writerow(["Sigma(K+S+I+R)", round(Sigma,5), round(C["Sigma"][0],5), round(C["Sigma"][1],5), "", "", "", "", N])
        w.writerow(["gap=Sigma-M_all", round(gap,5), round(C["gap"][0],5), round(C["gap"][1],5), "", "", "", "", N])
        w.writerow(["Sigma_KSI", round(Sigma_KSI,5), round(C["Sigma_KSI"][0],5), round(C["Sigma_KSI"][1],5), "", "", "", "", N])
        w.writerow(["gap_KSI", round(gap_KSI,5), round(C["gap_KSI"][0],5), round(C["gap_KSI"][1],5), "", "", "", "", N])
    fn = os.path.join(OUT, "res06_smoke.json" if SMOKE else "res06.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[R6] M_all={Mall:+.4f}{C['all']} (GATE) | Sigma={Sigma:+.4f} gap={gap:+.4f}{C['gap']} | "
        f"Sigma_KSI={Sigma_KSI:+.4f} | M K={Mreg['K']:+.3f} S={Mreg['S']:+.3f} I={Mreg['I']:+.3f} R={Mreg['R']:+.3f} "
        f"-> {verdict} :: {note}; wrote {fn}")

if __name__ == "__main__":
    main()
