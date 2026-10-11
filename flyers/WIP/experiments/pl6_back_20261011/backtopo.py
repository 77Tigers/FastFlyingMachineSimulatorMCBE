"""Back topology enumeration: rear bodies B0..B(n-1) with ANY words (list), K1 (wwmm) free, K2..K4 templates
(K4 = front boundary), automerge (solver picks merges), materials free, load L.
usage: python backtopo.py L N TL WK [--only i/m] [--r 2]   (combos split round-robin: process i of m)"""
import sys, itertools, pickle, time, argparse
from back6 import FlyerSAT, Infeasible, WORDS, show, tcells, report, BND_FRONT, KALL, cube, HERE
ap = argparse.ArgumentParser()
ap.add_argument('L', type=int); ap.add_argument('n', type=int); ap.add_argument('tl', type=float); ap.add_argument('wk', type=int)
ap.add_argument('--only', default='0/1'); ap.add_argument('--r', type=int, default=2)
ap.add_argument('--words', default=None)          # fixed rear words, e.g. mmww,wmmw
ap.add_argument('--riders', type=int, default=0)  # number of piston riders (kind P or S, any word), enumerated
ap.add_argument('--k2free', action='store_true')  # K2 free (box around its template, <= L blocks)
ap.add_argument('--tag', default='')
a = ap.parse_args()
i0, m = map(int, a.only.split('/'))
WL = list(WORDS)
rears = [tuple(a.words.split(','))] if a.words else list(itertools.product(WL, repeat=a.n))
RK = [(w, k) for w in WL for k in 'PS']
combos = [r + tuple(f'{w}:{k}' for w, k in rs) for r in rears for rs in itertools.combinations_with_replacement(RK, a.riders)]
for ci, ws in enumerate(combos):
    if ci % m != i0: continue
    rw = [x for x in ws if ':' in x]; ws_ = [x for x in ws if ':' not in x]
    names = [f'B{i}' for i in range(a.n)] + ['K1', 'K2', 'K3', 'K4'] + [f'R{i}' for i in range(len(rw))]
    words = [WORDS[w] for w in ws_] + [WORDS['wwmm'], tcells(2)[1], tcells(3)[1], tcells(4)[1]] + [WORDS[x.split(':')[0]] for x in rw]
    fixed = [None] * (a.n + 1) + [(tcells(K)[0], None) for K in (2, 3, 4)] + [None] * len(rw)
    boxes = ([cube((0, 0, 0), range(-2, 3), a.r) for _ in range(a.n)] + [cube((3, 0, 0), range(-2, 2), a.r), None, None, None]
             + [cube((1, 0, 0), range(-2, 4), a.r) for _ in rw])
    if a.k2free:
        fixed[a.n + 1] = None; boxes[a.n + 1] = cube((4, 1, 1), range(-2, 2), a.r)
    kbs = {f'R{i}': [x.split(':')[1]] for i, x in enumerate(rw)}
    try:
        M = FlyerSAT(words, None, a.L, kinds=KALL, leaf=True, maxglue=a.L - 1, fixed=fixed, names=names, boxes=boxes,
                     open_segs={a.n + 3: BND_FRONT}, automerge=True, leafrod=True, riders=list(kbs), kinds_by_seg=kbs)
    except Infeasible:
        print(ws, 'TRIV_INFEASIBLE', flush=True); continue
    M.m.Add(M.X[0, (0, 0, 0), 'g'] == 1)
    # B0 is the rearmost body: no other back body below x = 0 (removes duplicates)
    for s in range(1, a.n):
        for u in M.boxes[s]:
            if u[0] < 0:
                for k in M.kinds_of(s): M.m.Add(M.X[s, u, k] == 0)
    st, dt = M.solve(a.tl, a.wk)
    print(ws, st, f'{dt:.1f}s', flush=True)
    if st in ('OPTIMAL', 'FEASIBLE'):
        sol = M.extract(); print(show(sol)); print(report(M), flush=True)
        pickle.dump({'sol': sol, 'words': ws}, open(HERE / 'runs' / f"topo{a.tag}_L{a.L}_{'_'.join(ws).replace(':', '')}.pkl", 'wb'))
