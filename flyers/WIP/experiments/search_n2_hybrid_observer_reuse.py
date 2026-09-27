"""Reuse a front carrier cell as the hybrid's observer to lower its stroke load."""
from pathlib import Path
import os, subprocess, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from fastflyer import Block, Flyer, Kind

base = Flyer.load(ROOT / 'flyers/WIP/two_push_crosslayer_pl13.flyer')
out = Path(os.environ['TEMP']) / 'n2_hybrid_observer_reuse'
out.mkdir(exist_ok=True)
run = Path(os.environ['TEMP']) / 'flyer_batch.exe'
front = [p for p, b in base._cells.items() if b.kind == Kind.SLIME]

for limit in (12, 20):
    folder = out / f'pl{limit}'
    folder.mkdir(exist_ok=True)
    for p in front:
        for direction in range(6):
            f = Flyer(rng_state=2, push_limit=limit)
            f._cells = base._cells.copy()
            del f._cells[(15, 2, 17)]
            f._cells[(17, 1, 18)] = Block.piston(1, sticky=True)
            f._cells[p] = Block.observer(direction)
            dest = folder / f'o{p[0]}_{p[1]}_{p[2]}_d{direction}.flyer'
            try:
                f.save(dest)
            except Exception:
                pass
    q = subprocess.run([str(run), '160', str(folder)], capture_output=True, text=True)
    rows = []
    for line in q.stdout.splitlines():
        parts = line.split('\t')
        if len(parts) >= 2:
            try:
                rows.append((int(parts[1]), line))
            except ValueError:
                pass
    print(limit, 'tested', len(rows), 'top', *sorted(rows, reverse=True)[:15], sep='\n', flush=True)
