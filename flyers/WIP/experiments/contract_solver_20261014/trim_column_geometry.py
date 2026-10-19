"""Remove one glue cell from a bare natural column problem, preserving coordinates.

Re-anchor a removed port explicitly with --reanchor PORT_INDEX:X,Y,Z. This
creates a research fixture, not a verified machine or certified hardware pool.
"""
import argparse
import hashlib
import json
from pathlib import Path

from assemble import body_of, Flyer


def coord(text):
    result = tuple(map(int, text.split(",")))
    if len(result) != 3:
        raise ValueError("coordinates need three integers")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--remove", required=True, type=coord)
    parser.add_argument("--reanchor", action="append", default=[])
    args = parser.parse_args()
    source = args.problem.resolve()
    c = json.loads(source.read_text())
    if any(k in c for k in ("prescribed_script", "drive_script")):
        raise ValueError("requires a bare natural problem")
    flyer_source = source.parent / c["flyer"]
    f = Flyer.load(flyer_source)
    if any(b.kind in (6, 7, 8, 9, 10) for b in f._cells.values()):
        raise ValueError("requires bare geometry without hardware")
    if args.remove not in f._cells or f._cells[args.remove].kind not in (1, 2):
        raise ValueError("removal must be a glue cell")
    bodies = [body_of(f._cells, tuple(p["at"])) for p in c["ports"]]
    f.remove(args.remove)
    for item in args.reanchor:
        index, at = item.split(":", 1)
        index, at = int(index), coord(at)
        if at not in bodies[index] - {args.remove}:
            raise ValueError("new representative must belong to the original body")
        c["ports"][index]["at"] = list(at)
    for port, original in zip(c["ports"], bodies):
        if body_of(f._cells, tuple(port["at"])) != original - {args.remove}:
            raise ValueError("removal changes body connectivity")
    args.output.mkdir(parents=True, exist_ok=True)
    destination = args.output / "problem.flyer"
    before = {p: b.encode() for p, b in f._cells.items()}
    f.save(destination)
    g = Flyer.load(destination)
    minimum = lambda cells: tuple(min(p[i] for p in cells) for i in range(3))
    delta = tuple(b - a for a, b in zip(minimum(before), minimum(g._cells)))
    shift = lambda p: [a + b for a, b in zip(p, delta)]
    expected = {tuple(shift(p)): cell for p, cell in before.items()}
    if expected != {p: b.encode() for p, b in g._cells.items()}:
        raise ValueError("save changed more than translation")
    for port in c["ports"]:
        port["at"] = shift(port["at"])
    c["required_cells"] = [dict(row, at=shift(row["at"])) for row in c["required_cells"]
                           if tuple(row["at"]) != args.remove]
    if c.get("boundary_envelope"):
        c["boundary_envelope"] = {key: shift(value) for key, value in c["boundary_envelope"].items()}
    c["name"] += "-trimmed"
    c["flyer"] = "problem.flyer"
    (args.output / "problem.json").write_text(json.dumps(c, indent=2) + "\n")
    manifest = {"source": str(source), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "source_flyer_sha256": hashlib.sha256(flyer_source.read_bytes()).hexdigest(),
                "removed_glue": args.remove, "reanchors": args.reanchor, "save_translation": delta,
                "verified": False}
    (args.output / "mutation.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
