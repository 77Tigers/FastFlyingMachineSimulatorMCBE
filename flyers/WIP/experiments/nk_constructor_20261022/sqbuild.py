"""Fast square-ring constructor. L = multiple of 4 and of the base ring; m = L/4 bodies per side, side h rotated
h*90 degrees. Link types repeat with the base period L0, so when m % L0 == 0 we route side 0 only and copy its
connectors, rotated, to sides 1..3; otherwise every body is routed."""
import time
import construct, square
from nk import Timing, Ring, SYMS, bodies_for

INV = {0: 0, 1: 3, 2: 2, 3: 1}


def to_local(place, c):
    _, (oy, oz), si = place
    y, z = SYMS[INV[si]](c[1] - oy, c[2] - oz)
    return (c[0], y, z)


def to_world(place, c):
    _, (oy, oz), si = place
    y, z = SYMS[si](c[1], c[2])
    return (c[0], y + oy, z + oz)


def candidates(a, b, m):
    if m == 1: return [((a + 2, 0), (cy, cz)) for cy in range(a - 1, a + b + 3) for cz in range(-2, b + 3)]
    return [((a + 1, sz), (a - 1, cz)) for sz in (-1, 0) for cz in (b, b + 1, b + 2)]


def assemble(k, mod, step, cv):
    L = square.ring_size(k); m = L // 4; L0 = bodies_for(k)
    r = square.make(k, mod, step, cv)
    if not square.hard_ok(r): return None
    if m % L0 == 0:
        for X in range(m): r.route(X)
        for X in range(m, L):
            src = X % m
            cells = {to_world(r.place[X], to_local(r.place[src], c)) for c in r.glue[src] - r.plates[src] - r.contacts[src]}
            r.glue[X] = r.plates[X] | r.contacts[X] | cells
        r.invalidate()
    else:
        r.active = None; r.invalidate()
        for X in range(L): r.route(X)
    return r


def build(k, family='slabP'):
    mod = construct.grid_module(k, family); a, b = mod['size']
    L = square.ring_size(k); m = L // 4
    scored = []
    for step, cv in candidates(a, b, m):
        try:
            r = square.make(k, mod, step, cv)
            if not square.hard_ok(r): continue
            reps = [0, 1] if m > 1 else [0]
            r.active = sorted({Y for X in reps for Y in r.near(X, margin=6)})
            for X in reps: r.route(X)
            scored.append((max(r.size()[X] for X in reps), step, cv))
        except (RuntimeError, AssertionError):
            continue
    for _, step, cv in sorted(scored):
        try:
            r = assemble(k, mod, step, cv)
        except (RuntimeError, AssertionError):
            continue
        if r is None: continue
        sub = sorted({d % L for d in range(-3, 4)} | {(m // 2 + d) % L for d in range(-1, 2)})
        if not r.check(sub):
            r.params = (step, cv)
            return r
    return None


def build_fast(k, table, family='slabP'):
    """use the layout parameters chosen offline (table[k] = (step, cv)); falls back to build() if missing."""
    if str(k) not in table: return build(k, family)
    e = table[str(k)]; step, cv = tuple(e[0]), tuple(e[1])
    if len(e) > 2: family = e[2]
    mod = construct.grid_module(k, family)
    r = assemble(k, mod, step, cv); r.params = (step, cv)
    return r


if __name__ == '__main__':
    import sys
    for k in [int(x) for x in sys.argv[1].split(',')]:
        t = time.time(); r = build(k); dt = time.time() - t
        if r is None: print(k, 'none'); continue
        bad = r.check() if '-c' in sys.argv else []
        r.flyer(max(r.size()) + 3 * k + 10).save(f'out/n{k}_sq.flyer')
        print(k, 'L', r.T.L, 'max body', max(r.size()), 'time', round(dt, 2), 'bad', len(bad), bad[:2], flush=True)
