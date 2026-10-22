import sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
sys.path.insert(0, '../n6_20261020')
from close_ring import chain
from ring_designer import V9, ORDER
from nk import Timing, Ring
place, _ = chain([(d, (5, 4), 1) for d in (-1, 0, -1, 2)])
pl = [(v[0], tuple(v[1]), v[2]) for v in (place[X] for X in ORDER)]
mod = dict(R=[(0,) + tuple(r) for r in V9['R']], P=[tuple(p) for p in V9['P']], PLATE=V9['PLATE'], CONT=V9['CONT'])
t = time.time()
T = Timing(6); ring = Ring(T, [mod] * 4, pl)
for X in range(4): ring.route(X)
print('route', time.time() - t, ring.size(), ring.check()[:5])
ring.flyer(26).save('out/test_n6.flyer')
