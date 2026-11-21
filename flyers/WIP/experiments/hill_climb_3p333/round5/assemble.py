"""Export a back ring and its four towers in canonical slot zero."""

import argparse
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "nk_constructor_20261022"))
from fastflyer import Block, Flyer, Kind
from nk import Timing


def assemble(geometry, output, limit=None, start=0):
    header, *rows = geometry.read_text().splitlines()
    bodies, pl = map(int, header.split())
    flyer = Flyer(push_limit=limit or pl)
    parts = defaultdict(list)
    hosts = {}
    for row in rows:
        body, kind, *values = row.split()
        values = tuple(map(int, values))
        if kind == "body":
            hosts[int(body)] = values
        else:
            parts[int(body), kind].append(values)
    occupied = set()

    def put(pos, block):
        if pos in occupied:
            raise ValueError(f"overlap at {pos}")
        occupied.add(pos)
        flyer.set(pos, block)

    timing = Timing(4)
    for body in range(bodies):
        _, _, rest, honey = hosts[body]
        slot = (start - rest) % 6
        shift = sum((s - rest) % 6 >= 2 for s in range(start))
        for pos in parts[body, "G"] + parts[body, "C"]:
            put((pos[0] + shift, *pos[1:]), Block(Kind.HONEY if honey else Kind.SLIME))
        for pos in parts[body, "R"]:
            put((pos[0] + shift, *pos[1:]), Block(Kind.REDSTONE_BLOCK))
        for x, y, z in parts[body, "O"]:
            (center,) = parts[body, "C"]
            delta = tuple(c - o for c, o in zip(center, (x, y, z)))
            direction = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)].index(delta)
            put((x + shift, y, z), Block.observer(direction, powered=slot in (0, 3, 4, 5)))
        for x, y, z in parts[body, "P"]:
            put((x + shift, y, z), Block.piston(0, state=2 if slot == 1 else 0))
            if slot == 1:
                put((x + shift + 1, y, z), Block(Kind.PISTON_ARM))
        for x, y, z in parts[body, "S"]:
            put(
                (x + shift, y, z),
                Block.piston(1, sticky=True, state=2 if slot == 1 else 0),
            )
            if slot == 1:
                put((x + shift - 1, y, z), Block(Kind.PISTON_ARM))
        hoppers = sorted(parts[body, "H"] + parts[body, "L"])
        for firing, (x, y, z) in enumerate(hoppers, 3 if parts[body, "O"] else 2):
            dx, state = timing.pusher_canon(firing, slot)
            put((x + shift + dx, y, z), Block.piston(0, state=state))
            if state == 2:
                put((x + shift + dx + 1, y, z), Block(Kind.PISTON_ARM))
    flyer.save(str(output))
    low, high = flyer.bounds()
    dims = tuple(b - a + 1 for a, b in zip(low, high))
    print(
        output.name,
        flyer.push_limit,
        len(occupied),
        dims,
        hashlib.sha256(output.read_bytes()).hexdigest(),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("geometry", type=Path)
    parser.add_argument("flyer", type=Path)
    parser.add_argument("--pl", type=int)
    parser.add_argument("--slot", type=int, choices=range(6), default=0)
    args = parser.parse_args()
    assemble(args.geometry, args.flyer, args.pl, args.slot)
