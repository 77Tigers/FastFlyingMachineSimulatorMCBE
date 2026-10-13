"""Regenerates the N4 contract n4_13 (mmwmmw body pushes itself at slot 1; "pull twice" body).

Source: flyers/bank/pl22/pull_twice_mmwmmw.flyer, bank file at tick 0 (state at tick 12k is the tick-0 state
translated by 4k, verified for k=1..3, so no warm-up snapshot is needed).
Reference stroke: slot 1, actor sticky-less piston B6 carried by B7, powered by B7's own redstone/observer.
Kept: glue body B7 (17 cells: target = carrier = power source), actor B6, the other B7 pusher B4 (slot 4), and the
passenger piston B11.  B7's two pulls (slots 0 and 3) come from removed pistons (B14, B13, powered by body B8): prescribed.
The kept pistons also ride strokes of removed bodies B8/B9 (B4 slot 2, B6 slot 5, B11 slots 2 and 5): prescribed, cap 1.
Passengers B0, B13, B14 (and B1, B12) are omitted: they ride removed bodies, or (B14) are already extended at tick 0.
"""
import sys, json
from pathlib import Path
CDIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CDIR.parent))
from _n4lib import *

SRC = ROOT / "flyers/bank/pl22/pull_twice_mmwmmw.flyer"
SNAP_TICKS = 0
KEPT = [7, 6, 4, 11]
PORTS = [
    dict(name="target_in", role="input", body=7, prescribed=[0, 3]),
    dict(name="target_out", role="output", body=7),
    dict(name="piston4_in", role="input", body=4, prescribed=[2], cap={2: 1}, nobase=True),
    dict(name="piston6_in", role="input", body=6, prescribed=[5], cap={5: 1}, nobase=True),
    dict(name="piston11_in", role="input", body=11, prescribed=[2, 5], cap={2: 1, 5: 1}, nobase=True),
]

if __name__ == "__main__":
    res = finalize(CDIR, "n4_13", SRC, SNAP_TICKS, KEPT, PORTS)
    f = res["facts"]
    print({k: v for k, v in f.items() if k not in ("ports", "ref_strokes")})
    for p in f["ports"]:
        print(p["name"], p["role"], p["at"], p["word"], "prescribed", p["prescribed"], "cap", p["cap"])
    print(json.dumps(res["orders"]))
