#!/usr/bin/env python
# ATT-01c -- within-level control for the shared-sign artifact (PREREG_ATT01C.md, chained PRV-04 a71824cf...).
# Re-runs ATT-01's forward pass VERBATIM but (1) persists per-item RAW arrays and (2) splits corr(A,Y) by
# counterbalance level. Within a fixed level s is constant, so corr(A_signed,Y_signed)=corr(A_raw,Y_raw): the
# within-level correlation is content-following with the shared sign stripped out. A real tracker keeps a
# same-sign correlation in BOTH levels; a positional-bias head keeps a large POOLED r but collapses within each
# level. Reproduction check: pooled corr(s*A_raw, s*R) must match att01_heads.csv track_*_r (else HALT).
import os, json, time, csv
import numpy as np, torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
DONE, READY = 71496, 46678
NTMPL = 30
SH, EOT = 128006, 128009               # <|start_header_id|>, <|eot_id|>
BOOT = 200 if SMOKE else 5000
SEED = 20260914
FLOORS = [0.05, 0.10, 0.15]
LOCK_FLOOR = 0.10                       # PREREG §4

def log(*a): print(*a, flush=True)

def vec_corr(X, y):
    """Per-column Pearson r between columns of X (m,H) and vector y (m,). Returns (H,)."""
    Xc = X - X.mean(0); yc = y - y.mean()
    num = Xc.T @ yc
    den = np.sqrt((Xc ** 2).sum(0)) * np.sqrt((yc ** 2).sum()) + 1e-12
    return num / den

