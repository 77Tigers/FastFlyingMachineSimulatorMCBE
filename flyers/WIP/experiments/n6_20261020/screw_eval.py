"""Screw-ring estimate per module: link cost c(t, sym, s) for sym in {1,3}, s in 0..5, |t|<=R;
the four links share (t, sym); pick s pattern with sum 10 minimizing the max cost.
usage: python screw_eval.py MODJSON TOPN PROCS R OUT"""
import sys, json, itertools
from multiprocessing import Pool
from module_eval import ev, mod_of

if __name__ == '__main__':
    rows = json.load(open(sys.argv[1]))[:int(sys.argv[2])]
    procs, R, out = int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    jobs = []
    for i, r in enumerate(rows):
        mod = mod_of(r[3], r[4], r[5])
        for s in range(0, 6):
            for sym in (1, 3):
                for oy in range(-R, R + 1):
                    for oz in range(-R, R + 1):
                        jobs.append((i, mod, (s - 3, (oy, oz), sym)))
    with Pool(procs) as p: res = [x for x in p.imap_unordered(ev, jobs, chunksize=64) if x]
    c = {}
    for i, s, g, rel in res: c[(i, tuple(rel[1]), rel[2], s)] = g
    pats = [ss for ss in itertools.product(range(6), repeat=4) if sum(ss) == 10]
    summary = []
    for i, r in enumerate(rows):
        best = (99, None)
        keys = {(t, sym) for (j, t, sym, s) in c if j == i}
        for t, sym in keys:
            cs = [c.get((i, t, sym, s), 99) for s in range(6)]
            v = min((max(cs[s] for s in ss), ss) for ss in pats)
            if v[0] < best[0]: best = (v[0], (t, sym, v[1], cs))
        nrb = len(r[4])
        summary.append((best[0] + nrb + 6 if best[0] < 99 else 999, r[0], r[3], r[4], r[5], best[1]))
        print(i, 'base', r[0], 'screw load', summary[-1][0], best[1], flush=True)
    summary.sort(key=lambda x: x[0])
    json.dump(summary, open(out, 'w'))
