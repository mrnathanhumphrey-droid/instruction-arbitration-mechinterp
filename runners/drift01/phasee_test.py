"""HUNT-DRIFT-01 A5 — FAKE test of phaseb_lambda.py PHASEB=e (Amendment 5 9b92498d…: frozen B-b transcripts × 120 A5
items × drift / filler / prose; repro gate = the first 8 A4 items vs A4's b6_q0).
  python phasee_test.py <empty work folder on D:> <a folder holding inputs/FAKE_pilot_lp.npz>
First runs B-b FAKE SMOKE + FULL, then D FAKE SMOKE + FULL on them (the A4 reference), then: clean E SMOKE + FULL: row
counts = Σ|{k ≤ n}| × items × 3, items = the first n of a5_items.json, cond indices {0, 1, 3}, prose / filler distance =
drift distance, finite, prose ≠ drift / filler, repro bitwise on every row and = D's own rows, single-pass = fresh on
the FAKE, prose counts written; re-run bit-for-bit · plants: resumetamper → 3 · prosebreak → 3 · reprobreak → 3 ·
nondeterm → 3 · overbudget → 6 · bitcheck → 3 · wrong manifest sha → 2 · tampered a5_items → 2 · no b6_q0 in the
resume folder → refused · no DRIFT_RESUME → refused · no-clobber."""
import json, os, shutil, subprocess, sys, hashlib
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D
sys.stdout.reconfigure(encoding="utf-8")
W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True); assert not any(W.iterdir()), f"{W} not empty"
SRC = Path(sys.argv[2]).resolve()
STIM = Path(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl")
fails = []
def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name, flush=True)
    if not ok: fails.append(name)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
A5 = [x["item"] for x in json.loads((HERE / "a5_items.json").read_text(encoding="utf-8"))["items"]]
A4 = [x["item"] for x in json.loads((HERE / "fresh_items.json").read_text(encoding="utf-8"))["items"]]

