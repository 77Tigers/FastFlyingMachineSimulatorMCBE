"""link table with coverage routing (no fixed contacts). usage: python link_cover.py LAYOUT U"""
import sys, json
from multiprocessing import Pool
from ring_designer import Ring, ORDER, NEXT, V4c, V1c, V5c, hard_conflicts, route_cover
LAY = {'V4c': V4c, 'V1c': V1c, 'V5c': V5c}
FAR = 60


def ev(args):
    name, U, rel = args
    X = NEXT[U]
    place = {Y: (0, (FAR * (i + 1), FAR * (i + 1)), 0) for i, Y in enumerate(ORDER)}
    place[U] = (0, (0, 0), 0); place[X] = rel
    try:
        ring = Ring(LAY[name], place)
        if hard_conflicts(ring, first=True): return None
        g = route_cover(ring, X, maxlen=8)
        if [b for b in ring.check() if (b[0] == X and 'not carried' not in b[2]) or (b[0] == U and 'carried by ' + X in b[2])]: return None
        return (g, rel)
    except Exception:
        return None


if __name__ == '__main__':
    name, U = sys.argv[1], sys.argv[2]
    rels = [(x, (oy, oz), s) for x in range(-5, 3) for oy in range(-6, 7) for oz in range(-6, 7) for s in range(8)]
    with Pool(4) as p:
        res = [r for r in p.imap_unordered(ev, [(name, U, r) for r in rels], chunksize=16) if r]
    res.sort()
    from collections import defaultdict
    m = defaultdict(lambda: 99)
    for g, rel in res: m[rel[0]] = min(m[rel[0]], g)
    print(name, U, 'valid', len(res), 'min by x', dict(sorted(m.items())))
    json.dump(res, open(f'out/cover_{name}_{U}.json', 'w'))
