"""Brute-force observer (+<=1 support glue) placements powering a given sticky, on a base with the old observer
and supports removed. python obsbrute.py BASE OUT STICKY(x,y,z) REMOVE(x,y,z;..) NSUP LIM [R]"""
import sys, pathlib, itertools
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4]))
from fastflyer import Flyer, Block, Kind
base, out = sys.argv[1], pathlib.Path(sys.argv[2])
S = tuple(int(v) for v in sys.argv[3].split(','))
rm = [tuple(int(v) for v in c.split(',')) for c in sys.argv[4].split(';')] if sys.argv[4] != '-' else []
nsup, lim = int(sys.argv[5]), int(sys.argv[6]); R = int(sys.argv[7]) if len(sys.argv) > 7 else 3
out.mkdir(parents=True, exist_ok=True)
B = Flyer.load(base); cells = {tuple(p): b for p, b in B.blocks()}
for c in rm: cells.pop(c, None)
F = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
add = lambda a, b: (a[0]+b[0], a[1]+b[1], a[2]+b[2])
GL = (Kind.SLIME, Kind.HONEY)
targets = {S} | {add(S, f) for f in F if f != (-1,0,0) and add(S, f) in cells and cells[add(S, f)].kind in GL}
n = 0; seen = set()
for t in targets:
    for d, f in enumerate(F):
        o = (t[0]-f[0], t[1]-f[1], t[2]-f[2])
        if o in cells or (t == S and f == (1,0,0)): continue   # observer at S-X (front of sticky) ignored
        nb_glue = [add(o, g) for g in F if add(o, g) in cells and cells[add(o, g)].kind in GL]
        sups = [[]] if nb_glue else []
        if nsup:
            for g in F:
                s1 = add(o, g)
                if s1 in cells or s1 == t: continue
                for kind in GL:
                    if any(add(s1, h) in cells and cells[add(s1, h)].kind == kind for h in F) and \
                       not any(add(s1, h) in cells and cells[add(s1, h)].kind in GL and cells[add(s1, h)].kind != kind for h in F if False):
                        sups.append([(s1, kind)])
        for sp in sups:
            key = (o, d, tuple(sp))
            if key in seen: continue
            seen.add(key)
            g = Flyer.load(base); g.push_limit = lim
            for c in rm: g.remove(c)
            g.set(o, Block.observer(d))
            for c, k in sp: g.set(c, Block(k))
            nm = f'o{o[0]}.{o[1]}.{o[2]}d{d}' + ''.join(f's{c[0]}.{c[1]}.{c[2]}{k.name[0]}' for c, k in sp)
            g.save(str(out / f'{nm}_L{lim}.flyer')); n += 1
print('wrote', n)
