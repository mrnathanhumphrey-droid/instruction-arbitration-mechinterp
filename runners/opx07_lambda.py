#!/usr/bin/env python
# OPX-07 -- does the role MARKER mediate the ANCHORING (order-reversal invariance), separately from magnitude (OPX-03: marker ~0%)?
# 4 marker arms x 2 orders; one-sided A_sys/A_usr span patch from cb-twin; content+filler KEPT (non-degenerate, proven step-zero).
#   ROLE native | NSAME both->info | NDIST system->alpha,user->beta | NSTRIP NSAME+preamble-stripped(content kept)
# Per arm: signs_keep (dY_sys, dY_usr keep sign across orders = BLOCK-ANCHORED) vs signs_swap (follow position). raw dY (B flips).
# SIGN-DETERMINACY gate (the reviewer): an arm is readable only if |dY_sys| and |dY_usr| CIs exclude 0 AND each >= 3*nuisance
#   (nuisance = 0.06*|asym_ROLE_normal|, the OPX-03 offset share); else the arm is INDETERMINATE (a collapsed magnitude, not keep/swap).
# Mechanism map over (ROLE,NSAME,NDIST,NSTRIP): role-semantic (k,sw,sw,sw) | symmetry-breaking (k,sw,k,sw) |
#   preamble-mediated (k,k,k,sw) | content-mediated (k,k,k,k).
import os, json, time
import numpy as np, torch
from collections import defaultdict
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", HERE)
HF = os.environ.get("HF_TOKEN") or None
SMOKE = os.environ.get("SMOKE", "0") == "1"
LAYERS = list(range(8, 32)); DONE, READY = 71496, 46678; SH, EOT = 128006, 128009; HDR_END = "<|end_header_id|>\n\n"
NTMPL = 30; BOOT = 300 if SMOKE else 5000; SEED = 20260925
ARMS = ["ROLE", "NSAME", "NDIST", "NSTRIP"]
def log(*a): print(*a, flush=True)
def place(imp, filler, pos): return f"{imp} {filler}" if pos == "early" else f"{filler} {imp}"

