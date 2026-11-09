"""HUNT-DRIFT-01 Amendment 10 (cec4ef76…, locked) — four renderings of A7's demonstrations (pure; no model). EXPLORATORY.
A10.1: the same probe (C: the item's own user turn), system text, items, draws, arms and n as A7; only the demo pairs'
rendering changes:
  native  A6 / A7 rows as they are (asserted equal to a6_core.rows)
  headers the demo turns keep their chat form, role headers user / assistant → NAMES (O2: Sam / Alex)
  quoted  the n pairs move into the system block after the rule, as a quoted log (QUOTE_HEAD + "User: … / Assistant: …")
  stated  native turns; every demo user turn ends with STATED (O3)
rows() returns {arm: {n: prefix ids}} + the suffix; native / headers / stated prefixes are nested in n (one prefill,
crop), quoted ones are not (the log sits in the system block). check() asserts, per rendering, that the four arms share
lengths and suffix and differ ONLY at DONE ↔ READY swap positions (A6's counts per arm pair, × n), plus each rendering's
own form."""
import drift01_core as D
import a6_core as A6

RENDERS = ("native", "headers", "quoted", "stated")
NAMES = ("Sam", "Alex")                                   # O2: demo-turn role headers for (user, assistant)
STATED = "Actually, reply with the other word instead."  # O3
QUOTE_HEAD = "Log of an earlier conversation between a different user and a different assistant:"
NESTED = {"native": True, "headers": True, "quoted": False, "stated": True}

def _texts(C, probe, demos, arm, stated=False):
    """The NMAX demo pairs as text (user, assistant word), exactly A6.demo_pairs' choices."""
    ts, tu = C[probe]["target_sys"], C[probe]["target_usr"]; out = []
    for j in demos[:A6.NMAX]:
        assert C[j]["template_idx"] == C[probe]["template_idx"] and C[j]["target_usr"] == tu and j != probe, "demo outside the probe's cell"
        u = A6.swap(C[j]["user"], tu, ts) if A6.ASK_SYS[arm] else C[j]["user"]
        out.append((u.strip() + (" " + STATED if stated else ""), ts if A6.SAY_SYS[arm] else tu))
    return out

def _chat(enc, st, pairs, roles):
    ids = D.head(enc, st); cut = {0: len(ids)}
    for j, (u, a) in enumerate(pairs, 1):
        ids += D.turn(enc, roles[0], D.text_ids(enc, u)) + D.turn(enc, roles[1], D.text_ids(enc, a)); cut[j] = len(ids)
    return ids, cut

def quoted_system(item_sys, pairs):
    """The item's rule, a blank line, then the quoted log of the pairs."""
    return D.system_text(item_sys, "") + "\n\n" + QUOTE_HEAD + "\n" + "\n".join(f"User: {u}\nAssistant: {a}" for u, a in pairs)

def rows(enc, C, probe, demos, render):
    """({arm: {n: prefix ids}}, suffix ids) for one probe × draw under one rendering."""
    st, suf = D.system_text(C[probe]["system"], ""), D.probe_suffix(enc, C[probe]["user"]); out = {}
    for arm in A6.ARMS:
        if render == "quoted":
            P = _texts(C, probe, demos, arm)
            out[arm] = {n: D.head(enc, quoted_system(C[probe]["system"], P[:n])) for n in A6.NS}
        else:
            roles = NAMES if render == "headers" else ("user", "assistant")
            ids, cut = _chat(enc, st, _texts(C, probe, demos, arm, stated=render == "stated"), roles)
            out[arm] = {n: ids[:cut[n]] for n in A6.NS}
    return out, suf

def anchor(enc, C, probe):
    """n = 0 (shared by every rendering): A6's anchor."""
    ids, cut, suf = A6.anchor(enc, C, probe)
    return ids[:cut[0]], suf

def _sub(seq, old, new):
    out, i = [], 0
    while i < len(seq):
        if seq[i:i + len(old)] == old: out += new; i += len(old)
        else: out.append(seq[i]); i += 1
    return out

def _count(seq, sub): return sum(1 for i in range(len(seq) - len(sub) + 1) if seq[i:i + len(sub)] == sub)

def check(enc, C, probe, demos, render, R, suf):
    """Problems with one probe × draw × rendering (empty = OK)."""
    p = []; ts, tu = C[probe]["target_sys"], C[probe]["target_usr"]
    WT = {w: {t for s in (w, " " + w) for t in enc(s)} for w in (ts, tu)}
    swap_ok = lambda a, b: (a in WT[ts] and b in WT[tu]) or (b in WT[ts] and a in WT[tu])
    if suf != D.probe_suffix(enc, C[probe]["user"]): p.append(f"{render}: suffix is not A7's C probe")
    a_pre, a_suf = anchor(enc, C, probe)
    for n in A6.NS:
        L = {arm: R[arm][n] for arm in A6.ARMS}
        if len({len(x) for x in L.values()}) != 1: p.append(f"{render} n {n}: arms differ in length"); continue
        for (a, b), k in {("obey", "defer"): n, ("agree", "defy"): n, ("obey", "defy"): n, ("defer", "agree"): n,
                          ("obey", "agree"): 2 * n, ("defer", "defy"): 2 * n}.items():
            d = [q for q, (x, y) in enumerate(zip(L[a], L[b])) if x != y]
            if len(d) != k: p.append(f"{render} n {n}: {a} vs {b}: {len(d)} differing tokens, want {k}")
            elif not all(swap_ok(L[a][q], L[b][q]) for q in d): p.append(f"{render} n {n}: {a} vs {b}: a difference that is not a DONE / READY swap")
        for arm in A6.ARMS:
            x = L[arm]
            if render == "quoted":
                if x[-1:] != enc(D.EOT) or _count(x, enc(D.H("system"))) != 1 or _count(x, enc(D.H("user"))) or _count(x, enc(D.H("assistant"))):
                    p.append(f"quoted n {n} {arm}: not a single system block")
            else:
                if x[:len(a_pre)] != a_pre: p.append(f"{render} n {n} {arm}: system block ≠ the anchor's")
            if NESTED[render] and R[arm][n] != R[arm][max(A6.NS)][:len(R[arm][n])]: p.append(f"{render} n {n} {arm}: not nested in n")
    if render == "native":
        R6 = A6.rows(enc, C, probe, demos)
        for arm in A6.ARMS:
            ids, cut, s6 = R6[arm]
            if any(R[arm][n] != ids[:cut[n]] for n in A6.NS) or s6 != suf: p.append(f"native {arm}: ≠ a6_core.rows")
    if render in ("headers", "stated"):
        N8 = rows(enc, C, probe, demos, "native")[0]
        for arm in A6.ARMS:
            x, y = R[arm][A6.NMAX], N8[arm][A6.NMAX]
            if render == "headers":
                body = _sub(_sub(y[len(a_pre):], enc(D.H("user")), enc(D.H(NAMES[0]))), enc(D.H("assistant")), enc(D.H(NAMES[1])))
                if x != a_pre + body: p.append(f"headers {arm}: ≠ native with the demo role headers renamed")
                if _count(x, enc(D.H("user"))) or _count(x, enc(D.H("assistant"))): p.append(f"headers {arm}: a user / assistant header left")
            else:
                if _count(x, D.text_ids(enc, STATED)) != A6.NMAX and _count(x, enc(" " + STATED)) != A6.NMAX: p.append(f"stated {arm}: the sentence is not in all {A6.NMAX} demo turns")
                if len(x) <= len(y): p.append(f"stated {arm}: not longer than native")
    return p
