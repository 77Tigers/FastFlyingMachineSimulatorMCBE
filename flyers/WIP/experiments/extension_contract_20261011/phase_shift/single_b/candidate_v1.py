"""Generate one diagonal common-neighbour B/C fixture candidate.

This is a prescribed-input candidate, not a validated extension: the external
strokes are supplied by extension-drive and must still satisfy the trace.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
SAT = HERE.parents[2] / "two_bps_20261007"
sys.path[:0] = [str(ROOT), str(SAT)]
from satflyer5 import to_flyer

# P and S are diagonally offset, leaving two common neighbours. The main
# carrier glue serves both pistons; the second glue provides the alternating
# external +X drive lane required by the fixture lifecycle.
b = ("B", (1, 2, 3), {
    (3, 0, 1): "P4", (3, 1, 2): "S4",
    (3, 1, 1): "g", (3, 0, 0): "g",
}, "slime")

# Push and sticky-pull contact glues are joined by a short C body. O+Z is at
# (3,1,0), with its support at (4,1,0); at slot 4 it pulses toward B's hub.
c = ("C", (0, 3, 4), {
    (4, 0, 1): "g", (4, 1, 1): "g", (4, 1, 0): "g",
    (3, 1, 0): "O4",
}, "slime")

to_flyer([b, c], 12, 5).save(str(HERE / "candidate_v1.flyer"))
(HERE / "drive_v1.txt").write_text(
    "2 3 0 0 12\n4 4 1 1 12\n6 5 0 0 12\n", encoding="utf-8")