INP = W / "inputs"; INP.mkdir()
for f in ("panel.json", "intention_forms.json", "word_pool_drift01.txt", "fresh_items.json", "a5_items.json"): shutil.copy2(HERE / f, INP / f)
shutil.copy2(HERE / "prose_src" / "pg1228_prose.txt", INP / "pg1228_prose.txt")
shutil.copy2(STIM, INP / STIM.name); shutil.copy2(SRC / "inputs" / "FAKE_pilot_lp.npz", INP / "FAKE_pilot_lp.npz")
CLEAR = ("FAKE", "REAL", "SMOKE", "PLANT", "DRIFT_RESUME", "DRIFT_RESUME_MANIFEST_SHA", "WATCH_USD", "RATE_PER_H", "PHASEB", "DRIFT_BATCH")
def run(out, phase="e", smoke=True, inp=INP, **env):
    e = dict(os.environ); [e.pop(k, None) for k in CLEAR]
    e.update(FAKE="1", PHASEB=phase, SMOKE="1" if smoke else "0", DRIFT_INPUTS=str(inp), DRIFT_OUT=str(out), PYTHONIOENCODING="utf-8"); e.update(env)
    r = subprocess.run([sys.executable, str(HERE / "phaseb_lambda.py")], env=e, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr
RES = {}
for smoke, name, P_ in ((True, "resume_smoke", "FAKE_SMOKE_"), (False, "resume_full", "FAKE_")):
    code, txt = run(W / f"bb_{name}", phase="b", smoke=smoke)
    check(f"B-b FAKE {'SMOKE' if smoke else 'FULL'}: exit 0", code == 0)
    if code: print(txt[-2000:]); sys.exit(1)
    (INP / name).mkdir()
    for n in ("b5_transcripts.npz", "b5_transcripts.jsonl", "b5_transcripts_manifest.json", "b5_q0.npz"): shutil.copy2(W / f"bb_{name}" / f"{P_}{n}", INP / name / f"{P_}{n}")
    RES[smoke] = dict(DRIFT_RESUME=name, DRIFT_RESUME_MANIFEST_SHA=sha(INP / name / f"{P_}b5_transcripts_manifest.json"))
    code, txt = run(W / f"d_{name}", phase="d", smoke=smoke, **RES[smoke])
    check(f"D FAKE {'SMOKE' if smoke else 'FULL'} (the A4 reference): exit 0", code == 0)
    if code: print(txt[-2000:]); sys.exit(1)
    shutil.copy2(W / f"d_{name}" / f"{P_}b6_q0.npz", INP / name / f"{P_}b6_q0.npz")

def counts(out, P_, n_items, src, n_rep):
    q = np.load(out / f"{P_}a5_q0.npz")["rows"]; tr = [json.loads(l) for l in open(INP / src / f"{P_}b5_transcripts.jsonl", encoding="utf-8")]
    n = {t["tid"]: t["n"] for t in tr if "with_instruction" not in t}; ks = [k for k in D.K_Q0 if k <= max(n.values())]
    want = sum(sum(1 for k in ks if k <= n[t]) for t in n) * n_items * 3
    check(f"[{out.name}] A5 rows = Σ|{{k ≤ n}}| × {n_items} items × 3 = {want}", len(q) == want)
    check(f"[{out.name}] items = the first {n_items} of a5_items.json; cond indices = {{0, 1, 3}}",
          sorted({int(r[1]) for r in q}) == sorted(A5[:n_items]) and sorted({int(r[2]) for r in q}) == [0, 1, 3])
    d = q[q[:, 2] == 0]
    check(f"[{out.name}] filler AND prose distance = drift distance on every (transcript, item, k); finite",
          all(np.array_equal(d[:, [0, 1, 3, 6]], q[q[:, 2] == c][:, [0, 1, 3, 6]]) for c in (1, 3)) and np.isfinite(q[:, 4:6]).all())
    check(f"[{out.name}] prose readouts differ from drift and filler",
          not np.array_equal(q[q[:, 2] == 3][:, 4:6], d[:, 4:6]) and not np.array_equal(q[q[:, 2] == 3][:, 4:6], q[q[:, 2] == 1][:, 4:6]))
    rep = json.loads((out / f"{P_}a5_repro.json").read_text(encoding="utf-8")); RP = np.load(out / f"{P_}a5_repro.npz")["rows"]
    check(f"[{out.name}] repro gate: {n_rep} A4 items × 3 arms, bitwise on every row ({rep['bitwise']} / {rep['n']})",
          rep["n"] > 0 and rep["bitwise"] == rep["n"] and sorted({int(r[1]) for r in RP}) == sorted(A4[:n_rep]) and sorted({int(r[2]) for r in RP}) == [0, 1, 3])
    ref = {tuple(int(x) for x in r[:4]): tuple(r[4:6]) for r in np.load(INP / src / f"{P_}b6_q0.npz")["rows"]}
    check(f"[{out.name}] repro rows = the D run's own rows, key for key", all(ref[tuple(int(x) for x in r[:4])] == tuple(r[4:6]) for r in RP))
    G = json.loads((out / f"{P_}a5_gap_report.json").read_text(encoding="utf-8"))
    check(f"[{out.name}] single-pass + crop = a fresh pass on the FAKE (gap max {G['max']:.1e}); prose counts for {len(n)} transcripts",
          G["max"] < 1e-9 and len(json.loads((out / f"{P_}a5_prose.json").read_text(encoding="utf-8"))) == len(n))
    return q

code, txt = run(W / "e_smoke", **RES[True])
check("clean E SMOKE: exit 0, DONE, no grid fallback", code == 0 and "DONE" in txt and "fell back to the 4,096 grid 0 time(s)" in txt)
if code: print(txt[-2500:])
else:
    q1 = counts(W / "e_smoke", "FAKE_SMOKE_", 4, "resume_smoke", 2)
    code, txt = run(W / "e_smoke2", **RES[True])
    check("re-run: A5 rows bit-for-bit identical", code == 0 and np.load(W / "e_smoke2" / "FAKE_SMOKE_a5_q0.npz")["rows"].tobytes() == q1.tobytes())
code, txt = run(W / "e_full", smoke=False, **RES[False])
check("clean E FULL: exit 0, DONE, projection logged", code == 0 and "DONE" in txt and "PROJECTION" in txt)
if code: print(txt[-2500:])
else: counts(W / "e_full", "FAKE_", 120, "resume_full", 8)
for plant, want_code, want_txt, absent in (("resumetamper", 3, "RESUME FREEZE", "a5_repro.npz"), ("prosebreak", 3, "not token-matched", "a5_repro.npz"),
                                           ("reprobreak", 3, "A5 REPRO GATE FAILED", "a5_q0.npz"), ("nondeterm", 3, "REPEAT CHECK FAILED", "a5_q0.npz"),
                                           ("overbudget", 6, "PROJECTION", "a5_q0.npz"), ("bitcheck", 3, "BIT-CHECK FAILED", "a5_repro.npz")):
    out = W / f"plant_{plant}"; code, txt = run(out, PLANT=plant, **RES[True])
    ok = code == want_code and want_txt in txt and not (out / f"FAKE_SMOKE_{absent}").exists()
    check(f"PLANT {plant}: exit {want_code}, '{want_txt}', no {absent}", ok)
    if not ok: print(f"     got exit {code}:", txt[-600:])
code, txt = run(W / "bad_sha", DRIFT_RESUME="resume_smoke", DRIFT_RESUME_MANIFEST_SHA="0" * 64)
check("wrong manifest sha → 2", code == 2 and "not the pinned one" in txt)
INP2 = W / "inputs_bad_a5"; shutil.copytree(INP, INP2)
j = json.loads((INP2 / "a5_items.json").read_text(encoding="utf-8")); j["items"][0]["item"] = A4[0]
(INP2 / "a5_items.json").write_text(json.dumps(j), encoding="utf-8")
code, txt = run(W / "bad_a5", inp=INP2, **RES[True])
check("tampered a5_items.json → 2 (hash pin)", code == 2 and "a5_items.json hash mismatch" in txt)
INP3 = W / "inputs_no_ref"; shutil.copytree(INP, INP3); (INP3 / "resume_smoke" / "FAKE_SMOKE_b6_q0.npz").unlink()
code, txt = run(W / "no_ref", inp=INP3, **RES[True])
check("no A4 b6_q0 in the resume folder → refused, no a5_q0", code != 0 and not (W / "no_ref" / "FAKE_SMOKE_a5_q0.npz").exists())
code, txt = run(W / "no_resume")
check("no DRIFT_RESUME → refused", code != 0 and "DRIFT_RESUME is required" in txt)
code, txt = run(W / "e_smoke", **RES[True])
check("no-clobber", code != 0 and "not empty" in txt)
print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails))
sys.exit(1 if fails else 0)
