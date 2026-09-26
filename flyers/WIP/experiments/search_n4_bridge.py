"""Replace segment 2's long connector with short monotone paths and screen in Rust."""
from __future__ import annotations

import csv
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from fastflyer import Block, Flyer, Kind
from flyers.WIP.astra_ringgen_safe import make

OUT = Path(__file__).resolve().parent / "n4_bridge"
RUNNER = Path(os.environ["TEMP"]) / "flyer_measure.exe"
DIRS = ((1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def add(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def dist(a, b):
    return sum(abs(a[i] - b[i]) for i in range(3))


def main() -> None:
    OUT.mkdir(exist_ok=True)
    base, counts, (segments, _) = make(4, [(0, 0), (0, 4), (3, 1)], 0, 21)
    assert counts == [16, 16, 17]
    rear = {(-2, -1, 0), (-2, 0, -1), (-2, 0, 0), (-2, 0, 1), (-2, 1, 0)}
    front = {(2, 2, 1), (2, 3, 0), (2, 3, 1), (2, 3, 2), (2, 4, 1)}
    assert len(rear) == len(front) == 5
    connector = segments[2] - rear - front
    occupied = set(base._cells) - connector
    print("baseline connector", sorted(connector), flush=True)
    print("minimum terminal distance", min(dist(a, b) for a in rear for b in front), flush=True)
    visited = set()
    rows = []
    t0 = time.monotonic()

    def evaluate(path):
        cells = frozenset(path[1:-1])
        if len(cells) > 6 or cells in visited:
            return
        visited.add(cells)
        if any(p in occupied for p in cells):
            return
        for mask in range(8):
            kinds = tuple(Kind.HONEY if mask & (1 << i) else Kind.SLIME for i in range(3))
            candidate = Flyer(base.phase_x, base.phase_z, base.rng_state, 21)
            candidate._cells = {p: b for p, b in base._cells.items() if p not in connector}
            for i, segment in enumerate(segments):
                for p in segment - connector:
                    candidate.set(p, Block(kinds[i]))
            for p in cells:
                candidate.set(p, Block(kinds[2]))
            pathfile = OUT / "screen.flyer"
            candidate.save(pathfile)
            proc = subprocess.run([str(RUNNER), "120", str(pathfile)], capture_output=True, text=True)
            fields = proc.stdout.strip().split("\t")
            score = int(fields[1]) if proc.returncode == 0 and len(fields) > 1 else -1
            rows.append((len(cells), mask, score, " ".join(str(p) for p in sorted(cells))))
            if score >= 36:
                final = OUT / f"candidate_{len(rows):04}_{score}.flyer"
                candidate.save(final)
                print("PROMISING", len(rows), len(cells), mask, score, sorted(cells), flush=True)

    def walk(path, end, length):
        if len(path) - 1 == length:
            if path[-1] == end:
                evaluate(path)
            return
        if dist(path[-1], end) > length - (len(path) - 1):
            return
        for d in DIRS:
            q = add(path[-1], d)
            if q in path or q[0] < -2 or q[0] > 2:
                continue
            if q in occupied and q != end:
                continue
            walk(path + [q], end, length)

    for length in (6, 8):
        for a in sorted(rear):
            for b in sorted(front):
                if dist(a, b) <= length:
                    walk([a], b, length)
                if time.monotonic() - t0 > 180 or len(rows) > 3000:
                    break
            if time.monotonic() - t0 > 180 or len(rows) > 3000:
                break
        if time.monotonic() - t0 > 180 or len(rows) > 3000:
            break
    with (OUT / "summary.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("connector_count", "material_mask", "distance120", "cells"))
        writer.writerows(rows)
    print("DONE", len(rows), "screened", len(visited), "unique paths", round(time.monotonic()-t0,1), "seconds", flush=True)


if __name__ == "__main__":
    main()
