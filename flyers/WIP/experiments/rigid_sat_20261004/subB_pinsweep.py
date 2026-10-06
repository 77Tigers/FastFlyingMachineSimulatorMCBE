"""subB pinned sweeps over mirror offsets. Variants define pins on K4/K5/V (+ carriers) for mirror_gen.build.
usage: python subB_pinsweep.py VARIANT TL [maps] [dxlo,dxhi] [fmax] [start]"""
import sys, time
from subB_lib import *

T4 = tcells(4)[0]; T5 = tcells(5)[0]


def variant(name):
    """returns (mode, free, maxsize, pinfn)"""
    if name == 'B2':      # V rides K4@1 (K4 = template + g(8,3,2)), K5@2 (K5 = template - P + g(11,3,3) + P free)
        k4 = dict(T4); k4[(8, 3, 2)] = 'g'
        k5 = {u: k for u, k in T5.items() if k != 'P'}; k5[(11, 3, 3)] = 'g'
        def pins(M, P):
            P.only('K4', k4); P.cells('K5', k5); P.cells('V', {(9, 3, 3): 'P'})
            P.ride(1, 'V', 'K4'); P.ride(2, 'V', 'K5')
        return 'V', (4, 5), {'K4': 6, 'K5': 6, 'V': 1}, pins
    raise KeyError(name)


if __name__ == '__main__':
    name, tl = sys.argv[1], float(sys.argv[2])
    maps = sys.argv[3].split(',') if len(sys.argv) > 3 and sys.argv[3] != 'all' else list(YZ)
    lo, hi = (int(v) for v in (sys.argv[4] if len(sys.argv) > 4 else 'm3,1').replace('m', '-').split(','))
    fmax = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    start = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    mode, free, ms, pins = variant(name)
    cands = sorted(candidates(maps, 5, fmax, range(lo, hi + 1)), key=lambda c: (c[2], abs(c[1][0] + 1)))
    log = open(OUT / f'pinsweep_{name}.log', 'a'); cnt = {}
    print('candidates', len(cands), flush=True)
    for i, (mp, d, fd) in enumerate(cands[start:], start):
        t0 = time.time()
        M = build(mp, d, mode, 7, free=free, maxsize=ms)
        if isinstance(M, str): st, dt = M, 0
        else:
            P = Pins(M); 
            try:
                pins(M, P); st, dt, _ = solve(M, tl, 4)
            except KeyError as e: st, dt = 'PINERR', 0
        cnt[st] = cnt.get(st, 0) + 1
        log.write(f'{i} {mp} {d} fd={fd} {st} {dt:.1f} build={time.time()-t0-dt:.1f}\n'); log.flush()
        if st in ('OPTIMAL', 'FEASIBLE'):
            print('FOUND', mp, d, flush=True); print(report(M)); print(show(M.extract()), flush=True)
            save(M, mp, d, f'{name}_{mp}_{d[0]}_{d[1]}_{d[2]}')
        if i % 20 == 0: print(i, cnt, flush=True)
    print('done', cnt, flush=True)
