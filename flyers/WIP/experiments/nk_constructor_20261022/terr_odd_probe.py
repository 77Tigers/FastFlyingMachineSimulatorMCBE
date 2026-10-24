import sys, itertools
from concurrent.futures import ProcessPoolExecutor
import families as F, terrace


def job(a):
    k, w = a
    try:
        r = F.build(k, w)
        if r is None: return a, None
        L = r.T.L; m = L // 4
        if r.check(sorted({(X + d) % L for X in (0, 1, m) for d in range(-2, 3)})): return a, 'bad'
        return a, (F.predicted_pl(r), r.size()[:6])
    except Exception as e:
        return a, None


if __name__ == '__main__':
    jobs = [(k, 3 | (v << 2) | (l << 6)) for k in (17, 19, 21) for v in range(16) for l in (1, 3, 5, 7)]
    best = {}
    with ProcessPoolExecutor(14) as ex:
        for (k, w), res in ex.map(job, jobs):
            if res and res != 'bad' and (k not in best or res[0] < best[k][0][0]): best[k] = (res, w)
    for k in sorted(best): print(k, best[k], F.terrace_params(k, best[k][1]))
