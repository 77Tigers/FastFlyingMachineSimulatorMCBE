"""Bounded tip cross-section/column search against the verified joint T/G core.

Grow only connected slime at the existing tip's X plane. First certify each
supplied-tip control; then synthesize its three natural pushes, retaining every
existing natural action. Diagnostic search pools require strict PL11 acceptance.
"""
import argparse
import copy
import json
import subprocess
import time
from pathlib import Path

from assemble import Flyer, ROOT, port_pos
from fastflyer import Block
from joint_tip_layout import near


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path, help="verified run containing check/")
    ap.add_argument("output", type=Path)
    ap.add_argument("--seconds", type=float, default=150)
    ap.add_argument("--budget", type=float, default=2)
    ap.add_argument("--cells", type=int, default=4)
    ap.add_argument("--min-cells", type=int, default=1, help="skip completed smaller shape sizes")
    ap.add_argument("--rider-completion", action="store_true")
    ap.add_argument("--strict-search", action="store_true")
    ap.add_argument("--counterexample", nargs=3, type=int, metavar=("RNG", "PX", "PZ"))
    a = ap.parse_args()
    if not 1 <= a.min_cells <= a.cells:
        raise ValueError("require 1 <= min-cells <= cells")
    if a.output.exists():
        raise ValueError("refusing an existing search")
    a.output.mkdir(parents=True)
    source = a.source / "check"
    original = json.loads((source / "before_natural.json").read_text(encoding="utf-8"))
    base = Flyer.load(source / "problem.flyer")
    ti, tip = next((i, p) for i, p in enumerate(original["ports"]) if p["name"] == "tip")
    tx, ty, tz = tip["at"]
    drive = [list(map(int, s.split())) for s in (source / "drive.txt").read_text().splitlines()]
    omitted = {(t, *port_pos(tip, t, 10, 3)) for t in range(30) if t % 10 in (0, 2, 8)}
    kept = [r for r in drive if tuple(r[:4]) not in omitted]
    assert len(drive) - len(kept) == 9
    shapes = {frozenset({(ty, tz)})}
    start = time.monotonic()
    state = {"scope": "natural tip column on fixed joint T/G; other rear strokes supplied",
             "max_tip_glue": a.cells, "min_tip_glue": a.min_cells, "cases": [], "complete": False,
             "search_policy": {"strict_search": a.strict_search, "counterexample": a.counterexample,
                               "rider_completion": a.rider_completion, "budget_seconds": a.budget}}
    save = lambda: (a.output / "summary.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    for n in range(1, a.cells + 1):
        if n < a.min_cells:
            shapes = {frozenset(set(s) | {p}) for s in shapes for p in set.union(*(near(q) for q in s)) - set(s)
                      if (tx, *p) not in base._cells}
            continue
        for shape in sorted(shapes, key=lambda s: sorted(s)):
            if time.monotonic() - start >= a.seconds:
                break
            out = a.output / f"case{len(state['cases']):04d}"
            out.mkdir()
            row = {"case": out.name, "tip_yz": sorted(shape)}
            state["cases"].append(row)
            f = Flyer.load(source / "problem.flyer")
            for y, z in shape - {(ty, tz)}:
                assert (tx, y, z) not in f._cells
                f.set((tx, y, z), Block.decode(1))
            f.save(out / "problem.flyer")
            g = Flyer.load(out / "problem.flyer")
            minimum = lambda cells: tuple(min(p[k] for p in cells) for k in range(3))
            delta = tuple(b - v for v, b in zip(minimum(f._cells), minimum(g._cells)))
            sh = lambda p: [v + d for v, d in zip(p, delta)]
            assert {tuple(sh(p)): b.encode() for p, b in f._cells.items()} == {p: b.encode() for p, b in g._cells.items()}
            c = copy.deepcopy(original)
            c["name"] = "joint_tip_growth"
            for p in c["ports"]:
                p["at"] = sh(p["at"])
            c["ports"] += [{"name": f"tip_extra{i}", "at": sh((tx, y, z)), "word": tip["word"], "role": "input"}
                           for i, (y, z) in enumerate(sorted(shape - {(ty, tz)}))]
            c["required_cells"] = [{"at": list(p), "cell": b.encode()} for p, b in g._cells.items() if b.kind != 10]
            c["boundary_envelope"] = {"min": [min(p[k] for p in g._cells) - 5 for k in range(3)],
                                      "max": [max(p[k] for p in g._cells) + 5 for k in range(3)]}
            write_drive = lambda rows: (out / "drive.txt").write_text("\n".join(" ".join(map(str, (t, *sh((x, y, z)), cap))) for t, x, y, z, cap in rows) + "\n")
            write_drive(drive)
            (out / "control_drive.txt").write_bytes((out / "drive.txt").read_bytes())
            control = copy.deepcopy(c)
            control["prescribed_script"] = "control_drive.txt"
            (out / "control_problem.json").write_text(json.dumps(control, indent=2) + "\n", encoding="utf-8")
            subprocess.run([str(ROOT / "target/release/contract-verify.exe"), str(out / "control_problem.json"), str(out / "control.json"), "10", "4"], capture_output=True)
            report = json.loads((out / "control.json").read_text())
            row["control"] = report
            save()
            if not report["verified"]:
                continue
            for p in c["ports"]:
                if p["name"] == "tip" or p["name"].startswith("tip_extra"):
                    p["role"] = "output"
            write_drive(kept)
            (out / "problem.json").write_text(json.dumps(c, indent=2) + "\n", encoding="utf-8")
            with (out / "search.log").open("w") as log:
                command = [str(ROOT / "target/release/column-solve.exe"), str(out / "problem.json"), str(out / "search"), str(a.budget), "--wide", "--pool-only", "--target-port", str(ti)]
                if a.rider_completion:
                    command.append("--rider-completion")
                if a.strict_search:
                    command.append("--strict-search")
                if a.counterexample:
                    command += ["--counterexample", *map(str, a.counterexample)]
                subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
            pool = json.loads((out / "search/pool.json").read_text())
            row["proposals"] = len(pool)
            if pool:
                subprocess.run(["python", str(Path(__file__).with_name("certify_column_pool.py")), str(out / "problem.json"), str(out / "search/pool.json"), str(out / "cert"), "--seconds", str(max(1, a.seconds - (time.monotonic() - start)))], check=True, capture_output=True)
                cert = json.loads((out / "cert/summary.json").read_text())
                row["certification"] = {k: v for k, v in cert.items() if k != "cases"}
                if cert.get("lead"):
                    state["lead"] = cert["lead"]
                    break
            save()
        else:
            shapes = {frozenset(set(s) | {p}) for s in shapes for p in set.union(*(near(q) for q in s)) - set(s)
                      if (tx, *p) not in base._cells}
            continue
        break
    else:
        state["complete"] = True
    state["elapsed_seconds"] = time.monotonic() - start
    save()
    print(json.dumps({k: v for k, v in state.items() if k != "cases"}))


if __name__ == "__main__":
    main()
