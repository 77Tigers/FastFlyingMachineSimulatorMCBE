import sys, json, itertools, collections
import ring_designer as rd
from ring_designer import Ring, route_all, hard_conflicts
from close_ring import chain, apply, INV
from module_eval import mod_of
rd.STRICT = True
tab = json.load(open('out/v9_linkfull.json')); r = json.load(open('out/hand_modules.json'))[0]
mod = mod_of(r[3], r[4], r[5])
best = {}
for g, rel in tab:
    k = (rel[0], tuple(rel[1]), rel[2]); best[k] = min(best.get(k, 99), g)
good = [(g, k) for k, g in best.items() if g <= 16]
dset = {(k[0] + 2, k[1], k[2]): g for g, k in good}
reasons = collections.Counter(); n = 0
for (g0, r0), (g1, r1), (g2, r2) in itertools.product(good, repeat=3):
    place, _ = chain([r0, r1, r2, (0, (0, 0), 0)])
    xd, (dy, dz), sd = place['D']
    rel3 = (-xd, apply(INV[sd], (-dy, -dz)), INV[sd])
    if rel3 not in dset: continue
    n += 1
    if n > 300: break
    place, _ = chain([r0, r1, r2, rel3]); place = {k: (v[0], tuple(v[1]), v[2]) for k, v in place.items()}
    ring = Ring(mod, place)
    h = hard_conflicts(ring, first=True)
    if h: reasons['hard ' + h[0][2]] += 1; continue
    try: sz = route_all(ring)
    except Exception as e: reasons['route'] += 1; continue
    bad = ring.check()
    if bad: reasons['check ' + bad[0][2].split(' ')[1] if ' ' in bad[0][2] else bad[0][2]] += 1; continue
    reasons['ok'] += 1
print(n, reasons.most_common(12))
