"""HUNT-DRIFT-01 B-b — FAKE test of phaseb_lambda.py PHASEB=b (fresh generation, B5 + with-instruction; A3.3 prefill).
  python phaseb_b_test.py <empty work folder on D:> <a passing phaseb_test.py work folder (for its inputs/FAKE_pilot_lp.npz)>
Clean SMOKE + FULL: transcript counts (FULL 96 = M1/M3 × 3 personas × 2 T × 8 B5 seeds, + 12 with-instruction), only
B5 seeds, every saved transcript (with-instruction included) re-hashes to the manifest, Q0 rows = Σ |{k ≤ n}| × items ×
3, filler distance = drift distance, finite, single-pass + descending-k readouts = a fresh pass on the FAKE (gap 0),
re-run bit-for-bit. Plants: badseed → 2 · tamper → 3 · nondeterm → 3 · overbudget → 6 · bitcheck → 3 · oom → the
sub-batch halves, DONE · prefilloom → the 4,096-grid fallback is counted in the log, DONE · DRIFT_RESUME set →
refused · a low WATCH_USD → 5 / 6 · no-clobber."""
import json, os, re, shutil, subprocess, sys
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
CLEAR = ("FAKE", "REAL", "SMOKE", "PLANT", "DRIFT_RESUME", "DRIFT_RESUME_MANIFEST_SHA", "WATCH_USD", "RATE_PER_H", "PHASEB", "DRIFT_BATCH")
def run(out, smoke=True, **env):
    e = dict(os.environ); [e.pop(k, None) for k in CLEAR]
    e.update(FAKE="1", PHASEB="b", SMOKE="1" if smoke else "0", DRIFT_INPUTS=str(INP), DRIFT_OUT=str(out), PYTHONIOENCODING="utf-8"); e.update(env)
    r = subprocess.run([sys.executable, str(HERE / "phaseb_lambda.py")], env=e, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr

def counts(out, P, n_main, n_wi, n_items):
    tr = [json.loads(l) for l in open(out / f"{P}b5_transcripts.jsonl", encoding="utf-8")]
    main = [t for t in tr if "with_instruction" not in t]; wi = [t for t in tr if "with_instruction" in t]
    check(f"[{out.name}] transcripts: {n_main} main + {n_wi} with-instruction", len(main) == n_main and len(wi) == n_wi)
    check(f"[{out.name}] main = M1 / M3 only, every seed a B5 seed", {t["mode"] for t in main} == {"M1", "M3"} and all(t["seed"] in B.B5_SEEDS for t in main))
    Z = np.load(out / f"{P}b5_transcripts.npz"); man = json.loads((out / f"{P}b5_transcripts_manifest.json").read_text(encoding="utf-8"))
    flat = {}
    for q in range(len(Z["tid"])): flat.setdefault(int(Z["tid"][q]), []).append(Z["ids"][Z["off"][q]:Z["off"][q + 1]].tolist())
    rp = {t: list(zip(v[0::2], v[1::2])) for t, v in flat.items()}
    check(f"[{out.name}] saved ids (with-instruction included: tids ≥ {B.WI_TID0}) re-hash to the manifest", D.verify_frozen(rp, man["sha"]) == []
          and sum(1 for t in rp if t >= B.WI_TID0) == n_wi and len(man["sha"]) == n_main + n_wi)
    q = np.load(out / f"{P}b5_q0.npz")["rows"]; n = {t["tid"]: t["n"] for t in tr}; ks = [k for k in D.K_Q0 if k <= max(n.values())]
    want = sum(sum(1 for k in ks if k <= n[t["tid"]]) for t in main) * n_items * 3 + sum(sum(1 for k in ks if k <= n[t["tid"]]) for t in wi) * 3
    check(f"[{out.name}] Q0 rows = Σ|{{k ≤ n}}| × {n_items} items × 3 (main) + Σ|{{k ≤ n}}| × 3 (with-instruction) = {want}", len(q) == want)
    d, f = q[q[:, 2] == 0], q[q[:, 2] == 1]
    check(f"[{out.name}] filler distance = drift distance on every (transcript, item, k); readouts finite",
          np.array_equal(d[:, [0, 1, 3, 6]], f[:, [0, 1, 3, 6]]) and np.isfinite(q[:, 4:6]).all())
    G = json.loads((out / f"{P}b5_gap_report.json").read_text(encoding="utf-8"))
    check(f"[{out.name}] single-pass + descending-k crop = a fresh pass on the FAKE (gap max {G['max']:.1e})", G["max"] < 1e-9)
    return q

code, txt = run(W / "b_smoke")
check("clean B-b SMOKE: exit 0, DONE, no grid fallback", code == 0 and "DONE" in txt and "fell back to the 4,096 grid 0 time(s)" in txt)
if code: print(txt[-2500:])
else:
    q1 = counts(W / "b_smoke", "FAKE_SMOKE_", 8, 8, 2)
    code, txt = run(W / "b_smoke2")
    check("re-run: B5 Q0 rows bit-for-bit identical", code == 0 and np.load(W / "b_smoke2" / "FAKE_SMOKE_b5_q0.npz")["rows"].tobytes() == q1.tobytes())
code, txt = run(W / "b_full", smoke=False)
check("clean B-b FULL: exit 0, DONE, both projections logged", code == 0 and "DONE" in txt and txt.count("PROJECTION") == 2)
if code: print(txt[-2500:])
else: counts(W / "b_full", "FAKE_", 96, 12, 8)
for plant, want_code, want_txt, absent in (("badseed", 2, "not a B5 seed", "b5_transcripts_manifest.json"), ("tamper", 3, "FREEZE", "b5_q0.npz"),
                                           ("nondeterm", 3, "REPEAT CHECK FAILED", "b5_q0.npz"), ("overbudget", 6, "PROJECTION", "b5_transcripts_manifest.json"),
                                           ("bitcheck", 3, "BIT-CHECK FAILED", "b5_transcripts_manifest.json")):
    out = W / f"plant_{plant}"; code, txt = run(out, PLANT=plant)
    ok = code == want_code and want_txt in txt and not (out / f"FAKE_SMOKE_{absent}").exists()
    check(f"PLANT {plant}: exit {want_code}, '{want_txt}', no {absent}", ok)
    if not ok: print(f"     got exit {code}:", txt[-600:])
code, txt = run(W / "plant_oom", PLANT="oom", DRIFT_BATCH="4")
check("PLANT CUDA OOM in generation → sub-batch halved (4 → 2), DONE", code == 0 and "OOM at sub-batch 4 → 2" in txt and "DONE" in txt)
code, txt = run(W / "plant_prefilloom", PLANT="prefilloom")
m = re.search(r"fell back to the 4,096 grid (\d+) time", txt)
check("PLANT prefill OOM → the 4,096-grid fallback is COUNTED in the log (A3.3), DONE", code == 0 and m and int(m.group(1)) > 0)
code, txt = run(W / "resume_set", DRIFT_RESUME="resume")
check("DRIFT_RESUME set → refused (B-b never resumes)", code != 0 and "DRIFT_RESUME is not used" in txt)
code, txt = run(W / "watch_low", RATE_PER_H="100000", WATCH_USD="0.01")
check("WATCH_USD = 0.01 at a huge rate → watchdog (5) or projection (6)", code in (5, 6))
code, txt = run(W / "b_smoke")
check("no-clobber", code != 0 and "not empty" in txt)
print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails))
sys.exit(1 if fails else 0)
