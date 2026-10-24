"""lat family: scan the straight step (a + gy, sz) beyond the word's (a + 1, sz in {-1, 0}) with each k's current
module and corner, and corners around it. python lat_step_scan.py K,K"""
import sys, json, itertools
from concurrent.futures import ProcessPoolExecutor
import families as F, square, sqbuild


def job(args):
    k, word, step, cv = args
    fam, (a, b), sz, cy, cz = F.unpack(word, k)
    L = F.big_ring(k) if fam == 'latbig' else square.ring_size(k)
    mod = F.lat_module(k, a, b)
    if mod is None: return args, None
    if L // 4 > 1 and (word >> 7) & 1: mod = F.mirror_y(mod)
    try:
        r = sqbuild.assemble(k, mod, step, cv, L)
        if r is None: return args, None
        Lr = r.T.L; m = Lr // 4
        if r.check(sorted({(X + d) % Lr for X in (0, 1, m) for d in range(-3, 4)})): return args, None
        return args, F.predicted_pl(r)
    except (RuntimeError, AssertionError, KeyError, IndexError):
        return args, None


if __name__ == '__main__':
    bits = json.load(open('bits.json'))
    jobs = []
    for k in [int(x) for x in sys.argv[1].split(',')]:
        w = bits[str(k)]; fam, (a, b), sz, cy, cz = F.unpack(w, k)
        mod = F.lat_module(k, a, b); a2 = mod['size'][0]
        for gy, sz2 in itertools.product((1, 2), (-2, -1, 0, 1)):
            for dcy, dcz in itertools.product((-1, 0, 1), (-1, 0, 1)):
                jobs.append((k, w, (a2 + gy, sz2), (cy + dcy, cz + dcz)))
    res = {}
    with ProcessPoolExecutor(14) as ex:
        for args, pl in ex.map(job, jobs, chunksize=2):
            if pl: res.setdefault(args[0], []).append((pl, args[2], args[3]))
    for k in sorted(res):
        cur = F.predicted_pl(F.build(k, bits[str(k)]))
        print(k, 'current', cur, 'best', sorted(res[k])[:3], flush=True)
