"""Bounded initial-state search for two/three members of existing port bank."""
import itertools
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from competition import run

pool=[(x,s,None) for x in (-1,0) for s in range(4)]+[(0,0,2),(-1,0,2)]
rows=[]
for n in (2,3):
    for ix in itertools.combinations_with_replacement(range(len(pool)),n):
        initial=[pool[i] for i in ix]
        result=run(initial=initial)
        rows.append({'initial':initial,**{k:v for k,v in result.items()
                     if k in ('valid','tick','ticks','reason','repeat_from_tick')}})
report={'pool':pool,'cases':len(rows),'positive_cases':sum(r['valid'] for r in rows),
        'latest_first_failure':max(r.get('tick',0) for r in rows),'results':rows}
Path(__file__).with_name('min_members.json').write_text(json.dumps(report,indent=2))
print({k:v for k,v in report.items() if k not in ('pool','results')})
