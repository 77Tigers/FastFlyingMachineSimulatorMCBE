"""longer CP runs for side-contact modules; keeps the better of old/new per k in modules_lat2.json."""
import json, sys, cp_module
from concurrent.futures import ProcessPoolExecutor
def one(k):
    old = json.load(open('modules_lat.json')).get(str(k))
    a0, b0 = (old['a'], old['b']) if old else (4, 4)
    best = old
    for a, b in {(a0, b0), (a0 + 1, b0), (a0, b0 + 1), (a0 - 1, b0 + 1), (a0 + 1, b0 - 1)}:
        if a < 2 or b < 2 or a * b < k + 3: continue
        r = cp_module.solve(k, a, b, 90, 4)
        if r and (best is None or r['cost'] < best['cost']): best = r
    return k, best, old['cost'] if old else None
if __name__ == '__main__':
    ks = [int(x) for x in sys.argv[1].split(',')]
    out = {}
    with ProcessPoolExecutor(4) as ex:
        for k, best, oc in ex.map(one, ks):
            print(k, oc, '->', best['cost'], 'bound', best['bound'], flush=True); out[str(k)] = best
            json.dump(out, open('modules_lat2.json', 'w'))
