"""Which power need blocks a rot180 twin-pull core at load 7?  usage: python subA_powdiag.py dy,dz gx gy,gz wy,wz SEGS
SEGS: comma list of chain-1 names whose pistons may take power from outside (images too), e.g. K4 or K5 or F-less."""
import sys, time
from subA_lib import *
dy, dz = (int(v) for v in sys.argv[1].split(',')); gx = int(sys.argv[2])
g = tuple(int(v) for v in sys.argv[3].split(',')); w = tuple(int(v) for v in sys.argv[4].split(','))
pm = tuple(s for s in sys.argv[5].split(',') if s) if len(sys.argv) > 5 else ()
noF = len(sys.argv) > 6 and sys.argv[6] == 'noF'
d = (-1, dy, dz); phi = lambda q: (dy - q[0], dz - q[1]); cy, cz = dy // 2, dz // 2
ys = range(cy - 1, cy + 3); zs = range(cz - 1, cz + 3)
k4y = range(min(0, cy - 2), max(4, cy + 3) + 1); k4z = range(min(0, cz - 2), max(4, cz + 3) + 1)
boxes = {5: [(x, y, z) for x in range(gx, gx + 4) for y in ys for z in zs],
         4: [(x, y, z) for x in range(7, gx) for y in k4y for z in k4z]}
fb = [(x, y, z) for x in range(gx + 2, gx + 6) for y in range(cy - 2, cy + 4) for z in range(cz - 2, cz + 4)]
import os
LL = int(os.environ.get('LL', 7)); MS = {k: int(v) for k, v in (x.split('=') for x in os.environ.get('MS', '').split(',') if x)}
M = build('rot180', d, LL, boxes, fb, powmiss=pm, noF=noF, maxsize=MS or None)
pg = phi(g)
pin(M, [('K5', (gx, *g), 'g'), ('K5', (gx, *w), 'g'), ('K5', (gx + 1, *w), 'g'), ('K5', (gx + 2, *w), 'g'),
        ('K5', (gx + 2, *pg), 'S')], assume=False)
st, dt = M.solve(float(sys.argv[7]) if len(sys.argv) > 7 else 90, 4)
print(d, gx, g, w, 'L', LL, 'maxsize', MS, 'powmiss', pm, 'noF' if noF else '', st, round(dt, 1), flush=True)
if st in ('OPTIMAL', 'FEASIBLE'):
    print(report(M)); print(show([s for s in M.extract() if s[0] in ('K3', 'K4', 'K5', "K4'", "K5'", 'F')]))
