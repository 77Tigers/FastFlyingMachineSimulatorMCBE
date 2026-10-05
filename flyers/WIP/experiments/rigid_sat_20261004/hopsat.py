"""Exact search of hand-off (rider) flyers, e.g. the PL8 record family (bank/pl8/hop_pair_rod_observer):
bodies A (mwmw) and B (wmwm) carry no pistons; four riders hop between them:
  X1 pusher fires s0 (word wwmm: rides A@s2, B@s3)   X2 pusher fires s2 (mmww: rides A@s0, B@s1)
  Y1 sticky fires s0, pulls B@s1 (wwmm)              Y2 sticky fires s2, pulls B@s3 (mmww)
The solver chooses all cells, which carrier each rider rides, power (redstone/rod/observer) and materials.

usage: python hopsat.py LOAD TL WORKERS [BODYWORDS] [RIDERWORDS] [BOX]
  BODYWORDS default mwmw,wmwm ; RIDERWORDS default wwmm,mmww,wwmm,mmww ; BOX default m3:4,m3:3,m3:3
env: KINDS (default g,R,D0..D5,O0..O5,P,S), RIDERKINDS (default P,P,S,S), OBJ=maxload, OUT=dir
"""
import sys, pathlib, itertools, os, pickle, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
from satflyer import FlyerSAT, show, parse_range

if __name__ == '__main__':
    load, tl, wk = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
    bw = (sys.argv[4] if len(sys.argv) > 4 else 'mwmw,wmwm').split(',')
    rw = (sys.argv[5] if len(sys.argv) > 5 else 'wwmm,mmww,wwmm,mmww').split(',')
    bx = (sys.argv[6] if len(sys.argv) > 6 else 'm3:4,m3:3,m3:3').split(',')
    box = list(itertools.product(*[parse_range(r) for r in bx]))
    kinds = tuple(os.environ.get('KINDS', 'g,P,S,R,D0,D1,D2,D3,D4,D5,O0,O1,O2,O3,O4,O5').split(','))
    names = [f'B{i}' for i in range(len(bw))] + [f'R{i}' for i in range(len(rw))]
    rk = os.environ.get('RIDERKINDS', 'P,P,S,S').split(',')   # kind of each rider (pusher / sticky)
    kbs = {nm: [k] for nm, k in zip(names[len(bw):], rk)}
    M = FlyerSAT(bw + rw, box, load, kinds=kinds, leaf=True, maxglue=load, names=names,
                 riders=names[len(bw):], anchor=(0, 0, 0), kinds_by_seg=kbs)
    st, dt = M.solve(tl, wk, objective=os.environ.get('OBJ') or None)
    print(f'hop bodies={bw} riders={rw} load<={load}', st, f'{dt:.1f}s', flush=True)
    if st in ('OPTIMAL', 'FEASIBLE'):
        sol = M.extract(); print(show(sol))
        print('loads', {f'{j}@{t}': M.solver.Value(e) for (j, t), e in M.loadexpr.items()})
        print('riders', [(t, M.names[r], M.names[j]) for (t, r, j), v in M.rc.items() if M.solver.Value(v)])
        od = pathlib.Path(os.environ.get('OUT', HERE / 'runs' / 'hop')); od.mkdir(parents=True, exist_ok=True)
        tag = f'hop_{"-".join(bw)}_{"-".join(rw)}_L{load}'
        pickle.dump(sol, open(od / f'{tag}.pkl', 'wb')); print('saved', od / f'{tag}.pkl')
