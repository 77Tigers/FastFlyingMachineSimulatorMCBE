"""terrace: scan the straight step (gap, z shift sz) and the corner offset around each k's current word.
python terr_offset_scan.py K,K,..  -> out/terr_offset_K.json"""
import sys, json, itertools
from concurrent.futures import ProcessPoolExecutor
import families as F, terrace


def job(args):
    k, g, gap, sz, cv, box, pat = args
    try:
        r = terrace.build(k, g, gap, cv, box, pattern=pat, sz=sz)
        if r is None or terrace.collisions(r, bodies=list(range(min(r.T.L, 2 * (r.T.L // 4) + 4)))): return args, None
        terrace.route_all(r)
        L = r.T.L; m = L // 4
        if r.check(sorted({(X + d) % L for X in (0, 1, m) for d in range(-2, 3)})): return args, None
        return args, (F.predicted_pl(r), sum(r.size()))
    except (RuntimeError, AssertionError):
        return args, None


GAPS = (1, 2)

if __name__ == '__main__':
    import os
    GAPS = tuple(int(x) for x in os.environ.get('TG', '1,2').split(','))
    bits = json.load(open('bits.json'))
    jobs = []
    for k in [int(x) for x in sys.argv[1].split(',')]:
        w = bits[str(k)]; g, gap0, cv0, box, pat = F.terrace_params(k, w)
        a, b = box
        for gap, sz in itertools.product(GAPS, (-1, 0, 1)):
            for cy, cz in itertools.product(range(a - 2, a + 1), range(b - 1, b + 4)):
                jobs.append((k, g, gap, sz, (cy, cz), box, pat))
    res = {}
    with ProcessPoolExecutor(14) as ex:
        for args, out in ex.map(job, jobs, chunksize=2):
            if out: res.setdefault(args[0], []).append((out, args[2:5]))
    for k in sorted(res):
        res[k].sort()
        w = bits[str(k)]; g, gap0, cv0, box, pat = F.terrace_params(k, w)
        print(k, 'current', (gap0, 0, cv0), 'best', res[k][:3], flush=True)
        json.dump(res[k], open(f'out/terr_offset_{k}.json', 'w'))
