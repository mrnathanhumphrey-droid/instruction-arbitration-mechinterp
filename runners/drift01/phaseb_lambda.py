"""HUNT-DRIFT-01 Phase B runner (EXPLORATORY; PLAN_PHASE_B.md 1a660770…, locked). One process, one instance.
  FAKE=1 [SMOKE=1] [PLANT=<name>] PHASEB=a DRIFT_INPUTS=<dir> DRIFT_OUT=<empty dir> DRIFT_RESUME=<sub> DRIFT_RESUME_MANIFEST_SHA=<sha> python phaseb_lambda.py
  REAL=1 PHASEB=a … RATE_PER_H=<$> INSTANCE_T0=<unix s> python phaseb_lambda.py
B-a (resume, no generation): pins → model → BIT-CHECK → RESUME (the full run's frozen transcripts, verified) → slot +
span checks → REPEAT CHECK (the logits-kept branch, bitwise; its gap to the full run's readout path REPORTED) → B4
(720 × 8 arms, depth 0) → B1 full (720 × 7, depth 0, plant log-probs kept) → B3 (elicited choice, k ∈ {4, 16, 32}) →
B1 panel (frozen transcripts × 8 items × K_Q1 × 7, plant log-probs kept; PROJECTION after 2 transcripts → exit 6).
drift01_lambda.py (the full run's runner, d6a0ee77…) is NOT changed; the model / brancher / bit-check / RESUME code
below is copied from it verbatim, with lp_span / probe_span added (the same pass, every logit kept). B-b (fresh
generation, B5): PHASEB=b — fresh seeds 7101201–08, M1 + M3, 96 transcripts + the 12 with-instruction transcripts
(token ids saved), Q0 drift / filler / none on the 8 panel items, every prefix prefilled in ONE pass and probed in
descending k with the cache cropped between probes (Amendment 3 A3.3; a 4,096-token grid from 0 only on OOM, logged).
PHASEB=c (Amendment 3, 34a16542…, locked): A3.1 the matched skeleton (720 × 19 fresh single-pass rows, skeleton
checks on every row, repeat check) + A3.2 the chunk test (24 transcripts × 2 items × K_Q1 × 7 under the full run's
and B-a's cache chunking, against both runs' own readouts; the resume folder carries q1 + B-a's b1_panel).
PHASEB=d (Amendment 4, 569919b6…, locked; no generation): the 96 frozen B-b main transcripts (resume folder = B-b's
b5_transcripts + manifest + b5_q0, verified) → S7 REPRO: the 8 B-b items × drift / filler / none under this code vs
B-b's b5_q0 (bitwise count reported; max |Δ| > REPRO_TOL stops) → repeat check → projection → the 80 fresh items
(fresh_items.json) × drift / filler / none / prose (pg1228_prose.txt, token-matched every row), single pass (A3.3).
PHASEB=e (Amendment 5, 9b92498d…, locked; no generation): D's path with A5's items and arms — the same 96 frozen
transcripts (resume folder = B-b's b5_transcripts + manifest + A4's b6_q0, verified) → REPRO GATE: the first 8 A4
fresh items × drift / filler / prose vs A4's b6_q0 → repeat check → projection → the 120 A5 items (a5_items.json) ×
drift / filler / prose. Outputs a5_*; cond indices are B6_CONDS' (prose = 3), so rows compare key for key with b6_q0.
PHASEB=f (Amendment 6, 1e6de4f1…, locked; no transcripts, no generation): the 120 A5 items as probes × 8 demonstration
draws (a6_demos.json) × obey / defer / agree / defy (a6_core.py) × n ∈ {1, 2, 4, 8}, + the n = 0 anchor per probe →
row checks on EVERY probe × draw (arms token-identical but for the DONE / READY swaps) → repeat check → projection →
rows: one prefill per probe × draw × arm, probes in descending n. Outputs a6_q0, a6_rowcheck, a6_gap_report. a6_q0 also
carries lpD_ns / lpR_ns (the no-space tokens the demo replies use) — REPORTED ONLY, post-lock (LOG 2026-11-05).
PHASEB=g (Amendment 7, a66ef98b…, locked; no transcripts, no generation): F's design on the 120 A7 items (a7_items.json,
a7_demos.json), every row read off ONE prefill with two probes per crop — C (the item's user turn, A6's probe) and N (the
same turn asking for the system word; a7_core.py) — + both anchors per probe → row checks (A6's + the N check) on EVERY
probe × draw → repeat check → projection → rows. Outputs a7_q0 (column "probe": 0 = C, 1 = N), a7_rowcheck, a7_gap_report.
PHASEB=h (Amendment 8, 6bc527cd…, locked; no generation): the frozen B-b main transcripts (resume as E, verified) form
M1 / M3 pairs (same persona × temperature × seed); turn 1 spliced 2 × 2 (user turn from M1 / M3 × assistant turn from
M1 / M3, generated ids as saved), drift + token-matched filler (keyed by the user turn's transcript), k = 1, × the 120
A8 items (a8_items.json); + the re-read: the first 8 A5 items × every transcript, unspliced, drift / filler at k = 1
(A5's q0_rows). Row checks on EVERY pair × cell × item (turns parsed back to their sources; filler lengths = drift's;
unspliced cells = A5's q0_rows) → repeat check → projection → rows. Outputs a8_q0, a8_reread, a8_rowcheck, a8_gap_report.
PHASEB=i (Amendment 10, cec4ef76…, locked; no transcripts, no generation): G's items, draws, arms and n, probe C only,
under four renderings of the demos (a10_core.py: native / headers / quoted / stated) + the n = 0 anchor per probe → row
checks on EVERY probe × draw × rendering (stop) → REPRO GATE: native rows of the first 8 probes vs A7's locked a7_q0 (C)
within 0.05 nats (stop) → repeat check → projection → rows. Nested renderings: one prefill, descending-n crop; quoted: one
prefill per n. Outputs a10_q0 (column "render"; anchors render −1), a10_repro, a10_rowcheck, a10_gap_report.
PHASEB=j (Amendment 11, 9c4c627f…, locked; no generation): the 96 frozen B-b main transcripts (resume folder = B-b's
b5_transcripts + manifest + A5's a5_q0, verified; REAL a5_q0 = the locked A5 run's) → REPRO GATE: the first 8 A5 items ×
drift / filler / prose vs A5's a5_q0 (stop above 0.05 nats) → repeat check → projection → the 120 A5 items × the ONE new
arm, diverse filler (a11_core.py: natural text, each turn from a different book of the 8-book pool, token-matched every
row), single pass (A3.3). Outputs a11_q0 (cond index 4 = "diverse"), a11_repro, a11_gap_report, a11_diverse (per
transcript: tokens, the book of every turn, target-family counts per book).
Exit: 0 done · 2 a pin / guard refused · 3 a STOP rule (bit-check, freeze, slot, span, repeat, repro, prose) · 5 watchdog · 6 projection."""
import hashlib, json, os, sys, time
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D
import phaseb_core as B

FAKE, REAL, SMOKE = os.environ.get("FAKE") == "1", os.environ.get("REAL") == "1", os.environ.get("SMOKE") == "1"
PLANT = os.environ.get("PLANT", "")
if FAKE == REAL: sys.exit("exactly one of FAKE=1 / REAL=1")
if PLANT and not FAKE: sys.exit("PLANT is FAKE-only")
PHASE = os.environ.get("PHASEB", "")
if PHASE not in ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j"): sys.exit(f"PHASEB={PHASE!r}: 'a' (B1, B3, B4), 'b' (B5, fresh generation), 'c' (Amendment 3), 'd' (Amendment 4), 'e' (Amendment 5), 'f' (Amendment 6), 'g' (Amendment 7), 'h' (Amendment 8), 'i' (Amendment 10) or 'j' (Amendment 11)")
TAG = ("FAKE_" if FAKE else "REAL_") + ("SMOKE_" if SMOKE else "")
INP, OUT = Path(os.environ["DRIFT_INPUTS"]), Path(os.environ["DRIFT_OUT"])
OUT.mkdir(parents=True, exist_ok=True)
if any(p for p in OUT.iterdir() if not p.name.startswith(".")):     # dot-files = the watchdog's key, never outputs
    sys.exit(f"{OUT} is not empty (no clobber)")
WATCH = float(os.environ.get("WATCH_USD", "22"))
if not 0 < WATCH <= 60: sys.exit(f"WATCH_USD {WATCH} outside (0, 60]")
RATE = float(os.environ.get("RATE_PER_H", "0" if FAKE else "nan"))
if PHASE in ("a", "c", "d", "e", "h", "j") and not os.environ.get("DRIFT_RESUME"): sys.exit("B-a / C / D / E / H / J run on frozen transcripts only: DRIFT_RESUME is required")
if PHASE in ("b", "f", "g", "i") and os.environ.get("DRIFT_RESUME"): sys.exit("B-b / F / G / I read no frozen transcripts: DRIFT_RESUME is not used")
T0 = float(os.environ.get("INSTANCE_T0", time.time()))
if REAL and not np.isfinite(RATE): sys.exit("REAL needs RATE_PER_H (from the Lambda API)")
LOG = []
def say(*a):
    s = " ".join(str(x) for x in a); LOG.append(s); print("[DB]", s, flush=True)
def spend(): return (time.time() - T0) / 3600 * RATE
class Watchdog(Exception): pass
def watch():
    if spend() >= WATCH: raise Watchdog(f"spend ${spend():.2f} ≥ ${WATCH}")
def stop(code, why):
    (OUT / f"{TAG}STOP.txt").write_text(why + "\n", encoding="utf-8"); say("STOP", code, why)
    (OUT / f"{TAG}ledger.json").write_text(json.dumps({"rate_per_h": RATE, "t0": T0, "elapsed_h": (time.time() - T0) / 3600,
                                                        "spend_usd": spend(), "status": f"STOP {code}: {why}"}, indent=1), encoding="utf-8")
    flush_log(); sys.exit(code)
