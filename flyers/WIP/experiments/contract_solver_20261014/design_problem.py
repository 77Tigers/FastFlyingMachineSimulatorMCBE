"""Write a from-scratch design problem: glue bodies (cells + material + word), nothing else.

usage: python design_problem.py OUT_DIR SPEC.json
SPEC: {"name": "...", "period": 8, "advance": 2,
       "bodies": [{"word": "mwmw", "material": "slime", "cells": [[0,0,0],[0,1,0]]}, ...]}
The problem is a natural contract (the flyer must fly by itself), recurrence `advance`, every body cell required.
"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3]))
from fastflyer import Flyer, Block, Kind

out = Path(sys.argv[1]); spec = json.loads(Path(sys.argv[2]).read_text())
f = Flyer()
cells = []
for b in spec["bodies"]:
    k = Kind.SLIME if b["material"] == "slime" else Kind.HONEY
    for c in b["cells"]:
        f.set(tuple(c), Block(k)); cells.append(tuple(c))
out.mkdir(parents=True, exist_ok=True)
f.save(out / "problem.flyer")
saved = [tuple(p) for p in Flyer.load(out / "problem.flyer")._cells]
mn = lambda v: tuple(min(p[i] for p in v) for i in range(3))
a, b = mn(cells), mn(saved); d = tuple(b[i] - a[i] for i in range(3))
sh = lambda c: [c[0] + d[0], c[1] + d[1], c[2] + d[2]]
ports = [{"name": f"body{i}", "role": "output", "at": sh(bd["cells"][0]), "word": bd["word"]} for i, bd in enumerate(spec["bodies"])]
req = [{"at": sh(c), "cell": int(Kind.SLIME if bd["material"] == "slime" else Kind.HONEY)} for bd in spec["bodies"] for c in bd["cells"]]
contract = {"version": 1, "name": spec["name"], "flyer": "problem.flyer", "period_ticks": spec["period"], "advance": spec["advance"],
            "cycles": 3, "recurrence": "advance", "ports": ports, "required_cells": req}
(out / "problem.json").write_text(json.dumps(contract, indent=1) + "\n")
(out / "problem_meta.json").write_text(json.dumps({"kind": "design", "spec": spec}) + "\n")
print(out / "problem.json")
