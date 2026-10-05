"""Export only the fully checked symmetric result; preserve raw evidence."""
from pathlib import Path
import csv,json,hashlib,shutil
HERE=Path(__file__).resolve().parent;FLYERS=HERE.parents[2]
rows=list(csv.DictReader((HERE/'symmetric_pl46.full80.csv').open()))
assert len(rows)==80 and all(r['pass']=='true' and r['ticks']=='10000' and r['distance']=='3333' and r['limit']=='46' for r in rows)
trace=(HERE/'symmetric_pl46.audit10000.txt').read_text()
for wanted in ('max_successful_action=46','extension_failures=0','movement_failures=0','conservation_mismatch_ticks=0','distance=3333'):
    assert wanted in trace,wanted
src=HERE/'mv4_symmetric_pl46.flyer';dest=FLYERS/'bank/pl46/mv4_symmetric.flyer'
dest.parent.mkdir(exist_ok=True);shutil.copyfile(src,dest)
shutil.copyfile(src,FLYERS/'WIP/mv4_symmetric_pl46.flyer')
ledger=FLYERS/'bank/results.csv';record='46,mv4_symmetric,12,3345,3333,238,20000'
if record not in ledger.read_text().splitlines():
    with ledger.open('a',newline='') as f:f.write(record+'\n')
summary=dict(cases=80,passed=80,ticks=10000,distance=3333,max_action=46,encoded_limit=46,
             glue_cells=198,core_glue_counts=[36,30,33,36,30,33],
             sha256=hashlib.sha256(src.read_bytes()).hexdigest(),artifact=str(dest),
             full_passenger_state_recurrence=False)
(HERE/'verification_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
