import sys
from endcap import solve
from satflyer import show
K = ('g','P','S','R','D0','D1','D2','D3','D4','D5','O0','O1','O2','O3','O4','O5')
side, extra = sys.argv[1], sys.argv[2].split(',')
st, dt, sol, M = solve(side, 12, 120, 16, extra, nb=True, kinds=K, skip=('softcause',), objective='softcause')
print(st, round(dt, 1))
if sol:
    print('missing causes:', [(M.names[j], t) for (j, t), b in M.softcause.items() if not M.solver.Value(b)])
    print(show(sol))
