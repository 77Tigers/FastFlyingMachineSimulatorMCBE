import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4])); sys.path.insert(0, str(HERE.parent))
argv=sys.argv; sys.argv=['x']; import planner as P; sys.argv=argv
from fastflyer import Flyer, Kind
f = Flyer.load(str(HERE.parent/'orig.flyer'))
cells = {tuple(p): b for p, b in f.blocks()}
mn = min(p[0] for p in cells); print('minx', mn, 'n', len(cells), 'lim', f.push_limit)
bodies, ev = P.parse(str(HERE.parent/'orig.bodytrack.txt'))
own = {}
for b, d in bodies.items():
    for c in d['cells']: own[c] = b
# frame check
hit = sum(1 for c in own if c in cells); print('bodytrack cells present in start file:', hit, '/', len(own))
def nm(blk):
    k = blk.kind.name[:4]
    if blk.kind == Kind.PISTON: k = ('S' if blk.sticky else 'P') + 'xXyYzZ'[blk.direction] if hasattr(blk,'direction') else k
    return k
for b in map(int, sys.argv[1:]):
    print('B%d word %s' % (b, bodies[b]['word']))
    for c, k in bodies[b]['cells'].items():
        ns = []
        for f_ in P.FACES:
            q = P.add(c, f_)
            if q in cells: ns.append('%s:%s/B%s' % ('+x -x +y -y +z -z'.split()[P.FACES.index(f_)], cells[q].kind.name[:5], own.get(q, '?')))
        print('  ', c, k, ' '.join(ns))
