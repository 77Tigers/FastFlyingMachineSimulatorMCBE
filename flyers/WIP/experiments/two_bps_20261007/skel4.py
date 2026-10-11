"""Pinned search of the 4-body chain-B caps-only flyer (user paper caps, no middles), NS=5:
  R{2,4}: P0 pushes K0 @0            K0{0,1}: P3 pushes K1 @3, P2 pushes F @2, S3 pulls R @4
  K1{3,4}: S0 pulls K0 @1, S1 pulls R @2, P0 pushes F @0      F{0,2}: S3 pulls K1 @4
Pins: K0 glue G=(1,0,0); R.P0 at (0,0,0); K1.S0 at (4,0,0) (both moves of K0 on G); K0's P3/P2/S3 on lateral
faces of G (all 24 assignments). Everything else free in boxes; exact piston plan enforced.
usage: python skel4.py L [--tl 120] [--workers 4] [--only i] [--r 2]
"""
import sys, pathlib, itertools, pickle, argparse
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from satflyer5 import FlyerSAT, show, to_flyer, Infeasible

NS = 5
WORDS = [(2, 4), (0, 1), (3, 4), (0, 2)]
NAMES = ['R', 'K0', 'K1', 'F']
PLAN = {0: ['P0'], 1: ['P2', 'P3', 'S3'], 2: ['S0', 'S1', 'P0'], 3: ['S3']}
LAT = [(0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]


def assignments():
    out = []
    for perm in itertools.permutations(LAT, 3):
        out.append(dict(zip(['P3', 'P2', 'S3'], [(1,) + p[1:] for p in perm])))
    return out


def build(L, asg, r, extra_must=None):
    kinds = ['g', 'R'] + [f'D{q}' for q in range(6)] + [f'O{q}' for q in range(6)]
    yz = range(-r, r + 1)
    boxes = [list(itertools.product(range(-2, 3), yz, yz)), list(itertools.product(range(-1, 3), yz, yz)),
             list(itertools.product(range(1, 7), yz, yz)), list(itertools.product(range(2, 8), yz, yz))]
    kbs = {NAMES[i]: kinds + ks for i, ks in PLAN.items()}
    must = {'R': {(0, 0, 0): 'P0'}, 'K0': {(1, 0, 0): 'g', **{c: k for k, c in asg.items()}}, 'K1': {(4, 0, 0): 'S0'}}
    # derived target glue: K1 glue = P3 + 3E ; F glue = P2 + 2E ; R glue = S3 - E
    p3, p2, s3 = asg['P3'], asg['P2'], asg['S3']
    must['K1'][(p3[0] + 3, p3[1], p3[2])] = 'g'
    must['F'] = {(p2[0] + 2, p2[1], p2[2]): 'g'}
    must['R'][(s3[0] - 1, s3[1], s3[2])] = 'g'
    for nm, c in (extra_must or {}).items(): must.setdefault(nm, {}).update(c)
    S = FlyerSAT(WORDS, None, L, NS=NS, kinds=kinds, leaf=True, maxglue=8, names=NAMES, boxes=boxes,
                 kinds_by_seg=kbs, must=must)
    for i, ks in PLAN.items():
        for k in ks: S.m.Add(sum(S.X[i, u, k] for u in S.boxes[i]) == 1)
    return S


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('L', type=int); ap.add_argument('--tl', type=float, default=120)
    ap.add_argument('--workers', type=int, default=4); ap.add_argument('--only', type=int, default=-1)
    ap.add_argument('--r', type=int, default=2); ap.add_argument('--obj', default='none'); ap.add_argument('--part', default='0/1')
    a = ap.parse_args()
    odir = HERE / 'runs' / 'skel4'; odir.mkdir(parents=True, exist_ok=True)
    pi, pn = (int(z) for z in a.part.split('/'))
    for i, asg in enumerate(assignments()):
        if a.only >= 0 and i != a.only: continue
        if i % pn != pi: continue
        try:
            S = build(a.L, asg, a.r)
        except Infeasible as e:
            print(i, asg, 'TRIV', e, flush=True); continue
        st, dt = S.solve(a.tl, a.workers, objective=(None if a.obj == 'none' else a.obj))
        print(i, asg, st, round(dt, 1), flush=True)
        if st in ('OPTIMAL', 'FEASIBLE'):
            sol = S.extract(); ld = S.loads(); ml = max(ld.values())
            print(show(sol)); print(S.causes()); print(ld, flush=True)
            tag = f'cap4_L{ml}_a{i}'
            pickle.dump({'sol': sol, 'riders': [], 'merges': [], 'asg': asg}, open(odir / f'{tag}.pkl', 'wb'))
            to_flyer(sol, ml, NS).save(str(odir / f'{tag}.flyer'))
            print('saved', tag, flush=True)
