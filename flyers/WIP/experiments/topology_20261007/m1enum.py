"""Family 1 (F mmww + rider sticky Q wwmm on K5), skeleton-first search (2026-10-10).
1. Single-chain power-free model (pinfront f1_back boxes, K5/F kinds g,P,S only) at load 7: enumerate N skeletons.
2. Each skeleton: pinned (K5, F cells required, Q fixed), power blocks free within L1 radius R, full power at load 7:
   (a) single chain; (b) mirrored (pinfront.mbuild) at every (map, offset) in OFFS.
usage: python m1enum.py N [R] [TL] [maps]      e.g. python m1enum.py 10 1 20 flipz,rot180
"""
import sys, pathlib, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pinfront import *

N = int(sys.argv[1]); R = int(sys.argv[2]) if len(sys.argv) > 2 else 1
TL = float(sys.argv[3]) if len(sys.argv) > 3 else 20
maps = sys.argv[4].split(',') if len(sys.argv) > 4 else ['flipz', 'flipy', 'rot180', 'anti', 'rot90', 'rot270', 'id']
DS = {'flipz': [(0, z) for z in range(4, 11)], 'flipy': [(y, 0) for y in range(3, 9)],
      'rot180': [(y, z) for y in range(3, 7) for z in range(4, 9)], 'anti': [(y, z) for y in range(3, 7) for z in range(4, 8)],
      'rot90': [(y, z) for y in range(4, 7) for z in range(-1, 3)], 'rot270': [(y, z) for y in range(-2, 2) for z in range(4, 7)],
      'id': [(0, 3), (0, -3), (3, 0), (-3, 0), (2, 2), (-2, 2), (2, -2), (-2, -2)]}
L = 7
tm = [('K2', W4, T[2], None, None, None, None), ('K3', W5, T[3], None, None, None, None), ('K4', W4, T[4], None, None, None, None)]
M = build(VARIANTS['f1_back'](), L, skip=('power',))
import os
CAP = {'K5': int(os.environ.get('K5MAX', 5)), 'F': int(os.environ.get('FMAX', 6))}   # skeleton size caps (room for power)
for nm in ('K5', 'F'):
    i = M.names.index(nm)
    M.m.Add(M.size[i] <= CAP[nm])
    for u in M.boxes[i]:
        for k in M.kinds_of(i):
            if k not in ('g', 'P', 'S'): M.m.Add(M.X[i, u, k] == 0)
for it in range(N):
    st, dt = M.solve(120, 4)
    if st not in ('OPTIMAL', 'FEASIBLE'):
        print(f'skeleton search {it}: {st} -> stop', flush=True); break
    sv = M.solver; sk = {}; lits = []
    for nm in ('K5', 'F', 'Q'):
        i = M.names.index(nm)
        sk[nm] = {u: k for u in M.boxes[i] for k in M.kinds_of(i) if sv.Value(M.X[i, u, k])}
        lits += [M.X[i, u, k] for u, k in sk[nm].items()]
    M.m.AddBoolOr([l.Not() for l in lits])
    print(f'skeleton {it} ({dt:.1f}s): ' + ' | '.join(f'{nm}: ' + ' '.join(f'{u}{k}' for u, k in sorted(c.items()))
                                                     for nm, c in sk.items()), flush=True)
    parts = tm + [('K5', W5, None, nbhd(list(sk['K5']), R), None, sk['K5'], None),
                  ('F', W4, None, nbhd(list(sk['F']), R), None, sk['F'], None),
                  ('Q', W5, None, list(sk['Q']), ['S'], None, None)]
    P = build(parts, L)
    st2, _ = P.solve(TL, 4)
    print(f'   single chain powered L7: {st2}', flush=True)
    cnt = {}
    for mp in maps:
        for dx in (-1, 0, 1):
            for dy, dz in DS[mp]:
                d = (dx, dy, dz)
                P = mbuild(mp, d, L, parts)
                if P is None: cnt['SKEL'] = cnt.get('SKEL', 0) + 1; continue
                try:
                    st3, dt3 = P.solve(TL, 4)
                except Exception as e:
                    st3 = 'ERR ' + str(e)[:40]
                cnt[st3] = cnt.get(st3, 0) + 1
                if st3 != 'INFEASIBLE': print(f'   mirror {mp} {d}: {st3} {dt3:.1f}s', flush=True)
                if st3 in ('OPTIMAL', 'FEASIBLE'):
                    print(show([s for s in P.extract() if s[0].rstrip("'") in ('K4', 'K5', 'F', 'Q')])); print(report(P))
                    pickle.dump({'sol': P.extract(), 'map': mp, 'd': d, 'riders': sorted(P.names[r] for r in P.riders),
                                 'merges': [(1, ['K0', 'N']), (3, ["K0'", "N'"])]},
                                open(HERE / 'runs' / 'pin' / f'm1enum_s{it}_{mp}_{dx}_{dy}_{dz}_L7.pkl', 'wb'))
    print(f'   mirror summary {cnt}', flush=True)
