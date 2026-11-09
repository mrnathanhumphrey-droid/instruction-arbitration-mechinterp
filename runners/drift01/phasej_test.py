"""HUNT-DRIFT-01 A11 — FAKE test of phaseb_lambda.py PHASEB=j (Amendment 11 9c4c627f…: frozen B-b transcripts × 120 A5
items × diverse filler; repro gate = the first 8 A5 items × drift / filler / prose vs A5's a5_q0).
  python phasej_test.py <empty work folder on D:> <a folder holding inputs/FAKE_pilot_lp.npz>
Chain: B-b FAKE SMOKE + FULL → D (A4's b6_q0) → E (A5's a5_q0, the reference) → J. Clean J SMOKE + FULL: row counts =
Σ|{k ≤ n}| × items, items = the first n of a5_items.json, cond index {4}, diverse distance = E's drift distance key for
key, finite, diverse ≠ drift / filler / prose, k = 0 diverse = E's drift bitwise, repro gate bitwise on every row and =
E's own rows, single-pass = fresh on the FAKE, a11_diverse per transcript (book per turn, never twice in a row, per-book
tokens sum to the total = the transcript's first 32 pairs), re-run bit-for-bit, a11_analysis end-to-end on FULL ·
plants: resumetamper → 3 · diversebreak → 3 · samebook → 3 · reprobreak → 3 · nondeterm → 3 · overbudget → 6 · bitcheck → 3
· wrong manifest sha → 2 · tampered book text → 2 · tampered a5_items → 2 · no a5_q0 in the resume folder → 2 · no
DRIFT_RESUME → refused · no-clobber. Regression for the other phases: phasee_test.py, phasei_test.py."""
import json, os, shutil, subprocess, sys, hashlib
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D
import a11_core as A11
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

INP = W / "inputs"; INP.mkdir()
for f in ("panel.json", "intention_forms.json", "word_pool_drift01.txt", "fresh_items.json", "a5_items.json"): shutil.copy2(HERE / f, INP / f)
shutil.copy2(HERE / "prose_src" / "pg1228_prose.txt", INP / "pg1228_prose.txt")
for f in A11.FILES: shutil.copy2(HERE / "prose_src" / "diverse" / f, INP / f)
shutil.copy2(STIM, INP / STIM.name); shutil.copy2(SRC / "inputs" / "FAKE_pilot_lp.npz", INP / "FAKE_pilot_lp.npz")
CLEAR = ("FAKE", "REAL", "SMOKE", "PLANT", "DRIFT_RESUME", "DRIFT_RESUME_MANIFEST_SHA", "WATCH_USD", "RATE_PER_H", "PHASEB", "DRIFT_BATCH")
def run(out, phase="j", smoke=True, inp=INP, **env):
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
    for ph, nm in (("d", "b6_q0.npz"), ("e", "a5_q0.npz")):
        code, txt = run(W / f"{ph}_{name}", phase=ph, smoke=smoke, **RES[smoke])
        check(f"{ph.upper()} FAKE {'SMOKE' if smoke else 'FULL'}: exit 0", code == 0)
        if code: print(txt[-2000:]); sys.exit(1)
        shutil.copy2(W / f"{ph}_{name}" / f"{P_}{nm}", INP / name / f"{P_}{nm}")

