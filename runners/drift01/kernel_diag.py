"""HUNT-DRIFT-01 diagnostic (local GPU, EXPLORATORY; not a hunt result). Is the REAL smoke's cache-branch gap
(max |Δlp| 0.398 nats) an SDPA-KERNEL difference or a LOGIC bug in the branched path?
  <venv_drift_diag>\\Scripts\\python.exe kernel_diag.py <pulled smoke folder>
Model: Llama-3.2-1B-Instruct (same Llama architecture + tokenizer vocabulary as the 8B; fits 16 GB). Rows = the runner's
own builders (drift01_core) on the FROZEN smoke transcripts. For 48 seeded readouts it computes the fresh pass and the
branched pass exactly as drift01_lambda.py does (RealModel.lp / RealBrancher, copied), under: the default SDPA dispatch,
forced EFFICIENT, forced MATH. Kernel → the gap collapses when both paths are forced onto one kernel. Bug → it stays."""
import contextlib, json, os, sys
from pathlib import Path
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")   # as the instance (deterministic cuBLAS)
import numpy as np, torch
from torch.nn.attention import sdpa_kernel, SDPBackend
from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import drift01_core as D
SM = Path(sys.argv[1])
torch.use_deterministic_algorithms(True)
MID = "meta-llama/Llama-3.2-1B-Instruct"
tok = AutoTokenizer.from_pretrained(MID); enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
DT = {"bf16": torch.bfloat16, "fp32": torch.float32}[os.environ.get("DIAG_DTYPE", "bf16")]   # fp32: logic vs rounding
print("dtype", DT, flush=True)
mdl = AutoModelForCausalLM.from_pretrained(MID, torch_dtype=DT, attn_implementation="sdpa", device_map={"": 0}).eval()
print("model", MID, "rev", mdl.config._commit_hash, "| torch", torch.__version__, "| gpu", torch.cuda.get_device_name(0), flush=True)

def lp_fresh(ids):
    with torch.inference_mode():
        out = mdl(input_ids=torch.tensor([ids], device="cuda:0"), use_cache=False, num_logits_to_keep=1)
    return torch.log_softmax(out.logits[0, -1].float(), -1).cpu().numpy().astype(np.float64)
class Br:                                           # = drift01_lambda.RealBrancher
    def __init__(self): self.cache, self.n = DynamicCache(), 0
    def extend(self, chunk, step=4096):
        for i in range(0, len(chunk), step):
            c = list(chunk[i:i + step])
            with torch.inference_mode():
                mdl(input_ids=torch.tensor([c], device="cuda:0"), past_key_values=self.cache, use_cache=True, num_logits_to_keep=1)
            self.n += len(c)
    def probe(self, suffix):
        with torch.inference_mode():
            out = mdl(input_ids=torch.tensor([list(suffix)], device="cuda:0"), past_key_values=self.cache, use_cache=True, num_logits_to_keep=1)
        self.cache.crop(self.n)
        return torch.log_softmax(out.logits[0, -1].float(), -1).cpu().numpy().astype(np.float64)
    def pos(self): return self.n

# frozen smoke transcripts → pairs
Z = np.load(SM / "REAL_SMOKE_transcripts.npz"); man = json.loads((SM / "REAL_SMOKE_transcripts_manifest.json").read_text(encoding="utf-8"))
T = {}
for q in range(len(Z["tid"])): T.setdefault(int(Z["tid"][q]), []).append(Z["ids"][Z["off"][q]:Z["off"][q + 1]].tolist())
T = {t: list(zip(v[0::2], v[1::2])) for t, v in T.items()}
assert D.verify_frozen(T, man["sha"]) == [], "smoke transcripts do not match their manifest"
cells = [tuple(c) for c in man["cells"]]
C = [json.loads(l) for l in open(r"D:\Resolve Research\Prompt_Injection\run\prv02\setup\stimuli_contested.jsonl", encoding="utf-8")]
PANEL = [p["item"] for p in json.loads((HERE / "panel.json").read_text(encoding="utf-8"))["panel"]][:2]
POOL = (HERE / "word_pool_drift01.txt").read_text(encoding="utf-8").split()
TD, TR = enc(" DONE")[-1], enc(" READY")[-1]
seeds = sorted({c[3] for c in cells})
other = lambda t: next(u for u, c in enumerate(cells) if c[:3] == cells[t][:3] and c[3] == seeds[(seeds.index(cells[t][3]) + 1) % len(seeds)])
KQ0 = (0, 1, 2, 4, 8)

def branched(rows, cond, k):
    ids, cut, suf = rows[cond]; br = Br()
    for kk in sorted(cut):
        if kk not in KQ0: continue
        br.extend(ids[br.pos():cut[kk]])
        lp = br.probe(suf)
        if kk == k: return lp
rng = np.random.default_rng(7101001); picks = []
for _ in range(48):
    t = int(rng.integers(0, len(cells))); i = PANEL[int(rng.integers(0, len(PANEL)))]; cond = D.Q0_CONDS[int(rng.integers(0, 5))]
    rows = D.q0_rows(enc, POOL, C[i], D.PERSONAS[cells[t][1]], T[t], T[other(t)], t, KQ0)
    ks = [k for k in KQ0 if k in rows[cond][1]]; picks.append((rows, cond, ks[int(rng.integers(0, len(ks)))], t, i))

def run(backend):
    out = []
    for rows, cond, k, t, i in picks:
        ctx = sdpa_kernel(backend) if backend is not None else contextlib.nullcontext()
        with ctx:
            f = lp_fresh(D.row(*rows[cond], k)); b = branched(rows, cond, k)
        out.append((f[[TD, TR]], b[[TD, TR]], len(D.row(*rows[cond], k))))
    return out
res = {}
for name, be in (("default", None), ("EFFICIENT", SDPBackend.EFFICIENT_ATTENTION), ("MATH", SDPBackend.MATH)):
    r = run(be); d = np.array([np.abs(f - b).max() for f, b, _ in r]); res[name] = r
    print(f"{name:9s} fresh vs branched: max |Δlp| {d.max():.4f}  median {np.median(d):.4f}  (48 readouts, ctx {min(x[2] for x in r)}–{max(x[2] for x in r)} tokens)", flush=True)
fd = np.array([np.abs(a[0] - b[0]).max() for a, b in zip(res["default"], res["EFFICIENT"])])
bd = np.array([np.abs(a[1] - b[1]).max() for a, b in zip(res["default"], res["EFFICIENT"])])
print(f"kernel effect alone, FRESH default vs FRESH EFFICIENT: max {fd.max():.4f} median {np.median(fd):.4f}")
print(f"kernel effect alone, BRANCHED default vs BRANCHED EFFICIENT: max {bd.max():.4f} median {np.median(bd):.4f}")
lpv = np.array([x[0] for x in res["default"]]); print(f"readout scale: lp(target) range {lpv.min():.1f} … {lpv.max():.1f}")
