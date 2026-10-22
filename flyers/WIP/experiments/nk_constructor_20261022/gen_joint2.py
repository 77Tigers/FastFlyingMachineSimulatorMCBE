"""longer joint CP, hinted with the current best module (square_table family); keeps improvements only."""
import json, sys
from concurrent.futures import ProcessPoolExecutor
import joint_cp, construct
def one(k):
    t = json.load(open('square_table.json'))[str(k)]
    fam = t[2] if len(t) > 2 else 'slabP'
    mod = construct.grid_module(k, fam); a, b = mod['size']
    hint = dict(P=mod['P'], R=[r[1:] for r in mod['R']], PL=[p[1:] for p in mod['PLATE']])
    best = None
    for sz in (-1, 0):
        r = joint_cp.solve(k, a, b, (a + 1, sz), 150, workers=3, hint=hint)
        if r and (best is None or r['cost'] < best['cost']): best = r
    return k, best
if __name__ == '__main__':
    ks = [int(x) for x in sys.argv[1].split(',')]
    old = json.load(open('modules_joint.json'))
    with ProcessPoolExecutor(4) as ex:
        for k, best in ex.map(one, ks):
            prev = old.get(str(k), {}).get('cost', 999)
            print(k, prev, '->', best and best['cost'], flush=True)
            if best and best['cost'] < prev: old[str(k)] = best; json.dump(old, open('modules_joint.json', 'w'))
