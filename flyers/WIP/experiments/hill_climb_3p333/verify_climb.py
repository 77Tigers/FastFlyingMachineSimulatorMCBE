#!/usr/bin/env python3
"""Strict promotion gate for the 3.333 bps PL hill climb.

Fixed before round 1:
- 80 canonical (rng, phase_x, phase_z) cases from tools/src/lib.rs.
- Deterministic random split (seed 42): 20 climbing cases, 60 held-out cases.
- Objective score: minimum verified push limit (PL) passing 80/80 at 10,000 ticks
  with distance >= 3333 (>= 3.333 bps), 0 extension failures, 0 movement failures,
  and 0 conservation mismatches.

The speed/conservation gate decides `verdict` and the exit code (1 on FAIL).
`--check-exact` runs exact-state recurrence as a separate report that never
changes the verdict.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
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
UPDATE_BANK = ROOT / "scripts" / "update_bank.py"
CATALOGUE = ROOT / "flyers" / "bank" / "catalogue.json"

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

AUDIT_TICKS = 240


class VerificationError(RuntimeError):
    """A tool could not produce a usable result (as opposed to a failed flight)."""


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head() -> str | None:
    proc = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    return proc.stdout.strip() or None


def engine_sha256() -> dict:
    """Live engine fingerprint (same recipe as scripts/update_bank.py) plus the catalogue's value."""
    live = None
    if UPDATE_BANK.exists():
        spec = importlib.util.spec_from_file_location("update_bank", UPDATE_BANK)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        live = module.engine_fingerprint(ROOT)

    catalogue = None
    if CATALOGUE.exists():
        catalogue = json.loads(CATALOGUE.read_text()).get("engine_sha256")

    return {"live": live, "catalogue": catalogue, "matches_catalogue": live is not None and live == catalogue}


# ---------------------------------------------------------------------------
# Flyer helpers
# ---------------------------------------------------------------------------

def inspect_flyer(path: Path) -> dict:
    f = Flyer.load(str(path))
    bs = dict(f.blocks())
    if not bs:
        return {"push_limit": f.push_limit, "blocks": 0, "dims": [0, 0, 0]}
    dims = [max(c[axis] for c in bs) - min(c[axis] for c in bs) + 1 for axis in range(3)]
    return {"push_limit": f.push_limit, "blocks": len(bs), "dims": dims}


def write_with_pl(src: Path, pl: int, dst: Path) -> None:
    f = Flyer.load(str(src))
    f.push_limit = pl
    f.save(str(dst))


# ---------------------------------------------------------------------------
# Tool runners
# ---------------------------------------------------------------------------

def read_sample_rows(cmd: list[str], csv_path: Path) -> dict:
    """Run `fastflyer-research samples`. It exits 1 when cases fail, so only a missing CSV is an error."""
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if not csv_path.exists():
        raise VerificationError(f"samples produced no CSV (exit {proc.returncode}): {proc.stderr or proc.stdout}")

    with csv_path.open(newline="") as fh:
        rows = {(int(r["rng"]), int(r["phase_x"]), int(r["phase_z"])): r for r in csv.DictReader(fh)}

    missing = set(ALL_CASES) - set(rows)
    if missing:
        raise VerificationError(f"samples CSV missing {len(missing)} canonical cases")
    return rows


