"""HUNT-DRIFT-01 B6 — FAKE test of phaseb_lambda.py PHASEB=d (Amendment 4 569919b6…: frozen B-b transcripts × 80 fresh
items × drift / filler / none / prose; S7 repro of the 8 B-b items vs B-b's b5_q0).
  python phased_test.py <empty work folder on D:> <a folder holding inputs/FAKE_pilot_lp.npz>
First runs B-b FAKE SMOKE + FULL (the resume sources), then: prose_pairs unit checks · clean D SMOKE + FULL: row
counts = Σ|{k ≤ n}| × items × 4, prose / filler distance = drift distance, finite, S7 repro bitwise on every row,
single-pass = fresh on the FAKE, prose counts written; re-run bit-for-bit · plants: resumetamper → 3 · prosebreak → 3 ·
reprobreak → 3 · nondeterm → 3 · overbudget → 6 · bitcheck → 3 · wrong manifest sha → 2 · tampered fresh_items → 2 ·
no DRIFT_RESUME → refused · no-clobber."""
import json, os, shutil, subprocess, sys, hashlib
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D
import phaseb_core as B
sys.stdout.reconfigure(encoding="utf-8")
W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True); assert not any(W.iterdir()), f"{W} not empty"
SRC = Path(sys.argv[2]).resolve()
STIM = Path(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl")
fails = []
def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name, flush=True)
    if not ok: fails.append(name)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

# ---------------------------------------------------------------- prose_pairs, pure
P = list(range(10_000, 12_000)); pairs = [([1] * 5, [2] * 9), ([3] * 4, [4] * 7)]
pp = B.prose_pairs(P, pairs, 3); flat = [x for u, a in pp for x in u + a]
check("prose_pairs: per-turn token counts = the transcript's", [(len(u), len(a)) for u, a in pp] == [(5, 9), (4, 7)])
check("prose_pairs: ONE contiguous run of the prose (user j, assistant j, …)", flat == P[flat[0] - 10_000:flat[0] - 10_000 + 25])
check("prose_pairs: deterministic per tid, different across tids", pp == B.prose_pairs(P, pairs, 3) and pp != B.prose_pairs(P, pairs, 4))
try: B.prose_pairs(P[:10], pairs, 3); check("prose_pairs: prose shorter than the transcript → refused", False)
except SystemExit: check("prose_pairs: prose shorter than the transcript → refused", True)

