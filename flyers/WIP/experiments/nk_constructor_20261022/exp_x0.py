"""experiment: square ring with per-body x offsets (x0 pattern), lat module. python exp_x0.py K A B"""
import sys, itertools, time
import families as F, square, sqbuild
from nk import Timing, Ring

def make(k, mod, step, cv, x0s):
    L = square.ring_size(k); T = Timing(k, L); a, b = mod['size']
    pl = square.square_layout(L, a, b, step, cv)
    place = [(x0s[i % len(x0s)], p, h) for i, (_, p, h) in enumerate(pl)]
    return Ring(T, [mod] * L, place)

def try_one(k, mod, step, cv, x0s):
    r = make(k, mod, step, cv, x0s)
    if not square.hard_ok(r): return None
    try:
        for X in range(r.T.L): r.route(X)
    except (RuntimeError, AssertionError): return None
    return r

if __name__ == '__main__':
    k, a, b = map(int, sys.argv[1:4])
    mod = F.lat_module(k, a, b)
    L = square.ring_size(k); m = L // 4
    res = []
    t = time.time()
    for cy in range(a - 1, a + b + 3):
        for cz in range(-2, b + 3):
            for xs in itertools.product(range(-2, 3), repeat=3):
                x0s = (0,) + xs
                try: r = try_one(k, mod, (a + 2, 0), (cy, cz), x0s)
                except Exception as e: continue
                if r is None: continue
                sz = max(r.size())
                res.append((sz, sum(r.size()), (cy, cz), x0s))
    res.sort()
    print('time', round(time.time() - t, 1), 'n', len(res))
    for x in res[:15]: print(x)
