"""Periodic chain middles at NS slots: K_{i+1} = K_i shifted by v (slot-0 frame), word and fire slots shifted by D.
usage: python chainsym.py WORD0 D L [--M 5] [--r 2] [--xr m2:3] [--vs all|vx,vy,vz] [--tl 60] [--workers 6] [--NS 5]
Prints, for every v, status and (if found) max load of the constrained middles."""
import sys, pathlib, itertools, argparse, pickle, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from satflyer5 import FlyerSAT, pinfo, show, to_flyer

import os
NOSYM = bool(os.environ.get('NOSYM'))

def shiftk(k, d, NS):
    p = pinfo(k)
    if p is None: return k
    return f'{p[0]}{(p[1] + d) % NS}' + ('h' if p[2] == 2 else '')

def build(word0, D, v, M, box0, L, NS=5, kinds=('g', 'R', 'D2', 'D3', 'D4', 'D5', 'D0', 'D1', 'O0', 'O1', 'O2', 'O3', 'O4', 'O5'),
          maxglue=4, holds=(1,), open_ends=True):
    words = [tuple(sorted((w + i * D) % NS for w in word0)) for i in range(M)]
    # K_{i+1}(slot 0) = K_i(slot -D) + v = K_i(slot 0) + v - c_i E, c_i = moves of K_i in slots NS-D..NS-1
    offs = [(0, 0, 0)]
    for i in range(M - 1):
        c = sum(1 for w in words[i] if w >= NS - D)
        o = offs[-1]; offs.append((o[0] + v[0] - c, o[1] + v[1], o[2] + v[2]))
    boxes = [[(u[0] + offs[i][0], u[1] + offs[i][1], u[2] + offs[i][2]) for u in box0] for i in range(M)]
    flags = {'powmiss', 'Ptarget', 'Starget', 'cause_le1'}
    opn = {0: flags, M - 1: flags} if open_ends else {}
    S = FlyerSAT(words, None, L, NS=NS, kinds=kinds, leaf=True, maxglue=maxglue, boxes=boxes,
                 names=[f'K{i}' for i in range(M)], open_segs=opn, holds=holds)
    for i in (range(1, M) if not NOSYM else []):
        for u in box0:
            ui = (u[0] + offs[i][0], u[1] + offs[i][1], u[2] + offs[i][2])
            for k in S.kinds_of(0):
                S.m.Add(S.X[i, ui, shiftk(k, i * D, NS)] == S.X[0, u, k])
    return S, words

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('word0'); ap.add_argument('D', type=int); ap.add_argument('L', type=int)
    ap.add_argument('--M', type=int, default=5); ap.add_argument('--r', type=int, default=2)
    ap.add_argument('--xr', default='m1:2'); ap.add_argument('--vs', default='all')
    ap.add_argument('--tl', type=float, default=60); ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--NS', type=int, default=5); ap.add_argument('--maxglue', type=int, default=4)
    ap.add_argument('--norods', action='store_true'); ap.add_argument('--noobs', action='store_true')
    ap.add_argument('--noR', action='store_true')
    a = ap.parse_args()
    word0 = tuple(int(c) for c in a.word0)
    xa, xb = (int(z) for z in a.xr.replace('m', '-').split(':'))
    box0 = list(itertools.product(range(xa, xb + 1), range(-a.r, a.r + 1), range(-a.r, a.r + 1)))
    kinds = ['g'] + ([] if a.noR else ['R']) + ([] if a.norods else [f'D{d}' for d in range(6)]) + ([] if a.noobs else [f'O{d}' for d in range(6)])
    if a.vs == 'all':
        vs = [(vx, vy, vz) for vx in range(1, 6) for vy in range(-1, 2) for vz in range(-1, 2) if (vy, vz) >= (0, 0) or True]
        # y<->z and sign symmetry: keep vy >= 0, vz >= vy... (box symmetric) -> canonical
        vs = sorted({(vx, abs(vy), abs(vz)) if True else None for vx, vy, vz in vs})
        vs = sorted({(vx, min(vy, vz), max(vy, vz)) for vx, vy, vz in vs})
    else:
        vs = [tuple(int(z) for z in s.replace('m', '-').split(',')) for s in a.vs.split(';')]
    for v in vs:
        t0 = time.time()
        S, words = build(word0, a.D, v, a.M, box0, a.L, NS=a.NS, kinds=kinds, maxglue=a.maxglue)
        st, dt = S.solve(a.tl, a.workers, objective='maxload')
        msg = f'v={v} words={words} -> {st} {dt:.1f}s'
        if st in ('OPTIMAL', 'FEASIBLE'):
            sol = S.extract()
            ld = S.loads(); mid = {k: x for k, x in ld.items() if k[0] not in ('K0', f'K{a.M-1}')}
            msg += f' midload={max(mid.values())} sizes={[len(c) for _, _, c, _ in sol]}'
            print(msg, flush=True)
            print(show(sol[1:2])); print(S.causes()[:12])
            out = HERE / 'runs' / 'chainsym'; out.mkdir(parents=True, exist_ok=True)
            pickle.dump({'sol': sol, 'word0': word0, 'D': a.D, 'v': v}, open(out / f'w{a.word0}_D{a.D}_v{v[0]}{v[1]}{v[2]}_L{a.L}.pkl', 'wb'))
        else:
            print(msg, flush=True)
