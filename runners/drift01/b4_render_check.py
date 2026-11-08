"""HUNT-DRIFT-01 Phase B piece 2 — B4 render check (tokenizer only, no model; transformers 4.46.0 @ REV).
  <venv with transformers 4.46.0>\\Scripts\\python.exe b4_render_check.py
(1) every B4 arm (2 slots × 4 forms) for EVERY contested item: the text render = apply_chat_template, with the tool
slot given as role "ipython" AND as role "tool"; (2) segment-built ids (phaseb_core.b4_row) = the tokenizer on that
text; (3) the competing target sits only in the declared X turn (the inert assistant turn, system and "Continue."
carry none); (4) per slot, |distance(quoted) − distance(issued)| ≤ 1 token, imperative and intention separately
(PLAN_PHASE_B B4: must match within each slot ± 1) — distances reported per arm either way."""
import json, sys
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
dec = lambda ids: tok.decode(ids)
tmpl = lambda m: tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True)
C = [json.loads(l) for l in open(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl", encoding="utf-8")]
forms = json.loads((HERE / "intention_forms.json").read_text(encoding="utf-8"))["forms"]
pool = (HERE / "word_pool_drift01.txt").read_text(encoding="utf-8").split()
fails = []
def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name, flush=True)
    if not ok: fails.append(name)

bad_txt, bad_tool_role, bad_ids, bad_slot, ex = 0, 0, 0, 0, None
dist = {a: [] for a in B.B4_ARMS}
U, A, IPY = enc("user"), enc("assistant"), enc("ipython")
for i, it in enumerate(C):
    for arm in B.B4_ARMS:
        ids = B.b4_row(enc, pool, it, forms, arm, i)
        a_text = dec(D.turns_of(enc, ids)[2][1])                   # the inert assistant turn, as text
        m = B.b4_messages(it, forms, arm, a_text); t = tmpl(m)
        mine = D.BOS + D.H("system") + D.PRE + it["system"].strip() + D.EOT + D.H("user" if arm.startswith("user") else "ipython") + \
            (m[1]["content"].strip() if arm.startswith("user") else B.tool_content(m[1]["content"])) + D.EOT + \
            D.H("assistant") + a_text.strip() + D.EOT + D.H("user") + D.CONTINUE + D.EOT + D.H("assistant")
        if mine != t: bad_txt += 1; ex = ex or (arm, i, mine, t)
        if arm.startswith("tool"):
            m2 = [dict(x, role="tool") if x["role"] == "ipython" else x for x in m]
            bad_tool_role += tmpl(m2) != t
        # the inert turn is token-cut filler (as in the full run's Q1 inert): spliced as ids, never re-encoded text
        a_ids = D.turns_of(enc, ids)[2][1]; pre = t[:t.index(D.H("assistant")) + len(D.H("assistant"))]
        bad_ids += ids != enc(pre) + a_ids + enc(D.EOT + D.H("user") + D.CONTINUE + D.EOT + D.H("assistant")) or not t.startswith(pre + a_text.strip() + D.EOT)
        T = {enc(" " + it["target_usr"])[-1], enc(it["target_usr"])[-1]}
        hit = [role for role, c in D.turns_of(enc, ids) if c and T & set(c)]
        bad_slot += hit != [U if arm.startswith("user") else IPY]
        dist[arm].append(B.target_distance(enc, it, ids))
check(f"text render = apply_chat_template, 720 items × 8 arms (mismatches: {bad_txt})", bad_txt == 0)
if ex: print("  first mismatch:", ex[0], "item", ex[1], "\n   mine:", repr(ex[2][-300:]), "\n   tmpl:", repr(ex[3][-300:]))
check(f"tool slot: role 'tool' renders = role 'ipython' (mismatches: {bad_tool_role})", bad_tool_role == 0)
check(f"segment-built ids = tokenizer(template text) with the inert turn's ids spliced, 5,760 rows (mismatches: {bad_ids})", bad_ids == 0)
check(f"competing target only in the declared X turn, 5,760 rows (wrong: {bad_slot})", bad_slot == 0)
print("\n  tokens from the competing-target token to the readout, per arm (all 720 items):")
for a in B.B4_ARMS: print(f"    {a:17s} median {np.median(dist[a]):.0f}, range {min(dist[a])}–{max(dist[a])}")
for s in B.B4_SLOTS:
    for f in ("imp", "int"):
        d = np.array(dist[f"{s}_quoted_{f}"]) - np.array(dist[f"{s}_issued_{f}"])
        check(f"{s} slot, {f}: |quoted − issued| distance ≤ 1 per item (diff median {np.median(d):+.0f}, range {d.min():+d} … {d.max():+d})",
              np.abs(d).max() <= 1)
# (5) piece 3: the B3 rows (persona prefix + ask; + the ON / OFF arm) = apply_chat_template, both spellings, both words
pairs = [(enc(D.CONTINUE), enc("I wonder about tides. Let's think.")), (enc(D.CONTINUE), enc("Numbers, then."))]
msgs0 = [{"role": "system", "content": D.PERSONAS["P-curious"]}, {"role": "user", "content": D.CONTINUE}, {"role": "assistant", "content": "I wonder about tides. Let's think."},
         {"role": "user", "content": D.CONTINUE}, {"role": "assistant", "content": "Numbers, then."}]
ids, cut = D.context(enc, D.PERSONAS["P-curious"], pairs, 2); pre = ids[:cut[2]]
bad3 = 0
bad3 += pre + B.b3_ask(enc) != enc(tmpl(msgs0 + [{"role": "user", "content": B.B3_ASK}]))
for wid, (w, other) in B.b3_words(enc).items():
    opp = "READY" if w == "DONE" else "DONE"
    for word_id, txt in ((wid, dec([wid])), (other, dec([other]))):
        m = msgs0 + [{"role": "user", "content": B.B3_ASK}, {"role": "assistant", "content": txt}, {"role": "user", "content": B.B3_REPLY.format(opp)}]
        # the template trims assistant content: a space-led word renders bare, so compare the TEXT with the word spliced
        t = tmpl(m); lead = t[:t.index(B.B3_ASK)] + B.B3_ASK + D.EOT + D.H("assistant")
        bad3 += pre + B.b3_arm(enc, word_id, opp) != enc(lead) + [word_id] + enc(t[len(lead) + len(txt.strip()):])
check(f"B3 ask + ON / OFF arms = apply_chat_template (word ids spliced), 2 words × 2 spellings × 2 arms (mismatches: {bad3})", bad3 == 0)
it = C[0]
for arm in ("tool_issued_imp", "tool_quoted_imp"):
    print(f"\n  example {arm} (item {it['id']}) X turn as the model sees it: {B.tool_content(B.b4_plant(it, forms, arm))}")
print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails))
sys.exit(1 if fails else 0)
