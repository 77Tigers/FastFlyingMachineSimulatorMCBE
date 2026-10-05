"""The banked PL8 hand-off flyer (rigid_chain_20261003/pl8/hop_pl8_a.pkl), fixed, must be FEASIBLE at load 8 in
satflyer's rider model and INFEASIBLE at load 7."""
import sys, pathlib, pickle, itertools
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
from satflyer import FlyerSAT
from validate import kindstr
segs = pickle.load(open(HERE.parent / 'rigid_chain_20261003' / 'pl8' / 'hop_pl8_a.pkl', 'rb'))
fixed = [({c: kindstr(k) for c, k in s.cells.items()}, s.mat) for s in segs]
kinds = sorted({k for f, _ in fixed for k in f.values()} | {'g', 'P', 'S', 'R'})
for L in (8, 7):
    M = FlyerSAT([s.word for s in segs], None, L, kinds=kinds, leaf=True, maxglue=12, fixed=fixed,
                 names=[s.name for s in segs], riders=[s.name for s in segs if s.rider])
    st, dt = M.solve(60, 2); print('PL8 record fixed, load', L, st)
    if st in ('OPTIMAL', 'FEASIBLE'):
        print('  carriers', [(t, M.names[r], M.names[j]) for (t, r, j), v in M.rc.items() if M.solver.Value(v)])
