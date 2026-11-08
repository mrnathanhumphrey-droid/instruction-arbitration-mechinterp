"""HUNT-DRIFT-01 Phase B piece 3 — the FAKE test of phaseb_lambda.py B-a (local, no torch, no model). EXPLORATORY.
  python phaseb_test.py <empty work folder on D:>
Builds FAKE frozen transcripts with the UNCHANGED full-run runner (drift01_lambda.py: FAKE reference, SMOKE, FULL),
then B-a resumes them: clean SMOKE + clean FULL (row counts from the run's own transcripts; B1 readouts = the source
run's q1 / q1_full; B3 deterministic on a re-run, both branches exercised) → every planted defect trips its own stop:
bitcheck · nondeterm · resumetamper · spanoff · wrongslot (B4) · overbudget · b3same (OFF = the sampled word) · a manifest that is not the pinned one ·
no DRIFT_RESUME · PHASEB=b · PLANT outside FAKE · no-clobber · a low WATCH_USD."""
import hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D
import phaseb_core as B
sys.stdout.reconfigure(encoding="utf-8")
W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True); assert not any(W.iterdir()), f"{W} not empty"
STIM = Path(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl")
fails = []
def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name, flush=True)
    if not ok: fails.append(name)

# ------------------------------------------------------------------ unit: the B3 sampler
lp = np.log(np.array([0.5, 0.3, 0.2, 1e-300]))
draws = np.array([B.sample_token(lp, 1.0, s) for s in range(4000)])
fr = np.bincount(draws, minlength=4) / len(draws)
check(f"sample_token: frequencies ≈ softmax(lp) at T = 1 ({fr[:3].round(3).tolist()}), never the ~0 token", np.abs(fr[:3] - [0.5, 0.3, 0.2]).max() < 0.03 and fr[3] == 0)
d7 = np.bincount([B.sample_token(lp, 0.7, s) for s in range(4000)], minlength=4) / 4000; p7 = np.exp(lp[:3] / 0.7); p7 /= p7.sum()
check(f"sample_token: T = 0.7 sharpens as softmax(lp / T) ({d7[:3].round(3).tolist()} vs {p7.round(3).tolist()})", np.abs(d7[:3] - p7).max() < 0.03)
check("sample_token: same seed → same token (deterministic)", all(B.sample_token(lp, 1.0, s) == B.sample_token(lp, 1.0, s) for s in range(50)))

