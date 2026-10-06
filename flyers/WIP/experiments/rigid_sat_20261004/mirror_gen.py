"""General mirrored front (2026-10-06): chain 1 = load-7 start cap (runs/caps/start_L7_pinned.pkl) + alt templates up
to K_last; chain 2 = its image u -> A(u + pos_s(2) E) + d under ANY of the 8 yz symmetries A (front_mirror.YZ) and ANY
offset d (dx != -1 allowed), words shifted by 2 slots; both chains push ONE shared passive mwmw segment F.
Free: the chain segments in `free` (box x +-2, y/z +-r around template origins; images constrained equal), F, riders.
Second move of K_last:  mode V    = rider pusher (fires at that slot, rides any carrier twice)
                        mode S    = rider sticky (pulls at that slot)
                        mode none = no rider (the solver must find another cause, e.g. a twin pull)
Why dx matters: with dx = -1 every chain segment coincides with its mirror image (same x) at slots 1 and 3, so under
flipz nothing of chain 1 can touch chain 2 across the plane at those slots (all earlier runs used dx = -1).
usage: python mirror_gen.py one MAP dx,dy,dz (m = minus, e.g. m1,0,8) MODE LOAD [--last 5] [--free 4,5] [--tl 120] [--wk 8] [--r 2]
       python mirror_gen.py sweep MAPS MODE LOAD [--fmax 4] [--nproc 7] [--wk 2] [--tl 120] [--last 5] [--free 4,5]
"""
import sys, pickle, argparse, itertools, time
from multiprocessing import Pool
from front_mirror import YZ, dmap, shiftword
from cfgsat import *
from satflyer import wpos, fire_slot, Infeasible

E = (1, 0, 0)
START = pickle.load(open(HERE / 'runs' / 'caps' / 'start_L7_pinned.pkl', 'rb'))['sol']
ks = lambda k: k if isinstance(k, str) else f'{k[0]}{k[1]}'


def mapper(mp, d):
    f = YZ[mp]; dm = dmap(mp)
    km = lambda k: k if len(k) == 1 else f'{k[0]}{dm[int(k[1])]}'
    T = lambda u, p: (u[0] + p + d[0], f(u[1], u[2])[0] + d[1], f(u[1], u[2])[1] + d[2])
    return T, km


def second_slot(w):          # the later of two consecutive moves
    return w[1] if w[1] == (w[0] + 1) % 4 else w[0]


VR = 2


def chain(last, free, r, mode):
    """chain-1 parts: (name, word, fixedcells or None, box or None, rider kind or None)"""
    half = []
    for nm, w, cells, m in START:
        if nm in ('K0', 'N', 'K1'):
            half.append((nm, tuple(w), {c: ks(k) for c, k in cells.items()}, None, None))
    for K in range(2, last + 1):
        c, w = tcells(K)
        if K in free:
            o = ORG[K]
            half.append((f'K{K}', w, None, [add(o, (a, b, e)) for a in range(-2, 3) for b in range(-r, r + 1)
                                              for e in range(-r, r + 1)], None))
        else:
            half.append((f'K{K}', w, c, None, None))
    wl = tcells(last)[1]; k = second_slot(wl)
    if mode in ('V', 'S'):
        if mode == 'V': rw = tuple(sorted(((k + 2) % 4, (k + 3) % 4)))      # rests k, k+1
        else: rw = tuple(sorted(((k + 1) % 4, (k + 2) % 4)))                 # rests k-1, k
        o = ORG[last]; xr = range(-3, 2) if mode == 'V' else range(-1, 4)
        half.append(('V', rw, None, [add(o, (a, b, e)) for a in xr for b in range(-VR, VR + 1) for e in range(-VR, VR + 1)],
                     'P' if mode == 'V' else 'S'))
    return half


