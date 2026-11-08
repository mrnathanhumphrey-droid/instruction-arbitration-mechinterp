"""HUNT-DRIFT-01 A8 — FAKE test of phaseb_lambda.py PHASEB=h (Amendment 8 6bc527cd…: the frozen B-b transcripts as
M1 / M3 pairs × the 2 × 2 turn-1 splice × drift / filler × the 120 A8 items at k = 1, + the 8-item A5 re-read).
  python phaseh_test.py <empty work folder on D:> <a folder holding inputs/FAKE_pilot_lp.npz>
First runs B-b FAKE SMOKE + FULL (the transcripts to resume from), then: clean H SMOKE + FULL: row counts = pairs × 4 ×
2 × items and transcripts × re-read items × 2, codes, filler distance = drift distance, spliced ≠ unspliced readouts,
single-pass = fresh on the FAKE, row check written; re-run bit-for-bit; a8_analysis end-to-end on the FULL output ·
plants: splicebreak → 3 · resumetamper → 3 · nondeterm → 3 · overbudget → 6 · bitcheck → 3 · wrong manifest sha → 2 ·
tampered a8_items → 2 · no DRIFT_RESUME → refused · no-clobber."""
import json, os, shutil, subprocess, sys, hashlib
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding="utf-8")
W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True); assert not any(W.iterdir()), f"{W} not empty"
SRC = Path(sys.argv[2]).resolve()
STIM = Path(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl")
fails = []
def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name, flush=True)
    if not ok: fails.append(name)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
A8 = [x["item"] for x in json.loads((HERE / "a8_items.json").read_text(encoding="utf-8"))["items"]]
A5 = [x["item"] for x in json.loads((HERE / "a5_items.json").read_text(encoding="utf-8"))["items"]]
INP = W / "inputs"; INP.mkdir()
for f in ("panel.json", "intention_forms.json", "word_pool_drift01.txt", "a5_items.json", "a8_items.json"): shutil.copy2(HERE / f, INP / f)
shutil.copy2(STIM, INP / STIM.name); shutil.copy2(SRC / "inputs" / "FAKE_pilot_lp.npz", INP / "FAKE_pilot_lp.npz")
CLEAR = ("FAKE", "REAL", "SMOKE", "PLANT", "DRIFT_RESUME", "DRIFT_RESUME_MANIFEST_SHA", "WATCH_USD", "RATE_PER_H", "PHASEB", "DRIFT_BATCH")
def run(out, phase="h", smoke=True, inp=INP, **env):
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
    for n in ("b5_transcripts.npz", "b5_transcripts.jsonl", "b5_transcripts_manifest.json"): shutil.copy2(W / f"bb_{name}" / f"{P_}{n}", INP / name / f"{P_}{n}")
    RES[smoke] = dict(DRIFT_RESUME=name, DRIFT_RESUME_MANIFEST_SHA=sha(INP / name / f"{P_}b5_transcripts_manifest.json"))

def counts(out, P_, n_items, n_rr, src):
    z = np.load(out / f"{P_}a8_q0.npz"); q = z["rows"]; rr = np.load(out / f"{P_}a8_reread.npz")["rows"]
    man = json.loads((INP / src / f"{P_}b5_transcripts_manifest.json").read_text(encoding="utf-8")); nt = len(man["cells"]); NP = nt // 2
    check(f"[{out.name}] rows = {NP} pairs × 4 cells × 2 × {n_items} items = {NP * 8 * n_items}; re-read = {nt} × {n_rr} × 2 = {nt * n_rr * 2}",
          len(q) == NP * 8 * n_items and len(rr) == nt * n_rr * 2)
    check(f"[{out.name}] codes: pairs 0..{NP - 1}, cells 0..3, conds 0/1, items = the first {n_items} A8 items; re-read items = the first {n_rr} A5 items, conds 0/1",
          sorted({int(x) for x in q[:, 0]}) == list(range(NP)) and sorted({int(x) for x in q[:, 1]}) == [0, 1, 2, 3] and sorted({int(x) for x in q[:, 2]}) == [0, 1]
          and sorted({int(x) for x in q[:, 3]}) == sorted(A8[:n_items]) and sorted({int(x) for x in rr[:, 1]}) == sorted(A5[:n_rr]) and sorted({int(x) for x in rr[:, 2]}) == [0, 1])
    check(f"[{out.name}] pair metadata: {NP} pairs, personas / temps / seeds = the manifest's M1 cells",
          len(z["pair_seed"]) == NP and [list(map(str, [p, float(t), int(s)])) for p, t, s in zip(z["pair_persona"], z["pair_temp"], z["pair_seed"])]
          == [list(map(str, [c[1], float(c[2]), int(c[3])])) for c in man["cells"][:NP]])
    key = lambda c, cc: {(int(r[0]), int(r[3])): r for r in q[(q[:, 1] == c) & (q[:, 2] == cc)]}
    K = {(c, cc): key(c, cc) for c in range(4) for cc in (0, 1)}
    check(f"[{out.name}] filler distance = drift distance in every (pair, cell, item); all finite",
          all(K[(c, 0)][k][6] == K[(c, 1)][k][6] for c in range(4) for k in K[(c, 0)]) and np.isfinite(q[:, 4:9]).all() and np.isfinite(rr[:, 3:8]).all())
    check(f"[{out.name}] spliced cells differ from unspliced (M1.M3 ≠ M1.M1, M3.M1 ≠ M3.M3 drift readouts)",
          any(K[(2, 0)][k][4] != K[(0, 0)][k][4] for k in K[(0, 0)]) and any(K[(3, 0)][k][4] != K[(1, 0)][k][4] for k in K[(0, 0)]))
    G = json.loads((out / f"{P_}a8_gap_report.json").read_text(encoding="utf-8")); RC = json.loads((out / f"{P_}a8_rowcheck.json").read_text(encoding="utf-8"))
    check(f"[{out.name}] prefill + probe = a fresh pass on the FAKE (gap max {G['max']:.1e}); row check over {RC['units']} units",
          G["max"] < 1e-9 and RC["units"] == NP * 4 * n_items)
    return q

