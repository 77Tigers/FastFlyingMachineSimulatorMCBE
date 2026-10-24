"""two-stage link screen: straight-body cost with 3 corners, then full corner search for the best 30.
python link0_screen.py N K LAT MINSTEP"""
import sys, itertools
from concurrent.futures import ProcessPoolExecutor
import link0
from nk import bodies_for

CV3 = [(-2, 0), (0, -3), (2, 2), (-1, -2), (3, 0)]


def quick(a):
    k, mod, step = a
    best = None
    for cv in CV3:
        try: r = link0.back_ring(k, mod, step, cv, bodies_for(k) - 1)
        except (AssertionError, RuntimeError): continue
        if r is None: continue
        L = r.T.L; m = L // 4
        straight = max(r.size()[i] for i in range(L) if i % m not in (0, m - 1)) if m > 2 else max(r.size())
        sc = (straight, max(r.size()))
        if best is None or sc < best: best = sc
    return best


if __name__ == '__main__':
    n, k, lat, minstep = map(int, sys.argv[1:5])
    L = list(link0.links(n, lat=lat, minstep=minstep)); print(len(L), 'links', flush=True)
    with ProcessPoolExecutor(int(__import__("os").environ.get("L0W", 14))) as ex:
        q = list(ex.map(quick, [(k, mod, step) for mod, step, c in L], chunksize=8))
    cand = sorted([(qq, i) for i, qq in enumerate(q) if qq], key=lambda t: t[0])[:30]
    print('screen', [c[0] for c in cand[:10]], flush=True)
    with ProcessPoolExecutor(int(__import__("os").environ.get("L0W", 14))) as ex:
        full = list(ex.map(link0._ev, [(k, L[i][0], L[i][1]) for _, i in cand]))
    res = sorted([(f, L[i][1], L[i][0]) for (_, i), f in zip(cand, full) if f], key=lambda t: t[0][:2])
    for f, step, mod in res[:12]: print(f, step, mod, flush=True)
