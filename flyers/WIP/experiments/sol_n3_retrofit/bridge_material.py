"""Test nonadhesive cells in the shortened N3 connector."""
from pathlib import Path
from itertools import combinations
import csv
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from fastflyer import Block, Flyer, Kind

OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'flyers/WIP/experiments/n3_bridge'
RUNNER = Path(os.environ['TEMP']) / 'flyer_measure.exe'
ROUTE = [(x + 16, 2, 15) for x in range(-2, 3)]


def measure(f, ticks):
    path = OUT / 'screen.flyer'
    f.save(path)
    p = subprocess.run([str(RUNNER), str(ticks), str(path)], capture_output=True, text=True)
    fields = p.stdout.strip().split('\t')
    return int(fields[1]) if p.returncode == 0 and len(fields) > 1 else -1


def main():
    rows = []
    sources = sorted(SOURCE.glob('r0_rot*_inv*.flyer'))
    for source in sources:
        base = Flyer.load(source)
        assert all(base.get(p).kind in (Kind.SLIME, Kind.HONEY) for p in ROUTE)
        for size in range(1, 6):
            for positions in combinations(ROUTE, size):
                f = Flyer(base.phase_x, base.phase_z, base.rng_state, 19)
                f._cells = base._cells.copy()
                for p in positions:
                    f.set(p, Block(Kind.GLAZED_TERRACOTTA))
                d120 = measure(f, 120)
                d1000 = measure(f, 1000) if d120 >= 33 else -1
                rows.append((source.name, [p[0] - 16 for p in positions], d120, d1000))
                if d120 >= 33:
                    name = f'glazed_{len(rows)}_d{d120}.flyer'
                    f.save(OUT / name)
                    print('LEAD', name, source.name, positions, d120, d1000, flush=True)
    with (OUT / 'bridge_material.csv').open('w', newline='') as h:
        w = csv.writer(h)
        w.writerow(('source', 'glazed_route_x', 'distance120_pl19', 'distance1000_pl19'))
        w.writerows(rows)
    print('DONE', len(rows), 'best', max(r[2] for r in rows), flush=True)


if __name__ == '__main__':
    main()
