"""Step 1 of the design work: banked PL8 with K5's observer REMOVED and a power rider W (free word among the
candidates, free kind) giving V its slot-3 power.  usage: python t_bankW.py L WORD [r] [tl]"""
import sys, time
from pbuild import *
L = int(sys.argv[1]); wword = WORDS[sys.argv[2]] if sys.argv[2] in WORDS else tuple(int(c) for c in sys.argv[2])
r = int(sys.argv[3]) if len(sys.argv) > 3 else 2; tl = float(sys.argv[4]) if len(sys.argv) > 4 else 120
B = BANKC
K5 = {u: k for u, k in B['K5'][1].items() if k[0] != 'O'}
Fc = {u: k for u, k in B['F'][1].items() if u != (13, 4, 4)}
parts = [('K2',) + (B['K2'][0], B['K2'][1], None, None), ('K3', B['K3'][0], B['K3'][1], None, None),
         ('K4', B['K4'][0], B['K4'][1], None, None), ('K5', B['K5'][0], K5, None, None),
         ('V', B['V'][0], B['V'][1], None, None)]
parts = [(p[0], p[1], p[2], None, ['P'] if p[0] == 'V' else None) if p[0] == 'V' else p for p in parts]
parts[-1] = ('V', B['V'][0], B['V'][1], None, ['P'])
parts.append(('W', wword, None, cube((10, 3, 3), range(-3, 3), r), KPOW))
t0 = time.time()
M = build('flipz', (-1, 0, 8), L, parts, fixF=Fc)
print('built', round(time.time() - t0, 1), flush=True)
st, dt = M.solve(tl, 4)
print('W word', wword, 'L', L, st, round(dt, 1), flush=True)
if st in ('OPTIMAL', 'FEASIBLE'):
    print(report(M)); sol = save(M, HERE / 'runs' / f'bankW_{"".join(map(str, wword))}_L{L}.pkl')
    print(show([s for s in sol if s[0] in ('K4', 'K5', 'V', 'W', "W'", 'F')]))
