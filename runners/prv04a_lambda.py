#!/usr/bin/env python
# PRV-04a -- is the arbitration ROUTED? CONSTRUCTED BLOCK-SWAP (supersedes PRV-04 twin-swap).
# PREREG_PRV04A.md (sha folded at lock), chained to ATT-01c c99fdaa9...84.
# At the generation-position query row, for each target head, EXCHANGE the total attention mass between the two
# role blocks (shape-preserving, mass-preserving): new alpha[sys]=alpha[sys]*(m_usr/m_sys),
# new alpha[usr]=alpha[usr]*(m_sys/m_usr). No twin -- non-trivial by construction (no-op only if m_sys==m_usr).
# Attention analog of H4's residual projection-exchange. M_att=-dY/(2B), dY=Y_patched-Y_baseline signed by
# counterbalance, template-cluster bootstrap -- same scale as M. Arms from ATT-01c survivors (the clean set).
# Guards: VOID (same swap on uncontested, compliance>=90%) + plumbing (post==constructed, 0 weight) +
# swap-magnitude gate (TV(swapped,own)>=0.05). Per-level M_att reported as the shared-sign guard (ATT-01c lesson).
import os, json, time, csv
import numpy as np, torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.models.llama.modeling_llama import apply_rotary_pos_emb, repeat_kv

_TFV = tuple(int(x) for x in transformers.__version__.split(".")[:2])
THREE_TUPLE = _TFV < (4, 46)

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
DONE, READY = 71496, 46678
NTMPL = 30
SH, EOT = 128006, 128009
BOOT = 200 if SMOKE else 5000
SEED = 20260914
VOID_N = 30 if SMOKE else 120
PLUMB_EVERY = 40                       # sample plumbing/swap_tv on 1 in N items (0 inferential weight)
def log(*a): print(*a, flush=True)

STATE = {"bs": None, "cap": None}      # bs: {"sys":LongTensor,"usr":LongTensor,"layers":{L:set(h)}} ; cap: {"want":{L:[h]},"out":{}}

