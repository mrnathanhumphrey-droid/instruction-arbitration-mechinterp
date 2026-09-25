#!/usr/bin/env python
# AUTH-01 Phase 1 -- the authority curve (B). Llama-3.1-8B-Instruct, system-vs-USER contest, FORWARD ONLY.
# PREREG_AUTH01.md sha b2d1cc09d924470bb9d03e31ac988f13667c6437b49653e911e388ab09289f42, chained TOOL-03 a41a922b...
# Y=logP(POS)-logP(NEG) (TRUE/FALSE) at first assistant token; Y_signed=+R if target_sys==POS (+Y=obeys system).
# distance d in {0,256,1k,4k,16k} x order {normal,flipped}; filler placement: primary=after EARLY block (varies the
# recency GAP), secondary=after LATE block (absolute distance, holds gap; run at d in {1k,4k}). B_role(d)=(Bn+Bf)/2,
# B_recency(d)=(Bn-Bf)/2. Per-cell uncontested compliance FLOOR gate (degradation != deprioritization).
# logits_to_keep=1 (last-token logits only) so a 16k forward doesn't build an ~8GB full-seq logits tensor.
import os, json, time, csv
import numpy as np, torch
from collections import defaultdict
from transformers import AutoTokenizer, AutoModelForCausalLM
from make_stimuli import TEMPLATES

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
NTMPL = 30; BOOT = 300 if SMOKE else 5000; SEED = 20260922
SH, EOT = 128006, 128009
DISTS = [0, 256, 16384] if SMOKE else [0, 256, 1024, 4096, 16384]   # SMOKE includes 16k to validate memory/logits
SECONDARY_DS = [256] if SMOKE else [1024, 4096]
N16K = 4 if SMOKE else 180
NFLOOR = 8 if SMOKE else 60
NSMOKE = 20
def log(*a): print(*a, flush=True)


def _flip_perm(ids):  # old-index order for BOS/pre + user-block + system-block + assistant (ORD-01)
    sh = [i for i, t in enumerate(ids) if t == SH]; eot = [i for i, t in enumerate(ids) if t == EOT]
    pre = list(range(0, sh[0])); sys_blk = list(range(sh[0], eot[0] + 1))
    usr_blk = list(range(sh[1], eot[1] + 1)); asst = list(range(sh[2], len(ids)))
    return pre + usr_blk + sys_blk + asst


def _fill_in_system(order, placement):
    # filler goes in system iff (normal & primary) or (flipped & secondary); else in user
    return (order == "normal" and placement == "primary") or (order == "flipped" and placement == "secondary")


def build_text(tok, filler_ids, it, d, order, placement):
    ch = tok.decode(filler_ids[:d]) if d > 0 else ""
    fs = _fill_in_system(order, placement)
    sys_c = it["system"] + ((" " + ch) if (ch and fs) else "")
    usr_c = it["user"] + ((" " + ch) if (ch and not fs) else "")
    return tok.apply_chat_template([{"role": "system", "content": sys_c}, {"role": "user", "content": usr_c}],
                                   tokenize=False, add_generation_prompt=True)


def build_cell(tok, filler_ids, it, d, order, placement):
    """Return (final ids, competitor-gap, late-imperative->readout distance), measured on the POST-flip sequence."""
    text = build_text(tok, filler_ids, it, d, order, placement)
    enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
    ids = enc["input_ids"]; offs = enc["offset_mapping"]
    imp_s = TEMPLATES[it["template_idx"]].format(T=it["target_sys"])
    imp_u = TEMPLATES[it["template_idx"]].format(T=it["target_usr"])
    def span(imp):
        cs = text.index(imp); ce = cs + len(imp)
        return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
    ss, us = span(imp_s), span(imp_u)
    if order == "flipped":
        perm = _flip_perm(ids); ids = [ids[i] for i in perm]
        newpos = {old: new for new, old in enumerate(perm)}
        ss = sorted(newpos[i] for i in ss); us = sorted(newpos[i] for i in us)
    first, second = (ss, us) if ss[-1] <= us[0] else (us, ss)
    gap = second[0] - first[-1]                 # tokens between the two competing imperatives
    late_to_readout = (len(ids) - 1) - second[-1]  # tokens from the later imperative to the generation position
    return ids, gap, late_to_readout


def contested_ids(tok, filler_ids, it, d, order, placement):
    return build_cell(tok, filler_ids, it, d, order, placement)[0]


