"""List moving-glue contacts with other segments' blocks (per slot) for a fixed design built like mirror_diag."""
import sys, pickle
from front_mirror import *
mp, d = sys.argv[1], tuple(int(v) for v in sys.argv[2].split(','))
fcells = eval(sys.argv[3])
f = YZ[mp]; dm = dmap(mp)
km = lambda k: k if len(k) == 1 else f'{k[0]}{dm[int(k[1])]}'
T = lambda u, p: add((u[0] + p, *f(u[1], u[2])), d)
st = pickle.load(open(HERE / 'runs' / 'caps' / 'start_L7_pinned.pkl', 'rb'))['sol']
ks = lambda k: k if isinstance(k, str) else f'{k[0]}{k[1]}'
segs = [(nm, tuple(w), {c: ks(k) for c, k in cells.items()}) for nm, w, cells, m in st if nm in ('K0','N','K1','K2','K3','K4')]
c5, w5 = tcells(5); segs.append(('K5', w5, c5))
allsegs = list(segs) + [(nm + "'", shiftword(w), {T(u, wpos(w, 2)): km(k) for u, k in c.items()}) for nm, w, c in segs]
allsegs.append(('F', WORDS['mwmw'], fcells))
for t in range(4):
    world = {}
    for nm, w, c in allsegs:
        for u, k in c.items(): world[(u[0] + wpos(w, t), u[1], u[2])] = (nm, k, t in w)
    for v, (nm, k, mv) in world.items():
        if k != 'g' or not mv: continue
        for dd in D6:
            n = add(v, dd)
            if n in world and world[n][0] != nm:
                o, ok, omv = world[n]
                if nm < o or not omv: print(f's{t} {nm}{"*"} glue {v} touches {o}{"*" if omv else ""} {ok} {n}')
