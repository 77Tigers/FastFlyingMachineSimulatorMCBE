"""Sub-question A sweep: rot180 (dx=-1, dy,dz odd) twin-pull cores at every corner g of the 2x2 around c=(dy/2,dz/2),
both bridges w, gx in GX.  Pins: K5 glue (gx,g),(gx,w),(gx+1,w),(gx+2,w), twin sticky (gx+2,phi(g)).  K4 free
(cube x 7..gx-1, y/z covering template and c +-2), K5 box x gx..gx+3 over 4x4 around c, F box x gx+2..gx+5 over
6x6 around c (F <= 7 by load).  usage: python subA_sweep.py L "dy,dz;dy,dz" GX(,GX) [--k3] [--tl 60] [--maps rot180]"""
import sys, argparse, time
from subA_lib import *
ap = argparse.ArgumentParser()
ap.add_argument('L', type=int); ap.add_argument('ds'); ap.add_argument('gx')
ap.add_argument('--tl', type=float, default=60); ap.add_argument('--wk', type=int, default=4)
ap.add_argument('--k3', action='store_true'); ap.add_argument('--skip', default='')
ap.add_argument('--log', default='runs/subA/sweep.log'); ap.add_argument('--fr', type=int, default=2)
a_ = ap.parse_args()
skip = tuple(s for s in a_.skip.split(',') if s)
log = open(a_.log, 'a')
for ds in a_.ds.split(';'):
    dy, dz = (int(v) for v in ds.replace('m', '-').split(','))
    d = (-1, dy, dz); phi = lambda q: (dy - q[0], dz - q[1])
    cy, cz = dy // 2, dz // 2          # 2x2 = {cy,cy+1} x {cz,cz+1}
    corners = [(cy, cz), (cy + 1, cz), (cy, cz + 1), (cy + 1, cz + 1)]
    for gx in (int(v) for v in a_.gx.split(',')):
        for g in corners:
            pg = phi(g)
            for w in [(g[0], pg[1]), (pg[0], g[1])]:
                ys = range(cy - 1, cy + 3); zs = range(cz - 1, cz + 3)
                k4y = range(min(0, cy - 2), max(4, cy + 3) + 1); k4z = range(min(0, cz - 2), max(4, cz + 3) + 1)
                boxes = {5: [(x, y, z) for x in range(gx, gx + 4) for y in ys for z in zs],
                         4: [(x, y, z) for x in range(7, gx) for y in k4y for z in k4z]}
                if a_.k3: boxes[3] = cube(ORG[3], (-1, 1), (-2, 2), (-2, 2))
                fr = a_.fr
                fb = [(x, y, z) for x in range(gx + 2, gx + 6) for y in range(cy - fr, cy + fr + 2)
                      for z in range(cz - fr, cz + fr + 2)]
                t0 = time.time()
                M = build('rot180', d, a_.L, boxes, fb, skip=skip)
                tag = f'd={d} gx={gx} g={g} w={w}'
                if isinstance(M, str):
                    print(tag, M, flush=True); log.write(f'{tag} L{a_.L} {M}\n'); log.flush(); continue
                pins = [('K5', (gx, *g), 'g'), ('K5', (gx, *w), 'g'), ('K5', (gx + 1, *w), 'g'),
                        ('K5', (gx + 2, *w), 'g'), ('K5', (gx + 2, *pg), 'S')]
                pin(M, pins, assume=False)
                st, dt = M.solve(a_.tl, a_.wk)
                print(tag, 'L', a_.L, st, round(dt, 1), 'build', round(time.time() - t0 - dt, 1), flush=True)
                log.write(f'{tag} L{a_.L} {"k3 " if a_.k3 else ""}{st} {dt:.1f}\n'); log.flush()
                if st in ('OPTIMAL', 'FEASIBLE'):
                    print(report(M)); print(show(M.extract()))
                    p, _ = save(M, 'rot180', d, f'sweep_{dy}_{dz}_{gx}_{g[0]}{g[1]}_{w[0]}{w[1]}_L{a_.L}')
                    print('saved', p, flush=True)
