"""n2_03: C:wmmw|S:-|pull@0|T:mmww  (load 5; rotated occurrence: sticky B2 'mwwm' pull@2 of B0 'wwmm').
Source: flyers/bank/pl9/rigid_chain_capped.flyer: sticky piston B2 (16,1,15) retracts at slot 2 pulling B0 (5 cells).
B2 is powered by the observer (16,2,15) of B1 (kept as a 1-block input). B0's own pistons lose their power sources (3 RBs
of B3/B1 ablated: fixture still passes), so they stay retracted."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from n2_common import *
HERE = Path(__file__).resolve().parent

REF = ROOT / "flyers/bank/pl9/rigid_chain_capped.flyer"
TARGET = [(15, 1, 14), (15, 1, 15), (15, 1, 16), (15, 2, 16), (15, 3, 16)]   # B0 wwmm
CARRIER = [(16, 1, 15)]                                                       # B2 mwwm sticky piston
OB1 = [(16, 2, 15)]                                                           # B1 observer (powers B2)
KEEP = with_arms(REF, TARGET + CARRIER + OB1)
PORTS_IN = [
    {"name": "target_wwmm", "at": (15, 1, 15), "word": "wwmm", "slots": [3], "limit": [None, None, 5, 6]},
    {"name": "carrier_mwwm", "at": (16, 1, 15), "word": "mwwm", "slots": [0], "limit": [1, None, None, 6]},
    {"name": "ob1", "at": (16, 2, 15), "word": "mmww", "slots": [0, 1], "limit": 1},
]
PORTS_OUT = []
if __name__ == "__main__":
    SHIFT = make_candidate(REF, KEEP, HERE / "candidate.flyer")
    PORTS_IN[:] = shift_ports(PORTS_IN, SHIFT); PORTS_OUT[:] = shift_ports(PORTS_OUT, SHIFT)
    (HERE / "drive.txt").write_text("\n".join(drive_rows(PORTS_IN)) + "\n", encoding="ascii")
    for order in ("before_natural", "after_natural"):
        write_contract(HERE, "n2_03-pl9rigid", order, PORTS_IN, PORTS_OUT)
    print("built n2_03:", len(KEEP), "cells")
