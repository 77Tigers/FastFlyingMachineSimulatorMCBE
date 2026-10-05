"""Ordinary lower-limit validation of already short-screened geometry.

Usage: python limit_scan.py [limit=42]. Deduplicates geometry and skips candidates
already checked at this limit. Uses the existing portable 10,000-tick screen.
"""
import sys,json,csv,subprocess,shutil
from pathlib import Path
import common as c
from fastflyer import Flyer
limit=int(sys.argv[1]) if len(sys.argv)>1 else 42
OUT=c.HERE/f'limits{limit}';OUT.mkdir(exist_ok=True)
manifest=OUT/'manifest.json';records=json.loads(manifest.read_text()) if manifest.exists() else []
done={r['hash'] for r in records};sources=[]
for ledger in c.HERE.glob('*/attempts.jsonl'):
    for line in ledger.read_text().splitlines():
        r=json.loads(line)
        if r['outcome']=='short80_pass':sources.append(Path(r['path']))
for status in c.HERE.glob('*/reroute_status.json'):
    m=json.loads(status.read_text())
    sources.extend(Path(r['path']) for r in m.get('history',[]))
run=OUT/f'run{len(list(OUT.glob("run*"))):03d}';run.mkdir();pending=[]
for source in sources:
    f=Flyer.load(source);f.push_limit=limit
    try:hashed=f.content_hash()
    except ValueError as e:
        hashed='invalid:'+str(source)
        if hashed not in done:
            records.append(dict(hash=hashed,source=str(source),outcome='initial_limit_reject',error=str(e)));done.add(hashed)
        continue
    if hashed in done:continue
    dest=run/f'{hashed[:16]}.flyer';f.save(dest)
    if source.with_suffix('.json').exists():shutil.copyfile(source.with_suffix('.json'),dest.with_suffix('.json'))
    record=dict(hash=hashed,source=str(source),path=str(dest));pending.append(record);done.add(hashed)
if pending:
    csvpath=OUT/(run.name+'.csv')
    trial=subprocess.run([str(c.RUNNER),'screen',str(run),'10000','--out',str(csvpath)],
                         capture_output=True,text=True,timeout=1200)
    (OUT/(run.name+'.txt')).write_text(trial.stdout+trial.stderr)
    rows=list(csv.DictReader(csvpath.open()))
    # Keep all raw fields: clean stalled candidates must not count as successes.
    byname={Path(r.get('file',r.get('path',''))).stem:r for r in rows}
    for record in pending:
        r=byname.get(Path(record['path']).stem,{})
        record.update(outcome='screened',result=r)
        records.append(record)
c.write_json(manifest,records)
print(json.dumps(dict(limit=limit,new_candidates=len(pending),total=len(records),
                     screen_files=[str(p) for p in OUT.glob('run*.csv')])),flush=True)
