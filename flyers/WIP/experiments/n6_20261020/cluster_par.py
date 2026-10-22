"""Parallel cluster search: NR RBs, 6 pushers on a GxG grid; score = |P|+|R| plate + NR + cover/exit.
usage: python cluster_par.py G NR PROCS TL"""
import sys, json
from multiprocessing import Pool
from cluster_search3 import clusters
import os
import cluster_search
cluster_search.EXIT2 = os.environ.get('N6_EXIT2') == '1'
from cluster_search import cover_cost


def ev(a):
    P, R, tl = a
    r = cover_cost(P, R, tl=tl, workers=int(os.environ.get('N6_W', '2')))
    if not r: return None
    return (len(P) + 2 * len(R) + r[0], r[0], r[1], P, R, r[2])


if __name__ == '__main__':
    G, NR, procs, tl = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
    cl = list(clusters(G, NR)); print(len(cl), 'clusters', flush=True)
    with Pool(procs) as p: out = [r for r in p.imap_unordered(ev, [(P, R, tl) for P, R in cl], chunksize=4) if r]
    out.sort()
    for o in out[:15]: print(o[:5])
    json.dump(out[:300], open(f"out/clusters_G{G}_R{NR}{'_x2' if cluster_search.EXIT2 else ''}.json", 'w'))
