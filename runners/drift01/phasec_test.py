"""HUNT-DRIFT-01 Amendment 3 piece 2 — FAKE test of phaseb_lambda.py PHASEB=c (+ a B-a regression). EXPLORATORY.
  python phasec_test.py <empty work folder on D:> <a passing phaseb_test.py work folder (its src_* + b_* runs)>
Reuses that folder's FAKE source runs (drift01_lambda.py) and FAKE B-a outputs as the references. Checks: clean C
SMOKE + FULL (A3.1 rows = items × 19; distances matched across slots ± 2; A3.2 rows = picks × 2 × |K_Q1 ≤ n| × 7;
on the FAKE both chunkings reproduce both references bit-for-bit — the FAKE recomputes every probe in full, so this
checks keying, not kernels) · B-a SMOKE still DONE (regression) · plants: a3order (plant moved first) → exit 3 ·
nondeterm → exit 3 · chunknoise → completes, (a) 0 / N exact · resume folder without b1_panel → exit 2 ·
bitcheck → exit 3 · resumetamper → exit 3."""
import hashlib, json, os, re, shutil, subprocess, sys
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
INP = W / "inputs"; INP.mkdir()
for f in ("panel.json", "intention_forms.json", "word_pool_drift01.txt"): shutil.copy2(HERE / f, INP / f)
shutil.copy2(STIM, INP / STIM.name); shutil.copy2(SRC / "inputs" / "FAKE_pilot_lp.npz", INP / "FAKE_pilot_lp.npz")
def resume_inputs(name, src, ba, tag, with_panel=True):
    RI = W / f"inputs_{name}"; shutil.copytree(INP, RI); (RI / "resume").mkdir()
    for n in ("transcripts.npz", "transcripts.jsonl", "transcripts_manifest.json", "q1.npz", "q1_full.npz"):
        shutil.copy2(SRC / src / f"{tag}{n}", RI / "resume" / f"{tag}{n}")
    if with_panel: shutil.copy2(SRC / ba / f"{tag}b1_panel.npz", RI / "resume" / f"{tag}b1_panel.npz")
    return RI, hashlib.sha256((RI / "resume" / f"{tag}transcripts_manifest.json").read_bytes()).hexdigest()
