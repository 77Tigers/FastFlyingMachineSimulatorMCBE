"""Alternating-module rings A(m0) B(m1) C(m0) D(m1) from mixed link tables.
usage: python close_mixed.py MODS.json I0 I1 MAXG LIMIT"""
import sys, json, itertools
import ring_designer as rd
from ring_designer import Ring, route_all, hard_conflicts
from close_ring import chain, apply, INV
from module_eval import mod_of
from try_ring import sim, OUT
rd.STRICT = True
rows = json.load(open(sys.argv[1])); i0, i1 = int(sys.argv[2]), int(sys.argv[3])
maxg, lim = int(sys.argv[4]), int(sys.argv[5])
m0, m1 = mod_of(*rows[i0][3:6]), mod_of(*rows[i1][3:6])


def load(fn):
    best = {}
    for g, rel in json.load(open(fn)):
        k = (rel[0], tuple(rel[1]), rel[2]); best[k] = min(best.get(k, 99), g)
    return [(g, k) for k, g in best.items() if g <= maxg]
t01 = load(f'out/mix_{i0}_{i1}.json'); t10 = load(f'out/mix_{i1}_{i0}.json')
print(len(t01), len(t10), 'links')
dset = {(k[0] + 2, k[1], k[2]): g for g, k in t10}
found = []
for (g0, r0), (g1, r1), (g2, r2) in itertools.product(t01, t10, t01):
    place, _ = chain([r0, r1, r2, (0, (0, 0), 0)])
    xd, (dy, dz), sd = place['D']
    rel3 = (-xd, apply(INV[sd], (-dy, -dz)), INV[sd])
    if rel3 in dset: found.append((max(g0, g1, g2, dset[rel3]), g0 + g1 + g2 + dset[rel3], [r0, r1, r2, rel3]))
found.sort(); print(len(found), 'closed')
mods = {'A': m0, 'B': m1, 'C': m0, 'D': m1}
done = tried = 0
for mx, tot, rels in found:
    place, _ = chain(rels); place = {k: (v[0], tuple(v[1]), v[2]) for k, v in place.items()}
    tried += 1
    ring = Ring(mods, place)
    if hard_conflicts(ring, first=True): continue
    try: sz = route_all(ring)
    except Exception: continue
    if ring.check(): continue
    ld = {X: len(ring.glue[X]) + len(mods[X]['R']) + 6 for X in 'ABCD'}
    print('est', mx, 'glue', sz, 'load', ld, rels, flush=True)
    if max(ld.values()) <= 25:
        tag = f'mix{i0}{i1}_{done}'
        ring.flyer(40).save(str(OUT / f'{tag}.flyer')); print('  sim', sim(OUT / f'{tag}.flyer'), tag, flush=True)
        json.dump({'place': place, 'i0': i0, 'i1': i1}, open(OUT / f'{tag}.json', 'w'))
    done += 1
    if done >= lim: break
print('tried', tried)
