"""Twin-pull front (rot180, dx = -1): enumerate K5's sticky S5 position on top of the forced core, everything else free
in wide boxes (K3 = template + extras within r3, K4, F, P5).  Optional power relaxation (--powmiss K4 or K5) gives a
lower bound: if INFEASIBLE with K4's power free, K5's slot-0 power alone breaks the load; and vice versa.
usage: python twinpull_enum.py dy,dz gy,gz wy,wz L [--powmiss K4|K5] [--tl 120] [--wk 2] [--nproc 6] [--tag T]
       [--s5 x,y,z] (fix S5, enumerate P5) [--noF]
"""
import argparse, time, os
from multiprocessing import Pool
from subA_lib import build, pin, save, report, show, tcells
from subB_lib import nbhd
from satflyer import D6

ap = argparse.ArgumentParser()
ap.add_argument('d'); ap.add_argument('g'); ap.add_argument('w'); ap.add_argument('L', type=int)
ap.add_argument('--powmiss', default=''); ap.add_argument('--tl', type=float, default=120)
ap.add_argument('--wk', type=int, default=2); ap.add_argument('--nproc', type=int, default=6)
ap.add_argument('--r3', type=int, default=1); ap.add_argument('--tag', default='enum')
ap.add_argument('--gx', type=int, default=11); ap.add_argument('--noF', action='store_true')
ap.add_argument('--s5', default=None, help='fix S5 at x,y,z and enumerate P5 instead')
A = ap.parse_args()
dy, dz = (int(v) for v in A.d.replace('m', '-').split(','))
g = tuple(int(v) for v in A.g.split(',')); w = tuple(int(v) for v in A.w.split(','))
d = (-1, dy, dz); phi = lambda q: (dy - q[0], dz - q[1]); pg = phi(g); gx = A.gx
cy, cz = dy // 2, dz // 2
CORE = {(gx, *g): 'g', (gx, *w): 'g', (gx + 1, *w): 'g', (gx + 2, *w): 'g', (gx + 2, *pg): 'S'}
GLUE = [u for u, k in CORE.items() if k == 'g']
T3 = tcells(3)[0]
PM = tuple(x for x in A.powmiss.split(',') if x)


def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def s5_cands():
    """S5 cells: touching a core glue anywhere but S5's front (-X); front cell not in the core."""
    out = set()
    for u in GLUE:
        for dd in D6:
            c = add(u, dd)
            if c in CORE or dd == (1, 0, 0): continue     # dd = +X would put the glue in S5's front
            out.add(c)
    return sorted(c for c in out if add(c, (-1, 0, 0)) not in CORE)


def boxes():
    k4yz = [(y, z) for y in range(min(0, cy - 3), max(4, cy + 4) + 1) for z in range(min(0, cz - 3), max(4, cz + 4) + 1)]
    k5yz = [(y, z) for y in range(cy - 2, cy + 4) for z in range(cz - 2, cz + 4)]
    fyz = [(y, z) for y in range(cy - 3, cy + 5) for z in range(cz - 3, cz + 5)]
    b = {3: nbhd(list(T3), A.r3),
         4: [(x, y, z) for x in range(6, gx + 2) for y, z in k4yz],
         5: [(x, y, z) for x in range(gx - 1, gx + 5) for y, z in k5yz]}
    fb = [(x, y, z) for x in range(gx + 1, gx + 7) for y, z in fyz]
    return b, fb


def p5_cands(s5):
    core = dict(CORE); core[s5] = 'S'
    out = set()
    for u in GLUE:
        for dd in D6:
            c = add(u, dd)
            if c in core or dd == (-1, 0, 0): continue    # dd = -X would put the glue in P5's front
            out.add(c)
    return sorted(c for c in out if add(c, (1, 0, 0)) not in core)


def one(s5, p5=None):
    t0 = time.time()
    b, fb = boxes()
    M = build('rot180', d, A.L, b, fb, powmiss=PM, maxsize={'K5': 7 if not A.noF else 7}, noF=A.noF)
    if isinstance(M, str): return s5, M, 0, None
    pins = [('K5', u, k) for u, k in CORE.items()] + [('K5', s5, 'S')] + [('K3', u, k) for u, k in T3.items()]
    if p5 is not None: pins.append(('K5', p5, 'P'))
    try:
        pin(M, pins, assume=False)
    except KeyError as e:
        return s5, 'PIN_OUT', 0, None
    st, dt = M.solve(A.tl, A.wk)
    rep = None
    if st in ('OPTIMAL', 'FEASIBLE'):
        rep = report(M) + '\n' + show([s for s in M.extract() if s[0] in ('K3', 'K4', 'K5', "K4'", "K5'", 'F')])
        save(M, 'rot180', d, f'{A.tag}_{dy}_{dz}_{g[0]}{g[1]}_{w[0]}{w[1]}_S{s5[0]}{s5[1]}{s5[2]}_L{A.L}')
    return (s5 if p5 is None else (s5, p5)), st, dt, rep


def one_p(args): return one(*args)


if __name__ == '__main__':
    if A.s5:
        s5 = tuple(int(v) for v in A.s5.split(','))
        cands = [(s5, p) for p in p5_cands(s5)]
    else:
        cands = [(c,) for c in s5_cands()]
    print('d', d, 'g', g, 'w', w, 'L', A.L, 'powmiss', PM, 'noF', A.noF, 'S5 candidates', len(cands), cands, flush=True)
    cnt = {}
    log = open(os.path.join('runs', 'subA', f'{A.tag}.log'), 'a')
    with Pool(A.nproc) as pool:
        for s5, st, dt, rep in pool.imap_unordered(one_p, cands):
            cnt[st] = cnt.get(st, 0) + 1
            line = f'd={d} g={g} w={w} S5/P5={s5} L{A.L} pm={PM} noF={A.noF} {st} {dt:.1f}'
            print(line, flush=True); log.write(line + '\n'); log.flush()
            if rep: print(rep, flush=True)
    print('done', cnt, flush=True)
