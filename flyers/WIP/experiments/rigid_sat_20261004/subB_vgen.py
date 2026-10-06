"""V-family sweep: mode V; K4 must contain template (box = template + L1-nbhd r4), K5 must contain template minus P
(box = nbhd r5), V free, F free, V's carriers free (V@2 is K5 by geometry). maxsize K4<=m4, K5<=m5.
usage: python subB_vgen.py TAG TL m4 m5 r4 r5 [maps] [dxlo,dxhi] [fmax] [start] [only i,j,..]"""
import sys, time
from subB_lib import *
T4 = tcells(4)[0]; T5 = tcells(5)[0]
tag, tl, m4, m5, r4, r5 = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
maps = sys.argv[7].split(',') if len(sys.argv) > 7 and sys.argv[7] != 'all' else list(YZ)
lo, hi = (int(v) for v in (sys.argv[8] if len(sys.argv) > 8 else 'm3,1').replace('m', '-').split(','))
fmax = int(sys.argv[9]) if len(sys.argv) > 9 else 4
start = int(sys.argv[10]) if len(sys.argv) > 10 else 0
k5must = {u: k for u, k in T5.items() if k != 'P'}
cands = sorted(candidates(maps, 5, fmax, range(lo, hi + 1)), key=lambda c: (c[2], abs(c[1][0] + 1)))
log = open(OUT / f'vgen_{tag}.log', 'a'); cnt = {}
print('candidates', len(cands), flush=True)
for i, (mp, d, fd) in enumerate(cands[start:], start):
    t0 = time.time()
    M = build2(mp, d, 'V', 7, segs={'K4': ('box', nbhd(list(T4), r4)), 'K5': ('box', nbhd(list(k5must), r5))},
               maxsize={'K4': m4, 'K5': m5, 'V': 1})
    if isinstance(M, str): st, dt = M, 0
    else:
        P = Pins(M); P.cells('K4', T4); P.cells('K5', k5must)
        st, dt, _ = solve(M, tl, int(__import__("os").environ.get("WK", "4")))
    cnt[st] = cnt.get(st, 0) + 1
    log.write(f'{i} {mp} {d} fd={fd} {st} {dt:.1f} build={time.time()-t0-dt:.1f}\n'); log.flush()
    if st in ('OPTIMAL', 'FEASIBLE'):
        print('FOUND', mp, d, flush=True); print(report(M)); print(show(M.extract()), flush=True)
        save(M, mp, d, f'vgen_{tag}_{mp}_{d[0]}_{d[1]}_{d[2]}')
    if i % 20 == 0: print(i, cnt, flush=True)
print('done', cnt, flush=True)
