"""n2_04: C:mwwm|S:mwwm/wmmw|push@1|T:mmww  (load 2; rotated occurrence: K0 'mmww' piston (0,0,15) pushes N 'wmmw' at slot 2).
Source: flyers/bank/pl8/mirrored_chains_shared_mwmw.flyer chain z=15-17. Mutual: N's sticky (2,1,15) pulls K0 at slot 0.
K0's pistons are powered by K1's rod (2,0,17), N's sticky by K1's observer (3,0,16) (both kept as 1-block inputs)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from n2_common import *
HERE = Path(__file__).resolve().parent

REF = ROOT / "flyers/bank/pl8/mirrored_chains_shared_mwmw.flyer"
K0 = [(0, 0, 15), (0, 0, 16), (0, 1, 15), (0, 1, 16), (0, 1, 17)]   # mmww (carrier of the push)
N = [(2, 0, 15), (2, 1, 15)]                                          # wmmw (target; sticky + slime)
ROD = [(2, 0, 17)]                                                    # K1 rod: power source of K0's pistons
OBS = [(3, 0, 16)]                                                    # K1 observer: power source of N's sticky (slot 3 extension)
KEEP = with_arms(REF, K0 + N + ROD + OBS)
PORTS_IN = [
    {"name": "k0_mmww", "at": (0, 1, 15), "word": "mmww", "slots": [1], "limit": [5, 7, None, None]},
    {"name": "rod", "at": (2, 0, 17), "word": "wwmm", "slots": [2, 3], "limit": 1},
    {"name": "obs", "at": (3, 0, 16), "word": "wwmm", "slots": [2, 3], "limit": 1},
]
PORTS_OUT = [
    {"name": "n_wmmw", "at": (2, 0, 15), "word": "wmmw"},
]
if __name__ == "__main__":
    SHIFT = make_candidate(REF, KEEP, HERE / "candidate.flyer")
    PORTS_IN[:] = shift_ports(PORTS_IN, SHIFT); PORTS_OUT[:] = shift_ports(PORTS_OUT, SHIFT)
    (HERE / "drive.txt").write_text("\n".join(drive_rows(PORTS_IN)) + "\n", encoding="ascii")
    for order in ("before_natural",):   # after_natural only passes with obs slot-2 cap 3 (> reference 2): see NOTES.md
        write_contract(HERE, "n2_04-pl8mirrored", order, PORTS_IN, PORTS_OUT)
    print("built n2_04:", len(KEEP), "cells")
