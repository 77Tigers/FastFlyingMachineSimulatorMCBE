"""Which stripped reference pistons can the solver's one-step move generator propose at all?

usage: python flyers/WIP/experiments/contract_solver_20261014/coverage.py [REGEX]
Prints per-problem coverage and a histogram of uncovered piston cell types (dir, sticky, state, powered, angry,
moving) and their neighbourhoods.
"""
import json, re, sys, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3]))
from fastflyer import Flyer
D = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
VARIANTS = {(0,False,0),(0,False,2),(1,True,0),(1,True,2),(0,True,0)}
pat = re.compile(sys.argv[1] if len(sys.argv) > 1 else ".")
miss = collections.Counter(); tot = cov = 0
for meta in sorted(HERE.glob("flyerprobs/*/*/problem_meta.json")):
    d = meta.parent
    if d.name == "reference" or not pat.search(d.as_posix()):
        continue
    ref = Flyer.load(d.parent / "reference" / "reference.flyer"); pr = Flyer.load(d / "problem.flyer")
    rc = {tuple(p): b for p, b in ref._cells.items()}; pc = {tuple(p): b for p, b in pr._cells.items()}
    mn = lambda c: tuple(min(p[i] for p in c) for i in range(3))
    a, b = mn(rc), mn(pc); sh = tuple(b[i] - a[i] for i in range(3))
    rc = {(p[0]+sh[0], p[1]+sh[1], p[2]+sh[2]): v for p, v in rc.items()}
    stripped = [(p, v) for p, v in rc.items() if p not in pc and v.kind.name == "PISTON"]
    spots = set()
    for p, v in pc.items():
        if v.kind.name == "PISTON_ARM": continue
        for dd in D:
            q = (p[0]+dd[0], p[1]+dd[1], p[2]+dd[2])
            if q not in pc: spots.add(q)
    c = 0
    for p, v in stripped:
        key = (v.direction, v.sticky, v.state)
        ok = key in VARIANTS and not v.moving and (p in spots or (v.state == 2 and tuple(p[i]+D[v.direction][i] for i in range(3)) in spots))
        c += ok
        if not ok:
            nb = sorted(rc[tuple(p[i]+dd[i] for i in range(3))].kind.name[:3] for dd in D if tuple(p[i]+dd[i] for i in range(3)) in rc)
            miss[(f"dir{v.direction}", "sticky" if v.sticky else "normal", f"st{v.state}", "pow" if v.powered else "", "angry" if v.angry else "", "MOV" if v.moving else "", "spot" if p in spots else "nospot")] += 1
    tot += len(stripped); cov += c
print(f"stripped pistons {tot}, proposable {cov} ({100*cov/max(tot,1):.0f}%)")
for k, v in miss.most_common(20): print(v, k)
