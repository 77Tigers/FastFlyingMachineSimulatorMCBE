"""Finite local obstruction check for one hub powering four side pistons."""
import sys,json,itertools,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent
EASY=HERE.parent/'mv4_easy_20261004'
sys.path.insert(0,str(EASY))
import common as c
import builder

control=json.loads((HERE/'control.json').read_text())
assert control['same_content_hash'] and control['short80_pass']
meta=json.loads((EASY/'compact43/reroute_best.json').read_text())
place=(meta['centers'],meta['rotations'],meta['reflections'])
sites=((1,0),(-1,0),(0,1),(0,-1))
own=tuple(map(tuple,meta['parent']['own']))
prev=tuple(map(tuple,meta['parent']['previous']))
dirs=builder.D
def neighbors(y,z):return [(y+d[1],z+d[2]) for d in dirs if d[0]==0]
last_own=neighbors(0,-1)
last_prev=last_own
records=[]
for hub_x,d,own_d,prev_d in itertools.product((-1,0),dirs,last_own,last_prev):
    source=(hub_x-d[0],-d[1],-d[2])
    cfg=dict(piston_sites=sites,
             following_ribbons=((0,0),)*4,
             own=own[:3]+(own_d,),previous=prev[:3]+(prev_d,),
             observers=((source[0],source[1],source[2],*d),))
    rec=dict(hub_x=hub_x,direction=d,source=source,
             own_d=own_d,previous_d=prev_d)
    if hub_x!=0:
        rec['outcome']='wrong_firing_plane'
    elif source in ((-1,0,0),(0,0,0)):
        rec['outcome']='observer_overlaps_required_ribbon'
    else:
        captured={}
        def capture(must,fixed,bounds,cap,rng):
            captured.update(must=[set(s) for s in must],fixed=fixed)
            return None
        _,why=builder.build(0,place,cap=39,joint_router=capture,config=cfg)
        rec['outcome']='local_mandatory_clear' if captured else why[0]
        if captured:
            rec['mandatory_counts']=[len(s) for s in captured['must']]
    records.append(rec)
status=dict(control_passed=True,totals=dict(collections.Counter(r['outcome'] for r in records)),
            checked=len(records),first_failure=next((r for r in records if r['outcome']!='local_mandatory_clear'),None),
            first_survivor=next((r for r in records if r['outcome']=='local_mandatory_clear'),None),
            no_global_route_requested=True)
c.write_json(HERE/'four_spokes_results.json',status)
with (HERE/'four_spokes_cases.jsonl').open('w') as fp:
    for r in records:fp.write(json.dumps(r)+'\n')
print(json.dumps(status,indent=2))
