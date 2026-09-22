#!/usr/bin/env python
# TOOL-01 distance check (tokenizer ONLY, no model, no GPU): is d_role a distance/recency confound?
# The ipython header differs in token length from the user header, so the injected content could sit at a
# different distance from the generation position in the B_tool_raw vs B_user arms -- which would make d_role
# partly the ORD-01 recency effect rather than a role effect. Measures, per arm, the token distance from the
# injected imperative span to the readout (last token), across the full battery, and writes tool01_distance.csv.
import os, json, csv
import numpy as np
from transformers import AutoTokenizer
from make_tool_stimuli import TEMPLATES

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
GEN = "<|start_header_id|>assistant<|end_header_id|>\n\n"
def blk(h, b): return f"<|start_header_id|>{h}<|end_header_id|>\n\n{b}<|eot_id|>"


def main():
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_tool_contested.jsonl"), encoding="utf-8")]
    hlen = {r: len(tok(f"<|start_header_id|>{r}<|end_header_id|>\n\n", add_special_tokens=False)["input_ids"])
            for r in ("user", "ipython")}

    def measure(it):
        base3 = [{"role": "system", "content": it["system"]},
                 {"role": "user", "content": it["user_trigger"]},
                 {"role": "assistant", "content": it["assistant_stub"]}]
        prefix = tok.apply_chat_template(base3, tokenize=False, add_generation_prompt=False)
        tt = it["tool_text"]; imp = TEMPLATES[it["template_idx"]].format(T=it["target_tool"])
        r = {}
        for arm, text in [("user", prefix + blk("user", tt) + GEN),
                          ("tool_raw", prefix + blk("ipython", tt) + GEN),
                          ("tool_json", prefix + blk("ipython", json.dumps({"output": tt})) + GEN)]:
            enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
            offs = enc["offset_mapping"]; L = len(enc["input_ids"]); gen = L - 1
            cs = text.index(imp); ce = cs + len(imp)
            span = [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
            r[arm] = (L, gen - span[0], gen - span[-1])
        return r

    M = [measure(it) for it in stim]
    def col(arm, j): return np.array([m[arm][j] for m in M])
    arms = ["user", "tool_raw", "tool_json"]
    with open(os.path.join(OUT, "tool01_distance.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["arm", "header_tok_len", "mean_total_len", "mean_dist_start_to_readout", "mean_dist_end_to_readout"])
        for a in arms:
            hl = hlen["user" if a == "user" else "ipython"]
            w.writerow([a, hl, round(col(a, 0).mean(), 3), round(col(a, 1).mean(), 3), round(col(a, 2).mean(), 3)])
        de_role = col("tool_raw", 2) - col("user", 2)
        de_tj = col("tool_json", 2) - col("tool_raw", 2)
        w.writerow(["d_role_dist_end_delta(tool_raw-user)", "", "", "", f"{de_role.mean():.3f} (min {de_role.min()},max {de_role.max()})"])
        w.writerow(["d_tojson_dist_end_delta(tool_json-tool_raw)", "", "", "", f"{de_tj.mean():.3f} (min {de_tj.min()},max {de_tj.max()})"])
    print(f"n={len(M)} header_tok_len={hlen}")
    for a in arms:
        print(f"{a:<10} total={col(a,0).mean():.2f} dist_start={col(a,1).mean():.2f} dist_end={col(a,2).mean():.2f}")
    print(f"d_role dist_end delta = {(col('tool_raw',2)-col('user',2)).mean():+.3f} (min {(col('tool_raw',2)-col('user',2)).min()}, max {(col('tool_raw',2)-col('user',2)).max()})")
    print(f"d_role behavioral = +2.506 nats [+1.74,+3.29]  -> distance delta 0 => clean role effect")


if __name__ == "__main__":
    main()
