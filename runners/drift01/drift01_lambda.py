"""HUNT-DRIFT-01 piece 3 — the runner (EXPLORATORY; PLAN v0.3 locked fc6b8958…). One process, one instance.
  FAKE=1 [SMOKE=1] [PLANT=<name>] DRIFT_INPUTS=<dir> DRIFT_OUT=<empty dir> python drift01_lambda.py
  REAL=1 [SMOKE=1] DRIFT_INPUTS=<dir> DRIFT_OUT=<empty dir> RATE_PER_H=<$> INSTANCE_T0=<unix s> python drift01_lambda.py
Order: pins → model → BIT-CHECK (before any generation) → Phase 1 (generate, freeze) → freeze verify → REPEAT CHECK +
GAP REPORT (Amendment 1 A1.1) → Phase 2 (Q0 + Q1 branched off one prefill per transcript × item × condition) → Q1 full battery (depth 0) →
Phase 4 (per-turn L8 / L16 pooled residuals, drift + filler). The watchdog stops cleanly at $22 (the launcher kills at
$25). Every output file carries the run tag (FAKE_ / REAL_ [+ SMOKE_]); the output folder must start empty.
Exit: 0 done · 2 a pin / guard refused · 3 a STOP rule (bit-check, cache-branch, freeze, slot) · 5 watchdog ·
6 projection (after PROJ_TURNS Phase-1 turns, and again after the cache-branch check: the projected spend would reach
the watchdog → stop BEFORE spending it). Generation runs in sub-batches of ≤ DRIFT_BATCH (default 12) sequences."""
import hashlib, json, os, sys, time
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D

FAKE, REAL, SMOKE = os.environ.get("FAKE") == "1", os.environ.get("REAL") == "1", os.environ.get("SMOKE") == "1"
PLANT = os.environ.get("PLANT", "")
if FAKE == REAL: sys.exit("exactly one of FAKE=1 / REAL=1")
if PLANT and not FAKE: sys.exit("PLANT is FAKE-only")
TAG = ("FAKE_" if FAKE else "REAL_") + ("SMOKE_" if SMOKE else "")
INP, OUT = Path(os.environ["DRIFT_INPUTS"]), Path(os.environ["DRIFT_OUT"])
OUT.mkdir(parents=True, exist_ok=True)
if any(p for p in OUT.iterdir() if not p.name.startswith(".")):     # dot-files = the watchdog's key, never outputs
    sys.exit(f"{OUT} is not empty (no clobber)")
WATCH = float(os.environ.get("WATCH_USD", "22"))          # the launcher sets it to its cap − $3 (2026-10-25)
if not 0 < WATCH <= 60: sys.exit(f"WATCH_USD {WATCH} outside (0, 60]")
RATE = float(os.environ.get("RATE_PER_H", "0" if FAKE else "nan"))
RESUME = bool(os.environ.get("DRIFT_RESUME"))             # load an earlier run's frozen transcripts; Phase 1 skipped
T0 = float(os.environ.get("INSTANCE_T0", time.time()))
if REAL and not np.isfinite(RATE): sys.exit("REAL needs RATE_PER_H (from the Lambda API)")
LOG = []
def say(*a):
    s = " ".join(str(x) for x in a); LOG.append(s); print("[D1]", s, flush=True)
def spend(): return (time.time() - T0) / 3600 * RATE
class Watchdog(Exception): pass
def watch():
    if spend() >= WATCH: raise Watchdog(f"spend ${spend():.2f} ≥ ${WATCH}")
def stop(code, why):
    (OUT / f"{TAG}STOP.txt").write_text(why + "\n", encoding="utf-8"); say("STOP", code, why)
    (OUT / f"{TAG}ledger.json").write_text(json.dumps({"rate_per_h": RATE, "t0": T0, "elapsed_h": (time.time() - T0) / 3600,
                                                        "spend_usd": spend(), "status": f"STOP {code}: {why}"}, indent=1), encoding="utf-8")
    flush_log(); sys.exit(code)
