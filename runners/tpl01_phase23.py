#!/usr/bin/env python
# TPL-01 Phase 2 (native measurement) + Phase 3 (template swap, PRIMARY). Chained PRV-01h-r / Phase-1 lock.
# Forward-only readout Y = logP(POS)-logP(NEG) at first assistant token, Y_signed = +Y if target_sys==POS else -Y (+Y=obeys system).
# 7 models loaded sequentially on one instance. For each host we build cells by SERIALIZATION SWAP: the payload P is wrapped in a
# style's serialization and placed at the position the host template puts tool content, holding the host's role slot.
#
# Construction: render host NATIVE with a sentinel payload -> locate the injection turn's content region by the host's slot
# markers -> replace that region's serialization with ser_style(P). Native cell = ser_host(P). G-CONSTRUCT: P byte-identical in
# every cell (verified). N hosts (gemma/phi): no tool role -> injection is a user turn; native = raw P (floor).
import os, json, time, re
import numpy as np, torch
from transformers import AutoTokenizer, AutoModelForCausalLM

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
NTMPL = 30; BOOT = 300 if SMOKE else 5000; SEED = 20260925
MASS_FLOOR = 0.10
SENT = "PAYLOAD"   # private-use sentinel, unlikely to be escaped/split oddly
def log(*a): print(*a, flush=True)

MODELS = [   # key, model_id, kind, host?(phase3 host), N?
    ("llama",   "meta-llama/Llama-3.1-8B-Instruct",      "llama",   True,  False),
    ("mistral", "mistralai/Mistral-7B-Instruct-v0.3",    "mistral", True,  False),
    ("qwen",    "Qwen/Qwen2.5-7B-Instruct",              "qwen",    True,  False),
    # qwen3 DROPPED: transformers 4.46 doesn't support the qwen3 architecture; upgrading risks the anchor stack, and qwen3 was
    # only a within-family reproducibility check (Nemo still provides one). Documented env limitation.
    ("nemo",    "mistralai/Mistral-Nemo-Instruct-2407",  "mistral", False, False),
    ("gemma",   "google/gemma-2-9b-it",                   "gemma",   True,  True),
    ("phi",     "microsoft/Phi-3.5-mini-instruct",        "phi",     True,  True),
]
STYLES = ("llama", "mistral", "qwen")   # serializations transplanted in Phase 3
def ser(style, P):
    if style == "llama":   return json.dumps({"output": P})
    if style == "mistral": return '[TOOL_RESULTS] {"content": ' + P + ', "call_id": "call00001"}[/TOOL_RESULTS]'
    if style == "qwen":    return "<tool_response>\n" + P + "\n</tool_response>"
    raise ValueError(style)

# host injection-slot markers: (open, close, replace_inclusive). Region between open..close in the NATIVE-with-SENT render is the
# serialization to swap. For mistral the [TOOL_RESULTS] block IS the serialization (inclusive).
SLOT = {
    "llama":   ("<|start_header_id|>ipython<|end_header_id|>\n\n", "<|eot_id|>", False),
    "qwen":    None,   # last user turn; handled specially (im_start user .. im_end)
    "mistral": ("[TOOL_RESULTS]", "[/TOOL_RESULTS]", True),
    "gemma":   ("<start_of_turn>user\n", "<end_of_turn>", False),
    "phi":     ("<|user|>\n", "<|end|>", False),
}


