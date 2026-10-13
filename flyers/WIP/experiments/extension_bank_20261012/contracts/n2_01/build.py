"""n2_01: C:wwmm|S:mmww|push@0|T:mmww  (load 5).
Source: flyers/bank/pl8/mirrored_chains_shared_mwmw.flyer, chain z=15-19: K1 (wwmm, piston (3,2,17)) pushes the RB-bearing
stage (mmww, RB (3,2,16)) at slot 0; the stage's sticky (4,1,17) pulls K1 at slot 3 (mutual -> both bodies kept)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from n2_common import *
HERE = Path(__file__).resolve().parent

REF = ROOT / "flyers/bank/pl8/mirrored_chains_shared_mwmw.flyer"
CARRIER = [(2, 0, 17), (3, 0, 16), (3, 0, 17), (3, 1, 16), (3, 1, 17), (3, 2, 17)]   # B5 wwmm
TARGET = [(3, 2, 16), (4, 1, 17), (4, 2, 16), (4, 2, 17), (4, 2, 18)]                 # B6 mmww (RB inside)
NEXT_RB = [(6, 1, 18)]                                                                # B9's redstone block (powers B6 pistons)
KEEP = with_arms(REF, CARRIER + TARGET + NEXT_RB)
PORTS_IN = [
    {"name": "carrier_wwmm", "at": (3, 1, 17), "word": "wwmm", "slots": [2], "limit": [None, None, 6, 6]},
    {"name": "target_mmww", "at": (4, 2, 17), "word": "mmww", "slots": [1], "limit": [5, 5, None, None]},
    {"name": "next_rb", "at": (6, 1, 18), "word": "wwmm", "slots": [2, 3], "limit": 1},
]
PORTS_OUT = []
if __name__ == "__main__":
    SHIFT = make_candidate(REF, KEEP, HERE / "candidate.flyer")
    PORTS_IN[:] = shift_ports(PORTS_IN, SHIFT); PORTS_OUT[:] = shift_ports(PORTS_OUT, SHIFT)
    (HERE / "drive.txt").write_text("\n".join(drive_rows(PORTS_IN)) + "\n", encoding="ascii")
    for order in ("before_natural", "after_natural"):
        write_contract(HERE, "n2_01-pl8mirrored", order, PORTS_IN, PORTS_OUT)
    print("built n2_01:", len(KEEP), "cells")
