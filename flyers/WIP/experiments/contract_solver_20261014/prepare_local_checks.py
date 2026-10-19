"""Prepare independent and 10000-tick checks for a strict local candidate."""
import argparse
import copy
import json
import shutil
from pathlib import Path

from assemble import Flyer


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("case", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--reproduction", required=True)
    ap.add_argument("--scope", help="explicit interface scope when the default T/G-natural template does not apply")
    a = ap.parse_args()
    if a.output.exists():
        raise ValueError("refusing existing verification run")
    c = json.loads((a.case / "problem.json").read_text(encoding="utf-8"))
    report = json.loads((a.case / "result.json").read_text())
    assert report["verified"] and report["passed"] == report["total"] == 80
    assert report["orders_per_sample"] == 3 and report["ticks_per_order"] == 30
    assert report["encoded_limit"] == 11 and report["max_action"] <= 11
    f = Flyer.load(a.case / c["flyer"])
    assert f.push_limit == 11 and c["period_ticks"] == 10 and c["advance"] == 3 and c["cycles"] == 3
    drive = [list(map(int, s.split())) for s in (a.case / c["prescribed_script"]).read_text().splitlines()]
    assert all(row[-1] <= 11 for row in drive)
    for folder, cycles in ((a.output / "check", 3), (a.output / "longrun/check", 1000)):
        folder.mkdir(parents=True)
        shutil.copyfile(a.case / c["flyer"], folder / "problem.flyer")
        assert Flyer.load(folder / "problem.flyer").content_hash() == f.content_hash()
        q = copy.deepcopy(c)
        q.update(flyer="problem.flyer", prescribed_script="drive.txt", cycles=cycles)
        rows = drive if cycles == 3 else [(t + 10*i, x + 3*i, y, z, cap)
                                         for i in range(cycles) for t, x, y, z, cap in drive if t < 10]
        (folder / "drive.txt").write_text("\n".join(" ".join(map(str, row)) for row in rows) + "\n")
        for order in ("before_natural", "after_natural", "interleaved"):
            q["prescribed_order"] = order
            (folder / f"{order}.json").write_text(json.dumps(q, indent=2) + "\n", encoding="utf-8")
    shutil.copyfile(a.case / "result.json", a.output / "native_short.json")
    tip = next(p for p in c["ports"] if p["name"] == "tip")
    scope = "T/G all moves and rear slot2 natural; rear slots0/1 and neighbor supplied; tip "
    scope += "natural" if tip["role"] == "output" else "supplied"
    scope += "; all glue identities checked"
    if a.scope:
        scope = a.scope
    (a.output / "construction.json").write_text(json.dumps({"scope": scope, "natural_flyer": False,
        "source_case": str(a.case), "reproduction": a.reproduction + "; prepare_local_checks.py CASE OUT --reproduction CONSTRUCTOR"}, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(f._cells)} cells; native short passes max{report['max_action']}")


if __name__ == "__main__":
    main()
