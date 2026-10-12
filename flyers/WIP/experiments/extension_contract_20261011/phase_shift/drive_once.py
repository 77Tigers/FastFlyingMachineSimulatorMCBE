"""Write a rotated starting Flyer and the first-cycle external input script."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SAT = HERE.parents[1] / "two_bps_20261007"
sys.path[:0] = [str(ROOT), str(SAT)]
from satflyer5 import to_flyer

old = [
    ("A", (0, 1, 4), {
        (-1, 0, 0): "g", (0, 0, 0): "P2", (0, 0, 1): "g",
        (0, 0, 2): "g",
    }, "slime"),
    ("B", (0, 1, 2), {
        (0, 1, -1): "g", (1, 1, -1): "g", (2, 0, -1): "g",
        (2, 1, -1): "g", (3, 0, -1): "g", (3, 1, -1): "g",
        (3, 2, -1): "g", (4, 1, -1): "g", (0, 1, 0): "P3",
        (4, 1, 0): "S3",
    }, "honey"),
    ("C", (2, 3, 4), {
        (2, 0, 1): "R", (2, 2, 0): "O3", (3, 0, 0): "g",
        (3, 0, 1): "g", (3, 1, 0): "g", (3, 2, 0): "g",
        (4, 2, 0): "g", (5, 2, 0): "g", (6, 2, 0): "O3",
    }, "slime"),
]

# Start at old slot 4, before its movement. The per-segment initial offsets
# are the number of earlier moves in the old cycle: A=2, B=3, C=2.
offsets = {"A": 2, "B": 3, "C": 2}
rotated = []
for name, _, cells, mat in old:
    new_word = {"A": (0, 1, 2), "B": (1, 2, 3), "C": (0, 3, 4)}[name]
    translated = {(x + offsets[name], y, z): k for (x, y, z), k in cells.items()}
    rotated.append((name, new_word, translated, mat))

flyer = to_flyer(rotated, 10, 5)
flyer.save(str(HERE / "candidate_rotated.flyer"))

# Fixture contact targets: A's side glue next to its P2; B's leading glue site.
# These coordinates advance with their carrier after every successful stroke.
rows = []
for tick, x, z in [(0, 2, 17), (2, 3, 18), (4, 4, 17)]:
    rows.append(f"{tick} {x} 0 {z} 11")
for tick, x, y in [(2, 5, 0), (4, 7, 2), (6, 7, 0)]:
    rows.append(f"{tick} {x} {y} 15 11")
(HERE / "drive_once.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
print(HERE / "candidate_rotated.flyer")
print(HERE / "drive_once.txt")
