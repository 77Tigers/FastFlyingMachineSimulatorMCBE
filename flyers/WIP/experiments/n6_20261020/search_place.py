"""random search over module placements (yz offset, lattice symmetry, x origin) for a module layout."""
import sys, random, json, itertools
from multiprocessing import Pool
from ring_designer import Ring, ORDER, SYMS, V1, V2, V3, V4, V5
LAY = {'V1': V1, 'V2': V2, 'V3': V3, 'V4': V4, 'V5': V5}


def footprint(mod, sym, off):
    cells = set()
    for c in mod['R'] + mod['P']: cells.add(c)
    for c in mod['PLATE'] + mod['CONT']: cells.add((c[1], c[2]))
    return {(off[0] + SYMS[sym](*c)[0], off[1] + SYMS[sym](*c)[1]) for c in cells}


def sample(rng, mod):
    while True:
        place = {}; used = set()
        ok = True
        for i, X in enumerate(ORDER):
            sym = rng.randrange(8)
            if i == 0: off = (0, 0); x0 = 0
            else:
                off = (rng.randrange(-8, 9), rng.randrange(-8, 9)); x0 = rng.randrange(-4, 3)
            fp = footprint(mod, sym, off)
            halo = {(y + dy, z + dz) for y, z in fp for dy in (-1, 0, 1) for dz in (-1, 0, 1)}
            if halo & used: ok = False; break
            used |= fp; place[X] = (x0, off, sym)
        if ok: return place


def evaluate(args):
    name, seed = args
    rng = random.Random(seed); mod = LAY[name]
    place = sample(rng, mod)
    try:
        ring = Ring(mod, place)
        for X in ORDER: ring.route(X, maxlen=14)
        bad = ring.check()
        if bad: return None
        sz = ring.size()
        return (max(sz.values()), sum(sz.values()), seed, place)
    except Exception as e:
        return None


if __name__ == '__main__':
    name, n = sys.argv[1], int(sys.argv[2]); start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    with Pool(4) as p:
        res = [r for r in p.imap_unordered(evaluate, [(name, s) for s in range(start, start + n)], chunksize=4) if r]
    res.sort(key=lambda r: (r[0], r[1]))
    print(name, 'valid', len(res), 'of', n)
    for r in res[:8]: print(r[0], r[1], r[2], r[3])
    json.dump(res[:50], open(f"out/search_{name}_{start}.json", "w"))
