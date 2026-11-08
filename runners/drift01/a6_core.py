"""HUNT-DRIFT-01 Amendment 6 (1e6de4f1…, locked) — demonstration rows (pure; no model). EXPLORATORY.
A6.1: probe = the item's system text (P-none) + n demonstration pairs + the item's user turn, readout at the assistant
header. Demonstration pair j = (user text of demo item j, with the requested word swapped for agree / defy; assistant
= one bare word). Four arms, token-identical but for the swapped words:
  obey  (user asks competing, assistant competing) · defer (asks competing, says system)
  agree (asks system, says system)                 · defy  (asks system, says competing)
Doses are nested: row(n) = the first n pairs of the same 8-item list. check_rows() asserts, for every probe × draw,
that the arms share length and cuts and differ ONLY at the swapped-word positions, each a DONE ↔ READY token swap."""
import drift01_core as D

ARMS = ("obey", "defer", "agree", "defy")
NS = (1, 2, 4, 8)
NMAX = max(NS)
ASK_SYS = {"obey": False, "defer": False, "agree": True, "defy": True}      # demo user asks for the SYSTEM word?
SAY_SYS = {"obey": False, "defer": True, "agree": True, "defy": False}      # demo assistant says the SYSTEM word?

def swap(text, a, b):
    """Replace the single occurrence of word a with b (the battery's user texts carry their requested word once)."""
    assert text.count(a) == 1, f"'{a}' appears {text.count(a)} times"
    return text.replace(a, b)

def demo_pairs(enc, C, probe, demos, arm):
    """The NMAX demonstration pairs (user ids, assistant ids) for one probe × draw × arm."""
    ts, tu = C[probe]["target_sys"], C[probe]["target_usr"]; out = []
    for j in demos[:NMAX]:
        assert C[j]["template_idx"] == C[probe]["template_idx"] and C[j]["target_usr"] == tu and j != probe, "demo outside the probe's cell"
        u = swap(C[j]["user"], tu, ts) if ASK_SYS[arm] else C[j]["user"]
        out.append((D.text_ids(enc, u), D.text_ids(enc, ts if SAY_SYS[arm] else tu)))
    return out

def rows(enc, C, probe, demos):
    """{arm: (prefix ids, cut, suffix ids)}: prefix through NMAX pairs; row at n = prefix[:cut[n]] + suffix."""
    st, suf = D.system_text(C[probe]["system"], ""), D.probe_suffix(enc, C[probe]["user"])
    return {arm: (*D.context(enc, st, demo_pairs(enc, C, probe, demos, arm), NMAX), suf) for arm in ARMS}

def anchor(enc, C, probe):
    """n = 0: the system block + the probe (A5's k = 0 row for a P-none transcript)."""
    ids, cut = D.context(enc, D.system_text(C[probe]["system"], ""), [], 0)
    return ids, cut, D.probe_suffix(enc, C[probe]["user"])

def check_rows(enc, C, probe, R):
    """Every arm: same length, same cuts, same suffix; pairwise differences only at word-swap positions, each a
    {system word, competing word} token pair; obey vs defer / agree vs defy differ in the NMAX assistant words, obey vs
    defy / defer vs agree in the NMAX user words. Returns a list of problems (empty = OK)."""
    p = []; WT = {}
    for w in (C[probe]["target_sys"], C[probe]["target_usr"]):
        WT[w] = {t for s in (w, " " + w) for t in enc(s)}
    swap_ok = lambda a, b: (a in WT[C[probe]["target_sys"]] and b in WT[C[probe]["target_usr"]]) or (b in WT[C[probe]["target_sys"]] and a in WT[C[probe]["target_usr"]])
    ids0, cut0, suf0 = R["obey"]
    for arm in ARMS:
        ids, cut, suf = R[arm]
        if len(ids) != len(ids0) or cut != cut0 or suf != suf0: p.append(f"{arm}: length / cuts / suffix differ from obey")
    if p: return p
    want = {("obey", "defer"): NMAX, ("agree", "defy"): NMAX, ("obey", "defy"): NMAX, ("defer", "agree"): NMAX,
            ("obey", "agree"): 2 * NMAX, ("defer", "defy"): 2 * NMAX}
    for (a, b), n in want.items():
        d = [q for q, (x, y) in enumerate(zip(R[a][0], R[b][0])) if x != y]
        if len(d) != n: p.append(f"{a} vs {b}: {len(d)} differing tokens, want {n}")
        elif not all(swap_ok(R[a][0][q], R[b][0][q]) for q in d): p.append(f"{a} vs {b}: a difference that is not a DONE / READY swap")
        elif d and d[0] < cut0[0]: p.append(f"{a} vs {b}: a difference inside the system block")
    a_ids, a_cut, a_suf = anchor(enc, C, probe)
    if ids0[:cut0[0]] != a_ids or a_suf != suf0: p.append("the arms' system block / probe differ from the n = 0 anchor")
    return p
