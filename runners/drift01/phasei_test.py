"""HUNT-DRIFT-01 A10 — FAKE test of phaseb_lambda.py PHASEB=i (Amendment 10 cec4ef76…: A7's 120 probes × 8 draws ×
obey / defer / agree / defy × n ∈ {1, 2, 4, 8} × renderings native / headers / quoted / stated, probe C, + the n = 0 anchor).
  python phasei_test.py <empty work folder on D:> <a folder holding inputs/FAKE_pilot_lp.npz>
First a FAKE G FULL run → its FAKE_a7_q0.npz = the repro-gate reference. Clean I SMOKE + FULL: row counts = probes ×
(1 + draws × 4 × 4 × 4), items = the first n of a7_items.json, arm / n / draw / render codes, the four arms' distances equal
on every (item, draw, n, render), renderings' readouts differ, anchors render −1 at distance 0, repro gate bitwise on the
FAKE, prefill = fresh on the FAKE, row check written; re-run bit-for-bit; a10_analysis end-to-end on the FULL output ·
plants: a10hdr → 3 · reprooff → 3 · nondeterm → 3 · overbudget → 6 · bitcheck → 3 · tampered a7_demos → 2 · tampered
a7_items → 2 · no A7 reference → refused · DRIFT_RESUME set → refused · no-clobber."""
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
A7I = sorted(x["item"] for x in json.loads((HERE / "a7_items.json").read_text(encoding="utf-8"))["items"])
INP = W / "inputs"; INP.mkdir()
for f in ("panel.json", "intention_forms.json", "word_pool_drift01.txt", "a7_items.json", "a7_demos.json"): shutil.copy2(HERE / f, INP / f)
shutil.copy2(STIM, INP / STIM.name); shutil.copy2(SRC / "inputs" / "FAKE_pilot_lp.npz", INP / "FAKE_pilot_lp.npz")
CLEAR = ("FAKE", "REAL", "SMOKE", "PLANT", "DRIFT_RESUME", "DRIFT_RESUME_MANIFEST_SHA", "WATCH_USD", "RATE_PER_H", "PHASEB", "DRIFT_BATCH")
def run(out, smoke=True, inp=INP, phase="i", **env):
    e = dict(os.environ); [e.pop(k, None) for k in CLEAR]
    e.update(FAKE="1", PHASEB=phase, SMOKE="1" if smoke else "0", DRIFT_INPUTS=str(inp), DRIFT_OUT=str(out), PYTHONIOENCODING="utf-8"); e.update(env)
    r = subprocess.run([sys.executable, str(HERE / "phaseb_lambda.py")], env=e, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr

code, txt = run(W / "g_ref", smoke=False, phase="g")
check("FAKE G FULL (the repro-gate reference): exit 0", code == 0)
if code: print(txt[-2500:]); sys.exit(1)
INP_NOREF = W / "inputs_noref"; shutil.copytree(INP, INP_NOREF)
shutil.copy2(W / "g_ref" / "FAKE_a7_q0.npz", INP / "FAKE_a7_q0.npz")

def counts(out, P_, n_probe, nd):
    z = np.load(out / f"{P_}a10_q0.npz"); q = z["rows"]; want = n_probe * (1 + nd * 4 * 4 * 4)
    check(f"[{out.name}] rows = {n_probe} × (1 + {nd} × 4 × 4 × 4) = {want}", len(q) == want)
    check(f"[{out.name}] columns: A6's 9 + render; renders = native, headers, quoted, stated",
          list(z["cols"]) == ["item", "draw", "arm", "n", "lpD", "lpR", "dist_tokens", "lpD_ns", "lpR_ns", "render"]
          and list(z["renders"]) == ["native", "headers", "quoted", "stated"] and q.shape[1] == 10)
    body, anc = q[q[:, 2] < 4], q[q[:, 2] == 4]
    check(f"[{out.name}] items = the first {n_probe} A7 probes; arms {{0..3}}; n {{1,2,4,8}}; draws 0..{nd - 1}; render {{0..3}}",
          sorted({int(x) for x in q[:, 0]}) == A7I[:n_probe] and sorted({int(x) for x in body[:, 2]}) == [0, 1, 2, 3]
          and sorted({int(x) for x in body[:, 3]}) == [1, 2, 4, 8] and sorted({int(x) for x in body[:, 1]}) == list(range(nd))
          and sorted({int(x) for x in body[:, 9]}) == [0, 1, 2, 3])
    check(f"[{out.name}] anchors: one per probe, draw −1, n 0, distance 0, render −1",
          len(anc) == n_probe and set(anc[:, 1]) == {-1} and set(anc[:, 3]) == {0} and set(anc[:, 6]) == {0} and set(anc[:, 9]) == {-1}
          and len({int(r[0]) for r in anc}) == n_probe)
    K = {(a, r): {(int(x[0]), int(x[1]), int(x[3])): x for x in body[(body[:, 2] == a) & (body[:, 9] == r)]} for a in range(4) for r in range(4)}
    check(f"[{out.name}] the four arms' distances equal on every (item, draw, n, render); headers = native in length; all finite",
          all(K[(0, r)][k][6] == K[(a, r)][k][6] for a in range(4) for r in range(4) for k in K[(0, 0)])
          and all(K[(0, 0)][k][6] == K[(0, 1)][k][6] for k in K[(0, 0)]) and np.isfinite(q[:, 4:9]).all())
    check(f"[{out.name}] the renderings' readouts differ (native vs headers, quoted, stated); arms differ",
          all(any(K[(0, 0)][k][4] != K[(0, r)][k][4] for k in K[(0, 0)]) for r in (1, 2, 3)) and any(K[(0, 0)][k][4] != K[(1, 0)][k][4] for k in K[(0, 0)]))
    G = json.loads((out / f"{P_}a10_gap_report.json").read_text(encoding="utf-8")); RC = json.loads((out / f"{P_}a10_rowcheck.json").read_text(encoding="utf-8"))
    RP = json.loads((out / f"{P_}a10_repro.json").read_text(encoding="utf-8"))
    check(f"[{out.name}] repro gate bitwise on the FAKE ({RP['bitwise']} / {RP['n']}); prefill = fresh (gap max {G['max']:.1e}); row check over {RC['probe_draws']} probe × draw",
          RP["bitwise"] == RP["n"] > 0 and G["max"] < 1e-9 and RC["probe_draws"] == n_probe * nd and RC["renders"] == ["native", "headers", "quoted", "stated"])
    return q

code, txt = run(W / "i_smoke")
check("clean I SMOKE: exit 0, DONE, row checks OK, repro gate PASS, no grid fallback",
      code == 0 and "DONE" in txt and "A10 row checks OK" in txt and "repro gate PASS" in txt and "fell back to the 4,096 grid 0 time(s)" in txt)
if code: print(txt[-2500:])
else:
    q1 = counts(W / "i_smoke", "FAKE_SMOKE_", 4, 2)
    code, txt = run(W / "i_smoke2")
    check("re-run: A10 rows bit-for-bit identical", code == 0 and np.load(W / "i_smoke2" / "FAKE_SMOKE_a10_q0.npz")["rows"].tobytes() == q1.tobytes())
code, txt = run(W / "i_full", smoke=False)
check("clean I FULL: exit 0, DONE, projection logged", code == 0 and "DONE" in txt and "PROJECTION" in txt)
if code: print(txt[-2500:])
else:
    q = counts(W / "i_full", "FAKE_", 120, 8)
    g = np.load(W / "g_ref" / "FAKE_a7_q0.npz")["rows"]; gc = {(int(x[0]), int(x[1]), int(x[2]), int(x[3])): x[4:6] for x in g if x[9] == 0}
    nat = q[(q[:, 9] == 0) | (q[:, 9] == -1)]
    check("native rows = G's C rows bit-for-bit on ALL 120 probes (FAKE)", len(nat) == len(gc) and all((gc[(int(x[0]), int(x[1]), int(x[2]), int(x[3]))] == x[4:6]).all() for x in nat))
    r = subprocess.run([sys.executable, "-I", "-B", "-X", "utf8", str(HERE / "a10_analysis.py"), str(W / "i_full"), "FAKE_"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    check("a10_analysis end-to-end on the FULL FAKE output: exit 0, P1 + P2 verdicts written, 30 templates, S7 line",
          r.returncode == 0 and (W / "i_full" / "FAKE_A10_ANALYSIS.md").exists() and "**P1" in r.stdout and "**P2" in r.stdout and "30 templates" in r.stdout and "S7 repro gate" in r.stdout)
    if r.returncode: print(r.stdout[-1500:], r.stderr[-1500:])
for plant, want_code, want_txt in (("a10hdr", 3, "A10 ROW CHECK FAILED"), ("reprooff", 3, "REPRO GATE FAILED"), ("nondeterm", 3, "REPEAT CHECK FAILED"),
                                   ("overbudget", 6, "PROJECTION"), ("bitcheck", 3, "BIT-CHECK FAILED")):
    out = W / f"plant_{plant}"; code, txt = run(out, PLANT=plant)
    ok = code == want_code and want_txt in txt and not (out / "FAKE_SMOKE_a10_q0.npz").exists()
    check(f"PLANT {plant}: exit {want_code}, '{want_txt}', no a10_q0", ok)
    if not ok: print(f"     got exit {code}:", txt[-600:])
for fname, mutate in (("a7_demos.json", lambda j: j["demos"][0]["draws"][0].reverse()), ("a7_items.json", lambda j: j["items"].reverse())):
    INP2 = W / f"inputs_bad_{fname.split('.')[0]}"; shutil.copytree(INP, INP2)
    j = json.loads((INP2 / fname).read_text(encoding="utf-8")); mutate(j); (INP2 / fname).write_text(json.dumps(j), encoding="utf-8")
    code, txt = run(W / f"bad_{fname.split('.')[0]}", inp=INP2)
    check(f"tampered {fname} → 2 (hash pin)", code == 2 and f"{fname} hash mismatch" in txt)
code, txt = run(W / "noref", inp=INP_NOREF)
check("no A7 reference in the inputs → refused, no a10_q0", code != 0 and not (W / "noref" / "FAKE_SMOKE_a10_q0.npz").exists())
code, txt = run(W / "with_resume", DRIFT_RESUME="resume")
check("DRIFT_RESUME set → refused", code != 0 and "DRIFT_RESUME is not used" in txt)
code, txt = run(W / "i_smoke")
check("no-clobber", code != 0 and "not empty" in txt)
print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails))
sys.exit(1 if fails else 0)
