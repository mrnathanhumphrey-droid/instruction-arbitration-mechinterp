"""HUNT-DRIFT-01 Amendment 11 (9c4c627f…) build note, before any data: the diverse-filler TEXT of each pinned book.
Reads prose_src/diverse/pg<id>_body.txt (pinned by diverse_pin.py 02e9a98d…, hashes re-checked here), writes
prose_src/diverse/pg<id>_text.txt. The rule is pg1228's (prose_pin.py), applied per book:
  1. keep the AUTHOR'S main text only: from a fixed start line (the first chapter / lecture / letter / act) to a fixed
     end (before the back matter); front matter, editors' prefaces and introductions, contents, cast list, indexes cut;
  2. each paragraph's lines joined by one space, paragraphs separated by one blank line;
  3. editorial bracket blocks dropped: a paragraph that OPENS with "[Illustration", "[Footnote", a Gibbon note mark
     ("12a (return) ["), or (Chesterfield) any "[" — the PG editor's notes — is dropped with every following paragraph
     up to the first one that ends in "]" with the brackets net ≤ 0 (Gibbon's and Milman's notes run over several
     paragraphs; one closes early by a source typo). Emerson's footnote lines ("[1] St. Augustine…") are dropped alone.
     Authors' own bracketed asides (Twain's "[A stare from the Frenchman.]") and inline brackets (Ibsen's
     "_[stage directions]_") stay. Gibbon's inline note numbers ("poets 199 and") stay: not separable from real numbers.
  4. Chesterfield only: the 1-line paragraphs of the repeated volume title pages are dropped.
  5. inline editorial spans removed from kept paragraphs: Faraday's "[Footnote: …]", Chesterfield's "[… D.W.]".
  python -I diverse_build.py"""
import hashlib, re, sys
from pathlib import Path
D = Path(__file__).resolve().parent / "prose_src" / "diverse"
BODY = {1342: "ec5006ab5edb21cf0ee304712665ef03a8a96bc5ef2e8bb70877dca86973d79c", 731: "a770f822a73742aee217a8eb0f5dd2def677e1767d2f9887f172a8461f8e7dd2",
        2944: "5fd252f611d9a1d99958ac2bbe72a4248c9b5ab0f159270a6227ed0f0286ce21", 3176: "be5932dc121eb0276276d46d2aff71690b3f1389e72e2b1323d03fe4a6de5dcd",
        14474: "10da2aadb62c6bdba85ea21a849586d71f7af5a01e82ba2fbb8cfecfc82a8071", 3361: "77b322e3849c1990b8270740b7355ac476513a8dd62622710895a627fc1f2a4e",
        2542: "055e4f62e703f4cd4ab2e4a1e73f879bee53b82f72b6a3253f27ea854477d1cc", 34901: "7b13eba8d886fe97a8f9a596d5f5c24bf7a235946637d1317a31cababe8c55ff"}
# (start line, its occurrence among exact stripped matches, first prose words after it) · (end line exclusive or None = to the end, occurrence)
CUT = {1342:  (("It is a truth universally acknowledged, that a single man in possession", 1, "It is a truth"), ("CHISWICK PRESS:--CHARLES WHITTINGHAM AND CO.", 2)),
       731:   (("Chapter I: The Extent Of The Empire In The Age Of The", 4, "Antonines—Part I."), None),
       2944:  (("I.", 1, "HISTORY"), ("Next Volume", 2)),
       3176:  (("CHAPTER I.", 2, "For months the great pleasure excursion"), None),
       14474: (("LECTURE I.", 2, "A CANDLE: THE FLAME"), ("NOTES.", 2)),
       3361:  (("LETTER I", 1, "BATH, October 9, O. S. 1746"), ("PG EDITOR'S BOOKMARKS:", 1)),
       2542:  (("ACT I", 1, "_[SCENE.—A room furnished"), None),
       34901: (("CHAPTER I.", 2, "INTRODUCTORY."), None)}
