"""Rectangle ring layout: even body count, sides of m1/m2/m1/m2 bodies, each side rotated 90 degrees from the last,
so only two link types (straight, corner) occur."""
import sys, time
import construct
from nk import Timing, Ring, SYMS, bodies_for


def ring_size(k, minL=4):
    L = bodies_for(k)
    while L % 4 or L < minL: L += bodies_for(k)
    return L


def rect_layout(L, a, b, gy, cv, m1=None):
    """turtle walk; heading h uses sym h (90-degree steps). straight step (a+gy, 0), corner step cv, in heading frame."""
    half = L // 2
    if m1 is None: m1 = half // 2
    m2 = half - m1
    sides = [m1, m2, m1, m2]
    place = []; p = (0, 0); h = 0
    for side, m in enumerate(sides):
        for j in range(m):
            place.append((0, p, h))
            last = j == m - 1
            v = cv if last else (a + gy, 0)
            dv = SYMS[h](*v); p = (p[0] + dv[0], p[1] + dv[1])
        h = (h + 1) % 4
    return place


def build(k, gy, cv, m1=None, family='slabP'):
    L = ring_size(k); T = Timing(k, L)
    mod = construct.grid_module(k, family); a, b = mod['size']
    ring = Ring(T, [mod] * L, rect_layout(L, a, b, gy, cv, m1))
    for X in range(L): ring.route(X)
    return ring


if __name__ == '__main__':
    for k in [int(x) for x in sys.argv[1].split(',')]:
        mod = construct.grid_module(k, 'slabP'); a, b = mod['size']
        res = []; t = time.time()
        for gy in (1, 2):
            for cy in range(a - 1, a + 3):
                for cz in range(-1, 3):
                    try:
                        r = build(k, gy, (cy, cz))
                    except (RuntimeError, AssertionError): continue
                    bad = r.check()
                    if not bad: res.append((max(r.size()), gy, (cy, cz)))
        res.sort(); print(k, 'L', ring_size(k), 'a,b', (a, b), res[:3], round(time.time() - t, 1), flush=True)
