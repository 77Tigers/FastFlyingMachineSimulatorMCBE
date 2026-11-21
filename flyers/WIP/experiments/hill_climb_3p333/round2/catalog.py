"""Scan all three-hopper templates with two ports beside the pulled pickup."""

import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent


def orbit(ports):
    def transform(p, s):
        x, y, z = p
        if s & 4:
            z = -z
        for _ in range(s % 4):
            y, z = -z, y
        return x, y, z

    return min(tuple(sorted(transform(p, s) for p in ports)) for s in range(8))


def run(pl, reach, offsets, shell):
    seen = set()
    jobs = []
    for edge, x, y, z in product([1, 0], [0, 1, -1, 2, -2], range(-2, 3), range(-2, 3)):
        if abs(y) + abs(z) > shell:
            continue
        ports = [(0, 1, 0), (0, 0, 1) if edge else (0, -1, 0), (x, y, z)]
        if len(set(ports)) != 3 or len({p[1:] for p in ports}) != 3:
            continue
        key = orbit(ports)
        if key in seen:
            continue
        seen.add(key)
        jobs.append(f"v{edge}_{x}_{y}_{z}")
    print(len(jobs), "template classes", flush=True)

    def test(shape):
        stem = f"catalog{pl}_{shape}_{offsets[0]}_{offsets[1]}"
        proc = subprocess.run(
            [
                HERE / "ring",
                "3",
                str(pl),
                *map(str, offsets),
                shape,
                str(reach),
                stem,
                "2",
                "beam",
            ],
            cwd=HERE,
            capture_output=True,
            text=True,
            check=True,
        )
        return shape + " " + proc.stderr.replace("\n", " | ")

    with ThreadPoolExecutor(max_workers=6) as pool:
        for result in pool.map(test, jobs):
            print(result, flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("pl", type=int)
    p.add_argument("offset", type=int, nargs=2)
    p.add_argument("--reach", type=int, default=4)
    p.add_argument("--shell", type=int, default=2)
    a = p.parse_args()
    run(a.pl, a.reach, a.offset, a.shell)
