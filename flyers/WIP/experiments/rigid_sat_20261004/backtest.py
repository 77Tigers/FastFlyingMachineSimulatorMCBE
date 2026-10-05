"""Can the solver re-find the saved A8B8 back (fronts open) with A, B freed in boxes? Usage: python backtest.py LOAD TL WORKERS R"""
import sys, pathlib, pickle, itertools, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
import rigid; rigid.LEAF = True
from satflyer import FlyerSAT, show, to_rigid, add
from validate import kindstr
load, tl, wk, r = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
segs = pickle.load(open(HERE.parent / 'rigid_chain_20261003' / 'back_leaf_A8B8_load9.pkl', 'rb'))
fixed, boxes = [], []
for s in segs:
    world = {add(s.origin, c): kindstr(k) for c, k in s.cells.items()}
    if s.name in ('A', 'B'):
        fixed.append(None)
        boxes.append([add(s.origin, (dx, dy, dz)) for dx in range(-2, 4) for dy in range(-r, r + 1) for dz in range(-r, r + 1)])
    else:
        fixed.append((world, s.mat)); boxes.append(None)
names = [s.name for s in segs]
M = FlyerSAT([s.word for s in segs], None, load, leaf=True, maxglue=load - 1, fixed=fixed, names=names, boxes=boxes,
             open_segs={names.index('a2'), names.index('b2')})
t0 = time.time(); st, dt = M.solve(tl, wk, log=False); print(st, round(dt, 1))
if st in ('OPTIMAL', 'FEASIBLE'):
    sol = M.extract(); print(show(sol)); print('rigid.check', rigid.check(to_rigid(sol), ignore={'a2', 'b2'}))
