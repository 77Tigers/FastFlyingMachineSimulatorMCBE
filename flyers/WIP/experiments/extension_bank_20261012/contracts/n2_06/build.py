"""n2_06: C:mwmw/wmwm|S:-|pull@0|T:mwmw  (load 8; rotated occurrence: sticky B5 (17,1,15) retracts at slot 1 pulling B3 'wmwm').
Source: flyers/bank/pl8/hop_pair_rod_observer.flyer (a whole 16-cell 2.5 bps / PL8 flyer). Everything is kept except the hop
piston B1 (15,1,16), whose slot-0 push of B2 (with passengers B0, B4; load 8) is replaced by a prescribed stroke on B2."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from n2_common import *
HERE = Path(__file__).resolve().parent

REF = ROOT / "flyers/bank/pl8/hop_pair_rod_observer.flyer"
B0 = [(14, 2, 15)]                                                                         # hop piston (passenger/actor)
B2 = [(14, 2, 16), (15, 2, 16), (15, 2, 17), (16, 1, 16), (16, 2, 15), (16, 2, 16)]        # mwmw glue + rod
B3 = [(15, 0, 15), (15, 0, 16), (15, 1, 15), (16, 0, 15), (17, 0, 14), (17, 0, 15)]        # wmwm glue + observer (target)
B4 = [(16, 0, 16)]                                                                         # sticky
B5 = [(17, 1, 15)]                                                                         # sticky: actor of the primitive
KEEP = with_arms(REF, B0 + B2 + B3 + B4 + B5)
PORTS_IN = [
    {"name": "b2_mwmw", "at": (14, 2, 16), "word": "mwmw", "slots": [0], "limit": [8, None, 8, None]},
]
PORTS_OUT = [
    {"name": "b3_wmwm", "at": (15, 0, 15), "word": "wmwm"},
]
if __name__ == "__main__":
    SHIFT = make_candidate(REF, KEEP, HERE / "candidate.flyer")
    PORTS_IN[:] = shift_ports(PORTS_IN, SHIFT); PORTS_OUT[:] = shift_ports(PORTS_OUT, SHIFT)
    (HERE / "drive.txt").write_text("\n".join(drive_rows(PORTS_IN)) + "\n", encoding="ascii")
    for order in ("before_natural", "after_natural"):
        write_contract(HERE, "n2_06-pl8hoppair", order, PORTS_IN, PORTS_OUT)
    print("built n2_06:", len(KEEP), "cells")
