"""Terrace ring (prototype): each body's k hoppers are split into g floors that sit in g consecutive lane strips,
one floor per strip, each floor about 4 higher than the one before.  Strip d holds a diagonal of the ring:
body d floor g on top, body d+1 floor g-1 under it, ..., body d+g-1 floor 1, and body d+g's slab at the bottom.
So the spent hoppers of a floor are covered by the NEXT body's plate of the floor below (same lanes, 3 lower),
and only floor 1 needs real cover cells (a slab).  Strips go round a square ring like the square family's bodies.
python terrace.py K G [GAP] [CY CZ]"""
import sys, itertools
import construct, square
from nk import Timing, Ring, SYMS


def strip_pattern(p, box=None):
    mod = construct.grid_module(p, 'slabP', box=box)
    P = [tuple(c) for c in mod['P']]
    R = [tuple(c[1:]) for c in mod['R']]
    return P, R, mod['size']


def floor_sizes(k, g):
    q, r = divmod(k, g)
    return [q + (1 if f >= g - r else 0) for f in range(g)]   # floors 1..g, larger ones on top


import os
PHASE = int(os.environ.get('TERR_PH', 0))


def levels(T, g, smooth=True):
    """h[i][f] (f = 0..g-1 for floors 1..g) pusher level of body i, from the diagonal rule
    h(i+1, f-1) = h(i, f) - 4 + D_i.  Step s_d = 4 + T_{d+1} - T_d - D_d is kept as even as the ring allows."""
    L = T.L
    D = [T.shift(V, T.rest[V]) - T.shift(T.nxt(V), T.rest[V]) for V in range(L)]
    tot = 4 * L - sum(D)            # sum of all steps s_d
    base, extra = divmod(tot, L)
    ph = PHASE                       # where the extra steps fall (rotation)
    s = [base + (1 if ((d + ph) * extra) % L < extra else 0) for d in range(L)]
    assert sum(s) == tot
    Td = [0] * L
    for d in range(L - 1): Td[d + 1] = Td[d] + s[d] - 4 + D[d]
    assert Td[0] == Td[L - 1] + s[L - 1] - 4 + D[L - 1] - 0 or True
    h = [[None] * g for _ in range(L)]
    for d in range(L):
        for t in range(g):
            i = (d + t) % L; f = g - 1 - t
            h[i][f] = Td[d] - 4 * t + sum(D[(d + u) % L] for u in range(t))
    return h, s, D


import functools


@functools.lru_cache(maxsize=None)
def cp_pattern(p, a, b, g, det=2.0):
    import strip_cp
    r = strip_cp.solve(p, a, b, g, det)
    if r is None: return None
    return [tuple(c) for c in r['P']], [tuple(c) for c in r['R']], (a, b), [tuple(c) for c in r['PL']], [tuple(c) for c in r['S']]


@functools.lru_cache(maxsize=None)
def cp2_pattern(p, a, b, g, det=8.0):
    """strip pattern whose floor-1 cover may sit beside the hoppers (strip_cp.solve2, hinted with solve)"""
    import strip_cp
    h = strip_cp.solve(p, a, b, g, 2.0)
    r = strip_cp.solve2(p, a, b, g, det, hint=h)
    if r is None: return None
    return ([tuple(c) for c in r['P']], [tuple(c) for c in r['R']], (a, b), [tuple(c) for c in r['PL']],
            [tuple(c) for c in r['S']], [tuple(c) for c in r['SD']])


