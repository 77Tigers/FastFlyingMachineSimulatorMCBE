"""5-pusher modules for the slot-7-pull hybrid: enumerate nR RBs + 5 pushers (each pusher lateral to an RB,
plate = P+R columns connected) and score plate + RB + CP-minimal predecessor cover (cluster_search.cover_cost),
plus a flag whether a lateral cover column exists where the host's sticky could sit (free column at x=1 above a
x=-2 cover cell, lateral to a P plate cell, not R-adjacent). usage: python cluster5.py G NR [workers] [tl]"""
import sys, pathlib, itertools
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import cluster_search as cs
from cluster_search import nb, canon


def clusters(G, nR, nP=5):
    cells = [(y, z) for y in range(G) for z in range(G)]
    seen = set()
    for R in itertools.combinations(cells, nR):
        if any(b in nb(a) for a, b in itertools.combinations(R, 2)): continue
        adj = sorted({c for r in R for c in nb(r)} - set(R))
        for P in itertools.combinations(adj, nP):
            plate = set(P) | set(R)
            st = [P[0]]; vis = set()
            while st:
                u = st.pop()
                if u in vis: continue
                vis.add(u); st += [v for v in nb(u) if v in plate]
            if len(vis) != len(plate): continue
            key = canon(P, R)
            if key in seen: continue
            seen.add(key); yield P, R


if __name__ == '__main__':
    G, nR = int(sys.argv[1]), int(sys.argv[2])
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 2; tl = float(sys.argv[4]) if len(sys.argv) > 4 else 6
    out = []
    cl = list(clusters(G, nR)); print(len(cl), 'clusters', flush=True)
    for P, R in cl:
        r = cs.cover_cost(P, R, tl=tl, workers=w)
        if not r: continue
        Radj = {c for q in R for c in nb(q)}
        cover = r[2]
        sticky = [c[1:] for c in cover if c[0] == -2 and c[1:] not in Radj and any(n in P for n in nb(c[1:]))]
        base = len(P) + len(R) + len(R) + r[0]
        out.append((base, r[0], r[1], P, R, cover, sticky))
    out.sort(key=lambda o: o[0])
    for o in out[:15]: print('base', o[0], 'cover', o[1], o[2], 'P', o[3], 'R', o[4], 'cover', o[5], 'sticky cols', o[6])