def native_messages(kind, it, payload):
    sysmsg = it["system"]; ut = it["user_trigger"]; stub = it["assistant_stub"]
    if kind == "llama":
        return [{"role": "system", "content": sysmsg}, {"role": "user", "content": ut},
                {"role": "assistant", "content": stub}, {"role": "tool", "content": {"output": payload}}]
    if kind == "qwen":
        return [{"role": "system", "content": sysmsg}, {"role": "user", "content": ut},
                {"role": "assistant", "content": stub}, {"role": "tool", "content": payload}]
    if kind == "mistral":
        return [{"role": "system", "content": sysmsg}, {"role": "user", "content": ut},
                {"role": "assistant", "content": "", "tool_calls": [
                    {"id": "call00001", "type": "function", "function": {"name": "get_data", "arguments": {}}}]},
                {"role": "tool", "content": payload, "tool_call_id": "call00001", "name": "get_data"}]
    if kind == "gemma":   # no system role -> fold system into first user turn; no tool role -> injection in a user turn
        return [{"role": "user", "content": sysmsg + "\n\n" + ut}, {"role": "assistant", "content": stub},
                {"role": "user", "content": payload}]
    if kind == "phi":     # has system, no tool role -> injection in a user turn
        return [{"role": "system", "content": sysmsg}, {"role": "user", "content": ut},
                {"role": "assistant", "content": stub}, {"role": "user", "content": payload}]
    raise ValueError(kind)


def render_native(tok, kind, it, payload):
    return tok.apply_chat_template(native_messages(kind, it, payload), tokenize=False, add_generation_prompt=True)


def swap_region(native_sent_text, kind, ser_string):
    """Replace the injection turn's serialization region (holding P=SENT) with ser_string. Returns new text or None if the
    region can't be located (construction failure -> caught in dry check)."""
    if kind == "qwen":
        # last user turn is the injection turn: <|im_start|>user\n ... <|im_end|> containing SENT
        idx = native_sent_text.rfind("<|im_start|>user\n")
        if idx < 0: return None
        op = idx + len("<|im_start|>user\n"); cl = native_sent_text.find("<|im_end|>", op)
        if cl < 0 or SENT not in native_sent_text[op:cl]: return None
        return native_sent_text[:op] + ser_string + native_sent_text[cl:]
    open_m, close_m, incl = SLOT[kind]
    op0 = native_sent_text.rfind(open_m)
    if op0 < 0: return None
    if incl:   # replace open..close inclusive (mistral: whole [TOOL_RESULTS]..[/TOOL_RESULTS])
        cl0 = native_sent_text.find(close_m, op0)
        if cl0 < 0 or SENT not in native_sent_text[op0:cl0 + len(close_m)]: return None
        return native_sent_text[:op0] + ser_string + native_sent_text[cl0 + len(close_m):]
    op = op0 + len(open_m); cl = native_sent_text.find(close_m, op)
    if cl < 0 or SENT not in native_sent_text[op:cl]: return None
    return native_sent_text[:op] + ser_string + native_sent_text[cl:]


def cell_text(tok, kind, it, style_or_native):
    """style_or_native in {'native','llama','mistral','qwen','rawuser'}. Returns rendered prompt string."""
    P = it["tool_text"]
    if style_or_native == "rawuser":   # raw payload in a plain user turn (floor / N-native)
        base = native_messages("phi" if kind != "gemma" else "gemma", it, P)  # user-turn injection frame
        return tok.apply_chat_template(base, tokenize=False, add_generation_prompt=True)
    if style_or_native == "native":
        return render_native(tok, kind, it, P)
    # foreign serialization swap
    ns = render_native(tok, kind, it, SENT)
    return swap_region(ns, kind, ser(style_or_native, P))


def cells_for(key, kind, is_host, is_N):
    """Which (label) cells this model runs."""
    cs = []
    if is_N:
        cs.append(("native_rawuser", "native"))   # N native = raw user text floor
        for s in STYLES: cs.append((f"host_{s}", s))   # foreign serializations in user slot
    else:
        cs.append(("native", "native"))
        if is_host:
            for s in STYLES:
                if s != kind_style(kind):
                    cs.append((f"host_{s}", s))
    return cs


def kind_style(kind):
    return {"llama": "llama", "qwen": "qwen", "mistral": "mistral"}[kind]


