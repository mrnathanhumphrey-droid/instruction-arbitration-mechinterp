"""HUNT-DRIFT-01 Amendment 11 (9c4c627f…) O1: pin the diverse-filler book pool. 8 Project Gutenberg books, one per
genre; Nietzsche and every other Fellows persona author excluded (Nate 2026-11-08), Darwin excluded (the prose arm).
Strips the Gutenberg header and footer (the lines outside the *** START / *** END markers) and nothing else, as
prose_pin.py did for pg1228. Front matter / notes / cast lists are left for the build step.
Reads prose_src/diverse/pg<ID>_raw.txt, writes prose_src/diverse/pg<ID>_body.txt.
  python -I diverse_pin.py"""
import hashlib, re, sys
from pathlib import Path
D = Path(__file__).resolve().parent / "prose_src" / "diverse"
POOL = {  # genre: (PG id, raw sha256 as downloaded 2026-11-08 from gutenberg.org/cache/epub/<id>/pg<id>.txt)
    "fiction":    (1342,  "3f6bb9d6f78e0293b56acd4714dd68cb7d6d1d293402031ce9d5a216bcaf9d75"),  # Austen, Pride and Prejudice
    "history":    (731,   "7568212cddf0780c66d46444eefb8f46e9dfe3be9328d90452c7b006ff975ca3"),  # Gibbon, Decline and Fall, Vol. 1
    "essays":     (2944,  "5d9d28c12da8bd9aaf3043e9a2d08fbd46116efd5a3736490a393599aef6d278"),  # Emerson, Essays: First Series
    "travel":     (3176,  "0c95100895426b22f0a377bd4783f3fbd621b958b8f602c2c55192182b394fe0"),  # Twain, The Innocents Abroad
    "science":    (14474, "ee17c709443e87dd8d36e2f8d7065e54344bc5182e0dc856c08f058fbd9b013f"),  # Faraday, Chemical History of a Candle
    "letters":    (3361,  "2f9ed99eff7d288310f615b2f1210e50a7d8ccfaa339d3e5d054d3997b4df84d"),  # Chesterfield, Letters to His Son
    "drama":      (2542,  "d72a481b08ca7ace73e8ca2087b2baec29fc00e0d6e493f5e877b12116bccf4f"),  # Ibsen, A Doll's House
    "philosophy": (34901, "9ecc51191d7ba36f99b0f17b2f60ed54c3929577856f47f0616d8f198422b657"),  # Mill, On Liberty
}
RX = {w: re.compile(r"\b(" + "|".join(v) + r")\b", re.I) for w, v in   # = phaseb_lambda.py's target families (A4.1)
      {"DONE": ("done", "finished", "complete", "completed"), "READY": ("ready", "prepared", "set")}.items()}
sys.stdout.reconfigure(encoding="utf-8")
for g, (pid, rsha) in POOL.items():
    raw = (D / f"pg{pid}_raw.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == rsha, f"{g} pg{pid}: raw text hash mismatch"
    L = raw.decode("utf-8-sig").splitlines()
    s = [i for i, l in enumerate(L) if l.startswith("*** START OF THE PROJECT GUTENBERG EBOOK")]
    e = [i for i, l in enumerate(L) if l.startswith("*** END OF THE PROJECT GUTENBERG EBOOK")]
    assert len(s) == len(e) == 1 and s[0] < e[0], (g, pid, s, e)
    body = "\n".join(L[s[0] + 1:e[0]]).strip() + "\n"
    (D / f"pg{pid}_body.txt").write_text(body, encoding="utf-8", newline="\n")
    fam = {w: len(rx.findall(body)) for w, rx in RX.items()}
    print(f"{g:<10} pg{pid:<6} lines {e[0] - s[0] - 1:>6}  words {len(body.split()):>7}  DONE-fam {fam['DONE']:>4}  READY-fam {fam['READY']:>4}"
          f"  body sha256 {hashlib.sha256(body.encode('utf-8')).hexdigest()}")