def flush_log(): (OUT / f"{TAG}B_run.log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

# ------------------------------------------------------------------ pins
PINS = {"panel.json": "718732502b66acdb46f3f85700cbb659be5f6da1b2bfe818ba1f53c000fcd963",
        "intention_forms.json": "4e1f6b17425e4f1b18ede2ec9d40ccb2c7ec577ade18f8d7be2a6918d3ef5877",
        "word_pool_drift01.txt": "c26f8dd661ece2026df0dc57a2fa96541adf3e8ece92c5c08d53e8ee944d2aae",
        "stimuli_contested.jsonl": "d4145f1add05ec293d210ce40fe2ad3b858cc6abc2a4b86761e6f04573e629b4"}
CORE_SHA = "5f06a0916ba9c63d"          # the full run's core, unchanged
PHB_SHA = os.environ.get("PHASEB_CORE_SHA16", "")   # the launcher passes phaseb_core.py's recorded sha (16 hex)
if PHASE in ("d", "e"): PINS.update({"fresh_items.json": "f30d16a8b0055bc2ca8958cc38a71a997799bfb1a2524c970d9156f54b91c46f",
                                     "pg1228_prose.txt": "164cc858001f47bd0cab0c7a6c3d39292386d5294edaf4c28a239972754f0ec3"})
if PHASE in ("e", "f", "h"): PINS["a5_items.json"] = "8b1a1e32d360ff2da2fff21750807bab669aeae7f235c8e241b566b1b120ebf7"
if PHASE == "h": PINS["a8_items.json"] = "424638fd4cacf1740a5f1ca0b919013bcd7c832d7d772db07f05296e2e861769"
if PHASE == "f": PINS["a6_demos.json"] = "6d4348c7fc902a7d0865db05abfd05a7193bba94e0afe0494734d75d649a7cca"
if PHASE in ("g", "i"): PINS.update({"a7_items.json": "28fb1335d5492fc92437bfead62615ceafe6976b9a91485b57f926c92e8d4f89",
                                      "a7_demos.json": "376b156fe6a88271f41ecf453f4a67ee71832d54e0b13d9cd37d518b0d5d6420"})
if PHASE == "i" and REAL: PINS["REAL_a7_q0.npz"] = "8f9e4f83d963ff75ae72ba3ee68c6ec42922b10b9c3e7d54479970d74bab742f"   # A7's locked run (phaseBg_20261107T160254Z): the repro-gate reference
if PHASE == "j": PINS.update({"a5_items.json": "8b1a1e32d360ff2da2fff21750807bab669aeae7f235c8e241b566b1b120ebf7",
                               "pg1228_prose.txt": "164cc858001f47bd0cab0c7a6c3d39292386d5294edaf4c28a239972754f0ec3"})
A5_REAL_Q0 = "012f407ea79e668bbc25d6a283a58797978ffa6b21ff6905cf8297965d0fff04"   # A5's locked run (phaseBe_20261105T050023Z): the A11 repro reference + old arms
A11CORE_SHA = "f719bc2fda1118db"           # a11_core.py, recorded at build
REPRO_TOL11 = 0.05                         # A11.1 repro gate (A5's)
A6CORE_SHA = "3f69349e0246554c"          # a6_core.py, recorded at build
A7CORE_SHA = "a6b630593d5594bd"            # a7_core.py, recorded at build
A10CORE_SHA = "5c421fbefa422d75"           # a10_core.py, recorded at build
REPRO_TOL10 = 0.05                         # A10.1 repro gate (A5's)
A5_CONDS = ("drift", "filler", "prose")                  # A5.1: "none" dropped
for n, h in PINS.items():
    if sha(INP / n) != h: stop(2, f"{n} hash mismatch")
if sha(HERE / "drift01_core.py")[:16] != CORE_SHA: stop(2, "drift01_core.py is not the recorded piece-2 core")
if REAL and sha(HERE / "phaseb_core.py")[:16] != PHB_SHA: stop(2, "phaseb_core.py is not the recorded Phase-B core")
if PHASE in ("f", "g", "i"):
    if sha(HERE / "a6_core.py")[:16] != A6CORE_SHA: stop(2, "a6_core.py is not the recorded A6 core")
    import a6_core as A6
if PHASE == "i":
    if sha(HERE / "a10_core.py")[:16] != A10CORE_SHA: stop(2, "a10_core.py is not the recorded A10 core")
    import a10_core as A10
    if not (INP / (("FAKE_" if FAKE else "REAL_") + "a7_q0.npz")).exists(): stop(2, "A10 repro gate: A7's a7_q0.npz is not in the inputs")
if PHASE == "j":
    if sha(HERE / "a11_core.py")[:16] != A11CORE_SHA: stop(2, "a11_core.py is not the recorded A11 core")
    import a11_core as A11
    for n, h in A11.TEXT_SHA.items():
        if not (INP / n).is_file() or sha(INP / n) != h: stop(2, f"{n} hash mismatch")
if PHASE == "g":
    if sha(HERE / "a7_core.py")[:16] != A7CORE_SHA: stop(2, "a7_core.py is not the recorded A7 core")
    import a7_core as A7
if REAL:
    for n, h in json.loads((INP / "pilot_pins.json").read_text(encoding="utf-8")).items():
        if sha(INP / n) != h: stop(2, f"{n} hash mismatch")
C = [json.loads(l) for l in open(INP / "stimuli_contested.jsonl", encoding="utf-8")]
PANEL = [p["item"] for p in json.loads((INP / "panel.json").read_text(encoding="utf-8"))["panel"]]
PANEL = [PANEL[j] for j in range(12) if j % 3 in (0, 1)]       # Amendment 2 A2.2: the first two of each cell → 8 items
FORMS = json.loads((INP / "intention_forms.json").read_text(encoding="utf-8"))["forms"]
POOL = (INP / "word_pool_drift01.txt").read_text(encoding="utf-8").split()
say("pins OK", TAG, "smoke" if SMOKE else "full", f"phase B-{PHASE}")

# ------------------------------------------------------------------ design = the full run's (RESUME checks it)
MODES, TEMPS = ("M1", "M2", "M3"), (0.7, 1.0)
PERS = tuple(D.PERSONAS)
SEEDS = D.GEN_SEEDS[:2] if SMOKE else D.GEN_SEEDS
NTURN = 8 if SMOKE else 32
def gseed(*parts):
    return int(hashlib.sha256(repr(parts).encode()).hexdigest()[:15], 16)
KQ0 = tuple(k for k in D.K_Q0 if k <= NTURN); KQ1 = tuple(k for k in D.K_Q1 if k <= NTURN); KB3 = tuple(k for k in B.K_B3 if k <= NTURN)
if SMOKE: MODES, TEMPS, PERS, PANEL = ("M1", "M2"), (1.0,), ("P-none", "P-curious"), PANEL[:2]
FULL_ITEMS = list(range(10)) if SMOKE else list(range(len(C)))
CELLS = [(m, p, t, s) for m in MODES for p in PERS for t in TEMPS for s in SEEDS]   # transcript id = index
PROJ_UNITS = 2

# ------------------------------------------------------------------ model + tokenizer (copied from drift01_lambda.py; + spans)
class FakeTok:
    """Word-level stand-in: specials as in Llama, '\\n\\n' = 271, pool words 1000+, other words hashed. Special strings
    and blank-line runs are their own tokens, so a segment-built id list = the full-text tokenization."""
    SPEC = {"<|begin_of_text|>": 128000, "<|start_header_id|>": 128006, "<|end_header_id|>": 128007, "<|eot_id|>": 128009}
    def __init__(self, pool):
        import re
        self.re = re.compile("|".join(map(re.escape, self.SPEC)) + r"|\n+|[A-Za-z0-9']+|(?!<\|)\S")   # words; punctuation alone
        self.w = {w: 1000 + i for i, w in enumerate(pool)}; self.inv = {v: k for k, v in self.w.items()}
    def enc(self, s):
        out = []
        for m in self.re.findall(s):
            if m in self.SPEC: out.append(self.SPEC[m])
            elif m.startswith("\n"): out.append(271)
            else: out.append(self.w.get(m.lower(), 30000 + int(hashlib.md5(m.encode()).hexdigest(), 16) % 90000))
        return out
    def dec(self, ids): return " ".join(self.inv.get(i, f"w{i}") for i in ids)

def _lsm(z):
    z = z - z.max(-1, keepdims=True); return z - np.log(np.exp(z).sum(-1, keepdims=True))

class FakeModel:
    """Deterministic toy (d = 16), as in drift01_lambda.py. lp_all = the log-softmax at EVERY position (the B1 pass)."""
    d, V = 16, 128256
    def __init__(self, pool_ids, eot):
        g = np.random.default_rng(0); self.E = g.normal(0, 1, (self.V, self.d)).astype(np.float32)
        self.W = g.normal(0, 1, (self.V, self.d)).astype(np.float32); self.sysdir = g.normal(0, 1, self.d).astype(np.float32)
        self.pool_ids, self.eot = np.array(pool_ids), eot
    def hidden(self, ids):
        ids = np.asarray(ids); X = self.E[ids]; H = X + 0.3 * np.cumsum(X, 0) / np.arange(1, len(ids) + 1)[:, None]
        cut = np.where(ids == 128009)[0]; c = cut[0] if len(cut) else len(ids)
        H[:c] += self.sysdir
        return H
    def lp(self, ids):
        z = self.W @ self.hidden(ids)[-1].astype(np.float64); z -= z.max(); return z - np.log(np.exp(z).sum())
    lp_pilot = lp
    def lp_rows(self, ids, n):
        """log-softmax at the LAST n positions (rows), float64 — the last row = lp(ids)."""
        H = self.hidden(ids)[-n:].astype(np.float64); return _lsm(H @ self.W.T.astype(np.float64))
    def lp_span(self, ids):
        R = self.lp_rows(ids, len(ids)); tok = np.r_[np.nan, R[np.arange(len(ids) - 1), np.asarray(ids[1:])]]
        return R[-1], tok
    def mem_gb(self): return 0.0
    oomed = False
    def generate(self, contexts, temp, seed, maxnew):          # copied from drift01_lambda.py
        if PLANT == "oom" and len(contexts) > 1 and not FakeModel.oomed:
            FakeModel.oomed = True; raise RuntimeError("CUDA out of memory. (planted)")
        out = []
        for b, ctx in enumerate(contexts):
            rng = np.random.default_rng([seed, b]); n = int(rng.integers(3, maxnew + 1)); ids = []
            for t in range(n):
                z = self.W[self.pool_ids] @ self.hidden(list(ctx[-64:]) + ids)[-1] / temp
                p = np.exp(z - z.max()); p /= p.sum(); ids.append(int(rng.choice(self.pool_ids, p=p)))
            out.append((ids, False))
        return out

class FakeBrancher:
    def __init__(self, m): self.m, self.ids = m, []
    def extend(self, chunk): self.ids += list(chunk)
    def probe(self, suffix):
        lp = self.m.lp(self.ids + list(suffix))
        if PLANT == "nondeterm": FakeBrancher.calls += 1; lp = lp + 1e-9 * FakeBrancher.calls
        return lp
    def probe_h(self, suffix, layers):
        """A9: probe + a stand-in 'residual after layer l' at the readout position (the toy's last hidden row, scaled per l)."""
        lp = self.probe(suffix); h = self.m.hidden(self.ids + list(suffix))[-1]
        return lp, np.stack([h * (1 + 0.05 * l) for l in layers]).astype(np.float16)
    def probe_span(self, suffix):
        """(readout lp, token log-probs aligned to the suffix; [0] = NaN) — one pass, every suffix logit kept."""
        s = list(suffix); R = self.m.lp_rows(self.ids + s, len(s))
        tok = np.r_[np.nan, R[np.arange(len(s) - 1), np.asarray(s[1:])]]; last = R[-1]
        if PLANT == "nondeterm": FakeBrancher.calls += 1; last = last + 1e-9 * FakeBrancher.calls
        return last, tok
    calls = 0
    def pos(self): return len(self.ids)
    grid_used = 0
    def prefill(self, ids):
        """A3.3: the whole prefix in ONE pass (PLANT prefilloom forces the logged 4,096-grid fallback)."""
        if PLANT == "prefilloom": FakeBrancher.grid_used += 1
        self.ids = list(ids)
    def crop_to(self, n): self.ids = self.ids[:n]

def load():
    if FAKE:
        tk = FakeTok(POOL); return tk.enc, tk.dec, FakeModel([tk.w[w] for w in POOL[:400]], 128009), {"FAKE": True}
    import torch, transformers, subprocess
    from transformers import AutoModelForCausalLM, AutoTokenizer
    assert torch.__version__.startswith("2.7.0") and transformers.__version__ == "4.46.0", (torch.__version__, transformers.__version__)
    torch.use_deterministic_algorithms(True); torch.backends.cudnn.benchmark = False
    nm, mem = torch.cuda.get_device_name(0), torch.cuda.get_device_properties(0).total_memory
    if not ("H100" in nm and "PCIe" in nm and mem > 79e9): stop(2, f"GPU is {nm}; the hunt pins H100 80 GB PCIe")
    tok = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", revision=D.REV)
    mdl = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", revision=D.REV, torch_dtype=torch.bfloat16,
                                               attn_implementation="sdpa", device_map={"": 0}).eval()
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    ver = {"torch": torch.__version__, "transformers": transformers.__version__, "cuda": torch.version.cuda, "gpu": nm,
           "nvidia_smi": subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                                        capture_output=True, text=True).stdout.strip(), "attn": "sdpa", "revision": D.REV,
           "cublas_ws": os.environ.get("CUBLAS_WORKSPACE_CONFIG")}
    return enc, (lambda ids: tok.decode(ids)), RealModel(mdl, tok), ver

def _span_out(logits, ids):
    """log-softmax of every row (fp32, on the GPU) → (last row as float64 numpy, token log-probs [NaN, lp(ids[1]), …])."""
    import torch
    L = torch.log_softmax(logits.float(), -1); t = torch.tensor(ids[1:], device=L.device)
    tok = L[:-1].gather(1, t[:, None])[:, 0].cpu().numpy().astype(np.float64)
    return L[-1].cpu().numpy().astype(np.float64), np.r_[np.nan, tok]

class RealModel:
    def __init__(self, mdl, tok): self.mdl, self.tok = mdl, tok
    def lp(self, ids):
        import torch
        with torch.inference_mode():
            out = self.mdl(input_ids=torch.tensor([ids], device="cuda:0"), use_cache=False, num_logits_to_keep=1)
        return torch.log_softmax(out.logits[0, -1].float(), -1).cpu().numpy().astype(np.float64)
    def lp_pilot(self, ids):
        """The pilot's EXACT call (pilot_lambda.forward): full logits, hidden states on, no cache — for the bit-check."""
        import torch
        with torch.inference_mode():
            out = self.mdl(input_ids=torch.tensor([ids], device="cuda:0"), output_hidden_states=True, use_cache=False)
        return torch.log_softmax(out.logits[0, -1].float(), -1).cpu().numpy().astype(np.float64)
    def lp_span(self, ids):
        """One fresh pass, no cache, EVERY logit kept: (readout lp, per-token log-probs) — B1's same-pass read."""
        import torch
        with torch.inference_mode():
            out = self.mdl(input_ids=torch.tensor([ids], device="cuda:0"), use_cache=False)
            return _span_out(out.logits[0], list(ids))
    def mem_gb(self):
        import torch
        return torch.cuda.max_memory_allocated() / 2**30
    STOPS = (128001, 128008, 128009)        # copied from drift01_lambda.py
    def generate(self, contexts, temp, seed, maxnew):
        import torch
        eot = self.STOPS[-1]; L = max(map(len, contexts))
        ids = torch.tensor([[eot] * (L - len(c)) + list(c) for c in contexts], device="cuda:0")
        att = torch.tensor([[0] * (L - len(c)) + [1] * len(c) for c in contexts], device="cuda:0")
        torch.manual_seed(seed); torch.use_deterministic_algorithms(False)
        try:
            with torch.inference_mode():
                g = self.mdl.generate(input_ids=ids, attention_mask=att, do_sample=True, temperature=temp, top_p=1.0, top_k=0,
                                      max_new_tokens=maxnew, eos_token_id=list(self.STOPS), pad_token_id=eot)
        finally:
            torch.use_deterministic_algorithms(True)
        out = []
        for row in g[:, L:].tolist():
            cut = next((q for q, x in enumerate(row) if x in self.STOPS), None)
            out.append((row if cut is None else row[:cut], cut is None))
        return out

class RealBrancher:
    """One sequence, one DynamicCache: extend the prefix in chunks; probe = append the suffix, read the last logits,
    crop the cache back. probe_span = the same with every suffix logit kept."""
    def __init__(self, m):
        from transformers import DynamicCache
        self.m, self.cache, self.n = m, DynamicCache(), 0
    def extend(self, chunk, step=4096):
        import torch
        for i in range(0, len(chunk), step):
            c = list(chunk[i:i + step])
            with torch.inference_mode():
                self.m.mdl(input_ids=torch.tensor([c], device="cuda:0"), past_key_values=self.cache, use_cache=True, num_logits_to_keep=1)
            self.n += len(c)
    def probe(self, suffix):
        import torch
        with torch.inference_mode():
            out = self.m.mdl(input_ids=torch.tensor([list(suffix)], device="cuda:0"), past_key_values=self.cache, use_cache=True, num_logits_to_keep=1)
        self.cache.crop(self.n)
        return torch.log_softmax(out.logits[0, -1].float(), -1).cpu().numpy().astype(np.float64)
    def probe_h(self, suffix, layers):
        """A9: probe + the residual stream after each layer in `layers` at the readout position (the suffix's last token),
        fp16. The same forward pass as probe() with output_hidden_states on (hidden_states[l] = after decoder layer l)."""
        import torch
        with torch.inference_mode():
            out = self.m.mdl(input_ids=torch.tensor([list(suffix)], device="cuda:0"), past_key_values=self.cache, use_cache=True,
                             num_logits_to_keep=1, output_hidden_states=True)
            H = torch.stack([out.hidden_states[l][0, -1] for l in layers]).to(torch.float16).cpu().numpy()
        self.cache.crop(self.n)
        return torch.log_softmax(out.logits[0, -1].float(), -1).cpu().numpy().astype(np.float64), H
    def probe_span(self, suffix):
        import torch
        with torch.inference_mode():
            out = self.m.mdl(input_ids=torch.tensor([list(suffix)], device="cuda:0"), past_key_values=self.cache, use_cache=True)
            r = _span_out(out.logits[0], list(suffix))
        self.cache.crop(self.n)
        return r
    def pos(self): return self.n
    grid_used = 0
    def prefill(self, ids):
        """A3.3: the whole prefix in ONE forward pass; on CUDA OOM only, a fixed 4,096-token grid from position 0
        (never boundaries that depend on k), counted in grid_used and logged."""
        import torch
        try:
            with torch.inference_mode():
                self.m.mdl(input_ids=torch.tensor([list(ids)], device="cuda:0"), past_key_values=self.cache, use_cache=True, num_logits_to_keep=1)
            self.n = len(ids)
        except RuntimeError as e:
            if "out of memory" not in str(e).lower(): raise
            from transformers import DynamicCache
            torch.cuda.empty_cache(); self.cache, self.n = DynamicCache(), 0; RealBrancher.grid_used += 1
            self.extend(ids, step=4096)
    def crop_to(self, n): self.cache.crop(n); self.n = n

if PLANT == "a3order":                     # FAKE plant: the planted turn moved FIRST (the skeleton check must stop it)
    _a3t = B.a3_turns
    B.a3_turns = lambda *a: (lambda t: t if a[3] == "inert" else [t[-1]] + t[:-1])(_a3t(*a))
