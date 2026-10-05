"""PL42-targeted cap32 companion to the approved compact pickup-face sweep."""
import sys, json, time, itertools, collections, functools
import common as c
import bend_bridge
start = time.monotonic()
deadline = start + min(2700, int(sys.argv[1]) if len(sys.argv)>1 else 2700)
out = c.HERE/'faces32';out.mkdir(exist_ok=True)
parents=json.loads((c.HERE/'compact_faces/plan.json').read_text())['parents']
ledger=out/'attempts.jsonl'
records=[json.loads(s) for s in ledger.read_text().splitlines()] if ledger.exists() else []
done={r['case'] for r in records};stats=collections.Counter(r['outcome'] for r in records)
cases=list(itertools.product(range(len(parents)),range(2),range(2)))
default=c.base.bridge;lastprint=0
for case,(pi,profile,seed) in enumerate(cases):
    if case in done:continue
    if time.monotonic()+4>=deadline:break
    parent=parents[pi];c.six.OWN=parent['own'];c.six.PREVIOUS=parent['previous'];report={}
    c.base.bridge=default if profile==0 else functools.partial(bend_bridge.bridge,bend=.15)
    def joint(must,fixed,bounds,cap,rng):
        return c.paired_router.route(must,fixed,bounds,cap,rng,min(deadline,time.monotonic()+3),report)
    ans,why=c.six.build(300000+case,parent['placement'],cap=32,joint_router=joint)
    record=dict(case=case,parent=pi,cap=32,profile=profile,seed=seed,report=report,outcome=why[0] if why else 'routed')
    if ans:
        f,m=ans;routes=[set(map(tuple,s)) for s in m['segments']];f.push_limit=max(map(len,routes))+10
        path=out/f'case{case:04d}_pl{f.push_limit}.flyer';f.save(path)
        m.update(parent=parent,geometry_score=c.score(routes));c.write_json(path.with_suffix('.json'),m)
        record.update(path=str(path),limit=f.push_limit,score=c.score(routes))
        record['outcome']='short80_pass' if c.screen(path) else 'short80_fail'
    with ledger.open('a') as fp:fp.write(json.dumps(record)+'\n')
    records.append(record);done.add(case);stats[record['outcome']]+=1
    if time.monotonic()-lastprint>30:
        state=dict(done=len(done),total=len(cases),elapsed=round(time.monotonic()-start),statistics=stats)
        c.write_json(out/'status.json',state);print(json.dumps(state),flush=True);lastprint=time.monotonic()
state=dict(status='completed' if len(done)==len(cases) else 'chunk_complete',done=len(done),
           total=len(cases),elapsed=round(time.monotonic()-start),statistics=stats)
c.write_json(out/'status.json',state);print(json.dumps(state),flush=True)
sys.exit(0 if state['status']=='completed' else 3)
