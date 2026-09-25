#!/usr/bin/env python
# RES-06-FLIP -- is the Sigma=2.48 super-additive redundancy ORDER-STRUCTURAL? Chained RES-06 (076b2701...).
# Same ONE operation (TWIN-PATCH: item residual <- counterbalanced twin's, aligned same-index) and same K/S/I/R
# partition as RES-06, run at BOTH orders in one job:
#   normal  = system-block then user-block (RES-06 order; recency favors USER). Replication anchor: Sigma must
#             reproduce banked 2.479 +-0.10, else the harness drifted -> HALT.
#   flipped = ORD-01 flip (BOS + user-block + system-block + assistant; recency favors SYSTEM). The test.
# Partition is computed on the NORMAL sequence (RES-06's validated partition), then the flip is a token PERMUTATION
# and region indices are remapped through it (readout stays last; verified). Finding = paired dSigma (per-template)
# and per-region dM: |dSigma| small -> ORDER-INVARIANT redundancy (structural to content/decomposition); large ->
# ORDER-DEPENDENT (redundancy tracks recency). M_all=1 is a construction identity (twins same-length flips) BOTH
# orders; coherence via TWIN-BASED VOID (all-pos twin-patch reproduces the twin's argmax), group-before-subsample.
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
SEED = 20260914                      # same seed as RES-06 for comparability
BOS, SH, EOH, EOT = 128000, 128006, 128007, 128009
NL = 271                             # "\n\n"
REGIONS = ["K", "S", "I", "R"]
SIGMA_NORMAL_BANKED = 2.479          # RES-06 verdict; replication anchor
REPL_TOL = 0.10
DSIG_THR = 0.25                      # pre-committed: |dSigma| <= this & CI incl 0 -> order-invariant
def log(*a): print(*a, flush=True)


def partition(tok, TEMPLATES, it):
    """RES-06 partition on NORMAL order. Return ids, {K,S,I,R} positions, ok(bool)."""
    imp_s = TEMPLATES[it["template_idx"]].format(T=it["target_sys"])
    imp_u = TEMPLATES[it["template_idx"]].format(T=it["target_usr"])
    msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
    ids = enc["input_ids"]; offs = enc["offset_mapping"]; T = len(ids)
    sh = [i for i, t in enumerate(ids) if t == SH]; eoh = [i for i, t in enumerate(ids) if t == EOH]
    def span(imp):
        cs = text.index(imp); ce = cs + len(imp)
        return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
    si = span(imp_s); ui = span(imp_u)
    R = [T - 1]; S = sorted(set(si) | set(ui)); K = set()
    if ids[0] == BOS: K.add(0)
    for h in range(len(sh)):
        for p in range(sh[h], eoh[h] + 1): K.add(p)
    for i, t in enumerate(ids):
        if t == EOT: K.add(i)
    for h in (0, 1):
        p = eoh[h] + 1
        if p < T and ids[p] == NL: K.add(p)
    K.discard(T - 1); K = K - set(S)
    assigned = set(K) | set(S) | set(R)
    I = [p for p in range(T) if p not in assigned]; K = sorted(K)
    allp = set(K) | set(S) | set(I) | set(R)
    ok = (len(allp) == T and not (set(K) & set(S)) and not (set(K) & set(I)) and not (set(K) & set(R))
          and not (set(S) & set(I)) and not (set(S) & set(R)) and not (set(I) & set(R)))
    return ids, {"K": K, "S": S, "I": I, "R": R}, ok


def flip_perm(ids):
    """ORD-01 flip: old-index order = BOS/pre + user-block + system-block + assistant."""
    sh = [i for i, t in enumerate(ids) if t == SH]; eot = [i for i, t in enumerate(ids) if t == EOT]
    pre = list(range(0, sh[0])); sys_blk = list(range(sh[0], eot[0] + 1))
    usr_blk = list(range(sh[1], eot[1] + 1)); asst = list(range(sh[2], len(ids)))
    return pre + usr_blk + sys_blk + asst


def apply_flip(ids, reg):
    """Return flipped_ids and region positions remapped through the permutation."""
    perm = flip_perm(ids)
    fids = [ids[i] for i in perm]
    newpos = {old: new for new, old in enumerate(perm)}
    freg = {g: sorted(newpos[p] for p in reg[g]) for g in REGIONS}
    return fids, freg, newpos


