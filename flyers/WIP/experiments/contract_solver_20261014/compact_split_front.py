"""Bounded glue trimming + redstone relocation on the verified direct interface.

Keeps both column rows, observer and helper geometry fixed. No reference input.
Every accepted candidate must pass strict80x3 at encoded11. This is local only.
"""
import argparse
import itertools
import json
import subprocess
import time
from pathlib import Path

from assemble import Flyer
from fastflyer import Block

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DIRS = [tuple(d if i == k else 0 for i in range(3)) for k in range(3) for d in (-1,1)]


def adjacent(p):
    return {tuple(a+b for a,b in zip(p,d)) for d in DIRS}


def connected(cells):
    todo = [next(iter(cells))]
    seen = set(todo)
    while todo:
        for p in adjacent(todo.pop()) & cells - seen:
            seen.add(p)
            todo.append(p)
    return seen == cells


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--seconds", type=float, default=120)
    a = ap.parse_args()
    if a.output.exists():
        raise ValueError("refusing to repeat/overwrite an existing search")
    a.output.mkdir(parents=True)
    base = Flyer.load(a.source / "problem.flyer")
    contract = json.loads((a.source / "before_natural.json").read_text())
    glues = {p for p,b in base._cells.items() if b.kind == 1}
    rb, = [p for p,b in base._cells.items() if b.kind == 6]
    observer, = [p for p,b in base._cells.items() if b.kind == 7]
    start = time.monotonic()
    results = []
    complete = True
    for n in (2,1,0):
        for deleted in itertools.combinations(sorted(glues),n):
            kept = glues - set(deleted)
            if not connected(kept) or not adjacent(observer) & kept:
                continue
            occupied = set(base._cells) - set(deleted) - {rb}
            positions = set.union(*(adjacent(p) for p in kept)) - occupied
            for power_at in sorted(positions):
                if not n and power_at == rb:
                    continue  # unchanged verified control already preserved
                if time.monotonic()-start >= a.seconds:
                    complete = False
                    break
                folder = a.output / f"case{len(results):04d}"
                folder.mkdir()
                f = Flyer.load(a.source / "problem.flyer")
                for p in deleted:
                    f.remove(p)
                f.remove(rb)
                f.set(power_at,Block.decode(6))
                f.save(folder / "problem.flyer")
                if Flyer.load(folder / "problem.flyer").content_hash() != f.content_hash():
                    raise ValueError("unexpected normalization")
                c = json.loads(json.dumps(contract))
                c["name"] = f"compact_split_front_{len(results)}"
                c["prescribed_script"] = str((a.source/"drive.txt").resolve())
                if tuple(c["ports"][0]["at"]) not in kept:
                    c["ports"][0]["at"] = list(min(kept))
                c["required_cells"] = [{"at":list(p),"cell":b.encode()} for p,b in f._cells.items() if b.kind != 10]
                (folder/"before_natural.json").write_text(json.dumps(c,indent=2)+"\n")
                run = subprocess.run([str(ROOT/"target/release/contract-verify.exe"),str(folder/"before_natural.json"),str(folder/"result.json"),"5","4"],capture_output=True,text=True)
                report = json.loads((folder/"result.json").read_text())
                results.append({"case":folder.name,"deleted":deleted,"power_at":power_at,"remaining_glue":len(kept),"exit_code":run.returncode,**report})
            if not complete:
                break
        if not complete:
            break
    out = {"scope":"local prescribed interface only; fixed column rows/observer/helper", "complete":complete,
           "elapsed_seconds":time.monotonic()-start,"tested":len(results),"verified":sum(r["verified"] for r in results),"cases":results}
    (a.output/"summary.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({k:v for k,v in out.items() if k != "cases"}))


if __name__ == "__main__":
    main()
