"""Targeted link placements: put one of X's plate columns on a free exit column next to U's cluster, then CP.
usage: python link_exit.py LAYOUT U XS (e.g. -1,0)"""
import sys, json
from multiprocessing import Pool
from ring_designer import SYMS, NEXT
from link_cp import link_ring, body_cp, LAY
from ring_designer import route_cover

N4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def free_cols(mod, rad=3):
    P = set(map(tuple, mod['P'])); R = set(map(tuple, mod['R']))
    adj = lambda S: {(c[0] + a, c[1] + b) for c in S for a, b in N4}
    bad = P | R | adj(P) | adj(R)
    ys = [c[0] for c in P | R]; zs = [c[1] for c in P | R]
    return [(y, z) for y in range(min(ys) - rad, max(ys) + rad + 1) for z in range(min(zs) - rad, max(zs) + rad + 1)
            if (y, z) not in bad and any(((y + a, z + b) in adj(P)) for a, b in N4)]


def ev(a):
    name, U, rel = a
    try:
        ring, X = link_ring(name, U, rel)
        from ring_designer import hard_conflicts
        if hard_conflicts(ring, first=True): return None
        g = route_cover(ring, X, maxlen=8)
        r = body_cp(ring, X, margin=2, tl=20, workers=1, ub=g)
        if not r: return None
        bad = [b for b in ring.check() if (b[0] == X and 'not carried' not in b[2]) or (b[0] == U and 'carried by ' + X in b[2])]
        if bad: return None
        return (r[0], g, rel)
    except Exception:
        return None


if __name__ == '__main__':
    name, U = sys.argv[1], sys.argv[2]; xs = [int(v) for v in sys.argv[3].split(',')]
    mod = LAY[name]
    plate_cols = sorted({(c[1], c[2]) for c in mod['PLATE']})
    fc = free_cols(mod)
    rels = set()
    for f in fc:
        for s in range(8):
            for pc in plate_cols:
                ty, tz = SYMS[s](*pc)
                for x in xs: rels.add((x, (f[0] - ty, f[1] - tz), s))
    rels = sorted(rels)
    print(len(fc), 'free cols', len(rels), 'rels', flush=True)
    with Pool(4) as p: out = [r for r in p.imap_unordered(ev, [(name, U, r) for r in rels], chunksize=4) if r]
    out.sort()
    best = {}
    for r in out: best.setdefault(r[2][0], r)
    for x in sorted(best): print(x, best[x], [o for o in out if o[2][0] == x][:4])
    json.dump(out, open(f'out/exit_{name}_{U}.json', 'w'))
