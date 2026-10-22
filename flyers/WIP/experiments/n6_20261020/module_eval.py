"""Per-link cost curve c(s) for candidate modules (strict, link A, x = -3 + s).
usage: python module_eval.py CLUSTERS.json TOPN PROCS   (json rows: [score, cover, status, P, R, coverCells])"""
import sys, json, os
from multiprocessing import Pool
import ring_designer as rd
from ring_designer import Ring, ORDER, NEXT, hard_conflicts
rd.STRICT = True
FAR = 60


def mod_of(P, R, S):
    m = dict(R=[tuple(r) for r in R], P=[tuple(p) for p in P])
    m['PLATE'] = [(1,) + tuple(c) for c in m['P'] + m['R']]
    m['CONT'] = [tuple(c) for c in S]
    return m


def ev(a):
    mid, mod, rel = a
    U, X = 'A', 'B'
    place = {Y: (0, (FAR * (i + 1), FAR * (i + 1)), 0) for i, Y in enumerate(ORDER)}
    place[U] = (0, (0, 0), 0); place[X] = rel
    try:
        ring = Ring(mod, place)
        if hard_conflicts(ring, first=True): return None
        ring.route(X, maxlen=10)
        bad = [b for b in ring.check() if (b[0] == X and 'not carried' not in b[2]) or (b[0] == U and 'carried by ' + X in b[2])]
        if bad: return None
        return (mid, rel[0] + 3, len(ring.glue[X]), rel)
    except Exception:
        return None


if __name__ == '__main__':
    rows = json.load(open(sys.argv[1]))[:int(sys.argv[2])]
    procs = int(sys.argv[3])
    jobs = []
    mods = []
    for i, r in enumerate(rows):
        mod = mod_of(r[3], r[4], r[5]); mods.append(mod)
        for s in range(0, 5):
            for sym in range(8):
                for oy in range(-7, 8):
                    for oz in range(-7, 8):
                        jobs.append((i, mod, (s - 3, (oy, oz), sym)))
    with Pool(procs) as p: res = [r for r in p.imap_unordered(ev, jobs, chunksize=32) if r]
    best = {}
    for mid, s, g, rel in res:
        k = (mid, s)
        if k not in best or g < best[k][0]: best[k] = (g, rel)
    out = []
    for i, r in enumerate(rows):
        curve = [best.get((i, s), (99,))[0] for s in range(5)]
        nrb = len(r[4])
        # best ring estimate: choose s_i with sum 10 over 4 bodies minimizing max(glue + nrb)
        import itertools
        opts = [(max(curve[s] for s in ss) + nrb, ss) for ss in itertools.product(range(5), repeat=4) if sum(ss) == 10]
        est = min(opts)
        out.append((est[0], curve, nrb, r[3], r[4], r[5], {s: best.get((i, s), (99, None))[1] for s in range(5)}))
        print(i, 'base', r[0], 'curve', curve, 'nRB', nrb, 'est load-6', est, flush=True)
    out.sort(key=lambda o: o[0])
    json.dump(out, open(sys.argv[1].replace('.json', '_eval.json'), 'w'))
