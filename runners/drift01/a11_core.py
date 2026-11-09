"""HUNT-DRIFT-01 Amendment 11 (9c4c627f…, locked) core: the diverse-filler arm.
A11.1: every turn's content (user j, then assistant j, …) replaced by the SAME number of token ids of natural text from
ONE book of the pinned pool, each turn from a different book than the turn before it, at a seeded offset in that book.
Draws per transcript from default_rng([SEED_DIVERSE, tid]), in turn order, per turn: the book (turn 1 uniform over the 8;
after that uniform over the 7 that are not the previous turn's book), then the offset (uniform over the book's valid
starts). The arm keeps the drift's system message, skeleton and probe (A5's prose arm, B.b6_rows, with the content source
changed). Texts: prose_src/diverse/pg<id>_text.txt, built by diverse_build.py (rule logged before any data)."""
import numpy as np
import drift01_core as D

SEED_DIVERSE = 7101304                     # new; grep 2026-11-08: 0 hits in Connection_Program / Prompt_Injection(_public)
D.check_seed(SEED_DIVERSE)
POOL = (("fiction", 1342), ("history", 731), ("essays", 2944), ("travel", 3176),
        ("science", 14474), ("letters", 3361), ("drama", 2542), ("philosophy", 34901))
FILES = tuple(f"pg{pid}_text.txt" for _, pid in POOL)
TEXT_SHA = {"pg1342_text.txt": "3c5fd6733f5c82d5a09c472b8b5d37d930e230ca7777057752ab39397ebb68bd",
            "pg731_text.txt": "887423110813d76821248d85c841fc701763a04d62fa0d5103842a138a54bf91",
            "pg2944_text.txt": "065f58d19ebe3c8d1597eee4716643f359e74b09dad08e61ab8ae5c2115cde53",
            "pg3176_text.txt": "7ddecc1805f1df1a00a0c20f228749ed710cfcc65a3ed4fea1372090d44b35eb",
            "pg14474_text.txt": "9910d745fa5e2d83ebd5830d94af3eea7e417f74ee959f1a4f3ad78453f23d49",
            "pg3361_text.txt": "0c878f9e772ddcfec4107d8633c0cc3b83ded0b382d7c92023d5c7173455549f",
            "pg2542_text.txt": "15ea6a528d0ae6da36fdd06bb7e65abc7fc980282f56ca21dcccff42421d5fb8",
            "pg34901_text.txt": "da9f49d34da17b7a7fb2151737c42b2525e6f1d51de30984a9190877b4c5792f"}
assert set(TEXT_SHA) == set(FILES)
NB = len(POOL)

def diverse_pairs(books, pairs, tid):
    """(pairs of diverse content, book index per turn in turn order u1, a1, u2, a2, …). books = token-id lists, POOL order."""
    assert len(books) == NB
    rng = np.random.default_rng([SEED_DIVERSE, int(tid)]); out, bix, prev = [], [], None
    def take(n):
        nonlocal prev
        b = int(rng.integers(0, NB)) if prev is None else [x for x in range(NB) if x != prev][int(rng.integers(0, NB - 1))]
        if n > len(books[b]): raise SystemExit(f"book {POOL[b]} ({len(books[b])} tokens) is shorter than a turn of transcript {tid} ({n})")
        o = int(rng.integers(0, len(books[b]) - n + 1)); prev = b; bix.append(b)
        return list(books[b][o:o + n])
    for u, a in pairs:
        pu = take(len(u)); pa = take(len(a)); out.append((pu, pa))
    return out, bix

def diverse_row(enc, books, item, persona, pairs, tid, ks):
    """(prefix ids, cut, suffix ids, book per turn) for the diverse arm: drift's system message + skeleton + probe."""
    km = max(ks); dp, bix = diverse_pairs(books, pairs[:km], tid)
    sys_i = D.system_text(item["system"], persona)
    ids, cut = D.context(enc, sys_i, dp, km); _, dcut = D.context(enc, sys_i, pairs, km)
    assert [(len(u), len(a)) for u, a in dp] == [(len(u), len(a)) for u, a in pairs[:km]] and cut == dcut, \
        "diverse filler is not token-matched to the drift"
    assert all(x != y for x, y in zip(bix, bix[1:])), "two consecutive turns share a book"
    return ids, cut, D.probe_suffix(enc, item["user"]), bix
