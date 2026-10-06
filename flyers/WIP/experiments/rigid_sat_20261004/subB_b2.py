"""B2: V rides K4@1 + K5@2; K4 = template + g(8,3,2) fixed; K5 = template - P + g(11,3,3), P free nearby; V fixed (9,3,3).
usage: python subB_b2.py TL [maps] [dxlo,dxhi] [fmax] [start]"""
import sys, time
from subB_lib import *
T4 = tcells(4)[0]; T5 = tcells(5)[0]
k4 = dict(T4); k4[(8, 3, 2)] = 'g'
k5 = {u: k for u, k in T5.items() if k != 'P'}; k5[(11, 3, 3)] = 'g'
k5box = nbhd(list(k5), 1)
tl = float(sys.argv[1])
maps = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] != 'all' else list(YZ)
lo, hi = (int(v) for v in (sys.argv[3] if len(sys.argv) > 3 else 'm3,1').replace('m', '-').split(','))
fmax = int(sys.argv[4]) if len(sys.argv) > 4 else 4
start = int(sys.argv[5]) if len(sys.argv) > 5 else 0
cands = sorted(candidates(maps, 5, fmax, range(lo, hi + 1)), key=lambda c: (c[2], abs(c[1][0] + 1)))
log = open(OUT / 'b2.log', 'a'); cnt = {}
print('candidates', len(cands), flush=True)
for i, (mp, d, fd) in enumerate(cands[start:], start):
    t0 = time.time()
    M = build2(mp, d, 'V', 7, segs={'K4': ('fixed', k4), 'K5': ('box', k5box)}, vbox=[(9, 3, 3)],
               maxsize={'K5': 6, 'V': 1})
    if isinstance(M, str): st, dt = M, 0
    else:
        P = Pins(M); P.cells('K5', k5); P.ride(1, 'V', 'K4'); P.ride(2, 'V', 'K5')
        st, dt, _ = solve(M, tl, 4)
    cnt[st] = cnt.get(st, 0) + 1
    log.write(f'{i} {mp} {d} fd={fd} {st} {dt:.1f} build={time.time()-t0-dt:.1f}\n'); log.flush()
    if st in ('OPTIMAL', 'FEASIBLE'):
        print('FOUND', mp, d, flush=True); print(report(M)); print(show(M.extract()), flush=True)
        save(M, mp, d, f'B2_{mp}_{d[0]}_{d[1]}_{d[2]}')
    if i % 20 == 0: print(i, cnt, flush=True)
print('done', cnt, flush=True)
