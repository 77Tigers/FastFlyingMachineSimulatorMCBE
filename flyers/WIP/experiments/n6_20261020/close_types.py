"""4-body rings with a module type per body from mixed link tables out/mix_{a}_{b}.json (link A->B convention).
usage: python close_types.py MODS.json TYPES(comma) MAXG LIMIT"""
import sys, json, itertools, os
from collections import defaultdict
import ring_designer as rd
from ring_designer import Ring, route_all, hard_conflicts
from close_ring import chain, apply, INV
from module_eval import mod_of
from try_ring import sim, OUT
rd.STRICT = True
rows = json.load(open(sys.argv[1])); types = [int(v) for v in sys.argv[2].split(',')]
maxg, lim = int(sys.argv[3]), int(sys.argv[4])
mods_by = {i: mod_of(*rows[i][3:6]) for i in types}
tabs = {}
for a in types:
    for b in types:
        fn = f'out/mix_{a}_{b}.json'
        if not os.path.exists(fn): continue
        best = {}
        for g, rel in json.load(open(fn)):
            k = (rel[0], tuple(rel[1]), rel[2]); best[k] = min(best.get(k, 99), g)
        bys = defaultdict(list)
        for k, g in best.items():
            if g <= maxg: bys[k[0] + 3].append((g, k))
        tabs[a, b] = bys
cands = []
for seq in itertools.product(types, repeat=4):
    if seq[0] != min(seq): continue
    links = [(seq[i], seq[(i + 1) % 4]) for i in range(4)]
    if any(l not in tabs for l in links): continue
    for ss in itertools.product(range(6), repeat=4):
        if sum(ss) != 10: continue
        L = [tabs[links[i]].get(ss[i], []) for i in range(4)]
        if any(not l for l in L): continue
        dset = {(k[0] + 2, k[1], k[2]): g for g, k in L[3]}
        for (g0, r0), (g1, r1), (g2, r2) in itertools.product(L[0], L[1], L[2]):
            place, _ = chain([r0, r1, r2, (0, (0, 0), 0)])
            xd, (dy, dz), sd = place['D']
            rel3 = (-xd, apply(INV[sd], (-dy, -dz)), INV[sd])
            if rel3 in dset:
                cands.append((max(g0, g1, g2, dset[rel3]), seq, [r0, r1, r2, rel3]))
cands.sort(key=lambda c: c[0])
print(len(cands), 'closed candidates', flush=True)
done = 0
for mx, seq, rels in cands:
    place, _ = chain(rels); place = {k: (v[0], tuple(v[1]), v[2]) for k, v in place.items()}
    mods = {X: mods_by[t] for X, t in zip('ABCD', seq)}
    ring = Ring(mods, place)
    if hard_conflicts(ring, first=True): continue
    try: sz = route_all(ring)
    except Exception: continue
    if ring.check(): continue
    ld = {X: len(ring.glue[X]) + len(mods[X]['R']) + 6 for X in 'ABCD'}
    print('seq', seq, 'glue', sz, 'load', ld, rels, flush=True)
    if max(ld.values()) <= 25:
        tag = f'types_{"".join(map(str, seq))}_{done}'
        ring.flyer(40).save(str(OUT / f'{tag}.flyer')); print('  sim', sim(OUT / f'{tag}.flyer'), tag, flush=True)
        json.dump({'place': place, 'seq': seq}, open(OUT / f'{tag}.json', 'w'))
    done += 1
    if done >= lim: break
