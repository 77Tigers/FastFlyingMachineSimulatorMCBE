"""Sub-question A: rot180 twin-pull core with tight boxes.  usage: python subA_tight.py CASE L [--k4tmpl] [--skip ..]
K5 box x gx..gx+3 over the 4x4 yz square around the core; K4 box x 7..10; F box x gx+2..gx+5 (same yz square +-fr)."""
import sys, argparse, time
from subA_lib import *
ap = argparse.ArgumentParser()
ap.add_argument('case', type=int); ap.add_argument('L', type=int)
ap.add_argument('--k4tmpl', action='store_true'); ap.add_argument('--skip', default='')
ap.add_argument('--tl', type=float, default=120); ap.add_argument('--wk', type=int, default=4)
ap.add_argument('--fr', type=int, default=1); ap.add_argument('--k4', default='7,10')
ap.add_argument('--extra', default='', help='extra K5/F/K4 pins: SEG:x,y,z:kind;...')
ap.add_argument('--k3', action='store_true'); ap.add_argument('--noF', action='store_true')
ap.add_argument('--core', action='store_true')
a_ = ap.parse_args()
skip = tuple(s for s in a_.skip.split(',') if s)
a = (2, 3); gx = 11
sigs = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
sig = sigs[a_.case // 2]
pa = (a[0] + sig[0], a[1] + sig[1]); d = (-1, a[0] + pa[0], a[1] + pa[1])
w = [(a[0], pa[1]), (pa[0], a[1])][a_.case % 2]
ys = range(min(a[0], pa[0]) - 1, max(a[0], pa[0]) + 2); zs = range(min(a[1], pa[1]) - 1, max(a[1], pa[1]) + 2)
k4x = [int(v) for v in a_.k4.split(',')]
boxes = {5: [(x, y, z) for x in range(gx, gx + 4) for y in ys for z in zs],
         4: [(x, y, z) for x in range(k4x[0], k4x[1] + 1) for y in range(0, 5) for z in range(0, 5)]}
if a_.k3: boxes[3] = cube(ORG[3], (-1, 1), (-2, 2), (-2, 2))
fr = a_.fr
fb = [(x, y, z) for x in range(gx + 2, gx + 6) for y in range(ys[0] - fr + 1, ys[-1] + fr) for z in range(zs[0] - fr + 1, zs[-1] + fr)]
t0 = time.time()
M = build('rot180', d, a_.L, boxes, fb, skip=skip)
if isinstance(M, str): print(M); sys.exit()
pins = [('K5', (gx, *a), 'g'), ('K5', (gx, *w), 'g'), ('K5', (gx + 1, *w), 'g'), ('K5', (gx + 2, *w), 'g'),
        ('K5', (gx + 2, *pa), 'S')]
if a_.k4tmpl: pins += [('K4', u, k) for u, k in tcells(4)[0].items()]
for item in [s for s in a_.extra.split(';') if s]:
    sg, c, k = item.split(':'); pins.append((sg, tuple(int(v) for v in c.replace('m', '-').split(',')), k))
lits = pin(M, pins)
print('case', a_.case, 'd', d, 'w', w, 'pa', pa, 'L', a_.L, 'skip', skip, 'build', round(time.time() - t0, 1), flush=True)
st, dt, cr = core(M, lits, a_.tl) if a_.core else (*M.solve(a_.tl, a_.wk), None)
print('status', st, round(dt, 1), 'core', cr, flush=True)
if st in ('OPTIMAL', 'FEASIBLE'):
    print(report(M)); print(show(M.extract()))
    p, _ = save(M, 'rot180', d, f'tight_c{a_.case}_L{a_.L}')
    print('saved', p)
