"""HUNT-DRIFT-01 launcher input: the bit-check reference extracted from the pilot's OPEN outputs (no activations — the
runner needs only lp + lp_key; the Q3 role probe is refit locally, never on the instance).
  python make_pilot_lp.py
Reads trackA/pilot/out/pilot_acts_open.npz (sha recorded), writes pilot_lp_open.npz + pilot_pins.json here."""
import hashlib, json
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "pilot" / "out" / "pilot_acts_open.npz"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
Z = np.load(SRC); assert str(Z["open_arms"][0]) == "ORIG"
out = HERE / "pilot_lp_open.npz"
np.savez(out, lp=Z["lp"], lp_key=Z["lp_key"], open_arms=Z["open_arms"])
R = np.load(out); assert R["lp"].tobytes() == Z["lp"].tobytes() and R["lp_key"].tobytes() == Z["lp_key"].tobytes()
pins = {"pilot_lp_open.npz": sha(out)}
(HERE / "pilot_pins.json").write_text(json.dumps(pins, indent=1) + "\n", encoding="utf-8")
print(f"source {SRC.name} sha {sha(SRC)}; wrote {out.name} sha {pins['pilot_lp_open.npz']} ({len(R['lp'])} rows, bytes identical)")
