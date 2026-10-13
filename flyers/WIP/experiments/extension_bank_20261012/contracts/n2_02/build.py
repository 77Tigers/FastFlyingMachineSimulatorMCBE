"""n2_02: C:wwmm|S:-|pull@1|T:mmww  (load 5).
Source: flyers/bank/pl8/mirrored_chains_shared_mwmw.flyer, chain z=17-19: stage B9 (wwmm, sticky (7,2,17)) pulls stage B6 (mmww)
at slot 1; B6's piston (4,2,18) pushes B9 back at slot 2 (mutual -> both bodies kept). B9's pistons are powered by a rod of B10."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from n2_common import *
HERE = Path(__file__).resolve().parent

REF = ROOT / "flyers/bank/pl8/mirrored_chains_shared_mwmw.flyer"
CARRIER = [(6, 1, 18), (7, 1, 18), (7, 2, 17), (7, 2, 18), (7, 3, 18)]   # B9 wwmm
TARGET = [(3, 2, 16), (4, 1, 17), (4, 2, 16), (4, 2, 17), (4, 2, 18)]    # B6 mmww
RODS = [(8, 2, 17)]                                                       # B10 power rod (mmww); B10's 2nd rod (7,4,18) ablated (not needed)
KEEP = with_arms(REF, CARRIER + TARGET + RODS)
PORTS_IN = [
    {"name": "carrier_wwmm", "at": (7, 2, 18), "word": "wwmm", "slots": [3], "limit": [None, None, 5, 5]},
    {"name": "target_mmww", "at": (4, 2, 17), "word": "mmww", "slots": [0], "limit": [5, 5, None, None]},
    {"name": "rod_a", "at": (8, 2, 17), "word": "mmww", "slots": [0, 1], "limit": 1},
]
PORTS_OUT = []
if __name__ == "__main__":
    SHIFT = make_candidate(REF, KEEP, HERE / "candidate.flyer")
    PORTS_IN[:] = shift_ports(PORTS_IN, SHIFT); PORTS_OUT[:] = shift_ports(PORTS_OUT, SHIFT)
    (HERE / "drive.txt").write_text("\n".join(drive_rows(PORTS_IN)) + "\n", encoding="ascii")
    for order in ("before_natural", "after_natural"):
        write_contract(HERE, "n2_02-pl8mirrored", order, PORTS_IN, PORTS_OUT)
    print("built n2_02:", len(KEEP), "cells")
