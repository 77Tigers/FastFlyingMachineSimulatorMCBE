"""Twin-pull front (rot180, dx = -1) with wide boxes (2026-10-07): is the subA_tight negative box-limited?
K5 pinned to the forced core (glue (gx,g),(gx,w),(gx+1,w),(gx+2,w) + twin sticky (gx+2,phi(g))), everything else free:
K3 must contain its template (extra blocks allowed), K4 / F / rest of K5 free in wide boxes, all power required.
usage: python twinpull_big.py dy,dz gy,gz wy,wz L [--tl 600] [--wk 8] [--r3 1] [--k4pad 3] [--fpad 3] [--k5pad 1]
       [--powmiss K4|K5] (relaxation = lower bound) [--obj maxload]
"""
import argparse, time
from subA_lib import *

ap = argparse.ArgumentParser()
ap.add_argument('d'); ap.add_argument('g'); ap.add_argument('w'); ap.add_argument('L', type=int)
ap.add_argument('--tl', type=float, default=600); ap.add_argument('--wk', type=int, default=8)
ap.add_argument('--r3', type=int, default=1); ap.add_argument('--k4pad', type=int, default=3)
ap.add_argument('--fpad', type=int, default=3); ap.add_argument('--k5pad', type=int, default=1)
ap.add_argument('--gx', type=int, default=11); ap.add_argument('--k4x', default='6,12')
ap.add_argument('--powmiss', default='', help='e.g. K4 or K5: those pistons (and images) may take power from outside')
ap.add_argument('--obj', default=None, help='maxload: minimise the max load (L = upper bound)')
a_ = ap.parse_args()
dy, dz = (int(v) for v in a_.d.replace('m', '-').split(','))
g = tuple(int(v) for v in a_.g.split(',')); w = tuple(int(v) for v in a_.w.split(','))
d = (-1, dy, dz); phi = lambda q: (dy - q[0], dz - q[1]); pg = phi(g); gx = a_.gx
cy, cz = dy / 2, dz / 2


def yzbox(ylo, yhi, zlo, zhi):
    return [(y, z) for y in range(ylo, yhi + 1) for z in range(zlo, zhi + 1)]


k4x = [int(v) for v in a_.k4x.split(',')]
p4 = a_.k4pad
k4yz = yzbox(min(0, int(cy) - p4), max(4, int(cy) + 1 + p4), min(0, int(cz) - p4), max(4, int(cz) + 1 + p4))
p5 = a_.k5pad
k5yz = yzbox(int(cy) - 1 - p5, int(cy) + 2 + p5, int(cz) - 1 - p5, int(cz) + 2 + p5)
pf = a_.fpad
fyz = yzbox(int(cy) - pf, int(cy) + 1 + pf, int(cz) - pf, int(cz) + 1 + pf)
from subB_lib import nbhd
T3 = tcells(3)[0]
boxes = {3: nbhd(list(T3), a_.r3),
         4: [(x, y, z) for x in range(k4x[0], k4x[1] + 1) for y, z in k4yz],
         5: [(x, y, z) for x in range(gx - 1, gx + 5) for y, z in k5yz]}
fb = [(x, y, z) for x in range(gx + 1, gx + 7) for y, z in fyz]
t0 = time.time()
pm = tuple(x for x in a_.powmiss.split(',') if x)
M = build('rot180', d, a_.L, boxes, fb, powmiss=pm, maxsize={'K5': 7})
if isinstance(M, str):
    print(d, g, w, M); raise SystemExit
pins = [('K5', (gx, *g), 'g'), ('K5', (gx, *w), 'g'), ('K5', (gx + 1, *w), 'g'), ('K5', (gx + 2, *w), 'g'),
        ('K5', (gx + 2, *pg), 'S')] + [('K3', u, k) for u, k in T3.items()]
pin(M, pins, assume=False)
print('d', d, 'g', g, 'w', w, 'L', a_.L, 'boxes K3/K4/K5/F', [len(boxes[3]), len(boxes[4]), len(boxes[5]), len(fb)],
      'powmiss', pm, 'build', round(time.time() - t0, 1), flush=True)
st, dt = M.solve(a_.tl, a_.wk, objective=a_.obj)
print('status', st, round(dt, 1), flush=True)
if st in ('OPTIMAL', 'FEASIBLE'):
    print(report(M)); print(show([s for s in M.extract() if s[0] in ('K3', 'K4', 'K5', "K4'", "K5'", 'F')]))
    p, _ = save(M, 'rot180', d, f'big_{dy}_{dz}_{g[0]}{g[1]}_{w[0]}{w[1]}_L{a_.L}' + ('_pm' + '_'.join(pm) if pm else ''))
    print('saved', p, flush=True)
