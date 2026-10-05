# Single/double cell edits of a base flyer, encoded at a target push limit.
import sys, itertools, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from fastflyer import Flyer, Block, Kind
base, out, lim = sys.argv[1], pathlib.Path(sys.argv[2]), int(sys.argv[3])
mode = sys.argv[4] if len(sys.argv) > 4 else 'move'
f0 = Flyer.load(base)
cells = dict(f0.blocks())
glue = [p for p, b in cells.items() if b.kind in (Kind.SLIME, Kind.HONEY)]
D = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
empt = sorted({(p[0]+d[0], p[1]+d[1], p[2]+d[2]) for p in cells for d in D} - set(cells))
out.mkdir(parents=True, exist_ok=True)
n = 0
def save(f, tag):
    global n
    f.push_limit = lim; f.save(out / f'{tag}.flyer'); n += 1
mats = {'s': Block(Kind.SLIME), 'h': Block(Kind.HONEY)}
if mode in ('move', 'all'):
    for g in glue:
        for e in empt:
            for m, blk in mats.items():
                f = Flyer.load(base); f.remove(g); f.set(e, blk)
                save(f, f'mv_{g[0]}_{g[1]}_{g[2]}__{e[0]}_{e[1]}_{e[2]}{m}')
if mode in ('del', 'all'):
    for g in glue:
        f = Flyer.load(base); f.remove(g); save(f, f'del_{g[0]}_{g[1]}_{g[2]}')
    for g in glue:
        f = Flyer.load(base); f.set(g, mats['h'] if cells[g].kind == Kind.SLIME else mats['s']); save(f, f'sw_{g[0]}_{g[1]}_{g[2]}')
print(n, 'candidates')
