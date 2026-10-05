import sys
from endcap import solve
from satflyer import show
K = ('g','P','S','R','O0','O1','O2','O3','O4','O5')
for skip in [(), ('power',), ('adh',), ('move',), ('targets',), ('cause',), ('conn',)]:
    st, dt, sol, M = solve('end', 12, 60, 16, ['mwwm'], nb=True, kinds=K, box=(-3, 4, 2), skip=skip,
                           merges=[(0, ['K4', 'E0'])], keep=('K3', 'K4'))
    print(skip, st, round(dt, 1), flush=True)
st, dt, sol, M = solve('end', 12, 120, 16, ['mwwm'], nb=True, kinds=K, box=(-3, 4, 2), skip=('softcause',),
                       objective='softcause', merges=[(0, ['K4', 'E0'])], keep=('K3', 'K4'))
print(st, [(M.names[j], t) for (j, t), b in M.softcause.items() if sol and not M.solver.Value(b)])
if sol: print(show(sol))
