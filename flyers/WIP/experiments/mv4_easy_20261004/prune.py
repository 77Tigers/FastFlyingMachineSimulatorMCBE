"""Paired deletion and local shortcut sweep, preserving all existing interfaces.

Usage: python prune.py [seconds=600]. Only Astra's pruning/short-route directions.
No mechanism, power-source, piston or mandatory pickup changes.
"""
import json,time,random,collections,copy,sys
from pathlib import Path
import common as c
HERE=c.HERE
if len(sys.argv)>3:
    HERE=HERE/sys.argv[3];HERE.mkdir(exist_ok=True);c.HERE=HERE
start=time.monotonic();deadline=start+min(2700,int(sys.argv[1]) if len(sys.argv)>1 else 600)
source=Path(sys.argv[2]) if len(sys.argv)>2 else c.OLD/'ranked_a1.json'
meta=json.loads(source.read_text());data=c.capture(meta)
routes=[set(map(tuple,s)) for s in meta['segments']]
stats=collections.Counter();history=[];rng=random.Random(12345);counter=0

def try_candidate(i,candidate,method):
    global routes,counter
    trial=[set(s) for s in routes];trial[i]=candidate;trial[i+3]=c.paired_router.mirrored(candidate)
    stats['geometries']+=1
    if c.score(trial)>=c.score(routes) or not c.valid(trial,data):return False
    counter+=1;path=HERE/f'prune_{counter:04d}_pl46.flyer'
    limit=min(46,max(map(len,trial))+10)
    c.save(meta,trial,path,limit);stats['simulated']+=1
    if not c.screen(path):stats['screen_failure']+=1;return False
    routes=trial;stats['accepted']+=1
    history.append(dict(path=str(path),limit=limit,score=c.score(routes),method=method,body=i))
    print(json.dumps(history[-1]),flush=True)
    (HERE/'prune_best.json').write_text(json.dumps(dict(history=history,statistics=stats),indent=2))
    return True

def patches(i):
    s=routes[i];optional=s-data['must'][i]
    for p in sorted(optional):yield {p},'single_cell'
    # Short contiguous removable runs; unlike arbitrary subsets this is cheap.
    for p in sorted(optional):
        for radius in (1,2):
            patch={q for q in optional if sum(abs(q[k]-p[k]) for k in range(3))<=radius}
            if 1<len(patch)<=8:yield patch,f'local_radius{radius}'
    # Replace entire nonmandatory degree-two corridors, including detours wider
    # than the small-radius patches. Every resulting geometry is still checked.
    neighbors={p:[c.six.add(p,d) for d in c.six.D if c.six.add(p,d) in s] for p in s}
    seen=set()
    for p in sorted(optional):
        if p in seen or len(neighbors[p])!=2:continue
        run={p}
        for q in neighbors[p]:
            prev=p
            while q in optional and len(neighbors[q])==2 and q not in run:
                run.add(q);nxt=next(r for r in neighbors[q] if r!=prev);prev,q=q,nxt
        seen.update(run)
        if len(run)>1:yield run,'whole_corridor'

passes=0
while time.monotonic()<deadline:
    changed=False;passes+=1
    for i in sorted(range(3),key=lambda i:-len(routes[i])):
        blocked=c.blocked_pair(i,routes,data)
        for removed,method in list(patches(i)):
            stats['patches']+=1
            if time.monotonic()>=deadline:break
            candidate=routes[i]-removed
            if len(c.base.components(candidate))>1:
                cap=len(routes[i])-1
                while len(c.base.components(candidate))>1:
                    path=c.base.bridge(candidate,blocked,{},data['bounds'],rng,min(deadline,time.monotonic()+.4))
                    if path is None or len(candidate)+len(path)>cap:break
                    candidate.update(path)
                if len(c.base.components(candidate))>1:stats['overbudget_or_disconnected']+=1;continue
            if try_candidate(i,candidate,method):changed=True;break
    if not changed:break

state=dict(status='completed' if time.monotonic()<deadline else 'time_limit_reached',
           elapsed_seconds=round(time.monotonic()-start,1),passes=passes,statistics=stats,
           final_score=c.score(routes),history=history)
(HERE/'prune_status.json').write_text(json.dumps(state,indent=2))
c.save(meta,routes,HERE/'pruned_best.flyer',min(46,max(map(len,routes))+10))
print(json.dumps(state),flush=True)
