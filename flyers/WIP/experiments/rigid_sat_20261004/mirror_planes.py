"""[mirror_planes] mirror_literal.py with the mirror offset d as a 5th CLI argument 'dx,dy,dz' (default -1,0,8).
Prints SKEL_OVERLAP and exits if the fixed skeleton (chain 1 + its image) overlaps in some slot. In F-free modes F's box
is widened by the (dy, dz-8) shift so it can sit between the two chains. Original docstring follows.
User's literal plan on start7_front9 (2026-10-05): drop F's observer and rider M, mirror z -> 8 - z (flipz,
d = (-1,0,8)) with a half-cycle shift, shared mwmw F = glue (13,2,2..6) + redstone (12,2,2), (12,2,6).
modes: fixed (K4, K5, V as in start7_front9) | free (K4/K5 boxes + V free) | twin (no V: the twins may pull each
other) | suffix 'F' = F free in a box, 'K3' anywhere in the name = K3 free too (e.g. freeF, twinF, freeK3F).
usage: python mirror_planes.py MODE LOAD [TL WORKERS [dx,dy,dz]]   (writes runs/mirror_planes_MODE_LLOAD_dx_dy_dz.pkl if solved)"""
import sys, pickle
from front_mirror import *
from satflyer import show
mode, L = sys.argv[1], int(sys.argv[2])
mp = 'flipz'
d = tuple(int(v) for v in sys.argv[5].split(',')) if len(sys.argv) > 5 else (-1, 0, 8)
F = {(13, 2, z): 'g' for z in range(2, 7)}; F[(12, 2, 2)] = 'R'; F[(12, 2, 6)] = 'R'
f = YZ[mp]; dm = dmap(mp)
km = lambda k: k if len(k) == 1 else f'{k[0]}{dm[int(k[1])]}'
T = lambda u, p: add((u[0] + p, *f(u[1], u[2])), d)
src = pickle.load(open(HERE / 'runs' / 'assembled' / 'start7_front9.pkl', 'rb'))['sol']
ks = lambda k: k if isinstance(k, str) else f'{k[0]}{k[1]}'
by = {nm: (tuple(w), {c: ks(k) for c, k in cells.items()}) for nm, w, cells, m in src}
half = []
SEGS = ('K0', 'N', 'K1', 'K2', 'K3', 'K4', 'K5') + (() if mode.startswith('twin') else ('V',))
FREE = ('K4', 'K5', 'V') + (('K3',) if 'K3' in mode else ())
for nm in SEGS:
    w, c = by[nm]
    if mode != 'fixed' and nm in FREE:
        org = c and list(c)[0]
        cx = sum(u[0] for u in c) // len(c); cy = sum(u[1] for u in c) // len(c); cz = sum(u[2] for u in c) // len(c)
        r = 1 if nm == 'V' else 2
        half.append((nm, w, None, [(cx + a, cy + b, cz + e) for a in range(-2, 3) for b in range(-r, r + 1) for e in range(-r, r + 1)]))
    else:
        half.append((nm, w, c, None))
names, words, fixed, boxes, img = [], [], [], [], {}
for nm, w, c, b in half:
    names.append(nm); words.append(w); fixed.append((c, None) if c else None); boxes.append(b)
n1 = len(names)
for i, (nm, w, c, b) in enumerate(half):
    p = wpos(w, 2); names.append(nm + "'"); words.append(shiftword(w))
    if c: fixed.append(({T(u, p): km(k) for u, k in c.items()}, None)); boxes.append(None)
    else: fixed.append(None); boxes.append([T(u, p) for u in b]); img[i] = (n1 + i, p)
# skeleton overlap check: every fixed segment cell (all slots) must be disjoint
for t in range(4):
    occ = set()
    for w_, fx in zip(words, fixed):
        if fx is None: continue
        for c_ in fx[0]:
            cc = (c_[0] + wpos(w_, t), c_[1], c_[2])
            if cc in occ:
                print(mode, 'L', L, 'SKEL_OVERLAP', 0, 'd', d, 'slot', t, 'cell', cc, flush=True); sys.exit(0)
            occ.add(cc)
names.append('F'); words.append(WORDS['mwmw'])
if mode.endswith('F'):
    ey, ez = d[1], d[2] - 8
    fixed.append(None); boxes.append([(x, y, z) for x in range(11, 15) for y in range(min(0, ey), 5 + max(0, ey))
                                      for z in range(1 + min(0, ez), 8 + max(0, ez))])
else:
    fixed.append((F, None)); boxes.append(None)
M = FlyerSAT(words, None, L, kinds=KALL, leaf=True, maxglue=L - 1 if mode != 'fixed' else 12, fixed=fixed, names=names,
             boxes=boxes, riders=[r for r in ('V', "V'") if r in names], kinds_by_seg={r: ['P'] for r in ('V', "V'") if r in names},
             merges=[(1, ['K0', 'N']), (3, ["K0'", "N'"])])
for i, (j, p) in img.items():
    for u in boxes[i]:
        for k in M.kinds_of(i):
            M.m.Add(M.X[i, u, k] == M.X[j, T(u, p), km(k)])
st_, dt = M.solve(float(sys.argv[3]) if len(sys.argv) > 3 else 900, int(sys.argv[4]) if len(sys.argv) > 4 else 16, objective='maxload' if mode != 'fixed' else None)
print(mode, 'L', L, st_, round(dt, 1), 'd', d, flush=True)
if st_ in ('OPTIMAL', 'FEASIBLE'):
    print(report(M).split('\n')[0])
    sol = M.extract()
    for nm, w, c, m in sol:
        if nm in ('K4', 'K5', 'V', 'F'): print(nm, len(c), sorted(c.items()))
    pickle.dump({'sol': sol, 'map': mp, 'd': d, 'riders': ['V', "V'"], 'merges': [(1, ['K0', 'N']), (3, ["K0'", "N'"])]},
                open(HERE / 'runs' / f'mirror_planes_{mode}_L{L}_{d[0]}_{d[1]}_{d[2]}.pkl', 'wb'))
