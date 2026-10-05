"""Start cap at load 7 with K0 and N pinned to small hand layouts; only K1 (and optionally 1 extra K0/N block) free.

K0 = gK (0,0,0) g [pulled by K1 at s1] + contact c g [pulled by N at s0] + P1 (0,0,1) [pushes K1 at s2]
     + P2 = gN - 2E [pushes N at s2, carries N at s1 (merged move)]
N  = sticky at c + 2E + glue gN next to it.   K1 free (box), K2..K4 alt templates (K4 boundary).
Enumerates every (c, gN) with the cheap local checks, solves each exactly (rods + observers allowed).
usage: python start_pinned.py WORKERS TL [EXTRA]   EXTRA=1 lets K0 and N each add one block
"""
import sys, itertools, time, pickle
from cfgsat import *
from satflyer import D6

E = (1, 0, 0)
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def adj(a, b): return sum(abs(x - y) for x, y in zip(a, b)) == 1

wk, tl = int(sys.argv[1]), float(sys.argv[2])
extra = len(sys.argv) > 3 and sys.argv[3] == '1'
gK, P1 = (0, 0, 0), (0, 0, 1)
cands = []
for c in [add(gK, d) for d in D6] + [add(add(gK, (0, 0, -1)), d) for d in D6]:
    if c in (gK, P1) or c[0] != 0: continue
    if not (adj(c, gK) or adj(c, (0, 0, -1))): continue
    SN = add(c, (2, 0, 0))
    if add(c, E) in (gK, P1): continue
    for dn in D6:
        if dn[0] != 0: continue
        gN = add(SN, dn); P2 = sub(gN, (2, 0, 0))
        if P2 in (gK, P1, c): continue
        cands.append((c, gN, P2))
cands = sorted(set(cands))
print('layouts', len(cands), flush=True)
KX = ('g', 'P', 'S', 'R', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'O0', 'O1', 'O2', 'O3', 'O4', 'O5')
for c, gN, P2 in cands:
    SN = add(c, (2, 0, 0))
    k0 = {gK: 'g', c: 'g', P1: 'P', P2: 'P'}
    conn = None
    if not adj(c, gK): k0[(0, 0, -1)] = 'g'           # connector when c hangs off (0,0,-1)
    if not (adj(P2, gK) or adj(P2, c) or ((0, 0, -1) in k0 and adj(P2, (0, 0, -1)))): continue
    n = {SN: 'S', gN: 'g'}
    segs = [{'name': 'K1', 'free': 1, 'word': 'wwmm'}, {'name': 'K2', 'tmpl': 2}, {'name': 'K3', 'tmpl': 3},
            {'name': 'K4', 'tmpl': 4, 'open': BND_FRONT}]
    names = ['K0', 'N'] + [s['name'] for s in segs]
    words = [WORDS['mmww'], WORDS['wmmw']] + [WORDS['wwmm'], tcells(2)[1], tcells(3)[1], tcells(4)[1]]
    box1 = [add(ORG[1], (dx, dy, dz)) for dx in range(-3, 5) for dy in range(-2, 3) for dz in range(-2, 3)]
    if extra:
        bk0 = [add(gK, (dx, dy, dz)) for dx in range(-1, 2) for dy in range(-2, 3) for dz in range(-2, 3)]
        bn = [add(SN, (dx, dy, dz)) for dx in range(-1, 2) for dy in range(-2, 3) for dz in range(-2, 3)]
        fixed = [None, None, None, (tcells(2)[0], None), (tcells(3)[0], None), (tcells(4)[0], None)]
        boxes = [bk0, bn, box1, None, None, None]
        must = {'K0': k0, 'N': n}
        maxsize = [len(k0) + 1, len(n) + 1, None, None, None, None]
    else:
        fixed = [(k0, None), (n, None), None, (tcells(2)[0], None), (tcells(3)[0], None), (tcells(4)[0], None)]
        boxes = [None, None, box1, None, None, None]
        must, maxsize = None, None
    try:
        M = FlyerSAT(words, None, 7, kinds=KX, leaf=True, maxglue=6, fixed=fixed, names=names, boxes=boxes,
                     open_segs={5: BND_FRONT}, merges=[(1, ['K0', 'N'])], must=must, maxsize=maxsize)
    except Exception as e:
        print(c, gN, P2, 'ERR', e, flush=True); continue
    t0 = time.time(); st, dt = M.solve(tl, wk)
    print(c, gN, P2, st, f'{dt:.1f}s', flush=True)
    if st in ('OPTIMAL', 'FEASIBLE'):
        sol = M.extract(); print(show(sol)); print(report(M))
        pickle.dump({'sol': sol}, open(HERE / 'runs' / f'start_pinned_{c}_{gN}.pkl'.replace(' ', ''), 'wb'))
