"""HUNT-DRIFT-01 Amendment 4 (569919b6…) A4.1: the 80 fresh items. Uniform draw without replacement from the 720-item
old battery minus the 12 panel items, seed 7101301; not stratified. Reads only the battery and panel.json (no results).
Writes fresh_items.json next to this file.
  python -I draw_fresh.py"""
import hashlib, json
from collections import Counter
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
SRC = Path(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl")
SRC_SHA = "d4145f1add05ec293d210ce40fe2ad3b858cc6abc2a4b86761e6f04573e629b4"
assert hashlib.sha256(SRC.read_bytes()).hexdigest() == SRC_SHA, "old battery hash mismatch"
C = [json.loads(l) for l in open(SRC, encoding="utf-8")]
PANEL = {p["item"] for p in json.loads((HERE / "panel.json").read_text(encoding="utf-8"))["panel"]}
assert len(C) == 720 and len(PANEL) == 12
pool = [i for i in range(720) if i not in PANEL]
draw = sorted(int(i) for i in np.random.default_rng(7101301).choice(pool, 80, replace=False))
assert len(set(draw)) == 80 and not set(draw) & PANEL
out = {"seed": 7101301, "amendment": "PLAN_AMENDMENT_4.md 569919b6", "source": str(SRC), "source_sha256": SRC_SHA,
       "excluded_panel": sorted(PANEL), "items": [{"item": i, **{k: C[i][k] for k in ("id", "cell", "template_idx", "filler_idx")}} for i in draw]}
(HERE / "fresh_items.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print("items:", " ".join(C[i]["id"] for i in draw))
print("templates covered:", len({C[i]["template_idx"] for i in draw}), "of 30; items per template:", sorted(Counter(C[i]["template_idx"] for i in draw).values()))
print("cells:", dict(Counter(C[i]["cell"] for i in draw)))
print("fresh_items.json sha256", hashlib.sha256((HERE / "fresh_items.json").read_bytes()).hexdigest())