def counts(out, P_, n_items, src, n_rep):
    q = np.load(out / f"{P_}a11_q0.npz")["rows"]; tr = [json.loads(l) for l in open(INP / src / f"{P_}b5_transcripts.jsonl", encoding="utf-8")]
    n = {t["tid"]: t["n"] for t in tr if "with_instruction" not in t}; ks = [k for k in D.K_Q0 if k <= max(n.values())]
    want = sum(sum(1 for k in ks if k <= n[t]) for t in n) * n_items
    check(f"[{out.name}] A11 rows = Σ|{{k ≤ n}}| × {n_items} items = {want}", len(q) == want)
    check(f"[{out.name}] items = the first {n_items} of a5_items.json; cond index = {{4}}",
          sorted({int(r[1]) for r in q}) == sorted(A5[:n_items]) and {int(r[2]) for r in q} == {4})
    e5 = np.load(INP / src / f"{P_}a5_q0.npz")["rows"]; E = {tuple(int(x) for x in r[:4]): r for r in e5}
    dr = np.array([E[(int(r[0]), int(r[1]), 0, int(r[3]))] for r in q])
    check(f"[{out.name}] diverse distance = E's drift distance on every (transcript, item, k); finite", np.array_equal(q[:, 6], dr[:, 6]) and np.isfinite(q[:, 4:6]).all())
    k0 = q[:, 3] == 0
    check(f"[{out.name}] k = 0: diverse = E's drift bitwise ({int(k0.sum())} rows)", k0.any() and np.array_equal(q[k0, 4:6], dr[k0, 4:6]))
    other = lambda c: np.array([E[(int(r[0]), int(r[1]), c, int(r[3]))][4:6] for r in q[~k0]])
    check(f"[{out.name}] diverse readouts differ from drift, filler and prose at k > 0", all(not np.array_equal(q[~k0, 4:6], other(c)) for c in (0, 1, 3)))
    rep = json.loads((out / f"{P_}a11_repro.json").read_text(encoding="utf-8")); RP = np.load(out / f"{P_}a11_repro.npz")["rows"]
    check(f"[{out.name}] repro gate: {n_rep} A5 items × 3 arms, bitwise on every row ({rep['bitwise']} / {rep['n']})",
          rep["n"] > 0 and rep["bitwise"] == rep["n"] and sorted({int(r[1]) for r in RP}) == sorted(A5[:n_rep]) and sorted({int(r[2]) for r in RP}) == [0, 1, 3])
    check(f"[{out.name}] repro rows = the E run's own rows, key for key", all(tuple(E[tuple(int(x) for x in r[:4])][4:6]) == tuple(r[4:6]) for r in RP))
    G = json.loads((out / f"{P_}a11_gap_report.json").read_text(encoding="utf-8")); DI = json.loads((out / f"{P_}a11_diverse.json").read_text(encoding="utf-8"))
    check(f"[{out.name}] single-pass + crop = a fresh pass on the FAKE (gap max {G['max']:.1e}); a11_diverse for {len(n)} transcripts",
          G["max"] < 1e-9 and len(DI) == len(n))
    Zr = np.load(INP / src / f"{P_}b5_transcripts.npz"); L = {}
    for j in range(len(Zr["tid"])): L.setdefault(int(Zr["tid"][j]), []).append(int(Zr["off"][j + 1] - Zr["off"][j]))
    ok_b = all(all(x != y for x, y in zip(v["books"], v["books"][1:])) for v in DI.values())
    ok_n = all(sum(b["ntok"] for b in v["per_book"].values()) == v["ntok"] == sum(L[int(t)][:2 * max(ks)]) and len(v["books"]) == min(len(L[int(t)]), 2 * max(ks)) for t, v in DI.items())
    check(f"[{out.name}] a11_diverse: no book twice in a row; per-book tokens sum to the total = the drift's first {max(ks)} pairs", ok_b and ok_n)
    used = {b for v in DI.values() for b in v["books"]}
    check(f"[{out.name}] books used: {len(used)} of 8", len(used) == 8 if n_items > 4 else len(used) >= 4)
    return q

code, txt = run(W / "j_smoke", **RES[True])
check("clean J SMOKE: exit 0, DONE, no grid fallback", code == 0 and "DONE" in txt and "fell back to the 4,096 grid 0 time(s)" in txt)
if code: print(txt[-2500:])
else:
    q1 = counts(W / "j_smoke", "FAKE_SMOKE_", 4, "resume_smoke", 2)
    code, txt = run(W / "j_smoke2", **RES[True])
    check("re-run: A11 rows bit-for-bit identical", code == 0 and np.load(W / "j_smoke2" / "FAKE_SMOKE_a11_q0.npz")["rows"].tobytes() == q1.tobytes())
