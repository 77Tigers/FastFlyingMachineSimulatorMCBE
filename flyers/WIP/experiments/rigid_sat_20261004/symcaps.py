"""Symmetric two-chain caps (user's 'duplicate + reflection + split jobs' idea), 2026-10-04.

Chain 2 is the image of chain 1 under  T: cell u of segment s  ->  swapyz(u + pos_s(2)*E) + d,  word shifted by -2
slots (mmww <-> wwmm, mwwm <-> wmmw), observers/rods mirrored (+Y <-> +Z). Because the y<->z mirror keeps the alt
chain's staircase direction (1,1), the two chains stay parallel, so the same offset d works at the front and the back.
The solver designs chain 1 only (chain 2 is constrained equal to its image) and the two halves may power each other.

usage: python symcaps.py front|back LOAD TL WORKERS NPROC [dx,dy,dz ...]
"""
import sys, os, itertools, pickle, time, random
from multiprocessing import Pool
from cfgsat import *
from satflyer import wpos


def shiftword(w, k=-2): return tuple(sorted((m + k) % 4 for m in w))


def swap(u): return (u[0], u[2], u[1])


KMAP = {'O2': 'O4', 'O4': 'O2', 'O3': 'O5', 'O5': 'O3', 'D2': 'D4', 'D4': 'D2', 'D3': 'D5', 'D5': 'D3'}


def kmap(k): return KMAP.get(k, k)


def half(side):
    """chain-1 half: list of dicts like cfgsat segs, plus box spec."""
    if side.startswith('front'):
        base = [{'name': 'K2', 'tmpl': 2, 'open': BND_BACK}, {'name': 'K3', 'tmpl': 3}, {'name': 'K4', 'tmpl': 4},
                {'name': 'K5', 'free': 5, 'word': 'wwmm'}, {'name': 'F1', 'free': 6, 'word': 'mmww'}]
        if side == 'front': return base + [rider_seg('M1', 'P', 'mwwm', 6), rider_seg('V1', 'P', 'wmmw', 5)]
        if side == 'front_m': return base + [rider_seg('M1', 'P', 'mwwm', 6)]      # F1 may pull K5 (cross-powered)
        if side == 'front_none': return base                                         # e.g. user's pull-pull pair
        if side == 'front_free4': return base[:2] + [{'name': 'K4', 'free': 4, 'word': 'mmww'}] + base[3:]
    if side == 'backloop':   # no extra segment: K0 and its image K0' may push each other (user's back loop)
        return [{'name': 'K0', 'free': 0, 'word': 'mmww'}, {'name': 'K1', 'free': 1, 'word': 'wwmm'},
                {'name': 'K2', 'tmpl': 2}, {'name': 'K3', 'tmpl': 3}, {'name': 'K4', 'tmpl': 4, 'open': BND_FRONT}]
    return [{'name': 'K0', 'free': 0, 'word': 'mmww'}, {'name': 'K1', 'free': 1, 'word': 'wwmm'},
            {'name': 'K2', 'tmpl': 2}, {'name': 'K3', 'tmpl': 3}, {'name': 'K4', 'tmpl': 4, 'open': BND_FRONT},
            {'name': 'N', 'free': 0, 'word': 'wmmw'}]


