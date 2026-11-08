"""HUNT-DRIFT-01 Amendment 7 (a66ef98b…) A7.1: the 120 fresh probes and their demonstration draws.
Probes: from the 720-item old battery minus the 12 panel items, A4's 80 and A5's 120, per template (ascending
template_idx) and per cell (DONEsys, then READYsys): 2 drawn without replacement from that cell's items in ascending
index order, one rng, seed 7101701 → a7_items.json. Demonstrations: exactly A6.1 — for each probe (ascending item index)
and draw d = 0..7, an ordered list of 8 items drawn without replacement from the OTHER 11 items of the probe's
template × counterbalance cell, one rng, seed 7101702 → a7_demos.json. Reads only the battery, the amendment and the
earlier item files (no results).
  python -I draw_a7.py"""
import hashlib, json
from collections import Counter
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
SRC = Path(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl")
SRC_SHA = "d4145f1add05ec293d210ce40fe2ad3b858cc6abc2a4b86761e6f04573e629b4"
A7_SHA = "a66ef98b7550d2d26668e36a161e30faf83e0c7d3215a73d505685a95cf5b833"
A4_SHA = "f30d16a8b0055bc2ca8958cc38a71a997799bfb1a2524c970d9156f54b91c46f"
A5I_SHA = "8b1a1e32"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC) == SRC_SHA, "old battery hash mismatch"
assert sha(HERE / "PLAN_AMENDMENT_7.md") == A7_SHA, "Amendment 7 hash mismatch"
assert sha(HERE / "fresh_items.json") == A4_SHA, "A4 fresh_items hash mismatch"
assert sha(HERE / "a5_items.json").startswith(A5I_SHA), "a5_items.json hash mismatch"
C = [json.loads(l) for l in open(SRC, encoding="utf-8")]
PANEL = {p["item"] for p in json.loads((HERE / "panel.json").read_text(encoding="utf-8"))["panel"]}
A4 = {x["item"] for x in json.loads((HERE / "fresh_items.json").read_text(encoding="utf-8"))["items"]}
A5 = {x["item"] for x in json.loads((HERE / "a5_items.json").read_text(encoding="utf-8"))["items"]}
assert len(C) == 720 and len(PANEL) == 12 and len(A4) == 80 and len(A5) == 120 and not (PANEL & A4 or PANEL & A5 or A4 & A5)
USED = PANEL | A4 | A5; pool = [i for i in range(720) if i not in USED]; assert len(pool) == 508
# ---- probes (seed 7101701)
rng = np.random.default_rng(7101701); draw = []
for t in sorted({C[i]["template_idx"] for i in range(720)}):
    for cb in ("DONEsys", "READYsys"):
        cand = sorted(i for i in pool if C[i]["template_idx"] == t and C[i]["counterbalance"] == cb)
        draw += [int(i) for i in rng.choice(cand, 2, replace=False)]
PROBES = sorted(draw)
assert len(set(PROBES)) == 120 and not set(PROBES) & USED
assert all(v == 2 for v in Counter((C[i]["template_idx"], C[i]["counterbalance"]) for i in PROBES).values())
assert all(C[i]["user"].count(C[i]["target_usr"]) == 1 for i in PROBES)   # N probe: the competing word appears once
# ---- demonstrations (seed 7101702), as draw_a6.py
ND, NMAX = 8, 8
rng = np.random.default_rng(7101702); demos = {}
for p in PROBES:
    cand = sorted(i for i in range(720) if i != p and C[i]["template_idx"] == C[p]["template_idx"] and C[i]["counterbalance"] == C[p]["counterbalance"])
    assert len(cand) == 11, (p, len(cand))
    demos[p] = [[int(i) for i in rng.choice(cand, NMAX, replace=False)] for _ in range(ND)]
for p, L in demos.items():
    for l in L:
        assert len(set(l)) == NMAX and p not in l and all(C[i]["template_idx"] == C[p]["template_idx"] and C[i]["counterbalance"] == C[p]["counterbalance"] for i in l)
        assert all(C[i]["user"].count(C[i]["target_usr"]) == 1 for i in l)
head = {"amendment": f"PLAN_AMENDMENT_7.md {A7_SHA[:8]}", "source": str(SRC), "source_sha256": SRC_SHA}
items = {"seed": 7101701, **head, "excluded_panel": sorted(PANEL), "excluded_a4": sorted(A4), "excluded_a5": sorted(A5),
         "items": [{"item": i, **{k: C[i][k] for k in ("id", "cell", "template_idx", "filler_idx")}} for i in PROBES]}
(HERE / "a7_items.json").write_text(json.dumps(items, indent=1, ensure_ascii=False), encoding="utf-8")
dem = {"seed": 7101702, **head, "draws_per_item": ND, "n_max": NMAX, "nested": True, "demos": [{"item": p, "draws": demos[p]} for p in PROBES]}
(HERE / "a7_demos.json").write_text(json.dumps(dem, indent=1, ensure_ascii=False), encoding="utf-8")
print("probes:", " ".join(C[i]["id"] for i in PROBES))
print("templates:", len({C[i]["template_idx"] for i in PROBES}), "of 30, 4 each · cells:", dict(Counter(C[i]["cell"] for i in PROBES)))
use = Counter(i for L in demos.values() for l in L for i in l)
print(f"demos: {ND} draws × {NMAX} per probe · distinct demo items {len(use)} · uses per demo item min {min(use.values())} max {max(use.values())}")
print("a7_items.json sha256", sha(HERE / "a7_items.json")); print("a7_demos.json sha256", sha(HERE / "a7_demos.json"))
