"""joint module + straight-link cover/connector CP (joint_cp.py, from the nk_newmech subagent) for every k;
best result per k -> modules_joint.json"""
import json, sys
from concurrent.futures import ProcessPoolExecutor
import joint_cp, construct
def one(k):
    a0, b0 = construct.grid_module(k, 'slabP')['size']
    best = None
    for a, b in {(a0, b0), (b0, a0), (a0 + 1, b0), (a0, b0 + 1)}:
        for sz in (-1, 0):
            r = joint_cp.solve(k, a, b, (a + 1, sz), 45, workers=3)
            if r and (best is None or r['cost'] < best['cost']): best = r
    return k, best
if __name__ == '__main__':
    ks = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else range(3, 25)
    out = {}
    with ProcessPoolExecutor(4) as ex:
        for k, best in ex.map(one, ks):
            print(k, best and (best['cost'], best['bound'], best['a'], best['b'], best['step']), flush=True)
            if best: out[str(k)] = best; json.dump(out, open('modules_joint.json', 'w'))