# ------------------------------------------------------------------ FAKE frozen transcripts from the unchanged full-run runner
INP = W / "inputs"; INP.mkdir()
for f in ("panel.json", "intention_forms.json", "word_pool_drift01.txt"): shutil.copy2(HERE / f, INP / f)
shutil.copy2(STIM, INP / STIM.name)
CLEAR = ("FAKE", "REAL", "SMOKE", "PLANT", "FAKE_MAKE_REF", "DRIFT_RESUME", "DRIFT_RESUME_MANIFEST_SHA", "WATCH_USD", "RATE_PER_H", "PHASEB")
def run(script, out, **env):
    e = dict(os.environ); [e.pop(k, None) for k in CLEAR]
    e.update(FAKE="1", DRIFT_INPUTS=str(env.pop("INPUTS", INP)), DRIFT_OUT=str(out), PYTHONIOENCODING="utf-8"); e.update(env)
    r = subprocess.run([sys.executable, str(HERE / script)], env=e, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr
code, txt = run("drift01_lambda.py", W / "ref", SMOKE="0", FAKE_MAKE_REF="1"); shutil.copy2(W / "ref" / "FAKE_pilot_lp.npz", INP / "FAKE_pilot_lp.npz")
check("FAKE pilot reference (full-run runner)", code == 0)
for nm, sm in (("src_smoke", "1"), ("src_full", "0")):
    code, txt = run("drift01_lambda.py", W / nm, SMOKE=sm)
    check(f"source FAKE {'SMOKE' if sm == '1' else 'FULL'} run by the unchanged drift01_lambda.py: exit 0", code == 0)
    if code: print(txt[-1500:])
def resume_inputs(src, tag):
    RI = W / f"inputs_{src}"; shutil.copytree(INP, RI); (RI / "resume").mkdir()
    for n in ("transcripts.npz", "transcripts.jsonl", "transcripts_manifest.json", "q1.npz", "q1_full.npz"):
        shutil.copy2(W / src / f"{tag}{n}", RI / "resume" / f"{tag}{n}")
    return RI, hashlib.sha256((RI / "resume" / f"{tag}transcripts_manifest.json").read_bytes()).hexdigest()
RS, MS = resume_inputs("src_smoke", "FAKE_SMOKE_"); RF, MF = resume_inputs("src_full", "FAKE_")
def runb(out, smoke=True, **env):
    base = dict(SMOKE="1", INPUTS=RS, DRIFT_RESUME="resume", DRIFT_RESUME_MANIFEST_SHA=MS) if smoke else \
           dict(SMOKE="0", INPUTS=RF, DRIFT_RESUME="resume", DRIFT_RESUME_MANIFEST_SHA=MF)
    base.update(PHASEB="a"); base.update(env); return run("phaseb_lambda.py", out, **base)

def counts(src, out, P, ks_q1, ks_b3, nitems, npanel):
    n = {t["tid"]: t["n"] for t in (json.loads(l) for l in open(W / src / f"{P}transcripts.jsonl", encoding="utf-8")) if "tid" in t}
    L = lambda x: np.load(out / f"{P}{x}.npz")["rows"]
    b4, b1f, b3, b1p = L("b4"), L("b1_full"), L("b3"), L("b1_panel")
    want_p = sum(sum(1 for k in ks_q1 if k <= n[t]) for t in n) * npanel * 7; want3 = sum(sum(1 for k in ks_b3 if k <= n[t]) for t in n)
    check(f"[{out.name}] B4 rows = {nitems} items × 8 arms", len(b4) == nitems * 8 and len(np.unique(b4[:, 1])) == 8)
    check(f"[{out.name}] B1 full rows = {nitems} × 7", len(b1f) == nitems * 7)
    check(f"[{out.name}] B3 rows = Σ_t |{{k ∈ K_B3, k ≤ n_t}}| = {want3}", len(b3) == want3)
    check(f"[{out.name}] B1 panel rows = Σ_t |{{k ∈ K_Q1, k ≤ n_t}}| × {npanel} × 7 = {want_p}", len(b1p) == want_p)
    q1f = {(int(r[0]), int(r[1])): r[2:4] for r in np.load(W / src / f"{P}q1_full.npz")["rows"]}
    q1 = {tuple(int(x) for x in r[:4]): r[4:6] for r in np.load(W / src / f"{P}q1.npz")["rows"]}
    gf = max(np.abs(r[2:4] - q1f[(int(r[0]), int(r[1]))]).max() for r in b1f); gp = max(np.abs(r[4:6] - q1[tuple(int(x) for x in r[:4])]).max() for r in b1p)
    check(f"[{out.name}] B1 readouts = the source run's own (q1_full max |Δ| {gf:.1e}, q1 {gp:.1e}; ≤ 1e-9 on the FAKE: same rows)", gf <= 1e-9 and gp <= 1e-9)
    nt = {int(c): set(b1f[b1f[:, 1] == c, 5].astype(int).tolist()) for c in range(7)}
    same = all((b1f[b1f[:, 1] == D.Q1_CONDS.index(a), 5] == b1f[b1f[:, 1] == D.Q1_CONDS.index(u), 5]).all() for a, u in (("asst_imp", "user_imp"), ("asst_int", "user_int")))
    check(f"[{out.name}] B1 plant span: same plant text → same token count in either slot; log-probs finite and < 0",
          same and np.isfinite(b1f[:, 4]).all() and (b1f[:, 4] < 0).all() and np.isfinite(b1p[:, 6]).all())
    v = b3[:, 6] >= 0
    # (ON vs OFF readouts are NOT compared here: the toy's last state is order-invariant over the bag of tokens, and the
    # two arms hold the same tokens in a different order; the runner asserts the arms' content, PLANT b3same trips it)
    check(f"[{out.name}] B3: {int(v.sum())} valid of {len(b3)} — both branches run (FAKE lift); valid rows have finite ON / OFF readouts, dropped rows NaN",
          0 < v.sum() < len(b3) and np.isfinite(b3[v, 7:11]).all() and np.isnan(b3[~v, 7:11]).all())
    return b3

# ------------------------------------------------------------------ clean B-a SMOKE, twice (B3 sampling reproducible)
code, txt = runb(W / "b_smoke")
check("clean B-a SMOKE: exit 0, DONE, RESUMED, no generation", code == 0 and "DONE" in txt and "RESUMED" in txt and "phase 1 turn" not in txt)
if code: print(txt[-2500:])
else:
    b3a = counts("src_smoke", W / "b_smoke", "FAKE_SMOKE_", tuple(k for k in D.K_Q1 if k <= 8), tuple(k for k in B.K_B3 if k <= 8), 10, 2)
    code, txt = runb(W / "b_smoke2")
    check("B-a SMOKE re-run: B3 rows (sampled choices + readouts) bit-for-bit identical", code == 0 and
          np.load(W / "b_smoke2" / "FAKE_SMOKE_b3.npz")["rows"].tobytes() == b3a.tobytes())
    G = json.loads((W / "b_smoke" / "FAKE_SMOKE_B_gap_report.json").read_text(encoding="utf-8"))
    check(f"repeat check ran ({G['n']} picks); logits-kept vs readout gap reported ({G['max']:.1e} on the FAKE)", G["n"] == 6 and G["max"] < 1e-9)

# ------------------------------------------------------------------ clean B-a FULL
code, txt = runb(W / "b_full", smoke=False)
check("clean B-a FULL: exit 0, DONE, one PROJECTION logged", code == 0 and "DONE" in txt and txt.count("PROJECTION") == 1)
if code: print(txt[-2500:])
else:
    b3 = counts("src_full", W / "b_full", "FAKE_", D.K_Q1, B.K_B3, 720, 8)
    check("B3 (FULL): 144 transcripts × 3 k = 432 choice points", len(b3) == 432)

# ------------------------------------------------------------------ planted defects (SMOKE, each must trip its own stop)
for plant, want_code, want_txt, absent in (("bitcheck", 3, "BIT-CHECK FAILED", "b4"), ("nondeterm", 3, "REPEAT CHECK FAILED", "b4"),
                                           ("resumetamper", 3, "RESUME FREEZE", "b4"), ("spanoff", 3, "plant span is not the plant", "b4"),
                                           ("wrongslot", 3, "B4 plant not in its declared slot", "b4"), ("overbudget", 6, "PROJECTION", "b1_panel"),
                                           ("b3same", 3, "B3 arms wrong", "b3")):
    out = W / f"plant_{plant}"; code, txt = runb(out, PLANT=plant)
    ok = code == want_code and want_txt in txt and not (out / f"FAKE_SMOKE_{absent}.npz").exists()
    if plant == "overbudget": ok = ok and all((out / f"FAKE_SMOKE_{x}.npz").exists() for x in ("b4", "b1_full", "b3"))
    check(f"PLANT {plant}: exit {want_code}, '{want_txt}', no {absent} output" + (" (B4, B1 full, B3 kept)" if plant == "overbudget" else ""), ok)
    if not ok: print(f"     got exit {code}:", txt[-700:])
code, txt = runb(W / "badpin", DRIFT_RESUME_MANIFEST_SHA="0" * 64)
check("a manifest that is not the pinned one → exit 2", code == 2 and "not the pinned one" in txt)
code, txt = runb(W / "noresume", DRIFT_RESUME="")
check("no DRIFT_RESUME → refused (B-a never generates)", code != 0 and "DRIFT_RESUME is required" in txt)
code, txt = runb(W / "phase_b", PHASEB="b")
check("PHASEB=b (not built) → refused", code != 0 and "only 'a'" in txt)
code, txt = runb(W / "plant_real", FAKE="0", REAL="1", PLANT="bitcheck")
check("PLANT outside FAKE refused", code != 0 and "FAKE-only" in txt)
code, txt = runb(W / "b_smoke")
check("no-clobber: a run into a non-empty output folder is refused", code != 0 and "not empty" in txt)
code, txt = runb(W / "watch_low", RATE_PER_H="100000", WATCH_USD="0.01")
check("WATCH_USD = 0.01 at a huge rate → watchdog (exit 5) or projection (exit 6)", code in (5, 6) and ("WATCHDOG" in txt or "PROJECTION" in txt))
print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails))
sys.exit(1 if fails else 0)
