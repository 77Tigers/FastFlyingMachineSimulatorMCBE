"""screen rule-built back links (link0.links, n = k-1 hoppers) whose straight step leaves room for towers:
|step| >= W along one axis. Same two stages as link0_screen. python stack_links.py K W [LAT]"""
import sys, os
from concurrent.futures import ProcessPoolExecutor
import link0, link0_screen


if __name__ == '__main__':
    k, W = int(sys.argv[1]), int(sys.argv[2])
    lat = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    L = [(m, st, c) for m, st, c in link0.links(k - 1, lat=lat, minstep=2) if max(abs(st[0]), abs(st[1])) >= W]
    print(len(L), 'links', flush=True)
    with ProcessPoolExecutor(int(os.environ.get('L0W', 14))) as ex:
        q = list(ex.map(link0_screen.quick, [(k, m, st) for m, st, c in L], chunksize=8))
    cand = sorted([(qq, i) for i, qq in enumerate(q) if qq], key=lambda t: t[0])[:30]
    print('screen', [c[0] for c in cand[:10]], flush=True)
    with ProcessPoolExecutor(int(os.environ.get('L0W', 14))) as ex:
        full = list(ex.map(link0._ev, [(k, L[i][0], L[i][1]) for _, i in cand]))
    res = sorted([(f, L[i][1], L[i][0]) for (_, i), f in zip(cand, full) if f], key=lambda t: t[0][:2])
    for f, step, mod in res[:12]: print(f, step, mod, flush=True)
