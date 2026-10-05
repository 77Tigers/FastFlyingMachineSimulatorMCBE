"""Rider front cap at load 7 with the end segment's contacts and rider M pinned (2026-10-05).

Chain K2 (boundary), K3 templates; K4, K5 free (boxes); F (mmww, passive end) has g1 = (12,3,3) [pushed by K5's
pusher at s0, template position] and contact c [pushed by rider M at s1] pinned, plus up to EXTRA more free blocks
(power for K5's hub, M's observer, connectors). Rider M (mwwm) pinned at c - E; rider V (wmmw) free.
usage: python front_pinned.py WORKERS TL EXTRA [K5MODE]   K5MODE: free (default) | keep (template cells required)
"""
import sys, time, pickle
from cfgsat import *
from satflyer import D6

E = (1, 0, 0)
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def adj(a, b): return sum(abs(x - y) for x, y in zip(a, b)) == 1

wk, tl, extra = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
k5mode = sys.argv[4] if len(sys.argv) > 4 else 'free'
g1 = (12, 3, 3)
KX = ('g', 'P', 'S', 'R', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'O0', 'O1', 'O2', 'O3', 'O4', 'O5')
cands = []
for d1 in D6:                      # c next to g1, or one connector away
    c1 = add(g1, d1)
    if d1[0] != 0: continue
    cands.append((c1, None))
    for d2 in D6:
        c2 = add(c1, d2)
        if d2[0] != 0 or c2 == g1 or adj(c2, g1): continue
        cands.append((c2, c1))
print('layouts', len(cands), flush=True)
for c, conn in cands:
    M = sub(c, E)
    fpin = {g1: 'g', c: 'g'}
    if conn: fpin[conn] = 'g'
    segs = [('K2', 'tmpl', 2), ('K3', 'tmpl', 3), ('K4', 'free', 4), ('K5', 'free', 5)]
    names, words, fixed, boxes, must = [], [], [], [], {}
    for nm, kind, K in segs:
        names.append(nm)
        cells, w = tcells(K); words.append(w)
        if kind == 'tmpl': fixed.append((cells, None)); boxes.append(None)
        else:
            fixed.append(None)
            boxes.append([add(ORG[K], (dx, dy, dz)) for dx in range(-3, 4) for dy in range(-2, 3) for dz in range(-2, 3)])
            if nm == 'K5' and k5mode == 'keep': must['K5'] = cells
    names.append('F'); words.append(WORDS['mmww']); fixed.append(None)
    boxes.append([add(g1, (dx, dy, dz)) for dx in range(-2, 3) for dy in range(-2, 3) for dz in range(-2, 3)])
    must['F'] = fpin
    names.append('M'); words.append(WORDS['mwwm']); fixed.append(({M: 'P'}, None)); boxes.append(None)
    names.append('V'); words.append(WORDS['wmmw']); fixed.append(None)
    boxes.append([add(ORG[5], (dx, dy, dz)) for dx in range(-3, 1) for dy in range(-2, 3) for dz in range(-2, 3)])
    maxsize = [None, None, None, None, len(fpin) + extra, None, None]
    try:
        Mo = FlyerSAT(words, None, 7, kinds=KX, leaf=True, maxglue=6, fixed=fixed, names=names, boxes=boxes,
                      open_segs={0: BND_BACK}, riders=['M', 'V'], kinds_by_seg={'M': ['P'], 'V': ['P']},
                      must=must, maxsize=maxsize)
    except Exception as e:
        print(c, conn, 'ERR', e, flush=True); continue
    st, dt = Mo.solve(tl, wk)
    print(c, conn, st, f'{dt:.1f}s', flush=True)
    if st in ('OPTIMAL', 'FEASIBLE'):
        sol = Mo.extract(); print(show(sol)); print(report(Mo))
        pickle.dump({'sol': sol, 'riders': ['M', 'V']}, open(HERE / 'runs' / f'front_pinned_{c}_{conn}.pkl'.replace(' ', ''), 'wb'))
