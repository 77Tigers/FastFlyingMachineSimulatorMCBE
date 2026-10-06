"""Twin-powered front (2026-10-06): K3, K4, K5 re-laid in small boxes (template cells + L1 neighbourhood), so a segment's
pistons may be powered by its own twin (the twin sits at a unique x offset at the segment's fire slot) instead of by the
next chain segment. K3 must contain its template (it may add blocks, e.g. a redstone for K3''s hub); K4 must contain
only the glue K3 pushes (8,2,2); K5 is free in its box. Rider V (mode V) or no rider (mode none = twin pull), F free.
usage: python twinpow_sweep.py TAG MODE TL m3 m4 m5 r [maps|all] [dxlo,dxhi] [fmax] [nproc]
       (m3/m4/m5 = max blocks of K3/K4/K5; r = neighbourhood radius of the boxes)"""
import sys, time, os
from multiprocessing import Pool
from subB_lib import build2, nbhd, Pins, solve, save, report, show, tcells, candidates, YZ, OUT
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / 'runs' / 'twinpow'; RUNS.mkdir(parents=True, exist_ok=True)
T3, T4, T5 = tcells(3)[0], tcells(4)[0], tcells(5)[0]


def one(args):
    mp, d, mode, tl, m3, m4, m5, r = args
    t0 = time.time()
    segs = {'K3': ('box', nbhd(list(T3), r)), 'K4': ('box', nbhd(list(T4), r)), 'K5': ('box', nbhd(list(T5), r))}
    ms = {'K3': m3, 'K4': m4, 'K5': m5}
    if mode == 'V': ms['V'] = 1
    M = build2(mp, d, mode, int(os.environ.get('LOAD', 7)), segs=segs, maxsize=ms)
    if isinstance(M, str): return args, M, 0, None, None
    P = Pins(M); P.cells('K3', T3); P.cells('K4', {(8, 2, 2): 'g'})
    st, dt, _ = solve(M, tl, 1)
    rep = sol = None
    if st in ('OPTIMAL', 'FEASIBLE'):
        rep = report(M) + '\n' + show(M.extract())
        save(M, mp, d, f'twinpow_{mode}_{mp}_{d[0]}_{d[1]}_{d[2]}')
    return args, st, dt, time.time() - t0, rep


if __name__ == '__main__':
    tag, mode, tl = sys.argv[1], sys.argv[2], float(sys.argv[3])
    m3, m4, m5, r = (int(v) for v in sys.argv[4:8])
    maps = list(YZ) if len(sys.argv) <= 8 or sys.argv[8] == 'all' else sys.argv[8].split(',')
    lo, hi = (int(v) for v in (sys.argv[9] if len(sys.argv) > 9 else 'm3,1').replace('m', '-').split(','))
    fmax = int(sys.argv[10]) if len(sys.argv) > 10 else 4
    nproc = int(sys.argv[11]) if len(sys.argv) > 11 else 8
    cands = sorted(candidates(maps, 5, fmax, range(lo, hi + 1)), key=lambda c: (c[2], abs(c[1][0] + 1)))
    print('candidates', len(cands), flush=True)
    log = open(RUNS / f'{tag}.log', 'a'); cnt = {}
    with Pool(nproc) as pool:
        for args, st, dt, tot, rep in pool.imap_unordered(one, [(mp, d, mode, tl, m3, m4, m5, r) for mp, d, _ in cands]):
            cnt[st] = cnt.get(st, 0) + 1
            log.write(f'{args[0]} {args[1]} {mode} {st} {dt:.1f}\n'); log.flush()
            if rep: print('FOUND', args[0], args[1], st, '\n' + rep, flush=True)
            if sum(cnt.values()) % 50 == 0: print(cnt, flush=True)
    print('done', cnt, flush=True)
