"""Family 2 mirrored, skeleton enumeration (2026-10-09).
1. Power-free model (skip power, K4/K5 kinds g,P,S only, Q forced to pull K5) at load L: enumerate distinct skeletons
   (K4, K5, Q cells) with no-goods.
2. For each skeleton: pin it, let power blocks (any kind) be added in an L1 radius-R neighbourhood, solve with power
   at loads L and L+1.
usage: python m2enum.py MAP D L N [R] [TL]     e.g. python m2enum.py rot180 m1,5,7 7 15 2 60
"""
import sys, pathlib, time, os
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pinfront import *

mp, dd, L, N = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
R = int(sys.argv[5]) if len(sys.argv) > 5 else 2
TL = float(sys.argv[6]) if len(sys.argv) > 6 else 60
d = tuple(int(v) for v in dd.replace('m', '-').split(','))
tm = [('K2', W4, T[2], None, None, None, None), ('K3', W5, T[3], None, None, None, None)]


def force_q(M):
    for q, k5 in (('Q', 'K5'), ("Q'", "K5'")):
        iq, ik = M.names.index(q), M.names.index(k5)
        kq = [t for t in range(4) if M.ph[iq][t] == 'ret'][0]
        for u in M.boxes[iq]:
            v = (u[0] + M.sh[iq][kq] - 2 - M.sh[ik][kq], u[1], u[2])
            l = M.x(ik, v, 'g')
            if l is False: M.m.Add(M.X[iq, u, 'S'] == 0)
            else: M.m.Add(l == 1).OnlyEnforceIf(M.X[iq, u, 'S'])


k4box = nbhd(list(T[4]), 1)
k5box = sorted(set(nbhd(list(T[5]), 1) + cube((8, 0, 1), (12, 4, 5))))
qbox = cube((8, 0, 0), (13, 5, 6))
skel_parts = tm + [('K4', W4, None, k4box, None, {(8, 2, 2): 'g'}, None),
                   ('K5', W5, None, k5box, None, {(11, 2, 3): 'g'}, None),
                   ('Q', W4, None, qbox, ['S'], None, None)]
M = mbuild(mp, d, L, skel_parts, skip=('power',))
for nm in ('K4', 'K5'):         # skeleton = glue + pistons only
    i = M.names.index(nm)
    for u in M.boxes[i]:
        for k in M.kinds_of(i):
            if k not in ('g', 'P', 'S'): M.m.Add(M.X[i, u, k] == 0)
force_q(M)
seen = 0
for it in range(N):
    st, dt = M.solve(TL, 4)
    if st not in ('OPTIMAL', 'FEASIBLE'):
        print(f'skeleton search {it}: {st} {dt:.1f}s -> stop', flush=True); break
    sv = M.solver
    sk = {}
    lits = []
    for nm in ('K4', 'K5', 'Q'):
        i = M.names.index(nm)
        sk[nm] = {u: k for u in M.boxes[i] for k in M.kinds_of(i) if sv.Value(M.X[i, u, k])}
        lits += [M.X[i, u, k] for u, k in sk[nm].items()]
    rides = sorted((t, M.names[r], M.names[j]) for (t, r, j), v in M.rc.items() if sv.Value(v) and M.names[r] == 'Q')
    M.m.AddBoolOr([l.Not() for l in lits])          # no-good
    seen += 1
    desc = ' | '.join(f'{nm}: ' + ' '.join(f'{u}{k}' for u, k in sorted(c.items())) for nm, c in sk.items())
    print(f'skeleton {it} ({dt:.1f}s) Q rides {[(t, j) for t, _, j in rides]}: {desc}', flush=True)
    for LL in [int(v) for v in os.environ.get('LLS', f'{L},{L + 1}').split(',')]:
        parts = tm + [('K4', W4, None, nbhd(list(sk['K4']), R), None, sk['K4'], None),
                      ('K5', W5, None, nbhd(list(sk['K5']), R), None, sk['K5'], None),
                      ('Q', W4, None, list(sk['Q']), ['S'], None, None)]
        P = mbuild(mp, d, LL, parts)
        force_q(P)
        st2, dt2 = P.solve(TL, 4)
        print(f'   powered L={LL}: {st2} {dt2:.1f}s', flush=True)
        if st2 in ('OPTIMAL', 'FEASIBLE'):
            print(show([s for s in P.extract() if s[0] in ('K4', 'K5', 'Q', "K4'", "K5'", "Q'")])); print(report(P))
            od = HERE / 'runs' / 'pin'
            pickle.dump({'sol': P.extract(), 'map': mp, 'd': d, 'riders': sorted(P.names[r] for r in P.riders),
                         'merges': [(1, ['K0', 'N']), (3, ["K0'", "N'"])]},
                        open(od / f'm2enum_{mp}_{dd}_s{it}_L{LL}.pkl', 'wb'))
            break
print('skeletons', seen)
