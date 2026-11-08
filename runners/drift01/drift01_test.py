"""HUNT-DRIFT-01 piece 4 — the FAKE test (local, no torch, no model). EXPLORATORY.
  python drift01_test.py <empty work folder on D:>
Core unit checks (filler off by one, A(k) ratio of means + the ÷≈0 guard, band verdicts, k_half, bootstrap, seed
guard, freeze check, sensitivity mask, tagger, loop / attractor rules) → a clean FAKE SMOKE run → a clean FAKE FULL run
(counts against the design, computed from the run's own transcripts) → every planted defect must trip its own stop:
bitcheck · cachedrift · tamper · wrongslot · badseed · overbudget · a tampered pinned input · no-clobber · PLANT
outside FAKE."""
import json, os, shutil, subprocess, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D
W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True); assert not any(W.iterdir()), f"{W} not empty"
RUN = HERE / "drift01_lambda.py"
STIM = Path(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl")
fails = []
def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name, flush=True)
    if not ok: fails.append(name)
def refuses(fn, exc=(SystemExit, AssertionError, ValueError)):
    try: fn(); return False
    except exc: return True

# ------------------------------------------------------------------ core unit checks
POOL = (HERE / "word_pool_drift01.txt").read_text(encoding="utf-8").split()
FORMS = json.loads((HERE / "intention_forms.json").read_text(encoding="utf-8"))["forms"]
C = [json.loads(l) for l in open(STIM, encoding="utf-8")]
enc = lambda s: [ord(ch) for ch in s]                       # char-level stand-in: exercises the core's own logic
pairs = [(enc("Continue."), enc("I wonder about tides.")), (enc("Continue."), enc("Numbers, then."))]
check("filler: token-matched to the drift (q0_rows builds)", not refuses(lambda: D.q0_rows(enc, POOL, C[0], "", pairs, pairs, 0, (0, 1, 2))))
orig = D.fill_ids
D.fill_ids = lambda e, p, n, key: orig(e, p, n, key) + [1]   # PLANT: filler one token too long
check("PLANT filler off by one token → q0_rows REFUSES", refuses(lambda: D.q0_rows(enc, POOL, C[0], "", pairs, pairs, 0, (0, 1, 2))))
D.fill_ids = orig
check("A(k) = ratio of MEANS (not a mean of ratios)", abs(D.authority([1, 3], [0, 0], [2, 2], [0, 0]) - 1.0) < 1e-12
      and abs(D.authority([1, 3], [0, 0], [1, 3], [0, 0]) - 1.0) < 1e-12 and abs(D.authority([1, 1], [0, 0], [0.1, 3.9], [0, 0]) - 0.5) < 1e-12)
pi = D.per_item_authority([0.5, 2.0], [0, 0], [0.5, 4.0], [0, 0])
check("PLANT ÷≈0: per-item A with |Y(0) − Y_none(0)| < 1 nat → NaN (never pooled); ≥ 1 nat kept", np.isnan(pi[0]) and pi[1] == 0.5)
check("PLANT ÷0: pooled A with a zero denominator → NaN, not inf", np.isnan(D.authority([1], [0], [0], [0])))
check("band verdicts (δ = 0.234)", [D.band_verdict(-0.5, (-0.8, -0.3)), D.band_verdict(0.0, (-0.1, 0.1)), D.band_verdict(0.5, (0.3, 0.8)),
                                    D.band_verdict(-0.1, (-0.4, 0.2))] == ["content-driven", "distance-driven", "drift protects", "indeterminate"])
check("k_half: first k with A ≤ 0.5; None if never", D.k_half({0: 1, 4: 0.7, 16: 0.45, 64: 0.2}) == 16 and D.k_half({0: 1, 64: 0.6}) is None)
g = np.random.default_rng(5); it = np.repeat(np.arange(12), 8); sd = np.tile(np.arange(8), 12); x = 1.0 + g.normal(0, 1, 96)
lo, hi = D.boot2(x, None, it, sd)
check(f"two-way bootstrap: CI [{lo:.2f}, {hi:.2f}] covers the sample mean, finite", lo < x.mean() < hi and np.isfinite([lo, hi]).all())
check("PLANT seed outside 7101xxx (101, the v0.1 seeds' kind; 20261025 = stage-1 SEED_DISC) refused",
      refuses(lambda: D.check_seed(101)) and refuses(lambda: D.check_seed(20261025)) and not refuses(lambda: D.check_seed(7101101)))
