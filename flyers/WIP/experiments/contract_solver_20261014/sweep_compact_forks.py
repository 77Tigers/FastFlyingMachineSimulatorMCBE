"""Bounded tm_smol body0 fork orientations; sequential column probes only."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import time

from assemble import ext_contract, ROOT
from make_compact_body0 import build


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    binary = ROOT / "target/release/column-solve.exe"
    state = {"verified": False, "scope": "four lateral stems, two forward-fork leaves, eight glue cells",
             "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "cases": []}
    save = lambda: (args.output / "summary.json").write_text(json.dumps(state, indent=2) + "\n")
    center = (4, 5, 4)
    dirs = ((0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    add = lambda p, d: tuple(a + b for a, b in zip(p, d))
    for direction in dirs:
        stem = add(center, direction)
        branches = [add(stem, d) for d in dirs if add(stem, d) != center]
        for leaves in itertools.combinations(branches, 2):
            added = {stem, *leaves}
            row = {"added": sorted(added)}
            state["cases"].append(row)
            # Already exhausted by the initial compact-fork probe.
            if added == {(4, 4, 4), (4, 3, 4), (4, 4, 5)}:
                row["status"] = "previously_exhausted_zero_body0_options"
                save()
                continue
            out = args.output / f"case{len(state['cases']) - 1}"
            try:
                build(args.problem, out / "source", added)
            except ValueError as error:
                row.update(status="invalid_geometry", reason=str(error))
                save()
                continue
            c = json.loads((out / "source/problem.json").read_text())
            counts = {}
            for body in (0, 3):
                target = out / f"generated/body{body}"
                delta = ext_contract(c, body, 11, target, out / "source/problem.flyer", None)
                if delta != (0, 0, 0):
                    raise ValueError("unexpected extension normalization")
                cmd = [str(binary), str(target / "problem.json"), str(target / "sol"),
                       "45", "--pool-only", "--wide"]
                start = time.monotonic()
                with (out / f"body{body}.log").open("w") as log:
                    subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True)
                count = len(json.loads((target / "sol/pool.json").read_text()))
                counts[str(body)] = count
                row.setdefault("commands", []).append({"argv": cmd, "elapsed_seconds": time.monotonic() - start})
                row["candidates"] = counts
                save()
                if not count:
                    break
            row["status"] = "locally_nonempty" if counts.get("0") and counts.get("3") else "generator_gap"
            save()
            print(json.dumps(row), flush=True)
            if row["status"] == "locally_nonempty":
                state["next"] = "recertify all bodies on changed geometry; not a complete design"
                save()
                return
    state["complete"] = True
    save()


if __name__ == "__main__":
    main()
