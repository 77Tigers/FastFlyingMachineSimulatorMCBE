"""Greedy rerouting of one opposite pair; other pairs stay fixed.

Usage: python reroute.py [seconds=1200]. Finite seed/rail/reuse sweep per pass;
stops when a complete pass cannot improve size or bends, or at the deadline.
"""
import json,time,random,collections,sys
import common as c
if len(sys.argv)>2:
    c.HERE=c.HERE/sys.argv[2];c.HERE.mkdir(exist_ok=True)
start=time.monotonic();deadline=start+min(2700,int(sys.argv[1]) if len(sys.argv)>1 else 1200)
meta=json.loads((c.HERE/'pruned_best.json').read_text());data=c.capture(meta)
routes=[set(map(tuple,s)) for s in meta['segments']]
stats=collections.Counter();history=[];counter=0;passes=0;lastprint=0

while time.monotonic()<deadline:
    passes+=1;changed=False
    for i in sorted(range(3),key=lambda i:-len(routes[i])):
        for mode in ('flat','reuse','rail-4','rail-3','rail1'):
            weights={}
            if mode!='flat':
                bounds=data['bounds']
                for x in range(bounds[0],bounds[1]+1):
                    for y in range(bounds[2],bounds[3]+1):
                        for z in range(bounds[4],bounds[5]+1):
                            p=(x,y,z)
                            if mode=='reuse':weights[p]=0 if p in routes[i] else .4
                            else:weights[p]=.25*abs(x-int(mode[4:]))
            for seed in range(12):
                if time.monotonic()>=deadline:break
                stats['attempts']+=1
                blocked=c.blocked_pair(i,routes,data);candidate=set(data['must'][i])
                rng=random.Random(seed+passes*1000+i*100)
                while len(c.base.components(candidate))>1:
                    path=c.base.bridge(candidate,blocked,weights,data['bounds'],rng,
                                       min(deadline,time.monotonic()+.75))
                    if path is None or len(candidate)+len(path)>len(routes[i]):break
                    candidate.update(path)
                trial=[set(s) for s in routes];trial[i]=candidate;trial[i+3]=c.paired_router.mirrored(candidate)
                if c.valid(trial,data) and c.score(trial)<c.score(routes):
                    counter+=1;out=c.HERE/f'reroute_{counter:04d}.flyer'
                    limit=min(46,max(map(len,trial))+10)
                    c.save(meta,trial,out,limit);stats['screened']+=1
                    if c.screen(out):
                        routes=trial;changed=True;stats['accepted']+=1
                        history.append(dict(path=str(out),limit=limit,score=c.score(routes),body=i,mode=mode,seed=seed))
                        print(json.dumps(history[-1]),flush=True)
                        c.save(meta,routes,c.HERE/'reroute_best.flyer',limit)
                    else:stats['screen_failed']+=1
                if time.monotonic()-lastprint>=30:
                    state=dict(status='running',elapsed=round(time.monotonic()-start),statistics=stats,
                               passes=passes,score=c.score(routes),history=history)
                    (c.HERE/'reroute_status.json').write_text(json.dumps(state,indent=2))
                    print(json.dumps(dict(elapsed=state['elapsed'],stats=stats,score=c.score(routes))),flush=True)
                    lastprint=time.monotonic()
    if not changed:break
c.save(meta,routes,c.HERE/'reroute_best.flyer',min(46,max(map(len,routes))+10))
state=dict(status='completed' if time.monotonic()<deadline else 'time_limit_reached',
           elapsed=round(time.monotonic()-start),statistics=stats,passes=passes,
           score=c.score(routes),history=history)
(c.HERE/'reroute_status.json').write_text(json.dumps(state,indent=2));print(json.dumps(state),flush=True)
