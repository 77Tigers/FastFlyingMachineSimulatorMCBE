"""Close rings from one physical link table (link A; D's x shifted +2). usage: python close2.py TABLE MODJSON IDX MAXG LIMIT"""
import sys, json, itertools
from collections import defaultdict
import ring_designer as rd
from ring_designer import Ring, route_all, route2_all, hard_conflicts
from close_ring import chain, apply, INV
from module_eval import mod_of
from try_ring import sim, OUT

rd.STRICT = True
tab = json.load(open(sys.argv[1])); r = json.load(open(sys.argv[2]))[int(sys.argv[3])]
maxg, lim = int(sys.argv[4]), int(sys.argv[5])
mod = mod_of(r[3], r[4], r[5])
best = {}
for g, rel in tab:
    k = (rel[0], tuple(rel[1]), rel[2]); best[k] = min(best.get(k, 99), g)
good = [(g, k) for k, g in best.items() if g <= maxg]
print(len(good), 'links <=', maxg)
dset = {(k[0] + 2, k[1], k[2]): g for g, k in good}
found = []
for (g0, r0), (g1, r1), (g2, r2) in itertools.product(good, repeat=3):
    place, _ = chain([r0, r1, r2, (0, (0, 0), 0)])
    xd, (dy, dz), sd = place['D']
    rel3 = (-xd, apply(INV[sd], (-dy, -dz)), INV[sd])
    if rel3 in dset:
        found.append((max(g0, g1, g2, dset[rel3]), g0 + g1 + g2 + dset[rel3], [r0, r1, r2, rel3]))
found.sort()
print(len(found), 'closed')
done = 0
for mx, tot, rels in found:
    place, back = chain(rels)
    place = {k: (v[0], tuple(v[1]), v[2]) for k, v in place.items()}
    try:
        ring = Ring(mod, place)
        if hard_conflicts(ring, first=True): continue
        sz = route_all(ring)
        bad = ring.check()
        if bad: continue
    except Exception:
        continue
    m = max(sz.values()) + len(mod['R']) + 6
    print('est', mx, tot, 'full', sz, 'load', m, rels, flush=True)
    if m <= 25:
        tag = 'c2_' + '_'.join(str(v) for v in sz.values()) + f'_{done}'
        ring.flyer(40).save(str(OUT / f'{tag}.flyer'))
        print('  sim', sim(OUT / f'{tag}.flyer'), tag, flush=True)
    done += 1
    if done >= lim: break
