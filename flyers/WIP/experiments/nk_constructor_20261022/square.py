"""Square ring: L = multiple of 4 bodies (and of the N_k base ring), m = L/4 per side, side h rotated h*90 degrees.
Two link types: straight (y step a+gy, z offset sz) and corner (step cv), both in the heading frame.
Search: route only a representative straight body and corner body, then build + check the best full ring.
python square.py K1,K2,..."""
import sys, time, itertools
import construct
from nk import Timing, Ring, SYMS, bodies_for


def ring_size(k, m_min=1):
    L0 = bodies_for(k); L = L0
    while L % 4 or L // 4 < m_min: L += L0
    return L


def square_layout(L, a, b, step, cv):
    m = L // 4; place = []; p = (0, 0)
    for h in range(4):
        for j in range(m):
            place.append((0, p, h))
            v = cv if j == m - 1 else step
            d = SYMS[h](*v); p = (p[0] + d[0], p[1] + d[1])
    assert p == (0, 0)
    return place


def make(k, mod, step, cv, L=None):
    L = L or ring_size(k); T = Timing(k, L)
    a, b = mod['size']
    r = Ring(T, [mod] * L, square_layout(L, a, b, step, cv))
    m = L // 4
    if m > 4:   # only side 0 and its neighbours are routed / checked; the rest is copied by symmetry
        r.active = sorted({Y for X in (0, 1, m // 2, m - 1) for Y in r.near(X, margin=6)} | set(range(m)))
    return r


def hard_ok(ring):
    """no two bodies' hardware/plates/contacts share a cell at any slot (only bodies near the first corner)."""
    L = ring.T.L; m = L // 4
    near = sorted({(m + d) % L for d in range(-2, 3)} | {(1 + d) % L for d in range(-1, 2)})
    for s in range(ring.T.S):
        occ = ring.world(s, bodies=near)
        for c, lst in occ.items():
            if len({e[0] for e in lst}) > 1: return False
    return True


def rep_cost(ring):
    """route a straight body (1, if m>1) and the first corner body (m) only; return their largest size."""
    L = ring.T.L; m = L // 4
    reps = [m] + ([1] if m > 1 else [])
    for X in reps: ring.route(X)
    return max(ring.size()[X] for X in reps)


def search(k, family='slabP', verbose=False):
    mod = construct.grid_module(k, family); a, b = mod['size']
    L = ring_size(k); m = L // 4
    steps = [(a + gy, sz) for gy in (1, 2, 3) for sz in (-1, 0, 1)] if m > 1 else [(a + 2, 0)]
    cvs = [(cy, cz) for cy in range(a - 1, a + b + 3) for cz in range(-2, b + 3)]
    res = []
    for step in steps:
        for cv in cvs:
            try:
                r = make(k, mod, step, cv)
                if not hard_ok(r): continue
                c = rep_cost(r)
            except (RuntimeError, AssertionError):
                continue
            res.append((c, step, cv))
    res.sort()
    for c, step, cv in res[:12]:
        r = make(k, mod, step, cv)
        try:
            for X in range(r.T.L): r.route(X)
        except RuntimeError:
            continue
        bad = r.check()
        if verbose: print('  cand', c, step, cv, max(r.size()), len(bad), bad[:1])
        if not bad: return r, (step, cv)
    return None, None


if __name__ == '__main__':
    for k in [int(x) for x in sys.argv[1].split(',')]:
        t = time.time(); r, par = search(k, verbose='-v' in sys.argv)
        print(k, 'L', ring_size(k), 'best', max(r.size()) if r else None, par, round(time.time() - t, 1), flush=True)
