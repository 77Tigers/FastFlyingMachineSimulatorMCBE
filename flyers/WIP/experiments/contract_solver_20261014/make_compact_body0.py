"""Build an eight-glue tm_smol body0 with its rear carrier contact retained.

Shorten the forward fork and turn its Z branch into free space. Bare geometry
only; generated hardware must be recertified against this changed problem.
"""
import argparse
import hashlib
import json
from pathlib import Path

from assemble import body_of, Flyer


def build(problem, output, added):
    c = json.loads(problem.read_text())
    source = problem.parent / c["flyer"]
    f = Flyer.load(source)
    if any(b.kind in (6, 7, 8, 9, 10) for b in f._cells.values()):
        raise ValueError("input must be bare geometry")
    old_bodies = [body_of(f._cells, tuple(p["at"])) for p in c["ports"]]
    removed = {(5, 5, 4), (5, 4, 4), (5, 3, 4), (5, 4, 3)}
    if not removed <= old_bodies[0] or added & f._cells.keys():
        raise ValueError("input does not match the intended fork")
    cell = f._cells[tuple(c["ports"][0]["at"])]
    for p in removed:
        f.remove(p)
    for p in added:
        f.set(p, cell)
    for i, port in enumerate(c["ports"]):
        expected = (old_bodies[i] - removed) | added if i == 0 else old_bodies[i]
        if body_of(f._cells, tuple(port["at"])) != expected:
            raise ValueError(f"mutation merged or disconnected body {i}")
    if len(body_of(f._cells, tuple(c["ports"][0]["at"]))) != 8:
        raise ValueError("expected eight glue cells")
    output.mkdir(parents=True, exist_ok=True)
    f.save(output / "problem.flyer")
    g = Flyer.load(output / "problem.flyer")
    if {p: b.encode() for p, b in f._cells.items()} != {p: b.encode() for p, b in g._cells.items()}:
        raise ValueError("unexpected save normalization")
    old_required = {tuple(r["at"]) for r in c["required_cells"]}
    if not removed <= old_required:
        raise ValueError("removed cells were not required geometry")
    c["required_cells"] = [r for r in c["required_cells"] if tuple(r["at"]) not in removed]
    c["required_cells"] += [{"at": list(p), "cell": cell.encode()} for p in sorted(added)]
    c["name"] += "-compact-body0"
    c["flyer"] = "problem.flyer"
    (output / "problem.json").write_text(json.dumps(c, indent=2) + "\n")
    (output / "mutation.json").write_text(json.dumps({
        "verified": False, "source": str(problem.resolve()),
        "source_sha256": hashlib.sha256(problem.read_bytes()).hexdigest(),
        "source_flyer_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "removed": sorted(removed), "added": sorted(added), "body0_glue_cells": 8,
    }, indent=2) + "\n")
    print("Eight-glue fork built; all 13 body components preserved; save round trip passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build(args.problem, args.output, {(4, 4, 4), (4, 3, 4), (4, 4, 5)})
