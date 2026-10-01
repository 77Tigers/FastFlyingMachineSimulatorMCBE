"""Rip-up and re-route each body (Steiner over its terminals) to shrink glue; keeps the result only if
abcheck passes. usage: abreroute.py Aw Bw seed outfile"""
import sys, random
from abpr import *
from abre import rebuild


def reroute(Aw, Bw, seed, rounds=30):
    lay = Lay2(Aw, Bw)
    cols = valid_colorings(lay)
    glue = cols[seed % len(cols)]
    inc, err = place_route(lay, seed, glue)
    assert inc is not None, err
    rnd = random.Random(seed)
    def size(): return {b: len(inc.req[b]) for b in lay.bodies}
    best = max(size().values())
    for it in range(rounds):
        b = max(lay.bodies, key=lambda x: len(inc.req[x]) + rnd.random())
        snap = inc.snapshot()
        old = set(inc.req[b])
        terms = list(inc.terms[b])
        # remove non-terminal cells of b
        for c in old - set(terms):
            del inc.req[b][c]
            for k in range(lay.L): inc.occ[k].pop((c[0] + lay.off(b, k), c[1], c[2]), None)
        # greedy Steiner from a random terminal
        rnd.shuffle(terms)
        conn = {terms[0]}; ok = True
        for t in terms[1:]:
            if t in conn: continue
            path = inc.path_to(b, [t], conn, maxnodes=6000)
            if path is None: ok = False; break
            for q in path + [t]:
                if q not in inc.req[b]:
                    inc.req[b][q] = 1
                    for k in range(lay.L): inc.occ[k][(q[0] + lay.off(b, k), q[1], q[2])] = b
                conn.add(q)
        if ok: ok = partial_ok(inc)
        if not ok or len(inc.req[b]) >= len(old):
            inc.restore(snap); continue
        print('round', it, b, len(old), '->', len(inc.req[b]), flush=True)
    return lay, inc, glue


if __name__ == '__main__':
    Aw = sys.argv[1].split(','); Bw = sys.argv[2].split(',')
    lay, inc, glue = reroute(Aw, Bw, int(sys.argv[3]))
    req = {b: dict(inc.req[b]) for b in lay.bodies}
    pist = [dict(kind=p['kind'], f=p['f'], victim=p['victim'], yz=p['yz'], xi=p['xi']) for p in inc.pist]
    wd = World(lay, req, pist, inc.sources, glue=glue)
    pr = check(wd)
    print('check', len(pr), pr[:3])
    print({b: len(wd.cells[b]) for b in lay.bodies})
    wd.flyer(limit=250).save(sys.argv[4])
