"""HUNT-DRIFT-01 B5 per-item breakdown (EXPLORATORY, POST-HOC: hypothesis generation only; nothing here is a test).
  python b5_items.py <pulled B-b folder> [TAG]          → <folder>/<TAG>B5_ITEMS.md
Main transcripts only. K = {4, 8, 16, 32} (the B5 primary set) unless a column says otherwise.
  arm split   Δ = mean(Y_drift − Y_filler) = move_drift − move_filler, move_X = Y_X(k) − Y_X(0) (drift and filler share
              the k = 0 prefix); move_none = Y_none(k) − Y_none(0) (history under a system message WITHOUT the
              instruction: how the history itself leans between the two words).
  headroom    Y_drift(0) − Y_none(0): the instruction's authority before any history.
  overlap     per transcript, word-family counts in the assistant text of its first 32 turns (families fixed before
              counting: DONE = done finished complete completed; READY = ready prepared set); within each item,
              Spearman ρ over the 96 transcripts of the transcript's Δ vs (competing-family − system-family) count.
  template    template index, system + user text.
  depth       Δ at each k."""
import json, re, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D
import phaseb_core as B
sys.stdout.reconfigure(encoding="utf-8")
C = [json.loads(l) for l in open(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl", encoding="utf-8")]
FAM = {"DONE": ("done", "finished", "complete", "completed"), "READY": ("ready", "prepared", "set")}
RX = {w: re.compile(r"\b(" + "|".join(v) + r")\b", re.I) for w, v in FAM.items()}
F = Path(sys.argv[1]); TAG = sys.argv[2] if len(sys.argv) > 2 else "REAL_"
q = np.load(F / f"{TAG}b5_q0.npz")["rows"]; q = q[q[:, 0] < B.WI_TID0]
TR = {t["tid"]: t for t in (json.loads(l) for l in open(F / f"{TAG}b5_transcripts.jsonl", encoding="utf-8")) if "with_instruction" not in t}
Yv = D.y_signed(q[:, 4], q[:, 5], [C[int(i)]["target_sys"] for i in q[:, 1]])
Y = {(int(r[0]), int(r[1]), int(r[2]), int(r[3])): y for r, y in zip(q, Yv)}
DR, FI, NO = (B.B5_CONDS.index(x) for x in ("drift", "filler", "none"))
items = sorted({int(r[1]) for r in q}); tids = sorted(TR); KP = (4, 8, 16, 32); KS = sorted({int(r[3]) for r in q if r[3] > 0})
cnt = {t: {w: len(RX[w].findall(" ".join(x["assistant"] for x in TR[t]["turns"][:32]))) for w in FAM} for t in tids}
words = {t: len(" ".join(x["assistant"] for x in TR[t]["turns"][:32]).split()) for t in tids}
rank = lambda x: np.argsort(np.argsort(x)).astype(float)
rho = lambda a, b: float(np.corrcoef(rank(a), rank(b))[0, 1]) if np.std(a) > 0 and np.std(b) > 0 else float("nan")
m = lambda xs: float(np.mean(xs)) if len(xs) else float("nan")
OUT = []; md = lambda s="": OUT.append(s)
md(f"# B5 per-item breakdown — `{F.name}` — POST-HOC, hypothesis generation only\n")
md("## Arm split + headroom (k ∈ {4, 8, 16, 32}; means over the 96 main transcripts)\n")
md("| item | sys → competing | cell | Δ | move drift | move filler | move none | headroom Y_d(0) − Y_n(0) | Y_drift(0) |\n|---|---|---|---|---|---|---|---|---|")
rows = []
for i in items:
    c = C[i]; dd, mv_d, mv_f, mv_n = [], [], [], []
    for t in tids:
        for k in KP:
            if (t, i, DR, k) not in Y: continue
            dd.append(Y[(t, i, DR, k)] - Y[(t, i, FI, k)]); mv_d.append(Y[(t, i, DR, k)] - Y[(t, i, DR, 0)])
            mv_f.append(Y[(t, i, FI, k)] - Y[(t, i, FI, 0)]); mv_n.append(Y[(t, i, NO, k)] - Y[(t, i, NO, 0)])
    hr = m([Y[(t, i, DR, 0)] - Y[(t, i, NO, 0)] for t in tids]); y0 = m([Y[(t, i, DR, 0)] for t in tids])
    rows.append((i, m(dd), hr))
    md(f"| {c['id']} | {c['target_sys']} → {c['target_usr']} | {c['position']} | {m(dd):+.2f} | {m(mv_d):+.2f} | {m(mv_f):+.2f} | {m(mv_n):+.2f} | {hr:+.2f} | {y0:+.2f} |")
d_, h_ = np.array([r[1] for r in rows]), np.array([r[2] for r in rows])
md(f"\nAcross the 8 items: Spearman ρ(Δ, headroom) = {rho(d_, h_):+.2f} (n = 8, descriptive).")
md("\n## Depth profile — Δ at each k\n\n| item | " + " | ".join(f"k={k}" for k in KS) + " |\n|" + "---|" * (len(KS) + 1))
for i in items:
    md(f"| {C[i]['id']} | " + " | ".join(f"{m([Y[(t, i, DR, k)] - Y[(t, i, FI, k)] for t in tids if (t, i, DR, k) in Y]):+.2f}" for k in KS) + " |")
md("\n## Word overlap (assistant text, first 32 turns)\n")
tot = {w: sum(cnt[t][w] for t in tids) for w in FAM}; W = sum(words.values())
md(f"Family counts over all 96 transcripts ({W:,} words): DONE {tot['DONE']} ({1000 * tot['DONE'] / W:.2f} / 1k words) · "
   f"READY {tot['READY']} ({1000 * tot['READY'] / W:.2f} / 1k words). Transcripts with ≥ 1: DONE "
   f"{sum(cnt[t]['DONE'] > 0 for t in tids)} · READY {sum(cnt[t]['READY'] > 0 for t in tids)} of {len(tids)}.")
md("\nWithin each item, ρ over transcripts of the transcript's Δ (k ∈ {4..32}) vs (competing − system) family count:\n\n| item | ρ |\n|---|---|")
for i in items:
    c = C[i]; dt = np.array([m([Y[(t, i, DR, k)] - Y[(t, i, FI, k)] for k in KP if (t, i, DR, k) in Y]) for t in tids])
    ov = np.array([cnt[t][c["target_usr"]] - cnt[t][c["target_sys"]] for t in tids], float)
    md(f"| {c['id']} | {rho(dt, ov):+.2f} |")
md("\n## Template wording\n\n| item | template | Δ | system | user |\n|---|---|---|---|---|")
for i, dv, _ in sorted(rows, key=lambda r: r[1]):
    c = C[i]; md(f"| {c['id']} | {c['template_idx']} | {dv:+.2f} | {c['system']} | {c['user']} |")
md("\n## By mode (Δ, k ∈ {4..32})\n\n| item | M1 | M3 |\n|---|---|---|")
for i in items:
    md(f"| {C[i]['id']} | " + " | ".join(f"{m([Y[(t, i, DR, k)] - Y[(t, i, FI, k)] for t in tids if TR[t]['mode'] == mo for k in KP if (t, i, DR, k) in Y]):+.2f}" for mo in B.B5_MODES) + " |")
(F / f"{TAG}B5_ITEMS.md").write_text("\n".join(OUT) + "\n", encoding="utf-8"); print("\n".join(OUT))
