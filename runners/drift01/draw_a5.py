"""HUNT-DRIFT-01 Amendment 5 (9b92498d…) A5.1: the 120 fresh items. From the 720-item old battery minus the 12 panel
items and A4's 80, per template (ascending template_idx) and per cell (DONEsys, then READYsys): 2 drawn without
replacement from that cell's items in ascending index order, one rng, seed 7101401. Reads only the battery, panel.json
and fresh_items.json (no results). Writes a5_items.json next to this file.
  python -I draw_a5.py"""
import hashlib, json
from collections import Counter
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
SRC = Path(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl")
SRC_SHA = "d4145f1add05ec293d210ce40fe2ad3b858cc6abc2a4b86761e6f04573e629b4"
A4_SHA = "f30d16a8b0055bc2ca8958cc38a71a997799bfb1a2524c970d9156f54b91c46f"
assert hashlib.sha256(SRC.read_bytes()).hexdigest() == SRC_SHA, "old battery hash mismatch"
assert hashlib.sha256((HERE / "fresh_items.json").read_bytes()).hexdigest() == A4_SHA, "A4 fresh_items hash mismatch"
C = [json.loads(l) for l in open(SRC, encoding="utf-8")]
PANEL = {p["item"] for p in json.loads((HERE / "panel.json").read_text(encoding="utf-8"))["panel"]}
A4 = {x["item"] for x in json.loads((HERE / "fresh_items.json").read_text(encoding="utf-8"))["items"]}
assert len(C) == 720 and len(PANEL) == 12 and len(A4) == 80 and not PANEL & A4
pool = [i for i in range(720) if i not in PANEL | A4]; assert len(pool) == 628
rng = np.random.default_rng(7101401); draw = []
for t in sorted({C[i]["template_idx"] for i in pool}):
    for cb in ("DONEsys", "READYsys"):
        cand = sorted(i for i in pool if C[i]["template_idx"] == t and C[i]["counterbalance"] == cb)
        draw += [int(i) for i in rng.choice(cand, 2, replace=False)]
draw = sorted(draw)
assert len(set(draw)) == 120 and not set(draw) & (PANEL | A4)
assert all(v == 2 for v in Counter((C[i]["template_idx"], C[i]["counterbalance"]) for i in draw).values())
out = {"seed": 7101401, "amendment": "PLAN_AMENDMENT_5.md 9b92498d", "source": str(SRC), "source_sha256": SRC_SHA,
       "excluded_panel": sorted(PANEL), "excluded_a4": sorted(A4),
       "items": [{"item": i, **{k: C[i][k] for k in ("id", "cell", "template_idx", "filler_idx")}} for i in draw]}
(HERE / "a5_items.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print("items:", " ".join(C[i]["id"] for i in draw))
print("templates:", len({C[i]["template_idx"] for i in draw}), "of 30, 4 each (2 DONEsys + 2 READYsys)")
print("cells:", dict(Counter(C[i]["cell"] for i in draw)))
print("a5_items.json sha256", hashlib.sha256((HERE / "a5_items.json").read_bytes()).hexdigest())
