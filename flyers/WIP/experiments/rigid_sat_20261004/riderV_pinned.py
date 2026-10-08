"""Rider-V mirrored front at load 7 with the laws made explicit (2026-10-07): V rides K5 at slot 2 (law L1), so
K5 <= 6; V's slot-1 carrier is left to the solver (K4 then <= 6 through the load cap).  Same model as
mirror_gen.build (K4, K5 free in +-2 / +-r boxes, F free).  Used to re-run the UNKNOWN offsets of runs/gen_V_L7_free.log.
usage: python riderV_pinned.py MAP dx,dy,dz [--tl 300] [--wk 4]           (one offset)
       python riderV_pinned.py --log runs/gen_V_L7_free.log [--nproc 3] [--wk 3] [--tl 300] (all its UNKNOWN offsets)
"""
import argparse, time, os, re, pickle
from multiprocessing import Pool
import mirror_gen as G
from cfgsat import report, HERE
from satflyer import show

ap = argparse.ArgumentParser()
ap.add_argument('map', nargs='?'); ap.add_argument('d', nargs='?')
ap.add_argument('--tl', type=float, default=300); ap.add_argument('--wk', type=int, default=4)
ap.add_argument('--log', default=None); ap.add_argument('--nproc', type=int, default=3)
ap.add_argument('--k5', type=int, default=6); ap.add_argument('--L', type=int, default=7)
ap.add_argument('--out', default='runs/riderV_pinned.log')
A = ap.parse_args()


def one(args):
    mp, d = args
    t0 = time.time()
    M = G.build(mp, d, 'V', A.L, 5, (4, 5), 2, maxsize={'K5': A.k5})
    if isinstance(M, str): return args, M, 0, None
    iv, i5 = M.names.index('V'), M.names.index('K5')
    M.m.Add(M.rc[2, iv, i5] == 1)
    st, dt = M.solve(A.tl, A.wk)
    rep = None
    if st in ('OPTIMAL', 'FEASIBLE'):
        sol = M.extract()
        od = HERE / 'runs' / 'riderV'; od.mkdir(parents=True, exist_ok=True)
        pickle.dump({'sol': sol, 'map': mp, 'd': d, 'riders': ['V', "V'"],
                     'merges': [(1, ['K0', 'N']), (3, ["K0'", "N'"])]},
                    open(od / f'riderV_{mp}_{d[0]}_{d[1]}_{d[2]}_L{A.L}.pkl', 'wb'))
        rep = report(M) + '\n' + show(sol)
    return args, st, dt, rep


if __name__ == '__main__':
    if A.log:
        jobs = []
        for line in open(A.log):
            m = re.match(r'(\w+) \((-?\d+), (-?\d+), (-?\d+)\) V L7 UNKNOWN', line)
            if m: jobs.append((m.group(1), tuple(int(m.group(i)) for i in (2, 3, 4))))
    else:
        jobs = [(A.map, tuple(int(v) for v in A.d.replace('m', '-').split(',')))]
    print('jobs', len(jobs), 'L', A.L, 'K5<=', A.k5, flush=True)
    log = open(A.out, 'a'); cnt = {}
    with Pool(min(A.nproc, len(jobs))) as pool:
        for args, st, dt, rep in pool.imap_unordered(one, jobs):
            cnt[st] = cnt.get(st, 0) + 1
            line = f'{args[0]} {args[1]} V L{A.L} K5<={A.k5} rideK5@2 {st} {dt:.1f}'
            print(line, flush=True); log.write(line + '\n'); log.flush()
            if rep: print(rep, flush=True)
    print('done', cnt, flush=True)
