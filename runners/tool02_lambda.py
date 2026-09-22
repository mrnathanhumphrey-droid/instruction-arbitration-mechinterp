#!/usr/bin/env python
# TOOL-02 -- does ANY model's native chat-template formatting resist tool-borne injection? Template design -> resistance, in nats.
# PREREG_TOOL02.md sha 348608042a6ebbf5f83afc2050e6d4e92113a29ea88efd7d90f717d0c96221e0, chained TOOL-01 f7487149...
# FORWARD PASSES ONLY (no patching). One model per invocation (env MODEL_KEY in {llama,qwen,mistral}).
# Readout Y = logP(POS)-logP(NEG) at first assistant token (POS/NEG from stimuli; single-token per Gate 1).
# Y_signed = +R if target_sys==POS else -R  (+Y = obeys SYSTEM, B<0 = obeys injected/tool block).
# Conditions (per model, injection last): B_user (plain user, raw) | B_user_pad (distance-matched to native) |
#   B_tool_native (deployment path) | B_tool_markeronly (tool marker/structure, serialization stripped; Llama/Mistral only).
# Contrasts: d_native_raw = tool_native-user ; d_native_matched = tool_native-user_pad ; d_role = markeronly-user_pad ;
#   d_serial = tool_native-markeronly ; pad_only = user_pad-user (small-d exchange-rate point, persisted).
# Module-level build so the local tokenizer-only dry-check exercises the EXACT runner code.
import os, json, time, csv, re
import numpy as np
from collections import defaultdict
from make_tool_stimuli_cross import TEMPLATES

MODEL_KEY = os.environ.get("MODEL_KEY", "llama")
MODEL_ID = {"llama": "meta-llama/Llama-3.1-8B-Instruct",
            "qwen": "Qwen/Qwen2.5-7B-Instruct",
            "mistral": "mistralai/Mistral-7B-Instruct-v0.3"}[MODEL_KEY]
HAS_MARKERONLY = MODEL_KEY in ("llama", "mistral")   # Qwen: <tool_response> tags ARE the marker -> not separable (N/A)


def base3(it):
    return [{"role": "system", "content": it["system"]},
            {"role": "user", "content": it["user_trigger"]},
            {"role": "assistant", "content": it["assistant_stub"]}]


def render_user(tok, it):
    m = base3(it) + [{"role": "user", "content": it["tool_text"]}]
    return tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True)


def render_native(tok, it):
    if MODEL_KEY == "llama":
        m = base3(it) + [{"role": "tool", "content": {"output": it["tool_text"]}}]
    elif MODEL_KEY == "qwen":
        m = base3(it) + [{"role": "tool", "content": it["tool_text"]}]
    else:  # mistral: tool flow requires an assistant tool_call + 9-char alnum call id
        m = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user_trigger"]},
             {"role": "assistant", "content": "", "tool_calls": [
                 {"id": "call00001", "type": "function", "function": {"name": "get_calendar", "arguments": {}}}]},
             {"role": "tool", "content": it["tool_text"], "tool_call_id": "call00001", "name": "get_calendar"}]
    return tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True)


def render_markeronly(it, native_text):
    tt = it["tool_text"]
    if MODEL_KEY == "llama":
        return native_text.replace(json.dumps({"output": tt}), tt)
    return re.sub(r"(\[TOOL_RESULTS\])(.*?)(\[/TOOL_RESULTS\])",
                  lambda mm: mm.group(1) + " " + tt + mm.group(3), native_text, count=1, flags=re.S)


