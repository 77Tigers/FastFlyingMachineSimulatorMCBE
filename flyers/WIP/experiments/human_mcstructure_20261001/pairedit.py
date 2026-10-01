"""Delete-one + add-one glue screen. python pairedit.py IN.flyer TICKS LIMIT [MAXN]"""
import sys, pathlib, itertools
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4])); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fastflyer import Flyer, Block, Kind, DIRECTIONS
import simtools
from perturb import clone
def run(path, ticks, limit, add_only=False):
    f = Flyer.load(path); f.push_limit = limit
    cells = dict(f.blocks())
    glue = [p for p, b in cells.items() if b.kind in (Kind.SLIME, Kind.HONEY)]
    empties = sorted({(p[0]+d[0], p[1]+d[1], p[2]+d[2]) for p in cells for d in DIRECTIONS} - set(cells))
    vs = {}
    dels = [None] if add_only else [None] + glue
    for dp in dels:
        for e in empties:
            for k in (Kind.SLIME, Kind.HONEY):
                g = clone(f)
                if dp: g.remove(dp)
                g.set(e, Block(k)); vs[f'd{dp}_a{e}{k.name[0]}'] = g
    print(len(vs), 'variants')
    res = simtools.screen(vs, ticks)
    good = sorted(res.items(), key=lambda kv: -int(kv[1]['distance']))
    for n, r in good[:12]: print(f'{n:<40}', simtools.brief(r))
    return res
if __name__ == '__main__':
    run(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
