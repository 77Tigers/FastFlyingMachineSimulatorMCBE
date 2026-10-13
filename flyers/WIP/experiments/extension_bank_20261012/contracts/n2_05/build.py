"""n2_05: N2 rear cap, pull@1 of mmww+wmmw by wwmm carrier (adapted from extension_contract_20261011/prescribed_fixture/rear_cap)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from n2_common import *
HERE = Path(__file__).resolve().parent

REF = ROOT / "flyers/bank/pl7/tm_7pl_2.5bps.flyer"
KEEP = [
    (0, 0, 15), (0, 1, 15), (0, 0, 16), (0, 1, 16), (0, 1, 17),   # K0
    (2, 0, 15), (2, 1, 15), (1, 1, 15),                           # N (+ extended arm)
    (2, 0, 17), (3, 0, 16), (3, 0, 17), (3, 1, 16), (3, 1, 17), (3, 2, 17),  # K1
    (3, 2, 16),                                                   # redstone relay (input)
]
PORTS_IN = [
    {"name": "redstone_input", "at": (3, 2, 16), "word": "mmww", "slots": [0, 1], "limit": 1},
    {"name": "k1_input", "at": (3, 1, 17), "word": "wwmm", "slots": [3], "limit": [None, None, 6, 6]},
]
PORTS_OUT = [
    {"name": "k0_output", "at": (0, 1, 15), "word": "mmww"},
    {"name": "n_output", "at": (2, 0, 15), "word": "wmmw"},
]
SHIFT = make_candidate(REF, KEEP, HERE / "candidate.flyer")
PORTS_IN[:] = shift_ports(PORTS_IN, SHIFT); PORTS_OUT[:] = shift_ports(PORTS_OUT, SHIFT)
(HERE / "drive.txt").write_text("\n".join(drive_rows(PORTS_IN)) + "\n", encoding="ascii")
for order in ("before_natural", "after_natural"):
    write_contract(HERE, "n2_05-pl7-rearcap", order, PORTS_IN, PORTS_OUT)
print("built n2_05:", len(KEEP), "cells")
