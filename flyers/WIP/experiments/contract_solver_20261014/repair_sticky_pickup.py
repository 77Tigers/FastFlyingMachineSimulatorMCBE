"""Test short connected G pickup paths and offsetting trims on a failing tip.

New geometry contracts retain every other natural/input obligation. No supplied
tip motion, relaxed capacity or reference hardware is used.
"""
import os as _research_os
import argparse
import copy
import hashlib
import itertools
import json
import subprocess
import time
from pathlib import Path

from assemble import Flyer, ROOT
from fastflyer import Block
from trim_generated_carriers import connected


def adjacent(p):
    for k in range(3):
        for d in (-1, 1):
            q = list(p)
            q[k] += d
            yield tuple(q)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--actor", nargs=3, type=int, required=True)
    ap.add_argument("--max-add", type=int, default=3)
    ap.add_argument("--max-trim", type=int, default=3)
    ap.add_argument("--seconds", type=float, default=180)
    ap.add_argument("--omit", nargs=3, type=int, action="append", default=[],
                    help="remove named optional hardware before testing geometry")
    a = ap.parse_args()
    if a.output.exists():
        raise ValueError("refusing existing pickup search")
    a.output.mkdir(parents=True)
    c = json.loads((a.source / "problem.json").read_text(encoding="utf-8"))
    base = Flyer.load(a.source / c["flyer"])
    assert base.push_limit == 11
    required = {tuple(p["at"]) for p in c["required_cells"]}
    for row in a.omit:
        p = tuple(row)
        if p in required or p not in base._cells:
            raise ValueError("omit must name existing optional hardware")
        base.remove(p)
    points = {tuple(p["at"]) for p in c["ports"] if p["name"].startswith("G")}
    assert points and all(base._cells[p].kind == 2 for p in points)
    # G has moved once before tick4; the sticky has not moved since its pull.
    targets = {(p[0] - 1, *p[1:]) for p in adjacent(tuple(a.actor))}
    paths = set()

    def grow(path):
        if path[-1] in targets:
            paths.add(frozenset(path))
        if len(path) == a.max_add:
            return
        for q in adjacent(path[-1]):
            if q not in base._cells and q not in path:
                grow(path + [q])

    for p in sorted(points):
        for q in adjacent(p):
            if q not in base._cells:
                grow([q])
    options = []
    for path in sorted(paths, key=lambda s: (len(s), sorted(s))):
        for n in range(min(a.max_trim, len(points) - 1) + 1):
            for removed in itertools.combinations(sorted(points), n):
                if connected((points - set(removed)) | set(path)):
                    options.append((path, removed))
    state = {"scope": "new connected G pickup geometry; tip natural; rear0/1 and neighbor supplied",
             "source": str(a.source), "actor": a.actor, "omitted": a.omit, "paths": len(paths),
             "options": len(options), "cases": [], "complete": False,
             "sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                        [a.source / "problem.json", a.source / c["flyer"], Path(__file__),
                         ROOT / ('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))]}}
    save = lambda: (a.output / "summary.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    drive = [list(map(int, s.split())) for s in (a.source / c["prescribed_script"]).read_text().splitlines()]
    start = time.monotonic()
    for path, removed in options:
        if time.monotonic() - start >= a.seconds:
            break
        out = a.output / f"case{len(state['cases']):04d}"
        out.mkdir()
        f = Flyer.load(a.source / c["flyer"])
        for p in a.omit:
            f.remove(tuple(p))
        for p in removed:
            f.remove(p)
        for p in path:
            f.set(p, Block.decode(2))
        f.save(out / "problem.flyer")
        g = Flyer.load(out / "problem.flyer")
        minimum = lambda cells: tuple(min(p[k] for p in cells) for k in range(3))
        delta = tuple(b - v for v, b in zip(minimum(f._cells), minimum(g._cells)))
        sh = lambda p: [v + d for v, d in zip(p, delta)]
        assert {tuple(sh(p)): b.encode() for p, b in f._cells.items()} == {p: b.encode() for p, b in g._cells.items()}
        q = copy.deepcopy(c)
        q["ports"] = [p for p in q["ports"] if tuple(p["at"]) not in removed]
        for p in q["ports"]:
            p["at"] = sh(p["at"])
        q["ports"] += [{"name": f"G_pickup{i}", "at": sh(p), "word": "wmmmw", "role": "output"}
                       for i, p in enumerate(sorted(path))]
        q["required_cells"] = [{"at": list(p), "cell": b.encode()} for p, b in g._cells.items() if b.kind != 10]
        q["boundary_envelope"] = {"min": [min(p[k] for p in g._cells) - 5 for k in range(3)],
                                  "max": [max(p[k] for p in g._cells) + 5 for k in range(3)]}
        q.update(name="sticky_G_recovery", flyer="problem.flyer", prescribed_script="drive.txt")
        (out / "problem.json").write_text(json.dumps(q, indent=2) + "\n", encoding="utf-8")
        (out / "drive.txt").write_text("\n".join(" ".join(map(str, (t, *sh((x,y,z)), cap)))
                                                   for t,x,y,z,cap in drive) + "\n", encoding="utf-8")
        subprocess.run([str(ROOT / ('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))), str(out / "problem.json"),
                        str(out / "result.json"), "10", "4"], capture_output=True, check=False)
        report = json.loads((out / "result.json").read_text())
        state["cases"].append({"case": out.name, "added": sorted(path), "removed": removed, **report})
        save()
        if report["verified"]:
            state["lead"] = str(out)
            break
    else:
        state["complete"] = True
    state["elapsed_seconds"] = time.monotonic() - start
    save()
    print(json.dumps({k:v for k,v in state.items() if k != "cases"}))


if __name__ == "__main__":
    main()
