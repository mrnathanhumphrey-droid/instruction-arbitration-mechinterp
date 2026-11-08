"""HUNT-DRIFT-01 A6 — FAKE test of phaseb_lambda.py PHASEB=f (Amendment 6 1e6de4f1…: 120 A5 probes × 8 demo draws ×
obey / defer / agree / defy × n ∈ {1, 2, 4, 8} + the n = 0 anchor).
  python phasef_test.py <empty work folder on D:> <a folder holding inputs/FAKE_pilot_lp.npz>
Clean F SMOKE + FULL: row counts = probes × (1 + draws × 4 × 4), items = the first n of a5_items.json, arm / n / draw
codes, the four arms' distances equal on every (item, draw, n), arms' readouts differ, anchors at distance 0,
single-pass = fresh on the FAKE, row check written; re-run bit-for-bit; a6_analysis end-to-end on the FULL output ·
plants: a6swap → 3 · nondeterm → 3 · overbudget → 6 · bitcheck → 3 · tampered a6_demos → 2 · tampered a5_items → 2 ·
DRIFT_RESUME set → refused · no-clobber."""
import json, os, shutil, subprocess, sys
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
A5 = sorted(x["item"] for x in json.loads((HERE / "a5_items.json").read_text(encoding="utf-8"))["items"])
INP = W / "inputs"; INP.mkdir()
for f in ("panel.json", "intention_forms.json", "word_pool_drift01.txt", "a5_items.json", "a6_demos.json"): shutil.copy2(HERE / f, INP / f)
shutil.copy2(STIM, INP / STIM.name); shutil.copy2(SRC / "inputs" / "FAKE_pilot_lp.npz", INP / "FAKE_pilot_lp.npz")
CLEAR = ("FAKE", "REAL", "SMOKE", "PLANT", "DRIFT_RESUME", "DRIFT_RESUME_MANIFEST_SHA", "WATCH_USD", "RATE_PER_H", "PHASEB", "DRIFT_BATCH")
def run(out, smoke=True, inp=INP, **env):
    e = dict(os.environ); [e.pop(k, None) for k in CLEAR]
    e.update(FAKE="1", PHASEB="f", SMOKE="1" if smoke else "0", DRIFT_INPUTS=str(inp), DRIFT_OUT=str(out), PYTHONIOENCODING="utf-8"); e.update(env)
    r = subprocess.run([sys.executable, str(HERE / "phaseb_lambda.py")], env=e, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr

def counts(out, P_, n_probe, nd):
    q = np.load(out / f"{P_}a6_q0.npz")["rows"]; want = n_probe * (1 + nd * 4 * 4)
    check(f"[{out.name}] rows = {n_probe} × (1 + {nd} × 4 × 4) = {want}", len(q) == want)
    body, anc = q[q[:, 2] < 4], q[q[:, 2] == 4]
    check(f"[{out.name}] items = the first {n_probe} A5 probes; arms {{0..3}} + anchor 4; n {{1,2,4,8}}; draws 0..{nd - 1}",
          sorted({int(x) for x in q[:, 0]}) == A5[:n_probe] and sorted({int(x) for x in body[:, 2]}) == [0, 1, 2, 3]
          and sorted({int(x) for x in body[:, 3]}) == [1, 2, 4, 8] and sorted({int(x) for x in body[:, 1]}) == list(range(nd)))
    check(f"[{out.name}] anchors: one per probe, draw −1, n 0, distance 0", len(anc) == n_probe and set(anc[:, 1]) == {-1} and set(anc[:, 3]) == {0} and set(anc[:, 6]) == {0})
    cols = list(np.load(out / f"{P_}a6_q0.npz")["cols"])
    check(f"[{out.name}] columns: locked 7 + reported-only lpD_ns / lpR_ns, all finite",
          cols == ["item", "draw", "arm", "n", "lpD", "lpR", "dist_tokens", "lpD_ns", "lpR_ns"] and q.shape[1] == 9 and np.isfinite(q[:, 7:9]).all())
    key = lambda a: {(int(r[0]), int(r[1]), int(r[3])): r for r in body[body[:, 2] == a]}
    K = [key(a) for a in range(4)]
    check(f"[{out.name}] the four arms' distances equal on every (item, draw, n); all finite",
          all(K[0][k][6] == K[a][k][6] for a in (1, 2, 3) for k in K[0]) and np.isfinite(q[:, 4:6]).all())
    check(f"[{out.name}] arms' readouts differ (obey vs defer, agree vs defy)",
          any(K[0][k][4] != K[1][k][4] for k in K[0]) and any(K[2][k][4] != K[3][k][4] for k in K[0]))
    G = json.loads((out / f"{P_}a6_gap_report.json").read_text(encoding="utf-8")); RC = json.loads((out / f"{P_}a6_rowcheck.json").read_text(encoding="utf-8"))
    check(f"[{out.name}] single-pass + crop = a fresh pass on the FAKE (gap max {G['max']:.1e}); row check over {RC['probe_draws']} probe × draw",
          G["max"] < 1e-9 and RC["probe_draws"] == n_probe * nd)
    return q

code, txt = run(W / "f_smoke")
check("clean F SMOKE: exit 0, DONE, row checks OK, no grid fallback", code == 0 and "DONE" in txt and "A6 row checks OK" in txt and "fell back to the 4,096 grid 0 time(s)" in txt)
if code: print(txt[-2500:])
else:
    q1 = counts(W / "f_smoke", "FAKE_SMOKE_", 4, 2)
    code, txt = run(W / "f_smoke2")
    check("re-run: A6 rows bit-for-bit identical", code == 0 and np.load(W / "f_smoke2" / "FAKE_SMOKE_a6_q0.npz")["rows"].tobytes() == q1.tobytes())
code, txt = run(W / "f_full", smoke=False)
check("clean F FULL: exit 0, DONE, projection logged", code == 0 and "DONE" in txt and "PROJECTION" in txt)
if code: print(txt[-2500:])
else:
    counts(W / "f_full", "FAKE_", 120, 8)
    r = subprocess.run([sys.executable, "-I", "-B", str(HERE / "a6_analysis.py"), str(W / "f_full"), "FAKE_"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    check("a6_analysis end-to-end on the FULL FAKE output: exit 0, P1 verdict written, 30 templates",
          r.returncode == 0 and (W / "f_full" / "FAKE_A6_ANALYSIS.md").exists() and "**P1" in r.stdout and "30 templates" in r.stdout
          and "Reported only (post-lock" in r.stdout)
    if r.returncode: print(r.stdout[-1500:], r.stderr[-1500:])
for plant, want_code, want_txt in (("a6swap", 3, "A6 ROW CHECK FAILED"), ("nondeterm", 3, "REPEAT CHECK FAILED"),
                                   ("overbudget", 6, "PROJECTION"), ("bitcheck", 3, "BIT-CHECK FAILED")):
    out = W / f"plant_{plant}"; code, txt = run(out, PLANT=plant)
    ok = code == want_code and want_txt in txt and not (out / "FAKE_SMOKE_a6_q0.npz").exists()
    check(f"PLANT {plant}: exit {want_code}, '{want_txt}', no a6_q0", ok)
    if not ok: print(f"     got exit {code}:", txt[-600:])
for fname, mutate in (("a6_demos.json", lambda j: j["demos"][0]["draws"][0].reverse()), ("a5_items.json", lambda j: j["items"].reverse())):
    INP2 = W / f"inputs_bad_{fname.split('.')[0]}"; shutil.copytree(INP, INP2)
    j = json.loads((INP2 / fname).read_text(encoding="utf-8")); mutate(j); (INP2 / fname).write_text(json.dumps(j), encoding="utf-8")
    code, txt = run(W / f"bad_{fname.split('.')[0]}", inp=INP2)
    check(f"tampered {fname} → 2 (hash pin)", code == 2 and f"{fname} hash mismatch" in txt)
code, txt = run(W / "with_resume", DRIFT_RESUME="resume")
check("DRIFT_RESUME set → refused", code != 0 and "DRIFT_RESUME is not used" in txt)
code, txt = run(W / "f_smoke")
check("no-clobber", code != 0 and "not empty" in txt)
print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails))
sys.exit(1 if fails else 0)
