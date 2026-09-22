#!/usr/bin/env python
# RES-02 -- lens-free ceiling: full-residual CROSS-ROLE EXCHANGE. PREREG_RES02.md, chained RES-01b d00e8852...
# No probe, no subspace, no linearity. At every layer L8-31, OVERWRITE item i's imperative-span residual with the
# content-matched twin's opposite-slot span residual (same imperative, swapped provenance). M=-dY/(2B) signed by
# counterbalance, template-cluster bootstrap. Arm1 cross-role (treat); Arm2 same-role/same-target/diff-filler
# (disruption floor); VOID on uncontested (same-content replacement must keep >=90% compliance). Report Arm1-Arm2
# first. Reuses H4 hook harness (layers L8-31), blocks_and_imp span segmentation.
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
NTMPL = 30
BOOT = 300 if SMOKE else 5000
SEED = 20260914
SH, EOT = 128006, 128009
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
    log(f"[R2] model on {dev}; tf {transformers.__version__} L{LAYERS[0]}..{LAYERS[-1]} n={len(stim)} ({time.time()-t0:.0f}s)")

    def blocks_and_imp(it):
        imp_s = TEMPLATES[it["template_idx".format(T=it["target_sys"])
        imp_u = TEMPLATES[it["template_idx".format(T=it["target_usr"])
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]
        def span(imp):
            cs = text.index(imp); ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        return ids, span(imp_s), span(imp_u)

    # ---- pairings ----
    twin_g = defaultdict(dict)   # (tmpl,filler,pos) -> {cb: idx}
    src_g = defaultdict(list)    # (tmpl,pos,cb) -> [idx...]  (same target, vary filler)
    for i, it in enumerate(stim):
        twin_g[(it["template_idx"], it["filler_idx"], it["position"])][it["counterbalance" = i
        src_g[(it["template_idx"], it["position"], it["counterbalance"])].append(i)
    twin_of = {}
    for d in twin_g.values():
        if len(d) == 2:
            a, b = list(d.values()); twin_of[a] = b; twin_of[b] = a
    def source_of(i):
        it = stim[i]; cand = [j for j in src_g[(it["template_idx"], it["position"], it["counterbalance"])] if j != i]
        return cand[0] if cand else None

    SEG = {i: blocks_and_imp(stim[i]) for i in range(len(stim))}

    # ---- capture per-layer span residuals from a clean forward ----
    def capture(i):
        ids, si, ui = SEG[i]
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        cap = {}
        for L in LAYERS:
            cap[L] = {"s": hs[L][0, si, :].detach().clone(), "u": hs[L][0, ui, :].detach().clone()}
        return cap

    # ---- replacement hooks (H4-style, but overwrite specific span positions) ----
    STATE = {"repl": None}   # repl: {L: (pos_long_tensor, val_bf16_tensor)}
    handles = []
    def make_hook(L):
        def hook(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            r = STATE["repl"]
            if r is not None and L in r:
                pos, val = r[L]
                h[0, pos, :] = val
            return out
        return hook
    for L in LAYERS:
        handles.append(model.model.layers[L - 1].register_forward_hook(make_hook(L)))

    def run(ids, repl=None):
        STATE["repl"] = repl
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lg = model(input_ids=t, use_cache=False).logits[0, -1, :].float()
        STATE["repl"] = None
        lp = torch.log_softmax(lg, -1); return float(lp[DONE] - lp[READY])
    def ysig(R, it): return R if it["target_sys"] == "DONE" else -R

    def build_repl_cross(i, cap_twin):
        """item i's sys-span <- twin's usr-span (content X); usr-span <- twin's sys-span (content Y)."""
        ids, si, ui = SEG[i]; repl = {}
        for L in LAYERS:
            pos = []; val = []
            if si and len(si) == cap_twin[L]["u"].shape[0]:
                pos += si; val.append(cap_twin[L]["u"])
            if ui and len(ui) == cap_twin[L]["s"].shape[0]:
                pos += ui; val.append(cap_twin[L]["s"])
            if pos:
                repl[L] = (torch.tensor(pos, dtype=torch.long, device=dev), torch.cat(val, 0).to(torch.bfloat16))
        return repl
    def build_repl_same(i, cap_src):
        """item i's sys-span <- source's sys-span; usr-span <- source's usr-span (same role, diff filler)."""
        ids, si, ui = SEG[i]; repl = {}
        for L in LAYERS:
            pos = []; val = []
            if si and len(si) == cap_src[L]["s"].shape[0]:
                pos += si; val.append(cap_src[L]["s"])
            if ui and len(ui) == cap_src[L]["u"].shape[0]:
                pos += ui; val.append(cap_src[L]["u"])
            if pos:
                repl[L] = (torch.tensor(pos, dtype=torch.long, device=dev), torch.cat(val, 0).to(torch.bfloat16))
        return repl

    def spans_match(i, j, cross):
        _, si, ui = SEG[i]; _, sj, uj = SEG[j]
        return (len(si) == len(uj) and len(ui) == len(sj)) if cross else (len(si) == len(sj) and len(ui) == len(uj))

    # ---- items usable: have twin + source + matching spans for both arms ----
    use = []
    for i in range(len(stim)):
        j = twin_of.get(i); s = source_of(i)
        if j is None or s is None: continue
        if not SEG[i][1] or not SEG[i][2]: continue          # need both imperative spans
        if spans_match(i, j, True) and spans_match(i, s, False): use.append(i)
    if SMOKE: use = use[:40]
    n_skip = len(stim) - len(use)
    log(f"[R2] usable items={len(use)} skipped={n_skip} ({time.time()-t0:.0f}s)")

    # ---- self-check: cross-role must move item0 ----
    i0 = use[0]; yb0 = run(SEG[i0][0]); r0 = build_repl_cross(i0, capture(twin_of[i0])); yt0 = run(SEG[i0][0], r0)
    if abs(yt0 - yb0) < 1e-4:
        for h in handles: h.remove()
        raise SystemExit(f"SELFCHECK FAILED: cross-role exchange did not move Y (base {yb0:.4f} treat {yt0:.4f})")
    log(f"[R2] SELFCHECK ok (item0 base {yb0:+.4f} -> cross {yt0:+.4f})")

    # ---- main loop ----
    tmpl = np.array([stim[i]["template_idx"] for i in use])
    Yb = np.zeros(len(use)); Y1 = np.zeros(len(use)); Y2 = np.zeros(len(use))
    for n, i in enumerate(use):
        it = stim[i]; ids = SEG[i][0]
        Yb[n] = ysig(run(ids), it)
        Y1[n] = ysig(run(ids, build_repl_cross(i, capture(twin_of[i]))), it)
        Y2[n] = ysig(run(ids, build_repl_same(i, capture(source_of(i)))), it)
        if (n + 1) % 120 == 0: log(f"[R2] {n+1}/{len(use)} ({time.time()-t0:.0f}s)")
    B = float(Yb.mean()); log(f"[R2] baseline B={B:+.4f} ({time.time()-t0:.0f}s)")

    # ---- VOID: uncontested single-instruction span, same-content replacement, compliance >=90% ----
    # uncontested items have {slot, target} (no target_sys/usr). imperative = TEMPLATE.format(target) in the slot.
    uncsel = unc[::FLOOR_STRIDE]
    def unc_span(it):
        try:
            imp = TEMPLATES[it["template_idx".format(T=it["target"])
            msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
            text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
            ids = enc["input_ids"]; offs = enc["offset_mapping"]
            cs = text.index(imp); ce = cs + len(imp)
            sp = [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
            return ids, sp
        except Exception:
            return None
    def ucomply(ids, repl=None):
        STATE["repl"] = repl; t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lp = torch.log_softmax(model(input_ids=t, use_cache=False).logits[0, -1, :].float(), -1)
        STATE["repl"] = None
        return 1 if (lp[DONE] - lp[READY]) > 0 else 0
    # unsteered floor
    uok = un = 0
    for it in uncsel:
        seg = unc_span(it)
        if seg is None or not seg[1]: continue
        un += 1; uok += ucomply(seg[0])
    floor_uns = uok / max(1, un)
    # steered: replace the instruction span with a SAME-(template,position,slot,target) different-item span
    # (identical imperative string, foreign filler context) -> same content, tests patch destructiveness only
    grp = defaultdict(list)
    for k, it in enumerate(uncsel): grp[(it["template_idx"], it["position"], it["slot"], it["target"])].append(k)
    sok = sn = 0
    for k, it in enumerate(uncsel):
        seg = unc_span(it)
        if seg is None or not seg[1]: continue
        cand = [m for m in grp[(it["template_idx"], it["position"], it["slot"], it["target"])] if m != k]
        if not cand: continue
        ssg = unc_span(uncsel[cand[0)
        if ssg is None or len(ssg[1]) != len(seg[1]): continue
        t = torch.tensor([ssg[0, dtype=torch.long, device=dev)
        with torch.inference_mode():
            hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
        repl = {L: (torch.tensor(seg[1], dtype=torch.long, device=dev), hs[L][0, ssg[1], :].to(torch.bfloat16)) for L in LAYERS}
        sn += 1; sok += ucomply(seg[0], repl)
    floor_steer = sok / max(1, sn) if sn else float("nan")
    for h in handles: h.remove()
    thresh = 0.90 * floor_uns
    VOID = bool(sn > 0 and floor_steer < thresh)
    log(f"[R2] floor: unsteered {floor_uns:.3f} (n={un}) steered {floor_steer:.3f} (n={sn}) thr {thresh:.3f} VOID={VOID}")

    # ---- M + paired template-cluster bootstrap ----
    def per_t(a): return np.array([a[tmpl == t].mean() if (tmpl == t).any() else 0.0 for t in range(NTMPL)])
    ptB = per_t(Yb); d1 = Y1 - Yb; d2 = Y2 - Yb; pt1 = per_t(d1); pt2 = per_t(d2)
    def M_of(pt):
        return float(-pt.mean() / (2 * ptB.mean())) if abs(ptB.mean()) > 1e-9 else float("nan")
    M1 = M_of(pt1); M2 = M_of(pt2); Mdiff = M1 - M2
    rng = np.random.default_rng(SEED); B1 = np.empty(BOOT); B2 = np.empty(BOOT); BD = np.empty(BOOT)
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL); den = 2 * ptB[pk].mean()
        if abs(den) < 1e-9: B1[b] = B2[b] = BD[b] = np.nan; continue
        m1 = -pt1[pk].mean() / den; m2 = -pt2[pk].mean() / den
        B1[b] = m1; B2[b] = m2; BD[b] = m1 - m2
    def ci(a): lo, hi = np.nanpercentile(a, [2.5, 97.5]); return [float(lo), float(hi)]
    c1, c2, cd = ci(B1), ci(B2), ci(BD)

    if VOID:
        verdict = "VOID (patch lobotomizes model) -- NOT a null"
    elif M1 >= 0.80 and c1[0] > 0.70:
        verdict = "CEILING-HIGH (complete residual exchange accounts for ~the arbitration; residual carries it)"
    elif M1 <= 0.60:
        verdict = "CEILING-HALF-OR-LESS (even complete exchange ~half -> remainder not in residual at these positions)"
    else:
        verdict = "INTERMEDIATE (decomposition load-bearing; position-import control needed before claims)"
    arm1_gg_arm2 = bool(cd[0] > 0)

    out = {"prereg": "PREREG_RES02.md", "SMOKE": SMOKE,
           "chained_to_RES01B": "d00e885241a61246f9aabcd23abae9157488013d1b16e49b79bbe1eb9308d9b0",
           "transformers": transformers.__version__, "layers": LAYERS, "B": B,
           "n_pairs": len(use), "n_skipped": n_skip,
           "M1_cross_role": M1, "M1_ci": c1, "M2_disruption": M2, "M2_ci": c2,
           "M1_minus_M2": Mdiff, "M1_minus_M2_ci": cd, "arm1_gg_arm2": arm1_gg_arm2,
           "dY1": float(d1.mean()), "dY2": float(d2.mean()),
           "floor_unsteered": floor_uns, "floor_steered": floor_steer, "void_threshold": thresh, "VOID": VOID,
           "verdict": verdict,
           "limitation": "Arm1 imports twin POSITION with provenance (PREREG §2b); ceiling reading robust, "
                         "decomposition not. Arm2 is a conservative (lower-bound) disruption floor.",
           "runtime_s": round(time.time() - t0, 1)}
    import csv
    with open(os.path.join(OUT, "res02_arms_smoke.csv" if SMOKE else "res02_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["arm", "M", "ci_lo", "ci_hi", "dY", "n_pairs", "VOID"])
        w.writerow(["cross_role", round(M1, 5), round(c1[0], 5), round(c1[1], 5), round(float(d1.mean()), 5), len(use), VOID])
        w.writerow(["same_role_disruption", round(M2, 5), round(c2[0], 5), round(c2[1], 5), round(float(d2.mean()), 5), len(use), VOID])
        w.writerow(["cross_minus_disruption", round(Mdiff, 5), round(cd[0], 5), round(cd[1], 5), "", len(use), VOID])
    fn = os.path.join(OUT, "res02_smoke.json" if SMOKE else "res02.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[R2] M1={M1:+.4f} CI{c1} M2={M2:+.4f} CI{c2} M1-M2={Mdiff:+.4f} CI{cd} VOID={VOID} -> {verdict}; wrote {fn}")

if __name__ == "__main__":
    main()