TITLE3361 = {"LETTERS TO HIS SON", "By the EARL OF CHESTERFIELD", "on the Fine Art of becoming a", "MAN OF THE WORLD", "and a", "GENTLEMAN"}
NOTE = re.compile(r"^\d+[a-z]?\]? \(return\) \[")          # one Gibbon mark carries a stray "]" ("1491] (return) [")
def strip_inline(p, pid):
    """Inline editorial spans inside a kept paragraph: "[Footnote: … [greek: …] …]" (nesting-aware) and, Chesterfield,
    the PG editor's "[… D.W.]" / "{… D.W.}" insertions. Returns (paragraph, spans removed)."""
    n = 0
    while (i := p.find("[Footnote")) >= 0:
        d, j = 0, i
        while True:
            d += {"[": 1, "]": -1}.get(p[j], 0); j += 1
            if d == 0: break
        p = (p[:i].rstrip() + " " + p[j:].lstrip()).strip(); n += 1
    if pid == 3361:
        p, m = re.subn(r"\s*[\[{][^\[\]{}]*?D\.W\.[\]}]", "", p); n += m
    return p, n
sys.stdout.reconfigure(encoding="utf-8")
for pid, bsha in BODY.items():
    raw = (D / f"pg{pid}_body.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == bsha, f"pg{pid}: body hash mismatch"
    L = raw.decode("utf-8").splitlines(); (s_txt, s_n, s_next), end = CUT[pid]
    hits = [i for i, l in enumerate(L) if l.strip() == s_txt]; s = hits[s_n - 1]
    assert next(l for l in L[s + 1:] if l.strip()).strip().startswith(s_next) or L[s].strip().startswith(s_next), (pid, "start check")
    if end is None: e = len(L)
    else:
        eh = [i for i, l in enumerate(L) if l.strip() == end[0]]; e = eh[end[1] - 1]; assert e > s, (pid, "end before start")
    paras, cur = [], []
    for l in L[s:e]:
        if l.strip(): cur.append(l.strip())
        elif cur: paras.append(" ".join(cur)); cur = []
    if cur: paras.append(" ".join(cur))
    keep, inblk, depth, blen, drop, dropw, odd, maxb, ninl = [], False, 0, 0, 0, 0, [], 0, 0
    for p in paras:
        if not inblk and pid == 2944 and re.match(r"^\[\d+\] ", p): drop += 1; dropw += len(p.split()); continue   # Emerson's footnote lines
        if not inblk and (p.startswith(("[Illustration", "[Footnote")) or NOTE.match(p) or (pid == 3361 and p.startswith("["))):
            inblk, depth, blen = True, 0, 0
        if inblk:                          # the block closes at the first paragraph ending in "]" with brackets net ≤ 0
            depth += p.count("[") - p.count("]"); blen += 1; drop += 1; dropw += len(p.split())
            assert blen <= 40, (pid, "a bracket block runs past 40 paragraphs", p[:80])
            if p.endswith("]") and depth <= 0:
                if depth < 0: odd.append(p[:60])
                inblk, maxb = False, max(maxb, blen)
            continue
        if pid == 3361 and (p in TITLE3361 or re.fullmatch(r"\d{4}(-\d{4})?", p)): drop += 1; dropw += len(p.split()); continue
        p, m = strip_inline(p, pid); ninl += m
        keep.append(p)
    assert not inblk, (pid, "a bracket block never closed")
    if ninl: print(f"        inline editorial spans removed: {ninl}")
    if odd: print(f"        unbalanced bracket blocks (closed on ']', net < 0): {len(odd)} — first: {odd[0]!r}")
    print(f"        longest dropped block {maxb} paragraphs")
    txt = "\n\n".join(keep) + "\n"
    (D / f"pg{pid}_text.txt").write_text(txt, encoding="utf-8", newline="\n")
    print(f"pg{pid:<6} lines {s + 1}–{e}  paragraphs kept {len(keep):>5} dropped {drop:>4} ({dropw:,} words)  words {len(txt.split()):>7,}"
          f"  sha256 {hashlib.sha256(txt.encode('utf-8')).hexdigest()}")
    print(f"        head: {txt[:110]!r}\n        tail: {txt[-110:]!r}")
