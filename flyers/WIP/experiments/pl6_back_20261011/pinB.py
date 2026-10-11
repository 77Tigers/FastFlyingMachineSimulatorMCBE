"""Lead B pinned: K0/N = 7b minus relay (fixed), K1 and K2 free (any cells, <= L blocks), K3, K4 templates, load L."""
import sys, pickle
from back6 import FlyerSAT, WORDS, show, tcells, report, BND_FRONT, KALL, cube, HERE, K0, N
L, tl, wk = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]); r = int(sys.argv[4]) if len(sys.argv) > 4 else 2
names = ['K0', 'N', 'K1', 'K2', 'K3', 'K4']
words = [WORDS['mmww'], WORDS['wmmw'], WORDS['wwmm'], tcells(2)[1], tcells(3)[1], tcells(4)[1]]
fixed = [(K0, None), (N, None), None, None, (tcells(3)[0], None), (tcells(4)[0], None)]
boxes = [None, None, cube((3, 0, 0), range(-2, 2), r), cube((4, 1, 1), range(-2, 2), r), None, None]
M = FlyerSAT(words, None, L, kinds=KALL, leaf=True, maxglue=L - 1, fixed=fixed, names=names, boxes=boxes,
             open_segs={5: BND_FRONT}, merges=[(1, ['K0', 'N'])], leafrod=True)
st, dt = M.solve(tl, wk); print('pinB L', L, 'r', r, st, f'{dt:.1f}s', flush=True)
if st in ('OPTIMAL', 'FEASIBLE'):
    sol = M.extract(); print(show(sol)); print(report(M), flush=True)
    pickle.dump({'sol': sol}, open(HERE / 'runs' / f'pinB_L{L}_r{r}.pkl', 'wb'))
