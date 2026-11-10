"""HUNT-DRIFT-01 A9b — FAKE test of phaseb_lambda.py PHASEB=k (Amendment 9b 87eae7d9…: A10's rows + A7 probe N on the native
crops + the A8 subset, every row with residuals at a9b_core.LAYERS + Control 1).
  python phasek_test.py <empty work folder on D:> <a folder holding inputs/FAKE_pilot_lp.npz>
References first: FAKE G FULL (a7_q0) → FAKE I FULL (a10_q0) → FAKE B-b SMOKE + FULL (resume) → FAKE H SMOKE + FULL (a8_q0).
Clean K SMOKE + FULL: block sizes = a9b_core.n_rows; every row filled; codes per block; h / e0 shapes; A10 rows = I's
a10_q0 and A7-N rows = G's N rows and A8 rows = H's a8_q0 bit-for-bit on the FULL (every row, not only the gate); texts =
one per A10 row; repro gates bitwise; re-run bit-for-bit (rows, h, e0, texts) · plants: a9bswap → 3 · reprooff → 3 ·
nondeterm → 3 · hdrift → 3 · overbudget → 6 · bitcheck → 3 · no a10 reference → 2 · no resume → refused · no-clobber."""
import hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import a9b_core as A9B
sys.stdout.reconfigure(encoding="utf-8")
W = Path(sys.argv[1]).resolve(); W.mkdir(parents=True, exist_ok=True); assert not any(W.iterdir()), f"{W} not empty"
SRC = Path(sys.argv[2]).resolve()
STIM = Path(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl")
fails = []
def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name, flush=True)
    if not ok: fails.append(name)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
A7I = sorted(x["item"] for x in json.loads((HERE / "a7_items.json").read_text(encoding="utf-8"))["items"])
A8I = [x["item"] for x in json.loads((HERE / "a8_items.json").read_text(encoding="utf-8"))["items"]]
C = [json.loads(l) for l in open(STIM, encoding="utf-8")]
A8S = A9B.a8_subset(C, A8I)
check(f"a8_subset: 60 items, 30 templates, 1 DONEsys + 1 READYsys each, a8_items order ({len(A8S)})",
      len(A8S) == 60 and len({C[i]["template_idx"] for i in A8S}) == 30
      and all(sorted(C[i]["counterbalance"] for i in A8S if C[i]["template_idx"] == t) == ["DONEsys", "READYsys"] for t in range(30))
      and A8S == [i for i in A8I if i in set(A8S)])
INP = W / "inputs"; INP.mkdir()
for f in ("panel.json", "intention_forms.json", "word_pool_drift01.txt", "a5_items.json", "a7_items.json", "a7_demos.json", "a8_items.json"):
    shutil.copy2(HERE / f, INP / f)
