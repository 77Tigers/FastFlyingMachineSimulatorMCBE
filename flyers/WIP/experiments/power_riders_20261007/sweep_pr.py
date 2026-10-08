"""Twinpow-style sweep (rigid_sat_20261004/twinpow_sweep.py) WITH POWER RIDERS, on psat.
K2 = template; K3 must contain its template; K4 must contain glue (8,2,2) (what K3 pushes); K5 free; all three in
template L1 neighbourhoods of radius r.  Rider V (hand-off pusher, fires slot 3, any carriers) + power riders W
(one block R / rod / observer, no glue, words from --w; mirrored pairs) in a box around V's region; F free.
usage: python sweep_pr.py TAG L --w mwwm,wmwm [--r 1] [--tl 60] [--nproc 4] [--maps all] [--dx m3,1] [--fmax 4]
       [--nw 1] [--one MAP,dx,dy,dz]
"""
import sys, time, os, argparse
from multiprocessing import Pool
from pbuild import *
from mirror_gen import candidates

T3, T4, T5 = tcells(3)[0], tcells(4)[0], tcells(5)[0]
RUNS = HERE / 'runs' / 'sweep'; RUNS.mkdir(parents=True, exist_ok=True)


def one(args):
    mp, d, L, wwords, r, tl, nw, wk, ms = args
    t0 = time.time()
    parts = [('K2', tcells(2)[1], tcells(2)[0], None, None),
             ('K3', tcells(3)[1], None, nbhd(list(T3), r), None),
             ('K4', tcells(4)[1], None, nbhd(list(T4), r), None),
             ('K5', tcells(5)[1], None, nbhd(list(T5), r), None),
             ('V', (1, 2), None, cube(ORG[5], range(-3, 2), 2), ['P'])]
    for i in range(nw):
        parts.append((f'W{i}', wwords[i % len(wwords)], None, cube(ORG[5], range(-3, 3), 2), KPOW))
    M = build(mp, d, L, parts, maxsize=ms)
    if isinstance(M, str): return args, M, 0, None
    P = Pins(M); P.cells('K3', T3); P.cells('K4', {(8, 2, 2): 'g'})
    st, dt = M.solve(tl, wk)
    rep = None
    if st in ('OPTIMAL', 'FEASIBLE'):
        rep = report(M)
        sol = save(M, RUNS / f'pr_{mp}_{d[0]}_{d[1]}_{d[2]}_L{L}_{"".join("".join(map(str, w)) for w in wwords)}.pkl')
        rep += '\n' + show([s for s in sol if s[0] in ('K3', 'K4', 'K5', 'V', 'F') or s[0].startswith('W')])
    return args, st, dt, rep


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('tag'); ap.add_argument('L', type=int)
    ap.add_argument('--w', default='mwwm'); ap.add_argument('--r', type=int, default=1)
    ap.add_argument('--tl', type=float, default=60); ap.add_argument('--nproc', type=int, default=4)
    ap.add_argument('--wk', type=int, default=1)
    ap.add_argument('--maps', default='all'); ap.add_argument('--dx', default='m3,1')
    ap.add_argument('--fmax', type=int, default=4); ap.add_argument('--nw', type=int, default=1)
    ap.add_argument('--one', default=None); ap.add_argument('--m5', type=int, default=None)
    ap.add_argument('--m4', type=int, default=None)
    a = ap.parse_args()
    ww = [WORDS[w] if w in WORDS else tuple(int(c) for c in w) for w in a.w.split(',')]
    ms = {'K4': a.m4, 'K5': a.m5, 'V': 1}
    if a.one:
        p = a.one.replace('m', '-').split(',')
        args, st, dt, rep = one((p[0], tuple(int(v) for v in p[1:4]), a.L, ww, a.r, a.tl, a.nw, a.wk, ms))
        print(args[:2], st, round(dt, 1)); print(rep or ''); sys.exit()
    maps = list(YZ) if a.maps == 'all' else a.maps.split(',')
    lo, hi = (int(v) for v in a.dx.replace('m', '-').split(','))
    cands = sorted(candidates(maps, 5, a.fmax, range(lo, hi + 1)), key=lambda c: (c[2], abs(c[1][0] + 1)))
    print('candidates', len(cands), flush=True)
    log = open(RUNS / f'{a.tag}.log', 'a'); cnt = {}
    jobs = [(mp, d, a.L, ww, a.r, a.tl, a.nw, a.wk, ms) for mp, d, _ in cands]
    with Pool(a.nproc) as pool:
        for args, st, dt, rep in pool.imap_unordered(one, jobs):
            cnt[st] = cnt.get(st, 0) + 1
            log.write(f'{args[0]} {args[1]} {st} {dt:.1f}\n'); log.flush()
            if rep: print('FOUND', args[0], args[1], st, '\n' + rep, flush=True)
            if sum(cnt.values()) % 50 == 0: print(cnt, flush=True)
    print('done', cnt, flush=True)