def main():
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_contested.jsonl"), encoding="utf-8")]
    if SMOKE:  # BALANCED across both counterbalance levels (stim[:60] was all s=+1 -> empty -1 level)
        pos = [it for it in stim if it["target_sys"] == "DONE"][:30]
        neg = [it for it in stim if it["target_sys"] != "DONE"][:30]
        stim = pos + neg
    from make_stimuli import TEMPLATES
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 attn_implementation="eager", device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import transformers
    nL = model.config.num_hidden_layers; nH = model.config.num_attention_heads; HD = nL * nH
    log(f"[C] model on {dev}; tf {transformers.__version__} eager; L={nL} H={nH} heads={HD} "
        f"n={len(stim)} ({time.time()-t0:.0f}s)")

    def blocks_and_imp(it):
        imp_s = TEMPLATES[it["template_idx".format(T=it["target_sys"])
        imp_u = TEMPLATES[it["template_idx".format(T=it["target_usr"])
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]
        sh = [i for i, t in enumerate(ids) if t == SH]; eot = [i for i, t in enumerate(ids) if t == EOT]
        sys_block = list(range(sh[0], eot[0] + 1)); usr_block = list(range(sh[1], eot[1] + 1))
        def span(imp):
            cs = text.index(imp); ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        return ids, sys_block, usr_block, span(imp_s), span(imp_u)

    N = len(stim)
    imp_raw = np.zeros((N, HD), np.float64); blk_raw = np.zeros((N, HD), np.float64)   # UNSIGNED
    R = np.zeros(N); sgn = np.zeros(N); tmpl = np.array([it["template_idx"] for it in stim])
    with torch.inference_mode():
        for i, it in enumerate(stim):
            ids, sb, ub, si, ui = blocks_and_imp(it)
            t = torch.tensor([ids], dtype=torch.long, device=dev)
            out = model(input_ids=t, use_cache=False, output_attentions=True)
            lp = torch.log_softmax(out.logits[0, -1, :].float(), -1)
            R[i] = float(lp[DONE] - lp[READY])
            sgn[i] = 1.0 if it["target_sys"] == "DONE" else -1.0
            al = torch.stack([out.attentions[L][0, :, -1, :] for L in range(nL)], 0).float().cpu().numpy()
            imp_raw[i] = (al[:, :, si].sum(-1) - al[:, :, ui].sum(-1)).reshape(-1)   # RAW, no sign
            blk_raw[i] = (al[:, :, sb].sum(-1) - al[:, :, ub].sum(-1)).reshape(-1)
            del out, al
            if (i + 1) % 120 == 0: log(f"[C] {i+1}/{N} ({time.time()-t0:.0f}s)")

    # ---- persist per-item raw arrays (THE FIX: never re-run the GPU for re-analysis again) ----
    npz = os.path.join(OUT, "att01c_peritem_smoke.npz" if SMOKE else "att01c_peritem.npz")
    np.savez_compressed(npz, imp_raw=imp_raw, blk_raw=blk_raw, R=R, sgn=sgn, tmpl=tmpl,
                        nL=nL, nH=nH, seed=SEED)
    log(f"[C] persisted per-item arrays -> {npz} ({time.time()-t0:.0f}s)")

    # ---- reproduction check: pooled corr(s*A_raw, s*R) must match ATT-01 ----
    Ysig = sgn * R
    pooled_imp = vec_corr(sgn[:, None] * imp_raw, Ysig)
    pooled_blk = vec_corr(sgn[:, None] * blk_raw, Ysig)
    LH = [(L, h) for L in range(nL) for h in range(nH)]
    idx_of = {(L, h): j for j, (L, h) in enumerate(LH)}

    # load ATT-01 aggregates for reproduction + arm membership
    att01 = {}
    apath = os.path.join(HERE, "att01_heads.csv")
    have_att01 = os.path.exists(apath)
    if have_att01:
        with open(apath) as f:
            for row in csv.DictReader(f):
                att01[(int(row["layer"]), int(row["head"]))] = {
                    "track_imp_r": float(row["track_imp_r"]), "track_blk_r": float(row["track_blk_r"]),
                    "surv_imp": row["surv_imp"] == "True", "surv_blk": row["surv_blk"] == "True"}
        d_imp = np.array([abs(pooled_imp[idx_of[k - att01[k]["track_imp_r"]) for k in att01])
        d_blk = np.array([abs(pooled_blk[idx_of[k - att01[k]["track_blk_r"]) for k in att01])
        repro = {"max_abs_delta_imp": float(d_imp.max()), "max_abs_delta_blk": float(d_blk.max()),
                 "median_abs_delta_imp": float(np.median(d_imp)), "median_abs_delta_blk": float(np.median(d_blk))}
        log(f"[C] reproduction vs ATT-01: max|d| imp={repro['max_abs_delta_imp']:.4f} "
            f"blk={repro['max_abs_delta_blk']:.4f} median|d| blk={repro['median_abs_delta_blk']:.4f} "
            f"(bf16/GPU jitter expected small; SMOKE={SMOKE} uses a different subsample so deltas are large)")
        if not SMOKE and repro["median_abs_delta_blk"] > 0.05:   # PREREG §3 HALT: not the same computation
            log(f"[C] HALT reproduction FAILED median|d_blk|={repro['median_abs_delta_blk']:.4f} > 0.05 "
                f"-- not measuring the same thing as ATT-01; NOT reading the within-level control")
            json.dump({"prereg": "PREREG_ATT01C.md", "SMOKE": SMOKE, "verdict": "REPRODUCTION_FAILED",
                       "reproduction": repro}, open(os.path.join(OUT, "att01c.json"), "w"), indent=2)
            import sys as _s; _s.exit(3)
    else:
        repro = {"note": "att01_heads.csv absent -- reproduction check skipped (SMOKE ok)"}
        log("[C] WARN att01_heads.csv absent; reproduction check skipped")

    # ---- within-level correlation + template-cluster bootstrap CI, per level ----
    rng = np.random.default_rng(SEED)
    levels = {"+1": sgn > 0, "-1": sgn < 0}
    wl = {}   # wl[lvl] = dict of arrays over heads
    for lvl, mask in levels.items():
        if int(mask.sum()) < 2:   # empty/degenerate level -> guard (must not happen in FULL; loud if it does)
            log(f"[C] WARN level {lvl} n={int(mask.sum())} -- skipping bootstrap (SHOULD NOT HAPPEN IN FULL)")
            nan = np.full(HD, np.nan)
            wl[lvl] = {k: nan.copy() for k in ("r_imp", "r_blk", "imp_lo", "imp_hi", "blk_lo", "blk_hi",
                                               "sd_imp", "sd_blk", "mu_imp", "mu_blk")}
            wl[lvl]["n"] = int(mask.sum()); continue
        Xi = imp_raw[mask]; Xb = blk_raw[mask]; y = R[mask]; tm = tmpl[mask]
        r_imp = vec_corr(Xi, y); r_blk = vec_corr(Xb, y)
        sd_imp = Xi.std(0); sd_blk = Xb.std(0); mu_imp = Xi.mean(0); mu_blk = Xb.mean(0)
        by_t = [np.where(tm == tt)[0] for tt in range(NTMPL)]
        by_t = [g for g in by_t if len(g) > 0]; ncl = len(by_t)
        bI = np.empty((BOOT, HD)); bB = np.empty((BOOT, HD))
        for b in range(BOOT):
            pk = rng.integers(0, ncl, ncl)
            ii = np.concatenate([by_t[c] for c in pk])
            bI[b] = vec_corr(Xi[ii], y[ii]); bB[b] = vec_corr(Xb[ii], y[ii])
        wl[lvl] = {"r_imp": r_imp, "r_blk": r_blk,
                   "imp_lo": np.percentile(bI, 2.5, 0), "imp_hi": np.percentile(bI, 97.5, 0),
                   "blk_lo": np.percentile(bB, 2.5, 0), "blk_hi": np.percentile(bB, 97.5, 0),
                   "sd_imp": sd_imp, "sd_blk": sd_blk, "mu_imp": mu_imp, "mu_blk": mu_blk, "n": int(mask.sum())}
        log(f"[C] level {lvl}: n={int(mask.sum())} clusters={ncl} ({time.time()-t0:.0f}s)")

    # ---- per-head PASS (both levels, same sign, CI excl 0, |r|>=floor) ----
    def passes(lens, floor):
        p = wl["+1"]; m = wl["-1"]
        rp = p[f"r_{lens}"]; rm = m[f"r_{lens}"]
        lo_p, hi_p = p[f"{lens}_lo"], p[f"{lens}_hi"]; lo_m, hi_m = m[f"{lens}_lo"], m[f"{lens}_hi"]
        ci_p = (lo_p > 0) | (hi_p < 0); ci_m = (lo_m > 0) | (hi_m < 0)
        same = np.sign(rp) == np.sign(rm)
        mag = (np.abs(rp) >= floor) & (np.abs(rm) >= floor)
        return ci_p & ci_m & same & mag

    pass_blk = {f: passes("blk", f) for f in FLOORS}
    pass_imp = {f: passes("imp", f) for f in FLOORS}

    # ---- survivorship P over ATT-01 arm sets (PREREG §5) ----
    def frac(memberset, passmask):
        js = [idx_of[k] for k in memberset]
        if not js: return None
        return float(np.mean([passmask[j] for j in js])), len(js)

    arms = {}
    if have_att01:
        surv_blk_set = [k for k, v in att01.items() if v["surv_blk"
        surv_imp_set = [k for k, v in att01.items() if v["surv_imp"
        marker_set = [k for k, v in att01.items() if v["surv_blk"] and not v["surv_imp"   # marker-readers
        text_set = [k for k, v in att01.items() if v["surv_imp"] and not v["surv_blk"     # text-readers
        top10 = sorted(att01, key=lambda k: -max(abs(att01[k]["track_imp_r"]), abs(att01[k]["track_blk_r"])))[:10]
        setmap = {"blk_survivors": surv_blk_set, "imp_survivors": surv_imp_set,
                  "marker_readers": marker_set, "text_readers": text_set, "top10": top10}
        for nm, s in setmap.items():
            arms[nm] = {"n": len(s)}
            for f in FLOORS:
                pm = pass_blk[f] if nm in ("blk_survivors", "marker_readers") else \
                     (pass_imp[f] if nm in ("imp_survivors", "text_readers") else
                      (pass_blk[f] | pass_imp[f]))   # top10: pass under either lens
                fr = frac(s, pm)
                arms[nm][f"P@{f}"] = None if fr is None else round(fr[0], 4)

    # ---- primary metric + verdict (PREREG §5): P = blk-survivors pass at LOCK_FLOOR ----
    P = arms.get("blk_survivors", {}).get(f"P@{LOCK_FLOOR}") if have_att01 else None
    # top10 collapse check
    top10_collapse = None
    if have_att01:
        top10 = sorted(att01, key=lambda k: -max(abs(att01[k]["track_imp_r"]), abs(att01[k]["track_blk_r"])))[:10]
        pm = pass_blk[LOCK_FLOOR] | pass_imp[LOCK_FLOOR]
        top10_collapse = float(np.mean([not pm[idx_of[k for k in top10]))  # frac of top10 that FAIL
    if P is None:
        verdict = "SMOKE_OR_NO_ATT01"
    elif P >= 0.50:
        verdict = "TRACKING-REAL"
    elif P < 0.10 or (top10_collapse is not None and top10_collapse > 0.5):
        verdict = "TRACKING-ARTIFACT"
    else:
        verdict = "PARTIAL"

    # ---- per-head within-level CSV ----
    csvfn = os.path.join(OUT, "att01c_withinlevel_smoke.csv" if SMOKE else "att01c_withinlevel.csv")
    cols = ["layer", "head", "pooled_blk_r", "pooled_imp_r",
            "blk_r_p", "blk_lo_p", "blk_hi_p", "blk_r_m", "blk_lo_m", "blk_hi_m",
            "imp_r_p", "imp_r_m", "sd_blk_p", "sd_blk_m", "mu_blk_p", "mu_blk_m",
            "pass_blk_010", "pass_imp_010", "surv_blk_att01", "surv_imp_att01"]
    order = np.argsort(-np.maximum(np.abs(pooled_imp), np.abs(pooled_blk)))
    with open(csvfn, "w", newline="") as f:
        w = csv.writer(f); w.writerow(cols)
        for j in order:
            L, h = LH[j]; k = (L, h)
            a = att01.get(k, {})
            w.writerow([L, h, "%.6f" % pooled_blk[j], "%.6f" % pooled_imp[j],
                        "%.6f" % wl["+1"]["r_blk"][j], "%.6f" % wl["+1"]["blk_lo"][j], "%.6f" % wl["+1"]["blk_hi"][j],
                        "%.6f" % wl["-1"]["r_blk"][j], "%.6f" % wl["-1"]["blk_lo"][j], "%.6f" % wl["-1"]["blk_hi"][j],
                        "%.6f" % wl["+1"]["r_imp"][j], "%.6f" % wl["-1"]["r_imp"][j],
                        "%.6f" % wl["+1"]["sd_blk"][j], "%.6f" % wl["-1"]["sd_blk"][j],
                        "%.6f" % wl["+1"]["mu_blk"][j], "%.6f" % wl["-1"]["mu_blk"][j],
                        bool(pass_blk[LOCK_FLOOR][j]), bool(pass_imp[LOCK_FLOOR][j]),
                        a.get("surv_blk", ""), a.get("surv_imp", "")])

    out = {"prereg": "PREREG_ATT01C.md",
           "chained_to_PRV04": "a71824cfe2924a22098c194433c0ffea5f78ae83b83c93a6712c97d33ab6a458",
           "SMOKE": SMOKE, "n": N, "n_level_+1": wl["+1"]["n"], "n_level_-1": wl["-1"]["n"],
           "transformers": transformers.__version__, "boot": BOOT, "lock_floor": LOCK_FLOOR,
           "reproduction": repro, "arms": arms, "P_primary": P, "top10_fail_frac": top10_collapse,
           "verdict": verdict,
           "note": "Within-level corr(A_raw,R) with sign stripped. PASS = both levels same-sign CI-excl-0 & "
                   "|r|>=0.10. TRACKING-REAL P>=0.50 / ARTIFACT P<0.10 or top10 collapse / else PARTIAL.",
           "runtime_s": round(time.time() - t0, 1)}
    jf = os.path.join(OUT, "att01c_smoke.json" if SMOKE else "att01c.json")
    json.dump(out, open(jf, "w"), indent=2)
    log(f"[C] verdict={verdict} P={P} top10_fail={top10_collapse}; wrote {csvfn} + {jf} + {npz}")

if __name__ == "__main__":
    main()