def imp_span(tok, text, imp):
    enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
    offs = enc["offset_mapping"]; ids = enc["input_ids"]
    cs = text.index(imp); ce = cs + len(imp)
    sp = [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
    return ids, sp, offs


def dist_end(ids, sp): return (len(ids) - 1) - sp[-1]


def _pad_after_content(tok, text, ids, sp, tt, native_de, nid):
    """Insert N=native_de-this_de neutral tokens right after the tool_text content; return (ids, sp)."""
    N = native_de - dist_end(ids, sp)
    if N <= 0:
        return list(ids), list(sp)
    offs = tok(text, return_offsets_mapping=True, add_special_tokens=False)["offset_mapping"]
    ce_char = text.index(tt) + len(tt)
    ins = max((i for i, (a, b) in enumerate(offs) if b <= ce_char and b > a), default=sp[-1])
    return ids[:ins + 1] + [nid] * N + ids[ins + 1:], [i if i <= ins else i + N for i in sp]


def build(tok, it, nid):
    imp_t = TEMPLATES[it["template_idx".format(T=it["target_tool"])
    u_txt = render_user(tok, it); n_txt = render_native(tok, it)
    u_ids, u_sp, _ = imp_span(tok, u_txt, imp_t)
    n_ids, n_sp, _ = imp_span(tok, n_txt, imp_t)
    native_de = dist_end(n_ids, n_sp)
    out = {"user": (u_ids, u_sp), "native": (n_ids, n_sp)}
    out["user_pad"] = _pad_after_content(tok, u_txt, u_ids, u_sp, it["tool_text"], native_de, nid)
    if HAS_MARKERONLY:
        mo_txt = render_markeronly(it, n_txt)
        mo_ids, mo_sp, _ = imp_span(tok, mo_txt, imp_t)
        out["markeronly"] = _pad_after_content(tok, mo_txt, mo_ids, mo_sp, it["tool_text"], native_de, nid)
    return out


def main():
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    t0 = time.time()
    HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
    HF = os.environ.get("HF_TOKEN") or None
    SMOKE = os.environ.get("SMOKE", "0") == "1"
    STIM = os.environ.get("STIM", "stimuli_tool_contested_true_false.jsonl")
    NTMPL = 30; BOOT = 300 if SMOKE else 5000; SEED = 20260922
    stim = [json.loads(l) for l in open(os.path.join(HERE, STIM), encoding="utf-8")]
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    POS = stim[0]["readout_pos"]; NEG = stim[0]["readout_neg"]
    ip = tok(POS, add_special_tokens=False)["input_ids"]; ineg = tok(NEG, add_special_tokens=False)["input_ids"]
    assert len(ip) == 1 and len(ineg) == 1, f"GATE1 FAIL: {POS}/{NEG} not single-token in {MODEL_KEY}"
    TPOS, TNEG = ip[0], ineg[0]
    nid = tok(".", add_special_tokens=False)["input_ids"][-1]
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import transformers
    print(f"[T2:{MODEL_KEY}] {MODEL_ID} on {dev}; tf {transformers.__version__} n={len(stim)} readout={POS}/{NEG}={TPOS}/{TNEG} ({time.time()-t0:.0f}s)", flush=True)

    def run(ids):
        t = torch.tensor([ids], dtype=torch.long, device=dev)
        with torch.inference_mode():
            lg = model(input_ids=t, use_cache=False).logits[0, -1, :].float()
        lp = torch.log_softmax(lg, -1); return float(lp[TPOS] - lp[TNEG])
    def ysig(R, it): return R if it["target_sys"] == POS else -R

    use = list(range(len(stim)))
    if SMOKE:
        step = max(1, len(stim) // 40); use = list(range(0, len(stim), step))[:40]
    N = len(use); tmpl = np.array([stim[i]["template_idx"] for i in use])
    arms = ["user", "user_pad", "native"] + (["markeronly"] if HAS_MARKERONLY else [])
    Y = {a: np.zeros(N) for a in arms}; De = {a: np.zeros(N) for a in arms}
    for n, i in enumerate(use):
        it = stim[i]; b = build(tok, it, nid)
        for a in arms:
            ids, sp = b[a]; Y[a][n] = ysig(run(ids), it); De[a][n] = (len(ids) - 1) - sp[-1]
        if (n + 1) % 120 == 0: print(f"[T2:{MODEL_KEY}] {n+1}/{N} ({time.time()-t0:.0f}s)", flush=True)
    means = {a: float(Y[a].mean()) for a in arms}; dmeans = {a: float(De[a].mean()) for a in arms}
    print(f"[T2:{MODEL_KEY}] means " + " ".join(f"{a}={means[a]:+.3f}" for a in arms) + f" ({time.time()-t0:.0f}s)", flush=True)
    print(f"[T2:{MODEL_KEY}] dist_end " + " ".join(f"{a}={dmeans[a]:.2f}" for a in arms), flush=True)

    np.savez(os.path.join(OUT, f"tool02_{MODEL_KEY}_peritem{'_smoke' if SMOKE else ''}.npz"),
             use=np.array(use), tmpl=tmpl, **{f"Y_{a}": Y[a] for a in arms}, **{f"De_{a}": De[a] for a in arms})

    def per_t(a): return np.array([a[tmpl == t].mean() if (tmpl == t).any() else 0.0 for t in range(NTMPL)])
    pt = {a: per_t(Y[a]) for a in arms}
    rng = np.random.default_rng(SEED)
    keys = ["B_user", "B_native", "d_native_raw", "d_native_matched", "pad_only"]
    if HAS_MARKERONLY: keys += ["B_markeronly", "d_role", "d_serial"]
    boot = {k: np.empty(BOOT) for k in keys}
    for bi in range(BOOT):
        pk = rng.integers(0, NTMPL, NTMPL)
        u = pt["user"][pk].mean(); up = pt["user_pad"][pk].mean(); nv = pt["native"][pk].mean()
        boot["B_user"][bi] = u; boot["B_native"][bi] = nv
        boot["d_native_raw"][bi] = nv - u; boot["d_native_matched"][bi] = nv - up; boot["pad_only"][bi] = up - u
        if HAS_MARKERONLY:
            mo = pt["markeronly"][pk].mean(); boot["B_markeronly"][bi] = mo
            boot["d_role"][bi] = mo - up; boot["d_serial"][bi] = nv - mo
    def ci(a): lo, hi = np.nanpercentile(a, [2.5, 97.5]); return [float(lo), float(hi)]
    C = {k: ci(boot[k]) for k in keys}
    val = {"B_user": means["user"], "B_native": means["native"],
           "d_native_raw": means["native"] - means["user"], "d_native_matched": means["native"] - means["user_pad"],
           "pad_only": means["user_pad"] - means["user"]}
    if HAS_MARKERONLY:
        val["B_markeronly"] = means["markeronly"]; val["d_role"] = means["markeronly"] - means["user_pad"]
        val["d_serial"] = means["native"] - means["markeronly"]

    out = {"prereg": "PREREG_TOOL02.md", "SMOKE": SMOKE, "model_key": MODEL_KEY, "model_id": MODEL_ID,
           "prereg_sha256": "348608042a6ebbf5f83afc2050e6d4e92113a29ea88efd7d90f717d0c96221e0",
           "chained_to_TOOL01": "f74871490f7be6efdd4ebc830751f44f949c7055cda9046984428a0831694456",
           "transformers": transformers.__version__, "n": N, "readout": [POS, NEG],
           "has_markeronly": HAS_MARKERONLY, "means": means, "dist_end_means": dmeans, "values": val, "cis": C,
           "note_mistral": ("Mistral tool flow requires an assistant tool_call turn; B_user/pad use a text stub, so "
                            "d_native/d_role include that assistant-turn difference (intrinsic to routing through the tool "
                            "channel); d_serial (native vs markeronly) is clean (shared tool_call prefix)." if MODEL_KEY == "mistral" else ""),
           "note_qwen": ("Qwen renders tool output as a user turn + <tool_response> tags = NO privileged tool role; "
                         "markeronly N/A; d_native IS the combined tag effect." if MODEL_KEY == "qwen" else ""),
           "runtime_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, f"tool02_{MODEL_KEY}_arms{'_smoke' if SMOKE else ''}.csv"), "w", newline="") as fc:
        w = csv.writer(fc); w.writerow(["quantity", "value", "ci_lo", "ci_hi"])
        for k in keys: w.writerow([k, round(val[k], 4), round(C[k][0], 4), round(C[k][1], 4)])
        for a in arms: w.writerow([f"dist_end_{a}", round(dmeans[a], 3), "", ""])
    fn = os.path.join(OUT, f"tool02_{MODEL_KEY}{'_smoke' if SMOKE else ''}.json")
    json.dump(out, open(fn, "w"), indent=2)
    dr = f" d_role={val['d_role']:+.3f}{C['d_role']} d_serial={val['d_serial']:+.3f}{C['d_serial']}" if HAS_MARKERONLY else " (markeronly N/A)"
    print(f"[T2:{MODEL_KEY}] d_native_raw={val['d_native_raw']:+.3f}{C['d_native_raw']} matched={val['d_native_matched']:+.3f}{C['d_native_matched']} "
          f"pad_only={val['pad_only']:+.3f}{C['pad_only']}{dr}; wrote {fn}", flush=True)


if __name__ == "__main__":
    main()
