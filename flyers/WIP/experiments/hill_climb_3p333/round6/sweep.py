"""Repeat one bounded Round 6 search and aggregate its placement counters."""

import argparse
import itertools
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
OFFSETS = [(0, -3), (1, -3), (-1, -2)]
JOINT = [
    (0, -3, 9, 0), (0, -3, 9, 1), (0, -3, 2, 0), (0, -3, 2, 1),
    (-1, -2, 1, 1), (-1, -2, 2, 0), (1, -3, 9, 1), (1, -3, 2, 0),
]
CROSSED = [
    (0, -3, 2, 0), (-1, -2, 2, 0), (-1, -3, 4, 1), (0, -3, 9, 1),
    (-1, -2, 1, 1), (1, -3, 2, 0), (0, -2, 0, 0),
]


def cases(group):
    if group == "back":
        for (t0, t1), extra, observer in itertools.product(OFFSETS, range(6), range(3)):
            yield "back", t0, t1, extra, observer, 11, 80, "@"
    elif group == "joint":
        for pose in JOINT:
            yield "flex", *pose, -1, 0, 10, 11, 16, "@", "joint"
    elif group == "crossed":
        for pose, cover in itertools.product(CROSSED, (0, 1)):
            yield "flex", *pose, -1, cover, 10, 11, 20, "@", "swap"
    elif group == "rear":
        for sticky, shard in itertools.product(range(6), range(4)):
            yield "backup", 0, 6, sticky, shard, 32, "@"
    elif group == "plate":
        for plane, lane in itertools.product((2, 1, 3), range(6)):
            yield "three", plane, lane, -1, -1, 5, 24, "@"
    elif group == "rigid":
        for material, top in itertools.product(range(3), repeat=2):
            yield "rigid", 14, material, top, -1, "@"
    elif group == "half":
        for material, pickups, top in itertools.product(range(4), range(4), range(3)):
            yield "half", 14, material, pickups, top, "@"
    elif group == "split":
        for material, top, bottom, symmetry in itertools.product(
            range(4), range(1, 7), (0, 1), (2, 4, 5, 6, 7)
        ):
            yield "half", 14, material, 0, 0, "@", top, bottom, symmetry


def run(group, jobs):
    with tempfile.TemporaryDirectory(dir=HERE) as tmp:
        def search(item):
            i, (exe, *args) = item
            output = Path(tmp) / f"{i}.geometry"
            cmd = [HERE / exe, *(str(output if x == "@" else x) for x in args)]
            result = subprocess.run(cmd, text=True, capture_output=True, check=True)
            line = result.stdout.strip().splitlines()[-1]
            if output.exists() and output.stat().st_size:
                found = HERE / f"candidate_{group}_{i}.geometry"
                found.write_bytes(output.read_bytes())
                print(f"Geometry saved to {found.name}", flush=True)
            return line

        with ThreadPoolExecutor(max_workers=jobs) as pool:
            results = list(pool.map(search, enumerate(cases(group))))
    # Report the counters in the same order as the native program.
    counts = [list(map(int, re.findall(r"\b\d+\b", row))) for row in results]
    totals = iter(sum(column) for column in zip(*counts, strict=True))
    line = re.sub(r"\b\d+\b", lambda _: str(next(totals)), results[0])
    print(f"{group} ({len(results)} searches) {line}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("groups", metavar="group", nargs="+", choices=(
        "back", "joint", "crossed", "rear", "plate", "rigid", "half", "split"
    ))
    parser.add_argument("--jobs", type=int, default=6)
    args = parser.parse_args()
    for group in args.groups:
        run(group, args.jobs)
