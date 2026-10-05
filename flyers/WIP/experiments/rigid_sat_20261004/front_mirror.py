"""User's idea (2026-10-05): mirror the start7 flyer near its front and share ONE final segment F with word mwmw
(moves at slots 0 and 2): chain 1's last segment K5 (wwmm) pushes F at slot 0, the mirrored chain's K5' (mmww after
the half-cycle shift) pushes F at slot 2. F is passive (no pistons) and can power both hubs; no rider M needed.

chain 1 = load-7 start cap (K0, N, K1 from runs/caps/start_L7_pinned.pkl, fixed) + templates K2..K4 (fixed)
          + K5 free (wwmm) + rider V (P, wmmw: rides K4@1, K5@2, pushes K5@3).
chain 2 = image of chain 1 under  u -> A(u + pos_s(2) E) + d  (A = one of the 8 yz symmetries; words shifted by 2
          slots; directions of observers/rods mapped), with K5'/V' constrained equal to the images of K5/V.
F = free mwmw segment near K6's template origin.
usage: python front_mirror.py LOAD TL WORKERS NPROC [maps]
"""
import sys, itertools, pickle, time, os
from multiprocessing import Pool
from cfgsat import *
from satflyer import wpos, D6

YZ = {'swap': lambda y, z: (z, y), 'anti': lambda y, z: (-z, -y), 'flipy': lambda y, z: (-y, z),
      'flipz': lambda y, z: (y, -z), 'rot180': lambda y, z: (-y, -z), 'rot90': lambda y, z: (-z, y),
      'rot270': lambda y, z: (z, -y), 'id': lambda y, z: (y, z)}


def dmap(name):
    f = YZ[name]
    out = {0: 0, 1: 1}
    for i in range(2, 6):
        v = D6[i]; y, z = f(v[1], v[2]); out[i] = D6.index((0, y, z))
    return out


def shiftword(w, k=-2): return tuple(sorted((m + k) % 4 for m in w))


def build(mapname, d, L, kinds=KALL, free4=False, fpin=None):
    f = YZ[mapname]; dm = dmap(mapname)
    km = lambda k: k if len(k) == 1 else f'{k[0]}{dm[int(k[1])]}'
    T = lambda u, p: add((u[0] + p, *f(u[1], u[2])), d)
    st = pickle.load(open(HERE / 'runs' / 'caps' / 'start_L7_pinned.pkl', 'rb'))['sol']
    by = {nm: (w, cells) for nm, w, cells, m in st}
    ks = lambda k: k if isinstance(k, str) else f'{k[0]}{k[1]}'
    half = []   # (name, word, fixedcells or None, box or None, rider kind or None)
    for nm in ('K0', 'N', 'K1', 'K2', 'K3', 'K4'):
        w, cells = by[nm]
        if nm == 'K4' and free4:
            half.append((nm, tuple(w), None,
                         [add(ORG[4], (dx, dy, dz)) for dx in range(-2, 3) for dy in range(-2, 3) for dz in range(-2, 3)], None))
            continue
        half.append((nm, tuple(w), {c: ks(k) for c, k in cells.items()}, None, None))
    half.append(('K5', WORDS['wwmm'], None,
                 [add(ORG[5], (dx, dy, dz)) for dx in range(-3, 3) for dy in range(-2, 3) for dz in range(-2, 3)], None))
    half.append(('V', WORDS['wmmw'], None,
                 [add(ORG[5], (dx, dy, dz)) for dx in range(-3, 1) for dy in range(-2, 3) for dz in range(-2, 3)], 'P'))
    names, words, fixed, boxes, riders, kbs, img = [], [], [], [], [], {}, {}
    for nm, w, fc, bx, rk in half:
        names.append(nm); words.append(w); fixed.append((fc, None) if fc else None); boxes.append(bx)
        if rk: riders.append(nm); kbs[nm] = [rk]
    n1 = len(names)
    for i, (nm, w, fc, bx, rk) in enumerate(half):
        p = wpos(w, 2)
        names.append(nm + "'"); words.append(shiftword(w))
        if fc: fixed.append(({T(u, p): km(k) for u, k in fc.items()}, None)); boxes.append(None)
        else: fixed.append(None); boxes.append([T(u, p) for u in bx]); img[i] = (n1 + i, p)
        if rk: riders.append(nm + "'"); kbs[nm + "'"] = [rk]
    names.append('F'); words.append(WORDS['mwmw']); fixed.append(None)
    boxes.append([add(ORG[6], (dx, dy, dz)) for dx in range(-2, 3) for dy in range(-3, 4) for dz in range(-3, 4)])
    occ = set()
    for fx in fixed:
        if fx is None: continue
        for c in fx[0]:
            if c in occ: return None
            occ.add(c)
    M = FlyerSAT(words, None, L, kinds=kinds, leaf=True, maxglue=L - 1, fixed=fixed, names=names, boxes=boxes,
                 riders=riders, kinds_by_seg=kbs, merges=[(1, ['K0', 'N']), (3, ["K0'", "N'"])],
                 must={'F': fpin} if fpin else None)
    for i, (j, p) in img.items():
        for u in boxes[i]:
            for k in M.kinds_of(i):
                M.m.Add(M.X[i, u, k] == M.X[j, T(u, p), km(k)])
    return M