def run_samples(flyer_path: Path, distance: int, ticks: int, jobs: int, csv_path: Path) -> dict:
    cmd = [
        str(RESEARCH_BIN), "samples", str(flyer_path),
        "--distance", str(distance),
        "--ticks", str(ticks),
        "--jobs", str(jobs),
        "--out", str(csv_path),
    ]
    rows = read_sample_rows(cmd, csv_path)

    def row_ok(r: dict) -> bool:
        return (
            r.get("pass", "").lower() in ("true", "1", "yes")
            and int(r["distance"]) >= distance
            and int(r.get("extension_failures", "0")) == 0
            and int(r.get("movement_failures", "0")) == 0
            and int(r.get("conservation_mismatch_ticks", "0")) == 0
        )

    climb_pass = sum(1 for k in CLIMBING_CASES if row_ok(rows[k]))
    held_pass = sum(1 for k in HELDOUT_CASES if row_ok(rows[k]))
    distances = [int(rows[k]["distance"]) for k in ALL_CASES]
    climb_failures = [
        {
            "rng": k[0],
            "phase_x": k[1],
            "phase_z": k[2],
            "distance": int(rows[k]["distance"]),
            "ext_fail": int(rows[k].get("extension_failures", "0")),
            "move_fail": int(rows[k].get("movement_failures", "0")),
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
        "total_pass": climb_pass + held_pass,
        "min_distance": min(distances),
        "max_distance": max(distances),
        "min_bps": round(min(distances) * 10.0 / ticks, 4),
        "climbing_failures": climb_failures[:5],
    }


def run_exact_samples(flyer_path: Path, period: int, advance: int, ticks: int, jobs: int, csv_path: Path) -> dict:
    cmd = [
        str(RESEARCH_BIN), "samples", str(flyer_path),
        "--period", str(period),
        "--advance", str(advance),
        "--exact",
        "--ticks", str(ticks),
        "--jobs", str(jobs),
        "--out", str(csv_path),
    ]
    rows = read_sample_rows(cmd, csv_path)
    passed = sum(1 for r in rows.values() if r.get("pass", "").lower() in ("true", "1", "yes"))
    return {
        "period": period,
        "advance": advance,
        "ticks": ticks,
        "total_pass": passed,
        "total": len(ALL_CASES),
        "verdict": "PASS" if passed == len(ALL_CASES) else "FAIL",
    }


def run_audit(flyer_path: Path, ticks: int = AUDIT_TICKS) -> dict:
    """`fastflyer-research audit` prints `key=value` tokens; integer fields are converted."""
    cmd = [str(RESEARCH_BIN), "audit", str(flyer_path), str(ticks), "0"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise VerificationError(f"audit failed (exit {proc.returncode}): {proc.stderr or proc.stdout}")

    tokens = dict(t.split("=", 1) for t in proc.stdout.split() if "=" in t)
    fields = ["limit", "distance", "extensions", "extension_failures", "movement_failures",
              "max_successful_action", "conservation_mismatch_ticks"]
    missing = [f for f in fields if f not in tokens]
    if missing:
        raise VerificationError(f"audit output missing {missing}")
    return {f: int(tokens[f]) for f in fields}


def run_bank_stats(flyer_path: Path, ticks: int) -> dict:
    """`fastsim-bank-stats TICKS FILE` prints `index distance extensions failures conserved`."""
    proc = subprocess.run(
        [str(BANK_STATS_BIN), str(ticks), str(flyer_path)], capture_output=True, text=True, check=False
    )
    lines = proc.stdout.strip().splitlines()
    if proc.returncode != 0 or len(lines) != 1:
        raise VerificationError(f"fastsim-bank-stats failed (exit {proc.returncode}): {proc.stderr or proc.stdout}")

    _, distance, extensions, failures, conserved = lines[0].split("\t")
    return {
        "ticks": ticks,
        "distance": int(distance),
        "extensions": int(extensions),
        "extension_failures": int(failures),
        "endpoint_conserved": conserved == "true",
    }


def run_bodytrack(flyer_path: Path) -> str:
    if not BODYTRACK_BIN.exists():
        return ""
    proc = subprocess.run([str(BODYTRACK_BIN), str(flyer_path)], capture_output=True, text=True, check=False)
    return (proc.stdout or "").strip()


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------

def sample_failures(samples: dict) -> list[str]:
    reasons = []
    if samples["climbing_pass"] < samples["climbing_total"]:
        reasons.append(f"climbing {samples['climbing_pass']}/{samples['climbing_total']}")
    if samples["heldout_pass"] < samples["heldout_total"]:
        reasons.append(f"heldout {samples['heldout_pass']}/{samples['heldout_total']}")
    if samples["total_pass"] < len(ALL_CASES):
        reasons.append(f"total {samples['total_pass']}/{len(ALL_CASES)}")
    return reasons


def audit_failures(audit: dict, test_pl: int) -> list[str]:
    reasons = []
    if audit["movement_failures"] > 0:
        reasons.append(f"audit_240 movement_failures={audit['movement_failures']}")
    if audit["extension_failures"] > 0:
        reasons.append(f"audit_240 extension_failures={audit['extension_failures']}")
    if audit["max_successful_action"] > test_pl:
        reasons.append(f"audit_240 max_successful_action={audit['max_successful_action']} > PL {test_pl}")
    return reasons


def bank_stats_failures(stats: dict, distance: int) -> list[str]:
    reasons = []
    if stats["extension_failures"] > 0:
        reasons.append(f"bank_stats extension_failures={stats['extension_failures']}")
    if not stats["endpoint_conserved"]:
        reasons.append("bank_stats endpoint_conserved=false")
    if stats["distance"] < distance:
        reasons.append(f"bank_stats distance={stats['distance']} < {distance}")
    return reasons


def guarded(reasons: list[str], label: str, fn, *args):
    """Run one tool; record a tool error as a failure reason and return None."""
    try:
        return fn(*args)
    except (VerificationError, OSError, ValueError) as exc:
        reasons.append(f"{label} error: {exc}")
        return None


def verify(args: argparse.Namespace, td: Path) -> dict:
    meta = inspect_flyer(args.flyer)
    test_pl = args.pl if args.pl is not None else meta["push_limit"]

    target_flyer = args.flyer
    if test_pl != meta["push_limit"]:
        target_flyer = td / f"pl{test_pl}.flyer"
        write_with_pl(args.flyer, test_pl, target_flyer)

    reasons: list[str] = []

    csv_path = args.csv_out or (td / "samples.csv")
    samples = guarded(reasons, "samples", run_samples, target_flyer, args.distance, args.ticks, args.jobs, csv_path)
    if samples:
        reasons += sample_failures(samples)

    audit = guarded(reasons, "audit_240", run_audit, target_flyer, AUDIT_TICKS)
    if audit:
        reasons += audit_failures(audit, test_pl)

    bank_stats = guarded(reasons, "bank_stats", run_bank_stats, target_flyer, args.ticks)
    if bank_stats:
        reasons += bank_stats_failures(bank_stats, args.distance)

    minus_one = None
    if args.check_minus_one:
        minus_one = {"pl": test_pl - 1, "ticks": args.ticks, "distance_threshold": args.distance}
        if test_pl <= 1:
            reasons.append("minus_one: PL - 1 is below 1")
        else:
            m1_flyer = td / f"pl{test_pl - 1}.flyer"
            write_with_pl(args.flyer, test_pl - 1, m1_flyer)
            m1 = guarded(reasons, "minus_one", run_samples,
                         m1_flyer, args.distance, args.ticks, args.jobs, td / "samples_m1.csv")
            if m1:
                minus_one.update(total_pass=m1["total_pass"], min_distance=m1["min_distance"])
                if m1["total_pass"] > 0:
                    reasons.append(f"minus_one PL {test_pl - 1} passes {m1['total_pass']}/{len(ALL_CASES)}")

    exact = None
    if args.check_exact:
        exact = guarded([], "exact", run_exact_samples,
                        target_flyer, args.period, args.advance, args.ticks, args.jobs, td / "samples_exact.csv")

    verdict = "FAIL" if reasons else "PASS"
    result = {
        "file": str(args.flyer),
        "verdict": verdict,
        "failure_reasons": reasons,
        "evidence_level": "autonomous_flight" if verdict == "PASS" else "failed_flight",
        "flyer_sha256": sha256_file(args.flyer),
        "git_head": git_head(),
        "engine_sha256": engine_sha256(),
        "ticks": args.ticks,
        "distance_threshold": args.distance,
        "tested_pl": test_pl,
        "encoded_pl": meta["push_limit"],
        "blocks": meta["blocks"],
        "dims": meta["dims"],
        "samples": samples,
        "audit_240": audit,
        "bank_stats": bank_stats,
        "minus_one": minus_one,
    }
    if args.check_exact:
        result["exact_recurrence"] = exact
    if args.bodytrack:
        result["bodytrack"] = run_bodytrack(args.flyer)
    return result


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("flyer", type=Path)
    ap.add_argument("--pl", type=int, default=None, help="Override PL to test (defaults to flyer's encoded PL)")
    ap.add_argument("--distance", type=int, default=3333)
    ap.add_argument("--ticks", type=int, default=10000)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--check-minus-one", action="store_true", help="Also require PL-1 to pass 0/80")
    ap.add_argument("--check-exact", action="store_true",
                    help="Report exact-state recurrence separately (needs --period and --advance; never gates)")
    ap.add_argument("--period", type=int, default=None)
    ap.add_argument("--advance", type=int, default=None)
    ap.add_argument("--csv-out", type=Path, default=None)
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--bodytrack", action="store_true")
    ap.add_argument("--no-fail-exit", action="store_true", help="Exit 0 on FAIL (inspection only)")
    args = ap.parse_args()
    if args.check_exact and (args.period is None or args.advance is None):
        ap.error("--check-exact needs --period and --advance")
    return args


def main() -> int:
    args = parse_args()
    with tempfile.TemporaryDirectory() as td:
        result = verify(args, Path(td))

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, indent=2) + "\n")

    print(json.dumps(result, indent=2))
    if result["verdict"] == "PASS" or args.no_fail_exit:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
