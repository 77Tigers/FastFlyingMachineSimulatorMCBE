"""Towers (tower2, height h, power-only top) on back_cp back bodies: the joint-CP back module with k-1 hoppers on its
small diagonal straight step, corners searched. python tower_cp.py K H [NLAY NPOW MG]"""
import sys, json, itertools
from concurrent.futures import ProcessPoolExecutor
import tower2
from terrace import collisions
from joint_build import module


def back_module(res):
    P = {tuple(p) for p in res['P']}
    nb = lambda l: [(l[0] + 1, l[1]), (l[0] - 1, l[1]), (l[0], l[1] + 1), (l[0], l[1] - 1)]
    E = [(e[0],) + tuple(e[1]) for e in res['E']]
    cover = [e for e in E if (e[0] == -3 and e[1:] in P) or (e[0] == -2 and any(v in P for v in nb(e[1:])))]
    return module(res, cover), tuple(res['step'])


def job(args):
    k, h, i, cv, nlay, npow, mg = args
    res = json.load(open(f'out/back_cp_{k}.json'))[i]
    back = back_module(res)
    ok = False
    for lc in itertools.product(range(nlay), repeat=h):
        try: base = tower2.build(k, 1, h, lc, back=back, cv=cv, mg=mg)
        except (AssertionError, RuntimeError): continue
        if base is not None and not collisions(base): ok = True; break
    if not ok: return (i, cv), []
    try: return (i, cv), tower2.scan(k, 1, h, nlay, npow, keep=2, tag=f'cp{i}_{cv[0]}_{cv[1]}', back=back, cv=cv, mg=mg)
    except Exception as e: return (i, cv), repr(e)[:80]


if __name__ == '__main__':
    k, h = int(sys.argv[1]), int(sys.argv[2])
    nlay, npow, mg = (int(x) for x in (sys.argv[3:6] + ['4', '8', '1'][len(sys.argv[3:6]):]))
    res = json.load(open(f'out/back_cp_{k}.json'))
    jobs = []
    for i, r in enumerate(res):   # corners whose back ring alone is collision-free
        back = back_module(r)
        for cv in itertools.product(range(-3, r['a'] + r['b'] + 3), repeat=2):
            try: rb = tower2.build(k, 1, 0, (), back=back, cv=cv)
            except AssertionError: continue
            if not collisions(rb): jobs.append((k, h, i, cv, nlay, npow, mg))
    print(len(jobs), 'jobs', flush=True)
    with ProcessPoolExecutor(14) as ex:
        for key, out in ex.map(job, jobs):
            if out: print(key, out, flush=True)
