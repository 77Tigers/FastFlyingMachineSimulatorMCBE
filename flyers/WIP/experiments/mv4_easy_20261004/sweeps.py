"""Finite easy-direction sweep; resume-safe chunks of at most45 minutes.

Usage: python sweeps.py CATEGORY [seconds=1200], CATEGORY flat/rail/bend/backbone/ports.
Reuses the57 saved ranked symmetric placements; preserves interfaces and phase
contracts. Each route receives up to3 seconds; no saved/simulated PL exceeds46.
"""
import json,time,random,collections,sys,csv,itertools,functools,re
import common as c
import bend_bridge

category=sys.argv[1];seconds=min(2700,int(sys.argv[2]) if len(sys.argv)>2 else 1200)
start=time.monotonic();deadline=start+seconds
OUT=c.HERE/category;OUT.mkdir(exist_ok=True)
raw=json.loads((c.OLD/'survey.json').read_text())['ranked'];pool=[];seen=set()
for p in raw:
    key=json.dumps([p['placement'],p['own'],p['previous']])
    if key not in seen:seen.add(key);pool.append(p)
if category=='flat':profiles=[dict(name='flat')];parents=pool;seeds=range(2)
elif category=='rail':profiles=[dict(name=f'rail{x}',rail=x) for x in (-4,-3,-2,0,1)];parents=pool[:12];seeds=range(2)
elif category=='bend':
    profiles=[dict(name=f'bend{b}_rail{r}',bend=b,rail=r) for b,r in ((.15,None),(.4,None),(.15,-3),(.15,1),(.4,-3))]
    parents=pool[:12];seeds=range(2)
elif category=='backbone':
    rails=[(-4,),(-3,),(-2,),(0,),(1,),(-4,-2),(-3,-2),(-3,1),(-2,1)]
    profiles=[dict(name='backbone'+','.join(map(str,r)),allowed_rails=r) for r in rails]
    parents=pool[:12];seeds=range(1)
elif category=='ports':
    # Replay the nine previously documented pickup-face choices. Same member
    # positions, recovery/pickup X obligations and observer power arrangement.
    variants=[(((1,1),(-2,0),(1,1),(1,1)),((2,0),(-1,1),(-1,1),(2,0)))]
    for b in [(-1,1),(-2,0)]:
        for d in [(1,1),(-1,1)]:
            for pd in [(0,2),(1,1),(-1,1)]:
                if pd==d:continue
                variants.append((((1,1),b,d,(1,1)),((2,0),(-2,0) if b==(-1,1) else (-1,1),pd,(2,0))))
    profiles=[dict(name=f'ports{j}',own=own,previous=previous) for j,(own,previous) in enumerate(variants)]
    parents=pool[:12];seeds=range(2)
elif category.startswith('lower'):
    target=int(re.match(r'lower(\d+)',category)[1])
    plan=OUT/'parents.json'
    if plan.exists():parents=json.loads(plan.read_text())
    else:
        successful=[]
        for ledgerpath in c.HERE.glob('*/attempts.jsonl'):
            for line in ledgerpath.read_text().splitlines():
                row=json.loads(line)
                if row['outcome']=='short80_pass':successful.append(row)
        bestlimit=min(row['limit'] for row in successful)
        parents=[];keys=set()
        for row in sorted(successful,key=lambda r:r.get('score',[])):
            if row['limit']!=bestlimit:continue
            m=json.loads(__import__('pathlib').Path(row['path']).with_suffix('.json').read_text())
            parent=m['parent'];key=json.dumps([parent['placement'],parent['own'],parent['previous']])
            if key not in keys:keys.add(key);parents.append(parent)
        c.write_json(plan,parents)
    profiles=[dict(name='flat'),dict(name='bend.15',bend=.15),dict(name='rail-3',rail=-3),
              dict(name='rail1',rail=1),dict(name='two_backbones',allowed_rails=(-3,1))]
    seeds=range(2)