code, txt = run(W / "j_full", smoke=False, **RES[False])
check("clean J FULL: exit 0, DONE, projection logged", code == 0 and "DONE" in txt and "PROJECTION" in txt)
if code: print(txt[-2500:])
else:
    counts(W / "j_full", "FAKE_", 120, "resume_full", 8)
    shutil.copy2(INP / "resume_full" / "FAKE_a5_q0.npz", W / "j_full" / "FAKE_a5_q0_ref.npz")
    a5dir = W / "a5_ref"; a5dir.mkdir(); shutil.copy2(INP / "resume_full" / "FAKE_a5_q0.npz", a5dir / "FAKE_a5_q0.npz")
    r = subprocess.run([sys.executable, str(HERE / "a11_analysis.py"), str(W / "j_full"), str(a5dir), str(INP / "resume_full"), "FAKE_"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    md = (W / "j_full" / "FAKE_A11_ANALYSIS.md")
    check("a11_analysis end-to-end on the FAKE FULL: exit 0, P1 / P2 / S6 split written",
          r.returncode == 0 and md.exists() and all(s in md.read_text(encoding="utf-8") for s in ("**P1", "**P2", "split by the book", "S7")))
    if r.returncode: print(r.stdout[-1500:], r.stderr[-1500:])
for plant, want_code, want_txt, absent in (("resumetamper", 3, "RESUME FREEZE", "a11_repro.npz"), ("diversebreak", 3, "not token-matched", "a11_q0.npz"),
                                           ("samebook", 3, "share a book", "a11_q0.npz"), ("reprobreak", 3, "A11 REPRO GATE FAILED", "a11_q0.npz"),
                                           ("nondeterm", 3, "REPEAT CHECK FAILED", "a11_q0.npz"), ("overbudget", 6, "PROJECTION", "a11_q0.npz"),
                                           ("bitcheck", 3, "BIT-CHECK FAILED", "a11_repro.npz")):
    out = W / f"plant_{plant}"; code, txt = run(out, PLANT=plant, **RES[True])
    ok = code == want_code and want_txt in txt and not (out / f"FAKE_SMOKE_{absent}").exists()
    check(f"PLANT {plant}: exit {want_code}, '{want_txt}', no {absent}", ok)
    if not ok: print(f"     got exit {code}:", txt[-600:])
code, txt = run(W / "bad_sha", DRIFT_RESUME="resume_smoke", DRIFT_RESUME_MANIFEST_SHA="0" * 64)
check("wrong manifest sha → 2", code == 2 and "not the pinned one" in txt)
INP2 = W / "inputs_bad_book"; shutil.copytree(INP, INP2)
with open(INP2 / "pg2542_text.txt", "a", encoding="utf-8") as fh: fh.write("x\n")
code, txt = run(W / "bad_book", inp=INP2, **RES[True])
check("tampered book text → 2 (hash pin)", code == 2 and "pg2542_text.txt hash mismatch" in txt)
INP3 = W / "inputs_bad_a5"; shutil.copytree(INP, INP3)
j = json.loads((INP3 / "a5_items.json").read_text(encoding="utf-8")); j["items"][0]["item"] = j["items"][1]["item"]
(INP3 / "a5_items.json").write_text(json.dumps(j), encoding="utf-8")
code, txt = run(W / "bad_a5", inp=INP3, **RES[True])
check("tampered a5_items.json → 2 (hash pin)", code == 2 and "a5_items.json hash mismatch" in txt)
INP4 = W / "inputs_no_ref"; shutil.copytree(INP, INP4); (INP4 / "resume_smoke" / "FAKE_SMOKE_a5_q0.npz").unlink()
code, txt = run(W / "no_ref", inp=INP4, **RES[True])
check("no A5 a5_q0 in the resume folder → 2, no a11 outputs", code == 2 and "not in the resume folder" in txt and not (W / "no_ref" / "FAKE_SMOKE_a11_repro.npz").exists())
code, txt = run(W / "no_resume")
check("no DRIFT_RESUME → refused", code != 0 and "DRIFT_RESUME is required" in txt)
code, txt = run(W / "j_smoke", **RES[True])
check("no-clobber", code != 0 and "not empty" in txt)
print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails))
sys.exit(1 if fails else 0)
