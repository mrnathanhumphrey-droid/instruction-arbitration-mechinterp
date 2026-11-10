"""HUNT-DRIFT-01 Amendment 9b (87eae7d9…, locked) — Control 2: a frozen text encoder on the A10 rows. EXPLORATORY.
  FAKE=1 python a9b_encode.py <run folder> <TAG>        (deterministic toy encoder; no torch)
  REAL=1 python a9b_encode.py <run folder> <TAG>        (Qwen3-Embedding-8B @ a9b_core.ENC_REV, bf16, its own venv:
                                                          transformers == a9b_core.ENC_TRANSFORMERS; the Llama runner's
                                                          venv stays on 4.46.0)
Input: <TAG>a9b_texts.jsonl from PHASEB=k (one line per A10 row, in row order: the row's ids decoded to text — the
rendered transcript exactly as Llama reads it, through the readout position). A9b.1: no instruction prefix; the model's
own last-token pooling, L2-normalised (the model card's transformers recipe); ONE text per forward pass (no padding, so a
vector depends on its text alone). Truncation at ENC_MAXLEN tokens is counted and must be 0 (stop).
Determinism (STOP): the gate rows (the first 8 probes' native rows; the first 2 in SMOKE) are embedded a second time and
must equal the first pass bitwise.
Outputs: <TAG>a9b_enc.npy (rows × d, fp16; row k = texts line k) + <TAG>a9b_enc.json (versions, revision, counts, the
determinism check, token-length summary). Exit 0 done · 2 a pin refused · 3 a STOP rule."""
import hashlib, json, os, sys, time
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import a9b_core as A9B

FAKE, REAL = os.environ.get("FAKE") == "1", os.environ.get("REAL") == "1"
if FAKE == REAL: sys.exit("exactly one of FAKE=1 / REAL=1")
PLANT = os.environ.get("PLANT", "")
if PLANT and not FAKE: sys.exit("PLANT is FAKE-only")
F, TAG = Path(sys.argv[1]), sys.argv[2]
def stop(code, why):
    (F / f"{TAG}a9b_enc_STOP.txt").write_text(why + "\n", encoding="utf-8"); print("[ENC] STOP", code, why, flush=True); sys.exit(code)
for n in ("a9b_enc.npy", "a9b_enc.json"):
    if (F / f"{TAG}{n}").exists(): sys.exit(f"{TAG}{n} exists (no clobber)")
TX = [json.loads(l) for l in open(F / f"{TAG}a9b_texts.jsonl", encoding="utf-8")]
if [t["row"] for t in TX] != list(range(len(TX))): stop(3, "texts are not rows 0..n−1 in order")
Z = np.load(F / f"{TAG}a9b_q0.npz"); Q = Z["rows"]; n10 = int(Z["blocks"][0])
if len(TX) != n10: stop(3, f"{len(TX)} texts, the A10 block has {n10} rows")
items = sorted({int(x) for x in Q[:n10, 1]}); NG = 2 if "SMOKE" in TAG else 8
GATE = [k for k in range(n10) if int(Q[k, 1]) in items[:NG] and int(Q[k, 5]) in (0, -1)]

class FakeEnc:
    """Deterministic toy: hashed word vectors, a bigram term (so word ORDER matters, as in a contextual encoder), tanh,
    L2-normalised; d = 32."""
    d = 32
    def vec(self, w):
        return np.random.default_rng(int(hashlib.md5(w.encode()).hexdigest()[:8], 16)).normal(0, 1, self.d)
    def __call__(self, text):
        ws = text.split(); V = np.array([self.vec(w) for w in ws]); B = np.array([self.vec(a + "|" + b) for a, b in zip(ws, ws[1:])] or [np.zeros(self.d)])
        z = np.tanh(V.mean(0) + 0.5 * B.mean(0)); z = z / np.linalg.norm(z)
        return z.astype(np.float16), len(ws), False
    ver = {"FAKE": True}