shutil.copy2(STIM, INP / STIM.name); shutil.copy2(SRC / "inputs" / "FAKE_pilot_lp.npz", INP / "FAKE_pilot_lp.npz")
CLEAR = ("FAKE", "REAL", "SMOKE", "PLANT", "DRIFT_RESUME", "DRIFT_RESUME_MANIFEST_SHA", "WATCH_USD", "RATE_PER_H", "PHASEB", "DRIFT_BATCH")
def run(out, phase="k", smoke=True, inp=INP, **env):
    e = dict(os.environ); [e.pop(k, None) for k in CLEAR]
    e.update(FAKE="1", PHASEB=phase, SMOKE="1" if smoke else "0", DRIFT_INPUTS=str(inp), DRIFT_OUT=str(out), PYTHONIOENCODING="utf-8"); e.update(env)
    r = subprocess.run([sys.executable, str(HERE / "phaseb_lambda.py")], env=e, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr
def must(code, txt, what):
    check(f"{what}: exit 0", code == 0)
    if code: print(txt[-2500:]); sys.exit(1)

# ---------------------------------------------------------------- references
must(*run(W / "g_ref", phase="g", smoke=False), "FAKE G FULL (a7_q0)"); shutil.copy2(W / "g_ref" / "FAKE_a7_q0.npz", INP / "FAKE_a7_q0.npz")
must(*run(W / "i_ref", phase="i", smoke=False), "FAKE I FULL (a10_q0)"); INP_NO10 = W / "inputs_no10"; shutil.copytree(INP, INP_NO10)
shutil.copy2(W / "i_ref" / "FAKE_a10_q0.npz", INP / "FAKE_a10_q0.npz")
RES = {}
for smoke, name, P_ in ((True, "resume_smoke", "FAKE_SMOKE_"), (False, "resume_full", "FAKE_")):
    must(*run(W / f"bb_{name}", phase="b", smoke=smoke), f"FAKE B-b {'SMOKE' if smoke else 'FULL'}")
    (INP / name).mkdir()
    for n in ("b5_transcripts.npz", "b5_transcripts.jsonl", "b5_transcripts_manifest.json"): shutil.copy2(W / f"bb_{name}" / f"{P_}{n}", INP / name / f"{P_}{n}")
    RES[smoke] = dict(DRIFT_RESUME=name, DRIFT_RESUME_MANIFEST_SHA=sha(INP / name / f"{P_}b5_transcripts_manifest.json"))
    must(*run(W / f"h_{name}", phase="h", smoke=smoke, **RES[smoke]), f"FAKE H {'SMOKE' if smoke else 'FULL'} (a8_q0)")
    shutil.copy2(W / f"h_{name}" / f"{P_}a8_q0.npz", INP / f"{P_}a8_q0.npz")

# ---------------------------------------------------------------- clean K
def counts(out, P_, n_probe, nd, a8s, full=False):
    z = np.load(out / f"{P_}a9b_q0.npz"); q = z["rows"]; H = np.load(out / f"{P_}a9b_h.npy", mmap_mode="r"); E = np.load(out / f"{P_}a9b_e0.npy", mmap_mode="r")
    NP = len(z["pair_seed"]); n10, n7, n8 = A9B.n_rows(n_probe, nd, 4, 4, 4, NP, 4, len(a8s))
    check(f"[{out.name}] blocks = n_rows ({n10}, {n7}, {n8}); every row filled; cols = a9b_core.COLS",
          list(z["blocks"]) == [n10, n7, n8] and len(q) == n10 + n7 + n8 and z["filled"].all() and list(z["cols"]) == list(A9B.COLS) and np.isfinite(q[:, 10:]).all())
    check(f"[{out.name}] h {H.shape} = rows × {len(A9B.LAYERS)} layers × d, fp16; e0 {E.shape}; finite",
          H.shape[:2] == (len(q), len(A9B.LAYERS)) and H.dtype == np.float16 and E.shape == (len(q), H.shape[2]) and np.isfinite(H).all() and np.isfinite(E).all())
    b10, b7, b8 = q[:n10], q[n10:n10 + n7], q[n10 + n7:]
    check(f"[{out.name}] block codes: src 0 / 1 / 2; A10 probe C, renders −1..3; A7-N probe N, render 0 / −1; A8 items = the subset, pairs 0..{NP - 1}, cells 0..3, conds 0 / 1",
          set(b10[:, 0]) == {0} and set(b7[:, 0]) == {1} and set(b8[:, 0]) == {2} and set(b10[:, 6]) == {0} and set(b7[:, 6]) == {1}
          and sorted({int(x) for x in b10[:, 5]}) == [-1, 0, 1, 2, 3] and sorted({int(x) for x in b7[:, 5]}) == [-1, 0]
          and sorted({int(x) for x in b10[:, 1]}) == A7I[:n_probe] and sorted({int(x) for x in b8[:, 1]}) == sorted(a8s)
          and sorted({int(x) for x in b8[:, 7]}) == list(range(NP)) and sorted({int(x) for x in b8[:, 8]}) == [0, 1, 2, 3] and sorted({int(x) for x in b8[:, 9]}) == [0, 1])
    tx = [json.loads(l) for l in open(out / f"{P_}a9b_texts.jsonl", encoding="utf-8")]
    check(f"[{out.name}] texts: one per A10 row, rows 0..{n10 - 1} in order", [t["row"] for t in tx] == list(range(n10)) and all(t["text"] for t in tx))
    nat = b10[b10[:, 5] == 0]; k10 = {(int(x[1]), int(x[2]), int(x[3]), int(x[4])): k for k, x in enumerate(q[:n10]) if x[5] == 0}
    k7 = {(int(x[1]), int(x[2]), int(x[3]), int(x[4])): n10 + k for k, x in enumerate(b7) if x[5] == 0}
    check(f"[{out.name}] N rows share the C rows' crop: same distance; h differs (another suffix)",
          all(q[k10[key]][12] == q[k7[key]][12] for key in k10) and any((H[k10[key]] != H[k7[key]]).any() for key in list(k10)[:20]))
    RP = json.loads((out / f"{P_}a9b_repro.json").read_text(encoding="utf-8")); G = json.loads((out / f"{P_}a9b_gap_report.json").read_text(encoding="utf-8"))
    check(f"[{out.name}] repro gates bitwise on the FAKE ({RP['bitwise']} / {RP['n']}; by src {[RP['by_src'][s]['n'] for s in A9B.SRC]}); prefill = fresh (gap max {G['max']:.1e})",
          RP["bitwise"] == RP["n"] > 0 and all(RP["by_src"][s]["n"] > 0 for s in A9B.SRC) and G["max"] < 1e-9)
    if full:
        r10 = np.load(INP / "FAKE_a10_q0.npz")["rows"]; r7 = np.load(INP / "FAKE_a7_q0.npz")["rows"]; r8 = np.load(INP / f"{P_}a8_q0.npz")["rows"]
        F10 = {(int(x[0]), int(x[1]), int(x[2]), int(x[3]), int(x[9])): tuple(x[4:9]) for x in r10}
        F7 = {(int(x[0]), int(x[1]), int(x[2]), int(x[3])): tuple(x[4:9]) for x in r7 if x[9] == 1}
        F8 = {(int(x[0]), int(x[1]), int(x[2]), int(x[3])): tuple(x[4:9]) for x in r8}
        check("FULL: every A10 row = I's a10_q0 bit-for-bit (lpD, lpR, dist, no-space)",
              len(b10) == len(F10) and all(F10[(int(x[1]), int(x[2]), int(x[3]), int(x[4]), int(x[5]))] == tuple(x[10:15]) for x in b10))
        check("FULL: every A7-N row = G's N rows bit-for-bit", len(b7) == len(F7) and all(F7[(int(x[1]), int(x[2]), int(x[3]), int(x[4]))] == tuple(x[10:15]) for x in b7))
        check("FULL: every A8-subset row = H's a8_q0 bit-for-bit", all(F8[(int(x[7]), int(x[8]), int(x[9]), int(x[1]))] == tuple(x[10:15]) for x in b8))
    return q, H, E

code, txt = run(W / "k_smoke", **RES[True])
check("clean K SMOKE: exit 0, DONE, row checks OK, repro gates PASS, no grid fallback",
      code == 0 and "DONE" in txt and "A9b row checks OK" in txt and "repro gates PASS" in txt and "fell back to the 4,096 grid 0 time(s)" in txt)
if code: print(txt[-2500:])
else:
    q1, H1, E1 = counts(W / "k_smoke", "FAKE_SMOKE_", 4, 2, A8S[:3])
    code, txt = run(W / "k_smoke2", **RES[True])
    check("re-run: rows, h, e0 and texts bit-for-bit identical",
          code == 0 and np.load(W / "k_smoke2" / "FAKE_SMOKE_a9b_q0.npz")["rows"].tobytes() == q1.tobytes()
          and sha(W / "k_smoke2" / "FAKE_SMOKE_a9b_h.npy") == sha(W / "k_smoke" / "FAKE_SMOKE_a9b_h.npy")
          and sha(W / "k_smoke2" / "FAKE_SMOKE_a9b_e0.npy") == sha(W / "k_smoke" / "FAKE_SMOKE_a9b_e0.npy")
          and sha(W / "k_smoke2" / "FAKE_SMOKE_a9b_texts.jsonl") == sha(W / "k_smoke" / "FAKE_SMOKE_a9b_texts.jsonl"))
code, txt = run(W / "k_full", smoke=False, **RES[False])
check("clean K FULL: exit 0, DONE, projection logged", code == 0 and "DONE" in txt and "PROJECTION" in txt)
if code: print(txt[-2500:])
else: counts(W / "k_full", "FAKE_", 120, 8, A8S, full=True)

# ---------------------------------------------------------------- plants and refusals
for plant, want_code, want_txt in (("a9bswap", 3, "A9b ROW CHECK FAILED"), ("reprooff", 3, "REPRO GATE FAILED"), ("nondeterm", 3, "REPEAT CHECK FAILED"),
                                   ("hdrift", 3, "REPEAT CHECK FAILED"), ("overbudget", 6, "PROJECTION"), ("bitcheck", 3, "BIT-CHECK FAILED")):
    out = W / f"plant_{plant}"; code, txt = run(out, PLANT=plant, **RES[True])
    ok = code == want_code and want_txt in txt and not (out / "FAKE_SMOKE_a9b_q0.npz").exists()
    check(f"PLANT {plant}: exit {want_code}, '{want_txt}', no a9b_q0", ok)
    if not ok: print(f"     got exit {code}:", txt[-600:])
for name in ("resume_smoke",): shutil.copytree(INP / name, INP_NO10 / name)
shutil.copy2(INP / "FAKE_SMOKE_a8_q0.npz", INP_NO10 / "FAKE_SMOKE_a8_q0.npz")
code, txt = run(W / "no10", inp=INP_NO10, **RES[True])
check("no a10 reference in the inputs → 2, no a9b_q0", code == 2 and "a10_q0.npz is not in the inputs" in txt and not (W / "no10" / "FAKE_SMOKE_a9b_q0.npz").exists())
code, txt = run(W / "noresume")
check("no DRIFT_RESUME → refused", code != 0 and "DRIFT_RESUME is required" in txt)
code, txt = run(W / "k_smoke", **RES[True])
check("no-clobber", code != 0 and "not empty" in txt)
print("\nALL PASS" if not fails else "\nFAILURES: " + ", ".join(fails))
sys.exit(1 if fails else 0)