enc, dec, M, VER = load()
Brancher = FakeBrancher if FAKE else RealBrancher
TD, TR = enc(" DONE")[-1], enc(" READY")[-1]
TD0, TR0 = enc("DONE")[-1], enc("READY")[-1]   # A6 reported-only (post-lock, LOG 2026-11-05): the no-space tokens the demo replies use
WORDS = B.b3_words(enc)
say("model loaded", json.dumps(VER))

try:
    # -------------------------------------------------------------- BIT-CHECK (as the full run) — before anything else
    ref = np.load(INP / ("FAKE_pilot_lp.npz" if FAKE else "pilot_lp_open.npz"))
    key = {tuple(k): i for i, k in enumerate(ref["lp_key"].tolist())}
    bad = []
    for i in PANEL:
        ids, cut = D.context(enc, D.system_text(C[i]["system"], ""), [], 0)
        lp = M.lp_pilot(D.row(ids, cut, D.probe_suffix(enc, C[i]["user"]), 0))
        mine, theirs = np.array([lp[TD], lp[TR]], np.float32), ref["lp"][key[(0, i, 0)]]
        if PLANT == "bitcheck" and i == PANEL[0]: mine = mine.copy(); mine.view(np.uint32)[0] ^= 1
        if mine.tobytes() != np.asarray(theirs, np.float32).tobytes(): bad.append(C[i]["id"])
    if bad: stop(3, f"BIT-CHECK FAILED vs the pilot ORIG lp: {bad}")
    say("bit-check PASS", len(PANEL), "items bit-for-bit")

    if PHASE in ("a", "c"):
        # -------------------------------------------------------------- RESUME (copied): the frozen transcripts, verified
        R = INP / os.environ["DRIFT_RESUME"]; mf = R / f"{TAG}transcripts_manifest.json"
        if sha(mf) != os.environ.get("DRIFT_RESUME_MANIFEST_SHA", ""): stop(2, "RESUME: transcripts manifest is not the pinned one")
        man0 = json.loads(mf.read_text(encoding="utf-8"))
        if [tuple(c) for c in man0["cells"]] != CELLS: stop(2, "RESUME: the frozen transcripts are a different design")
        Zr = np.load(R / f"{TAG}transcripts.npz"); flat = {}
        for q in range(len(Zr["tid"])): flat.setdefault(int(Zr["tid"][q]), []).append(Zr["ids"][Zr["off"][q]:Zr["off"][q + 1]].tolist())
        T = {t: list(zip(v[0::2], v[1::2])) for t, v in flat.items()}
        if PLANT == "resumetamper": u, a = T[0][0]; T[0][0] = (u, a[:-1] + [a[-1] + 1])
        probs = D.verify_frozen(T, man0["sha"])
        if probs: stop(3, "RESUME FREEZE: " + "; ".join(probs[:5]))
        say(f"RESUMED: {len(T)} frozen transcripts loaded + verified (manifest {sha(mf)[:16]})")
        FR = {x: np.load(R / f"{TAG}{x}.npz")["rows"] for x in ("q1", "q1_full", "b1_panel") if (R / f"{TAG}{x}.npz").exists()}

    if PHASE == "a":
        # -------------------------------------------------------------- slot + span checks (every row the run will read)
        for i in sorted(set(PANEL) | set(FULL_ITEMS)):
            for cond in D.Q1_CONDS:
                kk = (i, D.Q1_CONDS.index(cond)); b = D.q1_block(enc, POOL, C[i], FORMS, cond, kk)
                if D.q1_slot_of(enc, C[i], b) != D.SLOT[cond]: stop(3, f"Q1 plant not in its declared slot: {C[i]['id']} {cond}")
                lo, hi = B.plant_span(enc, b, cond)
                if PLANT == "spanoff" and cond == "asst_int": lo += 1
                if b[lo:hi] != B.plant_ids(enc, POOL, C[i], FORMS, cond, kk): stop(3, f"B1 plant span is not the plant: {C[i]['id']} {cond}")
        for i in FULL_ITEMS:
            for arm in B.B4_ARMS:
                ids = B.b4_row(enc, POOL, C[i], FORMS, arm, i)
                want = enc("user" if arm.startswith("user") else "ipython")
                if PLANT == "wrongslot" and arm == "tool_quoted_imp": want = enc("user")
                T_ = {enc(" " + C[i]["target_usr"])[-1], enc(C[i]["target_usr"])[-1]}
                hit = [r for r, lo, hi in B.content_spans(enc, ids) if T_ & set(ids[lo:hi])]
                if hit != [want]: stop(3, f"B4 plant not in its declared slot: {C[i]['id']} {arm}")
        say("slot + span checks OK (Q1 panel + full, B4)")

        # -------------------------------------------------------------- REPEAT CHECK (stop) + logits-kept GAP (reported)
        rng = np.random.default_rng(D.check_seed(D.SEED_BOOT)); NCHK = 6 if SMOKE else 48; rep_bad, gaps = [], []
        for q in range(NCHK):
            t = int(rng.integers(0, len(CELLS))); i = PANEL[int(rng.integers(0, len(PANEL)))]
            ks = [k for k in KQ1 if k <= len(T[t])]; k = ks[int(rng.integers(0, len(ks)))]; c1 = D.Q1_CONDS[int(rng.integers(0, 7))]
            ids, cut = D.context(enc, D.system_text(C[i]["system"], D.PERSONAS[CELLS[t][1]]), T[t], k)
            blk = D.q1_block(enc, POOL, C[i], FORMS, c1, (i, D.Q1_CONDS.index(c1))); out = []
            for _ in range(2):
                br = Brancher(M); br.extend(ids[:cut[k]]); out.append(br.probe_span(blk))
            br = Brancher(M); br.extend(ids[:cut[k]]); one = br.probe(blk)
            if np.r_[out[0][0], out[0][1]].tobytes() != np.r_[out[1][0], out[1][1]].tobytes(): rep_bad.append((t, C[i]["id"], c1, k))
            gaps.append(float(max(abs(out[0][0][TD] - one[TD]), abs(out[0][0][TR] - one[TR]))))
        GAP = {"n": NCHK, "what": "probe_span (every logit kept) vs probe (num_logits_to_keep=1), same branched prefix, readout pair",
               "max": max(gaps), "median": float(np.median(gaps)), "rows": gaps}
        (OUT / f"{TAG}B_gap_report.json").write_text(json.dumps(GAP, indent=1), encoding="utf-8")
        if rep_bad: stop(3, f"REPEAT CHECK FAILED: logits-kept branch not bitwise reproducible: {rep_bad[:5]}")
        say(f"repeat check PASS ({NCHK} × 2, bitwise); logits-kept vs readout path (reported): max {GAP['max']:.4f} median {GAP['median']:.4f} nats")

        # -------------------------------------------------------------- B4: quoted vs issued, user + tool slot, depth 0
        R4 = []
        for i in FULL_ITEMS:
            watch()
            for a, arm in enumerate(B.B4_ARMS):
                ids = B.b4_row(enc, POOL, C[i], FORMS, arm, i); lp = M.lp(ids)
                R4.append((i, a, lp[TD], lp[TR], B.target_distance(enc, C[i], ids)))
        np.savez(OUT / f"{TAG}b4.npz", rows=np.array(R4, np.float64), cols=np.array(["item", "arm", "lpD", "lpR", "dist_tokens"]), arms=np.array(B.B4_ARMS))
        say(f"B4: {len(FULL_ITEMS)} items × {len(B.B4_ARMS)} arms, spend ${spend():.2f}")

        # -------------------------------------------------------------- B1 full battery: same pass = readout + plant log-probs
        R1F = []
        for i in FULL_ITEMS:
            watch(); head = D.head(enc, D.system_text(C[i]["system"], ""))
            for c, c1 in enumerate(D.Q1_CONDS):
                blk = D.q1_block(enc, POOL, C[i], FORMS, c1, (i, c)); lo, hi = B.plant_span(enc, blk, c1)
                last, tok = M.lp_span(head + blk); s = tok[len(head) + lo:len(head) + hi]
                R1F.append((i, c, last[TD], last[TR], s.sum(), hi - lo))
        R1F = np.array(R1F, np.float64)
        np.savez(OUT / f"{TAG}b1_full.npz", rows=R1F, cols=np.array(["item", "cond", "lpD", "lpR", "plant_lp_sum", "plant_ntok"]))
        if "q1_full" in FR:
            f = {(int(r[0]), int(r[1])): r[2:4] for r in FR["q1_full"]}
            g = [float(np.abs(r[2:4] - f[(int(r[0]), int(r[1]))]).max()) for r in R1F if (int(r[0]), int(r[1])) in f]
            say(f"B1 full vs the full run's q1_full readouts (reported): n {len(g)}, max |Δ| {max(g):.4f}, median {np.median(g):.4f} nats")
        say(f"B1 full: {len(FULL_ITEMS)} items × 7, spend ${spend():.2f}")

        # -------------------------------------------------------------- B3: elicited choice, ON (sampled) vs OFF (planted)
        R3 = []
        for t, p in T.items():
            watch(); m, pe, te, s = CELLS[t]
            ids, cut = D.context(enc, D.PERSONAS[pe], p, max(KB3)); br = Brancher(M)
            for k in KB3:
                if k not in cut: continue
                br.extend(ids[br.pos():cut[k]]); lp = br.probe(B.b3_ask(enc))
                lq = lp
                if FAKE: lq = lp.copy(); lq[list(WORDS)] = lp.max() + 1.0   # FAKE only: the toy never says DONE / READY → lift them so both branches run
                tok = B.sample_token(lq, te, gseed(s, m, te, k, "B3"))
                row = [t, k, tok, lp[tok], lp[TD], lp[TR]]
                if tok in WORDS:
                    w, other_id = WORDS[tok]; opp = "READY" if w == "DONE" else "DONE"
                    if PLANT == "b3same": other_id = tok
                    s_on, s_off = B.b3_arm(enc, tok, opp), B.b3_arm(enc, other_id, w)
                    a_on, a_off = (B.content_spans(enc, x)[1] for x in (s_on, s_off))
                    if s_on[a_on[1]:a_on[2]] != [tok] or s_off[a_off[1]:a_off[2]] != [WORDS[tok][1]] or WORDS[tok][1] == tok:
                        stop(3, f"B3 arms wrong: ON must carry the sampled token, OFF the other word (t{t} k{k})")
                    on, off = br.probe(s_on), br.probe(s_off)
                    row += [0 if w == "DONE" else 1, on[TD], on[TR], off[TD], off[TR]]
                else: row += [-1, np.nan, np.nan, np.nan, np.nan]
                R3.append(row)
        R3 = np.array(R3, np.float64)
        np.savez(OUT / f"{TAG}b3.npz", rows=R3, cols=np.array(["tid", "k", "tok", "lp_tok", "lpD_ask", "lpR_ask", "choice", "on_lpD", "on_lpR", "off_lpD", "off_lpR"]))
        nv = int((R3[:, 6] >= 0).sum()) if len(R3) else 0
        say(f"B3: {len(R3)} choice points, {nv} valid (min 200 of 432 in the plan), dropped {len(R3) - nv}, spend ${spend():.2f}")

        # -------------------------------------------------------------- B1 panel: frozen transcripts × 8 × K_Q1 × 7
        R1P, tp = [], time.time()
        for n, (t, p) in enumerate(T.items()):
            for i in PANEL:
                watch(); ids, cut = D.context(enc, D.system_text(C[i]["system"], D.PERSONAS[CELLS[t][1]]), p, max(KQ1)); br = Brancher(M)
                for k in KQ1:
                    if k not in cut: continue
                    br.extend(ids[br.pos():cut[k]])
                    for c, c1 in enumerate(D.Q1_CONDS):
                        blk = D.q1_block(enc, POOL, C[i], FORMS, c1, (i, c)); lo, hi = B.plant_span(enc, blk, c1)
                        last, tok = br.probe_span(blk); R1P.append((t, i, c, k, last[TD], last[TR], tok[lo:hi].sum(), hi - lo))
            if n + 1 == PROJ_UNITS:
                per = (time.time() - tp) / PROJ_UNITS; usd = spend() + per * (len(T) - PROJ_UNITS) / 3600 * RATE
                say(f"PROJECTION B1 panel ≈ {per * len(T) / 3600:.2f} h → spend at its end ≈ ${usd:.2f} (watchdog ${WATCH})")
                if usd >= WATCH or PLANT == "overbudget": stop(6, f"PROJECTION: B1 panel would end at ≈ ${usd:.2f} ≥ ${WATCH}; B4, B1 full, B3 kept")
        R1P = np.array(R1P, np.float64)
        np.savez(OUT / f"{TAG}b1_panel.npz", rows=R1P, cols=np.array(["tid", "item", "cond", "k", "lpD", "lpR", "plant_lp_sum", "plant_ntok"]))
        if "q1" in FR:
            f = {tuple(int(x) for x in r[:4]): r[4:6] for r in FR["q1"]}
            g = [float(np.abs(r[4:6] - f[tuple(int(x) for x in r[:4])]).max()) for r in R1P if tuple(int(x) for x in r[:4]) in f]
            say(f"B1 panel vs the full run's q1 readouts (reported): n {len(g)}, max |Δ| {max(g):.4f}, median {np.median(g):.4f} nats")
        say(f"B1 panel: {len(R1P)} rows, spend ${spend():.2f}")
    if PHASE == "c":
        # ---------------------------------------------------------- A3.1 skeleton checks (every row): plant only in its
        # turn, that turn LAST, target → readout distance equal across slots ± 2 (Amendment 3 34a16542…)
        ROLEID = {s: enc(B.A3_ROLE[s]) for s in B.A3_SLOTS}; ROWS = {}
        for i in FULL_ITEMS:
            T_ = {enc(" " + C[i]["target_usr"])[-1], enc(C[i]["target_usr"])[-1]}; dist = {}
            for arm in B.A3_ARMS:
                ids = B.a3_row(enc, POOL, C[i], FORMS, arm, i); sp = B.content_spans(enc, ids)[:4]
                hit = [q for q, (r, lo, hi) in enumerate(sp) if T_ & set(ids[lo:hi])]
                if arm == "inert":
                    if hit: stop(3, f"A3 all-inert row carries the target: {C[i]['id']}")
                else:
                    s = arm.split("_")[0]
                    if hit != [3] or sp[3][0] != ROLEID[s]: stop(3, f"A3 skeleton: plant not alone in its LAST turn: {C[i]['id']} {arm}")
                    dist[arm] = B.target_distance(enc, C[i], ids)
                ROWS[(i, arm)] = ids
            for w in B.A3_WRAPS:
                for f in ("imp", "int"):
                    v = [dist[f"{s}_{w}_{f}"] for s in B.A3_SLOTS]
                    if max(v) - min(v) > 2: stop(3, f"A3 skeleton: distance not matched across slots: {C[i]['id']} {w} {f} {v}")
        say(f"A3 skeleton checks OK: {len(ROWS)} rows (plant alone + last; distance matched ± 2)")
        # ---------------------------------------------------------- repeat check: fresh passes bitwise
        rng = np.random.default_rng(D.check_seed(D.SEED_BOOT)); keys = list(ROWS); bad = []
        for q in range(6 if SMOKE else 48):
            kq = keys[int(rng.integers(0, len(keys)))]; a, b = M.lp(ROWS[kq]), M.lp(ROWS[kq])
            if PLANT == "nondeterm": b = b + 1e-9
            if a.tobytes() != b.tobytes(): bad.append(kq)
        if bad: stop(3, f"REPEAT CHECK FAILED: A3 fresh passes not bitwise reproducible: {bad[:5]}")
        say("repeat check PASS (fresh passes, bitwise)")
        # ---------------------------------------------------------- A3.1 rows (fresh, single-pass: A3.3)
        RA = []
        for i in FULL_ITEMS:
            watch()
            for a, arm in enumerate(B.A3_ARMS):
                lp = M.lp(ROWS[(i, arm)]); RA.append((i, a, lp[TD], lp[TR], B.target_distance(enc, C[i], ROWS[(i, arm)]) or -1))
        np.savez(OUT / f"{TAG}a3.npz", rows=np.array(RA, np.float64), cols=np.array(["item", "arm", "lpD", "lpR", "dist_tokens"]), arms=np.array(B.A3_ARMS))
        say(f"A3.1: {len(FULL_ITEMS)} items × {len(B.A3_ARMS)} arms, spend ${spend():.2f}")
        # ---------------------------------------------------------- A3.2 chunk test (exempt from A3.3: it IS the test)
        if "q1" not in FR or "b1_panel" not in FR: stop(2, "A3.2 needs the full run's q1 + B-a's b1_panel in the resume folder")
        ref_f = {tuple(int(x) for x in r[:4]): r[4:6] for r in FR["q1"]}; ref_b = {tuple(int(x) for x in r[:4]): r[4:6] for r in FR["b1_panel"]}
        rng = np.random.default_rng(D.check_seed(D.SEED_BOOT)); pick = []
        for mode in MODES:
            ts = [t for t in range(len(CELLS)) if CELLS[t][0] == mode]; pick += sorted(int(x) for x in rng.choice(ts, min(8, len(ts)), replace=False))
        KA = sorted(set(KQ0) | set(KQ1)); RC = []
        for t in pick:
            for i in PANEL[:2]:
                watch(); ids, cut = D.context(enc, D.system_text(C[i]["system"], D.PERSONAS[CELLS[t][1]]), T[t], max(KQ0)); got = {}
                for arm_name, ks, span in (("a", KA, False), ("b", KQ1, True)):   # (a) the full run's chunking, (b) B-a's
                    br = Brancher(M)
                    for k in ks:
                        if k not in cut: continue
                        br.extend(ids[br.pos():cut[k]])
                        if k not in KQ1: continue
                        for c, c1 in enumerate(D.Q1_CONDS):
                            blk = D.q1_block(enc, POOL, C[i], FORMS, c1, (i, c))
                            lp = br.probe_span(blk)[0] if span else br.probe(blk)
                            v = np.array([lp[TD], lp[TR]])
                            if PLANT == "chunknoise" and arm_name == "a": v = v + 1e-7
                            got.setdefault((c, k), {})[arm_name] = v
                for (c, k), v in got.items():
                    key = (t, i, c, k)
                    if key not in ref_f or key not in ref_b: stop(2, f"A3.2: reference row missing {key}")
                    RC.append((t, i, c, k, *v["a"], *v["b"], *ref_f[key], *ref_b[key]))
        RC = np.array(RC, np.float64)
        np.savez(OUT / f"{TAG}a3_chunk.npz", rows=RC, cols=np.array(["tid", "item", "cond", "k", "a_lpD", "a_lpR", "b_lpD", "b_lpR", "full_lpD", "full_lpR", "ba_lpD", "ba_lpR"]))
        ea = int((RC[:, 4:6] == RC[:, 8:10]).all(1).sum()); eb = int((RC[:, 6:8] == RC[:, 10:12]).all(1).sum())
        say(f"A3.2 chunk test: {len(RC)} rows; (a) full-run chunking = the full run's q1 bit-for-bit on {ea} / {len(RC)}; "
            f"(b) B-a chunking = B-a's b1_panel bit-for-bit on {eb} / {len(RC)} (reported; the analysis applies A3.2)")
    if PHASE == "b":
        # ---------------------------------------------------------- B5 design (PLAN_PHASE_B.md B5)
        BSEEDS = B.B5_SEEDS[:2] if SMOKE else B.B5_SEEDS
        BC = [(m, p, t, s) for m in B.B5_MODES for p in PERS for t in TEMPS for s in BSEEDS]   # main tid = index
        if PLANT == "badseed": BC[0] = (BC[0][0], BC[0][1], BC[0][2], D.GEN_SEEDS[0])       # the main run's seed
        for c in BC:
            try: B.check_b5_seed(c[3])
            except SystemExit as e: stop(2, str(e))
        WI = [("M1", p, 1.0, s, it) for p in PERS for s in BSEEDS[:2] for it in ((PANEL[0], PANEL[1]) if SMOKE else (PANEL[0], PANEL[4]))]
        MAXNEW, BUDGET, BATCH, PROJ_TURNS = 256, 24576, int(os.environ.get("DRIFT_BATCH", "12")), 3
        BSZ = {"n": BATCH}; PROJ = {}
        say(f"B5 design: {len(BC)} transcripts ({'/'.join(B.B5_MODES)} × {len(PERS)} personas × {len(TEMPS)} T × {len(BSEEDS)} seeds) + {len(WI)} with-instruction, {NTURN} turns")
        # ---------------------------------------------------------- Phase 1 generation (copied from drift01_lambda.py; no M2)
        def first_user(mode): return D.text_ids(enc, D.M3_PROMPT if mode == "M3" else D.CONTINUE)
        def gen_batched(ctxs, temp, seed):
            out, b = [], 0
            while b < len(ctxs):
                n = BSZ["n"]
                try: out += M.generate(ctxs[b:b + n], temp, gseed(*seed, b), MAXNEW); b += n
                except Exception as e:
                    if "out of memory" not in str(e).lower() or n == 1: raise
                    if REAL: import torch; torch.cuda.empty_cache()
                    BSZ["n"] = max(1, n // 2); say(f"OOM at sub-batch {n} → {BSZ['n']}")
            return out
        def run_group(group, temp, sys_of, proj=None):
            pairs = {g: [] for g in group}; live = list(group); cont = {g: first_user(g[0]) for g in group}; tt = []
            for j in range(1, NTURN + 1):
                watch(); tj = time.time()
                ctx = {g: D.context(enc, sys_of(g), pairs[g], NTURN)[0] + D.turn(enc, "user", cont[g]) + enc(D.H("assistant")) for g in live}
                live = [g for g in live if len(ctx[g]) + 2 * MAXNEW < BUDGET]
                if not live: break
                gen = gen_batched([ctx[g] for g in live], temp, (group[0][3], group[0][0], temp, j, "A" if len(group[0]) == 4 else "W"))
                for g, (a, trunc) in zip(live, gen): pairs[g].append((cont[g], a)); cont[g] = D.text_ids(enc, D.CONTINUE)
                tt.append(time.time() - tj)
                say(f"phase 1 turn {j}: {len(live)} live, {tt[-1]:.1f} s, max ctx {max(map(len, ctx.values()))}, peak mem {M.mem_gb():.1f} GB, sub-batch {BSZ['n']}, spend ${spend():.2f}")
                if proj is not None and j == PROJ_TURNS:
                    b_, a_ = np.polyfit(np.arange(1, j + 1), tt, 1); p1 = sum(max(a_ + b_ * x, 0) for x in range(1, NTURN + 1)) * proj["weight"]
                    PROJ["phase1_s"] = p1; usd = spend() + p1 / 3600 * RATE
                    say(f"PROJECTION phase 1 ≈ {p1 / 3600:.2f} h → spend at its end ≈ ${usd:.2f} (watchdog ${WATCH})")
                    if usd >= WATCH or PLANT == "overbudget": stop(6, f"PROJECTION: phase 1 alone would end at ≈ ${usd:.2f} ≥ ${WATCH}; nothing kept but the log")
            return pairs
        groups = [(m, t, [c for c in BC if c[0] == m and c[2] == t]) for m in B.B5_MODES for t in TEMPS]
        wt = lambda g: -(-len(g) // BATCH); total_w = sum(wt(g) for _, _, g in groups) + wt(WI)
        T, t1 = {}, time.time()
        for n_, (m, t, grp) in enumerate(groups):
            got = run_group(grp, t, lambda g: D.PERSONAS[g[1]], proj={"weight": total_w / wt(grp)} if n_ == 0 else None)
            for g in grp: T[BC.index(g)] = got[g]
        got = run_group(WI, 1.0, lambda g: D.system_text(C[g[4]]["system"], D.PERSONAS[g[1]]))
        for w, g in enumerate(WI): T[B.WI_TID0 + w] = got[g]
        say(f"phase 1 done: {len(BC)} transcripts + {len(WI)} with-instruction, {time.time() - t1:.0f} s")
        # ---------------------------------------------------------- freeze (main + with-instruction, ids saved)
        man = {str(t): D.transcript_sha(p) for t, p in T.items()}
        flat = [(t, j, r, x) for t, p in T.items() for j, (u, a) in enumerate(p) for r, x in ((0, u), (1, a))]
        np.savez(OUT / f"{TAG}b5_transcripts.npz", ids=np.concatenate([np.asarray(x, np.int32) for *_, x in flat]),
                 off=np.cumsum([0] + [len(x) for *_, x in flat]), tid=np.array([f[0] for f in flat]), turn=np.array([f[1] for f in flat]), role=np.array([f[2] for f in flat]))
        with open(OUT / f"{TAG}b5_transcripts.jsonl", "w", encoding="utf-8") as fh:
            for t, p in T.items():
                meta = {"tid": t, "mode": BC[t][0], "persona": BC[t][1], "temp": BC[t][2], "seed": BC[t][3]} if t < B.WI_TID0 else \
                       {"tid": t, "with_instruction": t - B.WI_TID0, "cell": list(WI[t - B.WI_TID0][:4]), "item": C[WI[t - B.WI_TID0][4]]["id"]}
                fh.write(json.dumps({**meta, "n": len(p), "turns": [{"user": dec(u), "assistant": dec(a)} for u, a in p]}, ensure_ascii=False) + "\n")
        (OUT / f"{TAG}b5_transcripts_manifest.json").write_text(json.dumps({"cells": [list(c) for c in BC], "with_instruction": [list(w[:4]) + [C[w[4]]["id"]] for w in WI],
                                                                           "sha": man}, indent=1), encoding="utf-8")
        say("frozen; manifest sha", sha(OUT / f"{TAG}b5_transcripts_manifest.json"))
        if PLANT == "tamper": u, a = T[0][0]; T[0][0] = (u, a[:-1] + [a[-1] + 1])
        probs = D.verify_frozen(T, man)
        if probs: stop(3, "FREEZE: " + "; ".join(probs))
        # ---------------------------------------------------------- Q0 units: ONE prefill pass, probes in DESCENDING k (A3.3)
        def jobs():
            for t in T:
                if t < B.WI_TID0:
                    for i in PANEL: yield t, i, D.PERSONAS[BC[t][1]]
                else: yield t, WI[t - B.WI_TID0][4], D.PERSONAS[WI[t - B.WI_TID0][1]]
        def unit(t, i, pers, cond):
            rows = D.q0_rows(enc, POOL, C[i], pers, T[t], T[t], t, KQ0); ids, cut, suf = rows[cond]
            ks = sorted((k for k in KQ0 if k in cut), reverse=True); br = Brancher(M); br.prefill(ids[:cut[ks[0]]]); res = {}
            for k in ks:
                br.crop_to(cut[k]); lp = br.probe(suf); res[k] = (lp[TD], lp[TR], D.distance(cut, k))
            return res, rows
        # repeat check (stop) + branched-vs-fresh gap (reported), before Phase 2
        rng = np.random.default_rng(D.check_seed(D.SEED_BOOT)); J_ = list(jobs()); tc = time.time(); NCHK = 6 if SMOKE else 48; rep_bad, gaps = [], []
        for q in range(NCHK):
            t, i, pers = J_[int(rng.integers(0, len(J_)))]; cond = B.B5_CONDS[int(rng.integers(0, 3))]
            r1, rows = unit(t, i, pers, cond); r2, _ = unit(t, i, pers, cond)
            if np.array(list(r1.values())).tobytes() != np.array(list(r2.values())).tobytes(): rep_bad.append((t, C[i]["id"], cond))
            k = sorted(r1)[int(rng.integers(0, len(r1)))]; fresh = M.lp(D.row(*rows[cond], k))
            gaps.append({"cond": cond, "k": k, "gap": float(max(abs(r1[k][0] - fresh[TD]), abs(r1[k][1] - fresh[TR])))})
        GAP = {"n": NCHK, "what": "single-pass prefill + descending-k crop vs a fresh pass", "max": max(g["gap"] for g in gaps),
               "median": float(np.median([g["gap"] for g in gaps])), "rows": gaps}
        (OUT / f"{TAG}b5_gap_report.json").write_text(json.dumps(GAP, indent=1), encoding="utf-8")
        if rep_bad: stop(3, f"REPEAT CHECK FAILED: B5 units not bitwise reproducible: {rep_bad[:5]}")
        say(f"repeat check PASS ({NCHK} × 2, bitwise); gap vs fresh (reported): max {GAP['max']:.4f} median {GAP['median']:.4f} nats")
        per = (time.time() - tc) / (2 * NCHK); p2 = per * len(J_) * len(B.B5_CONDS); usd = spend() + p2 / 3600 * RATE
        say(f"PROJECTION phase 2 ≈ {p2 / 3600:.2f} h (upper bound) → spend ≈ ${usd:.2f}")
        if usd >= WATCH: stop(6, f"PROJECTION: phase 2 would end at ≈ ${usd:.2f} ≥ ${WATCH}; transcripts are frozen + saved")
        R5 = []
        for n_, (t, i, pers) in enumerate(J_):
            watch()
            for c, cond in enumerate(B.B5_CONDS):
                res, _ = unit(t, i, pers, cond); R5 += [(t, i, c, k, *v) for k, v in res.items()]
            if (n_ + 1) % 50 == 0: say(f"phase 2 unit {n_ + 1} / {len(J_)}: spend ${spend():.2f}")
        np.savez(OUT / f"{TAG}b5_q0.npz", rows=np.array(R5, np.float64), cols=np.array(["tid", "item", "cond", "k", "lpD", "lpR", "dist_tokens"]), conds=np.array(B.B5_CONDS))
        say(f"B5 Q0: {len(R5)} rows; one-pass prefill fell back to the 4,096 grid {Brancher.grid_used} time(s); spend ${spend():.2f}")
    if PHASE in ("d", "e"):
        E = PHASE == "e"; CONDS = A5_CONDS if E else B.B6_CONDS; CI_ = {c: B.B6_CONDS.index(c) for c in CONDS}
        PFX = "a5_" if E else "b6_"; RLAB = "A5 REPRO GATE" if E else "S7 REPRO"
        # ---------------------------------------------------------- RESUME: the frozen B-b transcripts, verified (Amendment 4 A4.1)
        BSEEDS = B.B5_SEEDS[:2] if SMOKE else B.B5_SEEDS
        BC = [(m, p, t, s) for m in B.B5_MODES for p in PERS for t in TEMPS for s in BSEEDS]
        R = INP / os.environ["DRIFT_RESUME"]; mf = R / f"{TAG}b5_transcripts_manifest.json"
        if sha(mf) != os.environ.get("DRIFT_RESUME_MANIFEST_SHA", ""): stop(2, "RESUME: B-b transcripts manifest is not the pinned one")
        man0 = json.loads(mf.read_text(encoding="utf-8"))
        if [tuple(c) for c in man0["cells"]] != BC: stop(2, "RESUME: the frozen B-b transcripts are a different design")
        Zr = np.load(R / f"{TAG}b5_transcripts.npz"); flat = {}
        for q in range(len(Zr["tid"])): flat.setdefault(int(Zr["tid"][q]), []).append(Zr["ids"][Zr["off"][q]:Zr["off"][q + 1]].tolist())
        T = {t: list(zip(v[0::2], v[1::2])) for t, v in flat.items()}
        if PLANT == "resumetamper": u, a = T[0][0]; T[0][0] = (u, a[:-1] + [a[-1] + 1])
        probs = D.verify_frozen(T, man0["sha"])                  # every saved transcript, with-instruction included
        if probs: stop(3, "RESUME FREEZE: " + "; ".join(probs[:5]))
        T = {t: p for t, p in T.items() if t < B.WI_TID0}       # A4.1: main transcripts only
        if sorted(T) != list(range(len(BC))): stop(2, f"RESUME: main transcripts {sorted(T)[:3]}… ≠ 0..{len(BC) - 1}")
        say(f"RESUMED: {len(T)} frozen B-b main transcripts loaded + verified (manifest {sha(mf)[:16]})")
        P12 = {p["item"] for p in json.loads((INP / "panel.json").read_text(encoding="utf-8"))["panel"]}
        FRESH = [x["item"] for x in json.loads((INP / "fresh_items.json").read_text(encoding="utf-8"))["items"]]
        if len(FRESH) != 80 or len(set(FRESH)) != 80 or set(FRESH) & P12: stop(2, "fresh_items.json: not 80 distinct non-panel items")
        REPI = PANEL                                             # D: the 8 B-b items vs b5_q0
        if E:                                                    # A5.1: 120 items, 2 + 2 per template; gate = the first 8 A4 items vs b6_q0
            A4F = FRESH; FRESH = [x["item"] for x in json.loads((INP / "a5_items.json").read_text(encoding="utf-8"))["items"]]
            if len(FRESH) != 120 or len(set(FRESH)) != 120 or set(FRESH) & (P12 | set(A4F)): stop(2, "a5_items.json: not 120 distinct items outside the panel and A4")
            REPI = A4F[:2] if SMOKE else A4F[:8]
        if SMOKE: FRESH = FRESH[:4]
        PROSE = enc((INP / "pg1228_prose.txt").read_text(encoding="utf-8"))
        if PLANT == "prosebreak":                                # FAKE plant: one prose turn a token short → the match check stops it
            _pp = B.prose_pairs
            B.prose_pairs = lambda pr, pa, t: (lambda o: [(o[0][0][:-1], o[0][1])] + o[1:])(_pp(pr, pa, t))
        if E: say(f"A5 design: {len(T)} transcripts × ({len(REPI)} A4 items × {len(CONDS)} repro + {len(FRESH)} A5 items × {len(CONDS)}), k ∈ {KQ0}; prose {len(PROSE)} tokens")
        else: say(f"B6 design: {len(T)} transcripts × ({len(PANEL)} B-b items × 3 repro + {len(FRESH)} fresh × {len(B.B6_CONDS)}), k ∈ {KQ0}; prose {len(PROSE)} tokens")
        def unit(t, i, conds):
            """One (transcript, item): rows built once; per cond ONE prefill pass, probes in DESCENDING k (A3.3)."""
            try: rows = B.b6_rows(enc, POOL, PROSE, C[i], D.PERSONAS[BC[t][1]], T[t], t, KQ0)
            except AssertionError as e: stop(3, f"B6 rows ({C[i]['id']}, t{t}): {e}")
            res = {}
            for cond in conds:
                ids, cut, suf = rows[cond]; ks = sorted((k for k in KQ0 if k in cut), reverse=True)
                br = Brancher(M); br.prefill(ids[:cut[ks[0]]]); res[cond] = {}
                for k in ks:
                    br.crop_to(cut[k]); lp = br.probe(suf); res[cond][k] = (lp[TD], lp[TR], D.distance(cut, k))
            return res, rows
        # ---------------------------------------------------------- S7 REPRO: the 8 B-b items under this code vs B-b's b5_q0
        REPRO_TOL = 0.05                                         # nats; a code / row mismatch moves readouts by far more
        RSRC = "b6_q0" if E else "b5_q0"; RCONDS = A5_CONDS if E else B.B5_CONDS
        ref = {tuple(int(x) for x in r[:4]): r[4:6] for r in np.load(R / f"{TAG}{RSRC}.npz")["rows"] if r[0] < B.WI_TID0}
        RP, tp = [], time.time()
        for t in T:
            for i in REPI:
                watch(); res, _ = unit(t, i, RCONDS)
                for cond in RCONDS:
                    c = B.B6_CONDS.index(cond)
                    for k, v in res[cond].items():
                        key = (t, i, c, k)
                        if key not in ref: stop(2, f"{RLAB}: {RSRC} row missing {key}")
                        got = np.array(v[:2]) + (1.0 if PLANT == "reprobreak" and key == (0, REPI[0], 1, 4) else 0.0)
                        RP.append((t, i, c, k, *got, *ref[key], v[2]))
        RP = np.array(RP, np.float64); dmax = np.abs(RP[:, 4:6] - RP[:, 6:8]).max(1)
        np.savez(OUT / f"{TAG}{PFX}repro.npz", rows=RP, cols=np.array(["tid", "item", "cond", "k", "lpD", "lpR", "ref_lpD" if E else "bb_lpD", "ref_lpR" if E else "bb_lpR", "dist_tokens"]))
        REP = {"n": len(RP), "bitwise": int((RP[:, 4:6] == RP[:, 6:8]).all(1).sum()), "max": float(dmax.max()), "median": float(np.median(dmax)), "tol": REPRO_TOL}
        (OUT / f"{TAG}{PFX}repro.json").write_text(json.dumps(REP, indent=1), encoding="utf-8")
        say(f"{RLAB if E else 'S7 repro'} vs {'A4 b6_q0' if E else 'B-b b5_q0'}: {REP['n']} rows, bitwise {REP['bitwise']} / {REP['n']}, max |Δ| {REP['max']:.4g}, median {REP['median']:.4g} nats, {time.time() - tp:.0f} s, spend ${spend():.2f}")
        if not REP["max"] <= REPRO_TOL: stop(3, f"{RLAB} FAILED: max |Δ| {REP['max']:.4g} > {REPRO_TOL} nats vs {'A4' if E else 'B-b'}'s {RSRC}")
        # ---------------------------------------------------------- repeat check (stop) + single-pass vs fresh gap (reported)
        J_ = [(t, i) for t in T for i in FRESH]
        rng = np.random.default_rng(D.check_seed(D.SEED_BOOT)); tc = time.time(); NCHK = 6 if SMOKE else 48; rep_bad, gaps = [], []
        for q in range(NCHK):
            t, i = J_[int(rng.integers(0, len(J_)))]; cond = CONDS[int(rng.integers(0, len(CONDS)))]
            r1, rows = unit(t, i, (cond,)); r2, _ = unit(t, i, (cond,))
            if PLANT == "nondeterm": r2 = {cond: {k: (v[0] + 1e-9, *v[1:]) for k, v in r2[cond].items()}}
            if np.array(list(r1[cond].values())).tobytes() != np.array(list(r2[cond].values())).tobytes(): rep_bad.append((t, C[i]["id"], cond))
            k = sorted(r1[cond])[int(rng.integers(0, len(r1[cond])))]; fresh = M.lp(D.row(*rows[cond], k))
            gaps.append({"cond": cond, "k": k, "gap": float(max(abs(r1[cond][k][0] - fresh[TD]), abs(r1[cond][k][1] - fresh[TR])))})
        GAP = {"n": NCHK, "what": "single-pass prefill + descending-k crop vs a fresh pass", "max": max(g["gap"] for g in gaps),
               "median": float(np.median([g["gap"] for g in gaps])), "rows": gaps}
        (OUT / f"{TAG}{PFX}gap_report.json").write_text(json.dumps(GAP, indent=1), encoding="utf-8")
        if rep_bad: stop(3, f"REPEAT CHECK FAILED: {'A5' if E else 'B6'} units not bitwise reproducible: {rep_bad[:5]}")
        say(f"repeat check PASS ({NCHK} × 2, bitwise); gap vs fresh (reported): max {GAP['max']:.4f} median {GAP['median']:.4f} nats")
        per = (time.time() - tc) / (2 * NCHK); p2 = per * len(J_) * len(CONDS); usd = spend() + p2 / 3600 * RATE
        say(f"PROJECTION fresh units ≈ {p2 / 3600:.2f} h (one cond per timed unit) → spend ≈ ${usd:.2f} (watchdog ${WATCH})")
        if usd >= WATCH or PLANT == "overbudget": stop(6, f"PROJECTION: fresh units would end at ≈ ${usd:.2f} ≥ ${WATCH}; {RLAB} kept")
        # ---------------------------------------------------------- prose passages: offset + target-family counts (A4.1, reported)
        RX = {w: __import__("re").compile(r"\b(" + "|".join(v) + r")\b", __import__("re").I) for w, v in
              {"DONE": ("done", "finished", "complete", "completed"), "READY": ("ready", "prepared", "set")}.items()}
        PI = {}
        for t in T:
            pp = B.prose_pairs(PROSE, T[t][:max(KQ0)], t); txt = " ".join(dec(u) + " " + dec(a) for u, a in pp)
            PI[t] = {"ntok": sum(len(u) + len(a) for u, a in pp), **{w: len(rx.findall(txt)) for w, rx in RX.items()}}
        (OUT / f"{TAG}{PFX}prose.json").write_text(json.dumps(PI, indent=1), encoding="utf-8")
        # ---------------------------------------------------------- the fresh items × CONDS (cond index = B6_CONDS')
        R6 = []
        for n_, (t, i) in enumerate(J_):
            watch(); res, _ = unit(t, i, CONDS)
            for cond in CONDS: R6 += [(t, i, CI_[cond], k, *v) for k, v in res[cond].items()]
            if (n_ + 1) % 400 == 0: say(f"fresh unit {n_ + 1} / {len(J_)}: spend ${spend():.2f}")
        np.savez(OUT / f"{TAG}{PFX}q0.npz", rows=np.array(R6, np.float64), cols=np.array(["tid", "item", "cond", "k", "lpD", "lpR", "dist_tokens"]), conds=np.array(B.B6_CONDS),
                 **({"arms": np.array(CONDS)} if E else {}))
        say(f"{'A5' if E else 'B6'} Q0: {len(R6)} rows; one-pass prefill fell back to the 4,096 grid {Brancher.grid_used} time(s); spend ${spend():.2f}")
    if PHASE == "f":
        # ---------------------------------------------------------- A6.1 design: probes × draws (Amendment 6 1e6de4f1…)
        PROBES = sorted(x["item"] for x in json.loads((INP / "a5_items.json").read_text(encoding="utf-8"))["items"])
        DM = {x["item"]: x["draws"] for x in json.loads((INP / "a6_demos.json").read_text(encoding="utf-8"))["demos"]}
        if sorted(DM) != PROBES or len(PROBES) != 120 or any(len(v) != 8 or any(len(l) != A6.NMAX for l in v) for v in DM.values()):
            stop(2, "a6_demos.json: not 120 probes × 8 draws × 8 demos over the A5 items")
        if SMOKE: PROBES = PROBES[:4]
        ND = 2 if SMOKE else 8; AI = {a: n for n, a in enumerate(A6.ARMS)}; ANCHOR = len(A6.ARMS)
        if PLANT == "a6swap":                                    # FAKE plant: one defer demo keeps the competing word → the row check stops
            _dp = A6.demo_pairs
            A6.demo_pairs = lambda enc_, C_, p_, d_, arm: (lambda o: ([(o[0][0], D.text_ids(enc_, C_[p_]["target_usr"]))] + o[1:]) if arm == "defer" and p_ == PROBES[0] else o)(_dp(enc_, C_, p_, d_, arm))
        say(f"A6 design: {len(PROBES)} probes × {ND} draws × {len(A6.ARMS)} arms × n ∈ {A6.NS} + 1 anchor per probe")
        # ---------------------------------------------------------- row checks on EVERY probe × draw (stop)
        ROWS = {}
        for p in PROBES:
            for d in range(ND):
                try: R_ = A6.rows(enc, C, p, DM[p][d])
                except AssertionError as e: stop(3, f"A6 rows ({C[p]['id']}, draw {d}): {e}")
                pr = A6.check_rows(enc, C, p, R_)
                if pr: stop(3, f"A6 ROW CHECK FAILED ({C[p]['id']}, draw {d}): {'; '.join(pr[:3])}")
                ROWS[(p, d)] = R_
        RCK = {"probe_draws": len(ROWS), "arms": list(A6.ARMS), "ns": list(A6.NS),
               "row_tokens_max": max(R_["obey"][1][A6.NMAX] + len(R_["obey"][2]) for R_ in ROWS.values())}
        (OUT / f"{TAG}a6_rowcheck.json").write_text(json.dumps(RCK, indent=1), encoding="utf-8")
        say(f"A6 row checks OK: {len(ROWS)} probe × draw, 4 arms each token-identical but for the DONE / READY swaps; longest row {RCK['row_tokens_max']} tokens")
        def unit6(p, d, arm):
            """One probe × draw × arm: ONE prefill through n = NMAX, probes in DESCENDING n (A3.3)."""
            ids, cut, suf = ROWS[(p, d)][arm]; br = Brancher(M); br.prefill(ids[:cut[A6.NMAX]]); res = {}
            for n in sorted(A6.NS, reverse=True):
                br.crop_to(cut[n]); lp = br.probe(suf); res[n] = (lp[TD], lp[TR], D.distance(cut, n), lp[TD0], lp[TR0])
            return res
        # ---------------------------------------------------------- repeat check (stop) + single-pass vs fresh gap (reported)
        KEYS = [(p, d, a) for (p, d) in ROWS for a in A6.ARMS]
        if not FAKE and len({TD, TR, TD0, TR0}) != 4: stop(2, "A6: the no-space DONE / READY tokens coincide with the readout tokens")
        rng = np.random.default_rng(D.check_seed(D.SEED_BOOT)); tc = time.time(); NCHK = 6 if SMOKE else 48; rep_bad, gaps = [], []
        for q in range(NCHK):
            p, d, a = KEYS[int(rng.integers(0, len(KEYS)))]; r1, r2 = unit6(p, d, a), unit6(p, d, a)
            if PLANT == "nondeterm": r2 = {n: (v[0] + 1e-9, *v[1:]) for n, v in r2.items()}
            if np.array(list(r1.values())).tobytes() != np.array(list(r2.values())).tobytes(): rep_bad.append((C[p]["id"], d, a))
            n = A6.NS[int(rng.integers(0, len(A6.NS)))]; fresh = M.lp(D.row(*ROWS[(p, d)][a], n))
            gaps.append({"arm": a, "n": n, "gap": float(max(abs(r1[n][0] - fresh[TD]), abs(r1[n][1] - fresh[TR])))})
        GAP = {"n": NCHK, "what": "single-pass prefill + descending-n crop vs a fresh pass", "max": max(g["gap"] for g in gaps),
               "median": float(np.median([g["gap"] for g in gaps])), "rows": gaps}
        (OUT / f"{TAG}a6_gap_report.json").write_text(json.dumps(GAP, indent=1), encoding="utf-8")
        if rep_bad: stop(3, f"REPEAT CHECK FAILED: A6 units not bitwise reproducible: {rep_bad[:5]}")
        say(f"repeat check PASS ({NCHK} × 2, bitwise); gap vs fresh (reported): max {GAP['max']:.4f} median {GAP['median']:.4f} nats")
        per = (time.time() - tc) / (2 * NCHK); p2 = per * len(KEYS); usd = spend() + p2 / 3600 * RATE
        say(f"PROJECTION A6 units ≈ {p2 / 3600:.2f} h → spend ≈ ${usd:.2f} (watchdog ${WATCH})")
        if usd >= WATCH or PLANT == "overbudget": stop(6, f"PROJECTION: A6 units would end at ≈ ${usd:.2f} ≥ ${WATCH}")
        # ---------------------------------------------------------- rows: anchors (n = 0, once per probe) + every unit
        R7 = []
        for p in PROBES:
            ids, cut, suf = A6.anchor(enc, C, p); br = Brancher(M); br.prefill(ids[:cut[0]]); lp = br.probe(suf)
            R7.append((p, -1, ANCHOR, 0, lp[TD], lp[TR], 0, lp[TD0], lp[TR0]))
        for n_, (p, d, a) in enumerate(KEYS):
            watch(); R7 += [(p, d, AI[a], n, *v) for n, v in unit6(p, d, a).items()]
            if (n_ + 1) % 400 == 0: say(f"A6 unit {n_ + 1} / {len(KEYS)}: spend ${spend():.2f}")
        np.savez(OUT / f"{TAG}a6_q0.npz", rows=np.array(R7, np.float64), cols=np.array(["item", "draw", "arm", "n", "lpD", "lpR", "dist_tokens", "lpD_ns", "lpR_ns"]),
                 arms=np.array(A6.ARMS + ("anchor",)))
        say(f"A6 Q0: {len(R7)} rows; one-pass prefill fell back to the 4,096 grid {Brancher.grid_used} time(s); spend ${spend():.2f}")
    if PHASE == "g":
        PROBES = sorted(x["item"] for x in json.loads((INP / "a7_items.json").read_text(encoding="utf-8"))["items"])
        DM = {x["item"]: x["draws"] for x in json.loads((INP / "a7_demos.json").read_text(encoding="utf-8"))["demos"]}
        if sorted(DM) != PROBES or len(PROBES) != 120 or any(len(v) != 8 or any(len(l) != A6.NMAX for l in v) for v in DM.values()):
            stop(2, "a7_demos.json: not 120 probes × 8 draws × 8 demos over the A7 items")
        if SMOKE: PROBES = PROBES[:4]
        ND = 2 if SMOKE else 8; AI = {a: n for n, a in enumerate(A6.ARMS)}; ANCHOR = len(A6.ARMS)
        if PLANT == "a7swap":                                    # FAKE plant: one N probe keeps the competing word → the N check stops
            _sn = A7.suffix_n
            A7.suffix_n = lambda enc_, C_, p_: D.probe_suffix(enc_, C_[p_]["user"]) if p_ == PROBES[0] else _sn(enc_, C_, p_)
        say(f"A7 design: {len(PROBES)} probes × {ND} draws × {len(A6.ARMS)} arms × n ∈ {A6.NS} × probes {A7.PROBES} + 2 anchors per probe")
        # ---------------------------------------------------------- row checks on EVERY probe × draw: A6's + the N probe (stop)
        ROWS, SN = {}, {}
        for p in PROBES:
            SN[p] = A7.suffix_n(enc, C, p)
            for d in range(ND):
                try: R_ = A6.rows(enc, C, p, DM[p][d])
                except AssertionError as e: stop(3, f"A7 rows ({C[p]['id']}, draw {d}): {e}")
                pr = A6.check_rows(enc, C, p, R_) + A7.check_n(enc, C, p, R_["obey"][2], SN[p])
                if pr: stop(3, f"A7 ROW CHECK FAILED ({C[p]['id']}, draw {d}): {'; '.join(pr[:3])}")
                ROWS[(p, d)] = R_
        RCK = {"probe_draws": len(ROWS), "arms": list(A6.ARMS), "ns": list(A6.NS), "probes": list(A7.PROBES),
               "row_tokens_max": max(R_["obey"][1][A6.NMAX] + len(R_["obey"][2]) for R_ in ROWS.values())}
        (OUT / f"{TAG}a7_rowcheck.json").write_text(json.dumps(RCK, indent=1), encoding="utf-8")
        say(f"A7 row checks OK: {len(ROWS)} probe × draw, 4 arms token-identical but for the DONE / READY swaps, N = C but the "
            f"one requested word; longest row {RCK['row_tokens_max']} tokens")
        def unit7(p, d, arm):
            """One probe × draw × arm: ONE prefill through n = NMAX, probes C then N at each n, n DESCENDING (A3.3)."""
            ids, cut, suf = ROWS[(p, d)][arm]; br = Brancher(M); br.prefill(ids[:cut[A6.NMAX]]); res = {}
            for n in sorted(A6.NS, reverse=True):
                br.crop_to(cut[n]); c = br.probe(suf); m = br.probe(SN[p]); dist = D.distance(cut, n)
                res[n] = ((c[TD], c[TR], dist, c[TD0], c[TR0]), (m[TD], m[TR], dist, m[TD0], m[TR0]))
            return res
        # ---------------------------------------------------------- repeat check (stop) + single-pass vs fresh gap (reported)
        KEYS = [(p, d, a) for (p, d) in ROWS for a in A6.ARMS]
        if not FAKE and len({TD, TR, TD0, TR0}) != 4: stop(2, "A7: the no-space DONE / READY tokens coincide with the readout tokens")
        rng = np.random.default_rng(D.check_seed(D.SEED_BOOT)); tc = time.time(); NCHK = 6 if SMOKE else 48; rep_bad, gaps = [], []
        for q in range(NCHK):
            p, d, a = KEYS[int(rng.integers(0, len(KEYS)))]; r1, r2 = unit7(p, d, a), unit7(p, d, a)
            if PLANT == "nondeterm": r2 = {n: ((v[0][0] + 1e-9, *v[0][1:]), v[1]) for n, v in r2.items()}
            if np.array(list(r1.values())).tobytes() != np.array(list(r2.values())).tobytes(): rep_bad.append((C[p]["id"], d, a))
            n = A6.NS[int(rng.integers(0, len(A6.NS)))]; ids, cut, suf = ROWS[(p, d)][a]
            fc, fn = M.lp(D.row(ids, cut, suf, n)), M.lp(D.row(ids, cut, SN[p], n))
            gaps.append({"arm": a, "n": n, "gap": float(max(abs(r1[n][0][0] - fc[TD]), abs(r1[n][0][1] - fc[TR]),
                                                            abs(r1[n][1][0] - fn[TD]), abs(r1[n][1][1] - fn[TR])))})
        GAP = {"n": NCHK, "what": "single-pass prefill + descending-n crop vs a fresh pass, C and N", "max": max(g["gap"] for g in gaps),
               "median": float(np.median([g["gap"] for g in gaps])), "rows": gaps}
        (OUT / f"{TAG}a7_gap_report.json").write_text(json.dumps(GAP, indent=1), encoding="utf-8")
        if rep_bad: stop(3, f"REPEAT CHECK FAILED: A7 units not bitwise reproducible: {rep_bad[:5]}")
        say(f"repeat check PASS ({NCHK} × 2, bitwise); gap vs fresh (reported): max {GAP['max']:.4f} median {GAP['median']:.4f} nats")
        per = (time.time() - tc) / (2 * NCHK); p2 = per * len(KEYS); usd = spend() + p2 / 3600 * RATE
        say(f"PROJECTION A7 units ≈ {p2 / 3600:.2f} h → spend ≈ ${usd:.2f} (watchdog ${WATCH})")
        if usd >= WATCH or PLANT == "overbudget": stop(6, f"PROJECTION: A7 units would end at ≈ ${usd:.2f} ≥ ${WATCH}")
        # ---------------------------------------------------------- rows: anchors (n = 0, C and N, once per probe) + every unit
        R8 = []
        for p in PROBES:
            ids, cut, suf = A6.anchor(enc, C, p); br = Brancher(M); br.prefill(ids[:cut[0]]); c = br.probe(suf); m = br.probe(SN[p])
            R8 += [(p, -1, ANCHOR, 0, c[TD], c[TR], 0, c[TD0], c[TR0], 0), (p, -1, ANCHOR, 0, m[TD], m[TR], 0, m[TD0], m[TR0], 1)]
        for n_, (p, d, a) in enumerate(KEYS):
            watch()
            for n, (vc, vn) in unit7(p, d, a).items(): R8 += [(p, d, AI[a], n, *vc, 0), (p, d, AI[a], n, *vn, 1)]
            if (n_ + 1) % 400 == 0: say(f"A7 unit {n_ + 1} / {len(KEYS)}: spend ${spend():.2f}")
        np.savez(OUT / f"{TAG}a7_q0.npz", rows=np.array(R8, np.float64),
                 cols=np.array(["item", "draw", "arm", "n", "lpD", "lpR", "dist_tokens", "lpD_ns", "lpR_ns", "probe"]),
                 arms=np.array(A6.ARMS + ("anchor",)), probes=np.array(A7.PROBES))
        say(f"A7 Q0: {len(R8)} rows; one-pass prefill fell back to the 4,096 grid {Brancher.grid_used} time(s); spend ${spend():.2f}")
    if PHASE == "h":
        # ---------------------------------------------------------- RESUME: the frozen B-b transcripts, verified (as E)
        BSEEDS = B.B5_SEEDS[:2] if SMOKE else B.B5_SEEDS
        BC = [(m, p, t, s) for m in B.B5_MODES for p in PERS for t in TEMPS for s in BSEEDS]
        R = INP / os.environ["DRIFT_RESUME"]; mf = R / f"{TAG}b5_transcripts_manifest.json"
        if sha(mf) != os.environ.get("DRIFT_RESUME_MANIFEST_SHA", ""): stop(2, "RESUME: B-b transcripts manifest is not the pinned one")
        man0 = json.loads(mf.read_text(encoding="utf-8"))
        if [tuple(c) for c in man0["cells"]] != BC: stop(2, "RESUME: the frozen B-b transcripts are a different design")
        Zr = np.load(R / f"{TAG}b5_transcripts.npz"); flat = {}
        for q in range(len(Zr["tid"])): flat.setdefault(int(Zr["tid"][q]), []).append(Zr["ids"][Zr["off"][q]:Zr["off"][q + 1]].tolist())
        T = {t: list(zip(v[0::2], v[1::2])) for t, v in flat.items()}
        if PLANT == "resumetamper": u, a = T[0][0]; T[0][0] = (u, a[:-1] + [a[-1] + 1])
        probs = D.verify_frozen(T, man0["sha"])
        if probs: stop(3, "RESUME FREEZE: " + "; ".join(probs[:5]))
        T = {t: p for t, p in T.items() if t < B.WI_TID0}       # main transcripts only
        if sorted(T) != list(range(len(BC))): stop(2, f"RESUME: main transcripts {sorted(T)[:3]}… ≠ 0..{len(BC) - 1}")
        say(f"RESUMED: {len(T)} frozen B-b main transcripts loaded + verified (manifest {sha(mf)[:16]})")
        NP = len(BC) // 2                                        # A8.1: pair j = (M1 transcript j, M3 transcript j + NP)
        if any(BC[j][0] != "M1" or BC[j + NP][0] != "M3" or BC[j][1:] != BC[j + NP][1:] for j in range(NP)) or any(len(T[t]) < 1 for t in T):
            stop(2, "A8: the transcripts do not form M1 / M3 pairs with a turn 1")
        P12 = {p["item"] for p in json.loads((INP / "panel.json").read_text(encoding="utf-8"))["panel"]}
        A5I = [x["item"] for x in json.loads((INP / "a5_items.json").read_text(encoding="utf-8"))["items"]]
        PROBES = [x["item"] for x in json.loads((INP / "a8_items.json").read_text(encoding="utf-8"))["items"]]
        if len(PROBES) != 120 or len(set(PROBES)) != 120 or set(PROBES) & (P12 | set(A5I)): stop(2, "a8_items.json: not 120 distinct items outside the panel and A5")
        REREAD = A5I[:2] if SMOKE else A5I[:8]
        if SMOKE: PROBES = PROBES[:4]
        CELLS8 = (("M1.M1", 0, 0), ("M3.M3", 1, 1), ("M1.M3", 0, 1), ("M3.M1", 1, 0))   # (label, user turn from M1 0 / M3 1, reply from)
        say(f"A8 design: {NP} M1 / M3 pairs × {len(CELLS8)} cells × drift / filler × {len(PROBES)} items at k = 1, + re-read {len(REREAD)} A5 items × {len(T)} transcripts")
        def cell_rows(j, c, i):
            """{cond: (prefix ids, cut)}, suffix for pair j × cell c × item i; filler keyed by the user turn's transcript."""
            _, us, rs = CELLS8[c]; tu, tr = (j, j + NP)[us], (j, j + NP)[rs]
            pairs = [(T[tu][0][0], T[tr][0][1])]
            if PLANT == "splicebreak" and j == 0 and c == 2: pairs = [(pairs[0][0], pairs[0][1][:-1] + [pairs[0][1][-1] + 1])]
            st = D.system_text(C[i]["system"], D.PERSONAS[BC[j][1]])
            return ({"drift": D.context(enc, st, pairs, 1), "filler": D.context(enc, st, D.filler_pairs(enc, POOL, pairs, tu), 1)},
                    D.probe_suffix(enc, C[i]["user"]))
        RU, RA, RS_ = enc("user"), enc("assistant"), enc("system")
        def check8(j, c, i, rows):
            """Problems with one pair × cell × item (empty = OK)."""
            _, us, rs = CELLS8[c]; tu, tr = (j, j + NP)[us], (j, j + NP)[rs]; p = []
            (di, dc), (fi, fc) = rows["drift"], rows["filler"]
            tt = D.turns_of(enc, di)
            if [r for r, _ in tt] != [RS_, RU, RA]: return [f"pair {j} {CELLS8[c][0]}: drift turns are not system / user / assistant"]
            if tt[1][1] != list(T[tu][0][0]) or tt[2][1] != list(T[tr][0][1]): p.append(f"pair {j} {CELLS8[c][0]}: spliced turn ≠ its source transcript's generated ids")
            tf = D.turns_of(enc, fi)
            if dc != fc or [len(x) for _, x in tf] != [len(x) for _, x in tt] or tf[0][1] != tt[0][1]: p.append(f"pair {j} {CELLS8[c][0]}: filler not token-matched to the drift")
            if c < 2:                                            # unspliced: = A5's own rows (drift01_core.q0_rows) at k = 1
                q = D.q0_rows(enc, POOL, C[i], D.PERSONAS[BC[tu][1]], T[tu], T[tu], tu, (0, 1))
                if di[:dc[1]] != q["drift"][0][:q["drift"][1][1]] or fi[:fc[1]] != q["filler"][0][:q["filler"][1][1]]:
                    p.append(f"pair {j} {CELLS8[c][0]}: unspliced row ≠ A5's q0_rows")
            return p
        # ---------------------------------------------------------- row checks on EVERY pair × cell × item (stop), before any readout
        UNITS = [(j, c, i) for j in range(NP) for c in range(len(CELLS8)) for i in PROBES]; LMAX = 0
        for (j, c, i) in UNITS:
            rows, suf = cell_rows(j, c, i); pr = check8(j, c, i, rows)
            if pr: stop(3, f"A8 ROW CHECK FAILED ({C[i]['id']}): {'; '.join(pr[:3])}")
            LMAX = max(LMAX, rows["drift"][1][1] + len(suf))
        RCK = {"units": len(UNITS), "pairs": NP, "cells": [x[0] for x in CELLS8], "items": len(PROBES), "row_tokens_max": LMAX}
        (OUT / f"{TAG}a8_rowcheck.json").write_text(json.dumps(RCK, indent=1), encoding="utf-8")
        say(f"A8 row checks OK: {len(UNITS)} pair × cell × item; spliced turns = their sources' generated ids; filler token-matched; "
            f"unspliced cells = A5's q0_rows; longest row {LMAX} tokens")
        def read(ids, cut, suf):
            br = Brancher(M); br.prefill(ids[:cut[1]]); lp = br.probe(suf)
            return lp[TD], lp[TR], D.distance(cut, 1), lp[TD0], lp[TR0]
        def unit8(j, c, i):
            rows, suf = cell_rows(j, c, i); return {cond: read(*rows[cond], suf) for cond in ("drift", "filler")}, rows, suf
        # ---------------------------------------------------------- repeat check (stop) + single-pass vs fresh gap (reported)
        if not FAKE and len({TD, TR, TD0, TR0}) != 4: stop(2, "A8: the no-space DONE / READY tokens coincide with the readout tokens")
        rng = np.random.default_rng(D.check_seed(D.SEED_BOOT)); tc = time.time(); NCHK = 6 if SMOKE else 48; rep_bad, gaps = [], []
        for q in range(NCHK):
            j, c, i = UNITS[int(rng.integers(0, len(UNITS)))]; (r1, rows, suf), (r2, _, _) = unit8(j, c, i), unit8(j, c, i)
            if PLANT == "nondeterm": r2 = {k: (v[0] + 1e-9, *v[1:]) for k, v in r2.items()}
            if np.array(list(r1.values())).tobytes() != np.array(list(r2.values())).tobytes(): rep_bad.append((j, CELLS8[c][0], C[i]["id"]))
            cond = ("drift", "filler")[int(rng.integers(0, 2))]; ids, cut = rows[cond]; fresh = M.lp(D.row(ids, cut, suf, 1))
            gaps.append({"cell": CELLS8[c][0], "cond": cond, "gap": float(max(abs(r1[cond][0] - fresh[TD]), abs(r1[cond][1] - fresh[TR])))})
        GAP = {"n": NCHK, "what": "prefill + probe vs a fresh pass of the same row", "max": max(g["gap"] for g in gaps),
               "median": float(np.median([g["gap"] for g in gaps])), "rows": gaps}
        (OUT / f"{TAG}a8_gap_report.json").write_text(json.dumps(GAP, indent=1), encoding="utf-8")
        if rep_bad: stop(3, f"REPEAT CHECK FAILED: A8 units not bitwise reproducible: {rep_bad[:5]}")
        say(f"repeat check PASS ({NCHK} × 2, bitwise); gap vs fresh (reported): max {GAP['max']:.4f} median {GAP['median']:.4f} nats")
        per = (time.time() - tc) / (2 * NCHK); p2 = per * (len(UNITS) + len(REREAD) * len(T)); usd = spend() + p2 / 3600 * RATE
        say(f"PROJECTION A8 units ≈ {p2 / 3600:.2f} h → spend ≈ ${usd:.2f} (watchdog ${WATCH})")
        if usd >= WATCH or PLANT == "overbudget": stop(6, f"PROJECTION: A8 units would end at ≈ ${usd:.2f} ≥ ${WATCH}")
        # ---------------------------------------------------------- the re-read: first A5 items × every transcript, unspliced, k = 1 (reported)
        RR = []
        for t in T:
            for i in REREAD:
                watch(); q = D.q0_rows(enc, POOL, C[i], D.PERSONAS[BC[t][1]], T[t], T[t], t, (0, 1)); suf = q["drift"][2]
                for cond in ("drift", "filler"):
                    ids, cut, _ = q[cond]; RR.append((t, i, B.B6_CONDS.index(cond), *read(ids, cut, suf)))
        np.savez(OUT / f"{TAG}a8_reread.npz", rows=np.array(RR, np.float64), cols=np.array(["tid", "item", "cond", "lpD", "lpR", "dist_tokens", "lpD_ns", "lpR_ns"]))
        say(f"A8 re-read: {len(RR)} rows ({len(REREAD)} A5 items × {len(T)} transcripts × drift / filler, k = 1); spend ${spend():.2f}")
        # ---------------------------------------------------------- rows: every pair × cell × item × drift / filler
        R9 = []
        for n_, (j, c, i) in enumerate(UNITS):
            watch(); res, _, _ = unit8(j, c, i)
            R9 += [(j, c, cc, i, *res[cond]) for cc, cond in enumerate(("drift", "filler"))]
            if (n_ + 1) % 2000 == 0: say(f"A8 unit {n_ + 1} / {len(UNITS)}: spend ${spend():.2f}")
        np.savez(OUT / f"{TAG}a8_q0.npz", rows=np.array(R9, np.float64),
                 cols=np.array(["pair", "cell", "cond", "item", "lpD", "lpR", "dist_tokens", "lpD_ns", "lpR_ns"]),
                 cells=np.array([x[0] for x in CELLS8]), conds=np.array(["drift", "filler"]), pair_persona=np.array([BC[j][1] for j in range(NP)]),
                 pair_temp=np.array([BC[j][2] for j in range(NP)], np.float64), pair_seed=np.array([BC[j][3] for j in range(NP)], np.int64))
        say(f"A8 Q0: {len(R9)} rows; spend ${spend():.2f}")
    if PHASE == "i":
        import functools
        PROBES = sorted(x["item"] for x in json.loads((INP / "a7_items.json").read_text(encoding="utf-8"))["items"])
        DM = {x["item"]: x["draws"] for x in json.loads((INP / "a7_demos.json").read_text(encoding="utf-8"))["demos"]}
        if sorted(DM) != PROBES or len(PROBES) != 120 or any(len(v) != 8 or any(len(l) != A6.NMAX for l in v) for v in DM.values()):
            stop(2, "a7_demos.json: not 120 probes × 8 draws × 8 demos over the A7 items")
        GATE = PROBES[:2] if SMOKE else PROBES[:8]                # A10.1: the first 8 A7 probes (sorted, as A7's rows)
        if SMOKE: PROBES = PROBES[:4]
        ND = 2 if SMOKE else 8; AI = {a: n for n, a in enumerate(A6.ARMS)}; ANCHOR = len(A6.ARMS); RI = {r: n for n, r in enumerate(A10.RENDERS)}
        if PLANT == "a10hdr":                                     # FAKE plant: one headers row keeps a user header → the row check stops
            _rw = A10.rows
            def _bad(enc_, C_, p_, d_, r_):
                R_, s_ = _rw(enc_, C_, p_, d_, r_)
                if r_ == "headers" and p_ == PROBES[0]:
                    R_["obey"] = {n: A10._sub(x, enc(D.H(A10.NAMES[0])), enc(D.H("user"))) for n, x in R_["obey"].items()}
                return R_, s_
            A10.rows = _bad
        @functools.lru_cache(maxsize=8)
        def build(p, d, r): return A10.rows(enc, C, p, DM[p][d], r)
        say(f"A10 design: {len(PROBES)} probes × {ND} draws × {len(A6.ARMS)} arms × n ∈ {A6.NS} × renderings {A10.RENDERS}, probe C, + 1 anchor per probe")
        # ---------------------------------------------------------- row checks on EVERY probe × draw × rendering (stop)
        L0, LMAX = {}, {r: 0 for r in A10.RENDERS}
        for p in PROBES:
            L0[p] = len(A10.anchor(enc, C, p)[0])
            for d in range(ND):
                for r in A10.RENDERS:
                    try: R_, suf = build(p, d, r)
                    except AssertionError as e: stop(3, f"A10 rows ({C[p]['id']}, draw {d}, {r}): {e}")
                    pr = A10.check(enc, C, p, DM[p][d], r, R_, suf)
                    if pr: stop(3, f"A10 ROW CHECK FAILED ({C[p]['id']}, draw {d}, {r}): {'; '.join(pr[:3])}")
                    LMAX[r] = max(LMAX[r], max(len(R_[a][A6.NMAX]) for a in A6.ARMS) + len(suf))
        RCK = {"probe_draws": len(PROBES) * ND, "renders": list(A10.RENDERS), "arms": list(A6.ARMS), "ns": list(A6.NS), "row_tokens_max": LMAX,
               "names": list(A10.NAMES), "stated": A10.STATED, "quote_head": A10.QUOTE_HEAD}
        (OUT / f"{TAG}a10_rowcheck.json").write_text(json.dumps(RCK, indent=1), encoding="utf-8")
        say(f"A10 row checks OK: {RCK['probe_draws']} probe × draw × {len(A10.RENDERS)} renderings, arms token-identical but for the "
            f"DONE / READY swaps, native = a6_core.rows; longest rows {LMAX}")
        def unit10(p, d, arm, r):
            """One probe × draw × arm × rendering, n DESCENDING (A3.3): nested renderings one prefill + crop; quoted one prefill per n."""
            R_, suf = build(p, d, r); res = {}; br = None
            if A10.NESTED[r]: br = Brancher(M); br.prefill(R_[arm][A6.NMAX])
            for n in sorted(A6.NS, reverse=True):
                if A10.NESTED[r]: br.crop_to(len(R_[arm][n]))
                else: br = Brancher(M); br.prefill(R_[arm][n])
                lp = br.probe(suf); res[n] = (lp[TD], lp[TR], len(R_[arm][n]) - L0[p], lp[TD0], lp[TR0])
            return res
        if not FAKE and len({TD, TR, TD0, TR0}) != 4: stop(2, "A10: the no-space DONE / READY tokens coincide with the readout tokens")
        # ---------------------------------------------------------- REPRO GATE: native vs A7's locked C rows (stop)
        ref = np.load(INP / (("FAKE_" if FAKE else "REAL_") + "a7_q0.npz"))["rows"]
        RF = {(int(x[0]), int(x[1]), int(x[2]), int(x[3])): (x[4], x[5]) for x in ref if int(x[9]) == 0}
        RP, dev = [], []
        for p in GATE:
            ids, suf = A10.anchor(enc, C, p); br = Brancher(M); br.prefill(ids); lp = br.probe(suf)
            RP.append((p, -1, ANCHOR, 0, lp[TD], lp[TR], *RF[(p, -1, ANCHOR, 0)]))
            for d in range(ND):
                for a in A6.ARMS:
                    for n, v in unit10(p, d, a, "native").items(): RP.append((p, d, AI[a], n, v[0], v[1], *RF[(p, d, AI[a], n)]))
        RP = np.array(RP, np.float64)
        if PLANT == "reprooff": RP[0, 4] += 0.1
        dev = np.abs(RP[:, 4:6] - RP[:, 6:8]).max(1); bw = int((RP[:, 4:6] == RP[:, 6:8]).all(1).sum())
        np.savez(OUT / f"{TAG}a10_repro.npz", rows=RP, cols=np.array(["item", "draw", "arm", "n", "lpD", "lpR", "a7_lpD", "a7_lpR"]))
        REP = {"n": len(RP), "bitwise": bw, "max": float(dev.max()), "median": float(np.median(dev)), "tol": REPRO_TOL10, "probes": [int(x) for x in GATE]}
        (OUT / f"{TAG}a10_repro.json").write_text(json.dumps(REP, indent=1), encoding="utf-8")
        if dev.max() > REPRO_TOL10: stop(3, f"REPRO GATE FAILED: native vs A7's C rows max |Δ| {dev.max():.4f} > {REPRO_TOL10} nats")
        say(f"repro gate PASS: native vs A7's C rows, {len(RP)} rows, bitwise {bw}, max |Δ| {dev.max():.4f}, median {np.median(dev):.4f} nats")
        # ---------------------------------------------------------- repeat check (stop) + single-pass vs fresh gap (reported)
        KEYS = [(p, d, a, r) for p in PROBES for d in range(ND) for r in A10.RENDERS for a in A6.ARMS]
        rng = np.random.default_rng(D.check_seed(D.SEED_BOOT)); tc = time.time(); NCHK = 6 if SMOKE else 48; rep_bad, gaps = [], []
        for q in range(NCHK):
            p, d, a, r = KEYS[int(rng.integers(0, len(KEYS)))]; r1, r2 = unit10(p, d, a, r), unit10(p, d, a, r)
            if PLANT == "nondeterm": r2 = {n: (v[0] + 1e-9, *v[1:]) for n, v in r2.items()}
            if np.array(list(r1.values())).tobytes() != np.array(list(r2.values())).tobytes(): rep_bad.append((C[p]["id"], d, a, r))
            n = A6.NS[int(rng.integers(0, len(A6.NS)))]; R_, suf = build(p, d, r); fresh = M.lp(R_[a][n] + suf)
            gaps.append({"render": r, "arm": a, "n": n, "gap": float(max(abs(r1[n][0] - fresh[TD]), abs(r1[n][1] - fresh[TR])))})
        GAP = {"n": NCHK, "what": "prefill (+ descending-n crop for nested renderings) vs a fresh pass", "max": max(g["gap"] for g in gaps),
               "median": float(np.median([g["gap"] for g in gaps])), "rows": gaps}
        (OUT / f"{TAG}a10_gap_report.json").write_text(json.dumps(GAP, indent=1), encoding="utf-8")
        if rep_bad: stop(3, f"REPEAT CHECK FAILED: A10 units not bitwise reproducible: {rep_bad[:5]}")
        say(f"repeat check PASS ({NCHK} × 2, bitwise); gap vs fresh (reported): max {GAP['max']:.4f} median {GAP['median']:.4f} nats")
        per = (time.time() - tc) / (2 * NCHK); p2 = per * len(KEYS); usd = spend() + p2 / 3600 * RATE
        say(f"PROJECTION A10 units ≈ {p2 / 3600:.2f} h → spend ≈ ${usd:.2f} (watchdog ${WATCH})")
        if usd >= WATCH or PLANT == "overbudget": stop(6, f"PROJECTION: A10 units would end at ≈ ${usd:.2f} ≥ ${WATCH}")
        # ---------------------------------------------------------- rows: anchors (n = 0, once per probe, render −1) + every unit
        R10 = []
        for p in PROBES:
            ids, suf = A10.anchor(enc, C, p); br = Brancher(M); br.prefill(ids); lp = br.probe(suf)
            R10.append((p, -1, ANCHOR, 0, lp[TD], lp[TR], 0, lp[TD0], lp[TR0], -1))
        for n_, (p, d, a, r) in enumerate(KEYS):
            watch(); R10 += [(p, d, AI[a], n, *v, RI[r]) for n, v in unit10(p, d, a, r).items()]
            if (n_ + 1) % 1000 == 0: say(f"A10 unit {n_ + 1} / {len(KEYS)}: spend ${spend():.2f}")
        np.savez(OUT / f"{TAG}a10_q0.npz", rows=np.array(R10, np.float64),
                 cols=np.array(["item", "draw", "arm", "n", "lpD", "lpR", "dist_tokens", "lpD_ns", "lpR_ns", "render"]),
                 arms=np.array(A6.ARMS + ("anchor",)), renders=np.array(A10.RENDERS))
        say(f"A10 Q0: {len(R10)} rows; one-pass prefill fell back to the 4,096 grid {Brancher.grid_used} time(s); spend ${spend():.2f}")
    if PHASE == "j":
        import re
        DV = len(B.B6_CONDS)                                    # cond index 4 = "diverse" (B6_CONDS' 0–3 unchanged)
        # ---------------------------------------------------------- RESUME: the frozen B-b transcripts, verified (as E)
        BSEEDS = B.B5_SEEDS[:2] if SMOKE else B.B5_SEEDS
        BC = [(m, p, t, s) for m in B.B5_MODES for p in PERS for t in TEMPS for s in BSEEDS]
        R = INP / os.environ["DRIFT_RESUME"]; mf = R / f"{TAG}b5_transcripts_manifest.json"
        if sha(mf) != os.environ.get("DRIFT_RESUME_MANIFEST_SHA", ""): stop(2, "RESUME: B-b transcripts manifest is not the pinned one")
        man0 = json.loads(mf.read_text(encoding="utf-8"))
        if [tuple(c) for c in man0["cells"]] != BC: stop(2, "RESUME: the frozen B-b transcripts are a different design")
        Zr = np.load(R / f"{TAG}b5_transcripts.npz"); flat = {}
        for q in range(len(Zr["tid"])): flat.setdefault(int(Zr["tid"][q]), []).append(Zr["ids"][Zr["off"][q]:Zr["off"][q + 1]].tolist())
        T = {t: list(zip(v[0::2], v[1::2])) for t, v in flat.items()}
        if PLANT == "resumetamper": u, a = T[0][0]; T[0][0] = (u, a[:-1] + [a[-1] + 1])
        probs = D.verify_frozen(T, man0["sha"])
        if probs: stop(3, "RESUME FREEZE: " + "; ".join(probs[:5]))
        T = {t: p for t, p in T.items() if t < B.WI_TID0}
        if sorted(T) != list(range(len(BC))): stop(2, f"RESUME: main transcripts {sorted(T)[:3]}… ≠ 0..{len(BC) - 1}")
        say(f"RESUMED: {len(T)} frozen B-b main transcripts loaded + verified (manifest {sha(mf)[:16]})")
        rf = R / f"{TAG}a5_q0.npz"
        if not rf.is_file(): stop(2, "A11: A5's a5_q0.npz is not in the resume folder")
        if REAL and sha(rf) != A5_REAL_Q0: stop(2, "A11: a5_q0.npz is not the locked A5 run's")
        A5I = [x["item"] for x in json.loads((INP / "a5_items.json").read_text(encoding="utf-8"))["items"]]
        if len(A5I) != 120 or len(set(A5I)) != 120: stop(2, "a5_items.json: not 120 distinct items")
        REPI = A5I[:2] if SMOKE else A5I[:8]                     # A11.1 gate: the first 8 A5 items (a5_items.json order)
        ITEMS = A5I[:4] if SMOKE else A5I
        PROSE = enc((INP / "pg1228_prose.txt").read_text(encoding="utf-8"))
        BOOKS = [enc((INP / f).read_text(encoding="utf-8")) for f in A11.FILES]
        if PLANT == "diversebreak":                              # FAKE plant: one diverse turn a token short → the match check stops it
            _dp = A11.diverse_pairs
            A11.diverse_pairs = lambda bk, pa, t: (lambda o: ([(o[0][0][0][:-1], o[0][0][1])] + o[0][1:], o[1]))(_dp(bk, pa, t))
        if PLANT == "samebook":                                  # FAKE plant: turn 2 reuses turn 1's book → the book check stops it
            _dp2 = A11.diverse_pairs
            A11.diverse_pairs = lambda bk, pa, t: (lambda o: (o[0], o[1][:1] + o[1][:1] + o[1][2:]))(_dp2(bk, pa, t))
        say(f"A11 design: {len(T)} transcripts × ({len(REPI)} A5 items × 3 repro + {len(ITEMS)} A5 items × diverse), k ∈ {KQ0}; "
            f"books {[(g, len(b)) for (g, _), b in zip(A11.POOL, BOOKS)]} tokens")
        PER = {t: D.PERSONAS[BC[t][1]] for t in T}
        def unit_j(t, i):
            """One (transcript, item), diverse arm: ONE prefill pass, probes in DESCENDING k (A3.3)."""
            try: ids, cut, suf, bix = A11.diverse_row(enc, BOOKS, C[i], PER[t], T[t], t, KQ0)
            except AssertionError as e: stop(3, f"A11 diverse row ({C[i]['id']}, t{t}): {e}")
            ks = sorted((k for k in KQ0 if k in cut), reverse=True); br = Brancher(M); br.prefill(ids[:cut[ks[0]]]); res = {}
            for k in ks:
                br.crop_to(cut[k]); lp = br.probe(suf); res[k] = (lp[TD], lp[TR], D.distance(cut, k))
            return res, (ids, cut, suf), bix
        # ---------------------------------------------------------- REPRO GATE: the first 8 A5 items × drift / filler / prose vs A5's a5_q0 (stop)
        ref = {tuple(int(x) for x in r[:4]): r[4:6] for r in np.load(rf)["rows"]}
        RP, tp = [], time.time()
        for t in T:
            for i in REPI:
                watch()
                try: rows = B.b6_rows(enc, POOL, PROSE, C[i], PER[t], T[t], t, KQ0)
                except AssertionError as e: stop(3, f"A11 gate rows ({C[i]['id']}, t{t}): {e}")
                for cond in ("drift", "filler", "prose"):
                    c = B.B6_CONDS.index(cond); ids, cut, suf = rows[cond]; ks = sorted((k for k in KQ0 if k in cut), reverse=True)
                    br = Brancher(M); br.prefill(ids[:cut[ks[0]]])
                    for k in ks:
                        br.crop_to(cut[k]); lp = br.probe(suf); key = (t, i, c, k)
                        if key not in ref: stop(2, f"A11 REPRO GATE: a5_q0 row missing {key}")
                        got = np.array([lp[TD], lp[TR]]) + (1.0 if PLANT == "reprobreak" and key == (0, REPI[0], 1, 4) else 0.0)
                        RP.append((t, i, c, k, *got, *ref[key], D.distance(cut, k)))
        RP = np.array(RP, np.float64); dmax = np.abs(RP[:, 4:6] - RP[:, 6:8]).max(1)
        np.savez(OUT / f"{TAG}a11_repro.npz", rows=RP, cols=np.array(["tid", "item", "cond", "k", "lpD", "lpR", "a5_lpD", "a5_lpR", "dist_tokens"]))
        REP = {"n": len(RP), "bitwise": int((RP[:, 4:6] == RP[:, 6:8]).all(1).sum()), "max": float(dmax.max()), "median": float(np.median(dmax)),
               "tol": REPRO_TOL11, "items": [int(x) for x in REPI]}
        (OUT / f"{TAG}a11_repro.json").write_text(json.dumps(REP, indent=1), encoding="utf-8")
        say(f"A11 REPRO GATE vs A5 a5_q0: {REP['n']} rows, bitwise {REP['bitwise']} / {REP['n']}, max |Δ| {REP['max']:.4g}, median {REP['median']:.4g} nats, {time.time() - tp:.0f} s, spend ${spend():.2f}")
        if not REP["max"] <= REPRO_TOL11: stop(3, f"A11 REPRO GATE FAILED: max |Δ| {REP['max']:.4g} > {REPRO_TOL11} nats vs A5's a5_q0")
        # ---------------------------------------------------------- repeat check (stop) + single-pass vs fresh gap (reported)
        J_ = [(t, i) for t in T for i in ITEMS]
        rng = np.random.default_rng(D.check_seed(D.SEED_BOOT)); tc = time.time(); NCHK = 6 if SMOKE else 48; rep_bad, gaps = [], []
        for q in range(NCHK):
            t, i = J_[int(rng.integers(0, len(J_)))]; r1, rows, _ = unit_j(t, i); r2, _, _ = unit_j(t, i)
            if PLANT == "nondeterm": r2 = {k: (v[0] + 1e-9, *v[1:]) for k, v in r2.items()}
            if np.array(list(r1.values())).tobytes() != np.array(list(r2.values())).tobytes(): rep_bad.append((t, C[i]["id"]))
            k = sorted(r1)[int(rng.integers(0, len(r1)))]; fresh = M.lp(D.row(*rows, k))
            gaps.append({"k": k, "gap": float(max(abs(r1[k][0] - fresh[TD]), abs(r1[k][1] - fresh[TR])))})
        GAP = {"n": NCHK, "what": "single-pass prefill + descending-k crop vs a fresh pass", "max": max(g["gap"] for g in gaps),
               "median": float(np.median([g["gap"] for g in gaps])), "rows": gaps}
        (OUT / f"{TAG}a11_gap_report.json").write_text(json.dumps(GAP, indent=1), encoding="utf-8")
        if rep_bad: stop(3, f"REPEAT CHECK FAILED: A11 units not bitwise reproducible: {rep_bad[:5]}")
        say(f"repeat check PASS ({NCHK} × 2, bitwise); gap vs fresh (reported): max {GAP['max']:.4f} median {GAP['median']:.4f} nats")
        per = (time.time() - tc) / (2 * NCHK); p2 = per * len(J_); usd = spend() + p2 / 3600 * RATE
        say(f"PROJECTION A11 units ≈ {p2 / 3600:.2f} h → spend ≈ ${usd:.2f} (watchdog ${WATCH})")
        if usd >= WATCH or PLANT == "overbudget": stop(6, f"PROJECTION: A11 units would end at ≈ ${usd:.2f} ≥ ${WATCH}; repro gate kept")
        # ---------------------------------------------------------- diverse passages: book per turn + target-family counts per book (A11.4 S6, reported)
        RX = {w: re.compile(r"\b(" + "|".join(v) + r")\b", re.I) for w, v in
              {"DONE": ("done", "finished", "complete", "completed"), "READY": ("ready", "prepared", "set")}.items()}
        DI = {}
        for t in T:
            dp, bix = A11.diverse_pairs(BOOKS, T[t][:max(KQ0)], t); turns = [x for pr in dp for x in pr]
            pb = {g: {"ntok": 0, "DONE": 0, "READY": 0, "turns": 0} for g, _ in A11.POOL}
            for ids_, b in zip(turns, bix):
                g = A11.POOL[b][0]; txt = dec(ids_); pb[g]["ntok"] += len(ids_); pb[g]["turns"] += 1
                for w, rx in RX.items(): pb[g][w] += len(rx.findall(txt))
            DI[t] = {"ntok": sum(len(x) for x in turns), "books": [A11.POOL[b][0] for b in bix], "per_book": pb,
                     **{w: sum(v[w] for v in pb.values()) for w in RX}}
        (OUT / f"{TAG}a11_diverse.json").write_text(json.dumps(DI, indent=1), encoding="utf-8")
        # ---------------------------------------------------------- the 120 A5 items × diverse (cond index 4)
        R11 = []
        for n_, (t, i) in enumerate(J_):
            watch(); res, _, _ = unit_j(t, i); R11 += [(t, i, DV, k, *v) for k, v in res.items()]
            if (n_ + 1) % 1000 == 0: say(f"A11 unit {n_ + 1} / {len(J_)}: spend ${spend():.2f}")
        np.savez(OUT / f"{TAG}a11_q0.npz", rows=np.array(R11, np.float64), cols=np.array(["tid", "item", "cond", "k", "lpD", "lpR", "dist_tokens"]),
                 conds=np.array(B.B6_CONDS + ("diverse",)))
        say(f"A11 Q0: {len(R11)} rows; one-pass prefill fell back to the 4,096 grid {Brancher.grid_used} time(s); spend ${spend():.2f}")
    status, code = "DONE", 0
except Watchdog as e:
    status, code = f"WATCHDOG: {e} — outputs written so far are PARTIAL", 5
    (OUT / f"{TAG}STOP_WATCHDOG.txt").write_text(status + "\n", encoding="utf-8")
(OUT / f"{TAG}ledger.json").write_text(json.dumps({"rate_per_h": RATE, "t0": T0, "elapsed_h": (time.time() - T0) / 3600,
                                                    "spend_usd": spend(), "watchdog_usd": WATCH, "status": status}, indent=1), encoding="utf-8")
(OUT / f"{TAG}checks.json").write_text(json.dumps({"versions": VER, "status": status, "plant": PLANT or None, "phase": "B-" + PHASE}, indent=1), encoding="utf-8")
say(status); flush_log(); sys.exit(code)
