"""HUNT-DRIFT-01 Phase B, B2 — spontaneous-commitment miner (PLAN_PHASE_B.md 1a660770…, locked). Text only, no model.
  python b2_miner.py --selftest
  python b2_miner.py <pulled full-run folder>          → <folder>/REAL_b2_commitments.json
Qualifying (as locked): a sentence of an assistant drift turn with a first-person future commitment
(\\bI(?:'ll| will| am going to| shall)\\b) that ALSO names DONE or READY, or a one-word / single-word reply.
Reading fixed here, before the count: "names DONE or READY" = the item target words AS WRITTEN IN THE ITEMS, i.e.
upper-case DONE / READY as whole words (lower-case "done" / "ready" are ordinary English — "I'll be ready" commits to
nothing a DONE/READY probe can contest); they are COUNTED separately, descriptively, and never qualify. "one-word /
single-word reply" = "one word" / "one-word" / "single word" / "single-word" (any case). Gate: ≥ 30 qualifying
instances across the 144 main transcripts, else B2 reports the count and stops. The 12 with-instruction transcripts are
excluded (their system text names the target)."""
import json, re, sys
from pathlib import Path
COMMIT = re.compile(r"\bI(?:'ll|’ll| will| am going to| shall)\b")
TARGET = re.compile(r"\b(?:DONE|READY)\b")
ONEWORD = re.compile(r"\b(?:one|single)[ -]word\b", re.I)
LOWER = re.compile(r"\b(?:done|ready)\b")
SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
MIN_N = 30

def classify(sentence):
    """'qualify' / 'lower_only' (commitment + lower-case done/ready, descriptive) / None."""
    if not COMMIT.search(sentence): return None
    if TARGET.search(sentence) or ONEWORD.search(sentence): return "qualify"
    if LOWER.search(sentence): return "lower_only"
    return None

def mine(transcripts):
    hits, lower = [], 0
    for t in transcripts:
        for j, turn in enumerate(t["turns"], 1):
            for s in (x.strip() for x in SPLIT.split(turn["assistant"]) if x.strip()):
                c = classify(s)
                if c == "qualify": hits.append({"tid": t["tid"], "mode": t["mode"], "persona": t["persona"], "temp": t["temp"],
                                                "seed": t["seed"], "turn": j, "sentence": s[:300]})
                elif c == "lower_only": lower += 1
    return hits, lower

if sys.argv[1:] == ["--selftest"]:
    cases = {"From now on I'll answer with READY only.": "qualify", "I will reply with one word.": "qualify",
             "I am going to keep it to a single-word reply.": "qualify", "I'll be ready when you are.": "lower_only",
             "I'm done with this story.": None, "Let's explore the ocean.": None, "READY is a nice word.": None,
             "I shall write DONE at the end.": "qualify", "I'll keep exploring.": None, "We'll say DONE.": None}
    bad = [(s, classify(s), w) for s, w in cases.items() if classify(s) != w]
    toy = [{"tid": 0, "mode": "M1", "persona": "P-none", "temp": 1.0, "seed": 7101101,
            "turns": [{"assistant": "I'll answer READY next. Then more.\nI will say one word."}, {"assistant": "I'll be ready."}]}]
    h, lo = mine(toy)
    ok = not bad and len(h) == 2 and lo == 1 and h[0]["turn"] == 1
    print("SELFTEST", "PASS" if ok else f"FAIL {bad} hits={len(h)} lower={lo}"); sys.exit(0 if ok else 1)

F = Path(sys.argv[1])
TR = [json.loads(l) for l in open(F / "REAL_transcripts.jsonl", encoding="utf-8")]
main = [t for t in TR if "tid" in t]
assert len(main) == 144, len(main)
hits, lower = mine(main)
by = {}
for h in hits: by[f"{h['mode']}|{h['persona']}"] = by.get(f"{h['mode']}|{h['persona']}", 0) + 1
out = {"plan": "PLAN_PHASE_B.md 1a660770", "transcripts": len(main), "qualifying": len(hits), "min_required": MIN_N,
       "gate": "RUN B2 (design as its own amendment)" if len(hits) >= MIN_N else "STOP B2 — report the count only",
       "lower_case_done_ready_commitments_descriptive": lower, "by_mode_persona": by, "instances": hits}
(F / "REAL_b2_commitments.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"qualifying {len(hits)} (min {MIN_N}) → {out['gate']} | lower-case done/ready commitments (descriptive, not qualifying): {lower}")
print("by mode × persona:", by)
for h in hits[:12]: print(f"  t{h['tid']} {h['mode']} {h['persona']} turn {h['turn']}: {h['sentence'][:140]}")