def fbox(mp, d, last):
    """F box: around both pusher targets of the template K_last and of its image."""
    T, km = mapper(mp, d)
    c, w = tcells(last)
    P = [u for u, k in c.items() if k == 'P'][0]
    Fw = WORDS['mwmw']
    kf = fire_slot(w); f1 = add(P, (wpos(w, kf) + 1 - wpos(Fw, kf), 0, 0))
    w2 = shiftword(w); P2 = T(P, wpos(w, 2)); kf2 = fire_slot(w2)
    f2 = add(P2, (wpos(w2, kf2) + 1 - wpos(Fw, kf2), 0, 0))
    lo = [min(a, b) for a, b in zip(f1, f2)]; hi = [max(a, b) for a, b in zip(f1, f2)]
    box = [(x, y, z) for x in range(lo[0] - 2, hi[0] + 2) for y in range(lo[1] - 2, hi[1] + 3)
           for z in range(lo[2] - 2, hi[2] + 3)]
    return box, f1, f2


PIN = False


def build(mp, d, mode, L, last=5, free=(4, 5), r=2, maxsize=None, skip=()):
    T, km = mapper(mp, d)
    half = chain(last, free, r, mode)
    names, words, fixed, boxes, riders, kbs, img = [], [], [], [], [], {}, {}
    for nm, w, c, b, rk in half:
        names.append(nm); words.append(w); fixed.append((c, None) if c else None); boxes.append(b)
        if rk: riders.append(nm); kbs[nm] = [rk]
    n1 = len(names)
    for i, (nm, w, c, b, rk) in enumerate(half):
        p = wpos(w, 2); names.append(nm + "'"); words.append(shiftword(w))
        if c: fixed.append(({T(u, p): km(k) for u, k in c.items()}, None)); boxes.append(None)
        else: fixed.append(None); boxes.append([T(u, p) for u in b]); img[i] = (n1 + i, p)
        if rk: riders.append(nm + "'"); kbs[nm + "'"] = [rk]
    for t in range(4):                      # fixed skeleton must not overlap in any slot
        occ = set()
        for w_, fx in zip(words, fixed):
            if fx is None: continue
            for c_ in fx[0]:
                cc = (c_[0] + wpos(w_, t), c_[1], c_[2])
                if cc in occ: return 'SKEL_OVERLAP'
                occ.add(cc)
    names.append('F'); words.append(WORDS['mwmw']); fixed.append(None); boxes.append(fbox(mp, d, last)[0])
    ms = None
    if maxsize:
        ms = [maxsize.get(nm.rstrip("'")) for nm in names]
    must = None
    if PIN:
        if PIN == 'core':   # only the chain mechanics: sticky, pusher and the origin glue (pushed + pulled cell)
            must = {f'K{K}': {u: k for u, k in tcells(K)[0].items() if k in ('S', 'P') or u == ORG[K]} for K in free}
        else:
            must = {f'K{K}': {u: k for u, k in tcells(K)[0].items() if PIN == 'full' or k != 'R'} for K in free}
    try:
        M = FlyerSAT(words, None, L, kinds=KALL, leaf=True, maxglue=L - 1, fixed=fixed, names=names, boxes=boxes,
                     riders=riders, kinds_by_seg=kbs, merges=[(1, ['K0', 'N']), (3, ["K0'", "N'"])], maxsize=ms,
                     must=must, skip=skip)
    except Infeasible:
        return 'TRIV_INFEASIBLE'
    for i, (j, p) in img.items():
        for u in boxes[i]:
            for k in M.kinds_of(i):
                M.m.Add(M.X[i, u, k] == M.X[j, T(u, p), km(k)])
    return M


