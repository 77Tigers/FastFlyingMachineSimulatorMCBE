"""Screen every rot180 exact-twin-pull core (dx = -1, dy/dz odd, corner g of the 2x2 around c = d/2, both bridges w)
with ALL K4/K5 piston power supplied from outside (powmiss K4,K5) in wide boxes.  An offset that is INFEASIBLE even
then is dead for the twin pull whatever the power; only the survivors need the power analysis (twinpull_enum.py).
usage: python twinpull_screen.py L "dy,dz;dy,dz;..." [--tl 120] [--wk 3] [--nproc 3]
"""
import argparse, time, os
from multiprocessing import Pool
from subA_lib import build, pin, report, show, tcells, save
from subB_lib import nbhd

ap = argparse.ArgumentParser()
ap.add_argument('L', type=int); ap.add_argument('ds')
ap.add_argument('--tl', type=float, default=120); ap.add_argument('--wk', type=int, default=3)
ap.add_argument('--nproc', type=int, default=3); ap.add_argument('--gx', type=int, default=11)
ap.add_argument('--pm', default='K4,K5'); ap.add_argument('--tag', default='screen')
A = ap.parse_args()
T3 = tcells(3)[0]
PM = tuple(x for x in A.pm.split(',') if x)


def job(args):
    dy, dz, g, w = args
    gx = A.gx; d = (-1, dy, dz); phi = lambda q: (dy - q[0], dz - q[1]); pg = phi(g)
    cy, cz = dy // 2, dz // 2
    k4yz = [(y, z) for y in range(min(0, cy - 3), max(4, cy + 4) + 1) for z in range(min(0, cz - 3), max(4, cz + 4) + 1)]
    k5yz = [(y, z) for y in range(cy - 2, cy + 4) for z in range(cz - 2, cz + 4)]
    fyz = [(y, z) for y in range(cy - 3, cy + 5) for z in range(cz - 3, cz + 5)]
    b = {3: nbhd(list(T3), 1), 4: [(x, y, z) for x in range(6, gx + 2) for y, z in k4yz],
         5: [(x, y, z) for x in range(gx - 1, gx + 5) for y, z in k5yz]}
    fb = [(x, y, z) for x in range(gx + 1, gx + 7) for y, z in fyz]
    t0 = time.time()
    M = build('rot180', d, A.L, b, fb, powmiss=PM, maxsize={'K5': 7})
    if isinstance(M, str): return args, M, 0, None
    pins = [('K5', (gx, *g), 'g'), ('K5', (gx, *w), 'g'), ('K5', (gx + 1, *w), 'g'), ('K5', (gx + 2, *w), 'g'),
            ('K5', (gx + 2, *pg), 'S')] + [('K3', u, k) for u, k in T3.items()]
    try:
        pin(M, pins, assume=False)
    except KeyError:
        return args, 'PIN_OUT', 0, None
    st, dt = M.solve(A.tl, A.wk)
    rep = None
    if st in ('OPTIMAL', 'FEASIBLE'):
        rep = report(M) + '\n' + show([s for s in M.extract() if s[0] in ('K3', 'K4', 'K5', 'F')])
        save(M, 'rot180', d, f'{A.tag}_{dy}_{dz}_{g[0]}{g[1]}_{w[0]}{w[1]}_L{A.L}')
    return args, st, dt, rep


if __name__ == '__main__':
    jobs = []
    for ds in A.ds.split(';'):
        dy, dz = (int(v) for v in ds.replace('m', '-').split(','))
        cy, cz = dy // 2, dz // 2
        for g in [(cy, cz), (cy + 1, cz), (cy, cz + 1), (cy + 1, cz + 1)]:
            pg = (dy - g[0], dz - g[1])
            for w in [(g[0], pg[1]), (pg[0], g[1])]:
                jobs.append((dy, dz, g, w))
    print('jobs', len(jobs), 'L', A.L, 'powmiss', PM, flush=True)
    log = open(os.path.join('runs', 'subA', f'{A.tag}.log'), 'a'); cnt = {}
    with Pool(A.nproc) as pool:
        for args, st, dt, rep in pool.imap_unordered(job, jobs):
            cnt[st] = cnt.get(st, 0) + 1
            line = f'd=(-1,{args[0]},{args[1]}) g={args[2]} w={args[3]} L{A.L} pm={PM} {st} {dt:.1f}'
            print(line, flush=True); log.write(line + '\n'); log.flush()
            if rep: print(rep, flush=True)
    print('done', cnt, flush=True)
