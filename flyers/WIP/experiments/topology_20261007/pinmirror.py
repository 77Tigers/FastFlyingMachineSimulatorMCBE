"""Mirrored versions of the two families (2026-10-09), built with pinfront.mbuild (no shared F; start caps included).
usage: python pinmirror.py MODE L MAP DX,DY,DZ [--obj maxload] [--tl 300] [--wk 4]
  MODE: bank   -- validation: banked PL8 (K4, K5, V, shared F fixed) must be FEASIBLE at 8, INFEASIBLE at 7
        m1     -- family 1 mirrored: K5 (wwmm, must hold g (11,2,3)), F (mmww), rider sticky Q (wwmm); Q may ride
                  any wwmm body at slots 2,3 (K5, K3 or the twin F')
        m2     -- family 2 mirrored: K4 (mmww, must hold g (8,2,2)), K5 (wwmm, must hold g (11,2,3)), rider sticky Q
                  (mmww) riding any mmww body at slots 0,1 (K4, or twin K5'/K3'); no F
  DX etc may use m for minus (m1,0,8).
"""
import sys, pathlib, pickle, argparse, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pinfront import *

ap = argparse.ArgumentParser()
ap.add_argument('mode'); ap.add_argument('L', type=int); ap.add_argument('map'); ap.add_argument('d')
ap.add_argument('--obj', default=None); ap.add_argument('--tl', type=float, default=300)
ap.add_argument('--wk', type=int, default=4); ap.add_argument('--save', action='store_true')
ap.add_argument('--r', type=int, default=1); ap.add_argument('--skip', default='')
ap.add_argument('--powmiss', default='', help='comma list of segments whose pistons may take power from outside')
ap.add_argument('--qk5', action='store_true', help='m2: force Q to pull K5 and its image to pull K5 image')
A = ap.parse_args()
d = tuple(int(v) for v in A.d.replace('m', '-').split(','))
RS = HERE.parent / 'rigid_sat_20261004'
ks = lambda k: k if isinstance(k, str) else f'{k[0]}{k[1]}'
tm = [('K2', W4, T[2], None, None, None, None), ('K3', W5, T[3], None, None, None, None)]
extra = ()
if A.mode == 'bank':
    B = {nm: (w, {c: ks(k) for c, k in cells.items()}) for nm, w, cells, m in
         pickle.load(open(RS / 'runs' / 'assembled' / 'mirror_freeF_L8.pkl', 'rb'))['sol']}
    parts = tm + [('K4', W4, B['K4'][1], None, None, None, None), ('K5', W5, B['K5'][1], None, None, None, None),
                  ('V', 'wmmw', B['V'][1], None, ['P'], None, None)]
    extra = [('F', 'mwmw', B['F'][1], None, None, None, None)]
elif A.mode == 'm1':
    k5box = sorted(set(nbhd(list(T[5]), A.r) + cube((12, 0, 1), (15, 4, 5))))
    fbox = sorted(set(nbhd(list(F6), A.r) + cube((12, 1, 1), (15, 5, 5))))
    parts = tm + [('K4', W4, T[4], None, None, None, None),
                  ('K5', W5, None, k5box, None, {(11, 2, 3): 'g'}, None),
                  ('F', W4, None, fbox, None, None, None),
                  ('Q', W5, None, cube((12, 0, 0), (16, 5, 6)), ['S'], None, None)]
elif A.mode == 'm2pin':   # skeleton of runs/pin/m2q_rot180_m1_5_7_L7_nopower.log pinned, power blocks free (r=A.r)
    k4 = {(8, 0, 2): 'S', (8, 1, 2): 'g', (8, 1, 3): 'P', (8, 2, 2): 'g'}
    k5 = {(10, 2, 3): 'g', (10, 3, 3): 'g', (11, 1, 2): 'S', (11, 1, 3): 'g', (11, 2, 3): 'g', (12, 2, 3): 'g'}
    q = (11, 3, 3)
    parts = tm + [('K4', W4, None, nbhd(list(k4), A.r), None, k4, None),
                  ('K5', W5, None, nbhd(list(k5), A.r), None, k5, A.L - 1),
                  ('Q', W4, None, [q], ['S'], None, None)]
elif A.mode == 'm2':
    parts = tm + [('K4', W4, None, nbhd(list(T[4]), A.r), None, {(8, 2, 2): 'g'}, None),
                  ('K5', W5, None, sorted(set(nbhd(list(T[5]), A.r) + cube((8, 0, 1), (12, 4, 5)))), None,
                   {(11, 2, 3): 'g'}, None),
                  ('Q', W4, None, cube((8, 0, 0), (13, 5, 6)), ['S'], None, None)]
t0 = time.time()
M = mbuild(A.map, d, A.L, parts, extra=extra, opens={n: {'powmiss'} for n in A.powmiss.split(',') if n}, skip=tuple(x for x in A.skip.split(',') if x))
if M is None:
    print(A.mode, A.map, d, 'SKEL_OVERLAP', flush=True); sys.exit()
if A.qk5:   # Q's sticky pulls at its ret slot the cell 2 behind its extended position = K5 glue (slot-0 frames)
    from psat import wpos
    for q, k5 in (('Q', 'K5'), ("Q'", "K5'")):
        iq, ik = M.names.index(q), M.names.index(k5)
        kq = [t for t in range(4) if M.ph[iq][t] == 'ret'][0]
        for u in M.boxes[iq]:
            v = (u[0] + M.sh[iq][kq] - 2 - M.sh[ik][kq], u[1], u[2])
            M.m.Add(M.x(ik, v, 'g') == 1).OnlyEnforceIf(M.X[iq, u, 'S']) if M.x(ik, v, 'g') is not False else M.m.Add(M.X[iq, u, 'S'] == 0)
st, dt = M.solve(A.tl, A.wk, objective=A.obj)
print(f'{A.mode} L={A.L} {A.map} d={d} obj={A.obj} -> {st} {dt:.1f}s (build {time.time() - t0 - dt:.1f}s)', flush=True)
if st in ('OPTIMAL', 'FEASIBLE'):
    print(show(M.extract())); print(report(M))
    if A.obj == 'maxload': print('max load', int(M.solver.ObjectiveValue()), 'bound', int(M.solver.BestObjectiveBound()))
    if A.save:
        od = HERE / 'runs' / 'pin'; od.mkdir(parents=True, exist_ok=True)
        pickle.dump({'sol': M.extract(), 'map': A.map, 'd': d, 'riders': sorted(M.names[r] for r in M.riders),
                     'merges': [(1, ['K0', 'N']), (3, ["K0'", "N'"])]},
                    open(od / f'mirror_{A.mode}_{A.map}_{A.d}_L{A.L}{"_" + A.obj if A.obj else ""}.pkl', 'wb'))
elif A.obj == 'maxload' and st == 'UNKNOWN':
    print('bound', M.solver.BestObjectiveBound())