# ---------------------------------------------------------------- inputs + B-b FAKE resume sources
INP = W / "inputs"; INP.mkdir()
for f in ("panel.json", "intention_forms.json", "word_pool_drift01.txt", "fresh_items.json"): shutil.copy2(HERE / f, INP / f)
shutil.copy2(HERE / "prose_src" / "pg1228_prose.txt", INP / "pg1228_prose.txt")
shutil.copy2(STIM, INP / STIM.name); shutil.copy2(SRC / "inputs" / "FAKE_pilot_lp.npz", INP / "FAKE_pilot_lp.npz")
CLEAR = ("FAKE", "REAL", "SMOKE", "PLANT", "DRIFT_RESUME", "DRIFT_RESUME_MANIFEST_SHA", "WATCH_USD", "RATE_PER_H", "PHASEB", "DRIFT_BATCH")
def run(out, phase="d", smoke=True, inp=INP, **env):
    e = dict(os.environ); [e.pop(k, None) for k in CLEAR]
    e.update(FAKE="1", PHASEB=phase, SMOKE="1" if smoke else "0", DRIFT_INPUTS=str(inp), DRIFT_OUT=str(out), PYTHONIOENCODING="utf-8"); e.update(env)
    r = subprocess.run([sys.executable, str(HERE / "phaseb_lambda.py")], env=e, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr
RES = {}
for smoke, name, P_ in ((True, "resume_smoke", "FAKE_SMOKE_"), (False, "resume_full", "FAKE_")):
    code, txt = run(W / f"bb_{name}", phase="b", smoke=smoke)
    check(f"B-b FAKE {'SMOKE' if smoke else 'FULL'} (the resume source): exit 0", code == 0)
    if code: print(txt[-2000:]); sys.exit(1)
    (INP / name).mkdir()
    for n in ("b5_transcripts.npz", "b5_transcripts.jsonl", "b5_transcripts_manifest.json", "b5_q0.npz"): shutil.copy2(W / f"bb_{name}" / f"{P_}{n}", INP / name / f"{P_}{n}")
    RES[smoke] = dict(DRIFT_RESUME=name, DRIFT_RESUME_MANIFEST_SHA=sha(INP / name / f"{P_}b5_transcripts_manifest.json"))

def counts(out, P_, n_items, bb):
    q = np.load(out / f"{P_}b6_q0.npz")["rows"]; tr = [json.loads(l) for l in open(bb / f"{P_}b5_transcripts.jsonl", encoding="utf-8")]
    n = {t["tid"]: t["n"] for t in tr if "with_instruction" not in t}; ks = [k for k in D.K_Q0 if k <= max(n.values())]
    want = sum(sum(1 for k in ks if k <= n[t]) for t in n) * n_items * len(B.B6_CONDS)
    check(f"[{out.name}] B6 rows = Σ|{{k ≤ n}}| × {n_items} items × {len(B.B6_CONDS)} = {want}", len(q) == want)
    check(f"[{out.name}] items = the first {n_items} of fresh_items.json, none from the panel",
          sorted({int(r[1]) for r in q}) == sorted(x["item"] for x in json.loads((HERE / "fresh_items.json").read_text(encoding="utf-8"))["items"][:n_items]))
    d = q[q[:, 2] == 0]
    check(f"[{out.name}] filler AND prose distance = drift distance on every (transcript, item, k); finite",
          all(np.array_equal(d[:, [0, 1, 3, 6]], q[q[:, 2] == c][:, [0, 1, 3, 6]]) for c in (1, 3)) and np.isfinite(q[:, 4:6]).all())
    check(f"[{out.name}] prose readouts differ from drift and filler (the arm is not a copy)",
          not np.array_equal(q[q[:, 2] == 3][:, 4:6], d[:, 4:6]) and not np.array_equal(q[q[:, 2] == 3][:, 4:6], q[q[:, 2] == 1][:, 4:6]))
    rep = json.loads((out / f"{P_}b6_repro.json").read_text(encoding="utf-8"))
    check(f"[{out.name}] S7 repro: bitwise on every row ({rep['bitwise']} / {rep['n']})", rep["n"] > 0 and rep["bitwise"] == rep["n"])
    G = json.loads((out / f"{P_}b6_gap_report.json").read_text(encoding="utf-8"))
    check(f"[{out.name}] single-pass + crop = a fresh pass on the FAKE (gap max {G['max']:.1e}); prose counts for {len(n)} transcripts",
          G["max"] < 1e-9 and len(json.loads((out / f"{P_}b6_prose.json").read_text(encoding="utf-8"))) == len(n))
    return q

code, txt = run(W / "d_smoke", **RES[True])
check("clean D SMOKE: exit 0, DONE, no grid fallback", code == 0 and "DONE" in txt and "fell back to the 4,096 grid 0 time(s)" in txt)
if code: print(txt[-2500:])
else:
    q1 = counts(W / "d_smoke", "FAKE_SMOKE_", 4, INP / "resume_smoke")
    code, txt = run(W / "d_smoke2", **RES[True])
    check("re-run: B6 rows bit-for-bit identical", code == 0 and np.load(W / "d_smoke2" / "FAKE_SMOKE_b6_q0.npz")["rows"].tobytes() == q1.tobytes())
code, txt = run(W / "d_full", smoke=False, **RES[False])
check("clean D FULL: exit 0, DONE, projection logged", code == 0 and "DONE" in txt and "PROJECTION" in txt)
if code: print(txt[-2500:])
else: counts(W / "d_full", "FAKE_", 80, INP / "resume_full")
for plant, want_code, want_txt, absent in (("resumetamper", 3, "RESUME FREEZE", "b6_repro.npz"), ("prosebreak", 3, "not token-matched", "b6_repro.npz"),
                                           ("reprobreak", 3, "S7 REPRO FAILED", "b6_q0.npz"), ("nondeterm", 3, "REPEAT CHECK FAILED", "b6_q0.npz"),
                                           ("overbudget", 6, "PROJECTION", "b6_q0.npz"), ("bitcheck", 3, "BIT-CHECK FAILED", "b6_repro.npz")):
    out = W / f"plant_{plant}"; code, txt = run(out, PLANT=plant, **RES[True])
    ok = code == want_code and want_txt in txt and not (out / f"FAKE_SMOKE_{absent}").exists()
    check(f"PLANT {plant}: exit {want_code}, '{want_txt}', no {absent}", ok)
    if not ok: print(f"     got exit {code}:", txt[-600:])
code, txt = run(W / "bad_sha", DRIFT_RESUME="resume_smoke", DRIFT_RESUME_MANIFEST_SHA="0" * 64)
check("wrong manifest sha → 2", code == 2 and "not the pinned one" in txt)
INP2 = W / "inputs_badfresh"; shutil.copytree(INP, INP2)
j = json.loads((INP2 / "fresh_items.json").read_text(encoding="utf-8")); j["items"][0]["item"] = 144
(INP2 / "fresh_items.json").write_text(json.dumps(j), encoding="utf-8")
code, txt = run(W / "bad_fresh", inp=INP2, **RES[True])
check("tampered fresh_items.json → 2 (hash pin)", code == 2 and "fresh_items.json hash mismatch" in txt)
code, txt = run(W / "no_resume")
check("no DRIFT_RESUME → refused", code != 0 and "DRIFT_RESUME is required" in txt)
code, txt = run(W / "d_smoke", **RES[True])
check("no-clobber", code != 0 and "not empty" in txt)
print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails))
sys.exit(1 if fails else 0)
