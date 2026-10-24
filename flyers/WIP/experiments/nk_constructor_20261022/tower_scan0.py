"""towers (human sticky, back untouched) on a given back link; scans corner, phase, level layouts, lane margins.
python tower_scan0.py K  (link from LINKS[k])"""
import sys, itertools, collections
from concurrent.futures import ProcessPoolExecutor
import tower2, square, families as F
import human_link as H
from nk import bodies_for

LINKS = {2: [({'P': [(1, 0)], 'R': [(0, 1, 1)], 'PLATE': [(1, 1, 0), (1, 1, 1)], 'CONT': [(-2, 0, 0)], 'size': (2, 3)}, (-1, -2)), ({'P': [(1, 0)], 'R': [(0, 1, 1)], 'PLATE': [(1, 1, 0), (1, 1, 1)], 'CONT': [(-2, 0, 0)], 'size': (3, 2)}, (-2, 0)), ({'P': [(1, 0)], 'R': [(0, 1, 1)], 'PLATE': [(1, 1, 0), (1, 1, 1)], 'CONT': [(-2, 0, 0)], 'size': (3, 2)}, (-2, -1)), ({'P': [(1, 1)], 'R': [(0, 1, 2)], 'PLATE': [(1, 1, 1), (1, 1, 2)], 'CONT': [(-2, 1, 0)], 'size': (2, 3)}, (1, -2)), ({'P': [(0, 1)], 'R': [(0, 0, 2)], 'PLATE': [(1, 0, 1), (1, 0, 2)], 'CONT': [(-2, 0, 0)], 'size': (1, 4)}, (0, -3))],
         3: [({'P': [(0, 0), (1, 1)], 'R': [(0, 1, 0)], 'PLATE': [(1, 0, 0), (1, 1, 1), (1, 1, 0)], 'CONT': [(-2, 0, 1)], 'size': (3, 2)}, (-3, 1)), ({'P': [(0, 0), (1, 1)], 'R': [(0, 1, 0)], 'PLATE': [(1, 0, 0), (1, 1, 1), (1, 1, 0)], 'CONT': [(-2, 0, 1)], 'size': (3, 2)}, (-2, 2)), ({'P': [(1, 1), (2, 0)], 'R': [(0, 1, 0)], 'PLATE': [(1, 1, 1), (1, 2, 0), (1, 1, 0)], 'CONT': [(-2, 2, 1)], 'size': (3, 2)}, (3, 1)), ({'P': [(1, 1), (2, 0)], 'R': [(0, 1, 0)], 'PLATE': [(1, 1, 1), (1, 2, 0), (1, 1, 0)], 'CONT': [(-2, 2, 1)], 'size': (3, 2)}, (2, 2)), ({'P': [(0, 1), (1, 0)], 'R': [(0, 1, 1)], 'PLATE': [(1, 0, 1), (1, 1, 0), (1, 1, 1)], 'CONT': [(-2, 0, 0)], 'size': (2, 3)}, (-2, -2)), ({'P': [(0, 1), (1, 0)], 'R': [(0, 1, 1)], 'PLATE': [(1, 0, 1), (1, 1, 0), (1, 1, 1)], 'CONT': [(-2, 0, 0)], 'size': (2, 3)}, (-1, -3)), ({'P': [(0, 1), (1, 0)], 'R': [(0, 1, 1)], 'PLATE': [(1, 0, 1), (1, 1, 0), (1, 1, 1)], 'CONT': [(-2, 0, 0)], 'size': (3, 2)}, (-3, -1)), ({'P': [(0, 1), (1, 0)], 'R': [(0, 1, 1)], 'PLATE': [(1, 0, 1), (1, 1, 0), (1, 1, 1)], 'CONT': [(-2, 0, 0)], 'size': (3, 2)}, (-2, -2)), ({'P': [(0, 0), (1, 1)], 'R': [(0, 0, 1)], 'PLATE': [(1, 0, 0), (1, 1, 1), (1, 0, 1)], 'CONT': [(-2, 1, 0)], 'size': (2, 3)}, (2, -2)), ({'P': [(0, 0), (1, 1)], 'R': [(0, 0, 1)], 'PLATE': [(1, 0, 0), (1, 1, 1), (1, 0, 1)], 'CONT': [(-2, 1, 0)], 'size': (2, 3)}, (1, -3)), ({'P': [(0, 1), (1, 2)], 'R': [(0, 1, 1)], 'PLATE': [(1, 0, 1), (1, 1, 2), (1, 1, 1)], 'CONT': [(-2, 0, 2)], 'size': (2, 3)}, (-2, 2)), ({'P': [(0, 1), (1, 2)], 'R': [(0, 1, 1)], 'PLATE': [(1, 0, 1), (1, 1, 2), (1, 1, 1)], 'CONT': [(-2, 0, 2)], 'size': (2, 3)}, (-1, 3))]}
CVS = {3: [(-2, 0), (-2, 0), (2, 2), (2, 2), (-2, -1), (-1, -2), (-2, -1), (-2, -1), (2, -3), (2, -3), (-1, 1), (-1, 1)]}


def job(args):
    k, mod, step, cv, ph, mg, nlay = args
    L = square.ring_size(k); xo = tower2.balanced_xoff(k, L, ph)
    why = collections.Counter(); best = None
    for lc in itertools.product(range(nlay), repeat=3):
        try: r, w = H.tower_ring(k, 3, step, cv, lc, mod=mod, mg=mg, hs=True, xo=xo, kb='s2')
        except (AssertionError, RuntimeError): r, w = None, 'err'
        why[w] += 1
        if r is None: continue
        try: r.flyer(1)
        except AssertionError: why['export'] += 1; continue
        sc = (F.predicted_pl(r), max(r.size()), lc)
        if best is None or sc < best: best = sc
    return args[3:6], best, dict(why)


if __name__ == '__main__':
    k = int(sys.argv[1])
    jobs = []
    import os
    cvs = CVS.get(k)
    for li, (mod, step) in enumerate(LINKS[k]):
        if os.environ.get('TS_TOP') and li >= int(os.environ['TS_TOP']): continue
        R = int(os.environ.get('TS_CVR', 1))
        cvl = ([(cvs[li][0] + a, cvs[li][1] + b) for a in range(-R, R + 1) for b in range(-R, R + 1)] if cvs else
               list(itertools.product(range(-3, 5), repeat=2)))
        phl = range(bodies_for(k)) if os.environ.get('TS_ALLPH') else ([bodies_for(k) - 1] if cvs else range(bodies_for(k)))
        for cv in cvl:
            for ph in phl:
                for mg in (((1, 1),) if os.environ.get('TS_MG11') else ((0, 1), (1, 1)) if cvs else ((0, 1), (1, 0), (1, 1))):
                    jobs.append((k, mod, step, cv, ph, mg, 4))
    print(len(jobs), 'jobs', flush=True)
    res = []
    with ProcessPoolExecutor(14) as ex:
        for key, best, why in ex.map(job, jobs, chunksize=4):
            if best: res.append((best, key)); print(key, best, flush=True)
    res.sort(); print('BEST', res[:5])