def main():
    t0 = time.time()
    contested = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_contested_true_false.jsonl"), encoding="utf-8")]
    uncon = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_uncontested_true_false.jsonl"), encoding="utf-8")]
    filler = open(os.path.join(HERE, "filler.txt"), encoding="utf-8").read()
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    POS = contested[0]["readout_pos"]; NEG = contested[0]["readout_neg"]
    TPOS = tok(POS, add_special_tokens=False)["input_ids"][0]; TNEG = tok(NEG, add_special_tokens=False)["input_ids"][0]
    filler_ids = tok(filler, add_special_tokens=False)["input_ids"]
    assert len(filler_ids) >= max(DISTS), f"filler too short {len(filler_ids)} < {max(DISTS)}"
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16, device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import transformers
    log(f"[A1] {MODEL_ID} on {dev}; tf {transformers.__version__} filler_tok={len(filler_ids)} readout={POS}/{NEG} ({time.time()-t0:.0f}s)")

    def run_last(ids):
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            try:
                lg = model(input_ids=t, use_cache=False, logits_to_keep=1).logits[0, -1, :].float()
            except TypeError:
                lg = model(input_ids=t, use_cache=False, num_logits_to_keep=1).logits[0, -1, :].float()
        return torch.log_softmax(lg, -1)

    def ysig(lp, it): R = float(lp[TPOS] - lp[TNEG]); return R if it["target_sys"] == POS else -R

    # ---- floor per d: uncontested, sole POS instruction in system + filler (primary), P(POS) compliance ----
    def floor_at(d):
        idx = list(range(0, len(uncon), max(1, len(uncon) // NFLOOR)))[:NFLOOR]
        ps = []
        for i in idx:
            it = uncon[i]
            if it["slot"] != "system": continue
            ch = tok.decode(filler_ids[:d]) if d > 0 else ""
            sys_c = it["system"] + (" " + ch if ch else "")
            text = tok.apply_chat_template([{"role": "system", "content": sys_c}, {"role": "user", "content": it["user"]}],
                                           tokenize=False, add_generation_prompt=True)
            lp = run_last(tok(text, add_special_tokens=False)["input_ids"])
            ps.append(float(torch.exp(lp[TPOS])))
        return float(np.mean(ps)) if ps else float("nan")

    # ---- main sweep ----
    cells = []  # (d, order, placement)
    for d in DISTS:
        for order in ["normal", "flipped"]:
            cells.append((d, order, "primary"))
    for d in SECONDARY_DS:
        for order in ["normal", "flipped"]:
            cells.append((d, order, "secondary"))

    results = {}   # (d,order,placement) -> dict(Y per-item, tmpl, gap_mean)
    peritem = {}
    for (d, order, placement) in cells:
        if d == 16384:
            items = contested[:: max(1, len(contested) // N16K)][:N16K]
        elif SMOKE:
            items = contested[:NSMOKE]
        else:
            items = contested
        Y = np.zeros(len(items)); tm = np.zeros(len(items), dtype=int); gaps = []; l2r = []
        for n, it in enumerate(items):
            ids, gap, lr = build_cell(tok, filler_ids, it, d, order, placement)
            Y[n] = ysig(run_last(ids), it); tm[n] = it["template_idx"]
            if n < 24: gaps.append(gap); l2r.append(lr)
        results[(d, order, placement)] = dict(mean=float(Y.mean()), n=len(items),
                                              gap=float(np.mean(gaps)), late2readout=float(np.mean(l2r)))
        peritem[f"{d}_{order}_{placement}_Y"] = Y; peritem[f"{d}_{order}_{placement}_tmpl"] = tm
        log(f"[A1] d={d} {order} {placement}: B={Y.mean():+.3f} n={len(items)} gap~{np.mean(gaps):.0f} late2rdout~{np.mean(l2r):.0f} ({time.time()-t0:.0f}s)")

    floors = {d: floor_at(d) for d in DISTS}
    floor0 = floors[DISTS[0]]
    log(f"[A1] floors {({d: round(v,3) for d,v in floors.items()})} floor0={floor0:.3f}")

    # ---- decomposition + bootstrap per d (primary) ----
    def per_t(Y, tm): return np.array([Y[tm == t].mean() if (tm == t).any() else np.nan for t in range(NTMPL)])
    rng = np.random.default_rng(SEED)
    curve = {}
    for d in DISTS:
        kn, kf = (d, "normal", "primary"), (d, "flipped", "primary")
        Yn, tmn = peritem[f"{d}_normal_primary_Y"], peritem[f"{d}_normal_primary_tmpl"]
        Yf, tmf = peritem[f"{d}_flipped_primary_Y"], peritem[f"{d}_flipped_primary_tmpl"]
        ptn, ptf = per_t(Yn, tmn), per_t(Yf, tmf)
        role = np.empty(BOOT); rec = np.empty(BOOT); bn = np.empty(BOOT); bf = np.empty(BOOT)
        for b in range(BOOT):
            pk = rng.integers(0, NTMPL, NTMPL)
            n_, f_ = np.nanmean(ptn[pk]), np.nanmean(ptf[pk])
            bn[b] = n_; bf[b] = f_; role[b] = (n_ + f_) / 2; rec[b] = (n_ - f_) / 2
        def ci(a): lo, hi = np.nanpercentile(a, [2.5, 97.5]); return [float(lo), float(hi)]
        degraded = bool(floors[d] < 0.5 * floor0)
        curve[d] = {"B_normal": results[kn]["mean"], "B_flipped": results[kf]["mean"],
                    "B_role": float(np.nanmean(role)), "B_role_ci": ci(role),
                    "B_recency": float(np.nanmean(rec)), "B_recency_ci": ci(rec),
                    "floor": floors[d], "floor_ratio": floors[d] / floor0 if floor0 else float("nan"),
                    "DEGRADED_not_read": degraded, "gap_normal": results[kn]["gap"],
                    "gap_flipped": results[kf]["gap"], "late2readout_normal": results[kn]["late2readout"],
                    "n": results[kn]["n"]}

    secondary = {}
    for d in SECONDARY_DS:
        try:
            Yn = peritem[f"{d}_normal_secondary_Y"]; Yf = peritem[f"{d}_flipped_secondary_Y"]
            secondary[d] = {"B_normal": float(Yn.mean()), "B_flipped": float(Yf.mean()),
                            "B_recency": float((Yn.mean() - Yf.mean()) / 2),
                            "gap_normal": results[(d, "normal", "secondary")]["gap"],
                            "late2readout_normal": results[(d, "normal", "secondary")]["late2readout"]}
        except KeyError:
            pass

    np.savez(os.path.join(OUT, "auth01_phase1_peritem" + ("_smoke" if SMOKE else "") + ".npz"), **peritem,
             floors=np.array([floors[d] for d in DISTS]), dists=np.array(DISTS))
    out = {"prereg": "PREREG_AUTH01.md", "phase": 1, "SMOKE": SMOKE, "model_id": MODEL_ID,
           "prereg_sha256": "b2d1cc09d924470bb9d03e31ac988f13667c6437b49653e911e388ab09289f42",
           "chained_to_TOOL03": "a41a922bae201bad3beda073fc760ddd4bcf5102d6e9921c7f958907c8f15a78",
           "transformers": transformers.__version__, "readout": [POS, NEG], "dists": DISTS,
           "filler_tokens_available": len(filler_ids), "n16k": N16K,
           "curve_primary": {str(d): curve[d] for d in DISTS}, "secondary": {str(d): secondary[d] for d in secondary},
           "floors": {str(d): floors[d] for d in DISTS}, "runtime_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "auth01_phase1_arms" + ("_smoke" if SMOKE else "") + ".csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["d", "B_normal", "B_flipped", "B_role", "role_lo", "role_hi", "B_recency", "rec_lo", "rec_hi", "floor", "floor_ratio", "degraded"])
        for d in DISTS:
            c = curve[d]; w.writerow([d, round(c["B_normal"],3), round(c["B_flipped"],3), round(c["B_role"],3),
                round(c["B_role_ci"][0],3), round(c["B_role_ci"][1],3), round(c["B_recency"],3),
                round(c["B_recency_ci"][0],3), round(c["B_recency_ci"][1],3), round(c["floor"],3), round(c["floor_ratio"],3), c["DEGRADED_not_read"]])
    fn = os.path.join(OUT, "auth01_phase1" + ("_smoke" if SMOKE else "") + ".json")
    json.dump(out, open(fn, "w"), indent=2)
    log("[A1] CURVE (primary): " + " | ".join(
        f"d={d} role={curve[d]['B_role']:+.2f} rec={curve[d]['B_recency']:+.2f} floor={curve[d]['floor']:.2f}"
        + ("[DEGRADED]" if curve[d]["DEGRADED_not_read"] else "") for d in DISTS))
    log(f"[A1] wrote {fn}")


if __name__ == "__main__":
    main()
