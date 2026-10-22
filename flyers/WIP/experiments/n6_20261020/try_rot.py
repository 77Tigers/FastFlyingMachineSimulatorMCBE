"""90-degree screw rings from one link translation. usage: python try_rot.py LAYOUT SYM TY TZ DXS(4 comma)"""
import sys
from close_ring import chain, LAY
from ring_designer import Ring, route_all, hard_conflicts, V9
LAY['V9'] = V9
from try_ring import sim, OUT

name, s, ty, tz = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
dxs = [int(v) for v in sys.argv[5].split(',')]
rels = [(dx, (ty, tz), s) for dx in dxs]
place, back = chain(rels)
print('closure back to A:', back)
place = {k: (v[0], tuple(v[1]), v[2]) for k, v in place.items()}
ring = Ring(LAY[name], place)
print('hard', hard_conflicts(ring, first=True))
print(route_all(ring), 'check', ring.check()[:4])
tag = f'rot_{name}_{s}_{ty}_{tz}_' + '_'.join(map(str, dxs))
ring.flyer(60).save(str(OUT / f'{tag}.flyer')); print(sim(OUT / f'{tag}.flyer'), place)