def main():
    t0 = time.time()
    stim = [json.loads(l) for l in open(os.path.join(HERE, "stimuli_contested.jsonl"), encoding="utf-8")]
    from make_stimuli import TEMPLATES, FILLERS
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=HF)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, token=HF, torch_dtype=torch.bfloat16, device_map={"":0}).eval()
    dev = next(model.parameters()).device
    import transformers
    log(f"[OPX7] model on {dev}; tf {transformers.__version__} L{LAYERS[0]}..{LAYERS[-1]} ({time.time()-t0:.0f}s)")

    def segment(it, arm):
        ti, fi, pos = it["template_idx"], it["filler_idx"], it["position"]
        imp_s = TEMPLATES[ti].format(T=it["target_sys"]); imp_u = TEMPLATES[ti].format(T=it["target_usr"])
        fsys, fusr = FILLERS[fi]; s = place(imp_s, fsys, pos); u = place(imp_u, fusr, pos)
        text = tok.apply_chat_template([{"role":"system","content":s},{"role":"user","content":u}], tokenize=False, add_generation_prompt=True)
        if arm in ("NSAME", "NSTRIP"):
            for r in ("system","user"): text = text.replace(f"<|start_header_id|>{r}<|end_header_id|>", "<|start_header_id|>info<|end_header_id|>")
        elif arm == "NDIST":
            text = text.replace("<|start_header_id|>system<|end_header_id|>","<|start_header_id|>alpha<|end_header_id|>")
            text = text.replace("<|start_header_id|>user<|end_header_id|>","<|start_header_id|>beta<|end_header_id|>")
        if arm == "NSTRIP":
            h = text.find(HDR_END)
            if h < 0: return None
            h += len(HDR_END); c = text.find(s)
            if c > h: text = text[:h] + text[c:]
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"]; offs = enc["offset_mapping"]
        sh = [i for i,t in enumerate(ids) if t==SH]; eot = [i for i,t in enumerate(ids) if t==EOT]
        if len(sh) < 3 or len(eot) < 2: return None
        def sp(imp, start=0):
            cs = text.find(imp, start)
            if cs < 0: return None
            ce = cs+len(imp); return [i for i,(a,b) in enumerate(offs) if a<ce and b>cs and b>a]
        si = sp(imp_s); ui = sp(imp_u, start=(text.find(imp_s)+len(imp_s)) if text.find(imp_s)>=0 else 0)
        if not si or not ui: return None
        return ids, si, ui, sh, eot

    def flip(ids, sh, eot):
        pre=list(range(0,sh[0])); sysb=list(range(sh[0],eot[0]+1)); usrb=list(range(sh[1],eot[1]+1)); asst=list(range(sh[2],len(ids)))
        order=pre+usrb+sysb+asst; return [ids[i] for i in order], {o:n for n,o in enumerate(order)}

    twin_g = defaultdict(dict)
    for i,it in enumerate(stim): twin_g[(it["template_idx"],it["filler_idx"],it["position"])][it["counterbalance"]]=i
    twin = {}
    for d in twin_g.values():
        if len(d)==2: a,b=list(d.values()); twin[a]=b; twin[b]=a

    STATE={"repl":None}; handles=[]
    def make_hook(L):
        def hook(mod,inp,out):
            h=out[0] if isinstance(out,tuple) else out; r=STATE["repl"]
            if r is not None and L in r: pos,val=r[L]; h[0,pos,:]=val
            return out
        return hook
    for L in LAYERS: handles.append(model.model.layers[L-1].register_forward_hook(make_hook(L)))
    def run(ids, repl=None):
        STATE["repl"]=repl; t=torch.tensor([ids],dtype=torch.long,device=dev)
        with torch.inference_mode():
            lp=torch.log_softmax(model(input_ids=t,use_cache=False).logits[0,-1,:].float(),-1)
        STATE["repl"]=None; return float(lp[DONE]-lp[READY]), float(torch.exp(lp[DONE])+torch.exp(lp[READY]))
    def ysig(R,it): return R if it["target_sys"]=="DONE" else -R
    def capture(ids):
        t=torch.tensor([ids],dtype=torch.long,device=dev)
        with torch.inference_mode(): hs=model(input_ids=t,output_hidden_states=True,use_cache=False).hidden_states
        return {L:hs[L][0].detach().clone() for L in LAYERS}
    def repl_one(pos_idx,cap,tw_idx): return {L:(torch.tensor(pos_idx,dtype=torch.long,device=dev), cap[L][tw_idx].to(torch.bfloat16)) for L in LAYERS}

    def usable(i):
        tw=twin.get(i)
        if tw is None: return False
        for m in ARMS:
            a=segment(stim[i],m); b=segment(stim[tw],m)
            if a is None or b is None: return False
            _,si,ui,_,_=a; _,tsi,tui,_,_=b
            if not (len(si)==len(tsi) and len(ui)==len(tui) and len(si)==len(tui) and len(ui)==len(tsi)): return False
        return True
    use=[i for i in range(len(stim)) if usable(i)]
    if SMOKE: use=use[:40]
    log(f"[OPX7] usable={len(use)} skipped={len(stim)-len(use)} ({time.time()-t0:.0f}s)")

    tmpl=np.array([stim[i]["template_idx"] for i in use]); N=len(use)
    # per arm/order arrays
    Yb={(m,o):np.zeros(N) for m in ARMS for o in ("n","f")}
    Ys={(m,o):np.zeros(N) for m in ARMS for o in ("n","f")}; Yu={(m,o):np.zeros(N) for m in ARMS for o in ("n","f")}
    for n,i in enumerate(use):
        it=stim[i]; tw=twin[i]
        for m in ARMS:
            ids,si,ui,sh,eot=segment(it,m); tids,tsi,tui,tsh,teot=segment(stim[tw],m)
            capn=capture(tids)
            Yb[(m,"n")][n]=ysig(run(ids)[0],it)
            Ys[(m,"n")][n]=ysig(run(ids,repl_one(si,capn,tsi))[0],it)
            Yu[(m,"n")][n]=ysig(run(ids,repl_one(ui,capn,tui))[0],it)
            fids,o2n=flip(ids,sh,eot); ftids,to2n=flip(tids,tsh,teot)
            fsi=[o2n[p] for p in si]; fui=[o2n[p] for p in ui]; ftsi=[to2n[p] for p in tsi]; ftui=[to2n[p] for p in tui]
            capf=capture(ftids)
            Yb[(m,"f")][n]=ysig(run(fids)[0],it)
            Ys[(m,"f")][n]=ysig(run(fids,repl_one(fsi,capf,ftsi))[0],it)
            Yu[(m,"f")][n]=ysig(run(fids,repl_one(fui,capf,ftui))[0],it)
        if (n+1)%40==0: log(f"[OPX7] {n+1}/{N} ({time.time()-t0:.0f}s)")
    for h in handles: h.remove()

    def per_t(a): return np.array([a[tmpl==t].mean() if (tmpl==t).any() else 0.0 for t in range(NTMPL)])
    dYs={(m,o):per_t(Ys[(m,o)]-Yb[(m,o)]) for m in ARMS for o in ("n","f")}
    dYu={(m,o):per_t(Yu[(m,o)]-Yb[(m,o)]) for m in ARMS for o in ("n","f")}
    pe={k:float(v.mean()) for k,v in dYs.items()}; pu={k:float(v.mean()) for k,v in dYu.items()}
    B={(m,o):float(Yb[(m,o)].mean()) for m in ARMS for o in ("n","f")}
    asym_ROLE_n=pu[("ROLE","n")]-pe[("ROLE","n")]
    nuisance=0.06*abs(asym_ROLE_n); thr=3*nuisance
    rng=np.random.default_rng(SEED)
    def ci(arr):
        out=np.empty(BOOT)
        for b in range(BOOT): pk=rng.integers(0,NTMPL,NTMPL); out[b]=arr[pk].mean()
        return [float(np.percentile(out,2.5)),float(np.percentile(out,97.5))]
    def sg(x): return 1 if x>0 else -1
    arm_res={}
    for m in ARMS:
        s_n,s_f,u_n,u_f=pe[(m,"n")],pe[(m,"f")],pu[(m,"n")],pu[(m,"f")]
        ci_sn=ci(dYs[(m,"n")]); ci_sf=ci(dYs[(m,"f")]); ci_un=ci(dYu[(m,"n")]); ci_uf=ci(dYu[(m,"f")])
        excl0=lambda c:not(c[0]<=0<=c[1])
        determinate=all([excl0(ci_sn),excl0(ci_sf),excl0(ci_un),excl0(ci_uf)]) and min(abs(s_n),abs(s_f),abs(u_n),abs(u_f))>=thr
        keep=(sg(s_f)==sg(s_n) and sg(u_f)==sg(u_n)); swap=(sg(s_f)==sg(u_n) and sg(u_f)==sg(s_n))
        verd="INDETERMINATE" if not determinate else ("keep" if keep and not swap else ("swap" if swap and not keep else "mixed"))
        arm_res[m]={"dY_sys_n":s_n,"dY_sys_f":s_f,"dY_usr_n":u_n,"dY_usr_f":u_f,
                    "ci_sys_n":ci_sn,"ci_sys_f":ci_sf,"ci_usr_n":ci_un,"ci_usr_f":ci_uf,
                    "asym_n":u_n-s_n,"asym_f":u_f-s_f,"B_n":B[(m,"n")],"B_f":B[(m,"f")],
                    "determinate":bool(determinate),"outcome":verd}
    pattern=tuple(arm_res[m]["outcome"] for m in ARMS)
    MAP={("keep","swap","swap","swap"):"ROLE-SEMANTIC (role words specifically mediate anchoring)",
         ("keep","swap","keep","swap"):"SYMMETRY-BREAKING (any distinct label mediates anchoring)",
         ("keep","keep","keep","swap"):"PREAMBLE-MEDIATED (the system preamble mediates anchoring)",
         ("keep","keep","keep","keep"):"CONTENT-MEDIATED (block content/filler mediates anchoring; marker does NOT)"}
    anchor_ok=(arm_res["ROLE"]["outcome"]=="keep")
    verdict=MAP.get(pattern, f"UNMAPPED pattern {pattern} -- report raw (some arm INDETERMINATE or mixed)")
    if not anchor_ok: verdict=f"ANCHOR-FAIL: ROLE outcome={arm_res['ROLE']['outcome']} (expected keep, reproducing OPX-02); "+verdict

    out={"prereg":"PREREG_OPX07.md","SMOKE":SMOKE,"transformers":transformers.__version__,"layers":LAYERS,"n_pairs":N,
         "nuisance_0.06xasymROLE":nuisance,"determinacy_threshold_3x":thr,"asym_ROLE_normal":asym_ROLE_n,
         "arms":arm_res,"pattern":pattern,"anchor_ROLE_keeps":bool(anchor_ok),"verdict":verdict,
         "scope":"raw dY primary (B flips w/ order). signs_keep=block-anchored, signs_swap=position; SIGN-DETERMINACY gate per arm "
                 "(|dY| CIs excl 0 AND >=3x the 6% OPX-03 offset nuisance) else INDETERMINATE. Content+filler kept => non-degenerate "
                 "(flip!=twin 0/720 step-zero). 4-arm matrix isolates role-semantic/symmetry-breaking/preamble/content. Single model.",
         "runtime_s":round(time.time()-t0,1)}
    import csv
    with open(os.path.join(OUT,"opx07_arms_smoke.csv" if SMOKE else "opx07_arms.csv"),"w",newline="") as fc:
        w=csv.writer(fc); w.writerow(["arm","dY_sys_n","dY_sys_f","dY_usr_n","dY_usr_f","asym_n","asym_f","B_n","B_f","determinate","outcome"])
        for m in ARMS:
            a=arm_res[m]; w.writerow([m,round(a["dY_sys_n"],3),round(a["dY_sys_f"],3),round(a["dY_usr_n"],3),round(a["dY_usr_f"],3),
                                      round(a["asym_n"],3),round(a["asym_f"],3),round(a["B_n"],3),round(a["B_f"],3),a["determinate"],a["outcome"]])
    np.savez(os.path.join(OUT,"opx07_peritem"+("_smoke" if SMOKE else "")+".npz"), use=np.array(use), tmpl=tmpl,
             **{f"Yb_{m}_{o}":Yb[(m,o)] for m in ARMS for o in ("n","f")},
             **{f"Ys_{m}_{o}":Ys[(m,o)] for m in ARMS for o in ("n","f")},
             **{f"Yu_{m}_{o}":Yu[(m,o)] for m in ARMS for o in ("n","f")})
    fn=os.path.join(OUT,"opx07_smoke.json" if SMOKE else "opx07.json"); json.dump(out,open(fn,"w"),indent=2)
    for m in ARMS:
        a=arm_res[m]; log(f"[OPX7] {m}: dYsys n{a['dY_sys_n']:+.2f}/f{a['dY_sys_f']:+.2f} dYusr n{a['dY_usr_n']:+.2f}/f{a['dY_usr_f']:+.2f} det={a['determinate']} -> {a['outcome']}")
    log(f"[OPX7] nuisance={nuisance:.2f} thr={thr:.2f} pattern={pattern} anchor={anchor_ok} -> {verdict}; wrote {fn}")

if __name__ == "__main__":
    main()
