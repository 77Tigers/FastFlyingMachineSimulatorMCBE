import sys
from modules import *
from satflyer import show
o2i, d = int(sys.argv[1]), tuple(int(x) for x in sys.argv[2].split(','))
sk, opens, free, nbs = front_skeleton(ORIENTS[o2i], d)
for skip in [(), ('power',), ('adh',), ('move',), ('targets',), ('cause',), ('conn',)]:
    names = [x[0] for x in sk]
    fixed = [None if nm in free else (cells, None) for nm, w, org, cells in sk]
    boxes = [box_around(org) if nm in free else None for nm, w, org, cells in sk]
    of = {names.index(k): v for k, v in opens.items()}
    M = FlyerSAT([x[1] for x in sk], None, 14, leaf=True, maxglue=13, fixed=fixed, names=names, boxes=boxes, open_segs=of, skip=skip)
    st, dt = M.solve(30, 16); print(skip, st, round(dt, 1), flush=True)
M = FlyerSAT([x[1] for x in sk], None, 14, leaf=True, maxglue=13, fixed=fixed, names=names, boxes=boxes, open_segs=of, skip=('softcause',))
st, dt = M.solve(60, 16, objective='softcause'); print(st)
if st in ('OPTIMAL', 'FEASIBLE'):
    print('missing', [(M.names[j], t) for (j, t), b in M.softcause.items() if not M.solver.Value(b)])
    print(show(M.extract()))
