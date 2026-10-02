"""delete 2 cells of a body (given snapshot coords) and add 1 slime cell touching the remainder. python d2a1.py BASE OUT LIM cells"""
import sys, pathlib, itertools
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4]))
from fastflyer import Flyer, Block, Kind
base, out, lim = sys.argv[1], pathlib.Path(sys.argv[2]), int(sys.argv[3])
body = [tuple(int(v) for v in c.split(',')) for c in sys.argv[4].split(';')]
out.mkdir(parents=True, exist_ok=True)
B = Flyer.load(base); cells = {tuple(p): b for p, b in B.blocks()}
F = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
add = lambda a, b: (a[0]+b[0], a[1]+b[1], a[2]+b[2])
n = 0
for a, b in itertools.combinations(body, 2):
    keep = [c for c in body if c not in (a, b)]
    for c in sorted({add(k, f) for k in keep for f in F}):
        if (c in cells and c not in (a, b)) or c in (a, b): continue
        if any(add(c, f) in cells and add(c, f) not in body and cells[add(c, f)].kind == Kind.SLIME for f in F): continue
        g = Flyer.load(base); g.push_limit = lim
        g.remove(a); g.remove(b); g.set(c, Block(Kind.SLIME))
        g.save(str(out / ('d%d.%d.%d_%d.%d.%d_a%d.%d.%d' % (a + b + c) + f'_L{lim}.flyer'))); n += 1
print('wrote', n)
