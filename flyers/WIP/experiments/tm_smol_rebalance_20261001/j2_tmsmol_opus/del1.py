import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[4]))
argv = sys.argv; sys.argv = ['x']; import planner as P; sys.argv = argv
from fastflyer import Flyer, Kind
base, out = sys.argv[1], pathlib.Path(sys.argv[2]); Bs = [int(x) for x in sys.argv[3].split(',')]
extra = [tuple(int(v) for v in c.split(',')) for c in sys.argv[4].split(';')] if len(sys.argv) > 4 else []
bodies, _ = P.parse(str(HERE.parent / 'base.bodytrack.txt'))
out.mkdir(parents=True, exist_ok=True)
F = Flyer.load(base); cells = {tuple(p) for p, b in F.blocks()}
targets = [(c[0]-2, c[1], c[2]) for b in Bs for c, k in bodies[b]['cells'].items() if k not in ('S-x',)] + [(c[0]-2, c[1], c[2]) for c in extra]
n = 0
for q in targets:
    if q not in cells: print('missing', q); continue
    for lim in [int(x) for x in __import__('os').environ.get('LIMS', '13,14').split(',')]:
        g = Flyer.load(base); g.push_limit = lim; g.remove(q)
        g.save(str(out / f'd{q[0]}.{q[1]}.{q[2]}_L{lim}.flyer')); n += 1
print('wrote', n)
