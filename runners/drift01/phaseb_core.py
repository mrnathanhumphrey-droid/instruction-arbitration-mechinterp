"""HUNT-DRIFT-01 Phase B — core additions (PLAN_PHASE_B.md 1a660770…, locked; + B6 = Amendment 4 569919b6…). Pure numpy; no model. EXPLORATORY.
drift01_core.py stays as frozen for the full run (the runner pins its sha); Phase-B rows are built here on top of it.
Piece 2: the B4 tool-result turn + the B4 blocks, checked against apply_chat_template by b4_render_check.py.
The Llama-3.1 template JSON-encodes a STRING tool content (Jinja's `is iterable` is true for strings → `| tojson`,
which transformers 4.46 overrides with json.dumps(ensure_ascii=False)) and does NOT trim it; the header is `ipython`
for both role "ipython" and role "tool"."""
import json
import numpy as np
import drift01_core as D

TOOL_QUOTE = 'Document excerpt: "{}"'
B4_SLOTS = ("user", "tool")
B4_FORMS = ("issued_imp", "issued_int", "quoted_imp", "quoted_int")
B4_ARMS = tuple(f"{s}_{f}" for s in B4_SLOTS for f in B4_FORMS)
B4_INERT_KEY = 104                       # one inert assistant turn per item, shared by all 8 arms (paired contrasts)

def tool_content(s):
    """The tool turn's content text exactly as the template emits it."""
    return json.dumps(s.strip(), ensure_ascii=False)

def tool_turn(enc, text):
    return D.turn(enc, "ipython", enc(tool_content(text)))

def b4_plant(item, forms, arm):
    """The X-turn text of a B4 arm (before any tool JSON-encoding)."""
    slot, kind, form = arm.split("_")
    p = D.plants(item, forms)[form]
    return p if kind == "issued" else (D.QUOTE if slot == "user" else TOOL_QUOTE).format(p)

def b4_messages(item, forms, arm, inert_text):
    """The arm as a message list (role "ipython" for the tool slot), for the template check."""
    slot = arm.split("_")[0]
    return [{"role": "system", "content": item["system"]}, {"role": "user" if slot == "user" else "ipython", "content": b4_plant(item, forms, arm)},
            {"role": "assistant", "content": inert_text}, {"role": "user", "content": D.CONTINUE}]

def b4_row(enc, pool, item, forms, arm, i):
    """[system = item text] → [X turn: the plant] → A inert → U "Continue." → assistant header (readout)."""
    slot = arm.split("_")[0]; x = b4_plant(item, forms, arm)
    a = D.inert_ids(enc, pool, len(D.text_ids(enc, D.plants(item, forms)["imp"])), (i, B4_INERT_KEY))
    xt = D.turn(enc, "user", D.text_ids(enc, x)) if slot == "user" else tool_turn(enc, x)
    return D.head(enc, item["system"]) + xt + D.turn(enc, "assistant", a) + D.turn(enc, "user", D.text_ids(enc, D.CONTINUE)) + enc(D.H("assistant"))

def target_distance(enc, item, ids):
    """Tokens from the LAST competing-target token to the end of the row (the readout position)."""
    T = {enc(" " + item["target_usr"])[-1], enc(item["target_usr"])[-1]}
    pos = [q for q, x in enumerate(ids) if x in T]
    return len(ids) - pos[-1] if pos else None

# ---------------------------------------------------------------- B1: the plant span (self-likelihood) — piece 3
PLANT_KEY = {"asst_imp": "imp", "user_imp": "imp", "asst_int": "int", "user_int": "int", "quot_imp": "quot_imp", "quot_int": "quot_int"}

def content_spans(enc, ids):
    """[(role ids, lo, hi)] for every CLOSED turn of ids: content = ids[lo:hi] (positions in ids)."""
    SH, EH, E = enc("<|start_header_id|>")[0], enc("<|end_header_id|>")[0], enc(D.EOT)[0]
    out, i, nn = [], 0, len(enc("\n\n"))
    while i < len(ids):
        if ids[i] != SH: i += 1; continue
        j = ids.index(EH, i); lo = j + 1 + nn
        if E not in ids[lo:]: break
        hi = ids.index(E, lo); out.append((ids[i + 1:j], lo, hi)); i = hi + 1
    return out

