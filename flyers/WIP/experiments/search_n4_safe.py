"""Bounded N4 ring search using the preserved generator and Rust simulator.

Run from the repository root. This is a research harness, not a physics model.
"""
from __future__ import annotations

import csv
import os
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from flyers.WIP.astra_ringgen_safe import make

OUT = Path(__file__).resolve().parent / "n4_safe"
RUNNER = Path(os.environ["TEMP"]) / "flyer_measure.exe"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    t0 = time.monotonic()
    rows = []
    generated = 0
    layouts = []
    for spacing in (4, 5, 3, 6):
        for cy in range(1, 5):
            for cz in range(1, spacing):
                layouts.append(((0, 0), (0, spacing), (cy, cz)))
    for centers in layouts:
        for seed in range(4):
            if generated >= 240 or time.monotonic() - t0 > 300:
                break
            ans = make(4, centers, seed, 22)
            if ans is None:
                continue
            flyer, counts, _ = ans
            generated += 1
            name = f"s{centers[1][1]}_y{centers[2][0]}z{centers[2][1]}_r{seed}"
            path = OUT / f"{name}.flyer"
            flyer.save(path)
            proc = subprocess.run(
                [str(RUNNER), "120", str(path)],
                capture_output=True, text=True, timeout=10,
            )
            fields = proc.stdout.strip().split("\t")
            distance = int(fields[1]) if proc.returncode == 0 and len(fields) >= 2 else -1
            rows.append((name, *counts, distance, proc.returncode))
            if distance < 36:
                path.unlink()
            if distance >= 36:
                print("PROMISING", name, counts, distance, flush=True)
        if generated >= 240 or time.monotonic() - t0 > 300:
            break
    with (OUT / "summary.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("name", "sticky0", "sticky1", "sticky2", "distance120", "returncode"))
        writer.writerows(rows)
    print("DONE", len(layouts), "layouts", generated, "generated", len(rows), "screened", round(time.monotonic()-t0, 1), "seconds", flush=True)


if __name__ == "__main__":
    main()
