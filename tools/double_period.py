"""Period doubling for a natural or prescribed contract: words repeat twice, period and advance double.

Hopping hardware (a piston that moves the target in even periods while its partner does it in odd periods)
recurs only every two glue periods; in the doubled contract every move instance has a single actor again,
so per-move decomposition and single-actor generators apply.

usage: python tools/double_period.py PROBLEM.json OUT_DIR [--factor 2]
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("problem", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--factor", type=int, default=2)
    a = ap.parse_args()
    c = json.loads(a.problem.read_text())
    n = a.factor
    p = c["period_ticks"]
    a.out.mkdir(parents=True, exist_ok=True)
    shutil.copy(a.problem.parent / c["flyer"], a.out / c["flyer"])
    for port in c["ports"]:
        port["word"] = port["word"] * n
        for key in ("baseline_load", "spare_load", "caps"):
            if key in port and isinstance(port[key], list):
                port[key] = port[key] * n
    if c.get("prescribed_script"):
        # the script already lists `cycles` periods of strokes; the doubled contract needs the same ticks
        shutil.copy(a.problem.parent / c["prescribed_script"], a.out / c["prescribed_script"])
    c["period_ticks"] = p * n
    c["advance"] = c["advance"] * n
    c["cycles"] = max(2, -(-c.get("cycles", 3) // n))
    c["name"] = c.get("name", "problem") + f"-x{n}"
    (a.out / "problem.json").write_text(json.dumps(c, indent=1) + "\n")
    print(a.out / "problem.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
