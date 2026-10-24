"""stack family over many k (research driver): back = side-contact CP module for k-1 hoppers in a few boxes (both
mirrors), the best few corner offsets, given parameter patterns; parallel over (k, back, corner).
Patterns: 'h' = human topology (k-1,0);(k,0);(k,0); 'h4' = one more middle level (k-1,0);(k-1,0);(k,0);(k,0).
Writes out/stack/all_<tag>.txt; the best flyer per k goes to out/stack/best_nKK_plPL.flyer.
python stack_all.py K1,K2,.. [PATTERN] [NBOX] [NCV]"""
import sys, os, time, math
from concurrent.futures import ProcessPoolExecutor
import stack, stack_scan, tower2, square
from nk import bodies_for


def params_of(k, pat):
    if pat == 'h': return [(k - 1, 0), (k, 0), (k, 0)]
    if pat == 'h4': return [(k - 1, 0), (k - 1, 0), (k, 0), (k, 0)]
    raise ValueError(pat)


def boxes(k, n):
    """boxes near square with room for k-1 hoppers and their RBs (area ~1.4-2.2 x hoppers)"""
    c = []
    for a in range(2, 9):
        for b in range(2, 9):
            if 1.4 * (k - 1) <= a * b <= 2.4 * (k - 1) + 2: c.append((abs(a - b), a * b, a, b))
    c.sort()
    return [(a, b) for _, _, a, b in c[:n]]


def corners_job(args):
    k, spec, ncv = args
    try:
        e = stack_scan.back_entry(k, spec)
        if e['mod'] is None: return k, spec, []
        return k, spec, stack.back_corners(k, e['mod'], e['step'], span=8, keep=ncv)
    except Exception as ex:
        return k, spec, []


def job(args):
    k, spec, cv, pat = args
    t = time.time(); st = {}
    try:
        e = stack_scan.back_entry(k, spec)
        xo = tower2.balanced_xoff(k, square.ring_size(k), bodies_for(k) - 1)
        res = stack.construct(k, (e['mod'], e['step']), params_of(k, pat), cv, xo, 3, stats=st, mg=(1, 1), max_leaves=8)
    except Exception as ex:
        return k, spec, cv, None, {'err': repr(ex)[:60]}, round(time.time() - t, 1)
    if not res: return k, spec, cv, None, st, round(time.time() - t, 1)
    p, lc, r = res
    name = f'out/stack/all_n{k:02d}_pl{p}_{pat}_{spec.replace(":", "").replace(",", "_")}_c{cv[0]}_{cv[1]}.flyer'.replace('-', 'm')
    r.flyer(p).save(name)
    return k, spec, cv, (p, lc, name), st, round(time.time() - t, 1)


if __name__ == '__main__':
    ks = [int(x) for x in sys.argv[1].split(',')]
    pat = sys.argv[2] if len(sys.argv) > 2 else 'h'
    nbox = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    ncv = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    W = int(os.environ.get('SW', 12))
    specs = [(k, f'lat:{a},{b},0,1,{mir}') for k in ks for a, b in boxes(k, nbox) for mir in (0, 1)]
    with ProcessPoolExecutor(W) as ex:
        cj = list(ex.map(corners_job, [(k, s, ncv) for k, s in specs]))
    jobs = [(k, s, cv, pat) for k, s, cvs in cj for cv in cvs]
    print(len(jobs), 'jobs', flush=True)
    best = {}
    with ProcessPoolExecutor(W) as ex:
        for k, spec, cv, res, st, dt in ex.map(job, jobs):
            print(k, spec, cv, res, st, dt, flush=True)
            if res and (k not in best or res[0] < best[k][0]): best[k] = res
    print('BEST', {k: v[0] for k, v in sorted(best.items())}, flush=True)
