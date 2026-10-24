"""one stack parameter list over several backs and corner offsets (parallel over (back, corner)).
python stack_one.py K PARAMS BACKS [NCV] [NLAY]   BACKS: '+'-separated list of bank indices or screen-file refs 'path:i'"""
import sys, os, time
from concurrent.futures import ProcessPoolExecutor
import stack, stack_scan, tower2, square
from nk import bodies_for


def job(a):
    k, params, bi, cv, nlay = a
    e = stack_scan.back_entry(k, bi)
    xo = tower2.balanced_xoff(k, square.ring_size(k), bodies_for(k) - 1)
    st = {}; t = time.time()
    mg = tuple(map(int, os.environ.get('MG', '0,1').split(',')))
    res = stack.construct(k, (e['mod'], e['step']), params, cv, xo, nlay, stats=st, mg=mg)
    out = None
    if res:
        p, lc, r = res
        name = 'out/stack/n%02d_' % k + '_'.join('%d%d' % ms for ms in params) + f'_{str(bi).split("/")[-1].replace(":", "")}_c{cv[0]}{cv[1]}.flyer'.replace('-', 'm')
        r.flyer(p + 2).save(name)
        out = (p, lc, name)
    return bi, cv, out, st, round(time.time() - t, 1)


if __name__ == '__main__':
    k = int(sys.argv[1]); params = [tuple(map(int, t.split(','))) for t in sys.argv[2].split(';')]
    backs = sys.argv[3].split('+'); ncv = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    nlay = int(sys.argv[5]) if len(sys.argv) > 5 else 6
    jobs = []
    for bi in backs:
        e = stack_scan.back_entry(k, bi)
        for cv in stack.back_corners(k, e['mod'], e['step'], span=8, keep=ncv): jobs.append((k, params, bi, cv, nlay))
    print(len(jobs), 'jobs', flush=True)
    with ProcessPoolExecutor(int(os.environ.get('SW', 4))) as ex:
        for r in ex.map(job, jobs): print(*r, flush=True)
