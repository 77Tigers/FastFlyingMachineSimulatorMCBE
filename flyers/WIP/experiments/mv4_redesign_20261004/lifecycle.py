"""Summarize actual reset/pickup overlap and seek the abstract reverse order."""
import sys,csv,json,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent
EASY=HERE.parent/'mv4_easy_20261004'
sys.path.insert(0,str(EASY))
import common as c
import competition_contract_snapshot as abstract
rows=list(csv.DictReader((HERE/'lifecycle_events.csv').open(encoding='utf-8-sig')))
for r in rows:r['tick']=int(r['tick']);r['step']=int(r['step']);r['id']=int(r['id'])
byid=collections.defaultdict(list)
for r in rows:byid[r['id']].append(r)
cycles=[];overlaps=[]
for pid,events in byid.items():
    fires=[i for i,r in enumerate(events) if r['event']=='state' and r['from']=='0' and r['to']=='1']
    for a,b in zip(fires,fires[1:]):
        span=events[a:b+1];first=span[0];end=span[-1]
        resets=[r for r in span if r['event']=='state' and r['from']=='3' and r['to']=='0']
        if resets:
            reset=resets[0]
            pickup=next((r for r in span if r['event']=='travel_start' and (r['tick'],r['step'])>(reset['tick'],reset['step'])),None)
            cycles.append(dict(pid=pid,fire=first['tick'],reset=reset['tick'],
                               pickup=pickup['tick'] if pickup else None,next_fire=end['tick']))
    bytick=collections.defaultdict(list)
    for r in events:bytick[r['tick']].append(r)
    for tick,evt in bytick.items():
        resets=[r for r in evt if r['event']=='state' and r['from']=='3' and r['to']=='0']
        moves=[r for r in evt if r['event']=='travel_start']
        for a in resets:
            for b in moves:
                if a['step']<b['step']:
                    overlaps.append(dict(tick=tick,pid=pid,reset_step=a['step'],pickup_step=b['step']))

# Abstract checker branches over within-tick actuator orders for the saved
# four-member contact contract. Find a reachable state where resetting first
# permits a pickup and starting the carrier first misses that same pickup.
states={tuple(abstract.INITIAL)};counterexample=None
for tick in range(24):
    following=set()
    for state in states:
        outcomes,failure=abstract.tick(state,tick)
        if failure:raise RuntimeError(failure)
        following.update(outcomes)
        for pid,(x,s,owner) in enumerate(state):
            if s!=3 or owner is not None:continue
            values={result[pid][2] for result in outcomes}
            if None in values and any(v is not None for v in values):
                selected={}
                for result,way in outcomes.items():
                    tag='picked' if result[pid][2] is not None else 'missed'
                    if tag not in selected:selected[tag]=dict(order=way['order'],result=result)
                if len(selected)==2:
                    counterexample=dict(tick=tick,member=pid,state=state,
                                        picked=selected['picked'],missed=selected['missed'])
                    break
        if counterexample:break
    if counterexample:break
    states=following

summary=dict(trace_ticks=240,fire_to_reset_deltas=dict(collections.Counter(r['reset']-r['fire'] for r in cycles)),
             next_fire_gaps=dict(collections.Counter(r['next_fire']-r['fire'] for r in cycles)),
             reset_then_pickup_same_tick=len(overlaps),first_overlap=overlaps[0] if overlaps else None,
             abstract_reverse_order=counterexample,
             conditional_four_member_bound_valid=False if overlaps else None,
             limit='One sampled simulator order plus the saved four-member abstract contact contract; no general three-member proof')
(HERE/'lifecycle_result.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='abstract_reverse_order'}))
print('abstract reverse order:',json.dumps(counterexample)[:1200] if counterexample else None)
