"""Targeted V-family: V rides K3'@1 and K5@2 (pinned), V at a hand-derived cell; K4 >= template (+nbhd r1, <=6 with
observer allowed), K5 >= template minus P (+nbhd r1, <=6). Offsets from subB_k3filter (dx 0/1)."""
import sys, time, os, io, contextlib
from subB_lib import *
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    import subB_k3filter as KF
T4 = tcells(4)[0]; T5 = tcells(5)[0]
k5must = {u: k for u, k in T5.items() if k != 'P'}
wk = int(os.environ.get('WK', '2')); tl = float(sys.argv[1]) if len(sys.argv) > 1 else 120
log = open(OUT / 'k3v.log', 'a'); cnt = {}
for i, (mp, d, fd, ok) in enumerate(sorted(KF.out, key=lambda o: o[2])):
    for v, how in ok:
        t0 = time.time()
        M = build2(mp, d, 'V', 7, segs={'K4': ('box', nbhd(list(T4), 1)), 'K5': ('box', nbhd(list(k5must), 1))},
                   vbox=[v], maxsize={'K4': 7, 'K5': 6, 'V': 1})
        if isinstance(M, str): st, dt = M, 0
        else:
            P = Pins(M); P.cells('K4', T4); P.cells('K5', k5must)
            P.cells('K5', {(11, v[1], v[2]): 'g'}); P.ride(1, 'V', "K3'"); P.ride(2, 'V', 'K5')
            st, dt, _ = solve(M, tl, wk)
        cnt[st] = cnt.get(st, 0) + 1
        log.write(f'{i} {mp} {d} V={v} {how} {st} {dt:.1f} build={time.time()-t0-dt:.1f}\n'); log.flush()
        if st in ('OPTIMAL', 'FEASIBLE'):
            print('FOUND', mp, d, v, flush=True); print(report(M)); print(show(M.extract()), flush=True)
            save(M, mp, d, f'k3v_{mp}_{d[0]}_{d[1]}_{d[2]}')
print('done', cnt, flush=True)
