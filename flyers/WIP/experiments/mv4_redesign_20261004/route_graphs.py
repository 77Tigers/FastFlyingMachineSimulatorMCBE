"""Route the ten selected carrier interfaces, at caps32/29/25 and two seeds."""
import sys,json,time,itertools,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent
EASY=HERE.parent/'mv4_easy_20261004'
sys.path.insert(0,str(EASY))
import common as c
import builder
START=time.monotonic();DEADLINE=START+min(2700,int(sys.argv[1]) if len(sys.argv)>1 else 2700)
OUT=HERE/'graph_routes';OUT.mkdir(exist_ok=True)
state=json.loads((HERE/'graph_results.json').read_text())
selected=state['selected'];assert len(selected)==10
old=json.loads((EASY/'compact43/reroute_best.json').read_text())
raw=json.loads((EASY.parent/'mv4_elegant_20261004/survey.json').read_text())['ranked']
placements=[];seen=set()
for item in raw:
    key=json.dumps(item['placement'])
    if key not in seen:seen.add(key);placements.append(item['placement'])
cases=list(itertools.product(range(len(selected)),(32,29,25),range(2)))
ledger=OUT/'attempts.jsonl';records=[json.loads(s) for s in ledger.read_text().splitlines()] if ledger.exists() else []
done={r['case'] for r in records};stats=collections.Counter(r['outcome'] for r in records)
baseline_routes=[set(map(tuple,s)) for s in old['segments']]

def valid(routes,must,fixed):
    for i in range(6):
        if not must[i]<=routes[i] or routes[i]&fixed[i] or len(c.base.components(routes[i]))!=1:return False
        for j in range(i):
            if routes[i]&c.base.obstacles(routes[j],j,i):return False
    return True

lastprint=0
for case,(si,cap,seed) in enumerate(cases):
    if case in done:continue
    if time.monotonic()+4>=DEADLINE:break
    parent=selected[si];place=placements[parent['placement']]
    config=dict(own=old['parent']['own'],previous=old['parent']['previous'],
                following=parent['following'],previous_carrier=parent['previous'])
    report={};flags=dict(warm=False,mode='general')
    def joint(must,fixed,bounds,cap,rng):
        if (place==[old['centers'],old['rotations'],old['reflections']]
                and max(map(len,baseline_routes))<=cap
                and valid(baseline_routes,must,fixed)):
            flags.update(warm=True,mode='warm');return baseline_routes
        router=c.base.route
        if parent['symmetric'] and all(c.paired_router.mirrored(must[i])==must[i+3] for i in range(3)):
            router=c.paired_router.route;flags['mode']='paired'
        return router(must,fixed,bounds,cap,rng,min(DEADLINE,time.monotonic()+3),report)
    ans,why=builder.build(400000+case,place,cap=cap,joint_router=joint,config=config)
    record=dict(case=case,selected=si,mask=parent['mask'],placement=parent['placement'],
                cap=cap,seed=seed,mode=flags['mode'],warm=flags['warm'],report=report,
                outcome=why[0] if why else 'routed')
    if ans:
        f,m=ans;routes=[set(map(tuple,s)) for s in m['segments']]
        counts=[len(s) for s in routes];f.push_limit=max(counts)+10
        if f.push_limit>=50:raise RuntimeError('Exceeded user limit')
        path=OUT/f'case{case:03d}_pl{f.push_limit}.flyer';f.save(path)
        m.update(parent=parent,encoded_limit=f.push_limit,
                 counts=counts,geometry=dict(max_glue=max(counts),total_glue=sum(counts)))
        c.write_json(path.with_suffix('.json'),m)
        record.update(path=str(path),limit=f.push_limit,counts=counts)
        record['outcome']='short80_pass' if c.screen(path) else 'short80_fail'
    with ledger.open('a') as fp:fp.write(json.dumps(record)+'\n')
    done.add(case);records.append(record);stats[record['outcome']]+=1
    if time.monotonic()-lastprint>30:
        progress=dict(done=len(done),total=len(cases),elapsed=round(time.monotonic()-START),
                      outcomes=stats)
        c.write_json(OUT/'status.json',progress);print(json.dumps(progress),flush=True);lastprint=time.monotonic()
result=dict(status='completed' if len(done)==len(cases) else 'chunk_complete',
            done=len(done),total=len(cases),elapsed=round(time.monotonic()-START),outcomes=stats,
            short_passes=sorted((dict(case=r['case'],limit=r['limit'],counts=r['counts'],path=r['path'])
                                 for r in records if r['outcome']=='short80_pass'),
                                key=lambda r:(r['limit'],max(r['counts']))))
c.write_json(OUT/'status.json',result);print(json.dumps({k:v for k,v in result.items() if k!='short_passes'}),flush=True)
