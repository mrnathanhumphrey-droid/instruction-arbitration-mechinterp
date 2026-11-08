"""HUNT-DRIFT-01 Amendment 8 (6bc527cd…) A8.1: the 120 never-probed items. From the 720-item old battery minus the 12
panel items, A4's 80, A5's 120 and A7's 120, per template (ascending template_idx) and per cell (DONEsys, then
READYsys): 2 drawn without replacement from that cell's items in ascending index order, one rng, seed 7101801 →
a8_items.json. Reads only the battery, the amendment and the earlier item files (no results).
  python -I draw_a8.py"""
import hashlib, json
from collections import Counter
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
SRC = Path(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl")
SRC_SHA = "d4145f1add05ec293d210ce40fe2ad3b858cc6abc2a4b86761e6f04573e629b4"
A8_SHA = "6bc527cdafdb8005dc963e30b6300eeb2296fcde0efd08400f098ce3320a6d47"
A4_SHA = "f30d16a8b0055bc2ca8958cc38a71a997799bfb1a2524c970d9156f54b91c46f"
A5I_SHA = "8b1a1e32"
A7I_SHA = "28fb1335d5492fc92437bfead62615ceafe6976b9a91485b57f926c92e8d4f89"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC) == SRC_SHA, "old battery hash mismatch"
assert sha(HERE / "PLAN_AMENDMENT_8.md") == A8_SHA, "Amendment 8 hash mismatch"
assert sha(HERE / "fresh_items.json") == A4_SHA, "A4 fresh_items hash mismatch"
assert sha(HERE / "a5_items.json").startswith(A5I_SHA), "a5_items.json hash mismatch"
assert sha(HERE / "a7_items.json") == A7I_SHA, "a7_items.json hash mismatch"
C = [json.loads(l) for l in open(SRC, encoding="utf-8")]
PANEL = {p["item"] for p in json.loads((HERE / "panel.json").read_text(encoding="utf-8"))["panel"]}
items = lambda f: {x["item"] for x in json.loads((HERE / f).read_text(encoding="utf-8"))["items"]}
A4, A5, A7 = items("fresh_items.json"), items("a5_items.json"), items("a7_items.json")
assert len(C) == 720 and (len(PANEL), len(A4), len(A5), len(A7)) == (12, 80, 120, 120)
USED = PANEL | A4 | A5 | A7; assert len(USED) == 332
pool = [i for i in range(720) if i not in USED]
rng = np.random.default_rng(7101801); draw = []
for t in sorted({C[i]["template_idx"] for i in range(720)}):
    for cb in ("DONEsys", "READYsys"):
        cand = sorted(i for i in pool if C[i]["template_idx"] == t and C[i]["counterbalance"] == cb)
        assert len(cand) >= 2, (t, cb, len(cand))
        draw += [int(i) for i in rng.choice(cand, 2, replace=False)]
PROBES = sorted(draw)
assert len(set(PROBES)) == 120 and not set(PROBES) & USED
assert all(v == 2 for v in Counter((C[i]["template_idx"], C[i]["counterbalance"]) for i in PROBES).values())
out = {"seed": 7101801, "amendment": f"PLAN_AMENDMENT_8.md {A8_SHA[:8]}", "source": str(SRC), "source_sha256": SRC_SHA,
       "excluded_panel": sorted(PANEL), "excluded_a4": sorted(A4), "excluded_a5": sorted(A5), "excluded_a7": sorted(A7),
       "items": [{"item": i, **{k: C[i][k] for k in ("id", "cell", "template_idx", "filler_idx")}} for i in PROBES]}
(HERE / "a8_items.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print("items:", " ".join(C[i]["id"] for i in PROBES))
print("templates:", len({C[i]["template_idx"] for i in PROBES}), "of 30, 4 each · cells:", dict(Counter(C[i]["cell"] for i in PROBES)))
print("free per template × cb before the draw: min", min(Counter((C[i]["template_idx"], C[i]["counterbalance"]) for i in pool).values()))
print("a8_items.json sha256", sha(HERE / "a8_items.json"))
