"""V6 link tables restricted to exit-aligned placements. usage: python link_v6.py LAYOUT EXITY EXITZ"""
import sys, json
from multiprocessing import Pool
from link_search import ev, LAY
from ring_designer import SYMS

if __name__ == '__main__':
    name = sys.argv[1]; exitc = (int(sys.argv[2]), int(sys.argv[3]))
    plate_cols = sorted({(c[1], c[2]) for c in LAY[name]['PLATE']})
    rels = sorted({(x, (exitc[0] - SYMS[s](*pc)[0] + dy, exitc[1] - SYMS[s](*pc)[1] + dz), s)
                   for s in range(8) for pc in plate_cols for x in range(-5, 3) for dy in (-1, 0, 1) for dz in (-1, 0, 1)})
    print(len(rels), flush=True)
    for U in 'ABCD':
        with Pool(4) as p: out = [r for r in p.map(ev, [(name, U, r) for r in rels], chunksize=8) if r]
        out.sort()
        best = {}
        for g, c, rel in out: best.setdefault(rel[0], (g, c, rel))
        print(U, {x: best[x][:2] for x in sorted(best)}, flush=True)
        json.dump(out, open(f'out/link_{name}_{U}.json', 'w'))
