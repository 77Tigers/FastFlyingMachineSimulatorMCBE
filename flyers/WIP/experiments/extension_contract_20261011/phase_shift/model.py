"""One small CP-SAT contact geometry experiment for the 3-bps phase-shift proposal.

This is a geometry/model experiment only. ext_<slot> waives the endogenous
cause requirement at declared external input strokes; it does not implement
those strokes or claim a periodic Flyer implementation. The selected seed uses
skip=("move",) to test contacts while permitting a same-slot occupied-cell
handoff; that relaxed result is not a valid ordinary SAT witness.
"""
from itertools import product
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
SAT = HERE.parents[1] / "two_bps_20261007"
sys.path.insert(0, str(SAT))
from satflyer5 import FlyerSAT, show


def main():
    # Pin only the two expected contact sites. The search places the six glue
    # cells, one redstone block and two observers around them.
    c = {(3, 0, 0): "g", (3, 1, 0): "g"}
    box = list(product(range(-1, 9), range(-2, 4), range(-1, 3)))
    kinds = {
        "A": ["g", "P2"],
        "B": ["g", "P3", "S3"],
        "C": ["g", "R", "O3"],
    }
    must = {
        "A": {(0, 0, 0): "P2", (0, 0, 1): "g", (0, 0, 2): "g"},
        "B": {(0, 1, 0): "P3", (4, 1, 0): "S3", (4, 2, -1): "g"},
        "C": c,
    }
    S = FlyerSAT(
        [(0, 1, 4), (0, 1, 2), (2, 3, 4)], box, 11, NS=5,
        kinds=["g", "R", "O3"], leaf=True, maxglue=9,
        names=["A", "B", "C"],
        open_segs={"A": {"ext_0", "ext_1", "ext_4"},
                   "B": {"ext_0", "ext_1", "ext_2"}},
        kinds_by_seg=kinds, must=must, skip=("move",),
    )
    for name, k, count in [("A", "P2", 1), ("B", "P3", 1),
                           ("B", "S3", 1), ("B", "g", 9), ("A", "g", 3),
                           ("C", "R", 1), ("C", "O3", 2), ("C", "g", 6)]:
        j = S.names.index(name)
        S.m.Add(sum(S.X[j, u, k] for u in S.boxes[j]) == count)
    status, elapsed = S.solve(55, 4, objective="maxload")
    print(f"status={status} elapsed_s={elapsed:.2f}")
    if status not in ("OPTIMAL", "FEASIBLE"):
        return 1
    sol = S.extract()
    print(show(sol))
    loads = S.loads()
    print("loads_by_segment_and_slot:")
    for key, value in sorted(loads.items(), key=lambda item: str(item[0])):
        print(f"  {key}: {value}")
    print("causes:")
    for row in S.causes():
        print(" ", row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