def build_fwd(mod, lidx):
    cfg = mod.config
    H = getattr(mod, "num_heads", None) or cfg.num_attention_heads
    KV = getattr(mod, "num_key_value_heads", None) or cfg.num_key_value_heads
    hd = mod.head_dim
    groups = getattr(mod, "num_key_value_groups", None) or (H // KV)
    scaling = getattr(mod, "scaling", None) or (hd ** -0.5)
    def fwd(hidden_states, position_embeddings=None, attention_mask=None, **kw):
        b, q_len, _ = hidden_states.shape
        q = mod.q_proj(hidden_states).view(b, q_len, H, hd).transpose(1, 2)
        k = mod.k_proj(hidden_states).view(b, q_len, KV, hd).transpose(1, 2)
        v = mod.v_proj(hidden_states).view(b, q_len, KV, hd).transpose(1, 2)
        cos, sin = position_embeddings
        q, k = apply_rotary_pos_emb(q, k, cos, sin)
        key = repeat_kv(k, groups); value = repeat_kv(v, groups)
        aw = torch.matmul(q, key.transpose(2, 3)) * scaling
        if attention_mask is not None:
            aw = aw + attention_mask[:, :, :, :key.shape[-2
        aw = torch.softmax(aw, dim=-1, dtype=torch.float32).to(q.dtype)
        bs = STATE["bs"]
        if bs is not None and lidx in bs["layers"]:
            sys_i = bs["sys"]; usr_i = bs["usr"]
            for h in bs["layers"][lidx]:
                row = aw[0, h, -1, :]                       # view into aw (generation-position row)
                ms = float(row[sys_i].sum()); mu = float(row[usr_i].sum())
                row[sys_i] = row[sys_i] * (mu / ms) if ms > 1e-4 else torch.full_like(row[sys_i], mu / max(1, sys_i.numel()))
                row[usr_i] = row[usr_i] * (ms / mu) if mu > 1e-4 else torch.full_like(row[usr_i], ms / max(1, usr_i.numel()))
        cap = STATE["cap"]
        if cap is not None and lidx in cap["want"]:
            for h in cap["want"][lidx]:
                cap["out"][(lidx, h)] = aw[0, h, -1, :].detach().float().cpu().numpy()
        out = mod.o_proj(torch.matmul(aw, value).transpose(1, 2).contiguous().view(b, q_len, -1))
        return (out, None, None) if THREE_TUPLE else (out, None)
    return fwd

def main():
    global THREE_TUPLE
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_contested.jsonl"), encoding="utf-8")]
    unc = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_uncontested.jsonl"), encoding="utf-8")]
    if SMOKE:
        pos = [it for it in stim if it["target_sys"] == "DONE"][:30]
        neg = [it for it in stim if it["target_sys"] != "DONE"][:30]
        stim = pos + neg
    from make_stimuli import TEMPLATES

    # ---- arms from ATT-01c survivors (att01c_withinlevel.csv) + bookkeeper from att01_heads.csv ----
    wl = list(csv.DictReader(open(os.path.join(HERE, "att01c_withinlevel.csv"))))
    def LHc(r): return (int(r["layer"]), int(r["head"]))
    def robust_blk(r): return min(abs(float(r["blk_r_p"])), abs(float(r["blk_r_m"])))
    def robust_imp(r): return min(abs(float(r["imp_r_p"])), abs(float(r["imp_r_m"])))
    blk_pass = [LHc(r) for r in sorted([r for r in wl if r["pass_blk_010"] == "True"], key=lambda r: -robust_blk(r))]
    imp_pass = [LHc(r) for r in sorted([r for r in wl if r["pass_imp_010"] == "True"], key=lambda r: -robust_imp(r))]
    nonpass = [LHc(r) for r in wl if r["pass_blk_010"] != "True" and r["pass_imp_010"] != "True"]
    log(f"[P4a] survivors: blk_pass={len(blk_pass)} imp_pass={len(imp_pass)} nonpass={len(nonpass)}")

    ar = list(csv.DictReader(open(os.path.join(HERE, "att01_heads.csv"))))
    def f(r, c): return float(r[c])
    def tb(r, c): return r[c] == "True"
    def alloc_sig(r): return (f(r, "alloc_imp_lo") > 0 or f(r, "alloc_imp_hi") < 0 or
                              f(r, "alloc_blk_lo") > 0 or f(r, "alloc_blk_hi") < 0)
    book = [(int(r["layer"]), int(r["head"])) for r in sorted(
        [r for r in ar if alloc_sig(r) and not tb(r, "surv_imp") and not tb(r, "surv_blk")],
        key=lambda r: -max(abs(f(r, "alloc_imp")), abs(f(r, "alloc_blk"))))][:25]

    from collections import Counter
    s25 = blk_pass[:25]; lay_need = Counter(L for L, h in s25)
    taken = set(blk_pass) | set(imp_pass) | set(book)
    rng = np.random.default_rng(SEED); rand = []
    npool = set(nonpass)
    for L, cnt in lay_need.items():
        pool = [h for h in range(32) if (L, h) in npool and (L, h) not in taken]
        rng.shuffle(pool); rand += [(L, h) for h in pool[:cnt

    ARMS = {"survivor_blk_3": blk_pass[:3], "survivor_blk_10": blk_pass[:10], "survivor_blk_25": s25,
            "survivor_imp_10": imp_pass[:10], "random_layermatched": rand,
            "bookkeeper_25": book, "defeater_allsurv": blk_pass}
    if SMOKE:
        ARMS = {"survivor_blk_3": blk_pass[:3], "survivor_imp_10": imp_pass[:5],
                "random_layermatched": rand[:3], "bookkeeper_25": book[:3], "defeater_allsurv": blk_pass}
    log(f"[P4a] arms: " + " ".join(f"{k}={len(v)}" for k, v in ARMS.items()))

    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 attn_implementation="eager", device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import inspect, re
    try:
        src = inspect.getsource(type(model.model.layers[0]).forward)
        m = re.search(r"([\w ,]+?)=\s*self\.self_attn\(", src)
        if m:
            THREE_TUPLE = (len([x for x in m.group(1).split(",") if x.strip()]) == 3)
        log(f"[P4a] decoder unpacks {'3' if THREE_TUPLE else '2'} from self_attn (tf str {transformers.__version__})")
    except Exception as e:
        log(f"[P4a] arity inspect failed ({e}); keeping THREE_TUPLE={THREE_TUPLE}")
    for L, layer in enumerate(model.model.layers):
        layer.self_attn.forward = build_fwd(layer.self_attn, L)
    log(f"[P4a] model on {dev}; attn monkeypatched ({time.time()-t0:.0f}s)")

    def blocks(it):
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text_ = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        ids = tok(text_, add_special_tokens=False)["input_ids"]
        sh = [i for i, t in enumerate(ids) if t == SH]; eot = [i for i, t in enumerate(ids) if t == EOT]
        sys_b = list(range(sh[0], eot[0] + 1)); usr_b = list(range(sh[1], eot[1] + 1))
        return ids, sys_b, usr_b
    def sgn(it): return 1.0 if it["target_sys"] == "DONE" else -1.0

    # per-item cache: ids, sys/usr LongTensors
    cache = {}
    def prep(i):
        if i not in cache:
            ids, sb, ub = blocks(stim[i])
            cache[i] = (ids, torch.tensor(sb, dtype=torch.long, device=dev), torch.tensor(ub, dtype=torch.long, device=dev))
        return cache[i]

    def yval(i, bs=None, cap=None):
        ids, _, _ = prep(i)
        STATE["bs"] = bs; STATE["cap"] = cap
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lg = model(input_ids=t, use_cache=False).logits[0, -1, :].float()
        STATE["bs"] = None; STATE["cap"] = None
        lp = torch.log_softmax(lg, -1)
        return sgn(stim[i]) * float(lp[DONE] - lp[READY])

    used = list(range(len(stim)))
    tmpl = np.array([stim[i]["template_idx"] for i in used])
    ssign = np.array([sgn(stim[i]) for i in used])
    Ybase = np.array([yval(i) for i in used])
    B = float(Ybase.mean()); log(f"[P4a] baseline B={B:+.4f} n={len(used)} ({time.time()-t0:.0f}s)")

    def heads_by_layer(hs):
        from collections import defaultdict
        d = defaultdict(set)
        for L, h in hs: d[L].add(h)
        return {L: hh for L, hh in d.items()}

    def boot_M(ptdY, ptB):
        r2 = np.random.default_rng(SEED); Ms = np.empty(BOOT)
        for b in range(BOOT):
            pk = r2.integers(0, NTMPL, NTMPL)
            denom = ptB[pk].mean()
            Ms[b] = -ptdY[pk].mean() / (2 * denom) if abs(denom) > 1e-9 else np.nan
        return np.nanpercentile(Ms, [2.5, 97.5])
    def per_template(dY, mask):
        pt = np.array([dY[(tmpl == k) & mask].mean() if ((tmpl == k) & mask).any() else 0.0 for k in range(NTMPL)])
        pb = np.array([Ybase[(tmpl == k) & mask].mean() if ((tmpl == k) & mask).any() else 0.0 for k in range(NTMPL)])
        return pt, pb
    def M_of(dY, mask):
        pt, pb = per_template(dY, mask)
        Bm = pb[pb != 0].mean() if (pb != 0).any() else B
        M = float(-pt.mean() / (2 * Bm)) if abs(Bm) > 1e-9 else float("nan")
        lo, hi = boot_M(pt, pb)
        return M, float(lo), float(hi)

    def run_arm(name, headset):
        hbl = heads_by_layer(headset)
        dY = np.empty(len(used)); tvs = []; plumb_ok = plumb_n = 0
        for n, i in enumerate(used):
            ids, sb_t, ub_t = prep(i)
            bs = {"sys": sb_t, "usr": ub_t, "layers": hbl}
            capi = {"want": {L: list(hh) for L, hh in hbl.items()}, "out": {}} if (n % PLUMB_EVERY == 0) else None
            yp = yval(i, bs=bs, cap=capi)
            dY[n] = yp - Ybase[n]
            if capi is not None:                                   # plumbing + swap_tv on this sampled item
                own = {"want": {L: list(hh) for L, hh in hbl.items()}, "out": {}}
                yval(i, cap=own)                                   # plain forward
                sset = set(sb_t.tolist()); uset = set(ub_t.tolist())
                for (L, h) in headset[:8]:
                    post = capi["out"].get((L, h)); o = own["out"].get((L, h))
                    if post is None or o is None: continue
                    ms = o[list(sset)].sum(); mu = o[list(uset)].sum()
                    pm_s = post[list(sset)].sum(); pm_u = post[list(uset)].sum()
                    plumb_n += 1
                    plumb_ok += 1 if (abs(pm_s - mu) < 2e-2 and abs(pm_u - ms) < 2e-2) else 0   # mass swapped?
                    tvs.append(float(0.5 * np.abs(post - o).sum()))
        M, lo, hi = M_of(dY, np.ones(len(used), bool))
        Mp, lop, hip = M_of(dY, ssign > 0)
        Mn, lon, hin = M_of(dY, ssign < 0)
        return {"M_att": M, "ci95": [lo, hi], "ci_excl0": bool(lo > 0 or hi < 0),
                "M_att_pos": Mp, "M_att_neg": Mn, "n_heads": len(headset),
                "plumbing_rate": (plumb_ok / plumb_n) if plumb_n else None,
                "swap_tv": float(np.mean(tvs)) if tvs else None}

    # ---- VOID: same block-swap on uncontested, compliance >= 90% floor ----
    from collections import defaultdict
    ug = defaultdict(dict)
    for idx, it in enumerate(unc):
        ug[(it["template_idx"], it["filler_idx"], it["position"])][it["slot" = idx
    upairs = [(d["system"], d["user"]) for d in ug.values() if "system" in d and "user" in d][:VOID_N]
    ucache = {}
    def uprep(idx):
        if idx not in ucache:
            ids, sb, ub = blocks(unc[idx])
            ucache[idx] = (ids, torch.tensor(sb, dtype=torch.long, device=dev), torch.tensor(ub, dtype=torch.long, device=dev))
        return ucache[idx]
    def ucomply(idx, bs=None):    # uncontested target=DONE: complies iff logP(DONE)>logP(READY)
        ids, _, _ = uprep(idx); STATE["bs"] = bs
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lp = torch.log_softmax(model(input_ids=t, use_cache=False).logits[0, -1, :].float(), -1)
        STATE["bs"] = None
        return 1 if (lp[DONE] - lp[READY]) > 0 else 0
    flat = [i for p in upairs for i in p]
    floor_uns = float(np.mean([ucomply(i) for i in flat])) if flat else 1.0
    def void_arm(headset):
        hbl = heads_by_layer(headset); ok = tot = 0
        for idx in flat:
            _, sb_t, ub_t = uprep(idx)
            ok += ucomply(idx, bs={"sys": sb_t, "usr": ub_t, "layers": hbl}); tot += 1
        return ok / tot if tot else 1.0

    results = {}
    for name, hs in ARMS.items():
        r = run_arm(name, hs)
        fr = void_arm(hs); r["floor_compliance"] = fr; r["floor_unsteered"] = floor_uns
        r["VOID"] = bool(fr < 0.90 * floor_uns)
        results[name] = r
        log(f"[P4a] {name}: M_att={r['M_att']:+.4f} CI[{r['ci95'][0]:+.4f},{r['ci95'][1]:+.4f}] "
            f"pos={r['M_att_pos']:+.3f} neg={r['M_att_neg']:+.3f} void={r['VOID']}(floor {fr:.2f}/{floor_uns:.2f}) "
            f"plumb={r['plumbing_rate']} swap_tv={r['swap_tv']} ({time.time()-t0:.0f}s)")

    # ---- VALIDITY GATES + reading (PREREG §6) ----
    sv = results.get("survivor_blk_25", results.get("survivor_blk_3", {}))
    rd = results.get("random_layermatched", {}); bk = results.get("bookkeeper_25", {})
    tx = results.get("survivor_imp_10", {})
    def plumb_ok(r): return (r.get("plumbing_rate") or 0) >= 0.90
    def swap_real(r): return (r.get("swap_tv") or 0) >= 0.05
    def near0(r): return r and abs(r.get("M_att", 9)) < 0.05
    def bothlevels(r): return r and (np.sign(r.get("M_att_pos", 0)) == np.sign(r.get("M_att_neg", 0))) \
        and abs(r.get("M_att_pos", 0)) >= 0.05 and abs(r.get("M_att_neg", 0)) >= 0.05
    if not plumb_ok(sv):
        reading = f"INVALID: block-swap not confirmed (survivor plumbing={sv.get('plumbing_rate')})"
    elif not swap_real(sv):
        reading = f"INVALID: swap ~no-op (survivor swap_tv={sv.get('swap_tv')}) -- survivors attend symmetrically by block; block-mass routing not the mechanism"
    elif bk and (not near0(bk) or bk.get("VOID")):
        reading = "INSTRUMENT-FAILURE: bookkeepers move/VOID -> generic disruption; other arms uninterpretable"
    elif rd and not near0(rd):
        reading = "INSTRUMENT-FAILURE: layer-matched random moves -> effect not specific to survivor heads"
    elif sv.get("M_att", 0) >= 0.20 and near0(rd) and near0(bk) and bothlevels(sv):
        reading = ("ROUTED: survivor block-attention causally carries a substantial share"
                   + ("; MARKER>>TEXT" if abs(sv.get("M_att", 0)) > 2 * abs(tx.get("M_att", 0)) else ""))
    elif sv.get("M_att", 0) >= 0.20 and not bothlevels(sv):
        reading = "SUSPECT: pooled M_att>=0.20 but per-level inconsistent -> residual shared-sign artifact, NOT read as ROUTED"
    elif all(near0(results[a]) for a in results):
        reading = "ALL-ARMS-NULL incl defeater -> block-attention routing at readout isn't the path; remainder elsewhere (composition or non-generation positions)"
    else:
        reading = "MIXED/PARTIAL -- read the ranked arm table"
    phaseB = bool(sv.get("M_att", 0) >= 0.20 and near0(rd) and near0(bk) and bothlevels(sv))

    out = {"prereg": "PREREG_PRV04A.md", "phase": "A", "SMOKE": SMOKE,
           "supersedes": "PREREG_PRV04.md", "chained_to_ATT01C": "c99fdaa9ccea199d5e2cd3709cfacafb3ffd00f67499c6081337df6f26800a84",
           "transformers": transformers.__version__, "B": B, "n_items": len(used),
           "arms": results, "reading": reading, "phaseB_combined_triggered": phaseB,
           "note": "Constructed block-swap (no twin). Do NOT sum M and M_att (§7). Plumbing 0 weight. "
                   "Per-level M_att is the shared-sign guard.",
           "runtime_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "prv04a_arms_smoke.csv" if SMOKE else "prv04a_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["arm", "n_heads", "M_att", "ci_lo", "ci_hi", "ci_excl0",
                                        "M_att_pos", "M_att_neg", "floor_compliance", "VOID", "plumbing_rate", "swap_tv"])
        for k, r in results.items():
            w.writerow([k, r["n_heads"], round(r["M_att"], 5), round(r["ci95"][0], 5), round(r["ci95"][1], 5),
                        r["ci_excl0"], round(r["M_att_pos"], 5), round(r["M_att_neg"], 5),
                        round(r["floor_compliance"], 4), r["VOID"], r["plumbing_rate"], r["swap_tv")
    fn = os.path.join(OUT, "prv04a_phaseA_smoke.json" if SMOKE else "prv04a_phaseA.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[P4a] reading: {reading}; phaseB_triggered={phaseB}; wrote {fn}")

if __name__ == "__main__":
    main()
