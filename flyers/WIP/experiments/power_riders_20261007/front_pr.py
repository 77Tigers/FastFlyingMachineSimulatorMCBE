"""Power-rider front search around the banked PL8 mirrored design (flipz, d = (-1,0,8) unless --map/--d given).
Segments K2, K3 fixed (banked = templates); K4, K5 = banked cells (fixed) or free in an L1 neighbourhood of
banked U template cells; V = banked or free box; power riders W (words from --w, kinds R/rods/observers) free in a
box around V; F = banked (minus its useless glue) or free.
usage: python front_pr.py L --w mwwm[,wmwm] [--k4 fix|nbR] [--k5 fix|nbR] [--v fix|box] [--f fix|free]
       [--nw 1] [--m4 N] [--m5 N] [--tl 120] [--wk 4] [--obj maxload] [--wbox R] [--tag T]
"""
import sys, time, argparse
from pbuild import *

ap = argparse.ArgumentParser()
ap.add_argument('L', type=int); ap.add_argument('--w', default='mwwm')
ap.add_argument('--k4', default='fix'); ap.add_argument('--k5', default='nb1')
ap.add_argument('--v', default='fix'); ap.add_argument('--f', default='fix')
ap.add_argument('--nw', type=int, default=1); ap.add_argument('--m4', type=int, default=None)
ap.add_argument('--m5', type=int, default=None); ap.add_argument('--tl', type=float, default=120)
ap.add_argument('--wk', type=int, default=4); ap.add_argument('--obj', default=None)
ap.add_argument('--wbox', type=int, default=2); ap.add_argument('--tag', default=None)
ap.add_argument('--map', default='flipz'); ap.add_argument('--d', default='m1,0,8')
ap.add_argument('--ride', default=None, help='comma list slot:rider:carrier pins, e.g. 1:V:K5p')
ap.add_argument('--nopow5', action='store_true', help='K5 may not hold observers')
ap.add_argument('--wself', type=int, default=0, help='number of self-mirror power riders (word wmwm/mwmw, on plane z=4)')
ap.add_argument('--wsword', default='wmwm')
A = ap.parse_args()
B = BANKC
d = tuple(int(v) for v in A.d.replace('m', '-').split(','))


def seg(nm, mode):
    w, c = B[nm]
    if mode == 'fix': return (nm, w, c, None, None)
    r = int(mode[2:])
    tc = tcells(int(nm[1:]))[0]
    return (nm, w, None, nbhd(list(c) + list(tc), r), None)


parts = [(n, B[n][0], B[n][1], None, None) for n in ('K2', 'K3')]
parts += [seg('K4', A.k4), seg('K5', A.k5)]
if A.v == 'fix': parts.append(('V', B['V'][0], B['V'][1], None, ['P']))
else: parts.append(('V', B['V'][0], None, cube((9, 3, 3), range(-2, 2), 2), ['P']))
words = [WORDS[w] if w in WORDS else tuple(int(c) for c in w) for w in A.w.split(',')]
for i in range(A.nw):
    parts.append((f'W{i}', words[i % len(words)], None, cube((10, 3, 3), range(-3, 3), A.wbox), KPOW))
for i in range(A.wself):
    parts.append((f'!X{i}', WORDS[A.wsword], None, [(x, y, 4) for x in range(6, 15) for y in range(-1, 6)], KPOW))
Fc = {u: k for u, k in B['F'][1].items() if u != (13, 4, 4)}
t0 = time.time()
ms = {'K4': A.m4, 'K5': A.m5}
M = build(A.map, d, A.L, parts, fixF=Fc if A.f == 'fix' else None, maxsize=ms)
if isinstance(M, str): print(M); sys.exit()
if A.nopow5:
    i5 = M.names.index('K5')
    for u in M.boxes[i5]:
        for k in M.kinds_of(i5):
            if k[0] == 'O': M.m.Add(M.X[i5, u, k] == 0)
if A.ride:
    P = Pins(M)
    for spec in A.ride.split(','):
        t, r, c = spec.split(':'); P.ride(int(t), r.replace('p', "'"), c.replace('p', "'"))
print('built', round(time.time() - t0, 1), 'vars', len(M.X), flush=True)
st, dt = M.solve(A.tl, A.wk, objective=A.obj)
print(vars(A), st, round(dt, 1), flush=True)
if st in ('OPTIMAL', 'FEASIBLE'):
    print(report(M))
    tag = A.tag or f'front_pr_L{A.L}_{A.w}_{A.k4}_{A.k5}_{A.v}_{A.f}'
    sol = save(M, HERE / 'runs' / f'{tag}.pkl')
    print(show([s for s in sol if s[0] in ('K4', 'K5', 'V', 'F') or s[0][0] in 'WX']))
    print('saved', HERE / 'runs' / f'{tag}.pkl')
