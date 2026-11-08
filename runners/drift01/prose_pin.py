"""HUNT-DRIFT-01 Amendment 4 (569919b6…) O1: pin the prose source. Strips the Gutenberg header and footer (the lines
outside the *** START / *** END markers) and nothing else. Reads prose_src/pg1228_raw.txt, writes prose_src/pg1228_body.txt.
  python -I prose_pin.py"""
import hashlib, sys
from pathlib import Path
D = Path(__file__).resolve().parent / "prose_src"
RAW_SHA = "362142cb7c6f90850477520cfe2a62fe423ae92ea8eb6d9cd8b30ddb39de60b9"   # as downloaded 2026-11-03
raw = (D / "pg1228_raw.txt").read_bytes()
assert hashlib.sha256(raw).hexdigest() == RAW_SHA, "raw text hash mismatch"
L = raw.decode("utf-8-sig").splitlines()
s = [i for i, l in enumerate(L) if l.startswith("*** START OF THE PROJECT GUTENBERG EBOOK")]
e = [i for i, l in enumerate(L) if l.startswith("*** END OF THE PROJECT GUTENBERG EBOOK")]
assert len(s) == len(e) == 1 and s[0] < e[0], (s, e)
body = "\n".join(L[s[0] + 1:e[0]]).strip() + "\n"
(D / "pg1228_body.txt").write_text(body, encoding="utf-8", newline="\n")
sys.stdout.reconfigure(encoding="utf-8")
print("lines", e[0] - s[0] - 1, "chars", len(body), "words", len(body.split()))
print("sha256", hashlib.sha256(body.encode("utf-8")).hexdigest())
print("head:", body[:300].replace("\n", " | "))
# Build note (Nate "go" 2026-11-03, logged before any data): the prose arm reads pg1228_prose.txt = the body from the
# "INTRODUCTION." heading that opens Darwin's text (the LAST of the three: two sit in the contents lists) up to, not
# including, the "INDEX." heading,
# each paragraph's lines joined by one space, paragraphs separated by one blank line.
B = body.splitlines(); intro = [i for i, l in enumerate(B) if l.strip() == "INTRODUCTION."]
assert len(intro) == 3 and next(l for l in B[intro[-1] + 1:] if l.strip()).startswith("When on board H.M.S."), intro
intro = intro[1:]
idx = [i for i, l in enumerate(B) if l.strip() == "INDEX."]                 # the back-of-book index is not prose either
assert len(idx) == 1 and idx[0] > intro[1], idx
paras, cur = [], []
for l in B[intro[1]:idx[0]]:
    if l.strip(): cur.append(l.strip())
    elif cur: paras.append(" ".join(cur)); cur = []
if cur: paras.append(" ".join(cur))
prose = "\n\n".join(paras) + "\n"
(D / "pg1228_prose.txt").write_text(prose, encoding="utf-8", newline="\n")
print("prose: paragraphs", len(paras), "words", len(prose.split()), "sha256", hashlib.sha256(prose.encode("utf-8")).hexdigest())
print("prose head:", prose[:300].replace("\n", " | "))
