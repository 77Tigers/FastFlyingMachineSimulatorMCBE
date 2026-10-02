"""Map orig bodytrack (start-frame) body cells into the t100 snapshot frame: global dx + per-body correction."""
import sys, pathlib, collections
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4])); sys.path.insert(0, str(HERE.parent))
argv=sys.argv; sys.argv=['x']; import planner as P; sys.argv=argv
from fastflyer import Flyer, Kind, Block
KM = {'sl': Kind.SLIME, 'ho': Kind.HONEY, 'RB': Kind.REDSTONE_BLOCK, 'gl': Kind.GLASS if hasattr(Kind,'GLASS') else None}
bodies, _ = P.parse(str(HERE.parent/'orig.bodytrack.txt'))
SNAP = HERE.parent/'snaps_orig'/'t100.flyer'
snap = Flyer.load(str(SNAP)); sc = {tuple(p): b for p, b in snap.blocks()}
def match(b, dx):
    n = 0
    for c, k in bodies[b]['cells'].items():
        q = (c[0]+dx, c[1], c[2])
        if k == 'P' or k.startswith('S'):
            n += q in sc and sc[q].kind == Kind.PISTON
        elif KM.get(k) is not None:
            n += q in sc and sc[q].kind == KM[k]
    return n
votes = collections.Counter()
for b in bodies:
    if bodies[b]['glue']:
        for dx in range(-60, 60): votes[dx] += match(b, dx)
DX = votes.most_common(1)[0][0]
off = {}
for b in bodies:
    best = max(range(DX-3, DX+4), key=lambda d: (match(b, d), -abs(d-DX)))
    off[b] = best
def to_snap(b, c): return (c[0]+off[b], c[1], c[2])
if __name__ == '__main__':
    print('DX', DX, 'snapshot minx', min(p[0] for p in sc))
    for b in sorted(bodies):
        if off[b] != DX: print('B%d off %+d (%d/%d)' % (b, off[b]-DX, match(b, off[b]), len(bodies[b]['cells'])))
    bad = [b for b in bodies if match(b, off[b]) < len(bodies[b]['cells'])]
    print('imperfect', bad)
