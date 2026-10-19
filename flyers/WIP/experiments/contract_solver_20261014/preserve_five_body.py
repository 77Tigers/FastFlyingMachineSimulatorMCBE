"""Preserve the independently checked, complete five-body glue compaction."""
import argparse
import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer, Kind


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rewire", action="store_true")
    args = ap.parse_args()
    base = HERE / "out/compaction/five_body_pl18"
    work = base / "rewire_v3" if args.rewire else base
    source = work / "solution.flyer" if args.rewire else work / "subsets_fixedpoint/solution.flyer"
    stem = "five_body_rewired" if args.rewire else "five_body_compacted"
    flyer = Flyer.load(source)
    independent = json.loads((work / "independent.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader((work / "longrun_samples.csv").open(encoding="utf-8")))
    assert independent["passed"] and len(independent["cases"]) == 80
    assert all(c["passed"] for c in independent["cases"])
    assert len(rows) == 80 and flyer.push_limit == 18
    for row in rows:
        assert row["pass"] == "true" and int(row["distance"]) == 3000
        assert int(row["limit"]) == 18 and int(row["max_successful_action"]) <= 18
        assert all(int(row[k]) == 0 for k in (
            "extension_failures", "movement_failures", "conservation_mismatch_ticks"))
    reference = Flyer.load(base / "extracted/reference/reference.flyer")
    removed = set(reference._cells) - set(flyer._cells)
    added = set(flyer._cells) - set(reference._cells)
    assert all(reference._cells[p].kind in (Kind.HONEY, Kind.SLIME) for p in removed)
    assert all(flyer._cells[p].kind in (Kind.HONEY, Kind.SLIME) for p in added)
    assert all(b == reference._cells[p] for p, b in flyer._cells.items() if p in reference._cells)
    assert flyer._piston_blocks == reference._piston_blocks
    if args.rewire:
        assert len(removed) == 3 and len(added) == 1
        change = {"removed_glue": sorted(removed), "added_glue": sorted(added),
                  "hardware_unchanged": True, "reference_cells": len(reference._cells),
                  "compacted_cells": len(flyer._cells), "global_limit": 18,
                  "method": "subset deletion then two-delete/one-insert rear reroute"}
        (work / "compaction_change.json").write_text(json.dumps(change, indent=2) + "\n", encoding="utf-8")
    else:
        change = json.loads((work / "compaction_change.json").read_text(encoding="utf-8"))
        assert removed == {tuple(p) for p in change["removed_glue"]} and not added
    tracked = HERE / "results"
    tracked.mkdir(exist_ok=True)
    shutil.copyfile(work / "longrun_samples.csv", tracked / f"{stem}_samples.csv")
    shutil.copyfile(work / "independent.json", tracked / f"{stem}_independent.json")
    evidence = [source, work / "compaction_change.json", ROOT / "tools/src/bin/glue-subset-solve.rs",
                ROOT / "tools/src/solve.rs"]
    evidence += [work / "audit.json", work / "progress.json"] if args.rewire else [
        work / "compacted_audit.json", work / "subsets_fixedpoint/progress.json", work / "subsets_v2/progress.json"]
    data = {
        "version": 1, "name": stem,
        "claim": f"Complete 3 bps PL18 flyer; {len(removed) - len(added)} fewer glue cells, hardware retained; global limit unchanged",
        "flyer_parameters": {k: getattr(flyer, k) for k in
                             ("phase_x", "phase_z", "rng_state", "push_limit")},
        "cells": [[*p, b.encode()] for p, b in sorted(flyer._cells.items())],
        "piston_owners": [{"at": list(p), "blocks": list(v)}
                          for p, v in sorted(flyer._piston_blocks.items())],
        "content_hash": flyer.content_hash(), "generation": change,
        "validation": {"independent_python_passed": 80, "longrun_passed": 80,
                       "ticks_per_case": 10000, "distance_per_case": 3000,
                       "maximum_action_load": 18, "extension_failures": 0,
                       "movement_failures": 0, "conservation_mismatch_ticks": 0,
                       "body2_peak_100_tick_diagnostic": 17},
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in evidence},
    }
    dest = tracked / f"{stem}.json"
    dest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Preserved {len(flyer._cells)} cells: {dest}")


if __name__ == "__main__":
    main()
