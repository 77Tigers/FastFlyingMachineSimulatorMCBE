"""classify k3v INFEASIBLE cases: does the base model (all rule families skipped, load 7) already fail?"""
import re, ast
from subB_lib import *
T4 = tcells(4)[0]; T5 = tcells(5)[0]
k5must = {u: k for u, k in T5.items() if k != 'P'}
SK = ('power', 'adh', 'move', 'targets', 'cause', 'conn')
out = open(OUT / 'k3class.log', 'w'); cnt = {}
for line in open(OUT / 'k3v.log'):
    m = re.match(r'(\d+) (\w+) (\(.*?\)) V=(\(.*?\)) (\w+) (\w+)', line)
    if not m or m.group(6) != 'INFEASIBLE': continue
    mp, d, v = m.group(2), ast.literal_eval(m.group(3)), ast.literal_eval(m.group(4))
    res = []
    for skip in (SK, ('power',)):
        M = build2(mp, d, 'V', 7, segs={'K4': ('box', nbhd(list(T4), 1)), 'K5': ('box', nbhd(list(k5must), 1))},
                   vbox=[v], maxsize={'K4': 7, 'K5': 6, 'V': 1}, skip=skip)
        P = Pins(M, assume=True); P.cells('K4', T4); P.cells('K5', k5must)
        P.cells('K5', {(11, v[1], v[2]): 'g'}); P.ride(1, 'V', "K3'"); P.ride(2, 'V', 'K5'); P.finish()
        st, dt, core = solve(M, 60, 1, P)
        res.append((st, core))
        if st == 'INFEASIBLE': break
    kind = 'skeleton' if res[0][0] == 'INFEASIBLE' else ('rules-not-power' if res[1][0] == 'INFEASIBLE' else 'power-only')
    cnt[kind] = cnt.get(kind, 0) + 1
    out.write(f'{mp} {d} V={v} {kind} {res}\n'); out.flush()
print(cnt)
