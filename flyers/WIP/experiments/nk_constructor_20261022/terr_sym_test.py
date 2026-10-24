"""terrace: the 8 box symmetries of each k's CP strip pattern (same cost, different edge lanes) on real rings.
python terr_sym_test.py K,K"""
import sys, json
from concurrent.futures import ProcessPoolExecutor
import families as F, terrace

SY = [lambda y, z, a, b: (y, z), lambda y, z, a, b: (a - 1 - y, z), lambda y, z, a, b: (y, b - 1 - z),
      lambda y, z, a, b: (a - 1 - y, b - 1 - z), lambda y, z, a, b: (z, y), lambda y, z, a, b: (b - 1 - z, y),
      lambda y, z, a, b: (z, a - 1 - y), lambda y, z, a, b: (b - 1 - z, a - 1 - y)]


def job(args):
    k, w, si = args
    g, gap, cv, box, pat = F.terrace_params(k, w)
    if pat != 'cp': return args, 'slab-pattern'
    p = max(terrace.floor_sizes(k, g))
    res = terrace.cp_pattern(p, box[0], box[1], g)
    if res is None: return args, None
    P, R, (a, b), PL, S = res
    f = SY[si]
    if si >= 4 and a != b: return args, 'non-square'
    tr = lambda cs: [f(y, z, a, b) for y, z in cs]
    order = sorted(range(len(P)), key=lambda i: P[i])   # floors take P[:size]; keep the same lanes per floor
    pattern = dict(P=tr(P), R=tr(R), PL=tr(PL), S=tr(S), size=(a, b) if si < 4 else (b, a))
    try:
        r = terrace.build(k, g, gap, cv, box, pattern=pattern)
        if r is None or terrace.collisions(r, bodies=list(range(min(r.T.L, 2 * (r.T.L // 4) + 4)))): return args, 'coll'
        terrace.route_all(r)
        L = r.T.L; m = L // 4
        if r.check(sorted({(X + d) % L for X in (0, 1, m) for d in range(-2, 3)})): return args, 'check'
        return args, F.predicted_pl(r)
    except (RuntimeError, AssertionError) as e:
        return args, 'err'


if __name__ == '__main__':
    bits = json.load(open('bits.json'))
    jobs = [(k, bits[str(k)], si) for k in [int(x) for x in sys.argv[1].split(',')] for si in range(8)]
    out = {}
    with ProcessPoolExecutor(14) as ex:
        for (k, w, si), pl in ex.map(job, jobs):
            out.setdefault(k, []).append((si, pl))
    for k in sorted(out): print(k, out[k], flush=True)
