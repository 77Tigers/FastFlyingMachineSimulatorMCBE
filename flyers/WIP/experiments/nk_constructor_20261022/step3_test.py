import sys, itertools, collections
from concurrent.futures import ProcessPoolExecutor
import human_link as H, tower2, families as F, link0

MOD3 = dict(H.MOD, size=(3, 2))


def job(a):
    cv, ph, mg, step = a
    xo = tower2.balanced_xoff(3, 20, ph)
    why = collections.Counter(); best = None
    for lc in itertools.product(range(4), repeat=3):
        try: r, w = H.tower_ring(3, 3, step, cv, lc, mod=MOD3, mg=mg, hs=True, xo=xo, kb='s2')
        except (AssertionError, RuntimeError): r, w = None, 'err'
        why[w.split(' ')[0]] += 1
        if r is None: continue
        try: r.flyer(1)
        except AssertionError: continue
        sc = (F.predicted_pl(r), max(r.size()), lc)
        if best is None or sc < best: best = sc
    return a, best, dict(why)


if __name__ == '__main__':
    # back ring alone first
    for step in ((3, 0), (3, -1)):
        b = link0.evaluate(3, MOD3, step); print('back', step, b, flush=True)
    jobs = [(cv, ph, mg, st) for st in ((3, 0), (3, -1)) for cv in itertools.product(range(2, 7), range(-3, 2))
            for ph in (4,) for mg in ((0, 1), (0, 2))]
    with ProcessPoolExecutor(10) as ex:
        res = [x for x in ex.map(job, jobs) if x[1]]
    res.sort(key=lambda t: t[1]); print(len(res), res[:5])
