"""Regenerates the N4 contract n4_14 (unpowered sticky pull of an mmwwmm 16-cell body at load 16).

Source: flyers/bank/pl22/exclusive_roles_3p333.flyer, settled snapshot after 48 ticks.
"""
import sys, json
from pathlib import Path
CDIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CDIR.parent))
from _n4lib import *

SRC = ROOT / "flyers/bank/pl22/exclusive_roles_3p333.flyer"
SNAP_TICKS = 48
KEPT = [0, 20]
EXTRA = [(17, 12, 18)]           # redstone block of B60 that powers B20's sticky piston at slot 3
# Same-tick row order of the prescribed script: carrier B20 first (it vacates the cells B0 is pulled into), then the
# target, then the lone redstone block.
ORDER = {"carrier_in": 0, "target_in": 1, "src60_in": 2}
PORTS = [
    dict(name="src60_in", role="input", body=60, at=(17, 12, 18), prescribed=[0, 3, 4, 5], cap={0: 1, 3: 1, 4: 1, 5: 1}),
    dict(name="carrier_in", role="input", body=20, prescribed=[0, 1, 2, 5]),
    dict(name="target_out", role="output", body=0),
    dict(name="target_in", role="input", body=0, prescribed=[0, 1, 5]),
]

if __name__ == "__main__":
    res = finalize(CDIR, "n4_14", SRC, SNAP_TICKS, KEPT, PORTS, extra_cells=EXTRA, prio=lambda p, s: ORDER[p["name"]])
    f = res["facts"]
    print({k: v for k, v in f.items() if k not in ("ports", "ref_strokes")})
    for p in f["ports"]:
        print(p["name"], p["role"], p["at"], p["word"], "prescribed", p["prescribed"], "cap", p["cap"])
    print(json.dumps(res["orders"]))
