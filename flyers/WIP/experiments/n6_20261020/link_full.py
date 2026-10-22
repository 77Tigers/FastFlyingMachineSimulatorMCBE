"""Full strict link-A table for one module (x = s-3, s in 0..4, offsets +-R, all syms).
usage: python link_full.py MODJSON INDEX PROCS R OUT"""
import sys, json
from multiprocessing import Pool
from module_eval import ev, mod_of

if __name__ == '__main__':
    rows = json.load(open(sys.argv[1])); r = rows[int(sys.argv[2])]
    procs, R, out = int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    mod = mod_of(r[3], r[4], r[5])
    jobs = [(0, mod, (s - 3, (oy, oz), sym)) for s in range(0, 6) for sym in range(8)
            for oy in range(-R, R + 1) for oz in range(-R, R + 1)]
    with Pool(procs) as p: res = [x for x in p.imap_unordered(ev, jobs, chunksize=32) if x]
    json.dump([(g, rel) for _, s, g, rel in res], open(out, 'w'))
    from collections import Counter
    print(len(res), sorted(Counter((s, g) for _, s, g, rel in res).items())[:30])
