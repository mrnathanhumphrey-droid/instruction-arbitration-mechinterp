"""On-instance self-terminate watchdog (break-proof). Deployed + armed by the launcher BEFORE the run, so
the instance cleans itself up even if the local launcher dies (session break). Terminates THIS instance via
the Lambda API when: PULLED flag appears / result json has existed for GRACE / run process died without a
result / HARDCAP elapsed. Key read from a sibling file, never a command line. argv: IID RESULT_JSON [RUNPROC]"""
import sys, time, os, requests

IID = sys.argv[1]
RESULT = sys.argv[2]
RUNPROC = sys.argv[3] if len(sys.argv) > 3 else "lambda.py"
D = os.path.dirname(RESULT) or "."
KEY = open(os.path.join(D, ".lam_key")).read().strip()
H = {"Authorization": "Bearer " + KEY}
PULLED = os.path.join(D, "PULLED")
GRACE = int(os.environ.get("WD_GRACE", "3600"))       # after result appears, let the launcher pull
HARDCAP = int(os.environ.get("WD_HARDCAP", "25200"))  # 7h absolute runaway guard
t0 = time.time(); dead = 0

def terminate(reason):
    print(f"[WD] terminate ({reason}) at {time.time()-t0:.0f}s", flush=True)
    for _ in range(12):
        try:
            r = requests.post("https://cloud.lambda.ai/api/v1/instance-operations/terminate",
                              headers=H, json={"instance_ids": [IID]}, timeout=30)
            print(f"[WD] {r.status_code} {r.text[:160]}", flush=True)
            if r.status_code < 300:
                return
        except Exception as e:
            print(f"[WD] err {e}", flush=True)
        time.sleep(15)

print(f"[WD] armed {IID} result={RESULT} grace={GRACE} hardcap={HARDCAP}", flush=True)
while True:
    el = time.time() - t0
    if os.path.exists(PULLED):
        terminate("PULLED flag"); break
    if el > HARDCAP:
        terminate("hardcap"); break
    if os.path.exists(RESULT):
        if time.time() - os.path.getmtime(RESULT) > GRACE:
            terminate("result+grace"); break
    else:
        alive = (os.system(f"pgrep -f {RUNPROC} >/dev/null 2>&1") == 0)
        dead = 0 if alive else dead + 1
        if dead >= 5 and el > 600:      # 5 consecutive misses past startup -> crashed/killed, no result
            terminate("run died without result"); break
    time.sleep(60)
print("[WD] done", flush=True)
