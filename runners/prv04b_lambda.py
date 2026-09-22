#!/usr/bin/env python
# PRV-04b -- swap-magnitude-MATCHED block-swap. PREREG_PRV04B.md (sha folded at lock), chained PRV-04a 07d70822...
# Removes PRV-04a's magnitude confound: deliver the SAME swap_tv tau to every head via the interpolant
# alpha' = alpha + t*(alpha_full - alpha), t = min(1, tau/d), d = TV(alpha_full, alpha). TV(alpha',alpha)=t*d=min(tau,d).
# Then compare M_att at matched magnitude -> M_att IS "per unit attention moved". Delivered TV recorded IN the
# forward (kills PRV-04a's multi-layer plumbing baseline-mismatch). Primary test: paired bootstrap of
# M_att(survivor_blk_25) - M_att(bookkeeper_25) and survivor_blk_25 - random. tau=0.10 (PREREG §2b).
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
TAU = 0.05                              # PREREG §2b RE-LOCKED 2026-09-19 (v1 0.10 infeasible: survivor cap ~0.06)
def log(*a): print(*a, flush=True)

STATE = {"bs": None}   # bs: {"sys":LongTensor,"usr":LongTensor,"layers":{L:set(h)},"tau":float,"rec":{(L,h):tv}}

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
            sys_i = bs["sys"]; usr_i = bs["usr"]; tau = bs["tau"]
            for h in bs["layers"][lidx]:
                row = aw[0, h, -1, :]
                own = row.clone()
                ms = float(own[sys_i].sum()); mu = float(own[usr_i].sum())
                full = own.clone()
                full[sys_i] = own[sys_i] * (mu / ms) if ms > 1e-4 else torch.full_like(own[sys_i], mu / max(1, sys_i.numel()))
                full[usr_i] = own[usr_i] * (ms / mu) if mu > 1e-4 else torch.full_like(own[usr_i], ms / max(1, usr_i.numel()))
                d = 0.5 * float((full - own).abs().sum())
                t = min(1.0, tau / d) if d > 1e-6 else 0.0
                new = own + t * (full - own)
                aw[0, h, -1, :] = new
                bs["rec"][(lidx, h)] = t * d                    # delivered TV, recorded in-forward
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

    wl = list(csv.DictReader(open(os.path.join(HERE, "att01c_withinlevel.csv"))))
    def LHc(r): return (int(r["layer"]), int(r["head"]))
    def rblk(r): return min(abs(float(r["blk_r_p"])), abs(float(r["blk_r_m"])))
    def rimp(r): return min(abs(float(r["imp_r_p"])), abs(float(r["imp_r_m"])))
    blk_pass = [LHc(r) for r in sorted([r for r in wl if r["pass_blk_010"] == "True"], key=lambda r: -rblk(r))]
    imp_pass = [LHc(r) for r in sorted([r for r in wl if r["pass_imp_010"] == "True"], key=lambda r: -rimp(r))]
    nonpass = [LHc(r) for r in wl if r["pass_blk_010"] != "True" and r["pass_imp_010"] != "True"]
    ar = list(csv.DictReader(open(os.path.join(HERE, "att01_heads.csv"))))
    def f(r, c): return float(r[c])
    def tbb(r, c): return r[c] == "True"
    def asig(r): return (f(r, "alloc_imp_lo") > 0 or f(r, "alloc_imp_hi") < 0 or
                         f(r, "alloc_blk_lo") > 0 or f(r, "alloc_blk_hi") < 0)
    book = [(int(r["layer"]), int(r["head"])) for r in sorted(
        [r for r in ar if asig(r) and not tbb(r, "surv_imp") and not tbb(r, "surv_blk")],
        key=lambda r: -max(abs(f(r, "alloc_imp")), abs(f(r, "alloc_blk"))))][:25]
    from collections import Counter, defaultdict
    s25 = blk_pass[:25]; need = Counter(L for L, h in s25)
    taken = set(blk_pass) | set(imp_pass) | set(book); npool = set(nonpass)
    rng = np.random.default_rng(SEED); rand = []
    for L, cnt in need.items():
        pool = [h for h in range(32) if (L, h) in npool and (L, h) not in taken]
        rng.shuffle(pool); rand += [(L, h) for h in pool[:cnt
    ARMS = {"survivor_blk_10": blk_pass[:10], "survivor_blk_25": s25, "bookkeeper_25": book,
            "random_layermatched": rand, "survivor_imp_10": imp_pass[:10], "defeater_allsurv": blk_pass}
    if SMOKE:
        ARMS = {"survivor_blk_10": blk_pass[:10], "bookkeeper_25": book[:5],
                "random_layermatched": rand[:5], "survivor_imp_10": imp_pass[:5], "defeater_allsurv": blk_pass}
    log(f"[P4b] survivors blk={len(blk_pass)} imp={len(imp_pass)} nonpass={len(nonpass)}; tau={TAU}")
    log(f"[P4b] arms: " + " ".join(f"{k}={len(v)}" for k, v in ARMS.items()))

    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 attn_implementation="eager", device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import inspect, re
    try:
        src = inspect.getsource(type(model.model.layers[0]).forward)
        m = re.search(r"([\w ,]+?)=\s*self\.self_attn\(", src)
        if m: THREE_TUPLE = (len([x for x in m.group(1).split(",") if x.strip()]) == 3)
        log(f"[P4b] decoder unpacks {'3' if THREE_TUPLE else '2'} (tf {transformers.__version__})")
    except Exception as e:
        log(f"[P4b] arity inspect failed ({e}); THREE_TUPLE={THREE_TUPLE}")
    for L, layer in enumerate(model.model.layers):
        layer.self_attn.forward = build_fwd(layer.self_attn, L)
    log(f"[P4b] model on {dev}; patched ({time.time()-t0:.0f}s)")

    def blocks(it):
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text_ = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        ids = tok(text_, add_special_tokens=False)["input_ids"]
        sh = [i for i, t in enumerate(ids) if t == SH]; eot = [i for i, t in enumerate(ids) if t == EOT]
        return ids, list(range(sh[0], eot[0] + 1)), list(range(sh[1], eot[1] + 1))
    def sgn(it): return 1.0 if it["target_sys"] == "DONE" else -1.0
    cache = {}
    def prep(i):
        if i not in cache:
            ids, sb, ub = blocks(stim[i])
            cache[i] = (ids, torch.tensor(sb, dtype=torch.long, device=dev), torch.tensor(ub, dtype=torch.long, device=dev))
        return cache[i]
    def yval(i, bs=None):
        ids, _, _ = prep(i); STATE["bs"] = bs
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lg = model(input_ids=t, use_cache=False).logits[0, -1, :].float()
        STATE["bs"] = None
        lp = torch.log_softmax(lg, -1)
        return sgn(stim[i]) * float(lp[DONE] - lp[READY])

    used = list(range(len(stim)))
    tmpl = np.array([stim[i]["template_idx"] for i in used])
    ssign = np.array([sgn(stim[i]) for i in used])
    Ybase = np.array([yval(i) for i in used])
    B = float(Ybase.mean()); log(f"[P4b] baseline B={B:+.4f} n={len(used)} ({time.time()-t0:.0f}s)")

    def hbl_of(hs):
        d = defaultdict(set)
        for L, h in hs: d[L].add(h)
        return {L: hh for L, hh in d.items()}
    ptB = np.array([Ybase[tmpl == k].mean() if (tmpl == k).any() else 0.0 for k in range(NTMPL)])
    def ptdY_of(dY):
        return np.array([dY[tmpl == k].mean() if (tmpl == k).any() else 0.0 for k in range(NTMPL)])
    def M_ci(ptdY, ptb):
        Bm = ptb[ptb != 0].mean() if (ptb != 0).any() else B
        M = float(-ptdY.mean() / (2 * Bm)) if abs(Bm) > 1e-9 else float("nan")
        r2 = np.random.default_rng(SEED); Ms = np.empty(BOOT)
        for b in range(BOOT):
            pk = r2.integers(0, NTMPL, NTMPL); den = ptb[pk].mean()
            Ms[b] = -ptdY[pk].mean() / (2 * den) if abs(den) > 1e-9 else np.nan
        lo, hi = np.nanpercentile(Ms, [2.5, 97.5]); return M, float(lo), float(hi)

    def run_arm(name, headset):
        hbl = hbl_of(headset); dY = np.empty(len(used)); tv_acc = defaultdict(list)
        for n, i in enumerate(used):
            ids, sb_t, ub_t = prep(i)
            rec = {}
            bs = {"sys": sb_t, "usr": ub_t, "layers": hbl, "tau": TAU, "rec": rec}
            yp = yval(i, bs=bs); dY[n] = yp - Ybase[n]
            for (L, h), tv in rec.items(): tv_acc[(L, h)].append(tv)
        ptdY = ptdY_of(dY)
        M, lo, hi = M_ci(ptdY, ptB)
        def lvl(msk):   # per-template mean over items of one counterbalance level
            pd = np.array([dY[(tmpl == k) & msk].mean() if ((tmpl == k) & msk).any() else 0.0 for k in range(NTMPL)])
            pb = np.array([Ybase[(tmpl == k) & msk].mean() if ((tmpl == k) & msk).any() else 0.0 for k in range(NTMPL)])
            return M_ci(pd, pb)
        Mp, lop, hip = lvl(ssign > 0)
        Mn, lon, hin = lvl(ssign < 0)
        deliv = float(np.mean([np.mean(v) for v in tv_acc.values()])) if tv_acc else 0.0
        return {"M_att": M, "ci95": [lo, hi], "ci_excl0": bool(lo > 0 or hi < 0),
                "M_att_pos": Mp, "M_att_neg": Mn, "n_heads": len(headset),
                "delivered_swap_tv": deliv, "match_ok": bool(0.04 <= deliv <= 0.06), "ptdY": ptdY.tolist()}

    # ---- VOID (matched swap on uncontested) ----
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
    def ucomply(idx, bs=None):
        ids, _, _ = uprep(idx); STATE["bs"] = bs
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lp = torch.log_softmax(model(input_ids=t, use_cache=False).logits[0, -1, :].float(), -1)
        STATE["bs"] = None
        return 1 if (lp[DONE] - lp[READY]) > 0 else 0
    flat = [i for p in upairs for i in p]
    floor_uns = float(np.mean([ucomply(i) for i in flat])) if flat else 1.0
    def void_arm(headset):
        hbl = hbl_of(headset); ok = tot = 0
        for idx in flat:
            _, sb_t, ub_t = uprep(idx)
            ok += ucomply(idx, bs={"sys": sb_t, "usr": ub_t, "layers": hbl, "tau": TAU, "rec": {}}); tot += 1
        return ok / tot if tot else 1.0

    results = {}
    for name, hs in ARMS.items():
        r = run_arm(name, hs)
        fr = void_arm(hs); r["floor_compliance"] = fr; r["floor_unsteered"] = floor_uns
        r["VOID"] = bool(fr < 0.90 * floor_uns)
        results[name] = r
        log(f"[P4b] {name}: M_att={r['M_att']:+.4f} CI[{r['ci95'][0]:+.4f},{r['ci95'][1]:+.4f}] "
            f"pos={r['M_att_pos']:+.3f} neg={r['M_att_neg']:+.3f} deliv_tv={r['delivered_swap_tv']:.3f} "
            f"match={r['match_ok']} void={r['VOID']}(floor {fr:.2f}/{floor_uns:.2f}) ({time.time()-t0:.0f}s)")

    # ---- paired Delta comparisons at matched magnitude ----
    def delta_ci(a, b):
        if a not in results or b not in results: return None
        pa = np.array(results[a]["ptdY"]); pb = np.array(results[b]["ptdY"])
        r2 = np.random.default_rng(SEED); Ds = np.empty(BOOT)
        for i in range(BOOT):
            pk = r2.integers(0, NTMPL, NTMPL); den = ptB[pk].mean()
            if abs(den) < 1e-9: Ds[i] = np.nan; continue
            Ds[i] = (-pa[pk].mean() / (2 * den)) - (-pb[pk].mean() / (2 * den))
        lo, hi = np.nanpercentile(Ds, [2.5, 97.5])
        return {"delta": float(-pa.mean() / (2 * ptB.mean()) + pb.mean() / (2 * ptB.mean())),
                "ci95": [float(lo), float(hi)], "excl0": bool(lo > 0 or hi < 0)}
    d_sv_bk = delta_ci("survivor_blk_25", "bookkeeper_25")
    d_sv_rd = delta_ci("survivor_blk_25", "random_layermatched")
    log(f"[P4b] Delta survivor_blk_25 - bookkeeper_25 = {d_sv_bk}; - random = {d_sv_rd}")

    # ---- reading (PREREG §5) ----
    sv = results.get("survivor_blk_25", {}); bk = results.get("bookkeeper_25", {}); rd = results.get("random_layermatched", {})
    def val(r): return r.get("M_att", 0.0)
    if not sv.get("match_ok") or not bk.get("match_ok"):
        reading = f"INVALID: magnitude match failed (sv deliv={sv.get('delivered_swap_tv')}, bk deliv={bk.get('delivered_swap_tv')})"
    elif bk.get("VOID") or sv.get("VOID"):
        reading = "INVALID: VOID (model broken by matched swap)"
    elif val(sv) >= 0.20 and d_sv_bk and d_sv_bk["excl0"] and d_sv_bk["delta"] > 0 and (d_sv_rd and d_sv_rd["delta"] > 0):
        reading = "TRACKING-ROUTES: at matched magnitude survivor_blk routes MORE than bookkeeper & random -> tracking-specific"
    elif abs(val(sv) - val(bk)) < 0.05 and val(sv) >= 0.10 and val(bk) >= 0.10 and val(sv) > val(rd) and val(bk) > val(rd):
        reading = "BLOCK-ROUTES-NOT-TRACKING-SPECIFIC: block allocation routes, tracking adds nothing causal"
    elif val(bk) >= 0.10 and val(sv) < 0.05:
        reading = "TRACKING-INERT: at equal magnitude tracking heads do nothing while allocators route -> tracking anti-predictive of causal role"
    elif all(abs(val(results[a])) < 0.05 for a in ("survivor_blk_25", "bookkeeper_25", "random_layermatched") if a in results):
        reading = "NOTHING-ROUTES: at matched tau all arms ~0 -> PRV-04a bookkeeper effect was pure excess magnitude; block-attention routing at readout isn't the path"
    else:
        reading = "MIXED -- read the arm table + deltas"
    log(f"[P4b] reading: {reading}")

    out = {"prereg": "PREREG_PRV04B.md", "SMOKE": SMOKE, "tau": TAU,
           "chained_to_PRV04A": "07d708224e827d2a119355cbb27d281ec3959e64e65143aea293549b6c3a3962",
           "transformers": transformers.__version__, "B": B, "n_items": len(used),
           "arms": {k: {kk: vv for kk, vv in r.items() if kk != "ptdY"} for k, r in results.items()},
           "delta_survivor_minus_bookkeeper": d_sv_bk, "delta_survivor_minus_random": d_sv_rd,
           "reading": reading, "note": "Matched-magnitude block-swap; M_att IS per-unit-attention efficiency. "
                                        "Do NOT sum M and M_att (§7).", "runtime_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "prv04b_arms_smoke.csv" if SMOKE else "prv04b_arms.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["arm", "n_heads", "M_att", "ci_lo", "ci_hi", "ci_excl0",
                                        "M_att_pos", "M_att_neg", "delivered_swap_tv", "match_ok", "floor_compliance", "VOID"])
        for k, r in results.items():
            w.writerow([k, r["n_heads"], round(r["M_att"], 5), round(r["ci95"][0], 5), round(r["ci95"][1], 5),
                        r["ci_excl0"], round(r["M_att_pos"], 5), round(r["M_att_neg"], 5),
                        round(r["delivered_swap_tv"], 4), r["match_ok"], round(r["floor_compliance"], 4), r["VOID")
    fn = os.path.join(OUT, "prv04b_smoke.json" if SMOKE else "prv04b.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[P4b] wrote {fn}")

if __name__ == "__main__":
    main()
