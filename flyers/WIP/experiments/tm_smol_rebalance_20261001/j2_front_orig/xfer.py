"""Carry transfer: remove rear carry cells that hold only middle pushers; give the middle body (the pushers' victim)
a short glue path (<=K cells, its material) touching the pusher's side/back so the middle carries it.
python xfer.py OUT [--lim=14] [--k=3]"""
import sys, pathlib, itertools
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4])); sys.path.insert(0, str(HERE.parent))
argv=sys.argv; sys.argv=['x']; import planner as P; sys.argv=argv
from fastflyer import Flyer, Kind, Block
import os
SRC = HERE.parent/('snaps_orig/t100.flyer' if os.environ.get('SNAP') else 'orig.flyer')
DX = 14 if os.environ.get('SNAP') else 0
bodies, _ = P.parse(str(HERE.parent/'orig.bodytrack.txt'))
for _b in bodies.values(): _b['cells'] = {(c[0]+DX, c[1], c[2]): k for c, k in _b['cells'].items()}
own = {c: b for b, d in bodies.items() for c in d['cells']}
base = Flyer.load(str(SRC)); cells = {tuple(p): b for p, b in base.blocks()}
GL = (Kind.SLIME, Kind.HONEY)
def mat(b): return Kind.SLIME if 'sl' in bodies[b]['cells'].values() else Kind.HONEY
# rear cell -> removal set, pushers to transfer, middle
PLAN = [  # (rear body, cells removed, pushers needing middle carry, middle)
 (9, [(2,6,12)], [14], 24),
 (15, [(3,3,9)], [26], 35),
 (15, [(3,5,9)], [23], 35),
 (16, [(3,6,10),(3,5,10)], [22], 29),
 (8, [(2,2,13)], [13], 30),
 (17, [(3,1,11)], [19, 20], 25),
]
lim = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--lim=')), 14))
K = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--k=')), 3))
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
pist = {p for p, b in cells.items() if b.kind in (Kind.PISTON, Kind.PISTON_ARM)}
front = {(p[0]+1, p[1], p[2]) for p in pist}
def okcell(c, kind, M, rm, path):
    if (c in cells and c not in rm) or c in front: return False
    for f in P.FACES:
        q = P.add(c, f)
        if q in rm or q in path: continue
        if q in cells and cells[q].kind == kind and own.get(q) != M: return False
        if q in cells and cells[q].kind == Kind.REDSTONE_BLOCK and own.get(q) != M: return False
    return True
cnt = 0
for R, rm, ps, M in PLAN:
    rm = set(rm); kind = mat(M); Mc = {c for c in bodies[M]['cells']}
    targets = set()
    for pb in ps:
        p = list(bodies[pb]['cells'])[0]
        for f in P.FACES:
            if f != (1, 0, 0): targets.add(P.add(p, f))
    paths = set()
    def grow(path):
        global cnt
        last = path[-1]
        if any(P.add(last, f) in Mc for f in P.FACES):
            paths.add(frozenset(path))
        if len(path) == K: return
        for f in P.FACES:
            n = P.add(last, f)
            if n in path: continue
            if okcell(n, kind, M, rm, path): grow(path + [n])
    for t in targets:
        if okcell(t, kind, M, rm, []): grow([t])
    # keep only minimal paths
    paths = [p for p in paths if not any(q < p for q in paths)]
    for p in paths:
        g = Flyer.load(str(SRC)); g.push_limit = lim
        for c in rm: g.remove(c)
        for c in p: g.set(c, Block(kind))
        g.save(str(out / f'B{R}to{M}_{"_".join("%d.%d.%d" % c for c in sorted(p))}.flyer')); cnt += 1
    print(R, M, len(paths))
print('wrote', cnt)
