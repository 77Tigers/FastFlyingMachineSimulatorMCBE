"""CP-optimal X glue for the best greedy rels at each x offset. usage: python link_cp_scan.py LAYOUT U TOPK"""
import sys, json
from multiprocessing import Pool
from link_cp import link_ring, body_cp
from ring_designer import route_cover


def ev(a):
    name, U, rel = a
    ring, X = link_ring(name, U, rel)
    try:
        g = route_cover(ring, X, maxlen=8)
        r = body_cp(ring, X, margin=2, tl=20, workers=1, ub=g)
    except Exception:
        return None
    if not r: return None
    U_ = U
    bad = [b for b in ring.check() if (b[0] == X and 'not carried' not in b[2]) or (b[0] == U_ and 'carried by ' + X in b[2])]
    return (r[0], g, rel, len(bad))


if __name__ == '__main__':
    name, U, k = sys.argv[1], sys.argv[2], int(sys.argv[3])
    res = json.load(open(f'out/cover_{name}_{U}.json'))
    byx = {}
    for g, rel in res: byx.setdefault(rel[0], []).append((g, (rel[0], tuple(rel[1]), rel[2])))
    jobs = [(name, U, rel) for x in sorted(byx) for g, rel in sorted(byx[x])[:k]]
    with Pool(4) as p: out = [r for r in p.map(ev, jobs) if r]
    best = {}
    for r in out:
        if r[3] == 0 and (r[2][0] not in best or r[0] < best[r[2][0]][0]): best[r[2][0]] = r
    for x in sorted(best): print(x, best[x])
    json.dump(out, open(f'out/cp_{name}_{U}.json', 'w'))
