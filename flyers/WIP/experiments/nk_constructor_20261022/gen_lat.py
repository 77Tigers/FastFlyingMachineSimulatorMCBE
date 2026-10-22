import json, sys, cp_module
from concurrent.futures import ProcessPoolExecutor
def one(k):
    best = None
    for a, b in ((4, 5), (4, 6), (5, 5), (5, 6), (4, 7), (5, 7), (6, 6), (4, 8), (5, 8), (6, 7)):
        if a * b < k + 4 or a * b > 3 * k: continue
        r = cp_module.solve(k, a, b, 30, 3)
        if r and (best is None or r['cost'] < best['cost']): best = r
    return k, best
if __name__ == '__main__':
    tab = json.load(open('modules_lat.json'))
    with ProcessPoolExecutor(4) as ex:
        for k, best in ex.map(one, range(13, 25)):
            print(k, best['cost'], best['bound'], flush=True); tab[str(k)] = best
            json.dump(tab, open('modules_lat.json', 'w'))
