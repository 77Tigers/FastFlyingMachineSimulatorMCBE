"""Clusters with plate = P + one RB front (7 cells) and the other RB attached by the rising connector:
R2 needs a free lateral column c (not P/R) that is also next to a P column (connector top joins that front)."""
import itertools, sys
from cluster_search import nb, canon, cover_cost

if __name__ == '__main__':
    G = int(sys.argv[1])
    cells = [(y, z) for y in range(G) for z in range(G)]
    seen = set(); out = []
    for R in itertools.permutations(cells, 2):
        R1, R2 = R
        if R2 in nb(R1): continue
        adj = sorted({c for r in R for c in nb(r)} - set(R))
        for P in itertools.combinations(adj, 6):
            plate = set(P) | {R1}
            st = [P[0]]; vis = set()
            while st:
                u = st.pop()
                if u in vis: continue
                vis.add(u); st += [v for v in nb(u) if v in plate]
            if len(vis) != 7: continue
            cs = [c for c in nb(R2) if c not in P and c not in R and any(q in P for q in nb(c))]
            if not cs: continue
            key = (canon(P, R), R1)
            if key in seen: continue
            seen.add(key)
            r = cover_cost(P, R, tl=4)
            if r: out.append((r[0], r[1], P, R1, R2, cs))
    out.sort()
    print(len(out), 'clusters')
    for o in out[:12]: print(o)
