"""Square ring whose straight links flip the next body 180 degrees (sides alternate orientation h, h+2)."""
import sys, time, json
import construct, square, sqbuild
from nk import Timing, Ring, SYMS


def layout(L, step, cv):
    m = L // 4; place = []; p = (0, 0); o = 0
    for side in range(4):
        h = side
        for j in range(m):
            place.append((0, p, o))
            last = j == m - 1
            v = cv if last else step
            d = SYMS[h](*v); p = (p[0] + d[0], p[1] + d[1])
            o = (side + 1) % 4 if last else (o + 2) % 4
    return place, p, o


def make(k, mod, step, cv):
    L = square.ring_size(k); T = Timing(k, L)
    place, p, o = layout(L, step, cv)
    if p != (0, 0): return None
    return Ring(T, [mod] * L, place)


def search(k, fam, verbose=False):
    mod = construct.grid_module(k, fam); a, b = mod['size']; L = square.ring_size(k); m = L // 4
    scored = []
    for step in [(sy, sz) for sy in range(a - 1, a + 4) for sz in range(-b - 1, b + 2)]:
        for cv in [(cy, cz) for cy in range(-2, a + b + 2) for cz in range(-b - 2, b + 3)]:
            r = make(k, mod, step, cv)
            if r is None: continue
            reps = [1, m] if m > 2 else [1]
            near = sorted({(X + d) % L for X in reps for d in range(-2, 3)})
            r.active = near
            ok = True
            for s in range(r.T.S):
                for c, lst in r.world(s, bodies=near).items():
                    if len({e[0] for e in lst}) > 1: ok = False; break
                if not ok: break
            if not ok: continue
            try:
                for X in reps: r.route(X)
            except RuntimeError: continue
            scored.append((max(r.size()[X] for X in reps), step, cv))
    scored.sort()
    for c, step, cv in scored[:20]:
        r = make(k, mod, step, cv)
        try:
            for X in range(L): r.route(X)
        except RuntimeError: continue
        bad = r.check()
        if verbose: print('  cand', c, step, cv, max(r.size()), len(bad), bad[:1], flush=True)
        if not bad: return r, (step, cv)
    return None, None


if __name__ == '__main__':
    for k in [int(x) for x in sys.argv[1].split(',')]:
        fam = json.load(open('square_table.json'))[str(k)]; fam = fam[2] if len(fam) > 2 else 'slabP'
        t = time.time(); r, par = search(k, fam, '-v' in sys.argv)
        print(k, fam, 'flip best', max(r.size()) if r else None, par, round(time.time() - t, 1), flush=True)
