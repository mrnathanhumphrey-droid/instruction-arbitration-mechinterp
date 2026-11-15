#!/usr/bin/env python
# TPL-04 STEP ZERO -- tokenizer-only, NO forward. Double-wrap dose-response on the SYSTEM content: disambiguate TPL-03's near-null
# (SIGN-IDENTITY-DEAD-AS-TESTED, one-sided) between (i) true idempotence of same-family nesting and (ii) under-power.
# Depths d in {0(native),1,2}: own_d = d*open + S + d*close (nested), inert_d = d*inert_open + S + d*inert_close (length-matched control).
# THE LOAD-BEARING CHECK (the OPX-06 failure mode): does d=2 realize as TWO distinct delimiter pairs in id-space, or do adjacent
# identical special tokens MERGE/DEDUP so 2x == 1x BY CONSTRUCTION (a degeneracy, not a dose)? If merged on a host, TPL-04 is DEAD
# for that host (no dose axis) -> that host routes to Design B instead. Hosts llama/qwen anchored + gemma; mistral/phi excluded (TPL-03).
import os, json, re
from transformers import AutoTokenizer

def _env(k):
    for l in open("D:/physics_detector/.env", encoding="utf-8"):
        if l.startswith(k + "="): return l.split("=", 1)[1].strip()
    return None
HF = _env("HF_TOKEN")
BATTERY = "D:/Resolve Research/Prompt_Injection/run/tpl01/stimuli_tool_contested_true_false.jsonl"
HOSTS = {"llama":"meta-llama/Llama-3.1-8B-Instruct","qwen":"Qwen/Qwen2.5-7B-Instruct","gemma":"google/gemma-2-9b-it"}
OWNWRAP = {"llama":("<|start_header_id|>","<|end_header_id|>"),
           "qwen":("<|im_start|>","<|im_end|>"), "gemma":("<start_of_turn>","<end_of_turn>")}
NEUTRAL = {"llama":("<|reserved_special_token_0|>","<|reserved_special_token_1|>"),
           "qwen":("<|fim_pad|>","<|fim_pad|>"), "gemma":("<unused0>","<unused1>")}   # qwen fim_pad per TPL-03 DECISION A
DEPTHS = [0, 1, 2]

def wrap(o, c, body, d):
    return o*d + body + c*d

def infix_add(tok, wrapped, native_ids):
    """return (preserved, added_tokens); preserved = native ids are a contiguous infix of wrapped ids."""
    w = tok(wrapped, add_special_tokens=False)["input_ids"]
    for st in range(len(w)-len(native_ids)+1):
        if w[st:st+len(native_ids)] == native_ids: return True, len(w)-len(native_ids), w
    return False, len(w)-len(native_ids), w

def main():
    stim = [json.loads(l) for l in open(BATTERY, encoding="utf-8")]
    sys0 = stim[0]["system"]
    print(f"[S0] battery {len(stim)}; sample system: {sys0[:60]!r}\n")
    all_ok = True
    for host, mid in HOSTS.items():
        tok = AutoTokenizer.from_pretrained(mid, token=HF, trust_remote_code=True)
        added = set(tok.get_added_vocab().values())
        o, c = OWNWRAP[host]; io, ic = NEUTRAL[host]
        o_ids = tok(o, add_special_tokens=False)["input_ids"]; c_ids = tok(c, add_special_tokens=False)["input_ids"]
        io_ids = tok(io, add_special_tokens=False)["input_ids"]; ic_ids = tok(ic, add_special_tokens=False)["input_ids"]
        nat_ids = tok(sys0, add_special_tokens=False)["input_ids"]
        # per-wrap open/close special ids (a single pair token each, from TPL-03)
        o_sp = [t for t in o_ids if t in added]; c_sp = [t for t in c_ids if t in added]
        host_ok = True; own_seqs = {}
        per_depth = []
        for d in DEPTHS:
            own = wrap(o, c, sys0, d); inr = wrap(io, ic, sys0, d)
            p_own, add_own, own_w = infix_add(tok, own, nat_ids)
            p_inr, add_inr, inr_w = infix_add(tok, inr, nat_ids)
            own_seqs[d] = tuple(own_w)
            # ANTI-MERGE: count the own open/close special ids actually present; must equal d each (d=2 -> 2, not merged to 1)
            n_open = sum(own_w.count(t) for t in o_sp); n_close = sum(own_w.count(t) for t in c_sp)
            realized = (n_open == d * len(o_sp)) and (n_close == d * len(c_sp)) if d > 0 else True
            bal = (add_own == add_inr)
            per_depth.append((d, p_own, add_own, p_inr, add_inr, n_open, n_close, realized, bal))
            host_ok = host_ok and p_own and p_inr and bal and realized
        # dose axis exists? own_0/own_1/own_2 all token-distinct (2x != 1x by construction)
        distinct = len({own_seqs[0], own_seqs[1], own_seqs[2]}) == 3
        # the decisive anti-merge tell: added tokens double from d=1 to d=2
        add1 = per_depth[1][2]; add2 = per_depth[2][2]; doubles = (add2 == 2*add1) and add1 > 0
        host_ok = host_ok and distinct and doubles
        all_ok = all_ok and host_ok
        print(f"[{host:6s}] own {o!r}{c!r} sp_open={o_sp} sp_close={c_sp} | inert {io!r}{ic!r}")
        for (d, po, ao, pi, ai, no, nc, rz, bl) in per_depth:
            print(f"         d={d}: own +{ao}tok(open×{no},close×{nc},realized={rz},preserved={po}) | inert +{ai}tok(preserved={pi}) | len-bal={bl}")
        print(f"         dose-axis: own_0/1/2 distinct={distinct} | add doubles 1->2 ({add1}->{add2})={doubles} | HOST_OK={host_ok}\n")
    print(f"[S0] ALL-HOSTS OK={all_ok}  (a host failing anti-merge/doubles has NO dose axis -> route it to Design B, not TPL-04)")

if __name__ == "__main__":
    main()
