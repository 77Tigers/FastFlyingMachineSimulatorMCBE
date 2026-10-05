"""Diagnose the reasoned mirror design with everything fixed except rider V (dropped; K5's slot-3 move excused)."""
import sys, pickle
from front_mirror import *
from satflyer import show
mp, d = sys.argv[1], tuple(int(v) for v in sys.argv[2].split(','))
fcells = eval(sys.argv[3])            # dict of F cells
f = YZ[mp]; dm = dmap(mp)
km = lambda k: k if len(k) == 1 else f'{k[0]}{dm[int(k[1])]}'
T = lambda u, p: add((u[0] + p, *f(u[1], u[2])), d)
st = pickle.load(open(HERE / 'runs' / 'caps' / 'start_L7_pinned.pkl', 'rb'))['sol']
ks = lambda k: k if isinstance(k, str) else f'{k[0]}{k[1]}'
segs = [(nm, tuple(w), {c: ks(k) for c, k in cells.items()}) for nm, w, cells, m in st if nm in ('K0','N','K1','K2','K3','K4')]
c5, w5 = tcells(5); segs.append(('K5', w5, c5))
names, words, fixed = [], [], []
for nm, w, c in segs:
    names.append(nm); words.append(w); fixed.append((c, None))
for nm, w, c in segs:
    p = wpos(w, 2); names.append(nm + "'"); words.append(shiftword(w)); fixed.append(({T(u, p): km(k) for u, k in c.items()}, None))
names.append('F'); words.append(WORDS['mwmw']); fixed.append((fcells, None))
skip = tuple(sys.argv[4].split(',')) if len(sys.argv) > 4 else ('softcause',)
M = FlyerSAT(words, None, 7, kinds=KALL, leaf=True, maxglue=12, fixed=fixed, names=names,
             merges=[(1, ['K0', 'N']), (3, ["K0'", "N'"])], skip=skip,
             open_segs={names.index('K5'): {'ext_pull'}, names.index("K5'"): {'ext_pull'}})
st_, dt = M.solve(60, 16, objective='softcause' if 'softcause' in skip else None)
print(skip, st_)
if st_ in ('OPTIMAL', 'FEASIBLE') and 'softcause' in skip:
    print('missing causes', [(M.names[j], t) for (j, t), b in M.softcause.items() if not M.solver.Value(b)])