def build_sym(side, d, L, box=(-3, 4, 2), kinds=KOBS, merges1=()):
    h = half(side)
    x0, x1, r = box
    names, words, fixed, boxes, opens, riders, kbs = [], [], [], [], {}, [], {}
    cellsets = []
    for s in h:                                   # chain 1
        names.append(s['name'])
        w = WORDS[s['word']] if 'word' in s else tcells(s['tmpl'])[1]
        words.append(w)
        if 'tmpl' in s:
            cells, _ = tcells(s['tmpl']); fixed.append((cells, None)); boxes.append(None); cellsets.append(list(cells))
        else:
            c = centre(s.get('free', s.get('near')))
            b = [add(c, (dx, dy, dz)) for dx in range(x0, x1 + 1) for dy in range(-r, r + 1) for dz in range(-r, r + 1)]
            fixed.append(None); boxes.append(b); cellsets.append(b)
            if 'rider' in s: riders.append(s['name']); kbs[s['name']] = [s['rider']]
        if 'open' in s: opens[len(names) - 1] = s['open']
    n1 = len(h)
    T = {}
    for i, s in enumerate(h):                     # chain 2 = images
        w2 = shiftword(words[i]); p2 = wpos(words[i], 2)
        tf = lambda u, p2=p2: add(swap((u[0] + p2, u[1], u[2])), d)
        T[i] = tf
        names.append(s['name'] + "'"); words.append(w2)
        if fixed[i] is not None:
            fixed.append(({tf(u): kmap(k) for u, k in fixed[i][0].items()}, None)); boxes.append(None)
        else:
            fixed.append(None); boxes.append([tf(u) for u in boxes[i]])
            if s['name'] in riders: riders.append(names[-1]); kbs[names[-1]] = kbs[s['name']]
        if i in opens: opens[len(names) - 1] = opens[i]
    occ = {}
    for i in range(len(names)):
        if fixed[i] is None: continue
        for c in fixed[i][0]:
            if c in occ: return None
            occ[c] = i
    merges = list(merges1) + [(((t - 2) % 4), [a + "'", b + "'"]) for t, (a, b) in merges1]
    M = FlyerSAT(words, None, L, kinds=kinds, leaf=True, maxglue=L - 1, fixed=fixed, names=names, boxes=boxes,
                 open_segs=opens, riders=riders, kinds_by_seg=kbs, merges=merges)
    for i in range(n1):                           # symmetry equalities
        if fixed[i] is not None: continue
        j = n1 + i
        for u in boxes[i]:
            for k in M.kinds_of(i):
                M.m.Add(M.X[i, u, k] == M.X[j, T[i](u), kmap(k)])
    return M


def solve(args):
    side, d, L, tl, wk = args
    t0 = time.time()
    try:
        M = build_sym(side, d, L, merges1=[(1, ('K0', 'N'))] if side == 'back' else ())
    except Exception as e:
        return d, 'ERR ' + repr(e)[:80], 0, None
    if M is None: return d, 'SKEL_OVERLAP', 0, None
    st, dt = M.solve(tl, wk)
    if st in ('OPTIMAL', 'FEASIBLE'):
        sol = M.extract()
        od = HERE / 'runs' / 'sym'; od.mkdir(parents=True, exist_ok=True)
        pickle.dump({'sol': sol, 'side': side, 'd': d, 'riders': sorted(M.names[r] for r in M.riders)},
                    open(od / f'sym_{side}_{d[0]}_{d[1]}_{d[2]}_L{L}.pkl', 'wb'))
        return d, st, time.time() - t0, report(M)
    return d, st, time.time() - t0, None


if __name__ == '__main__':
    side, L, tl, wk, npr = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    if len(sys.argv) > 6:
        offs = [tuple(int(v) for v in a.split(',')) for a in sys.argv[6:]]
    else:
        offs = list(itertools.product(range(-4, 4), range(-4, 5), range(-4, 5)))
        random.Random(1).shuffle(offs)
    print('placements', len(offs), flush=True)
    cnt = {}
    log = open(HERE / 'runs' / f'sym_{side}_L{L}.log', 'a')
    with Pool(npr) as pool:
        for d, st, dt, rep in pool.imap_unordered(solve, [(side, d, L, tl, wk) for d in offs]):
            cnt[st] = cnt.get(st, 0) + 1
            log.write(f'{d} {st} {dt:.1f}\n'); log.flush()
            if rep: print('FOUND', d, st, rep, flush=True)
            if sum(cnt.values()) % 50 == 0: print(cnt, flush=True)
    print('done', cnt, flush=True)
