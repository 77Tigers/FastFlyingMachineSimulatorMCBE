"""Retry named (map, d) candidates of the L7 w2 sweep with a long time limit, 1 process x 4 workers.
usage: python retry_unknown.py TL LOG MAP,dx,dy,dz [MAP,dx,dy,dz ...]   (m = minus sign)"""
import sys, re
from sweep_pr import *
tl, logf = float(sys.argv[1]), sys.argv[2]
ww = [WORDS['mwwm'], WORDS['wmwm']]; ms = {'K4': None, 'K5': None, 'V': 1}
log = open(logf, 'a')
for spec in sys.argv[3:]:
    p = spec.replace('m', '-').split(',') if not spec.startswith('rot') else spec.replace('m', '-').split(',')
    mp, d = p[0], tuple(int(v) for v in p[1:4])
    args, st, dt, rep = one((mp, d, 7, ww, 1, tl, 2, 4, ms))
    log.write(f'{mp} {d} {st} {dt:.1f} (retry tl={tl:.0f})\n'); log.flush()
    print(mp, d, st, round(dt, 1), flush=True)
    if rep: print('FOUND', rep, flush=True)