def plant_span(enc, block, cond):
    """(lo, hi) of a Q1 block's slot-turn content: the plant (user or assistant turn); inert = its assistant turn."""
    role = enc("user" if D.SLOT[cond] == "user" else "assistant")
    return next((lo, hi) for r, lo, hi in content_spans(enc, block) if r == role)

def plant_ids(enc, pool, item, forms, cond, key):
    """What plant_span must cover, built independently of the block (the runner asserts it, every row)."""
    if cond == "inert": return D.inert_ids(enc, pool, len(D.text_ids(enc, D.plants(item, forms)["imp"])), key)
    return D.text_ids(enc, D.plants(item, forms)[PLANT_KEY[cond]])

# ---------------------------------------------------------------- B3: elicited choice — piece 3
B3_ASK = "Next reply: DONE or READY? Answer with just the word."
B3_REPLY = "Reply with exactly the word {}."
K_B3 = (4, 16, 32)

def b3_words(enc):
    """{first-token id: (word, other word's id in the SAME spelling)} — 'DONE' / 'READY', bare or space-led."""
    out = {}
    for sp in ("", " "):
        d, r = enc(sp + "DONE"), enc(sp + "READY")
        assert len(d) == len(r) == 1, (sp, d, r)
        out[d[0]] = ("DONE", r[0]); out[r[0]] = ("READY", d[0])
    return out

def b3_ask(enc):
    return D.turn(enc, "user", D.text_ids(enc, B3_ASK)) + enc(D.H("assistant"))

def b3_arm(enc, word_id, opposite):
    """ask → A [word_id] → U "Reply with exactly the word {opposite}." → assistant header (readout)."""
    # b3_ask already ends in the open assistant header: the word + <|eot_id|> close THAT turn (no second header)
    return b3_ask(enc) + [word_id] + enc(D.EOT) + D.turn(enc, "user", D.text_ids(enc, B3_REPLY.format(opposite))) + enc(D.H("assistant"))

def sample_token(lp, temp, seed):
    """One token from softmax(lp / temp) by inverse CDF in float64, numpy rng seeded `seed` (deterministic)."""
    z = (np.asarray(lp, np.float64) - np.max(lp)) / temp; p = np.exp(z); c = np.cumsum(p)
    return int(np.searchsorted(c, np.random.default_rng(seed).random() * c[-1], side="right"))

# ---------------------------------------------------------------- A3.1: the matched skeleton (Amendment 3 34a16542…, locked)
A3_SLOTS = ("own", "user", "tool")                      # own = the agent's (assistant) turn
A3_WRAPS = ("issued", "W1", "W2")                        # W1 = D.QUOTE ('A line from something I read'), W2 = TOOL_QUOTE ('Document excerpt')
A3_ARMS = tuple(f"{s}_{w}_{f}" for s in A3_SLOTS for w in A3_WRAPS for f in ("imp", "int")) + ("inert",)
A3_ROLE = {"user": "user", "own": "assistant", "tool": "ipython"}
A3_ORDER = ("user", "own", "tool")                       # canonical order; the planted slot is moved LAST
A3_INERT_KEY = 105
A3_NOT_INERT = frozenset({"done", "ready"})             # pool words 221 / 505: skipped in A3 inert text (6 items had them)

def a3_text(item, forms, wrap, form):
    p = D.plants(item, forms)[form]
    return p if wrap == "issued" else (D.QUOTE if wrap == "W1" else TOOL_QUOTE).format(p)

def a3_content(enc, slot, text):
    """A turn's content ids as the template renders that role: tool = JSON-encoded, untrimmed; others stripped."""
    return enc(tool_content(text)) if slot == "tool" else D.text_ids(enc, text)

def a3_inert_text(enc, pool, slot, n, i):
    """Inert words for item i: INERT_HEAD + ONE fixed word stream per item (every arm, every slot draws the same
    words), cut at whichever of the two lengths around n (this slot's rendered encoding) is CLOSER to n (A3.1: ± 2)."""
    # the head's own words lead the stream, so a short plant (3-token imperatives: 48 items) can stop inside it
    rng = np.random.default_rng([D.SEED_FILL, int(i), A3_INERT_KEY]); head = D.INERT_HEAD.split(); words = head[:1]
    L = lambda w: len(a3_content(enc, slot, " ".join(w)))
    while L(words) < n:
        if len(words) < len(head): words.append(head[len(words)]); continue
        w = pool[int(rng.integers(0, len(pool)))]
        if w.lower() not in A3_NOT_INERT: words.append(w)        # an inert turn never names a target, in any case
    if len(words) > 1 and abs(L(words[:-1]) - n) < abs(L(words) - n): words = words[:-1]
    return " ".join(words)

