"""Delete-one + add-one glue screen aimed at the bodies that reach the limit.

python pairscreen.py IN.flyer OUTDIR BODYCELLS.txt [LIMIT=12] [TICKS=600]

BODYCELLS.txt: one 'x,y,z' per line, the glue cells that may be deleted (e.g. the cells of the load-12 bodies
from `BT_CELLS=1 human_bodytrack.exe`, which reports start-file coordinates). Additions: slime or honey in any empty
cell face-adjacent to a non-arm block. Also screens each deletion alone. Writes OUTDIR/pairs.csv and prints the best.
"""
import sys, pathlib, csv
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rebalance
from rebalance import clone, add, FACES, GLUE, ok
from fastflyer import Flyer, Block, Kind


def main():
    src, outdir, cellfile = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 12
    ticks = int(sys.argv[5]) if len(sys.argv) > 5 else 600
    outdir.mkdir(parents=True, exist_ok=True)
    f = Flyer.load(src); f.push_limit = limit
    cells = {tuple(p): b for p, b in f.blocks()}
    dels = [tuple(int(v) for v in l.split(',')) for l in open(cellfile) if l.strip()]
    dels = [p for p in dels if p in cells and cells[p].kind in GLUE]
    empties = sorted({add(p, d) for p, b in cells.items() if b.kind != Kind.PISTON_ARM for d in FACES} - set(cells))
    vs = {}
    for p in dels:
        g = clone(f); g.remove(p); vs[f'd{p[0]}_{p[1]}_{p[2]}'] = g
        for e in empties:
            for k in GLUE:
                g = clone(f); g.remove(p); g.set(e, Block(k))
                vs[f'd{p[0]}_{p[1]}_{p[2]}_a{e[0]}_{e[1]}_{e[2]}{k.name[0]}'] = g
    print(len(dels), 'deletions x', len(empties), 'empties ->', len(vs), 'variants', flush=True)
    names = sorted(vs); rows = []
    for i in range(0, len(names), 2000):  # batches keep temp dirs small
        rows += rebalance.screen({n: vs[n] for n in names[i:i+2000]}, outdir, ticks, limit)
        print('screened', len(rows), flush=True)
    with open(outdir / 'pairs.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    good = sorted((r for r in rows if ok(r, ticks, limit)), key=lambda r: (int(r['n_at_limit']), int(r['n_at_limit_m1'])))
    print(len(good), 'run clean')
    for r in good[:15]: print('  ', r['name'], r['n_at_limit'], r['n_at_limit_m1'], r['hist'])
    far = sorted((r for r in rows if not ok(r, ticks, limit)), key=lambda r: -int(r['distance']))
    print('best non-clean:', [(r['name'], r['distance'], r['failures']) for r in far[:5]])


if __name__ == '__main__':
    main()
