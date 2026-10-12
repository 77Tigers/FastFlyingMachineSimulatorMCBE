"""Pinned, small SAT check for the single-input contact/push/pull topology.

External stroke at B's third move is intentionally not represented as an
ordinary cause: C's slot-3 input collision is waived by ext_3 and must be
validated against the real simulator trace. The closed slot-4 push and
slot-0 sticky pull remain genuine SAT obligations.
"""
from itertools import product
import pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
SAT = HERE.parents[2] / "two_bps_20261007"
sys.path.insert(0, str(SAT))
from satflyer5 import FlyerSAT, show


def main():
    b = {(3, 0, 0): "P4", (3, 2, 0): "S4",
         (3, 1, 0): "g", (3, 1, 1): "g"}
    c = {(x, 2, 0): "g" for x in range(1, 6)}
    c.update({(5, 1, 0): "g", (5, 0, 0): "g", (3, 1, 0): "O0"})
    box = list(product(range(-2, 13), range(-2, 6), range(-2, 4)))
    S = FlyerSAT(
        [(1, 2, 3), (0, 3, 4)], box, 12, NS=5,
        kinds=["g", "O0"], leaf=True, maxglue=7,
        names=["B", "C"],
        kinds_by_seg={"B": ["g", "P4", "S4"], "C": ["g", "O0"]},
        open_segs={"B": {"ext_1", "ext_2", "ext_3"},
                   "C": {"ext_3"}},
        must={"B": b, "C": c}, skip=("move",),
    )
    for name, kinds in (("B", {"P4": 1, "S4": 1, "g": 2}),
                        ("C", {"O0": 1, "g": 7})):
        j = S.names.index(name)
        for kind, count in kinds.items():
            S.m.Add(sum(S.X[j, u, kind] for u in S.boxes[j]) == count)
    status, elapsed = S.solve(40, 2, objective="maxload")
    print(f"status={status} elapsed_s={elapsed:.2f}")
    if status not in ("FEASIBLE", "OPTIMAL"):
        return 1
    print(show(S.extract()))
    for key, value in sorted(S.loads().items(), key=lambda item: str(item[0])):
        print(f"load {key}: {value}")
    print("causes:")
    for row in S.causes():
        print(" ", row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