class RealEnc:
    def __init__(self):
        import torch, transformers
        from transformers import AutoModel, AutoTokenizer
        if transformers.__version__ != A9B.ENC_TRANSFORMERS: stop(2, f"transformers {transformers.__version__} ≠ {A9B.ENC_TRANSFORMERS}")
        torch.use_deterministic_algorithms(True); torch.backends.cudnn.benchmark = False
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(A9B.ENC_REPO, revision=A9B.ENC_REV, padding_side="left")
        self.m = AutoModel.from_pretrained(A9B.ENC_REPO, revision=A9B.ENC_REV, torch_dtype=torch.bfloat16, attn_implementation="sdpa").to("cuda:0").eval()
        self.d = int(self.m.config.hidden_size)
        self.ver = {"torch": torch.__version__, "transformers": transformers.__version__, "repo": A9B.ENC_REPO, "revision": A9B.ENC_REV,
                    "gpu": torch.cuda.get_device_name(0), "dtype": "bfloat16", "attn": "sdpa", "pooling": "last token, L2", "instruction": None,
                    "cublas_ws": os.environ.get("CUBLAS_WORKSPACE_CONFIG")}
    def __call__(self, text):
        torch = self.torch
        b = self.tok([text], padding=True, truncation=True, max_length=A9B.ENC_MAXLEN, return_tensors="pt").to("cuda:0")
        full = len(self.tok(text)["input_ids"])
        if "last_token" not in self.ver: self.ver["last_token"] = self.tok.convert_ids_to_tokens(int(b["input_ids"][0, -1]))   # the recipe's EOS, recorded
        with torch.inference_mode():
            h = self.m(**b).last_hidden_state[0, -1].float()          # one text, no padding: the last position IS the last token
            z = torch.nn.functional.normalize(h, p=2, dim=0)
        return z.to(torch.float16).cpu().numpy(), int(b["input_ids"].shape[1]), full > A9B.ENC_MAXLEN

DEADLINE = float(os.environ.get("ENC_DEADLINE", "inf"))   # unix s (launcher: hard cap − pull margin); a clean stop keeps the runner's files pullable
if time.time() >= DEADLINE: stop(6, "ENCODER DEADLINE: already past the deadline before loading")
M = FakeEnc() if FAKE else RealEnc()
T0 = time.time()
OUTP = F / f"{TAG}a9b_enc.npy"; E = np.lib.format.open_memmap(OUTP, mode="w+", dtype=np.float16, shape=(n10, M.d))
NT, trunc = np.zeros(n10, np.int64), 0
for k, t in enumerate(TX):
    z, nt, tr = M(t["text"]); E[k] = z; NT[k] = nt; trunc += int(tr)
    if (k + 1) % 500 == 0 or k + 1 == min(300, n10):          # projection after 300 texts, then every 500 (+ the gate re-pass)
        end = time.time() + (time.time() - T0) / (k + 1) * (n10 - k - 1 + len(GATE))
        if end > DEADLINE: E.flush(); stop(6, f"ENCODER DEADLINE: at {k + 1} / {n10} the projected end is {end - DEADLINE:.0f} s past the deadline")
    if (k + 1) % 5000 == 0: print(f"[ENC] {k + 1} / {n10} ({(time.time() - T0) / 60:.1f} min)", flush=True)
E.flush()
if trunc: stop(3, f"{trunc} texts exceed {A9B.ENC_MAXLEN} tokens (truncated)")
bad = []
for k in GATE:
    z, _, _ = M(TX[k]["text"])
    if PLANT == "encdrift" and k == GATE[0]: z = z.copy(); z.view(np.uint16)[0] ^= 1
    if z.tobytes() != np.asarray(E[k]).tobytes(): bad.append(k)
J = {"versions": M.ver, "rows": n10, "d": M.d, "tokens": {"min": int(NT.min()), "median": float(np.median(NT)), "max": int(NT.max())},
     "truncated": trunc, "determinism": {"rows": len(GATE), "bitwise": len(GATE) - len(bad), "bad": bad[:10]},
     "minutes": (time.time() - T0) / 60, "sha256_enc": hashlib.sha256(OUTP.read_bytes()).hexdigest()}
(F / f"{TAG}a9b_enc.json").write_text(json.dumps(J, indent=1), encoding="utf-8")
if bad: stop(3, f"ENCODER DETERMINISM FAILED: {len(bad)} / {len(GATE)} gate rows differ on a second pass")
print(f"[ENC] DONE: {n10} rows × d {M.d}; determinism {len(GATE)} / {len(GATE)} bitwise; tokens max {J['tokens']['max']}; {J['minutes']:.1f} min", flush=True)
