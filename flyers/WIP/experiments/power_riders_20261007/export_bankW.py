"""Banked PL8 + one unmirrored power rider W (redstone block, word wmwm) found by psat: it rides K5' at slot 1 and K5
at slot 3 across the mirror plane (z = 4).  Checked exactly in psat (loads), exported at the max load.
Real-sim test of the power-rider mechanism inside a full flyer.  usage: python export_bankW.py"""
import sys, pickle
from pbuild import *
import rigid
from psat import to_rigid
B = BANKC
parts = [(n, B[n][0], B[n][1], None, ['P'] if n == 'V' else None) for n in ('K2', 'K3', 'K4', 'K5', 'V')]
parts.append(('!W', (1, 3), {(11, 1, 4): 'R'}, None, ['R']))
for L in (7, 8):
    M = build('flipz', (-1, 0, 8), L, parts, fixF=B['F'][1]); st = M.solve(60, 4); print('load', L, st, flush=True)
    if st[0] in ('OPTIMAL', 'FEASIBLE'):
        print(report(M)); sol = save(M, HERE / 'runs' / 'bankW_dead_L8.pkl')
        rigid.to_flyer(to_rigid(sol), L).save(str(HERE / 'runs' / 'bankW_dead_L8.flyer'))
        rigid.to_flyer(to_rigid(sol), 7).save(str(HERE / 'runs' / 'bankW_dead_at_pl7.flyer'))
        print('saved runs/bankW_dead_L8.flyer'); break
