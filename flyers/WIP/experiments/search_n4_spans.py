"""Bounded search over axial span allocations of three-segment N4 rings."""
from __future__ import annotations

import csv
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from flyers.WIP.experiments.astra_ringgen_spans import make

OUT = Path(__file__).resolve().parent / "n4_spans"
RUNNER = Path(os.environ["TEMP"]) / "flyer_measure.exe"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    centers_list = (
        [(0, 0), (0, 4), (3, 1)],
        [(0, 0), (0, 4), (3, 3)],
        [(0, 0), (0, 4), (2, 2)],
    )
    allocations = sorted(
        ((a, b, 10-a-b) for a in range(2, 6) for b in range(2, 6)
         if 2 <= 10-a-b <= 5),
        key=lambda span: (max(span)-min(span), sum(abs(x-y) for x,y in zip(span,(3,3,4)))),
    )
    rows = []
    started = time.monotonic()
    generated = 0
    for ci, centers in enumerate(centers_list):
        for spans in allocations:
            for seed in range(3):
                if time.monotonic() - started > 300:
                    break
                ans = make(4, centers, seed, 20, spans)
                if ans is None:
                    rows.append((ci, *spans, seed, -1, -1, -1, -1))
                    continue
                f, counts, _ = ans
                generated += 1
                label = f"c{ci}_s{''.join(str(x) for x in spans)}_r{seed}"
                path = OUT / f"{label}.flyer"
                f.save(path)
                proc = subprocess.run([str(RUNNER), "120", str(path)], capture_output=True, text=True)
                fields = proc.stdout.strip().split("\t")
                score = int(fields[1]) if proc.returncode == 0 and len(fields) > 1 else -1
                rows.append((ci, *spans, seed, *counts, score))
                if score < 36:
                    path.unlink()
                else:
                    print("PROMISING",label,counts,score,flush=True)
            if time.monotonic() - started > 300:
                break
        print("CENTER_DONE",ci,"elapsed",round(time.monotonic()-started,1),flush=True)
        if time.monotonic() - started > 300:
            break
    with (OUT / "summary.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("centers", "span0", "span1", "span2", "seed", "sticky0", "sticky1", "sticky2", "distance120"))
        writer.writerows(rows)
    print("DONE",len(rows),"attempts",generated,"generated",round(time.monotonic()-started,1),"seconds",flush=True)


if __name__ == "__main__":
    main()
