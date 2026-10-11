"""Offsets where a FIXED twin glue cell lands on a relay cell next to K0's N-pusher at slot 2 -> solve each."""
import sys, itertools
from twin6 import build
from back6 import K0, N, tcells, WORDS
from psat import wpos
sys.path.insert(0, '../rigid_sat_20261004')
from front_mirror import YZ, shiftword
Q = [(2, -2, -1), (2, -1, 0), (2, -1, -2)]
k1t = {u: k for u, k in tcells(1)[0].items() if k == 'g'}
half = [(K0, WORDS['mmww']), (N, WORDS['wmmw']), (k1t, WORDS['wwmm']), (tcells(2)[0], tcells(2)[1])]
tl = float(sys.argv[1]) if len(sys.argv) > 1 else 120
cands = set()
for mp, f in YZ.items():
    for cells, w in half:
        p = wpos(w, 2); w2 = shiftword(w); s2 = wpos(w2, 2)
        for u, k in cells.items():
            if k != 'g': continue
            y, z = f(u[1], u[2])
            for q in Q:
                # twin cell slot-0 = (u0 + p + dx, y + dy, z + dz); at slot 2 add s2
                d = (q[0] - (u[0] + p + s2), q[1] - y, q[2] - z)
                cands.add((mp, d))
print(len(cands), 'targeted offsets', flush=True)
res = {}
for mp, d in sorted(cands):
    M = build(mp, d, 6)
    if isinstance(M, str): res[M] = res.get(M, 0) + 1; continue
    st, dt = M.solve(tl, 4)
    res[st] = res.get(st, 0) + 1
    print(mp, d, st, f'{dt:.1f}s', flush=True)
    if st in ('OPTIMAL', 'FEASIBLE'):
        from back6 import show, report
        import pickle
        sol = M.extract(); print(show(sol)); print(report(M), flush=True)
        pickle.dump({'sol': sol, 'map': mp, 'd': d}, open(f"runs/twinT_L6_{mp}_{'_'.join(map(str, d))}.pkl", 'wb'))
print(res)
