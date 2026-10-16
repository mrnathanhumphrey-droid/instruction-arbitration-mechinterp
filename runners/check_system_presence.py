#!/usr/bin/env python
# Is each item's system instruction actually present in the rendered prompt, per model and cell?
# Imports the TOOL-02, TOOL-03 and TPL-01 runners' own render functions (nothing re-implemented). Tokenizers only, no
# model, no GPU. Needs HF_TOKEN with access to the models. See verdicts/CORRECTION_MISTRAL_SYSTEM_DROP_2026-10-16.md.
import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "runners"), str(ROOT / "data")]
from transformers import AutoTokenizer  # noqa: E402

ITEMS = [json.loads(l) for l in open(ROOT / "data" / "stimuli_tool_contested_true_false.jsonl", encoding="utf-8")]
HF = os.environ.get("HF_TOKEN")


def count(texts):
    return sum(t is not None and it["system"] in t for it, t in zip(ITEMS, texts))


def line(probe, model, cells):
    n = len(ITEMS)
    print(f"{probe:8s} {model:10s} " + " | ".join(f"{k} {v}/{n}" for k, v in cells.items()), flush=True)


def tool_runner(mod_name, key):
    os.environ["MODEL_KEY"] = key
    sys.modules.pop(mod_name, None)
    return importlib.import_module(mod_name)


for key in ("llama", "qwen", "mistral"):
    T2 = tool_runner("tool02_lambda", key)
    tok = AutoTokenizer.from_pretrained(T2.MODEL_ID, token=HF)
    nat = [T2.render_native(tok, it) for it in ITEMS]
    line("TOOL-02", key, {"user": count(T2.render_user(tok, it) for it in ITEMS), "native": count(nat),
                          "markeronly": count(T2.render_markeronly(it, t) for it, t in zip(ITEMS, nat))})
    T3 = tool_runner("tool03_lambda", key)
    tc = [T3.render_tc(tok, it) for it in ITEMS]
    line("TOOL-03", key, {"U": count(T3.render_u(tok, it) for it in ITEMS),
                          "Tnc": count(T3.render_tnc(tok, it, t) for it, t in zip(ITEMS, tc)), "Tc": count(tc)})

import tpl01_phase23 as T1  # noqa: E402
for key, mid, kind, host, is_n in T1.MODELS:
    tok = AutoTokenizer.from_pretrained(mid, token=HF)
    cells = {label: count(T1.cell_text(tok, kind, it, c) for it in ITEMS)
             for label, c in T1.cells_for(key, kind, host, is_n) + [("rawuser", "rawuser")]}
    line("TPL-01", key, cells)
