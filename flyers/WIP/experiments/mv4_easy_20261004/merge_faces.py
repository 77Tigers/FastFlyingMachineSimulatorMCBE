"""Merge finished, disjoint face-sweep worker ledgers; retain the raw evidence."""
import json, collections
import common as c
out = c.HERE / 'compact_faces'
statuses = [json.loads(p.read_text()) for p in out.glob('status*.json')]
if any(s.get('status') not in ('completed', 'chunk_complete') for s in statuses):
    raise SystemExit('A worker is still active; no ledger was changed.')
ledger = out / 'attempts.jsonl'
rows = [json.loads(s) for s in ledger.read_text().splitlines()]
known = {r['case']: r for r in rows}
for tail in out.glob('attempts_tail*.jsonl'):
    for line in tail.read_text().splitlines():
        row = json.loads(line)
        if row['case'] in known:
            if row != known[row['case']]:
                raise SystemExit('Conflicting duplicate case; no merge completed.')
            continue
        with ledger.open('a') as f:
            f.write(json.dumps(row) + '\n')
        rows.append(row);known[row['case']] = row
plan = json.loads((out / 'plan.json').read_text())
total = len(plan['parents']) * 12
missing = sorted(set(range(total)) - known.keys())
state = dict(stage='routing', status='completed' if not missing else 'chunk_complete',
             done=len(known), total=total, missing_cases=missing,
             statistics=dict(collections.Counter(r['outcome'] for r in rows)),
             raw_tail_ledgers_retained=any(out.glob('attempts_tail*.jsonl')))
c.write_json(out / 'status.json', state)
print(json.dumps(state))
