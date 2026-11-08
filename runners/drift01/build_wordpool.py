"""HUNT-DRIFT-01 piece 1 (PLAN §1): the filler / inert-padding word pool, rebuilt HERE from the installed wordfreq.
  python build_wordpool.py
wordfreq 3.1.1 top_n_list("en", 5000, wordlist="best") is written as wordlist_wordfreq_3.1.1_en_best_top5000.txt and
must hash to the pinned list's recorded sha256 (90abc0a0…). Then the alphabetic-only filter → word_pool_drift01.txt
(frequency order). No stage-1 file is read; the stage-1 exclusion list is NOT applied (stage-1 code; PLAN §1)."""
import hashlib, sys
from pathlib import Path
import wordfreq
from importlib.metadata import version
HERE = Path(__file__).resolve().parent
PIN_SHA = "90abc0a03d8993e9d0bcca3bff8eeee198db597a09f026fa6a7869fafa4e26e2"
assert version("wordfreq") == "3.1.1", f"wordfreq {version('wordfreq')} installed; the pin is 3.1.1"
words = wordfreq.top_n_list("en", 5000, wordlist="best")
raw = HERE / "wordlist_wordfreq_3.1.1_en_best_top5000.txt"
raw.write_bytes(("\n".join(words) + "\n").encode("utf-8"))      # bytes: write_text on Windows would emit CRLF
got = hashlib.sha256(raw.read_bytes()).hexdigest()
if got != PIN_SHA:
    raw.replace(raw.with_suffix(".MISMATCH.txt")); sys.exit(f"wordlist hash {got} != pinned {PIN_SHA}")
assert len(words) == 5000 and len(set(words)) == 5000 and all(w == w.lower() for w in words)
pool = [w for w in words if w.isascii() and w.isalpha()]
out = HERE / "word_pool_drift01.txt"; out.write_bytes(("\n".join(pool) + "\n").encode("utf-8"))
print(f"wordlist OK (sha {got[:16]}…); pool {len(pool)} words (dropped {5000 - len(pool)} non-alphabetic); "
      f"pool sha {hashlib.sha256(out.read_bytes()).hexdigest()}")
