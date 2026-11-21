#!/usr/bin/env python3
"""Independent verifier and scorer for the 3.333 bps PL hill climb.

Fixed before round 1:
- 80 canonical (rng, phase_x, phase_z) cases from tools/src/lib.rs.
- Deterministic random split (seed 42): 20 climbing cases, 60 held-out cases.
- Objective score: minimum verified push limit (PL) passing 80/80 at 10,000 ticks
  with distance >= 3333 (>= 3.333 bps), 0 extension failures, 0 movement failures,
  and 0 conservation mismatches.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

from fastflyer import Flyer

ROOT = Path(__file__).resolve().parents[4]
RESEARCH_BIN = ROOT / "target" / "release" / "fastflyer-research"
BODYTRACK_BIN = ROOT / "target" / "release" / "bodytrack"
BANK_STATS_BIN = ROOT / "target" / "release" / "fastsim-bank-stats"

SAMPLE_RNGS = [0, 1, 2, 5, 42]
SAMPLE_PHASES = [0, 7, 8, 15]
ALL_CASES = [
    (rng, px, pz)
    for rng in SAMPLE_RNGS
    for px in SAMPLE_PHASES
    for pz in SAMPLE_PHASES
]

_rng = random.Random(42)
_shuffled = list(ALL_CASES)
_rng.shuffle(_shuffled)
CLIMBING_CASES = set(_shuffled[:20])
HELDOUT_CASES = set(_shuffled[20:])


def inspect_flyer(path: Path) -> dict:
    f = Flyer.load(str(path))
    bs = dict(f.blocks())
    if not bs:
        return {"push_limit": f.push_limit, "blocks": 0, "dims": [0, 0, 0]}
    xs = [c[0] for c in bs]
    ys = [c[1] for c in bs]
    zs = [c[2] for c in bs]
    dims = [max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, max(zs) - min(zs) + 1]
    return {
        "push_limit": f.push_limit,
        "blocks": len(bs),
        "dims": dims,
    }


def write_with_pl(src: Path, pl: int, dst: Path) -> None:
    f = Flyer.load(str(src))
    f.push_limit = pl
    f.save(str(dst))


def run_samples(flyer_path: Path, distance: int, ticks: int, jobs: int, csv_path: Path) -> dict:
    cmd = [
        str(RESEARCH_BIN),
        "samples",
        str(flyer_path),
        "--distance",
        str(distance),
        "--ticks",
        str(ticks),
        "--jobs",
        str(jobs),
        "--out",
        str(csv_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if not csv_path.exists():
        raise RuntimeError(f"samples produced no CSV ({proc.returncode}): {proc.stderr or proc.stdout}")

    rows = {}
    with csv_path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            key = (int(row["rng"]), int(row["phase_x"]), int(row["phase_z"]))
            rows[key] = row

    missing = set(ALL_CASES) - set(rows.keys())
    if missing:
        raise RuntimeError(f"CSV missing {len(missing)} canonical cases")

    def row_ok(r: dict) -> bool:
        return (
            r.get("pass", "").lower() in ("true", "1", "yes")
            and int(r["distance"]) >= distance
            and int(r.get("extension_failures", "0")) == 0
            and int(r.get("conservation_mismatch_ticks", "0")) == 0
        )

    climb_pass = sum(1 for k in CLIMBING_CASES if row_ok(rows[k]))
    held_pass = sum(1 for k in HELDOUT_CASES if row_ok(rows[k]))
    total_pass = climb_pass + held_pass
    distances = [int(rows[k]["distance"]) for k in ALL_CASES]
    climb_failures = [
        {
            "rng": k[0],
            "phase_x": k[1],
            "phase_z": k[2],
            "distance": int(rows[k]["distance"]),
            "ext_fail": int(rows[k].get("extension_failures", "0")),
            "cons_err": int(rows[k].get("conservation_mismatch_ticks", "0")),
        }
        for k in sorted(CLIMBING_CASES)
        if not row_ok(rows[k])
    ]
    return {
        "climbing_pass": climb_pass,
        "climbing_total": len(CLIMBING_CASES),
        "heldout_pass": held_pass,
        "heldout_total": len(HELDOUT_CASES),
        "total_pass": total_pass,
        "min_distance": min(distances),
        "max_distance": max(distances),
        "min_bps": round(min(distances) * 10.0 / ticks, 4),
        "climbing_failures": climb_failures[:5],
    }


def run_audit(flyer_path: Path, ticks: int = 240) -> dict:
    cmd = [str(RESEARCH_BIN), "audit", str(flyer_path), str(ticks), "0"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return {"error": proc.stderr or proc.stdout}
    out = {}
    for token in proc.stdout.strip().split():
        if "=" in token:
            k, v = token.split("=", 1)
            out[k] = v
    return out


def run_bodytrack(flyer_path: Path) -> str:
    if not BODYTRACK_BIN.exists():
        return ""
    proc = subprocess.run(
        [str(BODYTRACK_BIN), str(flyer_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    return (proc.stdout or "").strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("flyer", type=Path)
    ap.add_argument("--pl", type=int, default=None, help="Override PL to test (defaults to flyer's encoded PL)")
    ap.add_argument("--distance", type=int, default=3333)
    ap.add_argument("--ticks", type=int, default=10000)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--check-minus-one", action="store_true", help="Also verify PL-1 fails")
    ap.add_argument("--csv-out", type=Path, default=None)
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--bodytrack", action="store_true")
    args = ap.parse_args()

    meta = inspect_flyer(args.flyer)
    test_pl = args.pl if args.pl is not None else meta["push_limit"]

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        target_flyer = args.flyer
        if args.pl is not None and args.pl != meta["push_limit"]:
            target_flyer = td_path / f"pl{test_pl}.flyer"
            write_with_pl(args.flyer, test_pl, target_flyer)

        csv_path = args.csv_out or (td_path / "samples.csv")
        sample_res = run_samples(target_flyer, args.distance, args.ticks, args.jobs, csv_path)
        audit_res = run_audit(target_flyer, ticks=240)

        minus_one = None
        if args.check_minus_one and test_pl > 1:
            m1_flyer = td_path / f"pl{test_pl - 1}.flyer"
            write_with_pl(args.flyer, test_pl - 1, m1_flyer)
            minus_one = run_samples(
                m1_flyer,
                args.distance,
                args.ticks,
                args.jobs,
                td_path / "samples_m1.csv",
            )

    result = {
        "file": str(args.flyer),
        "tested_pl": test_pl,
        "encoded_pl": meta["push_limit"],
        "blocks": meta["blocks"],
        "dims": meta["dims"],
        "samples": sample_res,
        "audit_240": {
            "max_successful_action": audit_res.get("max_successful_action"),
            "movement_failures": audit_res.get("movement_failures"),
            "extension_failures": audit_res.get("extension_failures"),
            "distance_240": audit_res.get("distance"),
        },
        "minus_one": (
            {
                "pl": test_pl - 1,
                "ticks": args.ticks,
                "total_pass": minus_one["total_pass"],
                "min_distance": minus_one["min_distance"],
            }
            if minus_one
            else None
        ),
    }
    if args.bodytrack:
        result["bodytrack"] = run_bodytrack(args.flyer)

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, indent=2) + "\n")

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
