"""Build a slot-zero flyer from a routed set of bodies and run the local screens."""

import argparse
import re
import subprocess
import tempfile
from collections import defaultdict
from hashlib import sha256
from pathlib import Path

from fastflyer import Block, Flyer, Kind

HERE = Path(__file__).resolve().parent
BIN = HERE.parents[4] / "target" / "release"


def assemble(path, target, limit=None):
    header, *rows = path.read_text().splitlines()
    bodies, design_limit = map(int, header.split())
    flyer = Flyer(push_limit=limit or design_limit)
    contents = defaultdict(list)
    for row in rows:
        body, kind, *position = row.split()
        contents[int(body), kind].append(tuple(map(int, position)))
    occupied = set()

    def put(pos, block):
        if pos in occupied:
            raise ValueError(f"Overlapping blocks at {pos}")
        occupied.add(pos)
        flyer.set(pos, block)

    for body in range(bodies):
        slot = (-2 * body) % 6
        for pos in contents[body, "G"]:
            put(pos, Block(Kind.HONEY if body % 2 else Kind.SLIME))
        for x, y, z, *direction in contents[body, "R"]:
            faces = [
                (1, 0, 0),
                (-1, 0, 0),
                (0, 1, 0),
                (0, -1, 0),
                (0, 0, 1),
                (0, 0, -1),
            ]
            block = (
                Block.rod(faces.index(tuple(direction)))
                if direction
                else Block(Kind.REDSTONE_BLOCK)
            )
            put((x, y, z), block)
        for x, y, z in contents[body, "S"]:
            put((x, y, z), Block.piston(1, sticky=True, state=2 if slot == 1 else 0))
            if slot == 1:
                put((x - 1, y, z), Block(Kind.PISTON_ARM))
        for firing, (x, y, z) in enumerate(sorted(contents[body, "H"]), 2):
            extended = slot == firing + 1
            dx = (
                -1 if extended or slot == 1 else -2 if slot == 0 or slot > firing else 0
            )
            put((x + dx, y, z), Block.piston(0, state=2 if extended else 0))
            if extended:
                put((x + dx + 1, y, z), Block(Kind.PISTON_ARM))
    flyer.save(str(target))
    lo, hi = flyer.bounds()
    print(
        target,
        "PL",
        flyer.push_limit,
        "blocks",
        len(occupied),
        "XYZ",
        tuple(b - a + 1 for a, b in zip(lo, hi)),
        sha256(target.read_bytes()).hexdigest(),
    )
    for i in range(bodies):
        print(i, {kind: len(contents[i, kind]) for kind in ("G", "R", "H", "S")})


def check(path):
    with tempfile.TemporaryDirectory(dir=HERE) as tmp:
        for decrement, phase in [(0, 0), (0, 7), (1, 0), (1, 7)]:
            flyer = Flyer.load(str(path))
            flyer.push_limit -= decrement
            flyer.rng_state = 0
            flyer.phase_x = flyer.phase_z = phase
            copy = Path(tmp) / path.name
            flyer.save(str(copy))
            for ticks in [240] if decrement else [240, 10000]:
                result = subprocess.check_output(
                    [BIN / "fastflyer-research", "audit", copy, str(ticks), "0"],
                    text=True,
                )
                print(result.replace(str(copy), path.name).rstrip(), flush=True)
                values = dict(re.findall(r"(\w+)=(-?\d+)", result))
                distance = int(values["distance"])
                failures = [
                    int(values[key])
                    for key in (
                        "extension_failures",
                        "movement_failures",
                        "conservation_mismatch_ticks",
                    )
                ]
                if int(values["limit"]) != flyer.push_limit or (
                    int(values["phase_x"]),
                    int(values["phase_z"]),
                ) != (phase, phase):
                    raise ValueError("The audit ran at a different push limit or phase")
                if decrement and distance >= ticks // 3:
                    raise ValueError("The lower-limit control kept flying")
                if not decrement and (distance < ticks // 3 or any(failures)):
                    raise ValueError("The flyer failed the clean-distance check")
        subprocess.run(
            [BIN / "flyer-ledger", path, "--period", "12", "--periods", "2"], check=True
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("geometry", type=Path)
    parser.add_argument("flyer", type=Path)
    parser.add_argument("--pl", type=int)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    assemble(args.geometry, args.flyer, args.pl)
    if args.check:
        check(args.flyer)
