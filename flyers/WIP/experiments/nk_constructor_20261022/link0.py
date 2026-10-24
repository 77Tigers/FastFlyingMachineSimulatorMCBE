"""Back links with a straight column (user rule: the back connector goes 0-1 lanes sideways, preferably 0).
A link = n hopper lanes H, RB lanes R (each hopper beside one), front cluster = H + R at x = 1 (must be connected),
cover lanes Q at -2 beside the spent hoppers (free of H and R), and a column lane c beside the cluster. The next body's
column must run down the lane of its predecessor's main cover q0, so the straight step is q0 - c (0 lanes sideways).
Every link is built as a back ring (tower2.build, h = 0, balanced frame offsets) and checked.
python link0.py N K"""
import sys, itertools
import tower2, square
from terrace import collisions
from tower import route_all
from nk2 import power_problems

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
def nb(c): return [(c[0] + d[0], c[1] + d[1]) for d in N4]


def connected(cells):
    cells = set(cells); st = [next(iter(cells))]; seen = set()
    while st:
        u = st.pop()
        if u in seen: continue
        seen.add(u); st += [v for v in nb(u) if v in cells]
    return len(seen) == len(cells)


def links(n, box=3, lat=0, minstep=2):
    lanes = [(y, z) for y in range(box) for z in range(box)]
    seen = set()
    for H in itertools.combinations(lanes, n):
        Hs = set(H)
        cand = [l for l in lanes + [(y, z) for y in (-1, box) for z in range(box)] if l not in Hs and any(h in nb(l) for h in H)]
        for nr in range(1, n + 1):
            Rs = [R for R in itertools.combinations(cand, nr) if all(any(r in nb(h) for r in R) for h in H)
                  and connected(H + R)]
            if Rs: break
        for R in Rs:
            used = Hs | set(R)
            # cover lanes: greedy, the lane beside the most uncovered hoppers first
            free = sorted({v for h in H for v in nb(h) if v not in used})
            for q0 in free:
                Q = [q0]; left = [h for h in H if h not in nb(q0)]
                while left:
                    best = max((v for v in free if v not in Q), key=lambda v: sum(h in nb(v) for h in left), default=None)
                    if best is None or not any(h in nb(best) for h in left): break
                    Q.append(best); left = [h for h in left if h not in nb(best)]
                if left: continue
                for c in sorted({v for u in used for v in nb(u) if v not in used and v not in Q}):
                  for dl in ([(0, 0)] if lat == 0 else list(N4)):   # column lane of the next body = q0 + dl
                    step = (q0[0] + dl[0] - c[0], q0[1] + dl[1] - c[1])
                    if abs(step[0]) + abs(step[1]) < minstep: continue
                    # normalise to lanes >= 0
                    allc = list(used) + Q + [c]
                    oy, oz = min(l[0] for l in allc), min(l[1] for l in allc)
                    sh = lambda l: (l[0] - oy, l[1] - oz)
                    key = (tuple(sorted(map(sh, H))), tuple(sorted(map(sh, R))), tuple(map(sh, Q)), sh(c), step)
                    if key in seen: continue
                    seen.add(key)
                    a = max(l[0] for l in allc) - oy + 1; b = max(l[1] for l in allc) - oz + 1
                    mod = dict(P=[sh(h) for h in H], R=[(0,) + sh(r) for r in R],
                               PLATE=[(1,) + sh(l) for l in list(H) + list(R)], CONT=[(-2,) + sh(q) for q in Q],
                               size=(a, b))
                    yield mod, step, sh(c)


def back_ring(k, mod, step, cv, phase):
    L = square.ring_size(k)
    from nk import bodies_for
    xo = tower2.balanced_xoff(k, L, phase)
    r = tower2.build(k, 1, 0, (), back=(mod, step), cv=cv, xoff=xo)
    if r is None or collisions(r): return None
    route_all(r)
    if r.check() or power_problems(r): return None
    return r


def _ev(a): return evaluate(*a)


def evaluate(k, mod, step, span=7):
    from nk import bodies_for
    best = None
    for cv in itertools.product(range(-3, span), repeat=2):
        try: r = back_ring(k, mod, step, cv, bodies_for(k) - 1)
        except (AssertionError, RuntimeError): continue
        if r is None: continue
        sc = (max(r.size()), sum(r.size()), cv)
        if best is None or sc < best: best = sc
    return best


if __name__ == '__main__':
    n, k = int(sys.argv[1]), int(sys.argv[2])
    lat = int(sys.argv[3]) if len(sys.argv) > 3 else 0; minstep = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    from concurrent.futures import ProcessPoolExecutor
    L = list(links(n, lat=lat, minstep=minstep)); print(len(L), 'links', flush=True)
    res = []
    import os
    with ProcessPoolExecutor(int(os.environ.get('L0W', 12))) as ex:
        evs = list(ex.map(_ev, [(k, mod, step) for mod, step, c in L]))
    for (mod, step, c), ev in zip(L, evs):
        if ev: res.append((ev[0], ev[1], step, ev[2], mod)); print(res[-1][:4], mod['P'], mod['R'], mod['CONT'], flush=True)
    res.sort(key=lambda t: (t[0], t[1]))
    print('BEST', res[:5])
