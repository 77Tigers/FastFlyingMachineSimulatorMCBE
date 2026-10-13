"""Regenerates the N4 contract n4_12 (carrier wwmmmm pushes target mmmmww at slot 0; four-push ring).

Source: flyers/bank/pl22/four_push_ring.flyer, settled snapshot after 48 ticks (4 periods = one full
16-block chunk-phase cycle; the bank file at tick 0 is not yet in steady state).
Kept: target glue body (B1, 17 cells, holds the redstone), carrier glue body (B14, 18 cells) and the five
loose pistons that act on or ride with the slot-0 push (actor + its four passengers).
The carrier's four strokes (slots 2-5) come from removed pistons and are prescribed; everything else is natural.
"""
import sys, json
from pathlib import Path
CDIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CDIR.parent))
from _n4lib import *

SRC = ROOT / "flyers/bank/pl22/four_push_ring.flyer"
SNAP_TICKS = 48
# bodytrack ids on the snapshot: B1 target (mmmmww), B14 carrier (wwmmmm); singles = loose pistons
# P3 = actor (15,1,15) carried by B14, P0/P2/P4/P6 = its passengers (also the later B1 pushers).
KEPT = [1, 14, 3, 0, 2, 4, 6]
PORTS = [
    dict(name="target_out", role="output", body=1),
    dict(name="carrier_in", role="input", body=14, prescribed=[2, 3, 4, 5]),
]

if __name__ == "__main__":
    res = finalize(CDIR, "n4_12", SRC, SNAP_TICKS, KEPT, PORTS, recurrence="exact")
    f = res["facts"]
    print({k: v for k, v in f.items() if k not in ("ports", "ref_strokes")})
    for p in f["ports"]:
        print(p["name"], p["role"], p["at"], p["word"], "prescribed", p["prescribed"], "cap", p["cap"])
    print(json.dumps(res["orders"]))