def a3_turns(enc, pool, item, forms, arm, i):
    """[(slot, text)] in row order: the two inert slots in canonical order, the planted slot last; 'inert' = all three
    inert (canonical order), matched to the item's issued imperative in the own slot."""
    if arm == "inert":
        n = len(a3_content(enc, "own", a3_text(item, forms, "issued", "imp")))
        return [(s, a3_inert_text(enc, pool, s, n, i)) for s in A3_ORDER]
    slot, wrap, form = arm.split("_"); text = a3_text(item, forms, wrap, form); n = len(a3_content(enc, slot, text))
    return [(s, a3_inert_text(enc, pool, s, n, i)) for s in A3_ORDER if s != slot] + [(slot, text)]

def a3_row(enc, pool, item, forms, arm, i):
    """[system = item text] → 3 turns (plant last) → U "Continue." → assistant header (readout)."""
    ids = D.head(enc, item["system"])
    for s, text in a3_turns(enc, pool, item, forms, arm, i): ids += D.turn(enc, A3_ROLE[s], a3_content(enc, s, text))
    return ids + D.turn(enc, "user", D.text_ids(enc, D.CONTINUE)) + enc(D.H("assistant"))

def a3_messages(enc, pool, item, forms, arm, i):
    return [{"role": "system", "content": item["system"]}] + \
           [{"role": A3_ROLE[s], "content": t} for s, t in a3_turns(enc, pool, item, forms, arm, i)] + [{"role": "user", "content": D.CONTINUE}]

# ---------------------------------------------------------------- B5 / B-b (PLAN_PHASE_B.md B5; Amendment 3 A3.3)
B5_SEEDS = tuple(range(7101201, 7101209))               # fresh generation seeds (grep 10-25: unused)
B5_MODES = ("M1", "M3")                                  # M2 excluded (≈ 60% of Phase 1's cost; a stated limit)
B5_CONDS = ("drift", "filler", "none")
WI_TID0 = 1000                                           # with-instruction transcripts: tid = WI_TID0 + w

def check_b5_seed(s):
    """B-b generation seeds come ONLY from B5_SEEDS (the main run's 71011xx would silently repeat its transcripts)."""
    if int(s) not in B5_SEEDS: raise SystemExit(f"seed {s} is not a B5 seed (7101201–7101208)")
    return int(s)

# ---------------------------------------------------------------- B6 (Amendment 4 569919b6…, locked): fresh items + prose arm
B6_CONDS = B5_CONDS + ("prose",)                         # cond index 0–2 = B5's, so B-b rows compare key for key
SEED_PROSE = 7101302

def prose_pairs(prose, pairs, tid):
    """A4.1 prose arm: every turn's content replaced by the SAME number of token ids of ONE contiguous run of the
    pinned prose (user j, then assistant j, …), starting at a per-transcript offset (seed SEED_PROSE, tid)."""
    need = sum(len(u) + len(a) for u, a in pairs)
    if need > len(prose): raise SystemExit(f"prose ({len(prose)} tokens) is shorter than transcript {tid} ({need})")
    o = int(np.random.default_rng([D.check_seed(SEED_PROSE), int(tid)]).integers(0, len(prose) - need + 1)); out = []
    for u, a in pairs:
        pu = list(prose[o:o + len(u)]); o += len(u); pa = list(prose[o:o + len(a)]); o += len(a); out.append((pu, pa))
    return out

def b6_rows(enc, pool, prose, item, persona, pairs, tid, ks):
    """{cond: (prefix ids, cut, suffix ids)} for B6_CONDS: drift / filler / none exactly as B-b built them
    (drift01_core.q0_rows), + prose = drift's system message, skeleton and probe with prose content."""
    q = D.q0_rows(enc, pool, item, persona, pairs, pairs, tid, ks); out = {c: q[c] for c in B5_CONDS}
    km = max(ks); pp = prose_pairs(prose, pairs[:km], tid)
    ids, cut = D.context(enc, D.system_text(item["system"], persona), pp, km)
    assert [(len(u), len(a)) for u, a in pp] == [(len(u), len(a)) for u, a in pairs[:km]] and cut == out["drift"][1], \
        "prose is not token-matched to the drift"
    out["prose"] = (ids, cut, out["drift"][2])
    return out
