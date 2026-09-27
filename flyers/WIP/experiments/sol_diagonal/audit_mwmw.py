"""Independent audit inputs for the closed diagonal mwmw candidate."""
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer

source = ROOT / 'flyers/WIP/experiments/astra_diagonal/mwmw/c58.flyer'
base = Flyer.load(source)
out = Path(__file__).resolve().parent
for limit in (10, 11, 12):
    f = Flyer(rng_state=base.rng_state, push_limit=limit,
              phase_x=base.phase_x, phase_z=base.phase_z)
    f._cells = base._cells.copy()
    path = out / f'c58_pl{limit}.flyer'
    f.save(path)
    print(path.name, Flyer.load(path).validate())

meta_path = ROOT / 'flyers/WIP/experiments/astra_diagonal/mwmw_metadata.json'
rows_path = ROOT / 'flyers/WIP/experiments/astra_diagonal/mwmw_results.tsv'
meta = {item['id']: item for item in json.loads(meta_path.read_text())}
balanced = []
for row in rows_path.read_text().splitlines():
    fields = row.split('\t')
    if not fields[0].startswith('c'):
        continue
    cid = int(fields[0][1:])
    if meta[cid]['counts'] == [7, 7]:
        balanced.append((cid, *fields[1:]))
print('balanced 7/7:', balanced)
