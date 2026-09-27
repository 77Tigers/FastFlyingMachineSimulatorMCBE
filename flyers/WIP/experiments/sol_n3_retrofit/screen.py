"""Bounded static rear-corner substitutions on the verified N3 ring."""
from pathlib import Path
from itertools import combinations
import csv
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from flyers.WIP.astra_ringgen_safe import make
from fastflyer import Block, Flyer, Kind

OUT = Path(__file__).resolve().parent
RUNNER = Path(os.environ['TEMP']) / 'flyer_measure.exe'
BASE, COUNTS, (SEGMENTS, _) = make(3, [(0, 0), (0, 4), (3, 5), (5, 2), (3, -1)], 3, 19)
assert COUNTS == [14, 14, 14, 14, 15]
REAR = sorted(p for p in SEGMENTS[4] if p[0] == -2)
DIRS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def dist(a, b):
    return sum(abs(a[i] - b[i]) for i in range(3))


def measure(f, ticks):
    path = OUT / 'screen.flyer'
    try:
        f.save(path)
    except Exception:
        return -1
    p = subprocess.run([str(RUNNER), str(ticks), str(path)], capture_output=True, text=True)
    fields = p.stdout.strip().split('\t')
    return int(fields[1]) if p.returncode == 0 and len(fields) > 1 else -1


def candidate(remove, add):
    f = Flyer(BASE.phase_x, BASE.phase_z, BASE.rng_state, 19)
    f._cells = BASE._cells.copy()
    for p in remove:
        del f._cells[p]
    f._cells[add] = Block(Kind.SLIME)
    return f


def main():
    start = time.monotonic()
    rows = []
    seen = set()
    # A diagonal rear corner may replace two face contacts. Include x-adjacent
    # replacements to test a shifted pickup while preserving all fixed blocks.
    pairs = list(combinations(REAR, 2))
    for r1, r2 in pairs:
        choices = set()
        for p in (r1, r2):
            for d in DIRS:
                q = tuple(p[i] + d[i] for i in range(3))
                if q in BASE._cells or not -3 <= q[0] <= -1:
                    continue
                if dist(q, r1) <= 2 and dist(q, r2) <= 2:
                    choices.add(q)
        for q in sorted(choices):
            key = (r1, r2, q)
            if key in seen:
                continue
            seen.add(key)
            f = candidate((r1, r2), q)
            d120 = measure(f, 120)
            d1000 = measure(f, 1000) if d120 >= 33 else -1
            rows.append((r1, r2, q, d120, d1000))
            if d120 >= 33:
                name = f'corner_{len(rows)}_d{d120}.flyer'
                f.save(OUT / name)
                print('LEAD', name, r1, r2, q, d120, d1000, flush=True)
            if len(rows) >= 500 or time.monotonic() - start > 600:
                break
        if len(rows) >= 500 or time.monotonic() - start > 600:
            break
    with (OUT / 'summary.csv').open('w', newline='') as h:
        w = csv.writer(h)
        w.writerow(('removed1', 'removed2', 'added', 'distance120', 'distance1000'))
        w.writerows(rows)
    print('DONE', len(rows), 'elapsed', round(time.monotonic() - start, 1), 'best', max((r[3] for r in rows), default=-1), flush=True)


if __name__ == '__main__':
    main()
