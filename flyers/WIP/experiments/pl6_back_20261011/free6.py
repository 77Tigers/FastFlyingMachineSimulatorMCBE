"""Fully free merged start cap at load L: K0 (mmww), N (wmmw), K1 (wwmm) free in boxes (no template cells required),
merge K0+N at slot 1, K2..K4 alt templates (K4 = front boundary), materials free.  usage: python free6.py L TL WK [r]"""
import sys, pickle, time
from back6 import FlyerSAT, WORDS, show, tcells, report, BND_FRONT, KALL, cube, HERE
L, tl, wk = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]); r = int(sys.argv[4]) if len(sys.argv) > 4 else 2
names = ['K0', 'N', 'K1', 'K2', 'K3', 'K4']
words = [WORDS['mmww'], WORDS['wmmw'], WORDS['wwmm'], tcells(2)[1], tcells(3)[1], tcells(4)[1]]
fixed = [None, None, None, (tcells(2)[0], None), (tcells(3)[0], None), (tcells(4)[0], None)]
boxes = [cube((0, 0, 0), range(-2, 1), r), cube((2, 0, 0), range(-1, 3), r), cube((3, 0, 0), range(-2, 2), r), None, None, None]
M = FlyerSAT(words, None, L, kinds=KALL, leaf=True, maxglue=L - 1, fixed=fixed, names=names, boxes=boxes,
             open_segs={5: BND_FRONT}, merges=[(1, ['K0', 'N'])], anchor=None, leafrod=True)
M.m.Add(M.X[0, (0, 0, 0), 'g'] == 1)     # translation anchor for K0
t0 = time.time(); st, dt = M.solve(tl, wk); print('L', L, 'r', r, st, f'{dt:.1f}s', flush=True)
if st in ('OPTIMAL', 'FEASIBLE'):
    sol = M.extract(); print(show(sol)); print(report(M), flush=True)
    pickle.dump({'sol': sol}, open(HERE / 'runs' / f'free6_L{L}_r{r}.pkl', 'wb'))
