"""Build the hand-pinned rotated B/C flyer and its 12-tick input test."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
SAT = HERE.parents[2] / "two_bps_20261007"
sys.path[:0] = [str(ROOT), str(SAT)]
from satflyer5 import to_flyer

b = ("B", (1, 2, 3), {
    (3, 0, 0): "P4", (3, 2, 0): "S4",
    (3, 1, 0): "g", (3, 1, 1): "g",
}, "slime")
c_cells = {(x, 2, 0): "g" for x in range(1, 6)}
c_cells.update({(5, 1, 0): "g", (5, 0, 0): "g", (3, 1, 0): "O0"})
c = ("C", (0, 3, 4), c_cells, "slime")
to_flyer([b, c], 12, 5).save(str(HERE / "candidate.flyer"))

# Three supplied strokes for B (slots 1,2,3). Alternate the two transverse
# contact sites to leave each previous fixture arm clear until tick+3 cleanup.
rows = [
    "2 3 1 0 12",
    "4 4 1 1 12",
    "6 5 1 0 12",
]
(HERE / "drive.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
