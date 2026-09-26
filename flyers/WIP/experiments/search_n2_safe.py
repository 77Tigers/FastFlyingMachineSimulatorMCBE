"""Bounded two-push ring search at PL12, using the preserved safe generator."""
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

OUT = Path(__file__).resolve().parent / "n2_safe_search"
RUNNER = Path(os.environ["TEMP"]) / "flyer_measure.exe"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    rows = []
    start = time.monotonic()
    for y in range(0, 5):
        for z in range(0, 5):
            if y == z == 0:
                continue
            for seed in range(5):
                if time.monotonic() - start > 150:
                    break
                ans = make(2, [(0,0),(y,z)], seed, 12)
                if ans is None:
                    rows.append((y,z,seed,-1,-1,-1))
                    continue
                f, counts, _ = ans
                path = OUT / f"y{y}z{z}_s{seed}.flyer"
                f.save(path)
                proc = subprocess.run([str(RUNNER), "120", str(path)], capture_output=True, text=True)
                fields = proc.stdout.strip().split("\t")
                score = int(fields[1]) if proc.returncode == 0 and len(fields)>1 else -1
                rows.append((y,z,seed,*counts,score))
                if score < 26:
                    path.unlink()
                else:
                    print("PROMISING",y,z,seed,counts,score,flush=True)
            if time.monotonic() - start > 150:
                break
        if time.monotonic() - start > 150:
            break
    with (OUT / "summary.csv").open("w",newline="") as stream:
        writer=csv.writer(stream)
        writer.writerow(("center_y","center_z","geometry_seed","sticky0","sticky1","distance120"))
        writer.writerows(rows)
    print("DONE",len(rows),"attempts",round(time.monotonic()-start,1),"seconds",flush=True)


if __name__ == "__main__":
    main()
