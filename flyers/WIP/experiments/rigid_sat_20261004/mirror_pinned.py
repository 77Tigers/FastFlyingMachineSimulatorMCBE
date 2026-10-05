"""Last pinned attempt (2026-10-05): mirrored front with K4, K5 = alt TEMPLATE cells + at most ONE extra block each
(so K + rider <= 7), rider V free, shared mwmw F free (box, <= 7), start caps + K2, K3 fixed, mirror flipz offset d.
usage: python mirror_pinned.py TL WORKERS d1 [d2 ...]   (d as dx,dy,dz)"""
import sys, pickle
from front_mirror import *
from satflyer import show
tl, wk = float(sys.argv[1]), int(sys.argv[2])
st = pickle.load(open(HERE / 'runs' / 'caps' / 'start_L7_pinned.pkl', 'rb'))['sol']
ks = lambda k: k if isinstance(k, str) else f'{k[0]}{k[1]}'
for dstr in sys.argv[3:]:
    d = tuple(int(v) for v in dstr.split(','))
    f = YZ['flipz']; dm = dmap('flipz')
    km = lambda k: k if len(k) == 1 else f'{k[0]}{dm[int(k[1])]}'
    T = lambda u, p: add((u[0] + p, *f(u[1], u[2])), d)
    half = [(nm, tuple(w), {c: ks(k) for c, k in cells.items()}, None) for nm, w, cells, m in st if nm in ('K0', 'N', 'K1', 'K2', 'K3')]
    for K in (4, 5):
        c, w = tcells(K)
        half.append((f'K{K}', w, None, [add(ORG[K], (dx, dy, dz)) for dx in range(-2, 3) for dy in range(-2, 3) for dz in range(-2, 3)]))
    half.append(('V', WORDS['wmmw'], None, [add(ORG[5], (dx, dy, dz)) for dx in range(-3, 1) for dy in range(-2, 3) for dz in range(-2, 3)]))
    names, words, fixed, boxes, img = [], [], [], [], {}
    for nm, w, c, b in half:
        names.append(nm); words.append(w); fixed.append((c, None) if c else None); boxes.append(b)
    n1 = len(names)
    for i, (nm, w, c, b) in enumerate(half):
        p = wpos(w, 2); names.append(nm + "'"); words.append(shiftword(w))
        if c: fixed.append(({T(u, p): km(k) for u, k in c.items()}, None)); boxes.append(None)
        else: fixed.append(None); boxes.append([T(u, p) for u in b]); img[i] = (n1 + i, p)
    names.append('F'); words.append(WORDS['mwmw']); fixed.append(None)
    boxes.append([(x, y, z) for x in range(11, 15) for y in range(0, 6) for z in range(0, 9)])
    maxsize = [None] * len(names)
    for nm in ('K4', 'K5'): maxsize[names.index(nm)] = 6
    try:
        M = FlyerSAT(words, None, 7, kinds=KALL, leaf=True, maxglue=6, fixed=fixed, names=names, boxes=boxes,
                     riders=['V', "V'"], kinds_by_seg={'V': ['P'], "V'": ['P']}, maxsize=maxsize,
                     must={'K4': tcells(4)[0], 'K5': tcells(5)[0]}, merges=[(1, ['K0', 'N']), (3, ["K0'", "N'"])])
        for i, (j, p) in img.items():
            for u in boxes[i]:
                for k in M.kinds_of(i):
                    M.m.Add(M.X[i, u, k] == M.X[j, T(u, p), km(k)])
    except Exception as e:
        print(d, 'ERR', e, flush=True); continue
    s_, dt = M.solve(tl, wk)
    print(d, s_, round(dt, 1), flush=True)
    if s_ in ('OPTIMAL', 'FEASIBLE'):
        sol = M.extract(); print(show(sol)); print(report(M))
        pickle.dump({'sol': sol, 'map': 'flipz', 'd': d, 'riders': ['V', "V'"], 'merges': [(1, ['K0', 'N']), (3, ["K0'", "N'"])]},
                    open(HERE / 'runs' / f'mirror_pinned_{d[0]}_{d[1]}_{d[2]}.pkl', 'wb'))
        break
