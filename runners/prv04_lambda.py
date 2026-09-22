#!/usr/bin/env python
# PRV-04 PHASE A -- is the arbitration ROUTED? Causal attention-pattern SWAP (not ablate).
# PREREG_PRV04.md (sha folded at lock), chained to KDR-01 e2b78876...ebd0.
# For item i and its counterbalanced twin i' (same template/filler/position, cb flipped -> identical token
# positions), replace the ARM heads' attention distributions in i's forward with i''s. M_att = -dY/(2B),
# dY = Y_patched - Y_baseline signed by counterbalance, paired template-cluster bootstrap -- same scale as M.
# Arms from ATT-01's ranked table. Guards: per-arm VOID (uncontested floor >=90% unsteered) + plumbing
# (injected == twin's, zero inferential weight). Phase A = attention arms only (cheap, no deflation);
# the combined arm (Phase B) needs the k=50 residual swap and is gated on marker M_att>=0.20.
# Custom eager-attention forward supports capture + per-head inject; uses HF's apply_rotary_pos_emb/repeat_kv.
import os, json, time, csv
import numpy as np, torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.models.llama.modeling_llama import apply_rotary_pos_emb, repeat_kv

# transformers <4.46 attention returns (out, weights, past_kv) 3-tuple; >=4.46 returns (out, weights) 2-tuple.
# Instance images drift, so adapt to whatever actually loaded rather than trusting the pin.
_TFV = tuple(int(x) for x in transformers.__version__.split(".")[:2])
THREE_TUPLE = _TFV < (4, 46)

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
DONE, READY = 71496, 46678
NTMPL = 30
BOOT = 200 if SMOKE else 5000
SEED = 20260914
VOID_N = 40 if SMOKE else 120          # uncontested pairs subsample for the VOID guard
def log(*a): print(*a, flush=True)

STATE = {"capture": None, "inject": None}   # capture: dict[(L,h)]->np ; inject: dict[L]->{h: tensor(q,k)}

