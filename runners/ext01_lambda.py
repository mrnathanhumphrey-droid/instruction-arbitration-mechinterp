#!/usr/bin/env python
# EXT-01 (sharp 2-level, Llama) -- does adding the ROLE-WORD header token to the imperative-span cross-role exchange
# recover the "missing half" RES-02 left in place? Extends res02_lambda.py exactly (same battery, DONE/READY readout,
# cross-role residual overwrite at L8-31, content-matched twin). Arms:
#   L0    = imperative span only            (reproduces RES-02 Arm1 = anchor)
#   ROLE  = imperative span + role-word tok  (system 9125 / user 882 -- the role marker)
#   CTRL  = imperative span + end_header tok (128007, identical id in BOTH blocks -- shared, non-role-distinguishing;
#           position-matched, token-matched neutral control). marker gain = M(ROLE) - M(CTRL).
#   DISR  = same-role/diff-filler at L0      (RES-02 Arm2 disruption floor, for the L0 Arm1-Arm2 anchor)
# VOID inherited from RES-02 (uncontested same-content replacement keeps >=90% compliance).
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
SH, EH, EOT = 128006, 128007, 128009
NTMPL = 30; BOOT = 300 if SMOKE else 5000; SEED = 20260925
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
    log(f"[E1] model on {dev}; tf {transformers.__version__} L{LAYERS[0]}..{LAYERS[-1]} n={len(stim)} ({time.time()-t0:.0f}s)")

    def seg(it):
        imp_s = TEMPLATES[it["template_idx"]].format(T=it["target_sys"])
        imp_u = TEMPLATES[it["template_idx"]].format(T=it["target_usr"])
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]
        def span(imp):
            cs = text.index(imp); ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        shpos = [i for i, x in enumerate(ids) if x == SH]           # system, user, assistant openers
        meta = None
        if len(shpos) >= 2:
            rw_s, rw_u = shpos[0] + 1, shpos[1] + 1                 # role-word token = start_header +1
            eh_s, eh_u = shpos[0] + 2, shpos[1] + 2                 # end_header token
            ok = (ids[eh_s] == EH and ids[eh_u] == EH)             # structure sanity
            meta = {"rw_s": rw_s, "rw_u": rw_u, "eh_s": eh_s, "eh_u": eh_u, "ok": ok}
        return ids, span(imp_s), span(imp_u), meta

    twin_g = defaultdict(dict); src_g = defaultdict(list)
    for i, it in enumerate(stim):
        twin_g[(it["template_idx"], it["filler_idx"], it["position"])][it["counterbalance"]] = i
        src_g[(it["template_idx"], it["position"], it["counterbalance"])].append(i)
    twin_of = {}
    for d in twin_g.values():
        if len(d) == 2:
            a, b = list(d.values()); twin_of[a] = b; twin_of[b] = a
    def source_of(i):
        it = stim[i]; cand = [j for j in src_g[(it["template_idx"], it["position"], it["counterbalance"])] if j != i]
        return cand[0] if cand else None

    SEG = {i: seg(stim[i]) for i in range(len(stim))}

    def capture(i):
        ids, si, ui, m = SEG[i]
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        cap = {}
        for L in LAYERS:
            h = hs[L][0]
            cap[L] = {"s": h[si, :].detach().clone(), "u": h[ui, :].detach().clone(),
                      "rw_s": h[m["rw_s"], :].detach().clone(), "rw_u": h[m["rw_u"], :].detach().clone(),
                      "eh_s": h[m["eh_s"], :].detach().clone(), "eh_u": h[m["eh_u"], :].detach().clone()}
        return cap

    STATE = {"repl": None}; handles = []
    def make_hook(L):
        def hook(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            r = STATE["repl"]
            if r is not None and L in r:
                pos, val = r[L]; h[0, pos, :] = val
            return out
        return hook
    for L in LAYERS:
        handles.append(model.model.layers[L - 1].register_forward_hook(make_hook(L)))

    def run(ids, repl=None):
        STATE["repl"] = repl
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lp = torch.log_softmax(model(input_ids=t, use_cache=False).logits[0, -1, :].float(), -1)
        STATE["repl"] = None
        return float(lp[DONE] - lp[READY]), float(torch.exp(lp[DONE]) + torch.exp(lp[READY]))
    def ysig(R, it): return R if it["target_sys"] == "DONE" else -R

    def repl_cross(i, cap_tw, extra):
        """item sys-region <- twin usr-region ; item usr-region <- twin sys-region. extra in {None,'rw','eh'}."""
        ids, si, ui, m = SEG[i]; repl = {}
        for L in LAYERS:
            pos = []; val = []
            if extra:
                pos.append(m[extra + "_s"]); val.append(cap_tw[L][extra + "_u"].unsqueeze(0))
            pos += si; val.append(cap_tw[L]["u"])
            if extra:
                pos.append(m[extra + "_u"]); val.append(cap_tw[L][extra + "_s"].unsqueeze(0))
            pos += ui; val.append(cap_tw[L]["s"])
            repl[L] = (torch.tensor(pos, dtype=torch.long, device=dev), torch.cat(val, 0).to(torch.bfloat16))
        return repl
    def repl_same(i, cap_src):                                  # DISR: same-role diff-filler, span only (RES-02 Arm2)
        ids, si, ui, m = SEG[i]; repl = {}
        for L in LAYERS:
            repl[L] = (torch.tensor(si + ui, dtype=torch.long, device=dev),
                       torch.cat([cap_src[L]["s"], cap_src[L]["u"]], 0).to(torch.bfloat16))
        return repl

    def match(i, j):                                            # cross span-lengths align
        _, si, ui, _ = SEG[i]; _, sj, uj, _ = SEG[j]
        return len(si) == len(uj) and len(ui) == len(sj)
    def match_same(i, j):
        _, si, ui, _ = SEG[i]; _, sj, uj, _ = SEG[j]
        return len(si) == len(sj) and len(ui) == len(uj)

    # G-SEGMENT: usable = twin+source present, spans non-empty & aligned, header meta ok
    use = []
    for i in range(len(stim)):
        j = twin_of.get(i); s = source_of(i); _, si, ui, m = SEG[i]
        if j is None or s is None or not si or not ui or m is None or not m["ok"]: continue
        if match(i, j) and match_same(i, s): use.append(i)
    if SMOKE: use = use[:40]
    n_skip = len(stim) - len(use)
    log(f"[E1] usable={len(use)} skipped={n_skip} ({time.time()-t0:.0f}s)")

    # self-check: role-word arm must differ from baseline on item0
    i0 = use[0]; yb0, _ = run(SEG[i0][0]); ct = capture(twin_of[i0])
    yr0, _ = run(SEG[i0][0], repl_cross(i0, ct, "rw"))
    if abs(yr0 - yb0) < 1e-4:
        for h in handles: h.remove()
        raise SystemExit(f"SELFCHECK FAILED: role arm did not move Y (base {yb0:.4f} role {yr0:.4f})")
    log(f"[E1] SELFCHECK ok (item0 base {yb0:+.4f} -> role {yr0:+.4f})")

    tmpl = np.array([stim[i]["template_idx"] for i in use])
    Yb = np.zeros(len(use)); mB = np.zeros(len(use))
    YL0 = np.zeros(len(use)); Yrw = np.zeros(len(use)); Yeh = np.zeros(len(use)); Ydi = np.zeros(len(use))
    mL0 = np.zeros(len(use)); mrw = np.zeros(len(use))
    for n, i in enumerate(use):
        it = stim[i]; ids = SEG[i][0]; ct = capture(twin_of[i]); cs = capture(source_of(i))
        r, m = run(ids); Yb[n] = ysig(r, it); mB[n] = m
        r, m = run(ids, repl_cross(i, ct, None)); YL0[n] = ysig(r, it); mL0[n] = m
        r, m = run(ids, repl_cross(i, ct, "rw")); Yrw[n] = ysig(r, it); mrw[n] = m
        r, _ = run(ids, repl_cross(i, ct, "eh")); Yeh[n] = ysig(r, it)
        r, _ = run(ids, repl_same(i, cs)); Ydi[n] = ysig(r, it)
        if (n + 1) % 120 == 0: log(f"[E1] {n+1}/{len(use)} ({time.time()-t0:.0f}s)")
    B = float(Yb.mean()); log(f"[E1] B={B:+.4f} massB={mB.mean():.3f} massL0={mL0.mean():.3f} massROLE={mrw.mean():.3f} ({time.time()-t0:.0f}s)")

    # VOID (uncontested, same-content replacement) -- identical to RES-02
    uncsel = unc[::FLOOR_STRIDE]
    def unc_seg(it):
        try:
            imp = TEMPLATES[it["template_idx"]].format(T=it["target"])
            msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
            text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
            ids = enc["input_ids"]; offs = enc["offset_mapping"]
            cs = text.index(imp); ce = cs + len(imp)
            sp = [k for k, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
            return ids, sp
        except Exception:
            return None
    def ucomply(ids, repl=None):
        STATE["repl"] = repl; t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lp = torch.log_softmax(model(input_ids=t, use_cache=False).logits[0, -1, :].float(), -1)
        STATE["repl"] = None
        return 1 if (lp[DONE] - lp[READY]) > 0 else 0
    uok = un = 0
    for it in uncsel:
        s = unc_seg(it)
        if s and s[1]: un += 1; uok += ucomply(s[0])
    floor_uns = uok / max(1, un)
    grp = defaultdict(list)
    for k, it in enumerate(uncsel): grp[(it["template_idx"], it["position"], it["slot"], it["target"])].append(k)
    sok = sn = 0
    for k, it in enumerate(uncsel):
        s = unc_seg(it)
        if not s or not s[1]: continue
        cand = [mm for mm in grp[(it["template_idx"], it["position"], it["slot"], it["target"])] if mm != k]
        if not cand: continue
        ss = unc_seg(uncsel[cand[0]])
        if not ss or len(ss[1]) != len(s[1]): continue
        t = torch.tensor([ss[0]], dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        repl = {L: (torch.tensor(s[1], dtype=torch.long, device=dev), hs[L][0, ss[1], :].to(torch.bfloat16)) for L in LAYERS}
        sn += 1; sok += ucomply(s[0], repl)
    floor_steer = sok / max(1, sn) if sn else float("nan")
    for h in handles: h.remove()
    thresh = 0.90 * floor_uns; VOID = bool(sn > 0 and floor_steer < thresh)
    log(f"[E1] floor uns {floor_uns:.3f}(n{un}) steer {floor_steer:.3f}(n{sn}) thr {thresh:.3f} VOID={VOID}")

    # M + paired template-cluster bootstrap
    def per_t(a): return np.array([a[tmpl == tt].mean() if (tmpl == tt).any() else 0.0 for tt in range(NTMPL)])
    ptB = per_t(Yb)
    dL0 = YL0 - Yb; drw = Yrw - Yb; deh = Yeh - Yb; ddi = Ydi - Yb
    ptL0, ptrw, pteh, ptdi = per_t(dL0), per_t(drw), per_t(deh), per_t(ddi)
    def M_of(pt): return float(-pt.mean() / (2 * ptB.mean())) if abs(ptB.mean()) > 1e-9 else float("nan")
    ML0, Mrw, Meh, Mdi = M_of(ptL0), M_of(ptrw), M_of(pteh), M_of(ptdi)
    rng = np.random.default_rng(SEED)
    bL0 = np.empty(BOOT); brw = np.empty(BOOT); beh = np.empty(BOOT); bgain = np.empty(BOOT); banch = np.empty(BOOT)
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL); den = 2 * ptB[pk].mean()
        if abs(den) < 1e-9: bL0[b] = brw[b] = beh[b] = bgain[b] = banch[b] = np.nan; continue
        mL = -ptL0[pk].mean() / den; mr = -ptrw[pk].mean() / den; me = -pteh[pk].mean() / den; md = -ptdi[pk].mean() / den
        bL0[b] = mL; brw[b] = mr; beh[b] = me; bgain[b] = mr - me; banch[b] = mL - md
    def ci(a): lo, hi = np.nanpercentile(a, [2.5, 97.5]); return [float(lo), float(hi)]
    cL0, crw, ceh, cgain, canch = ci(bL0), ci(brw), ci(beh), ci(bgain), ci(banch)
    marker_gain = Mrw - Meh                                     # role-word over shared-header control

    anchor_ok = abs(ML0 - 0.462) <= 0.05                        # reproduce RES-02 Arm1
    if VOID:
        verdict = "VOID -- not a null"
    elif marker_gain >= 0.10 and cgain[0] > 0 and Mrw > ML0:
        verdict = "MARKER-CARRIES (role-word inclusion recovers a real chunk of the missing half)"
    elif cgain[0] <= 0 <= cgain[1] or abs(marker_gain) < 0.05:
        verdict = "MARKER-INERT (role word does not carry the missing half either -- 6th readable-feature null)"
    else:
        verdict = "INTERMEDIATE (marker gain small but nonzero; report, no headline)"

    out = {"prereg": "PREREG_EXT01.md", "SMOKE": SMOKE,
           "chained_to_TPL01_PHASE23": "08d2f0827031b1f4707052b438ae111696b56eb3583c733d3f0483c3cbb661d6",
           "transformers": transformers.__version__, "layers": LAYERS, "B": B, "n_pairs": len(use), "n_skipped": n_skip,
           "M_L0_imperative": ML0, "M_L0_ci": cL0, "M_ROLE_word": Mrw, "M_ROLE_ci": crw,
           "M_CTRL_endhdr": Meh, "M_CTRL_ci": ceh, "marker_gain_role_minus_ctrl": marker_gain, "marker_gain_ci": cgain,
           "M_DISR_disruption": Mdi, "M_L0_minus_DISR": ML0 - Mdi, "M_L0_minus_DISR_ci": canch,
           "dY_L0": float(dL0.mean()), "dY_ROLE": float(drw.mean()), "dY_CTRL": float(deh.mean()),
           "mass_B": float(mB.mean()), "mass_L0": float(mL0.mean()), "mass_ROLE": float(mrw.mean()),
           "anchor_L0_reproduces_RES02_0.462_pm0.05": bool(anchor_ok),
           "floor_unsteered": floor_uns, "floor_steered": floor_steer, "VOID": VOID, "verdict": verdict,
           "scope": "Property of the EXCHANGE operation; RES-06 twin-patch reached ~0.997 where exchange got 0.462 at "
                    "identical positions. No number here is 'the ceiling on role arbitration', only 'under exchange'. "
                    "On Llama the only cross-role-swappable role-distinguishing marker token is the role word; delimiters "
                    "are shared (inert to swap) and the system date preamble is asymmetric (unalignable) -- so this is the "
                    "sharp form of the extent question, not a graded curve.",
           "runtime_s": round(time.time() - t0, 1)}
    import csv
    with open(os.path.join(OUT, "ext01_arms_smoke.csv" if SMOKE else "ext01_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["arm", "M", "ci_lo", "ci_hi", "dY"])
        w.writerow(["L0_imperative", round(ML0, 5), round(cL0[0], 5), round(cL0[1], 5), round(float(dL0.mean()), 5)])
        w.writerow(["ROLE_word", round(Mrw, 5), round(crw[0], 5), round(crw[1], 5), round(float(drw.mean()), 5)])
        w.writerow(["CTRL_endhdr", round(Meh, 5), round(ceh[0], 5), round(ceh[1], 5), round(float(deh.mean()), 5)])
        w.writerow(["marker_gain", round(marker_gain, 5), round(cgain[0], 5), round(cgain[1], 5), ""])
        w.writerow(["DISR", round(Mdi, 5), "", "", round(float(ddi.mean()), 5)])
    np.savez(os.path.join(OUT, "ext01_peritem" + ("_smoke" if SMOKE else "") + ".npz"),
             use=np.array(use), tmpl=tmpl, Yb=Yb, YL0=YL0, Yrw=Yrw, Yeh=Yeh, Ydi=Ydi, mB=mB, mL0=mL0, mrw=mrw)
    fn = os.path.join(OUT, "ext01_smoke.json" if SMOKE else "ext01.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[E1] L0={ML0:+.4f}{cL0} ROLE={Mrw:+.4f}{crw} CTRL={Meh:+.4f}{ceh} gain={marker_gain:+.4f}{cgain} "
        f"anchor_ok={anchor_ok} VOID={VOID} -> {verdict}; wrote {fn}")

if __name__ == "__main__":
    main()
