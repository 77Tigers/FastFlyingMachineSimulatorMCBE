"""Compact progress from append-only evidence; does not read live status files."""
import json,collections
import common as c
groups={};candidates=[];verified=[]
for ledger in sorted(c.HERE.glob('*/attempts.jsonl')):
    records=[json.loads(s) for s in ledger.read_text().splitlines() if s.endswith('}')]
    groups[ledger.parent.name]=dict(done=len(records),counts=dict(collections.Counter(r['outcome'] for r in records)))
    candidates.extend(dict(category=ledger.parent.name,**r) for r in records if r['outcome']=='short80_pass')
for summary in c.HERE.glob('validation/*/summary.json'):
    record=json.loads(summary.read_text())
    if record['status']=='verified':verified.append(dict(path=str(summary),limit=int(record['fields']['limit']),artifact=record.get('artifact')))
best=sorted(candidates,key=lambda r:(r['limit'],r['score']))[:5]
state=dict(groups=groups,verified=verified,best_short=[dict(category=r['category'],case=r['case'],limit=r['limit'],score=r['score'],path=r['path']) for r in best])
c.write_json(c.HERE/'overview.json',state);print(json.dumps(state,indent=2))
