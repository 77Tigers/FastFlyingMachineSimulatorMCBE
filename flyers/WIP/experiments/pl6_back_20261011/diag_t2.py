import sys
from twin6 import build
from back6 import K0, N, tcells, WORDS
from psat import wpos
sys.path.insert(0, '../rigid_sat_20261004')
from front_mirror import YZ, shiftword
q = (2, -1, 0)
k1t = {u: k for u, k in tcells(1)[0].items() if k == 'g'}
half = [('K0', K0, WORDS['mmww']), ('N', N, WORDS['wmmw']), ('K1', k1t, WORDS['wwmm']), ('K2', tcells(2)[0], tcells(2)[1])]
stats = {}
for mp, f in YZ.items():
    for nm, cells, w in half:
        p = wpos(w, 2); s2 = wpos(shiftword(w), 2)
        for u, k in cells.items():
            if k != 'g': continue
            y, z = f(u[1], u[2]); d = (q[0] - (u[0] + p + s2), q[1] - y, q[2] - z)
            r = []
            for lab, sk, pm in (('np', ('power',), ()), ('pw', (), ()), ('K0miss', (), (0, 4))):
                M = build(mp, d, 6, skip=sk, powmiss=pm)
                if isinstance(M, str): r.append(M); break
                st, _ = M.solve(30, 4); r.append(f'{lab}:{st[:4]}')
            print(mp, d, nm + "'", u, ' '.join(r), flush=True)