def solve_one(args):
    mp, d, mode, L, last, free, r, tl, wk = args[:9]
    global VR, PIN
    VR = args[9] if len(args) > 9 else VR
    PIN = args[11] if len(args) > 11 else PIN
    obj = args[10] if len(args) > 10 else None
    t0 = time.time()
    M = build(mp, d, mode, L, last, free, r)
    if isinstance(M, str): return args, M, time.time() - t0, None
    st, dt = M.solve(tl, wk, objective=obj)
    rep = None
    if st in ('OPTIMAL', 'FEASIBLE'):
        sol = M.extract()
        od = HERE / 'runs' / 'gen'; od.mkdir(parents=True, exist_ok=True)
        tag = f'gen_{mp}_{d[0]}_{d[1]}_{d[2]}_{mode}_L{L}_last{last}'
        pickle.dump({'sol': sol, 'map': mp, 'd': d, 'riders': sorted(M.names[x] for x in M.riders),
                     'merges': [(1, ['K0', 'N']), (3, ["K0'", "N'"])]}, open(od / f'{tag}.pkl', 'wb'))
        rep = report(M) + '\n' + show(sol)
    return args, st, dt, rep


def candidates(maps, last, fmax, dxr=range(-3, 2)):
    out = []
    for mp in maps:
        for dx in dxr:
            for dy in range(-14, 15):
                for dz in range(-14, 15):
                    box, f1, f2 = fbox(mp, (dx, dy, dz), last)
                    if sum(abs(a - b) for a, b in zip(f1, f2)) > fmax: continue
                    out.append((mp, (dx, dy, dz), sum(abs(a - b) for a, b in zip(f1, f2))))
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd'); ap.add_argument('map'); ap.add_argument('a3'); ap.add_argument('a4'); ap.add_argument('a5', nargs='?')
    ap.add_argument('--last', type=int, default=5); ap.add_argument('--free', default=None)
    ap.add_argument('--tl', type=float, default=120); ap.add_argument('--wk', type=int, default=8)
    ap.add_argument('--r', type=int, default=2); ap.add_argument('--fmax', type=int, default=4)
    ap.add_argument('--nproc', type=int, default=7); ap.add_argument('--log', default=None)
    ap.add_argument('--dx', default='-3,1'); ap.add_argument('--vr', type=int, default=2); ap.add_argument('--obj', default=None); ap.add_argument('--pin', default=None, help='core | noR | full: free K must contain these template cells')
    a = ap.parse_args()
    free = tuple(int(v) for v in a.free.split(',')) if a.free else (a.last - 1, a.last)
    VR = a.vr
    if a.cmd == 'one':
        d = tuple(int(v) for v in a.a3.replace('m', '-').split(','))
        args, st, dt, rep = solve_one((a.map, d, a.a4, int(a.a5), a.last, free, a.r, a.tl, a.wk, a.vr, a.obj, a.pin))
        print(a.map, d, a.a4, a.a5, st, round(dt, 1), flush=True)
        if rep: print(rep)
    else:
        mode, L = a.a3, int(a.a4)
        maps = list(YZ) if a.map == 'all' else a.map.split(',')
        lo, hi = (int(v) for v in a.dx.replace('m', '-').split(','))
        cands = candidates(maps, a.last, a.fmax, range(lo, hi + 1))
        cands.sort(key=lambda c: c[2])
        print('candidates', len(cands), flush=True)
        log = open(a.log or HERE / 'runs' / f'gen_{mode}_L{L}_last{a.last}.log', 'a'); cnt = {}
        jobs = [(mp, d, mode, L, a.last, free, a.r, a.tl, a.wk, a.vr, a.obj, a.pin) for mp, d, _ in cands]
        with Pool(a.nproc) as pool:
            for args, st, dt, rep in pool.imap_unordered(solve_one, jobs):
                cnt[st] = cnt.get(st, 0) + 1
                log.write(f'{args[0]} {args[1]} {args[2]} L{args[3]} {st} {dt:.1f}\n'); log.flush()
                if rep: print('FOUND', args[0], args[1], st, '\n' + rep, flush=True)
                if sum(cnt.values()) % 25 == 0: print(cnt, flush=True)
        print('done', cnt, flush=True)