man = {"0": D.transcript_sha(pairs)}; bad = [(pairs[0][0], pairs[0][1][:-1] + [pairs[0][1][-1] + 1]), pairs[1]]
check("PLANT a transcript changed after freezing → verify_frozen reports it", D.verify_frozen({0: pairs}, man) == [] and D.verify_frozen({0: bad}, man) != [])
check("sensitivity mask drops templates 5, 7, 16, 20 only", D.drop_non_minimal(np.arange(30)).sum() == 26 and not D.drop_non_minimal([16])[0])
check("Q2 tagger: self-directives counted, plain prose not", D.tag_count("From now on I will always rhyme. Let's go.") >= 3
      and D.tag_count("The river was cold and the sky was grey.") == 0)
v = g.normal(0, 1, (4, 32)); per = np.array([v[t % 4] for t in range(40)]); rnd = g.normal(0, 1, (40, 32))
okp, p = D.loops(D.selfsim(per)); okr, _ = D.loops(D.selfsim(rnd))
check(f"loop rule: a period-4 sequence loops (p = {p}); random turns do not", okp and p == 4 and not okr)
check("attractor rule: ≥ 6 / 8 seeds with the same period → attractor; 5 → not",
      D.attractor([(True, 4)] * 6 + [(False, 0)] * 2, rnd[:8])[0] and not D.attractor([(True, 4)] * 5 + [(False, 0)] * 3, rnd[:8])[0])