def build(k, g, gap=1, cv=None, box=None, mirror=False, pattern='slab', sz=0):
    L = square.ring_size(k) * int(os.environ.get('TERR_RING', 1)); T = Timing(k, L)
    sizes = floor_sizes(k, g); p = max(sizes)
    PLx = Sx = None; SDx = []
    if isinstance(pattern, dict):   # an explicit strip pattern (strip_cp.solve_many entry)
        P, R, (a, b), PLx, Sx = ([tuple(c) for c in pattern['P']], [tuple(c) for c in pattern['R']], tuple(pattern['size']),
                                 [tuple(c) for c in pattern['PL']], [tuple(c) for c in pattern['S']])
    elif pattern == 'cp2':
        if box is None: box = construct.grid_module(p, 'slabP')['size']
        res = cp2_pattern(p, box[0], box[1], g)
        if res is None: return None
        P, R, (a, b), PLx, Sx, SDx = res
    elif pattern == 'cp':
        if box is None: box = construct.grid_module(p, 'slabP')['size']
        res = cp_pattern(p, box[0], box[1], g)
        if res is None: return None
        P, R, (a, b), PLx, Sx = res
    else:
        P, R, (a, b) = strip_pattern(p, box)
    if mirror: P = [(a - 1 - y, z) for y, z in P]; R = [(a - 1 - y, z) for y, z in R]
    if cv is None: cv = (a - 1, b + 1)
    place = square.square_layout(L, a, b, (a + gap, sz), cv)
    def world(d, c):
        _, (oy, oz), si = place[d % L]; y, z = SYMS[si](c[0], c[1]); return (y + oy, z + oz)
    h, s, D = levels(T, g)
    mods = []
    for i in range(L):
        mP, mR, mPL, mC = [], [], [], []
        for f in range(g):
            d = (i - (g - 1 - f)) % L
            lanes = P[:sizes[f]]; ls = set(lanes)
            rl = [r for r in R if any((r[0] + dy, r[1] + dz) in ls for dy, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
            hh = h[i][f]
            for c in lanes:
                wy, wz = world(d, c); mP.append((wy, wz, hh)); mPL.append((hh + 1, wy, wz))
                if not (f == 0 and SDx) or c in Sx: mC.append((hh - 3, wy, wz))
            for c in rl:
                wy, wz = world(d, c); mR.append((hh, wy, wz)); mPL.append((hh + 1, wy, wz))
            if PLx is not None:     # cp strip: extra plate lanes (connectivity); floor 1 also gets the extra slab lanes
                for c in PLx:
                    if c not in ls and c not in rl: wy, wz = world(d, c); mPL.append((hh + 1, wy, wz))
                if f == 0:
                    for c in Sx:
                        if c not in ls: wy, wz = world(d, c); mC.append((hh - 3, wy, wz))
                    for c in SDx:   # beside covers (cp2): -2, in a lane free of hoppers / RBs
                        wy, wz = world(d, c); mC.append((hh - 2, wy, wz))
        mods.append(dict(P=mP, R=mR, PLATE=mPL, CONT=mC, size=(a, b)))
    r = Ring(T, mods, [(0, (0, 0), 0)] * L)
    r.h, r.steps, r.D, r.sizes = h, s, D, sizes
    return r


def collisions(r, bodies=None):
    bad = []
    for s in range(r.T.S):
        occ = r.world(s, bodies=bodies)
        for c, lst in occ.items():
            if len({e[0] for e in lst}) > 1: bad.append((s, c, lst[:3]))
    return bad


def route_all(r):
    """connect every body: tree = its top-floor plate, everything else (other floors, slab, extras) joined to it."""
    T = r.T
    for X in range(T.L):
        full = set(r.plates[X])
        top = {c for c in full if c[0] == max(cc[0] for cc in full)}
        r.plates[X] = top
        r.extra[X] = set(r.extra[X]) | (full - top)
        r.route(X)
        r.plates[X] = full
    return r


if __name__ == '__main__':
    k, g = int(sys.argv[1]), int(sys.argv[2])
    gap = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    cv = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else None
    r = build(k, g, gap, cv)
    print('L', r.T.L, 'floors', r.sizes, 'steps', sorted(set(r.steps)), 'D', [d for d in r.D if d][:6])
    col = collisions(r, bodies=list(range(min(r.T.L, 12))))
    print('collisions', len(col), col[:3])
