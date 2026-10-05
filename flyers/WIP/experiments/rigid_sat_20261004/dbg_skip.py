import sys
from endcap import solve
from satflyer import show
K = ('g','P','S','R','D0','D1','D2','D3','D4','D5','O0','O1','O2','O3','O4','O5')
side, extra = sys.argv[1], sys.argv[2].split(',')
for skip in [(), ('power',), ('adh',), ('move',), ('targets',), ('cause',), ('conn',), ('power','adh'), ('adh','move')]:
    st, dt, sol, M = solve(side, 12, 60, 16, extra, nb=True, kinds=K, skip=skip)
    print(skip, st, round(dt, 1), flush=True)
