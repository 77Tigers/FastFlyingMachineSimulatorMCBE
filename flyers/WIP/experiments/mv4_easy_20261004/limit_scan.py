"""Ordinary lower-limit validation of already short-screened geometry.

Usage: python limit_scan.py [limit=42]. Deduplicates geometry and skips candidates
already checked at this limit. Uses one exact core case, RNG5/XZ0, stopping at
the first failure. A single pass must still receive the full80-case validation.
"""
import sys,json,csv,subprocess,shutil
from pathlib import Path
import common as c
from fastflyer import Flyer
def _tb(n):
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
    from fastflyer.research import binary
    return binary(n)
limit=int(sys.argv[1]) if len(sys.argv)>1 else 42
OUT=c.HERE/f'limits{limit}';OUT.mkdir(exist_ok=True)
manifest=OUT/'manifest.json';records=json.loads(manifest.read_text()) if manifest.exists() else []
done={r['hash'] for r in records};sources=[]
portable_failures={}
for csvpath in OUT.glob('run*.csv'):
    for r in csv.DictReader(csvpath.open()):
        if r.get('clean')=='false':portable_failures[Path(r['file']).stem]=r
for ledger in c.HERE.glob('*/attempts*.jsonl'):
    for line in ledger.read_text().splitlines():
        r=json.loads(line)
        if r['outcome']=='short80_pass':sources.append(Path(r['path']))
sources.extend(c.HERE.glob('**/pruned_best.flyer'))
for status in [c.HERE/'reroute_status.json',*c.HERE.glob('*/reroute_status.json')]:
    if not status.exists():continue
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
    if hashed[:16] in portable_failures:
        records.append(dict(hash=hashed,source=str(source),outcome='portable_rejected',result=portable_failures[hashed[:16]]));done.add(hashed);continue
    dest=run/f'{hashed[:16]}.flyer';f.save(dest)
    if source.with_suffix('.json').exists():shutil.copyfile(source.with_suffix('.json'),dest.with_suffix('.json'))
    record=dict(hash=hashed,source=str(source),path=str(dest));pending.append(record);done.add(hashed)
if pending:
    for record in pending:
        path=Path(record['path']);csvpath=path.with_suffix('.one.csv')
        trial=subprocess.run([str(_tb('mv4-audit-one')),str(path),'10000',str(csvpath)],
                             capture_output=True,text=True,timeout=120)
        path.with_suffix('.one.txt').write_text(trial.stdout+trial.stderr)
        rows=list(csv.DictReader(csvpath.open()));r=rows[0] if rows else {}
        record.update(outcome='single_pass' if trial.returncode==0 else 'single_rejected',result=r)
        records.append(record)
c.write_json(manifest,records)
print(json.dumps(dict(limit=limit,new_candidates=len(pending),total=len(records),
                     outcomes=dict(__import__('collections').Counter(r['outcome'] for r in records)),
                     single_pass_paths=[r['path'] for r in records if r['outcome']=='single_pass'])),flush=True)