def solve(args):
    mapname, d, L, tl, wk = args
    try:
        M = build(mapname, d, L)
    except Exception as e:
        return args, 'ERR ' + repr(e)[:100], 0, None
    if M is None: return args, 'SKEL_OVERLAP', 0, None
    st, dt = M.solve(tl, wk)
    if st in ('OPTIMAL', 'FEASIBLE'):
        sol = M.extract()
        od = HERE / 'runs' / 'mirror'; od.mkdir(parents=True, exist_ok=True)
        tag = f'mirror_{mapname}_{d[0]}_{d[1]}_{d[2]}_L{L}'
        pickle.dump({'sol': sol, 'map': mapname, 'd': d, 'riders': sorted(M.names[r] for r in M.riders),
                     'merges': [(1, ['K0', 'N']), (3, ["K0'", "N'"])]}, open(od / f'{tag}.pkl', 'wb'))
        return args, st, dt, report(M)
    return args, st, dt, None


def fixed_ok(mapname, d):
    """cheap check: chain 1's fixed cells and their images never overlap in any slot."""
    f = YZ[mapname]
    st = pickle.load(open(HERE / 'runs' / 'caps' / 'start_L7_pinned.pkl', 'rb'))['sol']
    parts = []
    for nm, w, cells, m in st:
        if nm not in ('K0', 'N', 'K1', 'K2', 'K3', 'K4'): continue
        w = tuple(w); p2 = wpos(w, 2); w2 = shiftword(w)
        parts.append((w, list(cells)))
        parts.append((w2, [add((u[0] + p2, *f(u[1], u[2])), d) for u in cells]))
    for t in range(4):
        occ = set()
        for w, cells in parts:
            sh = wpos(w, t)
            for c in cells:
                cc = (c[0] + sh, c[1], c[2])
                if cc in occ: return False
                occ.add(cc)
    return True


def candidates(maps):
    """offsets d where K5's image lands near F's region (both chains can reach F) and fixed parts don't overlap."""
    out = []
    for mp in maps:
        f = YZ[mp]
        for d in itertools.product(range(-3, 6), range(-12, 13), range(-12, 13)):
            k5i = add((ORG[5][0], *f(ORG[5][1], ORG[5][2])), d)       # K5 word wwmm: pos(2)=0
            if max(abs(k5i[0] - ORG[5][0] + 1), abs(k5i[1] - ORG[5][1]), abs(k5i[2] - ORG[5][2])) > 3: continue
            if fixed_ok(mp, d): out.append((mp, d))
    return out


if __name__ == '__main__':
    L, tl, wk, npr = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    maps = sys.argv[5].split(',') if len(sys.argv) > 5 else list(YZ)
    cands = candidates(maps)
    def closeness(md):     # distance between K5's template origin and its image (closest = most mirror-like first)
        mp, d = md; f = YZ[mp]
        k5i = add((ORG[5][0], *f(ORG[5][1], ORG[5][2])), d)
        return sum(abs(a - b) for a, b in zip(k5i, ORG[5]))
    cands.sort(key=closeness)
    print('candidates', len(cands), flush=True)
    log = open(HERE / 'runs' / f'mirror_L{L}.log', 'a'); cnt = {}
    with Pool(npr) as pool:
        for args, st, dt, rep in pool.imap_unordered(solve, [(mp, d, L, tl, wk) for mp, d in cands]):
            cnt[st] = cnt.get(st, 0) + 1
            log.write(f'{args[0]} {args[1]} {st} {dt:.1f}\n'); log.flush()
            if rep: print('FOUND', args[0], args[1], st, rep, flush=True)
            if sum(cnt.values()) % 50 == 0: print(cnt, flush=True)
    print('done', cnt, flush=True)
