#!/usr/bin/env python
# OPX-02 -- does the OPX-01 one-sided asymmetry (A_sys -0.93 / A_usr +1.90) follow RECENCY or ROLE?
# Composes OPX-01's one-sided same-index span patch with ORD-01's block-order flip (BOS+USER-blk+SYSTEM-blk+asst, o2n remap).
# Cells per order (normal = system first/user last; flipped = user first/system last), twin activations, span positions, L8-31:
#   A_sys  item sys-span <- twin sys-span (same-index, sys only)
#   A_usr  item usr-span <- twin usr-span (same-index, usr only)
#   EXCH   cross two-sided (RES-02 Arm1 anchor, normal ~0.462)
#   CONSTR same two-sided (become-the-twin ~1.0 -- construction check per order, NEVER evidence)
# PRIMARY = raw dY in nats per order (B flips sign with order -> M normalization not comparable across orders; M reported per
# order with its own B as secondary). DISCRIMINATOR: does the twin-directed OVERSHOOT follow the LAST block (recency) or the
# USER role (role)? Recency => the role-labeled effects SWAP sign between orders; Role => they stay.
import os, json, time
import numpy as np, torch
from collections import defaultdict
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
LAYERS = list(range(8, 32))
DONE, READY = 71496, 46678
SH, EOT = 128006, 128009
NTMPL = 30; BOOT = 300 if SMOKE else 5000; SEED = 20260925
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
    log(f"[OPX2] model on {dev}; tf {transformers.__version__} L{LAYERS[0]}..{LAYERS[-1]} n={len(stim)} ({time.time()-t0:.0f}s)")

    def segment(it):
        imp_s = TEMPLATES[it["template_idx"]].format(T=it["target_sys"])
        imp_u = TEMPLATES[it["template_idx"]].format(T=it["target_usr"])
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]
        sh = [i for i, t in enumerate(ids) if t == SH]; eot = [i for i, t in enumerate(ids) if t == EOT]
        def sp(imp):
            cs = text.index(imp); ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        return ids, sp(imp_s), sp(imp_u), sh, eot

    def flip(ids, sh, eot):                                   # BOS/pre + USER-blk + SYSTEM-blk + assistant ; old->new map
        pre = list(range(0, sh[0]))
        sys_blk = list(range(sh[0], eot[0] + 1)); usr_blk = list(range(sh[1], eot[1] + 1))
        asst = list(range(sh[2], len(ids)))
        order = pre + usr_blk + sys_blk + asst
        return [ids[i] for i in order], {old: new for new, old in enumerate(order)}

    twin_g = defaultdict(dict)
    for i, it in enumerate(stim):
        twin_g[(it["template_idx"], it["filler_idx"], it["position"])][it["counterbalance"]] = i
    twin_of = {}
    for d in twin_g.values():
        if len(d) == 2: a, b = list(d.values()); twin_of[a] = b; twin_of[b] = a
    SEG = {i: segment(stim[i]) for i in range(len(stim))}

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
            lp = torch.log_softmax(model(input_ids=t, use_cache=False).logits[0, -1, :].float(), -1)
        STATE["repl"] = None
        return float(lp[DONE] - lp[READY]), float(torch.exp(lp[DONE]) + torch.exp(lp[READY]))
    def ysig(R, it): return R if it["target_sys"] == "DONE" else -R
    def capture(ids):
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        return {L: hs[L][0].detach().clone() for L in LAYERS}

    def build(cell, sidx, uidx, tsidx, tuidx, cap):
        """repl for a cell. sidx/uidx = item span idx (this order); tsidx/tuidx = twin span idx (this order); cap=twin cap."""
        out = {}
        for L in LAYERS:
            if cell == "A_sys":   pos, val = sidx, [cap[L][tsidx]]
            elif cell == "A_usr": pos, val = uidx, [cap[L][tuidx]]
            elif cell == "EXCH":  pos, val = sidx + uidx, [cap[L][tuidx], cap[L][tsidx]]
            elif cell == "CONSTR":pos, val = sidx + uidx, [cap[L][tsidx], cap[L][tuidx]]
            out[L] = (torch.tensor(pos, dtype=torch.long, device=dev), torch.cat(val, 0).to(torch.bfloat16))
        return out

    def usable(i):
        _, si, ui, _, _ = SEG[i]; tw = twin_of.get(i)
        if tw is None or not si or not ui or len(SEG[i][0]) != len(SEG[tw][0]): return False
        _, tsi, tui, _, _ = SEG[tw]
        return len(si) == len(tsi) and len(ui) == len(tui) and len(si) == len(tui) and len(ui) == len(tsi)
    use = [i for i in range(len(stim)) if usable(i)]
    if SMOKE: use = use[:40]
    log(f"[OPX2] usable={len(use)} skipped={len(stim)-len(use)} ({time.time()-t0:.0f}s)")

    CELLS = ["A_sys", "A_usr", "EXCH", "CONSTR"]
    tmpl = np.array([stim[i]["template_idx"] for i in use]); N = len(use)
    Ybn = np.zeros(N); Ybf = np.zeros(N); mB = np.zeros(N)
    Yn = {c: np.zeros(N) for c in CELLS}; Yf = {c: np.zeros(N) for c in CELLS}
    for n, i in enumerate(use):
        it = stim[i]; ids, si, ui, sh, eot = SEG[i]; tw = twin_of[i]
        tids, tsi, tui, tsh, teot = SEG[tw]
        fids, o2n = flip(ids, sh, eot); ftids, to2n = flip(tids, tsh, teot)
        fsi = [o2n[p] for p in si]; fui = [o2n[p] for p in ui]
        ftsi = [to2n[p] for p in tsi]; ftui = [to2n[p] for p in tui]
        capn = capture(tids); capf = capture(ftids)
        r, m = run(ids); Ybn[n] = ysig(r, it); mB[n] = m
        Ybf[n] = ysig(run(fids)[0], it)
        for c in CELLS:
            Yn[c][n] = ysig(run(ids,  build(c, si, ui, tsi, tui, capn))[0], it)
            Yf[c][n] = ysig(run(fids, build(c, fsi, fui, ftsi, ftui, capf))[0], it)
        if (n + 1) % 60 == 0: log(f"[OPX2] {n+1}/{N} ({time.time()-t0:.0f}s)")
    Bn = float(Ybn.mean()); Bf = float(Ybf.mean())
    for h in handles: h.remove()
    log(f"[OPX2] B_normal={Bn:+.4f} B_flipped={Bf:+.4f} massB={mB.mean():.3f} ({time.time()-t0:.0f}s)")

    # raw dY per cell per order (PRIMARY); M per order with its own B (secondary)
    def per_t(a): return np.array([a[tmpl == tt].mean() if (tmpl == tt).any() else 0.0 for tt in range(NTMPL)])
    dYn = {c: Yn[c] - Ybn for c in CELLS}; dYf = {c: Yf[c] - Ybf for c in CELLS}
    ptn = {c: per_t(dYn[c]) for c in CELLS}; ptf = {c: per_t(dYf[c]) for c in CELLS}
    ptBn = per_t(Ybn); ptBf = per_t(Ybf)
    dYn_m = {c: float(dYn[c].mean()) for c in CELLS}; dYf_m = {c: float(dYf[c].mean()) for c in CELLS}
    def Mof(pt, ptB): return float(-pt.mean() / (2 * ptB.mean())) if abs(ptB.mean()) > 1e-9 else float("nan")
    Mn = {c: Mof(ptn[c], ptBn) for c in CELLS}; Mf = {c: Mof(ptf[c], ptBf) for c in CELLS}

    rng = np.random.default_rng(SEED)
    # discriminator scalars (raw dY): role-keep = dYf_sys - dYn_sys (0 if role); recency-swap = dYf_sys - dYn_usr (0 if recency)
    bkeep = np.empty(BOOT); bswap = np.empty(BOOT); bkeepU = np.empty(BOOT); bswapU = np.empty(BOOT)
    bBn = np.empty(BOOT); bBf = np.empty(BOOT)
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL)
        s_n = ptn["A_sys"][pk].mean(); u_n = ptn["A_usr"][pk].mean(); s_f = ptf["A_sys"][pk].mean(); u_f = ptf["A_usr"][pk].mean()
        bkeep[b] = s_f - s_n; bswap[b] = s_f - u_n; bkeepU[b] = u_f - u_n; bswapU[b] = u_f - s_n
        bBn[b] = ptBn[pk].mean(); bBf[b] = ptBf[pk].mean()
    def ci(a): lo, hi = np.nanpercentile(a, [2.5, 97.5]); return [float(lo), float(hi)]
    keep_sys = dYf_m["A_sys"] - dYn_m["A_sys"]; swap_sys = dYf_m["A_sys"] - dYn_m["A_usr"]
    keep_usr = dYf_m["A_usr"] - dYn_m["A_usr"]; swap_usr = dYf_m["A_usr"] - dYn_m["A_sys"]

    # outcome: recency if role-labeled effects swap (flipped sys ~ normal usr, flipped usr ~ normal sys) and NOT keep
    def sg(x): return 1 if x > 0 else -1
    signs_swap = (sg(dYf_m["A_sys"]) == sg(dYn_m["A_usr"])) and (sg(dYf_m["A_usr"]) == sg(dYn_m["A_sys"]))
    signs_keep = (sg(dYf_m["A_sys"]) == sg(dYn_m["A_sys"])) and (sg(dYf_m["A_usr"]) == sg(dYn_m["A_usr"]))
    Bflips = (sg(Bn) != sg(Bf))
    if signs_swap and not signs_keep:
        verdict = "RECENCY (the one-sided asymmetry follows the LAST block; role-labeled effects swap sign under reversal)"
    elif signs_keep and not signs_swap:
        verdict = "ROLE (the asymmetry stays with the roles; recency and role come apart at the span level)"
    else:
        verdict = "MIXED (neither clean swap nor clean keep; report the table)"

    anchor_ok = abs(Mn["EXCH"] - 0.462) <= 0.05 and abs(Mn["A_sys"] - (-0.930)) <= 0.15 and abs(Mn["A_usr"] - 1.899) <= 0.20
    constr_ok = Mn["CONSTR"] >= 0.95 and Mf["CONSTR"] >= 0.95

    out = {"prereg": "PREREG_OPX02.md", "SMOKE": SMOKE,
           "chained_to_OPX01": "bd3604acc00e29ce473b87481f604193406cc3fa28108247f481efb0325bb42a",
           "transformers": transformers.__version__, "layers": LAYERS, "B_normal": Bn, "B_flipped": Bf,
           "B_flips_sign": bool(Bflips), "n_pairs": N, "mass_B": float(mB.mean()),
           "dY_normal": dYn_m, "dY_flipped": dYf_m, "M_normal": Mn, "M_flipped": Mf,
           "keep_sys_dYf_minus_dYn_sys": keep_sys, "keep_sys_ci": ci(bkeep),
           "swap_sys_dYf_minus_dYn_usr": swap_sys, "swap_sys_ci": ci(bswap),
           "keep_usr": keep_usr, "keep_usr_ci": ci(bkeepU), "swap_usr": swap_usr, "swap_usr_ci": ci(bswapU),
           "signs_swap": bool(signs_swap), "signs_keep": bool(signs_keep),
           "anchor_normal_reproduces_opx01": bool(anchor_ok), "construction_check_both_orders_ge_0.95": bool(constr_ok),
           "verdict": verdict,
           "scope": "Property of these spans/layers/model/battery under residual overwrite; B flips with order so raw dY is "
                    "primary and M is reported per-order. Tests whether the OPX-01 -0.93/+1.90 asymmetry is recency- or "
                    "role-bound; does not relocate arbitration. CONSTR ~1.0 is a construction identity, never evidence.",
           "runtime_s": round(time.time() - t0, 1)}
    import csv
    with open(os.path.join(OUT, "opx02_arms_smoke.csv" if SMOKE else "opx02_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["cell", "dY_normal", "dY_flipped", "M_normal", "M_flipped"])
        for c in CELLS: w.writerow([c, round(dYn_m[c], 4), round(dYf_m[c], 4), round(Mn[c], 4), round(Mf[c], 4)])
        w.writerow(["B", round(Bn, 4), round(Bf, 4), "", ""])
    np.savez(os.path.join(OUT, "opx02_peritem" + ("_smoke" if SMOKE else "") + ".npz"),
             use=np.array(use), tmpl=tmpl, Ybn=Ybn, Ybf=Ybf,
             **{f"Yn_{c}": Yn[c] for c in CELLS}, **{f"Yf_{c}": Yf[c] for c in CELLS})
    fn = os.path.join(OUT, "opx02_smoke.json" if SMOKE else "opx02.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[OPX2] dY_n={{" + ", ".join(f'{c}:{dYn_m[c]:+.2f}' for c in CELLS) + "}}")
    log(f"[OPX2] dY_f={{" + ", ".join(f'{c}:{dYf_m[c]:+.2f}' for c in CELLS) + "}}")
    log(f"[OPX2] Bflips={Bflips} swap={signs_swap} keep={signs_keep} anchor={anchor_ok} constr={constr_ok} -> {verdict}; wrote {fn}")

if __name__ == "__main__":
    main()
