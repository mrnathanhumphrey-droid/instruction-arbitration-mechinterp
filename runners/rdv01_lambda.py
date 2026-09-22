#!/usr/bin/env python
# RDV-01 v2 -- does the model RE-DERIVE provenance after a single-layer edit? (corrected instrument)
# PREREG_RDV01.md v2 (sha folded at lock), chained to H4 v3 23d169b0...4d.
# v1 FAILED: span-mean probe on single-role POOL (content shortcut) + FRESH-fit routed around the edit ->
# anchor never scrambled -> 0/0. the lead researcher redesign + two additions folded:
#  * FIXED reference probe: train on UNEDITED layer-L residuals, EVALUATE that fixed probe on EDITED (as
#    Phase B's manip did -- it registered the edit). Not fresh-fit.
#  * CONTENT-MATCHED substrate: CONTESTED imperative spans, BOTH counterbalance cells pooled (system vs user
#    slot, content+lexical balanced -> probe forced onto provenance, no content/DONE-READY shortcut).
#  * HARD SCRAMBLE GATE (in-runner): the L8 edit MUST drop the fixed L8 probe (P_e rises) or SystemExit.
#  * POSITIVE CONTROL: edit at L30, read at L31 (one layer headroom -> near-total PERSISTENCE expected). If
#    control persists AND L8 recovers -> instrument demonstrated working; if control also "recovers" -> it's
#    the probe not the model, and we know for $0.60.
#  * RECOVERY pre-committed (not binary): per-layer P_e trajectory vs the unedited curve; RECOVERED at L iff
#    (P_e_edit[L]-P_e_uned[L]) <= 0.20*(0.5-P_e_uned[L]) i.e. within 20% of the unedited-vs-chance gap.
#    Report the SHAPE (snap-back @ L9 vs slow climb are different mechanisms, same verdict).
# Edit = projection-EXCHANGE (k=25 deflation subspace fit on the contested substrate; system -dv, user +dv)
# at imperative-span content tokens. Group-disjoint split by TEMPLATE. Mechanism test, not the M estimate.
import os, json, time
import numpy as np, torch
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
EDIT_L8, EDIT_L30 = 8, 30
READ_LAYERS = [9, 12, 16, 24, 31]        # L8-condition recovery trajectory
CAP_U = [8, 9, 12, 16, 24, 30, 31]       # layers to capture in the unedited pass (probes + subspaces)
KCAP = 5 if SMOKE else 25
PE_STOP = 0.45
SCRAMBLE_MIN = 0.30                       # hard gate: edit-layer P_e must exceed this under edit
RECOVER_FRAC = 0.20                       # recovered iff within 20% of unedited-vs-chance gap
BOOT = 200 if SMOKE else 2000
SEED = 20260914

def log(*a): print(*a, flush=True)

def build_subspace(X, y, tr, te, kcap, pe_stop):
    basis = []; Xdef = X.copy()
    for i in range(kcap + 1):
        sc = StandardScaler().fit(Xdef[tr])
        clf = LogisticRegression(C=1.0, max_iter=300, solver="lbfgs").fit(sc.transform(Xdef[tr]), y[tr])
        pe = 1.0 - float(clf.score(sc.transform(Xdef[te]), y[te]))
        if pe >= pe_stop or len(basis) >= kcap: break
        scale = sc.scale_.copy(); scale[~np.isfinite(scale) | (scale == 0)] = 1.0
        w = clf.coef_[0] / scale
        for b in basis: w = w - (w @ b) * b
        nw = np.linalg.norm(w)
        if nw < 1e-8: break
        w = w / nw; basis.append(w)
        Bm = np.array(basis).T; Xdef = X - (X @ Bm) @ Bm.T
    return (np.array(basis).T if basis else np.zeros((X.shape[1], 0), np.float32)).astype(np.float32), len(basis)

