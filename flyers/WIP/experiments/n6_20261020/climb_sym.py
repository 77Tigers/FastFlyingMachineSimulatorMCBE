"""placement climb with 180-degree symmetry: C = R180(A), D = R180(B), x origins C=A-1, D=B-1."""
import sys, random, json, math
from multiprocessing import Pool
from ring_designer import Ring, ORDER, V1, V2, V3, V4, V5, route_all, SYMS
from search_place import footprint
LAY = {'V1': V1, 'V2': V2, 'V3': V3, 'V4': V4, 'V5': V5}
ROT = {i: j for i in range(8) for j in range(8)
       if all(SYMS[j](y, z) == (-SYMS[i](y, z)[0], -SYMS[i](y, z)[1]) for y, z in [(1, 2), (3, 5)])}


def full(p):
    (xa, (ay, az), sa), (xb, (by, bz), sb) = p['A'], p['B']
    return {'A': p['A'], 'B': p['B'], 'C': (xa - 1, (-ay, -az), ROT[sa]), 'D': (xb - 1, (-by, -bz), ROT[sb])}


def score(name, p):
    place = full(p); mod = LAY[name]; used = set()
    for X in ORDER:
        fp = footprint(mod, place[X][2], place[X][1])
        if fp & used: return None
        used |= fp
    try:
        ring = Ring(mod, place); route_all(ring)
        if ring.check(): return None
        sz = ring.size(); return (max(sz.values()), sum(sz.values()))
    except Exception:
        return None


def nb(p, rng):
    q = dict(p); X = rng.choice(['A', 'B']); x0, (oy, oz), s = q[X]
    r = rng.random()
    if r < 0.35: oy += rng.choice([-1, 1])
    elif r < 0.7: oz += rng.choice([-1, 1])
    elif r < 0.85: x0 += rng.choice([-1, 1])
    else: s = rng.randrange(8)
    q[X] = (x0, (oy, oz), s); return q


def ev(a): return score(*a), a[1]


if __name__ == '__main__':
    name, iters, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    rng = random.Random(seed)
    # random restarts
    with Pool(4) as pool:
        starts = []
        while len(starts) < 4:
            cand = [{'A': (0, (rng.randrange(-4, 5), rng.randrange(-4, 5)), rng.randrange(8)),
                     'B': (rng.randrange(-3, 3), (rng.randrange(-8, 9), rng.randrange(-8, 9)), rng.randrange(8))} for _ in range(16)]
            starts += [(s, c) for s, c in pool.map(ev, [(name, c) for c in cand]) if s]
        starts.sort(key=lambda r: r[0])
        cur, p = starts[0]; best = (cur, p); print('start', cur, flush=True)
        T = 1.0
        for it in range(iters):
            res = [r for r in pool.map(ev, [(name, nb(p, rng)) for _ in range(8)]) if r[0]]
            if not res: continue
            res.sort(key=lambda r: r[0]); s, q = res[0]
            if s <= cur or rng.random() < math.exp(-((s[0] - cur[0]) * 10 + (s[1] - cur[1])) / T):
                cur, p = s, q
                if s < best[0]: best = (s, q); print(it, 'best', s, full(q), flush=True)
            T = max(0.3, T * 0.98)
    print('final', best[0], full(best[1]))
