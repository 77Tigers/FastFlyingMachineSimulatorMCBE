"""Clusters powered by a rod hard-powering an own glue cell C (rod soft-powers its laterals, C powers its laterals),
optionally plus RBs. score = plate(P fronts + C front + RB fronts, must be connected) + C + rod + RBs + cover.
usage: python cluster_rod.py G NRB PROCS TL"""
import sys, json, itertools, os
from multiprocessing import Pool
from cluster_search import nb, cover_cost, canon


def gen(G, nrb):
    cells = [(y, z) for y in range(G) for z in range(G)]
    seen = set()
    for r in cells:
        for c in nb(r):
            for Q in itertools.combinations([q for q in cells if q not in (r, c)], nrb):
                powered = set(nb(r)) | set(nb(c)) | {x for q in Q for x in nb(q)}
                powered -= {r, c} | set(Q)
                for P in itertools.combinations(sorted(powered), 6):
                    for extra in ((), (r,)):
                        plate = set(P) | {c} | set(Q) | set(extra)
                        st = [P[0]]; vis = set()
                        while st:
                            u = st.pop()
                            if u in vis: continue
                            vis.add(u); st += [v for v in nb(u) if v in plate]
                        if len(vis) != len(plate): continue
                        key = canon(P, (r, c) + tuple(Q)) + (canon([c], [r]), len(extra))
                        if key in seen: break
                        seen.add(key); yield P, r, c, Q, len(extra); break


def ev(a):
    P, r, c, Q, ex, tl = a
    res = cover_cost(P, [r, c] + list(Q), tl=tl, workers=2)
    if not res: return None
    plate = 6 + 1 + len(Q) + ex
    return (plate + 1 + 1 + len(Q) + res[0], res[0], P, r, c, Q, res[2])


if __name__ == '__main__':
    G, nrb, procs, tl = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
    cl = list(gen(G, nrb)); print(len(cl), 'clusters', flush=True)
    with Pool(procs) as p: out = sorted(x for x in p.imap_unordered(ev, [c + (tl,) for c in cl], chunksize=4) if x)
    for o in out[:12]: print(o[:6])
    json.dump(out[:200], open(f'out/rodclusters_G{G}_R{nrb}.json', 'w'))
