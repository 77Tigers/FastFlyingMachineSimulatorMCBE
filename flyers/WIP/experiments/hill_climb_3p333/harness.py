#!/usr/bin/env python3
"""Round 7 harness for the 3.333 bps PL hill climb.

    harness.py preflight                 check toolchain, binaries and scratch access
    harness.py replay                    re-fly every headline verified flyer for 240 ticks
    harness.py manifest init ...         write a search manifest skeleton
    harness.py manifest validate FILE..  check search manifests

Every subcommand exits 1 when something is broken.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"
RELEASE = ROOT / "target" / "release"
REQUIRED_BINARIES = ["fastflyer-research", "fastsim-bank-stats", "flyer-ledger"]
# The round build.sh scripts compile C++ in this image when the host has no g++.
GXX_DOCKER_IMAGE = "golang:1.26-bookworm"
CARGO_RUSTC = Path.home() / ".cargo" / "bin" / "rustc"

# Headline verified flyers: path relative to ROOT, pinned SHA-256, encoded PL.
HEADLINE_FLYERS = [
    ("flyers/bank/pl18/nk_lat_n4.flyer",
     "939a1091240e457e7324b034c541f4876c26c82496d963bf6d187b3d0345e34d", 18),
    ("flyers/WIP/experiments/hill_climb_3p333/round1/screw6_pl18.flyer",
     "5dc00035c1d330c8a7e18af5b7cb5b2f523cce3e0b48a821d8a4dfc5993b88f8", 18),
    ("flyers/WIP/experiments/hill_climb_3p333/round2/openplus6_pl18.flyer",
     "feafee9e36d0baad450b8282de5834c3f7d24932220abb8e0830af6840bea597", 18),
    ("flyers/WIP/experiments/hill_climb_3p333/round2/openplus3_pl19.flyer",
     "79225f2be9f9ff12a061a56f7d5dd3c1690eb3b28871a3bf466dbc43c05a69c3", 19),
    ("flyers/WIP/experiments/hill_climb_3p333/round3/mixed_screw_pl17.flyer",
     "1af92ba8b2816e8b6339d3271e47ea8b27b6972d3d54eb229c6afd7058c8e726", 17),
    ("flyers/WIP/experiments/hill_climb_3p333/round3/mixed_screw_pl16.flyer",
     "2b7b496eae6b6473889418495a89ca474e4e7aa989cf33e013d3ee8a82cecf45", 16),
    ("flyers/WIP/experiments/hill_climb_3p333/round4/mixed_screw_pl15.flyer",
     "b24c9bd405a7808b8b052d23a95e1189efc9badcc36224b3b14c8e5a213dbfa1", 15),
]
REPLAY_TICKS = 240
REPLAY_MIN_DISTANCE = 80  # 3.333 bps over 240 ticks

EVIDENCE_LEVELS = ["arithmetic_only", "local_witness", "prescribed_fixture", "closed_geometry", "autonomous_flight"]
MANIFEST_FIELDS = {
    "family": str,
    "evidence_level": str,
    "caps": dict,
    "seed": (int, type(None)),
    "ranges": dict,
    "time_budget_s": (int, float),
    "unique_placements": int,
    "per_stage_rejections": dict,
    "output_hashes": dict,
    "minimal_failure_witness": (dict, type(None)),
    "replay_cmd": str,
    "timestamps": dict,
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def print_json(data: dict) -> None:
    print(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# preflight
# ---------------------------------------------------------------------------

def command_check(cmd: list[str]) -> tuple[bool, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    output = (proc.stdout or proc.stderr).strip().splitlines()
    return proc.returncode == 0, output[0] if output else f"exit {proc.returncode}"


def gxx_check() -> tuple[bool, str]:
    if shutil.which("g++"):
        return command_check(["g++", "--version"])
    ok, detail = command_check(["docker", "run", "--rm", "--network", "none", GXX_DOCKER_IMAGE, "g++", "--version"])
    return ok, f"docker {GXX_DOCKER_IMAGE}: {detail}"


def rustc_check() -> tuple[bool, str]:
    rustc = shutil.which("rustc") or str(CARGO_RUSTC)
    return command_check([rustc, "--version"])


def executable_check(path: Path) -> tuple[bool, str]:
    if not path.is_file():
        return False, f"missing: {path}"
    if not os.access(path, os.X_OK):
        return False, f"not executable: {path}"
    return True, str(path.relative_to(ROOT))


def scratch_check() -> tuple[bool, str]:
    try:
        with tempfile.NamedTemporaryFile(dir=HERE, prefix=".preflight-", suffix=".tmp") as fh:
            fh.write(b"ok")
            fh.flush()
        return True, f"writable: {HERE.relative_to(ROOT)}"
    except OSError as exc:
        return False, str(exc)


def cmd_preflight(_args: argparse.Namespace) -> int:
    started = now()
    checks = {
        "venv_python": executable_check(VENV_PYTHON),
        "ortools": command_check([str(VENV_PYTHON), "-c", "import ortools; print(ortools.__version__)"]),
        "fastflyer": command_check([str(VENV_PYTHON), "-c", "import fastflyer; print('fastflyer ok')"]),
        "g++": gxx_check(),
        "rustc": rustc_check(),
        **{name: executable_check(RELEASE / name) for name in REQUIRED_BINARIES},
        "scratch_write": scratch_check(),
    }
    ok = all(passed for passed, _ in checks.values())
    print_json({
        "status": "OK" if ok else "BROKEN",
        "started_at": started,
        "finished_at": now(),
        "checks": {name: {"ok": passed, "detail": detail} for name, (passed, detail) in checks.items()},
    })
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# replay
# ---------------------------------------------------------------------------

def replay_one(rel_path: str, expected_sha: str, expected_pl: int) -> dict:
    from verify_climb import VerificationError, run_audit, run_bank_stats

    path = ROOT / rel_path
    row = {"flyer": rel_path, "pl": expected_pl, "problems": []}
    if not path.exists():
        row["problems"].append("missing file")
        return row

    if sha256_file(path) != expected_sha:
        row["problems"].append("sha256 mismatch")

    try:
        audit = run_audit(path, REPLAY_TICKS)
        stats = run_bank_stats(path, REPLAY_TICKS)
    except VerificationError as exc:
        row["problems"].append(str(exc))
        return row

    row.update(distance=audit["distance"], max_action=audit["max_successful_action"],
               bank_distance=stats["distance"], conserved=stats["endpoint_conserved"])
    problems = row["problems"]
    if audit["limit"] != expected_pl:
        problems.append(f"encoded PL {audit['limit']}")
    if audit["movement_failures"] or audit["extension_failures"] or audit["conservation_mismatch_ticks"]:
        problems.append("audit not clean")
    if audit["max_successful_action"] > expected_pl:
        problems.append(f"max action {audit['max_successful_action']} > PL")
    if min(audit["distance"], stats["distance"]) < REPLAY_MIN_DISTANCE:
        problems.append(f"distance < {REPLAY_MIN_DISTANCE}")
    if stats["extension_failures"] or not stats["endpoint_conserved"]:
        problems.append("bank-stats not clean")
    return row


def cmd_replay(_args: argparse.Namespace) -> int:
    rows = [replay_one(*entry) for entry in HEADLINE_FLYERS]

    print(f"Replay: {REPLAY_TICKS} ticks, distance >= {REPLAY_MIN_DISTANCE}, clean audit + fastsim-bank-stats")
    print(f"{'flyer':<34} {'PL':>3} {'dist':>5} {'bank':>5} {'max':>4} {'cons':>5}  result")
    for row in rows:
        name = row["flyer"].split("hill_climb_3p333/")[-1].removeprefix("flyers/bank/")
        result = "ok" if not row["problems"] else "REGRESSION: " + "; ".join(row["problems"])
        print(f"{name:<34} {row['pl']:>3} {row.get('distance', '-'):>5} {row.get('bank_distance', '-'):>5} "
              f"{row.get('max_action', '-'):>4} {str(row.get('conserved', '-')).lower():>5}  {result}")

    regressions = sum(1 for row in rows if row["problems"])
    print(f"{len(rows) - regressions}/{len(rows)} ok")
    return 1 if regressions else 0


# ---------------------------------------------------------------------------
# manifest
# ---------------------------------------------------------------------------

def validate_manifest(manifest: dict) -> list[str]:
    """Return a list of problems; an empty list means the manifest is valid."""
    errors = [f"missing field: {key}" for key in MANIFEST_FIELDS if key not in manifest]
    errors += [f"unknown field: {key}" for key in manifest if key not in MANIFEST_FIELDS]
    errors += [
        f"{key}: wrong type {type(manifest[key]).__name__}"
        for key, expected in MANIFEST_FIELDS.items()
        if key in manifest and not isinstance(manifest[key], expected)
    ]
    if errors:
        return errors

    level = manifest["evidence_level"]
    if level not in EVIDENCE_LEVELS:
        errors.append(f"evidence_level must be one of {EVIDENCE_LEVELS}")

    # Counts are over deduplicated poses: a repeated pose is one placement and at most one rejection.
    unique = manifest["unique_placements"]
    rejections = manifest["per_stage_rejections"]
    if unique < 0:
        errors.append("unique_placements must be >= 0")
    if any(not isinstance(n, int) or n < 0 for n in rejections.values()):
        errors.append("per_stage_rejections values must be ints >= 0")
    elif sum(rejections.values()) > unique:
        errors.append(f"per_stage_rejections total {sum(rejections.values())} > unique_placements {unique}")

    if any(not isinstance(h, str) or len(h) != 64 for h in manifest["output_hashes"].values()):
        errors.append("output_hashes values must be SHA-256 hex digests")

    # Only a verify_climb.py replay of a saved .flyer counts as closed flight.
    if level == "autonomous_flight":
        if "verify_climb.py" not in manifest["replay_cmd"]:
            errors.append("autonomous_flight needs a verify_climb.py replay_cmd")
        if not any(name.endswith(".flyer") for name in manifest["output_hashes"]):
            errors.append("autonomous_flight needs a .flyer in output_hashes")

    if "started" not in manifest["timestamps"]:
        errors.append("timestamps.started is required")
    return errors


def write_manifest(path: Path, **fields) -> dict:
    """Validate and write a manifest; raise ValueError when it is invalid."""
    manifest = {key: fields.get(key) for key in MANIFEST_FIELDS}
    errors = validate_manifest(manifest)
    if errors:
        raise ValueError("invalid manifest: " + "; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def cmd_manifest_init(args: argparse.Namespace) -> int:
    try:
        manifest = write_manifest(
            args.out,
            family=args.family,
            evidence_level=args.evidence_level,
            caps={},
            seed=args.seed,
            ranges={},
            time_budget_s=args.time_budget_s,
            unique_placements=0,
            per_stage_rejections={},
            output_hashes={},
            minimal_failure_witness=None,
            replay_cmd=args.replay_cmd,
            timestamps={"started": now(), "finished": None},
        )
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print_json(manifest)
    return 0


def cmd_manifest_validate(args: argparse.Namespace) -> int:
    report = {}
    for path in args.files:
        try:
            report[str(path)] = validate_manifest(json.loads(path.read_text()))
        except (OSError, json.JSONDecodeError) as exc:
            report[str(path)] = [str(exc)]
    print_json({name: errors or "valid" for name, errors in report.items()})
    return 1 if any(report.values()) else 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("preflight", help="check toolchain, binaries and scratch access").set_defaults(fn=cmd_preflight)
    sub.add_parser("replay", help="re-fly headline verified flyers").set_defaults(fn=cmd_replay)

    manifest = sub.add_parser("manifest", help="write or validate Round 7 search manifests")
    manifest_sub = manifest.add_subparsers(dest="manifest_command", required=True)

    init = manifest_sub.add_parser("init", help="write a manifest skeleton")
    init.add_argument("--family", required=True)
    init.add_argument("--evidence-level", required=True, choices=EVIDENCE_LEVELS)
    init.add_argument("--seed", type=int, default=None)
    init.add_argument("--time-budget-s", type=float, default=0.0)
    init.add_argument("--replay-cmd", default="")
    init.add_argument("--out", type=Path, required=True)
    init.set_defaults(fn=cmd_manifest_init)

    validate = manifest_sub.add_parser("validate", help="validate manifest files")
    validate.add_argument("files", type=Path, nargs="+")
    validate.set_defaults(fn=cmd_manifest_validate)

    return ap.parse_args()


def main() -> int:
    args = parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
