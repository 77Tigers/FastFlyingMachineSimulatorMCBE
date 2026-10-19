"""Preserve a verified local interface, including short cases and long-run inputs."""
import argparse
import hashlib
import json
from pathlib import Path

from assemble import Flyer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--push-limit", type=int, default=11)
    args = parser.parse_args()
    if args.push_limit <= 0:
        raise ValueError("push limit must be positive")
    read = lambda p: json.loads(p.read_text())
    short = read(args.run / "native_short.json")
    long = read(args.run / "longrun/result.json")
    for report, ticks in ((short, 30), (long, 10000)):
        if not (report["verified"] and report["passed"] == report["total"] == 80
                and report["orders_per_sample"] == 3 and report["ticks_per_order"] == ticks
                and report["encoded_limit"] == args.push_limit and report["max_action"] <= args.push_limit
                and report["failure"] is None):
            raise ValueError("incomplete or failed native verification")
    orders = ("before_natural", "after_natural", "interleaved")
    cases = {order: read(args.run / f"samples_{tag}.json")
             for order, tag in zip(orders, ("before", "after", "interleaved"))}
    for report in cases.values():
        if not (report["passed"] and len(report["cases"]) == 80
                and all(c["passed"] and c["whole_assembly_max_action"] <= args.push_limit for c in report["cases"])):
            raise ValueError("incomplete or failed independent verification")
    f = Flyer.load(args.run / "check/problem.flyer")
    if f.push_limit != args.push_limit:
        raise ValueError("artifact flyer's encoded limit differs from verified limit")
    construction = read(args.run / "construction.json")
    reproduction = construction.get("reproduction")
    if reproduction:
        reproduction += "; contract-verify OUT/check/before_natural.json RESULT.json 600 4"
    else:
        reproduction = ("make_split_front_link.py COMPACT/source OUT " if construction.get("helper_body_cells") else "make_split_puller_selective.py INTERFACE OUT --direct " + ("--compact " if construction.get("compact_column") else "")) + "--cycles 1000; contract-verify OUT/check/before_natural.json RESULT.json 600 4"
    if f.content_hash() != Flyer.load(args.run / "longrun/check/problem.flyer").content_hash():
        raise ValueError("short and long runs used different flyers")
    contracts = {order: read(args.run / f"check/{order}.json") for order in orders}
    evidence = ["construction.json", "check/problem.flyer", "check/drive.txt",
                "longrun/check/problem.flyer", "longrun/check/before_natural.json", "longrun/check/drive.txt"]
    artifact = {
        "scope": construction.get("scope", "local interface: front fully natural; both rear carriers and helper supplied") + "; not a closed natural flyer",
        "flyer_parameters": {k: getattr(f,k) for k in ("phase_x", "phase_z", "rng_state", "push_limit")},
        "cells": [[*p,b.encode()] for p,b in sorted(f._cells.items())],
        "piston_owners": [{"at":list(p), "blocks":[list(q) for q in members]}
                          for p,members in sorted(f._piston_blocks.items())],
        "content_hash": f.content_hash(),
        "construction": construction,
        "contracts": contracts, "prescribed_drive": (args.run / "check/drive.txt").read_text(),
        "independent_cases": cases, "native_short": short, "native_longrun": long,
        "longrun_contract": read(args.run / "longrun/check/before_natural.json"),
        "longrun_reproduction": reproduction,
        "sha256": {p: hashlib.sha256((args.run/p).read_bytes()).hexdigest() for p in evidence},
    }
    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    args.artifact.write_text(json.dumps(artifact, indent=2) + "\n")
    print(f"Preserved {len(f._cells)} cells, independent240/240 and native80x3x10000")


if __name__ == "__main__":
    main()
