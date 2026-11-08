"""HUNT-DRIFT-01 Amendment 7 (a66ef98b…, locked) — the no-conflict probe (pure; no model). EXPLORATORY.
A7.1: every A6 row (a6_core.rows, unchanged) is read twice off one prefix: probe C = the item's own user turn (asks for
the competing word; A6's probe) and probe N = the same user turn with the competing word swapped for the system word.
check_n() asserts that N has C's token count and differs from C at exactly one position, a competing → system word token."""
import drift01_core as D
import a6_core as A6

PROBES = ("C", "N")

def suffix_n(enc, C, probe):
    """The N probe: the item's user turn asking for the SYSTEM word, + the assistant header (readout position)."""
    it = C[probe]
    return D.probe_suffix(enc, A6.swap(it["user"], it["target_usr"], it["target_sys"]))

def check_n(enc, C, probe, suf_c, suf_n):
    """Problems with the N probe against the C probe (empty = OK)."""
    ts, tu = C[probe]["target_sys"], C[probe]["target_usr"]
    WT = {w: {t for s in (w, " " + w) for t in enc(s)} for w in (ts, tu)}
    if len(suf_c) != len(suf_n): return [f"N probe: {len(suf_n)} tokens, C has {len(suf_c)}"]
    d = [q for q, (x, y) in enumerate(zip(suf_c, suf_n)) if x != y]
    if len(d) != 1: return [f"N probe: {len(d)} differing tokens, want 1"]
    if not (suf_c[d[0]] in WT[tu] and suf_n[d[0]] in WT[ts]): return ["N probe: the difference is not a competing → system word token"]
    return []
