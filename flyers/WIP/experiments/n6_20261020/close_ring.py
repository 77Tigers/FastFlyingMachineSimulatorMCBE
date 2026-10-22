"""Combine per-link placement tables (out/link_LAY_U.json) into closed rings; verify the full ring.
usage: python close_ring.py LAYOUT MAXGLUE [LIMIT]"""
import sys, json, itertools
from collections import defaultdict
from ring_designer import Ring, ORDER, NEXT, SYMS, V4, V1, V3, V5, V6, route_all, hard_conflicts
LAY = {'V1': V1, 'V3': V3, 'V4': V4, 'V5': V5, 'V6': V6}

# compose lattice symmetries: SYMS[i] then SYMS[j] -> index
def apply(i, yz): return SYMS[i](*yz)
COMP = {}
for i in range(8):
    for j in range(8):
        pts = [(1, 2), (3, 5)]
        img = [apply(j, apply(i, p)) for p in pts]   # first i (inner), then j (outer)
        COMP[i, j] = next(k for k in range(8) if [apply(k, p) for p in pts] == img)


INV = {i: next(j for j in range(8) if all(apply(j, apply(i, p)) == p for p in [(1, 2), (3, 5)])) for i in range(8)}


def chain(rels):
    """rels: link rel for A->B, B->C, C->D, D->A (X relative to U at sym 0). returns placement of A..D and closure error"""
    place = {'A': (0, (0, 0), 0)}
    for U, rel in zip(ORDER, rels):
        X = NEXT[U]
        xu, (uy, uz), su = place[U]
        dx, (ry, rz), rs = rel
        oy, oz = apply(su, (ry, rz))
        pX = (xu + dx, (uy + oy, uz + oz), COMP[rs, su])
        if X == 'A': return place, pX
        place[X] = pX
    raise RuntimeError


if __name__ == '__main__':
    name, maxg = sys.argv[1], int(sys.argv[2]); lim = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    tabs = []
    for U in ORDER:
        res = json.load(open(f'out/link_{name}_{U}.json'))
        best = {}
        for g, c, r in res:
            if g <= maxg:
                k = (r[0], tuple(r[1]), r[2]); best[k] = min(best.get(k, 99), g)
        tabs.append(sorted((g, k) for k, g in best.items())[:int(sys.argv[4]) if len(sys.argv) > 4 else 300])
        print(U, len(tabs[-1]), 'links <=', maxg)
    # index last link by required value: need D->A rel such that chain closes
    found = []
    idx = defaultdict(list)
    for g, rel in tabs[3]: idx[rel].append(g)
    for (g0, r0), (g1, r1), (g2, r2) in itertools.product(tabs[0], tabs[1], tabs[2]):
        place, _ = chain([r0, r1, r2, (0, (0, 0), 0)])
        # required D->A rel: A at (0,(0,0),0) = D + rot_sD(rel)
        xd, (dy, dz), sd = place['D']
        inv = next(k for k in range(8) if COMP[k, sd] == 0)    # rel sym s with COMP[s, sd] == 0
        # rel yz with apply(sd, rel) = -(dy,dz)
        need = apply(INV[sd], (-dy, -dz))
        rel3 = (-xd, need, inv)
        if rel3 in idx:
            found.append((max(g0, g1, g2, min(idx[rel3])), g0 + g1 + g2 + min(idx[rel3]), [r0, r1, r2, rel3]))
    found.sort()
    print('closed candidates', len(found))
    seen = 0
    for mx, tot, rels in found[:lim]:
        place, _ = chain(rels)
        place = {k: (v[0], tuple(v[1]), v[2]) for k, v in place.items()}
        try:
            ring = Ring(LAY[name], place)
            if hard_conflicts(ring, first=True): continue
            sz = route_all(ring)
            if ring.check(): continue
        except Exception as e:
            continue
        print('pair-est', mx, tot, 'full', sz, place, flush=True)
        seen += 1
        if seen >= 10: break
