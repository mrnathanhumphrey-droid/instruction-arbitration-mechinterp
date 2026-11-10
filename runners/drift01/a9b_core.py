"""HUNT-DRIFT-01 Amendment 9b (87eae7d9…, locked) — design constants and pure helpers (no model). EXPLORATORY.
A9b.1: A10's rows (4 renderings, probe C, + anchors), A7's probe-N rows (native, read off the same crops as C, as A7 did)
+ N anchors, and an A8 subset (1 DONEsys + 1 READYsys per template, the first of each in a8_items.json order), each read
with the residual stream after LAYERS at the readout position (fp16) + Control 1 (Llama's layer-0 input embeddings
mean-pooled over the whole row) + the readouts. Control 2 (Qwen3-Embedding-8B) runs on the A10 rows' text in its own
process (a9b_encode.py)."""

LAYERS = (8, 14, 16, 20, 26)                     # O1 (settled): A9's set + Chen's layer 16; hidden_states[l] = after decoder layer l
ENC_REPO = "Qwen/Qwen3-Embedding-8B"
ENC_REV = "1d8ad4ca9b3dd8059ad90a75d4983776a23d44af"   # pinned at build 2026-11-09 (HF API sha; lastModified 2025-07-07)
ENC_TRANSFORMERS = "4.51.3"                      # Qwen3 needs ≥ 4.51; the Llama runner stays on 4.46.0 (separate venv)
ENC_MAXLEN = 8192
FOLD_SEED = 7101901                              # A9b.2 (= A9's; never drawn with)
SRC = ("a10", "a7n", "a8")                       # row source codes 0 / 1 / 2
COLS = ("src", "item", "draw", "arm", "n", "render", "probe", "pair", "cell", "cond",
        "lpD", "lpR", "dist_tokens", "lpD_ns", "lpR_ns")
NA = -9                                          # "not applicable" code in a9b_q0 columns

def a8_subset(C, a8_order):
    """A9b.1: per template, the first DONEsys and the first READYsys item in a8_items.json order (60 for 30 templates),
    returned in a8_items.json order."""
    seen, out = set(), []
    for i in a8_order:
        k = (C[i]["template_idx"], C[i]["counterbalance"])
        if k not in seen: seen.add(k); out.append(i)
    return out

def n_rows(n_probe, nd, n_arms, ns, n_render, n_pairs, n_cells, n_a8):
    """Rows in a9b_q0, in write order: A10 (anchors + units), A7-N (anchors + units), A8 subset."""
    a10 = n_probe * (1 + nd * n_arms * ns * n_render)
    a7n = n_probe * (1 + nd * n_arms * ns)
    a8 = n_pairs * n_cells * 2 * n_a8
    return a10, a7n, a8
