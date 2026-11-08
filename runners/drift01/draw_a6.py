"""HUNT-DRIFT-01 Amendment 6 (1e6de4f1…) A6.1: the demonstration draws. For each of the 120 A5 probe items (ascending
item index) and draw d = 0..7: an ordered list of 8 demonstration items, drawn without replacement from the OTHER 11
items of the probe's template × counterbalance cell (ascending index order), one rng, seed 7101501. The n-pair rows use
the first n of the list (nested); the same list serves all four arms. Reads only the battery, the amendment and
a5_items.json (no results). Writes a6_demos.json next to this file.
  python -I draw_a6.py"""
import hashlib, json
from collections import Counter
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
SRC = Path(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl")
SRC_SHA = "d4145f1add05ec293d210ce40fe2ad3b858cc6abc2a4b86761e6f04573e629b4"
A6_SHA = "1e6de4f19e5abe55b18c13a10c1efabd62a80848f5e47ffa01c1c213acd716b8"
A5I_SHA = "8b1a1e32"
assert hashlib.sha256(SRC.read_bytes()).hexdigest() == SRC_SHA, "old battery hash mismatch"
assert hashlib.sha256((HERE / "PLAN_AMENDMENT_6.md").read_bytes()).hexdigest() == A6_SHA, "Amendment 6 hash mismatch"
assert hashlib.sha256((HERE / "a5_items.json").read_bytes()).hexdigest().startswith(A5I_SHA), "a5_items.json hash mismatch"
C = [json.loads(l) for l in open(SRC, encoding="utf-8")]
PROBES = sorted(x["item"] for x in json.loads((HERE / "a5_items.json").read_text(encoding="utf-8"))["items"])
assert len(C) == 720 and len(PROBES) == 120
ND, NMAX = 8, 8
rng = np.random.default_rng(7101501); demos = {}
for p in PROBES:
    cand = sorted(i for i in range(720) if i != p and C[i]["template_idx"] == C[p]["template_idx"] and C[i]["counterbalance"] == C[p]["counterbalance"])
    assert len(cand) == 11, (p, len(cand))
    demos[p] = [[int(i) for i in rng.choice(cand, NMAX, replace=False)] for _ in range(ND)]
for p, L in demos.items():
    for l in L:
        assert len(set(l)) == NMAX and p not in l and all(C[i]["template_idx"] == C[p]["template_idx"] and C[i]["counterbalance"] == C[p]["counterbalance"] for i in l)
        assert all(C[i]["user"].count(C[i]["target_usr"]) == 1 for i in l)   # the word to swap appears exactly once
out = {"seed": 7101501, "amendment": f"PLAN_AMENDMENT_6.md {A6_SHA[:8]}", "source": str(SRC), "source_sha256": SRC_SHA,
       "draws_per_item": ND, "n_max": NMAX, "nested": True,
       "demos": [{"item": p, "draws": demos[p]} for p in PROBES]}
(HERE / "a6_demos.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
use = Counter(i for L in demos.values() for l in L for i in l)
print(f"probes {len(demos)} · draws {ND} × {NMAX} demos each · distinct demo items used {len(use)} · uses per demo item min {min(use.values())} max {max(use.values())}")
print("position mix of slot-1 demos:", dict(Counter(C[l[0]]["position"] for L in demos.values() for l in L)))
print("a6_demos.json sha256", hashlib.sha256((HERE / "a6_demos.json").read_bytes()).hexdigest())
