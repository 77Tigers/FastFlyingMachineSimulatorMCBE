"""Diagnostic: can two parallel template chains (chain 2 = symmetric image at offset d) coexist at all, ignoring caps?
Segments K1..K7 templates (K1 open at the back, K7 open at the front) and their images."""
import sys, itertools, re
from symcaps import *
import symcaps

def half_mid(side):
    return ([{'name': 'K1', 'tmpl': 1, 'open': {'ext_push', 'Starget', 'pow'}}] +
            [{'name': f'K{K}', 'tmpl': K} for K in range(2, 7)] +
            [{'name': 'K7', 'tmpl': 7, 'open': {'ext_pull', 'Ptarget', 'powmiss'}}])
symcaps.half = half_mid
res = {}
offs = [tuple(int(v) for v in a.split(',')) for a in open('runs/sym_close_offs.txt').read().split()]
for d in offs:
    M = build_sym('mid', d, 7)
    if M is None: res[d] = 'SKEL_OVERLAP'; continue
    st, dt = M.solve(60, 8); res[d] = st
from collections import Counter
print(Counter(res.values()))
def load(f):
    out = {}
    for ln in open(f):
        m = re.match(r'\((-?\d+), (-?\d+), (-?\d+)\) (\S+)', ln)
        if m: out[tuple(int(m.group(i)) for i in (1, 2, 3))] = m.group(4)
    return out
b = load('runs/sym_back_L7.log')
print('back INFEASIBLE but middles OK:', sorted(d for d in offs if b.get(d) == 'INFEASIBLE' and res[d] in ('OPTIMAL', 'FEASIBLE')))
print('middles INFEASIBLE:', sorted(d for d in offs if res[d] == 'INFEASIBLE'))