def build_fwd(mod, lidx):
    cfg = mod.config
    H = getattr(mod, "num_heads", None) or cfg.num_attention_heads
    KV = getattr(mod, "num_key_value_heads", None) or cfg.num_key_value_heads
    hd = mod.head_dim
    groups = getattr(mod, "num_key_value_groups", None) or (H // KV)
    scaling = getattr(mod, "scaling", None) or (hd ** -0.5)   # this tf build lacks mod.scaling
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
        inj = STATE["inject"]
        if inj is not None and lidx in inj:
            for h, w in inj[lidx].items():
                aw[0, h] = w
        cap = STATE["capture"]   # capture AFTER inject so a plumbing capture verifies the injected value
        if cap is not None and lidx in cap["want"]:
            for h in cap["want"][lidx]:
                cap["out"][(lidx, h)] = aw[0, h].detach().to(torch.float16).cpu().numpy()
        out = mod.o_proj(torch.matmul(aw, value).transpose(1, 2).contiguous().view(b, q_len, -1))
        return (out, None, None) if THREE_TUPLE else (out, None)   # match caller's unpack arity
    return fwd

def main():
    global THREE_TUPLE
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_contested.jsonl"), encoding="utf-8")]
    unc = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_uncontested.jsonl"), encoding="utf-8")]
    from make_stimuli import TEMPLATES
    # ---- arms from att01_heads.csv ----
    rows = list(csv.DictReader(open(os.path.join(HERE, "att01_heads.csv"))))
    def f(r, c): return float(r[c])
    def tb(r, c): return r[c] == "True"
    def alloc_sig(r): return (f(r, "alloc_imp_lo") > 0 or f(r, "alloc_imp_hi") < 0 or
                              f(r, "alloc_blk_lo") > 0 or f(r, "alloc_blk_hi") < 0)
    LH = lambda r: (int(r["layer"]), int(r["head"]))
    marker = [LH(r) for r in sorted([r for r in rows if tb(r, "surv_blk") and not tb(r, "surv_imp")],
                                    key=lambda r: -abs(f(r, "track_blk_r")))]
    text = [LH(r) for r in sorted([r for r in rows if tb(r, "surv_imp") and not tb(r, "surv_blk")],
                                  key=lambda r: -abs(f(r, "track_imp_r")))]
    book = [LH(r) for r in sorted([r for r in rows if alloc_sig(r) and not tb(r, "surv_imp") and not tb(r, "surv_blk")],
                                  key=lambda r: -max(abs(f(r, "alloc_imp")), abs(f(r, "alloc_blk"))))][:25]
    alltrack = [LH(r) for r in rows if tb(r, "surv_imp") or tb(r, "surv_blk")]
    # layer-matched random to marker-25
    m25 = marker[:25]; from collections import Counter
    lay_need = Counter(l for l, h in m25); tracking = set(marker) | set(text)
    rng = np.random.default_rng(SEED); rand = []
    for L, cnt in lay_need.items():
        pool = [h for h in range(32) if (L, h) not in tracking and (L, h) not in book]
        rng.shuffle(pool); rand += [(L, h) for h in pool[:cnt
    ARMS = {"marker_3": marker[:3], "marker_10": marker[:10], "marker_25": m25,
            "text_3": text[:3], "text_10": text[:10], "text_25": text[:25],
            "bookkeeper_25": book, "random_layermatched": rand, "defeater_alltrack": alltrack}
    if SMOKE: ARMS = {"marker_3": marker[:3], "text_3": text[:3], "bookkeeper_25": book[:3],
                      "random_layermatched": rand[:3], "defeater_alltrack": alltrack}
    log(f"[P4] arms: " + " ".join(f"{k}={len(v)}" for k, v in ARMS.items()))

    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 attn_implementation="eager", device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    # __version__ can lie about the attention API (seen: 4.46.0 string with the pre-4.46 3-tuple decoder).
    # Read the ACTUAL decoder source to learn how many values it unpacks from self.self_attn(...).
    import inspect, re
    try:
        src = inspect.getsource(type(model.model.layers[0]).forward)
        m = re.search(r"([\w ,]+?)=\s*self\.self_attn\(", src)
        if m:
            THREE_TUPLE = (len([x for x in m.group(1).split(",") if x.strip()]) == 3)
        log(f"[P4] decoder unpacks {'3' if THREE_TUPLE else '2'} from self_attn (tf str {transformers.__version__})")
    except Exception as e:
        log(f"[P4] arity inspect failed ({e}); keeping THREE_TUPLE={THREE_TUPLE}")
    for L, layer in enumerate(model.model.layers):
        layer.self_attn.forward = build_fwd(layer.self_attn, L)
    log(f"[P4] model on {dev}; attn monkeypatched ({time.time()-t0:.0f}s)")

    def ids_of(it):
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text_ = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        return tok(text_, add_special_tokens=False)["input_ids"]
    def sgn(it): return 1.0 if it["target_sys"] == "DONE" else -1.0
    def ysig(ids, it, inject=None, capture=None):
        STATE["inject"] = inject; STATE["capture"] = capture
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lg = model(input_ids=t, use_cache=False).logits[0, -1, :].float()
        STATE["inject"] = None; STATE["capture"] = None
        lp = torch.log_softmax(lg, -1)
        return sgn(it) * float(lp[DONE] - lp[READY])

    # ---- twin pairing (contested): key = template/filler/position, cb flipped ----
    from collections import defaultdict
    grp = defaultdict(dict)
    for idx, it in enumerate(stim):
        grp[(it["template_idx"], it["filler_idx"], it["position"])][it["counterbalance" = idx
    pairs = [(d.get("DONEsys"), d.get("READYsys")) for d in grp.values() if len(d) == 2]
    pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
    if SMOKE: pairs = pairs[:40]
    ids_cache = {}
    def gid(idx):
        if idx not in ids_cache: ids_cache[idx] = ids_of(stim[idx])
        return ids_cache[idx]
    log(f"[P4] {len(pairs)} twin pairs ({time.time()-t0:.0f}s)")

    # ---- baseline (no patch) over all paired items ----
    used = sorted({i for p in pairs for i in p})
    Ybase = {i: ysig(gid(i), stim[i]) for i in used}
    tmpl = {i: stim[i]["template_idx"] for i in used}
    B = float(np.mean([Ybase[i] for i in used])); log(f"[P4] baseline B={B:+.4f} ({time.time()-t0:.0f}s)")

    def heads_by_layer(headset):
        d = defaultdict(list)
        for L, h in headset: d[L].append(h)
        return dict(d)

    def run_arm(name, headset):
        hbl = heads_by_layer(headset)
        dY = []; tt = []; plumb_ok = plumb_n = 0; tvs = []
        # each direction of each pair patched with the OTHER as twin
        oriented = [(i, j) for (a, b) in pairs for (i, j) in ((a, b), (b, a))]
        for n, (i, j) in enumerate(oriented):
            capj = {"want": hbl, "out": {}}
            ysig(gid(j), stim[j], capture=capj)                    # capture twin j's arm-head weights
            inj = {}
            for (L, h) in headset:
                w = capj["out"].get((L, h))
                if w is None: continue
                inj.setdefault(L, {})[h] = torch.tensor(w, dtype=torch.bfloat16, device=dev)
            capi = {"want": hbl, "out": {}} if (n % 50 == 0) else None
            yp = ysig(gid(i), stim[i], inject=inj, capture=capi)
            if capi is not None:
                own = {"want": hbl, "out": {}}
                ysig(gid(i), stim[i], capture=own)                 # i's OWN routing (plain forward)
                for (L, h) in headset[:8]:
                    a = capi["out"].get((L, h)); w = capj["out"].get((L, h)); o = own["out"].get((L, h))
                    if a is not None and w is not None:            # PLUMBING: post-inject == twin?
                        plumb_n += 1; plumb_ok += 1 if np.allclose(a, w, atol=2e-2) else 0
                    if w is not None and o is not None:            # SWAP MAGNITUDE: TV(twin, own)
                        tvs.append(float(0.5 * np.abs(w.astype(np.float32) - o.astype(np.float32)).sum(-1).mean()))
            dY.append(yp - Ybase[i]); tt.append(tmpl[i])
        dY = np.array(dY); tt = np.array(tt)
        ptdY = np.array([dY[tt == k].mean() if (tt == k).any() else 0.0 for k in range(NTMPL)])
        ptB = np.array([np.mean([Ybase[i] for i in used if tmpl[i] == k]) if any(tmpl[i] == k for i in used) else 0.0
                        for k in range(NTMPL)])
        M = float(-ptdY.mean() / (2 * B))
        rng2 = np.random.default_rng(SEED); Ms = np.empty(BOOT)
        for b in range(BOOT):
            pk = rng2.integers(0, NTMPL, NTMPL); Ms[b] = -ptdY[pk].mean() / (2 * ptB[pk].mean())
        lo, hi = np.percentile(Ms, [2.5, 97.5])
        return {"M_att": M, "ci95": [float(lo), float(hi)], "ci_excl0": bool(lo > 0 or hi < 0),
                "n_heads": len(headset), "plumbing_rate": (plumb_ok / plumb_n) if plumb_n else None,
                "swap_tv": float(np.mean(tvs)) if tvs else None}

    # ---- per-arm VOID (uncontested twins) ----
    ug = defaultdict(dict)
    for idx, it in enumerate(unc):
        ug[(it["template_idx"], it["filler_idx"], it["position"])][it["slot" = idx
    upairs = [(d["system"], d["user"]) for d in ug.values() if "system" in d and "user" in d][:VOID_N]
    uids = {}
    def guid(idx):
        if idx not in uids: uids[idx] = ids_of(unc[idx])
        return uids[idx]
    def comply(idx, inject=None):   # uncontested target=DONE: complies iff logP(DONE)>logP(READY)
        STATE["inject"] = inject
        t = torch.tensor([guid(idx)], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lp = torch.log_softmax(model(input_ids=t, use_cache=False).logits[0, -1, :].float(), -1)
        STATE["inject"] = None
        return 1 if (lp[DONE] - lp[READY]) > 0 else 0
    floor_uns = np.mean([comply(i) for (i, j) in upairs] + [comply(j) for (i, j) in upairs]) if upairs else 1.0
    def void_arm(headset):
        hbl = heads_by_layer(headset); ok = tot = 0
        for (i, j) in upairs:
            for (a, b) in ((i, j), (j, i)):
                capb = {"want": hbl, "out": {}}
                STATE["capture"] = capb
                tb_ = torch.tensor([guid(b)], dtype=torch.long, device=dev)
                with torch.inference_mode(): model(input_ids=tb_, use_cache=False)
                STATE["capture"] = None
                inj = {}
                for (L, h) in headset:
                    w = capb["out"].get((L, h))
                    if w is not None: inj.setdefault(L, {})[h] = torch.tensor(w, dtype=torch.bfloat16, device=dev)
                ok += comply(a, inject=inj); tot += 1
        return ok / tot if tot else 1.0

    results = {}
    for name, hs in ARMS.items():
        r = run_arm(name, hs)
        fr = void_arm(hs); r["floor_compliance"] = fr; r["floor_unsteered"] = float(floor_uns)
        r["VOID"] = bool(fr < 0.90 * floor_uns)
        results[name] = r
        log(f"[P4] {name}: M_att={r['M_att']:+.4f} CI[{r['ci95'][0]:+.4f},{r['ci95'][1]:+.4f}] "
            f"void={r['VOID']}(floor {fr:.2f}/{floor_uns:.2f}) plumb={r['plumbing_rate']} swap_tv={r['swap_tv']} ({time.time()-t0:.0f}s)")

    # ---- VALIDITY GATES (must pass before any null is interpretable) ----
    mk = results.get("marker_25", {}); bk = results.get("bookkeeper_25", {}); rd = results.get("random_layermatched", {})
    tx = results.get("text_25", results.get("text_3", {}))
    def plumb_ok(r): return (r.get("plumbing_rate") or 0) >= 0.90    # injection confirmed took
    def swap_real(r): return (r.get("swap_tv") or 0) >= 0.05         # twin routing actually differs from own
    inj_ok = plumb_ok(mk); swap_ok = swap_real(mk)
    def near0(r): return r and abs(r.get("M_att", 9)) < 0.05
    if not inj_ok:
        reading = f"INVALID: injection not confirmed (marker plumbing={mk.get('plumbing_rate')}) -- null uninterpretable, fix before reading"
    elif not swap_ok:
        reading = f"INVALID: swap is ~no-op (marker swap_tv={mk.get('swap_tv')}) -- twins too similar at these heads; null uninterpretable"
    elif bk and (not near0(bk) or bk.get("VOID")):
        reading = "INSTRUMENT-FAILURE: bookkeepers move/VOID -> generic attention disruption; other arms not cleanly interpretable"
    elif mk.get("M_att", 0) >= 0.20 and near0(bk) and near0(rd):
        reading = ("ROUTED: marker arm carries a substantial share through the tracking heads"
                   + ("; MARKER>>TEXT" if mk.get("M_att", 0) > 2 * abs(tx.get("M_att", 0)) else ""))
    elif all(near0(results[a]) for a in results):
        reading = "ALL-ARMS-NULL incl defeater -> routing at these positions isn't the path; remainder is elsewhere (composition, not location)"
    else:
        reading = "MIXED/PARTIAL -- read the ranked arm table"
    phaseB = bool(mk.get("M_att", 0) >= 0.20 and near0(bk) and near0(rd))

    out = {"prereg": "PREREG_PRV04.md", "phase": "A", "SMOKE": SMOKE,
           "chained_to_KDR01": "e2b7887640630bd8c2710348cfb13e51ccca98c7858b15e1f535387d5d95ebd0",
           "transformers": transformers.__version__, "B": B, "n_pairs": len(pairs),
           "arms": results, "reading": reading, "phaseB_combined_triggered": phaseB,
           "note": "OBSERVED via causal swap. Do NOT sum M and M_att (§7). Plumbing = zero inferential weight.",
           "runtime_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "prv04_arms.csv" if not SMOKE else "prv04_arms_smoke.csv"), "w", newline="") as fcsv:
        w = csv.writer(fcsv); w.writerow(["arm", "n_heads", "M_att", "ci_lo", "ci_hi", "ci_excl0", "floor_compliance", "VOID", "plumbing_rate", "swap_tv"])
        for k, r in results.items():
            w.writerow([k, r["n_heads"], round(r["M_att"], 5), round(r["ci95"][0], 5), round(r["ci95"][1], 5),
                        r["ci_excl0"], round(r["floor_compliance"], 4), r["VOID"], r["plumbing_rate"], r["swap_tv")
    fn = os.path.join(OUT, "prv04_phaseA_smoke.json" if SMOKE else "prv04_phaseA.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[P4] reading: {reading}; phaseB_triggered={phaseB}; wrote {fn}")

if __name__ == "__main__":
    main()
