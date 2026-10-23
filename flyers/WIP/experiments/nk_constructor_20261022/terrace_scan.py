"""scan terrace options per k (offline, like calibrate): python terrace_scan.py K1,K2,..."""
import sys, itertools
from concurrent.futures import ProcessPoolExecutor
import terrace as Tr, simk, square

def opts(k):
    for g in (2, 3):
        p = max(Tr.floor_sizes(k, g))
        a, b = Tr.strip_pattern(p)[2]
        for gap in (1, 2, 3):
            for cv in [(a - 1, b + d) for d in (0, 1, 2)]:
                yield g, gap, cv

def one(k):
    res = []
    for g, gap, cv in opts(k):
        try:
            r = Tr.build(k, g, gap, cv)
            if Tr.collisions(r, bodies=list(range(min(r.T.L, 2 * (r.T.L // 4) + 4)))): continue
            Tr.route_all(r)
        except (RuntimeError, AssertionError) as e:
            continue
        res.append((max(r.size()), g, gap, cv))
    res.sort()
    for sz, g, gap, cv in res[:6]:
        r = Tr.build(k, g, gap, cv); Tr.route_all(r)
        L = r.T.L; m = L // 4
        sub = sorted({(X + d) % L for X in (0, m, 2 * m, 3 * m) for d in range(-3, 4)})
        bad = r.check(sub)
        if bad: continue
        pl = sz + k; p = f'out/terr_{k}.flyer'; r.flyer(pl).save(p)
        ok, out = simk.flies(p, k, pl)
        if ok: return k, (pl, g, gap, cv), res[:3]
    return k, None, res[:3]

if __name__ == '__main__':
    ks = [int(x) for x in sys.argv[1].split(',')]
    with ProcessPoolExecutor(8) as ex:
        for k, best, top in ex.map(one, ks):
            print(k, best, top, flush=True)
