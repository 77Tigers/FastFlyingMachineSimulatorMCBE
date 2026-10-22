"""CP-polish top greedy rels of a link table at given x offsets. usage: python polish.py LAYOUT U XS TOPK"""
import sys, json
from multiprocessing import Pool
from link_cp import link_ring, body_cp
from ring_designer import route_all


def ev(a):
    name, U, rel, g0 = a
    try:
        ring, X = link_ring(name, U, rel)
        ring.route(X, maxlen=12)
        r = body_cp(ring, X, margin=2, tl=40, workers=1, ub=len(ring.glue[X]))
        if not r: return None
        bad = [b for b in ring.check() if (b[0] == X and 'not carried' not in b[2]) or (b[0] == U and 'carried by ' + X in b[2])]
        return (r[0], g0, rel, r[1], len(bad))
    except Exception as e:
        return None


if __name__ == '__main__':
    name, U = sys.argv[1], sys.argv[2]; xs = [int(v) for v in sys.argv[3].split(',')]; k = int(sys.argv[4])
    res = json.load(open(f'out/link_{name}_{U}.json'))
    jobs = []
    for x in xs:
        rows = sorted([r for r in res if r[2][0] == x])[:k]
        jobs += [(name, U, (r[2][0], tuple(r[2][1]), r[2][2]), r[0]) for r in rows]
    with Pool(4) as p: out = [r for r in p.map(ev, jobs) if r]
    out.sort()
    for r in out[:12]: print(r)
    json.dump(out, open(f'out/polish_{name}_{U}.json', 'w'))
