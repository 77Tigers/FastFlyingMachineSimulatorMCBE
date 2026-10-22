"""Square-ring module with lateral edge cover: W (next, along +y) covers V's edge column y=a-1 from the gap lane y=a
at x=-2, the rest by a slab at x=-3; one empty edge lane (notch) lets W's connector rise beside it."""
import sys, time
import construct, square
from construct import nb, connected


def sq_module(k, notch_z=None):
    best = None
    for a in range(1, 12):
        for b in range(1, 14):
            if a * b > 2 * k + 12: break
            for off in range(5):
                cells = [(y, z) for y in range(a) for z in range(b)]
                Rs = {c for c in cells if (c[0] + 2 * c[1] + off) % 5 == 0}
                for nz in range(b):
                    notch = (a - 1, nz)
                    Rn = Rs - {notch}
                    cand = [c for c in cells if c not in Rn and c != notch and any(v in Rn for v in nb(c))]
                    if len(cand) < k: continue
                    cand.sort(key=lambda c: (-c[0], abs(c[1] - (b - 1) / 2)))   # fill the edge column first
                    P = cand[:k]; Ps = set(P)
                    R = [r for r in Rn if any(v in Ps for v in nb(r))]
                    plate = sorted(Ps | set(R))
                    if not connected(plate): continue
                    edge = [p for p in P if p[0] == a - 1]
                    rest = [p for p in P if p[0] != a - 1]
                    cover = [(-2, a, p[1]) for p in edge] + [(-3,) + p for p in rest]
                    cost = len(plate) + len(R) + len(cover)
                    if best is None or cost < best[0]: best = (cost, a, b, P, R, plate, cover)
    _, a, b, P, R, plate, cover = best
    return dict(R=[(0,) + r for r in R], P=P, PLATE=[(1,) + c for c in plate], CONT=cover, size=(a, b))


def search(k, verbose=False):
    mod = sq_module(k); a, b = mod['size']
    L = square.ring_size(k); m = L // 4
    res = []
    for sz in (-1, 0, 1):
        step = (a + 1, sz)
        for cv in [(cy, cz) for cy in range(a - 1, a + b + 3) for cz in range(-2, b + 3)]:
            try:
                r = square.make(k, mod, step, cv)
                if not square.hard_ok(r): continue
                c = square.rep_cost(r)
            except (RuntimeError, AssertionError):
                continue
            res.append((c, step, cv))
    res.sort()
    for c, step, cv in res[:10]:
        r = square.make(k, mod, step, cv)
        try:
            for X in range(r.T.L): r.route(X)
        except RuntimeError: continue
        bad = r.check()
        if verbose: print('  cand', c, step, cv, max(r.size()), len(bad), bad[:1])
        if not bad: return r, (step, cv)
    return None, None


if __name__ == '__main__':
    for k in [int(x) for x in sys.argv[1].split(',')]:
        m = sq_module(k); print(k, 'module', m['size'], 'P', len(m['P']), 'R', len(m['R']), 'plate', len(m['PLATE']), 'cover', len(m['CONT']))
        t = time.time(); r, par = search(k, '-v' in sys.argv)
        print('  best', max(r.size()) if r else None, par, round(time.time() - t, 1), flush=True)
