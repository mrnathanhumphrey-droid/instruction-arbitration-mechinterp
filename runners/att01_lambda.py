#!/usr/bin/env python
# ATT-01 -- locate role-sensitive attention (OBSERVATIONAL; no causal claim leaves this probe).
# PREREG_ATT01.md (sha folded at lock), sidecar chained to PREREG_H4 da688c1e...f9f75.
# For each layer L, head h, at the generation position: does the head's split of attention between the two
# role blocks track which instruction the model obeys?
#   A_imp = mass(system-imperative span) - mass(user-imperative span)
#   A_blk = mass(system-block, headers+markers included) - mass(user-block)
# Sign both by the counterbalance EXACTLY as Y_signed (s=+1 if target_sys==DONE else -1) so lexical/slot
# priors cancel as they do in the readout. Two quantities per head:
#   (1) ALLOCATION: mean A_signed != 0  (does it split by role at all)
#   (2) TRACKING:   corr(A_signed, Y_signed) across items  (does its split predict the winner) <- money
# Stats: cluster-bootstrap by template (30), percentile CI; null = shuffle Y_signed WITHIN template (1000),
# ranked list read against that null (not zero); Bonferroni over the 1024-head family. Both A_imp & A_blk
# reported -- disagreement localizes text-vs-marker and IS a result. Ranked table + null, no binary verdict,
# NO causal verb. EAGER attention (SDPA/flash return no weights).
import os, json, time
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
NULLN = 100 if SMOKE else 1000
SEED = 20260914

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
    if SMOKE: stim = stim[:60]
    from make_stimuli import TEMPLATES
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 attn_implementation="eager", device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import transformers
    nL = model.config.num_hidden_layers; nH = model.config.num_attention_heads; HD = nL * nH
    log(f"[A] model on {dev}; tf {transformers.__version__} eager; L={nL} H={nH} heads={HD} "
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
    Aimp = np.zeros((N, HD), np.float64); Ablk = np.zeros((N, HD), np.float64)
    Ysig = np.zeros(N); sign = np.zeros(N); tmpl = np.array([it["template_idx"] for it in stim])
    with torch.inference_mode():
        for i, it in enumerate(stim):
            ids, sb, ub, si, ui = blocks_and_imp(it)
            t = torch.tensor([ids], dtype=torch.long, device=dev)
            out = model(input_ids=t, use_cache=False, output_attentions=True)
            lp = torch.log_softmax(out.logits[0, -1, :].float(), -1)
            R = float(lp[DONE] - lp[READY])
            s = 1.0 if it["target_sys"] == "DONE" else -1.0
            Ysig[i] = s * R; sign[i] = s
            # last-row attention over keys, all layers x heads -> (nL,nH,seq)
            al = torch.stack([out.attentions[L][0, :, -1, :] for L in range(nL)], 0).float().cpu().numpy()
            imp = al[:, :, si].sum(-1) - al[:, :, ui].sum(-1)      # (nL,nH)
            blk = al[:, :, sb].sum(-1) - al[:, :, ub].sum(-1)
            Aimp[i] = (s * imp).reshape(-1); Ablk[i] = (s * blk).reshape(-1)
            del out, al
            if (i + 1) % 120 == 0: log(f"[A] {i+1}/{N} ({time.time()-t0:.0f}s)")

    # ---- point estimates ----
    alloc_imp = Aimp.mean(0); alloc_blk = Ablk.mean(0)
    track_imp = vec_corr(Aimp, Ysig); track_blk = vec_corr(Ablk, Ysig)

    # ---- cluster bootstrap by template ----
    by_t = [np.where(tmpl == t)[0] for t in range(NTMPL)]
    rng = np.random.default_rng(SEED)
    aI = np.empty((BOOT, HD)); aB = np.empty((BOOT, HD)); tI = np.empty((BOOT, HD)); tB = np.empty((BOOT, HD))
    for b in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL)
        idx = np.concatenate([by_t[t] for t in pk])
        XI = Aimp[idx]; XB = Ablk[idx]; y = Ysig[idx]
        aI[b] = XI.mean(0); aB[b] = XB.mean(0); tI[b] = vec_corr(XI, y); tB[b] = vec_corr(XB, y)
        if (b + 1) % 1000 == 0: log(f"[A] boot {b+1}/{BOOT} ({time.time()-t0:.0f}s)")
    def ci(a): return np.percentile(a, 2.5, 0), np.percentile(a, 97.5, 0)
    aI_lo, aI_hi = ci(aI); aB_lo, aB_hi = ci(aB); tI_lo, tI_hi = ci(tI); tB_lo, tB_hi = ci(tB)

    # ---- null: shuffle Y_signed WITHIN template, recompute tracking r (1000 draws) ----
    nI = np.empty((NULLN, HD)); nB = np.empty((NULLN, HD))
    for d in range(NULLN):
        yp = Ysig.copy()
        for t in range(NTMPL):
            gi = by_t[t]; yp[gi] = rng.permutation(yp[gi])
        nI[d] = vec_corr(Aimp, yp); nB[d] = vec_corr(Ablk, yp)
        if (d + 1) % 500 == 0: log(f"[A] null {d+1}/{NULLN} ({time.time()-t0:.0f}s)")
    # per-head empirical two-sided p vs its own null
    nullp_imp = (np.abs(nI) >= np.abs(track_imp)).mean(0)
    nullp_blk = (np.abs(nB) >= np.abs(track_blk)).mean(0)

    BONF = 0.05 / HD
    ci_excl0_imp = (tI_lo > 0) | (tI_hi < 0); ci_excl0_blk = (tB_lo > 0) | (tB_hi < 0)
    surv_imp = (nullp_imp < BONF) & ci_excl0_imp
    surv_blk = (nullp_blk < BONF) & ci_excl0_blk

    # ---- ranked table (sorted by max |tracking r| under either lens) ----
    LH = [(L, h) for L in range(nL) for h in range(nH)]
    order = np.argsort(-np.maximum(np.abs(track_imp), np.abs(track_blk)))
    rows = []
    for j in order:
        L, h = LH[j]
        rows.append({"layer": L, "head": h,
                     "alloc_imp": alloc_imp[j], "alloc_imp_lo": aI_lo[j], "alloc_imp_hi": aI_hi[j],
                     "track_imp_r": track_imp[j], "track_imp_lo": tI_lo[j], "track_imp_hi": tI_hi[j],
                     "track_imp_nullp": nullp_imp[j], "surv_imp": bool(surv_imp[j]),
                     "alloc_blk": alloc_blk[j], "alloc_blk_lo": aB_lo[j], "alloc_blk_hi": aB_hi[j],
                     "track_blk_r": track_blk[j], "track_blk_lo": tB_lo[j], "track_blk_hi": tB_hi[j],
                     "track_blk_nullp": nullp_blk[j], "surv_blk": bool(surv_blk[j])})
    cols = ["layer", "head", "alloc_imp", "alloc_imp_lo", "alloc_imp_hi", "track_imp_r", "track_imp_lo",
            "track_imp_hi", "track_imp_nullp", "surv_imp", "alloc_blk", "alloc_blk_lo", "alloc_blk_hi",
            "track_blk_r", "track_blk_lo", "track_blk_hi", "track_blk_nullp", "surv_blk"]
    csvfn = os.path.join(OUT, "att01_heads_smoke.csv" if SMOKE else "att01_heads.csv")
    with open(csvfn, "w") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join(("%d" % r[c] if c in ("layer", "head") else
                              ("%s" % r[c] if c in ("surv_imp", "surv_blk") else "%.6f" % r[c])) for c in cols) + "\n")

    n_surv_imp = int(surv_imp.sum()); n_surv_blk = int(surv_blk.sum())
    # falsifier (SS8): no head tracks above null at Bonferroni under EITHER lens -> attention at readout
    # does not carry arbitration; arbitration lives where neither instrument looks (a bigger finding).
    falsifier_fired = bool(n_surv_imp == 0 and n_surv_blk == 0)
    top = rows[0]
    disagree = bool((top["surv_imp"] != top["surv_blk"]) or
                    (np.sign(top["track_imp_r"]) != np.sign(top["track_blk_r"]) and
                     min(abs(top["track_imp_r"]), abs(top["track_blk_r"])) > 0.05))
    out = {"prereg": "PREREG_ATT01.md", "chained_to_H4": "da688c1ec1194bd04cc147aa0aeadc1cc2d5407da8d59670943019abb63f9f75",
           "SMOKE": SMOKE, "n": N, "n_layers": nL, "n_heads": nH, "head_family": HD, "bonferroni_alpha": BONF,
           "transformers": transformers.__version__, "boot": BOOT, "null_draws": NULLN,
           "n_survivors_imp": n_surv_imp, "n_survivors_blk": n_surv_blk,
           "falsifier_fired_no_tracking_head": falsifier_fired,
           "top_head": {"layer": top["layer"], "head": top["head"],
                        "track_imp_r": top["track_imp_r"], "track_imp_nullp": top["track_imp_nullp"],
                        "track_blk_r": top["track_blk_r"], "track_blk_nullp": top["track_blk_nullp"]},
           "top10": [{"layer": r["layer"], "head": r["head"], "track_imp_r": round(r["track_imp_r"], 4),
                      "track_imp_nullp": r["track_imp_nullp"], "track_blk_r": round(r["track_blk_r"], 4),
                      "track_blk_nullp": r["track_blk_nullp"], "surv_imp": r["surv_imp"], "surv_blk": r["surv_blk"]}
                     for r in rows[:10,
           "imp_blk_top_disagree": disagree,
           "note": "OBSERVATIONAL. correlation is correlation; ranked list = targets for a future patching "
                   "probe, NOT a causal path. No causal verb in the verdict.",
           "runtime_s": round(time.time() - t0, 1)}
    jf = os.path.join(OUT, "att01_smoke.json" if SMOKE else "att01.json")
    json.dump(out, open(jf, "w"), indent=2)
    log(f"[A] survivors imp={n_surv_imp} blk={n_surv_blk} falsifier={falsifier_fired}; "
        f"top L{top['layer']}H{top['head']} r_imp={top['track_imp_r']:+.3f} r_blk={top['track_blk_r']:+.3f}; "
        f"wrote {csvfn} + {jf}")

if __name__ == "__main__":
    main()