code, txt = run(W / "h_smoke", **RES[True])
check("clean H SMOKE: exit 0, DONE, row checks OK", code == 0 and "DONE" in txt and "A8 row checks OK" in txt)
if code: print(txt[-2500:])
else:
    q1 = counts(W / "h_smoke", "FAKE_SMOKE_", 4, 2, "resume_smoke")
    code, txt = run(W / "h_smoke2", **RES[True])
    check("re-run: A8 rows bit-for-bit identical", code == 0 and np.load(W / "h_smoke2" / "FAKE_SMOKE_a8_q0.npz")["rows"].tobytes() == q1.tobytes())
code, txt = run(W / "h_full", smoke=False, **RES[False])
check("clean H FULL: exit 0, DONE, projection logged", code == 0 and "DONE" in txt and "PROJECTION" in txt)
if code: print(txt[-2500:])
else:
    counts(W / "h_full", "FAKE_", 120, 8, "resume_full")
    r = subprocess.run([sys.executable, "-I", "-B", "-X", "utf8", str(HERE / "a8_analysis.py"), str(W / "h_full"), "FAKE_"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    check("a8_analysis end-to-end on the FULL FAKE output: exit 0, P1 verdict written, 30 templates",
          r.returncode == 0 and (W / "h_full" / "FAKE_A8_ANALYSIS.md").exists() and "**P1" in r.stdout and "30 templates" in r.stdout)
    if r.returncode: print(r.stdout[-1500:], r.stderr[-1500:])
for plant, want_code, want_txt in (("splicebreak", 3, "A8 ROW CHECK FAILED"), ("resumetamper", 3, "RESUME FREEZE"), ("nondeterm", 3, "REPEAT CHECK FAILED"),
                                   ("overbudget", 6, "PROJECTION"), ("bitcheck", 3, "BIT-CHECK FAILED")):
    out = W / f"plant_{plant}"; code, txt = run(out, PLANT=plant, **RES[True])
    ok = code == want_code and want_txt in txt and not (out / "FAKE_SMOKE_a8_q0.npz").exists()
    check(f"PLANT {plant}: exit {want_code}, '{want_txt}', no a8_q0", ok)
    if not ok: print(f"     got exit {code}:", txt[-600:])
code, txt = run(W / "bad_manifest", DRIFT_RESUME="resume_smoke", DRIFT_RESUME_MANIFEST_SHA="0" * 64)
check("wrong manifest sha → 2", code == 2 and "manifest is not the pinned one" in txt)
INP2 = W / "inputs_bad_a8"; shutil.copytree(INP, INP2)
j = json.loads((INP2 / "a8_items.json").read_text(encoding="utf-8")); j["items"].reverse(); (INP2 / "a8_items.json").write_text(json.dumps(j), encoding="utf-8")
code, txt = run(W / "bad_a8", inp=INP2, **RES[True])
check("tampered a8_items.json → 2 (hash pin)", code == 2 and "a8_items.json hash mismatch" in txt)
code, txt = run(W / "no_resume")
check("no DRIFT_RESUME → refused", code != 0 and "DRIFT_RESUME is required" in txt)
code, txt = run(W / "h_smoke", **RES[True])
check("no-clobber", code != 0 and "not empty" in txt)
print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails))
sys.exit(1 if fails else 0)
