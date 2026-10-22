"""Clusters with NR redstone blocks: score = plate(P+R, must be connected) + NR + cover/exit (cluster_search.cover_cost)."""
import itertools, sys
from cluster_search import nb, canon, cover_cost


def clusters(G, NR):
    cells = [(y, z) for y in range(G) for z in range(G)]
    seen = set()
    for R in itertools.combinations(cells, NR):
        if any(b in nb(a) for a, b in itertools.combinations(R, 2)): continue
        adj = sorted({c for r in R for c in nb(r)} - set(R))
        for P in itertools.combinations(adj, 6):
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
    G, NR = int(sys.argv[1]), int(sys.argv[2])
    cl = list(clusters(G, NR)); print(len(cl), 'clusters', flush=True)
    out = []
    for P, R in cl:
        r = cover_cost(P, R, tl=3)
        if r: out.append((len(P) + 2 * len(R) + r[0], r[0], r[1], P, R))
    out.sort()
    for o in out[:10]: print(o)
