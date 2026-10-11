"""Model sanity: no riders, K0/N free -> load 7 should be FEASIBLE (7b), load 6 tells whether riders are needed."""
from back6 import *
for L, k0max in ((7, 5), (6, 4)):
    M = build(L, (), 6, k0free=True, k0max=k0max, nmax=2)
    st, dt = M.solve(300, 8); print(L, st, round(dt, 1), flush=True)
    if st in ('OPTIMAL', 'FEASIBLE'): print(show(M.extract())); print(report(M))
