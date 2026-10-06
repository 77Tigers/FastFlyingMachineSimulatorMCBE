"""mode S (rider sticky Q) at load 8, K4 template, K5 free (r=2): checks the >=8 bound is reachable."""
import sys
from subB_lib import *
mp = sys.argv[1]; d = tuple(int(v) for v in sys.argv[2].replace('m', '-').split(',')); L = int(sys.argv[3])
G.PIN = None
M = G.build(mp, d, 'S', L, 5, (5,), 2)
st, dt = M.solve(float(sys.argv[4]), 4)
print(mp, d, 'S', L, st, round(dt, 1), flush=True)
if st in ('OPTIMAL', 'FEASIBLE'):
    print(report(M)); sol = M.extract(); print('\n'.join(l for l in show(sol).split('\n') if l.split()[0] in ('K4', 'K5', 'V', "K5'", "V'", 'F')))
    save(M, mp, d, f'S_L{L}_{mp}_{d[0]}_{d[1]}_{d[2]}')
