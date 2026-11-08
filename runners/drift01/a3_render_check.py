"""HUNT-DRIFT-01 Amendment 3 piece 1 — A3.1 render check (tokenizer only, no model; transformers 4.46.0 @ REV).
  <venv with transformers 4.46.0>\\Scripts\\python.exe a3_render_check.py
For EVERY contested item × the 19 A3 arms (3 slots × 3 wrappers × 2 forms + all-inert): (1) phaseb_core.a3_row ids =
the tokenizer on apply_chat_template's text (no splicing: every turn is text); (2) the competing target sits only in
the planted turn, which is the LAST of the three (the all-inert row carries none); (3) per item × wrapper × form, the
target → readout distance is equal across the 3 slots within ± 2 tokens (Amendment 3 A3.1); (4) every inert turn's
content is within ± 2 tokens of its row's plant (rendered in its own slot's encoding); (5) the inert words of every
arm are one per-item stream (each inert text is a prefix of the longest one); (6) no inert turn names DONE / READY in ANY case."""
import json, re, sys
from pathlib import Path
import numpy as np
import transformers
from transformers import AutoTokenizer
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D
import phaseb_core as B
assert transformers.__version__ == "4.46.0", transformers.__version__
sys.stdout.reconfigure(encoding="utf-8")
tok = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", revision=D.REV)
enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
tmpl = lambda m: tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True)
C = [json.loads(l) for l in open(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl", encoding="utf-8")]
forms = json.loads((HERE / "intention_forms.json").read_text(encoding="utf-8"))["forms"]
pool = (HERE / "word_pool_drift01.txt").read_text(encoding="utf-8").split()
fails = []
def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name, flush=True)
    if not ok: fails.append(name)
ROLE_IDS = {s: enc(B.A3_ROLE[s]) for s in B.A3_SLOTS}
bad_ids, bad_slot, bad_last, dev, prefix_bad, ex, named = 0, 0, 0, [], 0, None, 0
dist = {}
for i, it in enumerate(C):
    T = {enc(" " + it["target_usr"])[-1], enc(it["target_usr"])[-1]}; inert_texts = []
    for arm in B.B4_ARMS[:0] + B.A3_ARMS:
        ids = B.a3_row(enc, pool, it, forms, arm, i); t = tmpl(B.a3_messages(enc, pool, it, forms, arm, i))
        if ids != enc(t): bad_ids += 1; ex = ex or (arm, i, tok.decode(ids)[-400:], t[-400:])
        sp = B.content_spans(enc, ids)[:4]                     # system + the 3 turns
        hit = [k for k, (r, lo, hi) in enumerate(sp) if T & set(ids[lo:hi])]
        turns = B.a3_turns(enc, pool, it, forms, arm, i)
        if arm == "inert": bad_slot += hit != []
        else:
            slot = arm.split("_")[0]; bad_slot += hit != [3] or sp[3][0] != ROLE_IDS[slot]
            bad_last += turns[-1][0] != slot
            n = sp[3][2] - sp[3][1]; dev += [abs((hi - lo) - n) for r, lo, hi in sp[1:3]]
            dist[(i, arm)] = B.target_distance(enc, it, ids)
        inert_texts += [t_ for s, t_ in turns if not (arm != "inert" and s == arm.split("_")[0])]
    named += sum(1 for x in inert_texts if re.search(r"(done|ready)", x, re.I))
    longest = max(inert_texts, key=len); prefix_bad += not all(longest.startswith(x) for x in inert_texts)
n_rows = len(C) * len(B.A3_ARMS)
check(f"a3_row ids = tokenizer(apply_chat_template text), {len(C)} items × {len(B.A3_ARMS)} arms = {n_rows} rows (mismatches: {bad_ids})", bad_ids == 0)
if ex: print("  first mismatch:", ex[0], "item", ex[1], "\n   mine:", repr(ex[2]), "\n   tmpl:", repr(ex[3]))
check(f"competing target only in the planted turn, in its declared role; all-inert rows carry none (wrong: {bad_slot})", bad_slot == 0)
check(f"the planted slot is the LAST of the three turns, every arm (wrong: {bad_last})", bad_last == 0)
dd = [max(dist[(i, f"{s}_{w}_{f}")] for s in B.A3_SLOTS) - min(dist[(i, f"{s}_{w}_{f}")] for s in B.A3_SLOTS)
      for i in range(len(C)) for w in B.A3_WRAPS for f in ("imp", "int")]
check(f"distance equal across the 3 slots within ± 2 per item × wrapper × form (max spread {max(dd)}; spread counts {dict(zip(*np.unique(dd, return_counts=True)))})", max(dd) <= 2)
for w in B.A3_WRAPS:
    print(f"     {w:6s} distance median by slot: " + ", ".join(f"{s} {np.median([dist[(i, f'{s}_{w}_imp')] for i in range(len(C))]):.0f}" for s in B.A3_SLOTS))
dv = np.array(dev)
check(f"inert turns within ± 2 tokens of the row's plant (max |Δ| {dv.max()}; share > 2: {(dv > 2).mean():.2%})", dv.max() <= 2)
check(f"inert words = one stream per item (every inert text a prefix of the longest; bad items: {prefix_bad})", prefix_bad == 0)
check(f"no inert turn names done / ready in any case (found: {named})", named == 0)
it = C[0]
for arm in ("own_W1_imp", "user_W2_imp", "tool_issued_imp"):
    print(f"\n  example {arm} (item {it['id']}), the 3 turns as rendered:")
    for s, t_ in B.a3_turns(enc, pool, it, forms, arm, 0): print(f"    [{B.A3_ROLE[s]}] {B.tool_content(t_) if s == 'tool' else t_}")
print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails))
sys.exit(1 if fails else 0)
