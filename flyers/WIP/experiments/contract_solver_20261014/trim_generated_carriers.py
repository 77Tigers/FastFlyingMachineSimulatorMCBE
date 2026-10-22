"""Test single connected G-glue trims on generated full tip columns.

These are explicitly NEW geometry contracts: remove the nominated G port/cell,
retain all other natural obligations, permanent identities and the old envelope.
No optional-hardware pruning or relaxed acceptance is involved.
"""
import os as _research_os
import argparse
import copy
import json
import subprocess
import time
from pathlib import Path

from assemble import Flyer, ROOT


def connected(points):
    todo = {next(iter(points))}
    seen = set()
    while todo:
        p = todo.pop()
        seen.add(p)
        todo |= {q for q in points - seen if sum(abs(a-b) for a, b in zip(p, q)) == 1}
    return seen == points


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("search", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--seconds", type=float, default=180)
    ap.add_argument("--sticky-only", action="store_true", help="only new optional pull actors")
    a = ap.parse_args()
    if a.output.exists():
        raise ValueError("existing trim search")
    a.output.mkdir(parents=True)
    old = json.loads((a.search / "summary.json").read_text())
    sources = [a.search / c["case"] / "cert" / f"case{q['index']:04d}"
               for c in old["cases"] if (a.search / c["case"] / "cert/summary.json").exists()
               for q in json.loads((a.search / c["case"] / "cert/summary.json").read_text())["cases"]]
    if a.sticky_only:
        selected = []
        for src in sources:
            c = json.loads((src / "problem.json").read_text())
            required = {tuple(r["at"]) for r in c["required_cells"]}
            f = Flyer.load(src / "problem.flyer")
            if any(b.kind == 9 and b.sticky and p not in required for p,b in f._cells.items()):
                selected.append(src)
        sources = selected
    state = {"scope": "new geometry: connected single G glue deletion; natural tip retained; other rear strokes supplied",
             "sources": len(sources), "cases": [], "complete": False}
    save = lambda: (a.output / "summary.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    start = time.monotonic()
    for src in sources:
        c = json.loads((src / "problem.json").read_text())
        points = {tuple(p["at"]) for p in c["ports"] if p["name"].startswith("G")}
        for removed in sorted(points):
            if not connected(points - {removed}):
                continue
            if time.monotonic() - start >= a.seconds:
                break
            f = Flyer.load(src / "problem.flyer")
            assert f.push_limit == 11 and f._cells[removed].kind == 2
            f.remove(removed)
            out = a.output / f"case{len(state['cases']):04d}"
            out.mkdir()
            f.save(out / "problem.flyer")
            g = Flyer.load(out / "problem.flyer")
            minimum = lambda cells: tuple(min(p[k] for p in cells) for k in range(3))
            delta = tuple(b-v for v, b in zip(minimum(f._cells), minimum(g._cells)))
            sh = lambda p: [v+d for v, d in zip(p, delta)]
            assert {tuple(sh(p)): b.encode() for p, b in f._cells.items()} == {p: b.encode() for p, b in g._cells.items()}
            q = copy.deepcopy(c)
            q["ports"] = [p for p in q["ports"] if tuple(p["at"]) != removed]
            q["required_cells"] = [r for r in q["required_cells"] if tuple(r["at"]) != removed]
            for p in q["ports"]:
                p["at"] = sh(p["at"])
            for r in q["required_cells"]:
                r["at"] = sh(r["at"])
            q["boundary_envelope"] = {k: sh(v) for k, v in q["boundary_envelope"].items()}
            q.update(name="generated_tip_G_leaf_trim", flyer="problem.flyer", prescribed_script="drive.txt")
            (out / "problem.json").write_text(json.dumps(q, indent=2) + "\n", encoding="utf-8")
            drive = [list(map(int, s.split())) for s in (src / c["prescribed_script"]).read_text().splitlines()]
            assert all(r[-1] <= 11 for r in drive)
            (out / "drive.txt").write_text("\n".join(" ".join(map(str, (t, *sh((x, y, z)), cap))) for t, x, y, z, cap in drive) + "\n")
            subprocess.run([str(ROOT / ('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))), str(out / "problem.json"), str(out / "result.json"), "10", "4"], capture_output=True)
            report = json.loads((out / "result.json").read_text())
            row = {"case": out.name, "source": str(src), "removed_G_glue": list(removed), **report}
            state["cases"].append(row)
            save()
            if report["verified"]:
                state["lead"] = str(out)
                break
        else:
            continue
        break
    else:
        state["complete"] = True
    state["elapsed_seconds"] = time.monotonic() - start
    save()
    print(json.dumps({k: v for k, v in state.items() if k != "cases"}))


if __name__ == "__main__":
    main()
