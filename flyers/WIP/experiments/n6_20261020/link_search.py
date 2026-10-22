"""Evaluate one link U->X in isolation: X's module placed relative to U's; route X's connector.
usage: python link_search.py LAYOUT U [xr] -> prints best relative placements by connector length."""
import sys, itertools, json
from multiprocessing import Pool
import os
import ring_designer as rd
from ring_designer import Ring, ORDER, NEXT, PREV, V1, V2, V3, V4, V5, V6, V9, hard_conflicts
rd.STRICT = os.environ.get('N6_STRICT') == '1'
LAY = {'V1': V1, 'V2': V2, 'V3': V3, 'V4': V4, 'V5': V5, 'V6': V6, 'V9': V9}
FAR = 60


def setup(name, U, rel):
    X = NEXT[U]
    place = {}
    for i, Y in enumerate(ORDER):
        place[Y] = (0, (FAR * (i + 1), FAR * (i + 1)), 0)
    place[U] = (0, (0, 0), 0)
    place[X] = rel
    return Ring(LAY[name], place), X


def ev(args):
    name, U, rel = args
    try:
        ring, X = setup(name, U, rel)
        if hard_conflicts(ring, first=True): return None
        conn = ring.route(X, maxlen=12)
        bad = [b for b in ring.check() if b[0] == X]
        if bad: return None
        return (len(ring.glue[X]), len(conn), rel)
    except Exception:
        return None


if __name__ == '__main__':
    name, U = sys.argv[1], sys.argv[2]
    rels = [(x, (oy, oz), s) for x in range(-5, 5) for oy in range(-6, 7) for oz in range(-6, 7) for s in range(8)]
    with Pool(int(os.environ.get('N6_PROCS', '4'))) as p:
        res = [r for r in p.imap_unordered(ev, [(name, U, r) for r in rels], chunksize=16) if r]
    res.sort()
    print(name, U, '->', NEXT[U], 'valid', len(res), 'of', len(rels))
    for r in res[:15]: print(r)
    json.dump(res, open(f"out/link_{name}_{U}{'_strict' if rd.STRICT else ''}.json", 'w'))