else:raise ValueError(category)
caps=(target,target-1) if category.startswith('lower') else ((35,34,33) if category!='backbone' else (35,34))
cases=list(itertools.product(range(len(parents)),range(len(profiles)),caps,seeds))
ledger=OUT/'attempts.jsonl';records=[json.loads(s) for s in ledger.read_text().splitlines()] if ledger.exists() else []
done={r['case'] for r in records};stats=collections.Counter(r['outcome'] for r in records)
default_bridge=c.base.bridge;lastprint=0

def domain_reachable(must,blocked,bounds):
    reached={min(must)};todo=list(reached)
    while todo:
        p=todo.pop()
        for d in c.six.D:
            q=c.six.add(p,d)
            if q in reached or not all(bounds[2*k]<=q[k]<=bounds[2*k+1] for k in range(3)):continue
            if q not in must and q in blocked:continue
            reached.add(q);todo.append(q)
    return must<=reached

for index,(pi,mode,cap,seed) in enumerate(cases):
    if index in done:continue
    if time.monotonic()+4>=deadline:break
    parent=parents[pi];profile=profiles[mode];report={}
    if 'own' in profile:parent=dict(parent,own=profile['own'],previous=profile['previous'])
    c.six.OWN=parent['own'];c.six.PREVIOUS=parent['previous']
    route_seed=100000+index*7+seed
    if 'bend' in profile:c.base.bridge=functools.partial(bend_bridge.bridge,bend=profile['bend'])
    else:c.base.bridge=default_bridge
    def joint(must,fixed,bounds,cap,rng):
        if 'allowed_rails' in profile:
            fixed=[set(s) for s in fixed];rails=set(profile['allowed_rails'])
            for i in range(6):
                # Backbones plus X-directed terminal stubs. Opposite copies use
                # mirrored terminal columns, so the allowed domains also repeat.
                stems={(p[1],p[2]) for p in must[i]}
                for x in range(bounds[0],bounds[1]+1):
                    if x in rails:continue
                    for y in range(bounds[2],bounds[3]+1):
                        for z in range(bounds[4],bounds[5]+1):
                            if (y,z) not in stems:fixed[i].add((x,y,z))
                blocked=set(fixed[i])
                for j in range(6):
                    if j!=i:blocked.update(c.base.obstacles(must[j],j,i))
                if not domain_reachable(must[i],blocked,bounds):
                    report['rejection']='backbone_domain_disconnected';return None
        return c.paired_router.route(must,fixed,bounds,cap,rng,
                    min(deadline,time.monotonic()+3),report,profile.get('rail'))
    ans,why=c.six.build(route_seed,parent['placement'],cap=cap,joint_router=joint)
    record=dict(case=index,parent=pi,profile=profile,cap=cap,seed=seed,report=report,
                outcome=why[0] if why else 'routed')
    if ans:
        f,m=ans;routes=[set(map(tuple,s)) for s in m['segments']]
        f.push_limit=min(46,max(map(len,routes))+10)
        path=OUT/f'case{index:04d}_pl{f.push_limit}.flyer';f.save(path)
        m.update(parent=parent,profile=profile,geometry_score=c.score(routes))
        c.write_json(path.with_suffix('.json'),m)
        record.update(path=str(path),limit=f.push_limit,score=c.score(routes))
        record['outcome']='short80_pass' if c.screen(path) else 'short80_fail'
    elif report.get('rejection'):record['outcome']=report['rejection']
    with ledger.open('a') as f:f.write(json.dumps(record)+'\n')
    records.append(record);done.add(index);stats[record['outcome']]+=1
    if time.monotonic()-lastprint>=30:
        state=dict(status='running',elapsed_seconds=round(time.monotonic()-start,1),
                   cases_total=len(cases),cases_done=len(done),statistics=stats)
        c.write_json(OUT/'status.json',state);print(json.dumps(state),flush=True);lastprint=time.monotonic()
c.base.bridge=default_bridge
state=dict(status='completed' if len(done)==len(cases) else 'chunk_complete',
           elapsed_seconds=round(time.monotonic()-start,1),cases_total=len(cases),
           cases_done=len(done),statistics=stats)
c.write_json(OUT/'status.json',state);print(json.dumps(state),flush=True)
sys.exit(0 if state['status']=='completed' else 3)