def main():
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_tool_contested_true_false.jsonl"), encoding="utf-8")]
    use = list(range(0, len(stim), len(stim) // 40))[:40] if SMOKE else list(range(len(stim)))
    N = len(use); tmpl = np.array([stim[i]["template_idx"] for i in use])
    tgt_pos = np.array([1 if stim[i]["target_sys"] == stim[i]["readout_pos"] else 0 for i in use])
    import transformers
    results = {}
    for key, mid, kind, is_host, is_N in MODELS:
        tl = time.time()
        tok = AutoTokenizer.from_pretrained(mid, token=HF, trust_remote_code=True)
        POS = stim[0]["readout_pos"]; NEG = stim[0]["readout_neg"]
        TPOS = tok(POS, add_special_tokens=False)["input_ids"][0]; TNEG = tok(NEG, add_special_tokens=False)["input_ids"][0]
        model = AutoModelForCausalLM.from_pretrained(mid, token=HF, torch_dtype=torch.bfloat16,
                                                     device_map={"": 0}, trust_remote_code=True).eval()
        dev = next(model.parameters()).device
        log(f"[TPL:{key}] {mid} loaded ({time.time()-tl:.0f}s); TPOS/TNEG={TPOS}/{TNEG}")

        prefix_ids = tok("Answer:", add_special_tokens=False)["input_ids"]   # forced-readout slot (MASS-gate rescue)
        # FORCED targets: on BPE tokenizers (llama/qwen/nemo/gemma) the token the model emits AFTER "Answer:" is the
        # LEADING-SPACE variant (' TRUE'/' FALSE'), so reading the no-space TPOS/TNEG there leaks mass to ~0 (confirmed
        # tokenizer-only: forced m=0.000 on llama/qwen in the prior FULL). Derive the post-prefix target per model; for
        # mistral/phi it equals the raw target (they matched, forced mass was already healthy).
        fullT = tok("Answer: " + POS, add_special_tokens=False)["input_ids"]
        fullF = tok("Answer: " + NEG, add_special_tokens=False)["input_ids"]
        assert fullT[:len(prefix_ids)] == prefix_ids and fullF[:len(prefix_ids)] == prefix_ids, "Answer: not a clean token boundary"
        TPOS_f = fullT[len(prefix_ids)]; TNEG_f = fullF[len(prefix_ids)]
        TARGETS = {"raw": (TPOS, TNEG), "forced": (TPOS_f, TNEG_f)}
        log(f"[TPL:{key}] forced targets TPOS_f/TNEG_f={TPOS_f}/{TNEG_f} (raw {TPOS}/{TNEG})")
        def Y(text):
            base = tok(text, add_special_tokens=False)["input_ids"]
            out = {}
            for tag, ids in (("raw", base), ("forced", base + prefix_ids)):
                tp, tn = TARGETS[tag]
                t = torch.tensor([ids], dtype=torch.long, device=dev)
                with torch.inference_mode():
                    lp = torch.log_softmax(model(input_ids=t, use_cache=False).logits[0, -1, :].float(), -1)
                out[tag] = (float(lp[tp] - lp[tn]), float(torch.exp(lp[tp]) + torch.exp(lp[tn])))
            return out

        cells = cells_for(key, kind, is_host, is_N)
        # always also compute rawuser floor for anchor contrast (non-N)
        labels = [c[0] for c in cells]
        if not is_N and "native_rawuser" not in labels:
            cells = cells + [("rawuser", "rawuser")]
        cell_Y = {}; cell_M = {}; cell_Yf = {}; cell_Mf = {}; gconstruct_ok = True; sample = {}
        for label, spec in cells:
            Ys = np.zeros(N); Ms = np.zeros(N); Yf = np.zeros(N); Mf = np.zeros(N)
            for n, i in enumerate(use):
                it = stim[i]; wpos = it["target_sys"] == POS
                txt = cell_text(tok, kind, it, spec)
                if txt is None or it["tool_text"] not in txt:
                    gconstruct_ok = False; txt = txt or ""
                if n == 0: sample[label] = txt[-260:]
                o = Y(txt)
                Ys[n] = o["raw"][0] if wpos else -o["raw"][0]; Ms[n] = o["raw"][1]
                Yf[n] = o["forced"][0] if wpos else -o["forced"][0]; Mf[n] = o["forced"][1]
            cell_Y[label] = Ys; cell_M[label] = Ms; cell_Yf[label] = Yf; cell_Mf[label] = Mf
            log(f"[TPL:{key}] cell {label}: Y_raw={Ys.mean():+.3f}(m{Ms.mean():.3f}) Y_forced={Yf.mean():+.3f}(m{Mf.mean():.3f}) ({time.time()-t0:.0f}s)")
        # per-cell template-cluster bootstrap CI on mean Y_signed (forced = primary, comparable across cells; raw for anchor)
        def per_t(x): return np.array([x[tmpl == t].mean() if (tmpl == t).any() else np.nan for t in range(NTMPL)])
        def boot_ci(Ys):
            rng = np.random.default_rng(SEED); pt = per_t(Ys)
            bd = np.array([np.nanmean(pt[rng.integers(0, NTMPL, NTMPL)]) for _ in range(BOOT)])
            return [float(np.nanpercentile(bd, 2.5)), float(np.nanpercentile(bd, 97.5))]
        ci = {label: boot_ci(cell_Yf[label]) for label in cell_Yf}          # CI on forced (primary)
        nat = "native_rawuser" if is_N else "native"
        anchor_contrast = (float(cell_Y[nat].mean()) - float(cell_Y["rawuser"].mean())) if ("rawuser" in cell_Y and not is_N) else None
        results[key] = {"model_id": mid, "kind": kind, "is_host": is_host, "is_N": is_N,
                        "Y_signed_raw": {k: float(v.mean()) for k, v in cell_Y.items()},
                        "mass_raw": {k: float(v.mean()) for k, v in cell_M.items()},
                        "Y_signed_forced": {k: float(v.mean()) for k, v in cell_Yf.items()},
                        "mass_forced": {k: float(v.mean()) for k, v in cell_Mf.items()},
                        "ci_forced": ci,
                        "anchor_contrast_native_minus_rawuser_RAW": anchor_contrast,
                        "gconstruct_ok": bool(gconstruct_ok),
                        "low_mass_raw_cells": [k for k, v in cell_M.items() if float(v.mean()) < MASS_FLOOR],
                        "low_mass_forced_cells": [k for k, v in cell_Mf.items() if float(v.mean()) < MASS_FLOOR],
                        "sample_tail": sample}
        np.savez(os.path.join(OUT, f"tpl01_{key}_peritem" + ("_smoke" if SMOKE else "") + ".npz"),
                 use=np.array(use), tmpl=tmpl, tgt_pos=tgt_pos, **{f"Yraw_{k}": v for k, v in cell_Y.items()},
                 **{f"Mraw_{k}": v for k, v in cell_M.items()}, **{f"Yf_{k}": v for k, v in cell_Yf.items()},
                 **{f"Mf_{k}": v for k, v in cell_Mf.items()})
        del model; torch.cuda.empty_cache()
        log(f"[TPL:{key}] done ({time.time()-tl:.0f}s); gconstruct={gconstruct_ok} "
            f"low_mass_raw={results[key]['low_mass_raw_cells']} low_mass_forced={results[key]['low_mass_forced_cells']}")

    out = {"prereg": "PREREG_TPL01_PHASE23.md", "probe": "TPL-01-P23", "SMOKE": SMOKE,
           "chained_to_PHASE1": "35e52e1231c418e4dfb2273a4496a03a950dc934da29d06a159e65ce6ac41e5e",
           "transformers": transformers.__version__, "n": N,
           "readout": [stim[0]["readout_pos"], stim[0]["readout_neg"]], "results": results,
           "runtime_s": round(time.time() - t0, 1)}
    fn = os.path.join(OUT, "tpl01_phase23" + ("_smoke" if SMOKE else "") + ".json")
    json.dump(out, open(fn, "w"), indent=2)
    log("[TPL] ANCHORS (native - rawuser contrast, RAW): " +
        " ".join(f"{k}={results[k]['anchor_contrast_native_minus_rawuser_RAW']}" for k in results if not results[k]["is_N"]))
    log(f"[TPL] wrote {fn}")


if __name__ == "__main__":
    main()