def build_seg(tok, TEMPLATES, it, order):
    ids, reg, ok = partition(tok, TEMPLATES, it)
    if order == "normal":
        return ids, reg, ok
    fids, freg, _ = apply_flip(ids, reg)
    return fids, freg, ok


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
    log(f"[R6F] model on {dev}; tf {transformers.__version__} n={len(stim)} ({time.time()-t0:.0f}s)")

    # twins + same-slot sources (normal-order structure; unchanged by flip)
    twin_g = defaultdict(dict); src_g = defaultdict(list)
    for i, it in enumerate(stim):
        twin_g[(it["template_idx"], it["filler_idx"], it["position"])][it["counterbalance"]] = i
        src_g[(it["template_idx"], it["position"], it["counterbalance"])].append(i)
    twin_of = {}
    for d in twin_g.values():
        if len(d) == 2: a, b = list(d.values()); twin_of[a] = b; twin_of[b] = a
    def source_of(i):
        it = stim[i]; c = [j for j in src_g[(it["template_idx"], it["position"], it["counterbalance"])] if j != i]
        return c[0] if c else None

    # precompute normal partition once (validity + same-length gate); flip is deterministic from it
    PART = {}
    for i in range(len(stim)):
        PART[i] = partition(tok, TEMPLATES, stim[i])
    def usable(i):
        tw = twin_of.get(i)
        if tw is None: return False
        if len(PART[i][0]) != len(PART[tw][0]): return False
        return PART[i][2] and PART[tw][2]
    use = [i for i in range(len(stim)) if usable(i)]
    if SMOKE: use = use[:40]
    tmpl = np.array([stim[i]["template_idx"] for i in use]); N = len(use)
    log(f"[R6F] usable={N} skipped={len(stim)-N} ({time.time()-t0:.0f}s)")

    # hooks
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

    def capture(ids):
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        return {L: hs[L][0].detach().clone() for L in LAYERS}
    def run_R(ids, repl=None):
        STATE["repl"] = repl; t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lg = model(input_ids=t, use_cache=False).logits[0, -1, :].float()
        STATE["repl"] = None
        lp = torch.log_softmax(lg, -1); return float(lp[DONE] - lp[READY]), int(torch.argmax(lg))
    def ysig(R, it): return R if it["target_sys"] == "DONE" else -R
    def repl_from(item_pos, src_cap, src_pos):
        if len(item_pos) != len(src_pos) or len(item_pos) == 0: return None
        ip = torch.tensor(item_pos, dtype=torch.long, device=dev)
        sp = torch.tensor(src_pos, dtype=torch.long, device=dev)
        return {L: (ip, src_cap[L][sp].to(torch.bfloat16)) for L in LAYERS}

    def seg(i, order):
        ids, reg, _ = PART[i]
        if order == "normal": return ids, reg
        fids, freg, _ = apply_flip(ids, reg); return fids, freg

    def M_of(pt, ptB):
        return float(-pt.mean() / (2 * ptB.mean())) if abs(ptB.mean()) > 1e-9 else float("nan")

    orders = ["normal", "flipped"]
    per = {}   # order -> per-item arrays
    void = {}
    for order in orders:
        # self-check
        i0 = use[0]; ids0, _ = seg(i0, order); c0 = capture(seg(twin_of[i0], order)[0])
        allp0 = list(range(len(ids0)))
        yb0, _ = run_R(ids0); ya0, _ = run_R(ids0, repl_from(allp0, c0, allp0))
        if abs(ya0 - yb0) < 1e-4:
            for h in handles: h.remove()
            raise SystemExit(f"SELFCHECK FAILED ({order}): all-pos twin-patch did not move Y")
        log(f"[R6F] {order} SELFCHECK ok (item0 {yb0:+.3f}->all {ya0:+.3f}) ({time.time()-t0:.0f}s)")
        Yb = np.zeros(N); Yall = np.zeros(N)
        Yreg = {g: np.zeros(N) for g in REGIONS}
        Yflo = {g: np.full(N, np.nan) for g in REGIONS}
        nfloor = {g: 0 for g in REGIONS}
        twin_hit = 0; twin_tot = 0
        for n, i in enumerate(use):
            it = stim[i]; ids, reg = seg(i, order); tw = twin_of[i]
            tids, _ = seg(tw, order); capt = capture(tids)
            allp = list(range(len(ids)))
            Rb, _ = run_R(ids); Yb[n] = ysig(Rb, it)
            Ra, arg_all = run_R(ids, repl_from(allp, capt, allp)); Yall[n] = ysig(Ra, it)
            _, arg_twin = run_R(tids)             # twin's own argmax (twin-based VOID target)
            twin_tot += 1; twin_hit += int(arg_all == arg_twin)
            for g in REGIONS:
                rp = repl_from(reg[g], capt, reg[g])
                Yreg[g][n] = ysig(run_R(ids, rp)[0], it) if rp is not None else Yb[n]
            sc = source_of(i)
            if sc is not None:
                sids, sreg = seg(sc, order); caps = capture(sids)
                for g in REGIONS:
                    rp = repl_from(reg[g], caps, sreg[g])
                    if rp is not None:
                        Yflo[g][n] = ysig(run_R(ids, rp)[0], it); nfloor[g] += 1
            if (n + 1) % 60 == 0: log(f"[R6F] {order} {n+1}/{N} ({time.time()-t0:.0f}s)")
        per[order] = dict(Yb=Yb, Yall=Yall, Yreg=Yreg, Yflo=Yflo, nfloor=nfloor, B=float(Yb.mean()))
        void[order] = twin_hit / max(1, twin_tot)
        log(f"[R6F] {order} B={Yb.mean():+.4f} twinVOID_hit={void[order]:.3f} "
            + " ".join(f"{g}:{nfloor[g]}" for g in REGIONS) + f" ({time.time()-t0:.0f}s)")
    for h in handles: h.remove()

    # ---- per-order M/Sigma + within-order bootstrap, and PAIRED dSigma bootstrap ----
    def per_t(a):
        return np.array([np.nanmean(a[tmpl == t]) if np.any((tmpl == t) & ~np.isnan(a)) else 0.0 for t in range(NTMPL)])
    ptB = {o: per_t(per[o]["Yb"]) for o in orders}
    ptR = {o: {g: per_t(per[o]["Yreg"][g] - per[o]["Yb"]) for g in REGIONS} for o in orders}
    ptA = {o: per_t(per[o]["Yall"] - per[o]["Yb"]) for o in orders}
    Mreg = {o: {g: M_of(ptR[o][g], ptB[o]) for g in REGIONS} for o in orders}
    Mall = {o: M_of(ptA[o], ptB[o]) for o in orders}
    Sigma = {o: sum(Mreg[o][g] for g in REGIONS) for o in orders}
    Sigma_KSI = {o: Mreg[o]["K"] + Mreg[o]["S"] + Mreg[o]["I"] for o in orders}

    rng = np.random.default_rng(SEED)
    keys = []
    for o in orders:
        keys += [f"{o}_Sigma", f"{o}_Sigma_KSI", f"{o}_all"] + [f"{o}_{g}" for g in REGIONS]
    keys += ["dSigma", "dSigma_KSI"] + [f"dM_{g}" for g in REGIONS]
    boot = {k: np.empty(BOOT) for k in keys}
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL)
        sig_b = {}
        for o in orders:
            den = 2 * ptB[o][pk].mean()
            if abs(den) < 1e-9:
                for k in keys: boot[k][b] = np.nan
                sig_b = None; break
            mr = {g: -ptR[o][g][pk].mean() / den for g in REGIONS}
            ma = -ptA[o][pk].mean() / den
            sg = sum(mr[g] for g in REGIONS); sksi = mr["K"] + mr["S"] + mr["I"]
            boot[f"{o}_Sigma"][b] = sg; boot[f"{o}_Sigma_KSI"][b] = sksi; boot[f"{o}_all"][b] = ma
            for g in REGIONS: boot[f"{o}_{g}"][b] = mr[g]
            sig_b[o] = (sg, sksi, mr)
        if sig_b is None: continue
        boot["dSigma"][b] = sig_b["flipped"][0] - sig_b["normal"][0]
        boot["dSigma_KSI"][b] = sig_b["flipped"][1] - sig_b["normal"][1]
        for g in REGIONS: boot[f"dM_{g}"][b] = sig_b["flipped"][2][g] - sig_b["normal"][2][g]
    def ci(a): lo, hi = np.nanpercentile(a, [2.5, 97.5]); return [float(lo), float(hi)]
    C = {k: ci(boot[k]) for k in keys}

    dSigma = Sigma["flipped"] - Sigma["normal"]
    # ---- gates + mechanical verdict ----
    repl_ok = abs(Sigma["normal"] - SIGMA_NORMAL_BANKED) <= REPL_TOL
    mall_ok = all(abs(Mall[o] - 1.0) <= 0.15 for o in orders)
    if not repl_ok:
        verdict = f"HARNESS-DRIFT (Sigma_normal={Sigma['normal']:.3f} vs banked {SIGMA_NORMAL_BANKED} +-{REPL_TOL}; do NOT interpret)"
    elif not mall_ok:
        verdict = f"HARNESS-PROBLEM (M_all off 1: normal {Mall['normal']:.3f} flipped {Mall['flipped']:.3f})"
    elif abs(dSigma) <= DSIG_THR and C["dSigma"][0] <= 0 <= C["dSigma"][1]:
        verdict = "ORDER-INVARIANT (dSigma~0: the super-additive redundancy is NOT a property of order; structural to content/decomposition)"
    elif C["dSigma"][0] > 0 or C["dSigma"][1] < 0:
        verdict = f"ORDER-DEPENDENT (dSigma={dSigma:+.3f} CI excludes 0: redundancy tracks order; see per-region dM)"
    else:
        verdict = "INCONCLUSIVE (dSigma CI wide, includes 0 but |dSigma|>thr)"

    np.savez(os.path.join(OUT, "res06_flip_peritem" + ("_smoke" if SMOKE else "") + ".npz"),
             use=np.array(use), tmpl=tmpl,
             **{f"{o}_Yb": per[o]["Yb"] for o in orders}, **{f"{o}_Yall": per[o]["Yall"] for o in orders},
             **{f"{o}_Y{g}": per[o]["Yreg"][g] for o in orders for g in REGIONS},
             **{f"{o}_Yflo_{g}": per[o]["Yflo"][g] for o in orders for g in REGIONS})
    out = {"prereg": "PREREG_RES06FLIP.md", "SMOKE": SMOKE,
           "chained_to_RES06": "076b270179f52c37c4f569f738544747fea63e90b226c8c7e24225afa8e79409",
           "transformers": transformers.__version__, "n_pairs": N, "n_skipped": len(stim) - N,
           "B": {o: per[o]["B"] for o in orders}, "twin_void_hit": void,
           "M_all": Mall, "M_all_ci": {o: C[f"{o}_all"] for o in orders},
           "Sigma": Sigma, "Sigma_ci": {o: C[f"{o}_Sigma"] for o in orders},
           "Sigma_KSI": Sigma_KSI, "Sigma_KSI_ci": {o: C[f"{o}_Sigma_KSI"] for o in orders},
           "M_by_region": {o: Mreg[o] for o in orders},
           "M_ci_by_region": {o: {g: C[f"{o}_{g}"] for g in REGIONS} for o in orders},
           "dSigma": dSigma, "dSigma_ci": C["dSigma"], "dSigma_KSI": Sigma_KSI["flipped"] - Sigma_KSI["normal"],
           "dSigma_KSI_ci": C["dSigma_KSI"], "dM_by_region": {g: Mreg["flipped"][g] - Mreg["normal"][g] for g in REGIONS},
           "dM_ci_by_region": {g: C[f"dM_{g}"] for g in REGIONS},
           "Sigma_normal_banked": SIGMA_NORMAL_BANKED, "replication_ok": repl_ok, "M_all_ok": mall_ok,
           "verdict": verdict, "runtime_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "res06_flip_arms" + ("_smoke" if SMOKE else "") + ".csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["order", "region", "M", "ci_lo", "ci_hi"])
        for o in orders:
            for g in REGIONS: w.writerow([o, g, round(Mreg[o][g],5), round(C[f"{o}_{g}"][0],5), round(C[f"{o}_{g}"][1],5)])
            w.writerow([o, "ALL(anchor)", round(Mall[o],5), round(C[f"{o}_all"][0],5), round(C[f"{o}_all"][1],5)])
            w.writerow([o, "Sigma", round(Sigma[o],5), round(C[f"{o}_Sigma"][0],5), round(C[f"{o}_Sigma"][1],5)])
        w.writerow(["delta", "Sigma", round(dSigma,5), round(C["dSigma"][0],5), round(C["dSigma"][1],5)])
        for g in REGIONS: w.writerow(["delta", g, round(Mreg["flipped"][g]-Mreg["normal"][g],5), round(C[f"dM_{g}"][0],5), round(C[f"dM_{g}"][1],5)])
    fn = os.path.join(OUT, "res06_flip" + ("_smoke" if SMOKE else "") + ".json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[R6F] Sigma normal={Sigma['normal']:+.3f}{C['normal_Sigma']} flipped={Sigma['flipped']:+.3f}{C['flipped_Sigma']} "
        f"| dSigma={dSigma:+.3f}{C['dSigma']} | B n={per['normal']['B']:+.2f} f={per['flipped']['B']:+.2f} "
        f"| twinVOID n={void['normal']:.2f} f={void['flipped']:.2f} -> {verdict}")
    log(f"[R6F] per-region M normal={ {g: round(Mreg['normal'][g],2) for g in REGIONS} } flipped={ {g: round(Mreg['flipped'][g],2) for g in REGIONS} }")
    log(f"[R6F] wrote {fn}")


if __name__ == "__main__":
    main()
