"""Measure saved N4 candidates across a small phase/RNG sample in actual Rust."""
from __future__ import annotations

import csv
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer

OUT = Path(__file__).resolve().parent / "phase_sample"
RUNNER = Path(os.environ["TEMP"]) / "flyer_measure.exe"
SOURCES = {
    "pl22_cross": ROOT / "flyers/WIP/experiments/n4_safe/s4_y3z1_r0.flyer",
    "pl21_bridge": ROOT / "flyers/WIP/experiments/n4_bridge/candidate_0004_40.flyer",
}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    phases = (0, 7, 8, 15)
    seeds = (0, 1, 2, 5, 42)
    for label, source in SOURCES.items():
        rows = []
        for rng in seeds:
            for px in phases:
                for pz in phases:
                    candidate = Flyer.load(source)
                    candidate.rng_state = rng
                    candidate.phase_x = px
                    candidate.phase_z = pz
                    path = OUT / "screen.flyer"
                    candidate.save(path)
                    proc = subprocess.run([str(RUNNER), "10000", str(path)], capture_output=True, text=True)
                    fields = proc.stdout.strip().split("\t")
                    score = int(fields[1]) if proc.returncode == 0 and len(fields) > 1 else -1
                    rows.append((rng, px, pz, score))
                    if score == 3333:
                        candidate.save(OUT / f"{label}_rng{rng}_x{px}_z{pz}.flyer")
            print(label, "rng", rng, "completed", flush=True)
        with (OUT / f"{label}.csv").open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("rng", "phase_x", "phase_z", "distance10000"))
            writer.writerows(rows)
        print(label, "successes", sum(score == 3333 for *_, score in rows), "of", len(rows), "min", min(score for *_, score in rows), flush=True)


if __name__ == "__main__":
    main()
