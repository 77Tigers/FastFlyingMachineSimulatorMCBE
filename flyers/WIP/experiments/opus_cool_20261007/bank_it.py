# Historical one-off; use scripts/bank_add.py for banking new flyers.
"""Bank opus_cool (gull-wing mirrored bird) only after the full 80-case samples pass.
Copies runs/gull_last13_j7.flyer -> flyers/bank/pl8/opus_cool.flyer, appends the results.csv row (research_runner
measure numbers) and adds the catalogue.json entry measured by the same tool scripts/update_bank.py uses
(target/release/fastflyer-bank-stats), keeping update_bank's key order and formatting. Engine fingerprint must match.
"""
from pathlib import Path
import csv, json, shutil, subprocess, sys, os
from hashlib import sha256
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from update_bank import engine_fingerprint

SRC = HERE / 'runs' / 'gull_last13_j7.flyer'
CSV = HERE / 'runs' / 'gull_last13_j7.samples.csv'
DEST = ROOT / 'flyers' / 'bank' / 'pl8' / 'opus_cool.flyer'
ROW = '8,opus_cool,0,2500,2500,168,75000'      # research_runner measure: start_min_x 0, end_min_x 2500, end_blocks 168

rows = list(csv.DictReader(CSV.open()))
assert len(rows) == 80 and all(r['pass'] == 'true' and r['limit'] == '8' and r['distance'] == '2500'
                               and r['max_successful_action'] == '8' for r in rows), 'samples not 80/80'
cat_path = ROOT / 'flyers' / 'bank' / 'catalogue.json'
cat = json.loads(cat_path.read_text(encoding='utf-8'))
assert cat['engine_sha256'] == engine_fingerprint(ROOT), 'engine changed: run scripts/update_bank.py instead'
DEST.parent.mkdir(exist_ok=True)
shutil.copyfile(SRC, DEST)
ledger = ROOT / 'flyers' / 'bank' / 'results.csv'
text = ledger.read_text()
if ROW not in text.splitlines():
    with ledger.open('a', newline='') as f:
        f.write(('' if text.endswith('\n') else '\n') + ROW + '\n')
exe = ROOT / 'target' / 'release' / ('fastflyer-bank-stats.exe' if os.name == 'nt' else 'fastflyer-bank-stats')
out = subprocess.check_output([str(exe), '10000', str(DEST)], cwd=ROOT, text=True).strip()
_, distance, extensions, failures, conserved = out.split('\t')
key = DEST.relative_to(ROOT).as_posix()
new = {'sha256': sha256(DEST.read_bytes()).hexdigest(), 'ticks': 10000, 'distance': int(distance),
       'speed_bps': int(distance) * 10 / 10000, 'extensions': int(extensions), 'extension_failures': int(failures),
       'endpoint_conserved': conserved == 'true'}
entries = dict(cat['entries']); entries[key] = new
order = [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / 'flyers' / 'bank').rglob('*.flyer'))]
assert set(order) == set(entries), set(order) ^ set(entries)
cat['entries'] = {k: entries[k] for k in order}
cat_path.write_text(json.dumps(cat, indent=2) + '\n', encoding='utf-8')
print('banked', DEST, new)