RS, MS = resume_inputs("smoke", "src_smoke", "b_smoke", "FAKE_SMOKE_"); RF, MF = resume_inputs("full", "src_full", "b_full", "FAKE_")
RN, MN = resume_inputs("nopanel", "src_smoke", "b_smoke", "FAKE_SMOKE_", with_panel=False)
CLEAR = ("FAKE", "REAL", "SMOKE", "PLANT", "DRIFT_RESUME", "DRIFT_RESUME_MANIFEST_SHA", "WATCH_USD", "RATE_PER_H", "PHASEB")
def run(out, smoke=True, phase="c", inputs=None, ms=None, **env):
    e = dict(os.environ); [e.pop(k, None) for k in CLEAR]
    e.update(FAKE="1", PHASEB=phase, SMOKE="1" if smoke else "0", DRIFT_INPUTS=str(inputs or (RS if smoke else RF)), DRIFT_OUT=str(out),
             DRIFT_RESUME="resume", DRIFT_RESUME_MANIFEST_SHA=ms or (MS if smoke else MF), PYTHONIOENCODING="utf-8"); e.update(env)
    r = subprocess.run([sys.executable, str(HERE / "phaseb_lambda.py")], env=e, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr

def counts(out, P, src, nitems, npanel_items, ks_q1, modes_n):
    n = {t["tid"]: t["n"] for t in (json.loads(l) for l in open(SRC / src / f"{P}transcripts.jsonl", encoding="utf-8")) if "tid" in t}
    a3, ch = (np.load(out / f"{P}{x}.npz")["rows"] for x in ("a3", "a3_chunk"))
    check(f"[{out.name}] A3.1 rows = {nitems} items × 19 arms", len(a3) == nitems * 19 and len(np.unique(a3[:, 1])) == 19)
    arms = list(B.A3_ARMS); by = {(int(r[0]), arms[int(r[1])]): r[4] for r in a3}
    spread = max(max(by[(i, f"{s}_{w}_{f}")] for s in B.A3_SLOTS) - min(by[(i, f"{s}_{w}_{f}")] for s in B.A3_SLOTS)
                 for i in range(nitems) for w in B.A3_WRAPS for f in ("imp", "int"))
    check(f"[{out.name}] saved distances matched across slots ± 2 (FAKE tokenizer; max spread {spread:.0f})", spread <= 2)
    tids = sorted({int(r[0]) for r in ch}); want = sum(sum(1 for k in ks_q1 if k <= n[t]) for t in tids) * npanel_items * 7
    check(f"[{out.name}] A3.2 rows = {len(tids)} picked transcripts ({modes_n}) × {npanel_items} items × K_Q1 × 7 = {want}", len(ch) == want and len(tids) == modes_n)
    ea, eb = (ch[:, 4:6] == ch[:, 8:10]).all(1).mean(), (ch[:, 6:8] == ch[:, 10:12]).all(1).mean()
    check(f"[{out.name}] FAKE: (a) = the full run's q1 and (b) = B-a's b1_panel bit-for-bit on every row ({ea:.0%}, {eb:.0%})", ea == 1 and eb == 1)
    check(f"[{out.name}] every A3 readout finite", np.isfinite(a3[:, 2:4]).all())

code, txt = run(W / "c_smoke")
check("clean C SMOKE: exit 0, DONE, skeleton + repeat + A3.2 logged", code == 0 and "DONE" in txt and "A3 skeleton checks OK" in txt and "A3.2 chunk test" in txt)
if code: print(txt[-2500:])
else: counts(W / "c_smoke", "FAKE_SMOKE_", "src_smoke", 10, 2, tuple(k for k in D.K_Q1 if k <= 8), 8)
code, txt = run(W / "c_full", smoke=False)
check("clean C FULL: exit 0, DONE", code == 0 and "DONE" in txt)
if code: print(txt[-2500:])
else: counts(W / "c_full", "FAKE_", "src_full", 720, 2, D.K_Q1, 24)
code, txt = run(W / "a_smoke", phase="a")
check("regression: B-a SMOKE on the same runner still exit 0, DONE", code == 0 and "DONE" in txt and "B1 panel:" in txt)
for plant, want_code, want_txt, absent in (("a3order", 3, "A3 skeleton", "a3"), ("nondeterm", 3, "REPEAT CHECK FAILED", "a3"),
                                           ("bitcheck", 3, "BIT-CHECK FAILED", "a3"), ("resumetamper", 3, "RESUME FREEZE", "a3")):
    out = W / f"plant_{plant}"; code, txt = run(out, PLANT=plant)
    ok = code == want_code and want_txt in txt and not (out / f"FAKE_SMOKE_{absent}.npz").exists()
    check(f"PLANT {plant}: exit {want_code}, '{want_txt}', no {absent} output", ok)
    if not ok: print(f"     got exit {code}:", txt[-600:])
code, txt = run(W / "plant_chunknoise", PLANT="chunknoise")
m = re.search(r"\(a\) full-run chunking = the full run's q1 bit-for-bit on (\d+) / (\d+)", txt)
check("PLANT chunknoise (1e-7 on the (a) readouts): completes, and the log reports (a) 0 / N exact", code == 0 and m and m.group(1) == "0" and int(m.group(2)) > 0)
code, txt = run(W / "nopanel", inputs=RN, ms=MN)
check("resume folder without B-a's b1_panel → exit 2", code == 2 and "needs the full run's q1 + B-a's b1_panel" in txt)
print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails))
sys.exit(1 if fails else 0)
