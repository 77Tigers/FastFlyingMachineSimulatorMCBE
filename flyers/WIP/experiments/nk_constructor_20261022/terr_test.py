import sys, terrace as Tr, construct
from concurrent.futures import ProcessPoolExecutor
def one(args):
    k, mir, cyd = args
    p = max(Tr.floor_sizes(k, 2)); a0, b0 = construct.grid_module(p, 'slabP')['size']
    best = None
    for da in (-1, 0, 1, 2):
        for db in (-1, 0, 1, 2):
            a, b = max(a0 + da, 2), max(b0 + db, 2)
            for gap in (1, 2):
                for cz in range(b, b + 4):
                    try:
                        r = Tr.build(k, 2, gap, (a - 1 + cyd, cz), (a, b), mir)
                        if Tr.collisions(r, bodies=list(range(min(r.T.L, 2 * (r.T.L // 4) + 4)))): continue
                        Tr.route_all(r)
                    except Exception: continue
                    s = max(r.size())
                    if best is None or s < best[0]: best = (s, (a, b), gap, cz)
    return k, mir, cyd, best
if __name__ == '__main__':
    ks = [int(x) for x in sys.argv[1].split(',')]
    jobs = [(k, m, c) for k in ks for m in (0, 1) for c in (0, 1)]
    with ProcessPoolExecutor(8) as ex:
        for res in ex.map(one, jobs): print(res, flush=True)
