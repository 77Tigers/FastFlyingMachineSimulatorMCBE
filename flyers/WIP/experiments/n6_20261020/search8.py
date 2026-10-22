"""8-body alternating rings (m0,m1)x4 built from a 4-link unit with net 180-degree rotation (closes automatically).
usage: python search8.py MODS.json I0 I1 MAXG PROCS"""
import sys, json, itertools
from multiprocessing import Pool
import ring_designer as rd
from ring_designer import Ring, route_all, hard_conflicts, set_bodies
from close_ring import chain, COMP
from module_eval import mod_of
rd.STRICT = True
set_bodies(8)


def load(fn, maxg):
    best = {}
    for g, rel in json.load(open(fn)):
        k = (rel[0], tuple(rel[1]), rel[2]); best[k] = min(best.get(k, 99), g)
    return [(g, k) for k, g in best.items() if g <= maxg]


def ev(a):
    mods, rels = a
    try:
        place, back = chain(rels + rels)
        if back != (0, (0, 0), 0): return None
        place = {k: (v[0], tuple(v[1]), v[2]) for k, v in place.items()}
        ring = Ring(mods, place)
        if hard_conflicts(ring, first=True): return None
        sz = route_all(ring)
        if ring.check(): return None
        ld = max(len(ring.glue[X]) + len(mods[X]['R']) + 6 for X in mods)
        return (ld, sz, rels, place)
    except Exception:
        return None


if __name__ == '__main__':
    rows = json.load(open(sys.argv[1])); i0, i1 = int(sys.argv[2]), int(sys.argv[3])
    maxg, procs = int(sys.argv[4]), int(sys.argv[5])
    m0, m1 = mod_of(*rows[i0][3:6]), mod_of(*rows[i1][3:6])
    mods = {X: (m0, m1)[i % 2] for i, X in enumerate('ABCDEFGH')}
    t01 = load(f'out/mix_{i0}_{i1}.json', maxg); t10 = load(f'out/mix_{i1}_{i0}.json', maxg)
    # sum s = 10 over the unit with s<=3: keep only the stretches that can participate
    S01 = {int(v) for v in sys.argv[6].split(',')} if len(sys.argv) > 6 else {0}
    S10 = {int(v) for v in sys.argv[7].split(',')} if len(sys.argv) > 7 else {-1}
    t01 = [x for x in t01 if x[1][0] in S01]; t10 = [x for x in t10 if x[1][0] in S10]
    print(len(t01), len(t10), 'links', flush=True)
    units = []
    for (g0, r0), (g1, r1), (g2, r2), (g3, r3) in itertools.product(t01, t10, t01, t10):
        r3 = (r3[0] + 2, r3[1], r3[2])
        if r0[0] + r1[0] + r2[0] + r3[0] != 0: continue
        s = 0
        for r in (r0, r1, r2, r3): s = COMP[r[2], s]
        if s != 2: continue
        units.append([r0, r1, r2, r3])
    print(len(units), 'units', flush=True)
    with Pool(procs) as p:
        res = [r for r in p.imap_unordered(ev, [(mods, u) for u in units], chunksize=8) if r]
    res.sort(key=lambda r: r[0])
    print(len(res), 'valid rings')
    for r in res[:10]: print(r[0], r[1], r[2])
    json.dump([(r[0], r[2]) for r in res[:50]], open(f'out/ring8_{i0}_{i1}.json', 'w'))