def main():
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_contested.jsonl"), encoding="utf-8")]
    if SMOKE: stim = stim[:80]
    from make_stimuli import TEMPLATES
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16,
                                                 device_map={"": 0}).eval()
    dev = next(model.parameters()).device
    import transformers
    log(f"[R2] model on {dev}; tf {transformers.__version__} ({time.time()-t0:.0f}s); n={len(stim)} k={KCAP}")

    def locate(it):
        imp_s = TEMPLATES[it["template_idx".format(T=it["target_sys"])
        imp_u = TEMPLATES[it["template_idx".format(T=it["target_usr"])
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False); offs = enc["offset_mapping"]
        def sp(imp):
            cs = text.index(imp); ce = cs + len(imp)
            return [i for i, (a, b) in enumerate(offs) if a < ce and b > cs and b > a]
        return enc["input_ids"], sp(imp_s), sp(imp_u)
    lay = [locate(it) for it in stim]
    tmpl_of = np.array([it["template_idx"] for it in stim])
    # group-disjoint split by TEMPLATE (templates with idx%3==0 -> test, else train)
    def is_test_tmpl(t): return (t % 3 == 0)

    STATE = {"sys": None, "usr": None, "dv": None}
    def edit_hook(mod, inp, out):
        h = out[0] if isinstance(out, tuple) else out
        if STATE["dv"] is not None:
            if STATE["sys"]: h[0, STATE["sys"], :] += (-STATE["dv"])
            if STATE["usr"]: h[0, STATE["usr"], :] += (STATE["dv"])
        return out

    def capture_pass(cap_layers, edit_layer=None, dv=None):
        """One forward per item; returns per-layer dicts of token arrays X[L], y (slot), tmpl (per token)."""
        X = {L: [] for L in cap_layers}; Y = []; TM = []
        hh = model.model.layers[edit_layer - 1].register_forward_hook(edit_hook) if edit_layer else None
        STATE["dv"] = (torch.tensor(dv, dtype=torch.bfloat16, device=dev) if dv is not None else None)
        with torch.inference_mode():
            for i, ((ids, ss, su), it) in enumerate(zip(lay, stim)):
                STATE["sys"], STATE["usr"] = (ss, su) if edit_layer else (None, None)
                t = torch.tensor([ids], dtype=torch.long, device=dev)
                hs = model(input_ids=t, output_hidden_states=True, use_cache=False).hidden_states
                for L in cap_layers:
                    r = hs[L][0].float().cpu().numpy()
                    for j in ss: X[L].append(r[j]);
                    for j in su: X[L].append(r[j])
                # labels/tmpl appended once per token, aligned with X order (sys tokens then usr tokens)
                for _ in ss: Y.append(1); TM.append(it["template_idx"])
                for _ in su: Y.append(0); TM.append(it["template_idx"])
                if (i + 1) % 200 == 0: log(f"[R2] pass(edit={edit_layer}) {i+1}/{len(stim)} ({time.time()-t0:.0f}s)")
        if hh: hh.remove()
        STATE["dv"] = None
        return {L: np.array(X[L], np.float32) for L in cap_layers}, np.array(Y, np.int8), np.array(TM)

    # ---- UNEDITED pass ----
    Xu, y, tm = capture_pass(CAP_U)
    te = np.array([is_test_tmpl(t) for t in tm]); tr = ~te
    log(f"[R2] unedited captured; tokens={len(y)} train={int(tr.sum())} test={int(te.sum())} ({time.time()-t0:.0f}s)")

    # ---- subspaces + swap vectors at L8 and L30 (contested-fit, Phase-B-style deflation) ----
    def swap_vec(L):
        B, k = build_subspace(Xu[L], y, tr, te, KCAP, PE_STOP)
        diff = Xu[L][y == 1].mean(0) - Xu[L][y == 0].mean(0)   # system - user
        dv = (B @ (B.T @ diff)).astype(np.float32)
        return dv, k, float(np.linalg.norm(dv))
    dv8, k8, n8 = swap_vec(EDIT_L8); dv30, k30, n30 = swap_vec(EDIT_L30)
    log(f"[R2] L8 k={k8} |dv|={n8:.3f}; L30 k={k30} |dv|={n30:.3f} ({time.time()-t0:.0f}s)")

    # ---- FIXED reference probes (train on UNEDITED train tokens per layer) ----
    probes = {}
    for L in CAP_U:
        sc = StandardScaler().fit(Xu[L][tr])
        clf = LogisticRegression(C=1.0, max_iter=300, solver="lbfgs").fit(sc.transform(Xu[L][tr]), y[tr])
        probes[L] = (sc, clf)
    def pe_fixed(L, X):   # held-out error of the FIXED layer-L probe on test tokens of X
        sc, clf = probes[L]
        return 1.0 - float((clf.predict(sc.transform(X[L][te])) == y[te]).mean())
    pe_uned = {L: pe_fixed(L, Xu) for L in CAP_U}

    # ---- EDITED passes ----
    Xe8, _, _ = capture_pass([EDIT_L8] + READ_LAYERS, edit_layer=EDIT_L8, dv=dv8)   # L8 condition
    Xe30, _, _ = capture_pass([EDIT_L30, 31], edit_layer=EDIT_L30, dv=dv30)         # positive control
    pe_e8 = {L: pe_fixed(L, Xe8) for L in [EDIT_L8] + READ_LAYERS}
    pe_e30 = {L: pe_fixed(L, Xe30) for L in [EDIT_L30, 31]}

    # ---- HARD GATES ----
    gate_edit_landed = pe_e8[EDIT_L8] >= SCRAMBLE_MIN
    gate_ctrl_landed = pe_e30[EDIT_L30] >= SCRAMBLE_MIN
    def recovered(L, pe_e):
        gap = 0.5 - pe_uned[L]
        return bool((pe_e[L] - pe_uned[L]) <= RECOVER_FRAC * gap) if gap > 1e-6 else None
    def gapclosed(L, pe_e):
        gap = 0.5 - pe_uned[L]
        return round(1.0 - (pe_e[L] - pe_uned[L]) / gap, 4) if gap > 1e-6 else float("nan")
    ctrl_persists = (not recovered(31, pe_e30))   # control at L31 should NOT recover

    # ---- recovery trajectory (L8 condition) + bootstrap CI on gap-closed @ L31 ----
    traj = {}
    for L in READ_LAYERS:
        traj[str(L)] = {"pe_unedited": round(pe_uned[L], 4), "pe_edited": round(pe_e8[L], 4),
                        "gap_closed": gapclosed(L, pe_e8), "recovered": recovered(L, pe_e8)}
    # bootstrap gap-closed@L31 by resampling test templates
    rng = np.random.default_rng(SEED); test_tmpls = np.unique(tm[te]); boots = []
    sc31, clf31 = probes[31]
    pu31 = (clf31.predict(sc31.transform(Xu[31][te])) == y[te]); pe31 = (clf31.predict(sc31.transform(Xe8[31][te])) == y[te])
    tm_te = tm[te]
    for _ in range(BOOT):
        pk = rng.choice(test_tmpls, len(test_tmpls), replace=True)
        m = np.isin(tm_te, pk)
        if m.sum() < 5: continue
        peu = 1 - pu31[m].mean(); pee = 1 - pe31[m].mean(); gap = 0.5 - peu
        if gap > 1e-6: boots.append(1.0 - (pee - peu) / gap)
    gc31_ci = [round(float(np.percentile(boots, 2.5)), 4), round(float(np.percentile(boots, 97.5)), 4)] if boots else [float("nan")]*2

    # ---- verdict ----
    if not gate_edit_landed:
        verdict = f"HALT: L8 edit did not scramble (P_e_edit_L8={pe_e8[EDIT_L8]:.3f} < {SCRAMBLE_MIN}) -- instrument broken, no reading"
    elif not gate_ctrl_landed:
        verdict = f"HALT: L30 control edit did not land (P_e_edit_L30={pe_e30[EDIT_L30]:.3f} < {SCRAMBLE_MIN})"
    elif not ctrl_persists:
        verdict = f"CONTROL-FAILED: positive control recovered at L31 (gap_closed={gapclosed(31,pe_e30):.2f}) -- instrument cannot distinguish persistence; L8 reading UNINTERPRETABLE"
    else:
        rec31 = recovered(31, pe_e8); gc31 = gapclosed(31, pe_e8)
        if rec31 or gc31 >= 0.80:
            verdict = f"RE-DERIVATION-DEMONSTRATED (control persists; L8 recovers, gap_closed@L31={gc31:.2f})"
        elif gc31 < 0.20:
            verdict = f"EDIT-PERSISTS (control persists; L8 stays scrambled, gap_closed@L31={gc31:.2f}) -- 're-derivation' leaves the framing"
        else:
            verdict = f"PARTIAL-RECOVERY (control persists; gap_closed@L31={gc31:.2f}) -- report the shape"

    out = {"prereg": "PREREG_RDV01.md", "version": "v2", "chained_to_H4v3": "23d169b02ea9c555d6e58179749b836a3c0d06d1ac35e1d0c84583ba706dad4d",
           "SMOKE": SMOKE, "transformers": transformers.__version__, "n_spans": len(stim),
           "substrate": "contested imperative spans, both counterbalance cells, group-disjoint by template",
           "k8": k8, "dv8_norm": round(n8, 4), "k30": k30, "dv30_norm": round(n30, 4),
           "scramble_min": SCRAMBLE_MIN, "recover_frac": RECOVER_FRAC,
           "gate_edit_landed": bool(gate_edit_landed), "pe_edit_L8": round(pe_e8[EDIT_L8], 4),
           "gate_ctrl_landed": bool(gate_ctrl_landed), "pe_edit_L30": round(pe_e30[EDIT_L30], 4),
           "positive_control_L31": {"pe_unedited": round(pe_uned[31], 4), "pe_edited": round(pe_e30[31], 4),
                                    "gap_closed": gapclosed(31, pe_e30), "persists": bool(ctrl_persists)},
           "L8_recovery_trajectory": traj, "gapclosed_L31_ci95": gc31_ci,
           "pe_unedited_all": {str(L): round(pe_uned[L], 4) for L in CAP_U},
           "verdict": verdict, "note": "MECHANISM test. Recovery of provenance decodability is the behavioral "
           "signature of re-derivation, not a watched circuit rebuild. Fixed probe + positive control + hard "
           "scramble gate (v1 failed silently on a content shortcut).", "runtime_s": round(time.time() - t0, 1)}
    fn = os.path.join(OUT, "rdv01_smoke.json" if SMOKE else "rdv01.json")
    json.dump(out, open(fn, "w"), indent=2)
    log(f"[R2] edit-landed L8 P_e={pe_e8[EDIT_L8]:.3f} ctrl L30->L31 persists={ctrl_persists} "
        f"(L31 u{pe_uned[31]:.3f}/e{pe_e30[31]:.3f}); L8 traj " +
        " ".join(f"L{L}:{traj[str(L)]['gap_closed']}" for L in READ_LAYERS))
    log(f"[R2] -> {verdict}; wrote {fn}")

if __name__ == "__main__":
    main()
