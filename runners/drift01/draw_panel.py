"""HUNT-DRIFT-01 item panel (PLAN §4): 12 old-battery contested items, 3 per cell, 12 distinct templates, every filler
twice, seed SEED_PANEL 7101002 (hunt-only namespace 7101xxx; v0.1's 20261025 collided with stage-1 SEED_DISC).
Reads only the open old battery. Writes panel.json next to this file.
  python draw_panel.py"""
import hashlib, json
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
SRC = Path(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl")
SRC_SHA = "d4145f1add05ec293d210ce40fe2ad3b858cc6abc2a4b86761e6f04573e629b4"
assert hashlib.sha256(SRC.read_bytes()).hexdigest() == SRC_SHA, "old battery hash mismatch"
C = [json.loads(l) for l in open(SRC, encoding="utf-8")]
CELLS = ["DONEsys|early", "DONEsys|late", "READYsys|early", "READYsys|late"]
rng = np.random.default_rng(7101002)
tmpl = rng.choice(30, 12, replace=False).tolist()
fill = rng.permutation([f for f in range(6) for _ in range(2)]).tolist()
idx = {(it["cell"], it["template_idx"], it["filler_idx"]): i for i, it in enumerate(C)}
panel = []
for j in range(12):
    i = idx[(CELLS[j // 3], tmpl[j], fill[j])]
    panel.append({"item": i, **{k: C[i][k] for k in ("id", "cell", "template_idx", "filler_idx", "system", "user", "target_sys", "target_usr")}})
assert len({p["template_idx"] for p in panel}) == 12 and all(sum(p["filler_idx"] == f for p in panel) == 2 for f in range(6))
out = {"seed": 7101002, "source": str(SRC), "source_sha256": SRC_SHA, "panel": panel}
(HERE / "panel.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
for p in panel: print(p["id"], p["cell"], "t", p["template_idx"], "f", p["filler_idx"], "|", p["user"])
