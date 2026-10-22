"""Rebuild the accepted N6 flyers. usage: python build_best.py OUTDIR"""
import sys, pathlib
from ring_designer import Ring, V4, route_all
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
PLACE = {'A': (-1, (-2, 0), 6), 'B': (-1, (-1, 6), 0), 'C': (-1, (-5, 5), 6), 'D': (-3, (-5, 1), 6)}
ring = Ring(V4, PLACE); print(route_all(ring), 'check', ring.check())
ring.flyer(30).save(str(out / 'n6_ring_pinwheel_pl30.flyer'))

# 90-degree screw ring of V6 modules (PL28, 80/80; PL27 0/80)
from close_ring import chain, LAY
from ring_designer import V6
place, _ = chain([(-1, (-4, 1), 1), (0, (-4, 1), 1), (-1, (-4, 1), 1), (2, (-4, 1), 1)])
ring = Ring(V6, {k: (v[0], tuple(v[1]), v[2]) for k, v in place.items()}); print(route_all(ring), 'check', ring.check())
ring.flyer(28).save(str(out / 'n6_screw_v6_pl28.flyer'))

# 90-degree screw ring of V9 modules (3 RBs, 2x2 cover in the hole): PL26, 80/80; PL25 0/80
from ring_designer import V9
place, _ = chain([(d, (5, 4), 1) for d in (-1, 0, -1, 2)])
ring = Ring(V9, {k: (v[0], tuple(v[1]), v[2]) for k, v in place.items()}); print(route_all(ring), 'check', ring.check())
ring.flyer(26).save(str(out / 'n6_screw_ring3rb_pl26.flyer'))