def flush_log(): (OUT / f"{TAG}run.log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

# ------------------------------------------------------------------ pins (LOG.md lock + piece records)
PINS = {"panel.json": "718732502b66acdb46f3f85700cbb659be5f6da1b2bfe818ba1f53c000fcd963",
        "intention_forms.json": "4e1f6b17425e4f1b18ede2ec9d40ccb2c7ec577ade18f8d7be2a6918d3ef5877",
        "word_pool_drift01.txt": "c26f8dd661ece2026df0dc57a2fa96541adf3e8ece92c5c08d53e8ee944d2aae",
        "stimuli_contested.jsonl": "d4145f1add05ec293d210ce40fe2ad3b858cc6abc2a4b86761e6f04573e629b4"}
CORE_SHA = "5f06a0916ba9c63d"          # Amendment 2 core (K to 32; "shuffled" → "cross")
for n, h in PINS.items():
    if sha(INP / n) != h: stop(2, f"{n} hash mismatch")
if sha(HERE / "drift01_core.py")[:16] != CORE_SHA: stop(2, "drift01_core.py is not the recorded piece-2 core")
if REAL:
    for n, h in json.loads((INP / "pilot_pins.json").read_text(encoding="utf-8")).items():
        if sha(INP / n) != h: stop(2, f"{n} hash mismatch")
C = [json.loads(l) for l in open(INP / "stimuli_contested.jsonl", encoding="utf-8")]
PANEL = [p["item"] for p in json.loads((INP / "panel.json").read_text(encoding="utf-8"))["panel"]]
PANEL = [PANEL[j] for j in range(12) if j % 3 in (0, 1)]       # Amendment 2 A2.2: the first two of each cell → 8 items
FORMS = json.loads((INP / "intention_forms.json").read_text(encoding="utf-8"))["forms"]
POOL = (INP / "word_pool_drift01.txt").read_text(encoding="utf-8").split()
say("pins OK", TAG, "smoke" if SMOKE else "full")

# ------------------------------------------------------------------ design (PLAN §3–§4), SMOKE = a thin slice
MODES, TEMPS = ("M1", "M2", "M3"), (0.7, 1.0)
PERS = tuple(D.PERSONAS)
SEEDS = D.GEN_SEEDS[:2] if SMOKE else D.GEN_SEEDS
NTURN = 8 if SMOKE else 32                 # Amendment 1 A1.2 (was 64)
def gseed(*parts):
    """Amendment 1 A1.3: a generation call's torch seed = a hash of (generation seed, mode, temperature, turn, role,
    sub-batch offset) — no two cells share a sampling stream (smoke #1: M1 and M2 shared turn 1)."""
    return int(hashlib.sha256(repr(parts).encode()).hexdigest()[:15], 16)
KQ0 = tuple(k for k in D.K_Q0 if k <= NTURN); KQ1 = tuple(k for k in D.K_Q1 if k <= NTURN)
if SMOKE: MODES, TEMPS, PERS, PANEL = ("M1", "M2"), (1.0,), ("P-none", "P-curious"), PANEL[:2]
FULL_ITEMS = list(range(10)) if SMOKE else list(range(len(C)))
BUDGET, MAXNEW = 24576, 256
BATCH, PROJ_TURNS = int(os.environ.get("DRIFT_BATCH", "12")), 3
CELLS = [(m, p, t, s) for m in MODES for p in PERS for t in TEMPS for s in SEEDS]   # transcript id = index
WITH_I = ([("M1", p, 1.0, SEEDS[0], PANEL[0]) for p in PERS] if SMOKE else
          [("M1", p, 1.0, s, it) for p in PERS for s in D.GEN_SEEDS[:2] for it in (PANEL[0], PANEL[4])])   # c0144, c0525
if PLANT == "badseed": CELLS[0] = (CELLS[0][0], CELLS[0][1], CELLS[0][2], 101)
for c in CELLS:
    try: D.check_seed(c[3])
    except SystemExit as e: stop(2, str(e))

# ------------------------------------------------------------------ model + tokenizer
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

class FakeModel:
    """Deterministic toy (d = 16): h_t = E[id] + 0.3·running mean of E + a system-block term; log-softmax over the full
    vocabulary from h_last. Generation samples pool words or <|eot_id|>. Exercises every path; means nothing."""
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
    def mem_gb(self): return 0.0
    def layers(self, ids):
        H = self.hidden(ids); return {8: H, 16: 1.1 * H}
    oomed = False
    def generate(self, contexts, temp, seed, maxnew):
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
        if PLANT == "cachedrift": lp = lp + 0.05                     # a constant gap: reported, not a stop
        if PLANT == "nondeterm": FakeBrancher.calls += 1; lp = lp + 1e-9 * FakeBrancher.calls   # not reproducible: a stop
        return lp
    calls = 0
    def pos(self): return len(self.ids)

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
    def layers(self, ids):
        import torch
        with torch.inference_mode():
            out = self.mdl(input_ids=torch.tensor([ids], device="cuda:0"), use_cache=False, output_hidden_states=True, num_logits_to_keep=1)
        return {L: out.hidden_states[L][0].float().cpu().numpy() for L in (8, 16)}
    STOPS = (128001, 128008, 128009)        # <|end_of_text|>, <|eom_id|>, <|eot_id|> = the model's own generation_config eos
    def generate(self, contexts, temp, seed, maxnew):
        """One batched turn: left-padded contexts, sampling at `temp`, stop at ANY of the model's three eos ids (passing
        only <|eot_id|> would let it run past <|end_of_text|> / <|eom_id|>). Content = tokens before the first stop.
        Deterministic algorithms are switched OFF for sampling only (not needed — the transcripts are frozen; some
        sampling / position-id kernels may refuse under them) and back ON for every readout. Seed = the batch's derived
        seed (torch.manual_seed); exact regeneration is NOT promised."""
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
    def mem_gb(self):
        import torch
        return torch.cuda.max_memory_allocated() / 2**30

class RealBrancher:
    """One sequence, one DynamicCache: extend the prefix in chunks; probe = append the suffix, read the last logits,
    crop the cache back. num_logits_to_keep = 1 throughout."""
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
    def pos(self): return self.n

enc, dec, M, VER = load()
Brancher = FakeBrancher if FAKE else RealBrancher
TD, TR = enc(" DONE")[-1], enc(" READY")[-1]
EOT_ID = enc(D.EOT)[0]
say("model loaded", json.dumps(VER))

if FAKE and os.environ.get("FAKE_MAKE_REF") == "1":      # test fixture: the FAKE stand-in for the pilot's open lp
    lp = [M.lp_pilot(D.row(*D.context(enc, D.system_text(C[i]["system"], ""), [], 0), D.probe_suffix(enc, C[i]["user"]), 0)) for i in PANEL]
    np.savez(OUT / "FAKE_pilot_lp.npz", lp=np.array([[x[TD], x[TR]] for x in lp], np.float32), lp_key=np.array([[0, i, 0] for i in PANEL], np.int16))
    say("FAKE reference written"); flush_log(); sys.exit(0)

try:
    # -------------------------------------------------------------- BIT-CHECK (PLAN §4.3) — before anything is generated
    ref = np.load(INP / ("FAKE_pilot_lp.npz" if FAKE else "pilot_lp_open.npz"))     # REAL: lp extract of the pilot's open file
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

    # -------------------------------------------------------------- Phase 1: generation (PLAN §3)
    def first_user(mode): return D.text_ids(enc, D.M3_PROMPT if mode == "M3" else D.CONTINUE)
    BSZ = {"n": BATCH}
    def gen_batched(ctxs, temp, seed):
        """M.generate in sub-batches of ≤ BSZ sequences (KV ≈ 131 KB / token / sequence on the 8B). The SMOKE never
        reaches long contexts, so a CUDA out-of-memory HALVES the sub-batch for the rest of the run and retries
        (logged), instead of crashing at turn ~40 of the full run."""
        out, b = [], 0
        while b < len(ctxs):
            n = BSZ["n"]
            try: out += M.generate(ctxs[b:b + n], temp, gseed(*seed, b), MAXNEW); b += n
            except Exception as e:
                if "out of memory" not in str(e).lower() or n == 1: raise
                if REAL: import torch; torch.cuda.empty_cache()
                BSZ["n"] = max(1, n // 2); say(f"OOM at sub-batch {n} → {BSZ['n']}")
        return out
    def run_group(group, temp, sys_of, b_sys=None, proj=None):
        """Generate NTURN pairs for every cell in `group` (same temperature), batched per turn. M2: B replies in turn.
        proj = {"weight": total sub-batch-turn weight of all of Phase 1 / this group's} → after PROJ_TURNS turns, fit
        seconds per turn = a + b·j and STOP (exit 6) if spend so far + projected Phase 1 ≥ the watchdog."""
        pairs = {g: [] for g in group}; live = list(group); cont = {g: first_user(g[0]) for g in group}; bpairs = {g: [] for g in group}
        tt = []
        for j in range(1, NTURN + 1):
            watch(); tj = time.time()
            ctx = {g: D.context(enc, sys_of(g), pairs[g], NTURN)[0] + D.turn(enc, "user", cont[g]) + enc(D.H("assistant")) for g in live}
            live = [g for g in live if len(ctx[g]) + 2 * MAXNEW < BUDGET]
            if not live: break
            gen = gen_batched([ctx[g] for g in live], temp, (group[0][3], group[0][0], temp, j, "A" if len(group[0]) == 4 else "W"))
            for g, (a, trunc) in zip(live, gen): pairs[g].append((cont[g], a)); cont[g] = D.text_ids(enc, D.CONTINUE)
            if b_sys is not None:                                 # M2: B sees A's turns as user, its own as assistant
                bctx = {g: D.context(enc, b_sys, bpairs[g], NTURN)[0] + D.turn(enc, "user", pairs[g][-1][1]) + enc(D.H("assistant")) for g in live}
                bgen = gen_batched([bctx[g] for g in live], temp, (group[0][3], group[0][0], temp, j, "B"))
                for g, (b, _) in zip(live, bgen): bpairs[g].append((pairs[g][-1][1], b)); cont[g] = b
            tt.append(time.time() - tj)
            say(f"phase 1 turn {j}: {len(live)} live, {tt[-1]:.1f} s, max ctx {max(map(len, ctx.values()))}, "
                f"peak mem {M.mem_gb():.1f} GB, sub-batch {BSZ['n']}, spend ${spend():.2f}")
            if proj is not None and j == PROJ_TURNS:
                b, a = np.polyfit(np.arange(1, j + 1), tt, 1); p1 = sum(max(a + b * x, 0) for x in range(1, NTURN + 1)) * proj["weight"]
                PROJ["phase1_s"] = p1; usd = spend() + p1 / 3600 * RATE
                say(f"PROJECTION phase 1 ≈ {p1 / 3600:.2f} h → spend at its end ≈ ${usd:.2f} (watchdog ${WATCH})")
                if usd >= WATCH or PLANT == "overbudget": stop(6, f"PROJECTION: phase 1 alone would end at ≈ ${usd:.2f} ≥ ${WATCH}; nothing kept but the log")
        return pairs
    PROJ = {}; T = {}; t1 = time.time()
    if RESUME:
        # RESUME (2026-10-25): Phase 1 is NOT re-run — the frozen transcripts of an earlier run are loaded, their
        # manifest must hash to the pinned DRIFT_RESUME_MANIFEST_SHA (the launcher takes it from a verified pull), the
        # design must be this run's, and every transcript must re-hash to the manifest (the same freeze check).
        R = INP / os.environ["DRIFT_RESUME"]; mf = R / f"{TAG}transcripts_manifest.json"
        if sha(mf) != os.environ.get("DRIFT_RESUME_MANIFEST_SHA", ""): stop(2, "RESUME: transcripts manifest is not the pinned one")
        man0 = json.loads(mf.read_text(encoding="utf-8"))
        if [tuple(c) for c in man0["cells"]] != CELLS: stop(2, "RESUME: the frozen transcripts are a different design")
        Zr = np.load(R / f"{TAG}transcripts.npz"); flat = {}
        for q in range(len(Zr["tid"])): flat.setdefault(int(Zr["tid"][q]), []).append(Zr["ids"][Zr["off"][q]:Zr["off"][q + 1]].tolist())
        T = {t: list(zip(v[0::2], v[1::2])) for t, v in flat.items()}
        if PLANT == "resumetamper": u, a = T[0][0]; T[0][0] = (u, a[:-1] + [a[-1] + 1])
        man = man0["sha"]; probs = D.verify_frozen(T, man)
        if probs: stop(3, "RESUME FREEZE: " + "; ".join(probs[:5]))
        for n in ("transcripts.npz", "transcripts.jsonl", "transcripts_manifest.json"):
            (OUT / f"{TAG}{n}").write_bytes((R / f"{TAG}{n}").read_bytes())
        say(f"RESUMED: {len(T)} frozen transcripts loaded + verified (manifest {sha(mf)[:16]}); Phase 1 skipped")
    groups = [] if RESUME else [(m, t, [c for c in CELLS if c[0] == m and c[2] == t]) for m in MODES for t in TEMPS]
    wt = lambda g, m: -(-len(g) // BATCH) * (2 if m == "M2" else 1)
    total_w = sum(wt(g, m) for m, _, g in groups) + (-(-len(WITH_I) // BATCH) if WITH_I else 0)
    for n, (m, t, grp) in enumerate(groups):
        got = run_group(grp, t, lambda g: D.PERSONAS[g[1]], D.B_SYSTEM if m == "M2" else None,
                        proj={"weight": total_w / wt(grp, m)} if n == 0 else None)
        for g in grp: T[CELLS.index(g)] = got[g]
    TW = {}
    if WITH_I and not RESUME:                                     # one batched group (all at T 1.0, M1)
        got = run_group(WITH_I, 1.0, lambda g: D.system_text(C[g[4]]["system"], D.PERSONAS[g[1]]))
        TW = {k: got[w] for k, w in enumerate(WITH_I)}
    if not RESUME:
        say(f"phase 1 done: {len(T)} transcripts + {len(TW)} with-instruction, {time.time() - t1:.0f} s")
        # freeze
        man = {str(t): D.transcript_sha(p) for t, p in T.items()}
        flat = [(t, j, r, x) for t, p in T.items() for j, (u, a) in enumerate(p) for r, x in ((0, u), (1, a))]
        np.savez(OUT / f"{TAG}transcripts.npz", ids=np.concatenate([np.asarray(x, np.int32) for *_, x in flat]) if flat else np.zeros(0, np.int32),
                 off=np.cumsum([0] + [len(x) for *_, x in flat]), tid=np.array([f[0] for f in flat]), turn=np.array([f[1] for f in flat]),
                 role=np.array([f[2] for f in flat]))
        with open(OUT / f"{TAG}transcripts.jsonl", "w", encoding="utf-8") as f:
            for t, p in T.items():
                m, pe, te, s = CELLS[t]
                f.write(json.dumps({"tid": t, "mode": m, "persona": pe, "temp": te, "seed": s, "n": len(p),
                                    "turns": [{"user": dec(u), "assistant": dec(a)} for u, a in p]}, ensure_ascii=False) + "\n")
            for w, p in TW.items():
                f.write(json.dumps({"with_instruction": w, "cell": list(WITH_I[w][:4]), "item": C[WITH_I[w][4]]["id"],
                                    "turns": [{"user": dec(u), "assistant": dec(a)} for u, a in p]}, ensure_ascii=False) + "\n")
        (OUT / f"{TAG}transcripts_manifest.json").write_text(json.dumps({"cells": [list(c) for c in CELLS], "sha": man}, indent=1), encoding="utf-8")
        say("frozen; manifest sha", sha(OUT / f"{TAG}transcripts_manifest.json"))
        if PLANT == "tamper": u, a = T[0][0]; T[0][0] = (u, a[:-1] + [a[-1] + 1])
        probs = D.verify_frozen(T, man)
        if probs: stop(3, "FREEZE: " + "; ".join(probs))

    # -------------------------------------------------------------- Q1 slot assertion (every item, every condition)
    for i in sorted(set(PANEL) | set(FULL_ITEMS)):
        for cond in D.Q1_CONDS:
            b = D.q1_block(enc, POOL, C[i], FORMS, cond, (i, D.Q1_CONDS.index(cond)))
            want = D.SLOT[cond] if not (PLANT == "wrongslot" and cond == "asst_imp") else "user"
            if D.q1_slot_of(enc, C[i], b) != want: stop(3, f"Q1 plant not in its declared slot: {C[i]['id']} {cond}")
    say("Q1 slots OK")

    # -------------------------------------------------------------- Phase 2 helpers
    def other(t):
        """Amendment 2 A2.1 (C-cross): the transcript of the SAME mode, temperature and seed under the NEXT persona in
        the cycle P-none → P-neutral → P-curious (over the personas this run has); probed under t's own system message."""
        m, p, T_, s = CELLS[t]; nxt = PERS[(PERS.index(p) + 1) % len(PERS)]
        return CELLS.index((m, nxt, T_, s))
    def unit(t, i, cond, rows, q1=False):
        """One prefill of the prefix, branched at every k: returns {k: lp pair}, {k: distance}, and Q1 {(cond1, k): lp}."""
        ids, cut, suf = rows[cond]; br = Brancher(M); res, dist, r1 = {}, {}, {}
        for k in sorted(cut):
            if k not in KQ0 and not (q1 and k in KQ1): continue
            br.extend(ids[br.pos():cut[k]])
            if k in KQ0: lp = br.probe(suf); res[k] = (lp[TD], lp[TR]); dist[k] = D.distance(cut, k)
            if q1 and k in KQ1:
                for c1 in D.Q1_CONDS:
                    lp = br.probe(D.q1_block(enc, POOL, C[i], FORMS, c1, (i, D.Q1_CONDS.index(c1)))); r1[(c1, k)] = (lp[TD], lp[TR])
        return res, dist, r1

    # -------------------------------------------------------------- Amendment 1 A1.1: REPEAT check (stop) + GAP report
    # (the locked 0.02-nat cache-branch tolerance assumed bf16 equivalence of the two paths; the fp32 diagnosis showed
    # the logic exact and the bf16 gap = rounding). Each pick: the branched unit TWICE (must be bitwise identical) +
    # one fresh pass (the |branched − fresh| distribution is REPORTED beside the pilot JITTER, not gated).
    rng = np.random.default_rng(D.check_seed(D.SEED_BOOT)); tc = time.time(); NCHK = 6 if SMOKE else 48; rep_bad, gaps = [], []
    for q in range(NCHK):
        t = int(rng.integers(0, len(CELLS))); i = PANEL[int(rng.integers(0, len(PANEL)))]; cond = D.Q0_CONDS[int(rng.integers(0, 5))]
        rows = D.q0_rows(enc, POOL, C[i], D.PERSONAS[CELLS[t][1]], T[t], T[other(t)], t, KQ0)
        ks = [k for k in KQ0 if k in rows[cond][1]]; k = ks[int(rng.integers(0, len(ks)))]
        r1, _, _ = unit(t, i, cond, rows); r2, _, _ = unit(t, i, cond, rows); fresh = M.lp(D.row(*rows[cond], k))
        if np.array(list(r1.values())).tobytes() != np.array(list(r2.values())).tobytes(): rep_bad.append((t, C[i]["id"], cond))
        gaps.append({"cond": cond, "k": k, "gap": float(max(abs(r1[k][0] - fresh[TD]), abs(r1[k][1] - fresh[TR])))})
    GAP = {"n": NCHK, "max": max(g["gap"] for g in gaps), "median": float(np.median([g["gap"] for g in gaps])),
           "by_cond": {c: float(np.median([g["gap"] for g in gaps if g["cond"] == c])) for c in {g["cond"] for g in gaps}},
           "jitter_sd_pilot": 0.2342, "rows": gaps}
    (OUT / f"{TAG}gap_report.json").write_text(json.dumps(GAP, indent=1), encoding="utf-8")
    if rep_bad: stop(3, f"REPEAT CHECK FAILED: branched readouts not bitwise reproducible: {rep_bad[:5]}")
    say(f"repeat check PASS ({NCHK} × 2 branched, bitwise); GAP branched vs fresh (reported): max {GAP['max']:.4f} median {GAP['median']:.4f} nats")
    # projection 2: one check pick ≈ two branched units + one fresh pass; the main loop has len(T) × panel × 5 units
    per = (time.time() - tc) / (2 * NCHK); p2 = per * len(T) * len(PANEL) * len(D.Q0_CONDS); usd = spend() + p2 / 3600 * RATE
    say(f"PROJECTION phase 2 ≈ {p2 / 3600:.2f} h (upper bound: check units include a fresh pass) → spend ≈ ${usd:.2f}")
    if usd >= WATCH: stop(6, f"PROJECTION: phase 2 would end at ≈ ${usd:.2f} ≥ ${WATCH}; transcripts are frozen + saved")

    # -------------------------------------------------------------- Phase 2 main loop: Q0 + Q1 (panel)
    R0, R1 = [], []
    for t in T:
        for i in PANEL:
            watch()
            rows = D.q0_rows(enc, POOL, C[i], D.PERSONAS[CELLS[t][1]], T[t], T[other(t)], t, KQ0)
            for cond in D.Q0_CONDS:
                res, dist, r1 = unit(t, i, cond, rows, q1=(cond == "drift"))
                R0 += [(t, i, D.Q0_CONDS.index(cond), k, *res[k], dist[k]) for k in res]
                R1 += [(t, i, D.Q1_CONDS.index(c1), k, *v) for (c1, k), v in r1.items()]
        say(f"phase 2 transcript {t}: spend ${spend():.2f}")
    np.savez(OUT / f"{TAG}q0.npz", rows=np.array(R0, np.float64), cols=np.array(["tid", "item", "cond", "k", "lpD", "lpR", "dist_tokens"]))
    np.savez(OUT / f"{TAG}q1.npz", rows=np.array(R1, np.float64), cols=np.array(["tid", "item", "cond", "k", "lpD", "lpR"]))

    # -------------------------------------------------------------- Q1 full battery, depth 0, P-none
    RF = []
    for i in FULL_ITEMS:
        watch(); head = D.head(enc, D.system_text(C[i]["system"], ""))
        for c1 in D.Q1_CONDS:
            lp = M.lp(head + D.q1_block(enc, POOL, C[i], FORMS, c1, (i, D.Q1_CONDS.index(c1)))); RF.append((i, D.Q1_CONDS.index(c1), lp[TD], lp[TR]))
    np.savez(OUT / f"{TAG}q1_full.npz", rows=np.array(RF, np.float64), cols=np.array(["item", "cond", "lpD", "lpR"]))
    say("Q1 full battery:", len(FULL_ITEMS), "items")

    # -------------------------------------------------------------- Phase 4: per-turn pooled residuals (drift + filler)
    V = {}
    for t, p in T.items():
        watch()
        for kind, pp in (("drift", p), ("filler", D.filler_pairs(enc, POOL, p, t))):
            ids, cut = D.context(enc, D.PERSONAS[CELLS[t][1]], pp, NTURN); Hs = M.layers(ids)
            spans = [(cut[j] - len(pp[j - 1][1]) - 1, cut[j] - 1) for j in range(1, len(pp) + 1)]   # assistant content
            V[(t, kind)] = {L: np.stack([Hs[L][a:b].mean(0) if b > a else np.zeros(Hs[L].shape[1]) for a, b in spans]).astype(np.float16) for L in (8, 16)}
    np.savez(OUT / f"{TAG}phase4.npz", **{f"t{t}_{kind}_L{L}": v[L] for (t, kind), v in V.items() for L in (8, 16)})
    status, code = "DONE", 0
except Watchdog as e:
    status, code = f"WATCHDOG: {e} — outputs written so far are PARTIAL", 5
    (OUT / f"{TAG}STOP_WATCHDOG.txt").write_text(status + "\n", encoding="utf-8")
(OUT / f"{TAG}ledger.json").write_text(json.dumps({"rate_per_h": RATE, "t0": T0, "elapsed_h": (time.time() - T0) / 3600,
                                                    "spend_usd": spend(), "watchdog_usd": WATCH, "status": status}, indent=1), encoding="utf-8")
(OUT / f"{TAG}checks.json").write_text(json.dumps({"versions": VER, "status": status, "plant": PLANT or None}, indent=1), encoding="utf-8")
say(status); flush_log(); sys.exit(code)
