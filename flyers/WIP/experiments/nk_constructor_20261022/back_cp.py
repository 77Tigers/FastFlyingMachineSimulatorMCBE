"""Joint CP back bodies with k-1 hoppers for towers (small / diagonal steps, RB on its own connector allowed).
python back_cp.py K SECS  -> out/back_cp_K.json (list of results, best first)"""
import sys, json
from concurrent.futures import ProcessPoolExecutor
import joint_cp

CASES = [(2, 3, (2, -2)), (2, 2, (1, -3)), (2, 2, (3, 1)), (2, 3, (1, 3)), (2, 3, (2, 1)), (3, 3, (2, 1))]


def job(args):
    n, a, b, step, secs = args
    r = joint_cp.solve(n, a, b, step, secs=secs, workers=4, rbcol=True)
    return r


if __name__ == '__main__':
    k, secs = int(sys.argv[1]), float(sys.argv[2])
    with ProcessPoolExecutor(4) as ex:
        res = [r for r in ex.map(job, [(k - 1, a, b, st, secs) for a, b, st in CASES]) if r]
    res.sort(key=lambda r: r['cost'])
    for r in res: print(r['cost'], r['bound'], r['a'], r['b'], r['step'], 'PL', len(r['PL']), 'R', len(r['R']), 'E', len(r['E']))
    json.dump(res, open(f'out/back_cp_{k}.json', 'w'))