# ------------------------------------------------------------------ inputs folder (pinned files + the FAKE pilot reference)
INP = W / "inputs"; INP.mkdir()
for f in ("panel.json", "intention_forms.json", "word_pool_drift01.txt"): shutil.copy2(HERE / f, INP / f)
shutil.copy2(STIM, INP / STIM.name)
def run(out, **env):
    e = dict(os.environ); [e.pop(k, None) for k in ("FAKE", "REAL", "SMOKE", "PLANT", "FAKE_MAKE_REF", "DRIFT_RESUME", "DRIFT_RESUME_MANIFEST_SHA", "WATCH_USD", "RATE_PER_H")]
    e.update(FAKE="1", DRIFT_INPUTS=str(env.pop("INPUTS", INP)), DRIFT_OUT=str(out), PYTHONIOENCODING="utf-8"); e.update(env)
    r = subprocess.run([sys.executable, str(RUN)], env=e, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr
code, txt = run(W / "ref", SMOKE="0", FAKE_MAKE_REF="1"); shutil.copy2(W / "ref" / "FAKE_pilot_lp.npz", INP / "FAKE_pilot_lp.npz")
check("FAKE pilot reference built for the 8 panel items (Amendment 2 A2.2)", code == 0 and len(np.load(INP / "FAKE_pilot_lp.npz")["lp"]) == 8)

# ------------------------------------------------------------------ clean SMOKE
code, txt = run(W / "smoke", SMOKE="1")
check("clean FAKE SMOKE: exit 0, DONE", code == 0 and "DONE" in txt)
if code: print(txt[-2000:])

# ------------------------------------------------------------------ clean FULL (counts from the run's own transcripts)
code, txt = run(W / "full", SMOKE="0")
check("clean FAKE FULL: exit 0, DONE, both projections logged", code == 0 and "DONE" in txt and txt.count("PROJECTION") == 2)
if code: print(txt[-3000:])
else:
    F = W / "full"; P = "FAKE_"
    tr = [json.loads(l) for l in open(F / f"{P}transcripts.jsonl", encoding="utf-8")]
    main = [t for t in tr if "tid" in t]; wi = [t for t in tr if "with_instruction" in t]
    check(f"transcripts: 144 (3 modes × 3 personas × 2 T × 8 seeds) + 12 with-instruction", len(main) == 144 and len(wi) == 12)
    n = {t["tid"]: t["n"] for t in main}
    want0 = sum(sum(1 for k in D.K_Q0 if k <= n[t]) for t in n) * 8 * 5
    want1 = sum(sum(1 for k in D.K_Q1 if k <= n[t]) for t in n) * 8 * 7
    q0, q1, qf = (np.load(F / f"{P}{x}.npz")["rows"] for x in ("q0", "q1", "q1_full"))
    check(f"Q0 rows = Σ_t |{{k ≤ n_t}}| × 8 items × 5 conditions = {want0}", len(q0) == want0)
    check(f"Q1 rows = Σ_t |{{k ∈ K_Q1, k ≤ n_t}}| × 8 × 7 = {want1}", len(q1) == want1)
    dd, cc = q0[q0[:, 2] == 0], q0[q0[:, 2] == 2]; pos = dd[:, 3] > 0
    check("Amendment 2 A2.1: C-cross differs from C-drift at k > 0 (not a relabelling) and equals it at k = 0",
          np.array_equal(dd[~pos, 4:6], cc[~pos, 4:6]) and (np.abs(dd[pos, 4:6] - cc[pos, 4:6]).max(1) > 0).mean() > 0.99
          and np.mean(dd[pos, 4]) != np.mean(cc[pos, 4]))
    check("Q1 full battery: 720 items × 7 conditions", len(qf) == 720 * 7 and len(np.unique(qf[:, 0])) == 720)
    d = q0[q0[:, 2] == 0]; f = q0[q0[:, 2] == 1]
    check("C-filler distance = C-drift distance at every (transcript, item, k) (token-matched)", np.array_equal(d[:, [0, 1, 3, 6]], f[:, [0, 1, 3, 6]]))
    check("every readout finite", np.isfinite(q0[:, 4:6]).all() and np.isfinite(q1[:, 4:6]).all() and np.isfinite(qf[:, 2:4]).all())
    Z = np.load(F / f"{P}transcripts.npz"); manj = json.loads((F / f"{P}transcripts_manifest.json").read_text(encoding="utf-8"))["sha"]
    rebuilt = {}
    for q in range(len(Z["tid"])):
        rebuilt.setdefault(int(Z["tid"][q]), []).append(Z["ids"][Z["off"][q]:Z["off"][q + 1]].tolist())
    rp = {t: list(zip(v[0::2], v[1::2])) for t, v in rebuilt.items()}
    check("saved transcript ids re-hash to the manifest (the freeze is real)", D.verify_frozen(rp, manj) == [])
    P4 = np.load(F / f"{P}phase4.npz")
    check("phase 4: 144 transcripts × {drift, filler} × {L8, L16}, one vector per turn", len(P4.files) == 144 * 4
          and all(P4[f"t{t}_drift_L8"].shape[0] == n[t] for t in n))
    G = json.loads((F / f"{P}gap_report.json").read_text(encoding="utf-8"))
    check("gap report: 48 repeat-checked picks, gap 0 on the exact FAKE (Amendment 1 A1.1)", G["n"] == 48 and G["max"] == 0.0)
    check("Amendment 1 A1.2: every main transcript has 32 turns", all(t["n"] == 32 for t in main))
    t1 = {}
    for t in main: t1.setdefault((t["persona"], t["temp"], t["seed"]), []).append(t["turns"][0]["assistant"])
    check("Amendment 1 A1.3: no two modes share a first turn (same persona, T, seed)", all(len(set(v)) == len(v) for v in t1.values()))
    L = json.loads((F / f"{P}ledger.json").read_text(encoding="utf-8"))
    check("ledger written, status DONE", L["status"] == "DONE")

# ------------------------------------------------------------------ planted defects (SMOKE, each must trip its own stop)
out = W / "plant_cachedrift"; code, txt = run(out, SMOKE="1", PLANT="cachedrift")
G = json.loads((out / "FAKE_SMOKE_gap_report.json").read_text(encoding="utf-8")) if (out / "FAKE_SMOKE_gap_report.json").exists() else {}
check("PLANT a constant branched-vs-fresh gap (0.05) → REPORTED in the gap report, not a stop (Amendment 1 A1.1)",
      code == 0 and abs(G.get("max", 0) - 0.05) < 1e-6 and abs(G.get("median", 0) - 0.05) < 1e-6)
for plant, want_code, want_txt, no_q0 in (("bitcheck", 3, "BIT-CHECK FAILED", True), ("nondeterm", 3, "REPEAT CHECK FAILED", True),
                                          ("tamper", 3, "FREEZE", True), ("wrongslot", 3, "declared slot", True),
                                          ("badseed", 2, "namespace", True), ("overbudget", 6, "PROJECTION", True)):
    out = W / f"plant_{plant}"; code, txt = run(out, SMOKE="1", PLANT=plant)
    ok = code == want_code and want_txt in txt and (not no_q0 or not (out / "FAKE_SMOKE_q0.npz").exists())
    check(f"PLANT {plant}: exit {want_code}, '{want_txt}', no Phase-2 output", ok)
    if not ok: print(f"     got exit {code}:", txt[-600:])
out = W / "plant_oom"; code, txt = run(out, SMOKE="1", PLANT="oom", DRIFT_BATCH="4")
check("PLANT CUDA out-of-memory in generation → sub-batch halved (4 → 2), run completes", code == 0 and "OOM at sub-batch 4 → 2" in txt and "DONE" in txt)
# RESUME (2026-10-25): load the clean SMOKE's frozen transcripts, skip Phase 1, must reproduce its readouts bit-for-bit
import hashlib
RI = W / "inputs_resume"; shutil.copytree(INP, RI); (RI / "resume").mkdir()
for n in ("transcripts.npz", "transcripts.jsonl", "transcripts_manifest.json"): shutil.copy2(W / "smoke" / f"FAKE_SMOKE_{n}", RI / "resume" / f"FAKE_SMOKE_{n}")
MS = hashlib.sha256((RI / "resume" / "FAKE_SMOKE_transcripts_manifest.json").read_bytes()).hexdigest()
code, txt = run(W / "resume_ok", SMOKE="1", INPUTS=RI, DRIFT_RESUME="resume", DRIFT_RESUME_MANIFEST_SHA=MS)
same = code == 0 and np.load(W / "resume_ok" / "FAKE_SMOKE_q0.npz")["rows"].tobytes() == np.load(W / "smoke" / "FAKE_SMOKE_q0.npz")["rows"].tobytes()
check("RESUME: Phase 1 skipped, frozen transcripts verified, Q0 readouts = the original smoke's BIT-FOR-BIT", same and "RESUMED" in txt and "phase 1 turn" not in txt)
code, txt = run(W / "resume_badpin", SMOKE="1", INPUTS=RI, DRIFT_RESUME="resume", DRIFT_RESUME_MANIFEST_SHA="0" * 64)
check("RESUME with a manifest that is not the pinned one → exit 2", code == 2 and "not the pinned one" in txt)
code, txt = run(W / "resume_tamper", SMOKE="1", INPUTS=RI, DRIFT_RESUME="resume", DRIFT_RESUME_MANIFEST_SHA=MS, PLANT="resumetamper")
check("PLANT a resumed transcript changed after freezing → exit 3 'RESUME FREEZE'", code == 3 and "RESUME FREEZE" in txt)
RJ = W / "inputs_resume_full"; shutil.copytree(RI, RJ)
for n in ("transcripts.npz", "transcripts.jsonl", "transcripts_manifest.json"): (RJ / "resume" / f"FAKE_SMOKE_{n}").rename(RJ / "resume" / f"FAKE_{n}")
code, txt = run(W / "resume_design", SMOKE="0", INPUTS=RJ, DRIFT_RESUME="resume", DRIFT_RESUME_MANIFEST_SHA=MS)
check("RESUME of a different design (smoke transcripts into a full run) → exit 2", code == 2 and "different design" in txt)
code, txt = run(W / "watch_low", SMOKE="1", RATE_PER_H="100000", WATCH_USD="0.01")
check("settable cap: WATCH_USD = 0.01 at a huge rate → the watchdog stops the run (exit 5 or a projection exit 6)", code in (5, 6) and ("WATCHDOG" in txt or "PROJECTION" in txt))
bad = W / "inputs_bad"; shutil.copytree(INP, bad); (bad / "panel.json").write_bytes((bad / "panel.json").read_bytes() + b" ")
code, txt = run(W / "plant_pin", SMOKE="1", INPUTS=bad)
check("PLANT a pinned input changed by one byte (panel.json) → exit 2 'hash mismatch'", code == 2 and "panel.json hash mismatch" in txt)
code, txt = run(W / "smoke", SMOKE="1")
check("no-clobber: a run into a non-empty output folder is refused", code != 0 and "not empty" in txt)
code, txt = run(W / "plant_real", SMOKE="1", FAKE="0", REAL="1", PLANT="bitcheck")
check("PLANT outside FAKE refused", code != 0 and "FAKE-only" in txt)
print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails))
sys.exit(1 if fails else 0)
