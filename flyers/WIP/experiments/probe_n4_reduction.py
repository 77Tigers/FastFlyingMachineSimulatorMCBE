"""Test one-cell deletions of the PL22 N4 ring's overloaded segment."""
from __future__ import annotations

import csv
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from flyers.WIP.astra_ringgen_safe import make

OUT = Path(__file__).resolve().parent / "n4_reduction"
RUNNER = Path(os.environ["TEMP"]) / "flyer_measure.exe"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    rows = []
    centers = [(0, 0), (0, 4), (3, 1)]
    ref, counts, (segments, _) = make(4, centers, 0, 21)
    assert counts == [16, 16, 17]
    for index, cell in enumerate(sorted(segments[2])):
        candidate, _, _ = make(4, centers, 0, 21)
        candidate.remove(cell)
        path = OUT / f"delete_{index:02}.flyer"
        candidate.save(path)
        proc = subprocess.run([str(RUNNER), "120", str(path)], capture_output=True, text=True)
        fields = proc.stdout.strip().split("\t")
        distance = int(fields[1]) if proc.returncode == 0 and len(fields) > 1 else -1
        rows.append((index, *cell, distance))
        if distance < 36:
            path.unlink()
    with (OUT / "summary.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("index", "x", "y", "z", "distance120"))
        writer.writerows(rows)
    print(*rows, sep="\n")


if __name__ == "__main__":
    main()
