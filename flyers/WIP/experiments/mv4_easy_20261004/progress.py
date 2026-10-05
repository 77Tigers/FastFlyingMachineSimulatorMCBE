"""Small, read-only report of the approved face extension and its best routes."""
import json, collections, sys
from pathlib import Path
root = Path(__file__).resolve().parent
out = root / 'compact_faces'
plan = json.loads((out / 'plan.json').read_text())
rows = [json.loads(s) for ledger in out.glob('attempts*.jsonl') for s in ledger.read_text().splitlines() if s.endswith('}')]
rows = list({r['case']: r for r in rows}.values())
passed = sorted((r for r in rows if r['outcome'] == 'short80_pass'), key=lambda r: (r['limit'], r['score']))
if '--brief' in sys.argv:
    cap32 = root/'faces32/status.json'
    print(json.dumps(dict(faces_done=len(rows), faces_total=len(plan['parents'])*12,
                          outcomes=dict(collections.Counter(r['outcome'] for r in rows)),
                          best_new_limit=passed[0]['limit'] if passed else None,
                          cap32=json.loads(cap32.read_text()) if cap32.exists() else None)))
    raise SystemExit(0)
print(json.dumps(dict(
    status=json.loads((out / 'status.json').read_text()),
    tail_status=[json.loads(p.read_text()) for p in out.glob('status_tail*.json')],
    combined_done=len(rows), combined_total=len(plan['parents'])*12,
    covers=len(plan['face_sets']), placements=plan['placements'],
    survey=plan['survey_statistics'],
    outcomes=dict(collections.Counter(r['outcome'] for r in rows)),
    best=[dict(case=r['case'], limit=r['limit'], score=r['score'], path=r['path']) for r in passed[:3]]
), indent=2))
