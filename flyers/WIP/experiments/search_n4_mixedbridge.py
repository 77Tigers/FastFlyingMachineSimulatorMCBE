"""Bounded mixed-material bridge test for the PL21 N4 ring."""
from __future__ import annotations

import csv
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from fastflyer import Block, Flyer, Kind
from flyers.WIP.astra_ringgen_safe import make

OUT = Path(__file__).resolve().parent / "n4_mixedbridge"
RUNNER = Path(os.environ["TEMP"]) / "flyer_measure.exe"
PATHS = (
    ((-2, 1, 1), (-1, 1, 1), (0, 1, 1), (1, 1, 1), (2, 1, 1)),
    ((-2, 2, 0), (-1, 2, 0), (0, 2, 0), (1, 2, 0), (2, 2, 0)),
)


def score(candidate: Flyer, ticks: int, path: Path) -> int:
    candidate.save(path)
    proc = subprocess.run([str(RUNNER), str(ticks), str(path)], capture_output=True, text=True)
    fields = proc.stdout.strip().split("\t")
    return int(fields[1]) if proc.returncode == 0 and len(fields) > 1 else -1


def main() -> None:
    OUT.mkdir(exist_ok=True)
    base, counts, (segments, _) = make(4, [(0, 0), (0, 4), (3, 1)], 0, 21)
    rear = {(-2, -1, 0), (-2, 0, -1), (-2, 0, 0), (-2, 0, 1), (-2, 1, 0)}
    front = {(2, 2, 1), (2, 3, 0), (2, 3, 1), (2, 3, 2), (2, 4, 1)}
    old = segments[2] - rear - front
    assert counts == [16, 16, 17] and len(old) == 7
    rows = []
    for route, cells in enumerate(PATHS):
        for mask in (3, 4):
            segment_kinds = tuple(Kind.HONEY if mask & (1 << i) else Kind.SLIME for i in range(3))
            for bridge_bits in range(32):
                candidate = Flyer(base.phase_x, base.phase_z, base.rng_state, 21)
                candidate._cells = {p: b for p, b in base._cells.items() if p not in old}
                for i, segment in enumerate(segments):
                    for p in segment - old:
                        candidate.set(p, Block(segment_kinds[i]))
                for j, p in enumerate(cells):
                    kind = Kind.HONEY if bridge_bits & (1 << j) else Kind.SLIME
                    candidate.set(p, Block(kind))
                screen = OUT / "screen.flyer"
                d120 = score(candidate, 120, screen)
                d1000 = score(candidate, 1000, screen) if d120 >= 36 else -1
                d10000 = score(candidate, 10000, screen) if d1000 >= 300 else -1
                rows.append((route, mask, bridge_bits, d120, d1000, d10000))
                if d1000 >= 300:
                    candidate.save(OUT / f"r{route}_m{mask}_b{bridge_bits:02}.flyer")
                    print("SURVIVOR",rows[-1],flush=True)
    with (OUT / "summary.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("route", "segment_mask", "bridge_bits", "distance120", "distance1000", "distance10000"))
        writer.writerows(rows)
    print("DONE",len(rows),"max1000",max(x[4] for x in rows),"max10000",max(x[5] for x in rows),flush=True)


if __name__ == "__main__":
    main()
