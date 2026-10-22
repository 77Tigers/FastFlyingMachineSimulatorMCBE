"""Search 90-degree screw rings: same link translation t and rotation s for all four links.
usage: python screw_search.py LAYOUT [strict]"""
import sys
from multiprocessing import Pool
import ring_designer as rd
from close_ring import chain, LAY
from ring_designer import Ring, route_all, route2_all, hard_conflicts, V8, V9, V9b
LAY['V8'] = V8; LAY['V9'] = V9; LAY['V9b'] = V9b
ROUTER = route2_all

import itertools
PATTERNS = [(a, b, c, -(a + b + c)) for a, b, c in itertools.product((-2, -1, 0, 1), repeat=3) if -1 <= -(a + b + c) <= 3]


def ev(a):
    name, s, t, dxs, strict, rt = a
    global ROUTER
    ROUTER = route_all if rt else route2_all
    rd.STRICT = strict
    try:
        place, back = chain([(dx, t, s) for dx in dxs])
        if back != (0, (0, 0), 0): return None
        ring = Ring(LAY[name], {k: (v[0], tuple(v[1]), v[2]) for k, v in place.items()})
        if hard_conflicts(ring, first=True): return None
        sz = ROUTER(ring)
        if ring.check(): return None
        return (max(sz.values()), sum(sz.values()), s, t, dxs)
    except Exception:
        return None


if __name__ == '__main__':
    SYMSET = (1, 3) if 'all' not in sys.argv[2:] else range(8)
    name = sys.argv[1]; strict = 'strict' in sys.argv[2:]
    if 'r1' in sys.argv[2:]: ROUTER = route_all
    jobs = [(name, s, (ty, tz), p, strict, 'r1' in sys.argv[2:]) for s in SYMSET for ty in range(-8, 9) for tz in range(-8, 9) for p in PATTERNS]
    with Pool(int(__import__('os').environ.get('N6_PROCS', '4'))) as pool: res = sorted(r for r in pool.map(ev, jobs, chunksize=8) if r)
    print(len(res), 'valid')
    for r in res[:12]: print(r)
