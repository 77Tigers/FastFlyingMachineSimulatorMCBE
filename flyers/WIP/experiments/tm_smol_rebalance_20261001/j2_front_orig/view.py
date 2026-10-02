"""Print snapshot slices. python view.py T x0 x1 y0 y1 z0 z1 (snapshot coords, t100 frame shifted so start-frame x = sx-14-(slot shift none))"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4]))
from fastflyer import Flyer, Kind
t, x0, x1, y0, y1, z0, z1 = map(int, sys.argv[1:8])
f = Flyer.load(str(HERE.parent/'snaps_orig'/f't{t}.flyer')) if t else Flyer.load(str(HERE.parent/'orig.flyer'))
c = {tuple(p): b for p, b in f.blocks()}
mn = min(p[0] for p in c)
def ch(b):
    if b is None: return ' .'
    k = b.kind
    if k == Kind.SLIME: return 'sl'
    if k == Kind.HONEY: return 'ho'
    if k == Kind.REDSTONE_BLOCK: return 'RB'
    if k == Kind.PISTON: return ('S' if b.sticky else 'P') + '>' '<^v+-'[b.direction] if False else ('S' if b.sticky else 'P') + 'XxYyZz'[b.direction] + str(b.state)
    if k == Kind.PISTON_ARM: return 'a' + 'XxYyZz'[b.direction]
    if k == Kind.OBSERVER: return 'O' + 'XxYyZz'[b.direction]
    return k.name[:2]
print('tick', t, 'minx', mn)
for z in range(z0, z1+1):
    print(' z=%d   x:' % z + ''.join('%4d' % x for x in range(x0, x1+1)))
    for y in range(y1, y0-1, -1):
        print('  y=%2d    ' % y + ''.join('%4s' % ch(c.get((x+mn, y, z))).replace(' .', '.') for x in range(x0, x1+1)))
