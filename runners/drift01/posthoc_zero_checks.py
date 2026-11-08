"""$0 checks on existing HUNT-DRIFT-01 outputs (post-hoc, not pre-registered; read-only; prints only).
(1) per-arm aligned A and READY part W vs k, relative to k = 0: full run (144 transcripts, 8 panel items, 5 arms) and B-b (96 × 8, 3 arms).
(2) Q3 role-axis slide (drift minus filler, L8) vs authority loss (drift − filler Y) per transcript, full run.
(3) A5 prose W at k = 1 per transcript vs the DONE − READY family-word count in that transcript's first prose turn pair."""
import json, os, re, sys
from pathlib import Path
import numpy as np
H = Path(r"D:\Resolve Research\Connection_Program\trackA\hunts\drift01"); sys.path.insert(0, str(H))
import drift01_core as D, phaseb_core as B
sys.stdout.reconfigure(encoding="utf-8")
C = [json.loads(l) for l in open(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl", encoding="utf-8")]
rk = lambda x: np.argsort(np.argsort(x)); sp = lambda a, b: float(np.corrcoef(rk(a), rk(b))[0, 1])
def boot_rho(a, b, n=2000, seed=7101001):
    g = np.random.default_rng(seed); r = []
    for _ in range(n):
        i = g.integers(0, len(a), len(a)); r.append(sp(a[i], b[i]))
    return np.percentile(r, [2.5, 97.5])

def arm_table(q, conds, label):
    """Item-balanced over DONEsys / READYsys items: A = (D̄ + R̄)/2, W = (R̄ − D̄)/2 of Y_signed, mean over transcripts."""
    y = D.y_signed(q[:, 4], q[:, 5], [C[int(i)]["target_sys"] for i in q[:, 1]])
    rdy = np.array([C[int(i)]["counterbalance"] == "READYsys" for i in q[:, 1]])
    KS = sorted({int(k) for k in q[:, 3]}); print(f"\n[{label}] items {len(set(q[:,1].astype(int)))} (READYsys {len({int(i) for i, r in zip(q[:,1], rdy) if r})}) · transcripts {len(set(q[:,0].astype(int)))}")
    for c, nm in enumerate(conds):
        out = []
        for k in KS:
            s = (q[:, 2] == c) & (q[:, 3] == k)
            if not s.any(): continue
            d, r = y[s & ~rdy].mean(), y[s & rdy].mean(); out.append(f"k{k} A {(d + r) / 2:+.2f} W {(r - d) / 2:+.2f}")
        print(f"  {nm:8s} " + " | ".join(out))

# (1) full run and B-b
F = H / "out/full_20261025T121206Z"; q0 = np.load(F / "REAL_q0.npz")["rows"]
arm_table(q0, D.Q0_CONDS, "full run Q0 (cond order = Q0_CONDS)")
arm_table(np.load(H / "out/phaseBb_20261102T230350Z/REAL_b5_q0.npz")["rows"], B.B5_CONDS, "B-b b5_q0")

# (2) Q3 slide vs authority loss, full run
man = json.loads((F / "REAL_transcripts_manifest.json").read_text(encoding="utf-8")); CELLS = [tuple(c) for c in man["cells"]]
pil = H.parents[1] / "pilot"; probe = D.fit_role_probe(np.load(pil / "out" / "pilot_acts_open.npz"), np.load(pil / "pilot_inputs.npz"))
P4 = np.load(F / "REAL_phase4.npz"); y0 = D.y_signed(q0[:, 4], q0[:, 5], [C[int(i)]["target_sys"] for i in q0[:, 1]])
dr, fi = D.Q0_CONDS.index("drift"), D.Q0_CONDS.index("filler")
print("\n[Q3 slide (drift − filler, rel. turn 1; + = toward system) vs Δ = mean_i Y_drift − Y_filler at k] per transcript, full run")
for k in (8, 16, 32):
    sl, de, md = [], [], []
    for t in sorted({int(x) for x in q0[:, 0]}):
        if f"t{t}_drift_L8" not in P4.files: continue
        r = D.role_trajectory(probe, P4[f"t{t}_drift_L8"].astype(np.float64), P4[f"t{t}_filler_L8"].astype(np.float64))["rel_turn1_minus_filler"]
        a = (q0[:, 0] == t) & (q0[:, 3] == k)
        if len(r) < k or not ((a) & (q0[:, 2] == dr)).any(): continue
        yd, yf = y0[a & (q0[:, 2] == dr)], y0[a & (q0[:, 2] == fi)]
        sl.append(r[k - 1]); de.append(yd.mean() - yf.mean()); md.append(CELLS[t][0])
    sl, de, md = map(np.array, (sl, de, md)); lo, hi = boot_rho(sl, de)
    by = " · ".join(f"{m} {sp(sl[md == m], de[md == m]):+.2f} (n {int((md == m).sum())})" for m in sorted(set(md)))
    print(f"  k={k}: ρ {sp(sl, de):+.2f} [{lo:+.2f}, {hi:+.2f}] n {len(sl)} · within mode: {by}")

# (3) prose k = 1 DONE lean vs first prose pair's family-word counts (A5)
os.environ.setdefault("HF_HOME", r"R:\hf\c_huggingface"); os.environ["HF_HUB_OFFLINE"] = "1"; os.environ["TRANSFORMERS_OFFLINE"] = "1"
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", revision=D.REV, cache_dir=r"R:\hf\c_huggingface\hub")
enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]; dec = lambda ids: tok.decode(ids)
PROSE = enc((H / "prose_src" / "pg1228_prose.txt").read_text(encoding="utf-8"))
Bb = H / "out/phaseBb_20261102T230350Z"; Zr = np.load(Bb / "REAL_b5_transcripts.npz"); flat = {}
for q in range(len(Zr["tid"])): flat.setdefault(int(Zr["tid"][q]), []).append(Zr["ids"][Zr["off"][q]:Zr["off"][q + 1]].tolist())
T = {t: list(zip(v[0::2], v[1::2])) for t, v in flat.items() if t < B.WI_TID0}
PI = json.loads((H / "out/phaseBe_20261105T050023Z/REAL_a5_prose.json").read_text(encoding="utf-8"))
RX = {w: re.compile(r"\b(" + "|".join(v) + r")\b", re.I) for w, v in {"DONE": ("done", "finished", "complete", "completed"), "READY": ("ready", "prepared", "set")}.items()}
chk = sum(1 for t in T if sum(len(u) + len(a) for u, a in B.prose_pairs(PROSE, T[t][:32], t)) == PI[str(t)]["ntok"])
print(f"\n[prose reconstruction] ntok matches REAL_a5_prose.json for {chk} / {len(T)} transcripts")
q5 = np.load(H / "out/phaseBe_20261105T050023Z/REAL_a5_q0.npz")["rows"]; y5 = D.y_signed(q5[:, 4], q5[:, 5], [C[int(i)]["target_sys"] for i in q5[:, 1]])
rdy5 = np.array([C[int(i)]["counterbalance"] == "READYsys" for i in q5[:, 1]]); PR, FI = B.B6_CONDS.index("prose"), B.B6_CONDS.index("filler")
w1, w1f, net, cnt = [], [], [], []
for t in sorted(T):
    u, a = B.prose_pairs(PROSE, T[t][:1], t)[0]; txt = dec(u) + " " + dec(a)
    nd, nr = len(RX["DONE"].findall(txt)), len(RX["READY"].findall(txt))
    def W(c):
        s = (q5[:, 0] == t) & (q5[:, 3] == 1) & (q5[:, 2] == c); return (y5[s & rdy5].mean() - y5[s & ~rdy5].mean()) / 2
    w1.append(W(PR) - W(FI)); net.append(nd - nr); cnt.append(nd + nr)
w1, net, cnt = map(np.array, (w1, net, cnt)); lo, hi = boot_rho(net, w1)
print(f"[prose − filler W at k = 1 per transcript] mean {w1.mean():+.2f} · transcripts with any family word in turn pair 1: {(cnt > 0).sum()} / {len(cnt)}")
print(f"  ρ(DONE − READY count, W) {sp(net, w1):+.2f} [{lo:+.2f}, {hi:+.2f}]  (DONE lexical account predicts ρ < 0)")
print(f"  W where the first pair has NO family words: {w1[cnt == 0].mean():+.2f} (n {(cnt == 0).sum()}) · with DONE > READY: {w1[net > 0].mean() if (net > 0).any() else float('nan'):+.2f} (n {(net > 0).sum()})")
