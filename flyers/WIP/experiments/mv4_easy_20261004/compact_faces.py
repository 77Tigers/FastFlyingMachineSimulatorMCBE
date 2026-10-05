"""User-approved extension: minimum-size pickup-face covers, same mechanisms.

Usage: python compact_faces.py [seconds=2700] [case_offset=0]. Resumes a saved plan.
First surveys all minimal face-set pairs on saved regular layouts. Then routes
all valid interfaces with caps35/33/31, flat/bend, two seeds. Each route
gets3 seconds; every chunk is at most45 minutes. No new power/lifecycle scheme.
"""
import sys,json,time,itertools,collections,random,functools
import common as c
import bend_bridge
START=time.monotonic();DEADLINE=START+min(2700,int(sys.argv[1]) if len(sys.argv)>1 else 2700)
OUT=c.HERE/'compact_faces';OUT.mkdir(exist_ok=True)
OFFSET=int(sys.argv[2]) if len(sys.argv)>2 else 0
STATUS=OUT/('status.json' if not OFFSET else f'status_tail{OFFSET}.json')
PISTONS=((1,0),(-1,0),(0,1),(2,1))

def covers():
    options=[[(y+1,z),(y-1,z),(y,z+1),(y,z-1)] for y,z in PISTONS]
    grouped={}
    for assignment in itertools.product(*options):
        points=frozenset(assignment)
        if points not in grouped:grouped[points]=assignment
    smallest=min(map(len,grouped))
    return [dict(sites=sorted(s),assignment=a) for s,a in sorted(grouped.items(),key=lambda q:sorted(q[0])) if len(s)==smallest],smallest

def mst(cells):
    groups=c.base.components(cells);reached={0};cost=0
    while len(reached)<len(groups):
        d,j=min((min(sum(abs(a[k]-b[k]) for k in range(3)) for a in groups[i] for b in groups[j]),j)
                for i in reached for j in range(len(groups)) if j not in reached)
        reached.add(j);cost+=d
    return cost

choices,minimum=covers();raw=json.loads((c.OLD/'survey.json').read_text())['ranked']
placements=[];seen=set()
for p in raw:
    key=json.dumps(p['placement'])
    if key not in seen:seen.add(key);placements.append(p['placement'])
surveyfile=OUT/'survey.jsonl';survey=[json.loads(s) for s in surveyfile.read_text().splitlines()] if surveyfile.exists() else []
done={r['case'] for r in survey};space=list(itertools.product(range(len(placements)),range(len(choices)),range(len(choices))))
lastprint=0
for case,(pi,oi,vi) in enumerate(space):
    if case in done:continue
    if time.monotonic()+4>=DEADLINE:break
    own=choices[oi]['assignment'];previous=choices[vi]['assignment'];data={}
    c.six.OWN=own;c.six.PREVIOUS=previous
    def inspect(must,fixed,bounds,cap,rng):
        ranks=[mst(s) for s in must[:3]]
        data.update(rank=[max(ranks),sum(ranks)],mandatory_counts=list(map(len,must)),
                    span_bounds=[max(len(s),1+sum(max(p[k] for p in s)-min(p[k] for p in s) for k in range(3))) for s in must])
        return None
    ans,why=c.six.build(0,placements[pi],cap=39,joint_router=inspect)
    record=dict(case=case,placement=placements[pi],own=own,previous=previous,
                own_sites=choices[oi]['sites'],previous_sites=choices[vi]['sites'],
                outcome='interface_valid' if data else why[0],**data)
    with surveyfile.open('a') as f:f.write(json.dumps(record)+'\n')
    survey.append(record);done.add(case)
    if time.monotonic()-lastprint>30:
        state=dict(stage='survey',done=len(done),total=len(space),elapsed=round(time.monotonic()-START))
        c.write_json(OUT/'status.json',state);print(json.dumps(state),flush=True);lastprint=time.monotonic()
if len(done)!=len(space):
    c.write_json(OUT/'status.json',dict(stage='survey',status='chunk_complete',done=len(done),total=len(space)))
    sys.exit(3)

planfile=OUT/'plan.json'
ranked=sorted((r for r in survey if r['outcome']=='interface_valid'),key=lambda r:(r['rank'],max(r['span_bounds']),sum(r['mandatory_counts'])))
if planfile.exists():
    plan=json.loads(planfile.read_text())
    # Keep existing case identities stable when adding the remaining valid covers.
    known={p['case'] for p in plan['parents']}
    extra=[p for p in ranked if p['case'] not in known]
    if extra:
        plan['parents'].extend(extra);c.write_json(planfile,plan)
else:
    parents=ranked
    plan=dict(face_set_minimum=minimum,face_sets=choices,placements=len(placements),survey_cases=len(space),
              survey_statistics=dict(collections.Counter(r['outcome'] for r in survey)),parents=parents)
    c.write_json(planfile,plan)
parents=plan['parents'];cases=list(itertools.product(range(len(parents)),(35,33,31),range(2),range(2)))
ledger=OUT/('attempts.jsonl' if not OFFSET else f'attempts_tail{OFFSET}.jsonl');records=[json.loads(s) for s in ledger.read_text().splitlines()] if ledger.exists() else []
completed={r['case'] for r in records};stats=collections.Counter(r['outcome'] for r in records)
default=c.base.bridge
for case,(pi,cap,profile,seed) in enumerate(cases):
    if case<OFFSET:continue
    if case in completed:continue
    if time.monotonic()+4>=DEADLINE:break
    parent=parents[pi];c.six.OWN=parent['own'];c.six.PREVIOUS=parent['previous'];report={}
    c.base.bridge=default if profile==0 else functools.partial(bend_bridge.bridge,bend=.15)
    def joint(must,fixed,bounds,cap,rng):
        return c.paired_router.route(must,fixed,bounds,cap,rng,min(DEADLINE,time.monotonic()+3),report)
    ans,why=c.six.build(200000+case,parent['placement'],cap=cap,joint_router=joint)
    record=dict(case=case,parent=pi,cap=cap,profile=profile,seed=seed,report=report,outcome=why[0] if why else 'routed')
    if ans:
        f,m=ans;routes=[set(map(tuple,s)) for s in m['segments']];f.push_limit=min(46,max(map(len,routes))+10)
        path=OUT/f'case{case:04d}_pl{f.push_limit}.flyer';f.save(path)
        m.update(parent=parent,geometry_score=c.score(routes));c.write_json(path.with_suffix('.json'),m)
        record.update(path=str(path),limit=f.push_limit,score=c.score(routes))
        record['outcome']='short80_pass' if c.screen(path) else 'short80_fail'
    with ledger.open('a') as f:f.write(json.dumps(record)+'\n')
    records.append(record);completed.add(case);stats[record['outcome']]+=1
    if time.monotonic()-lastprint>30:
        state=dict(stage='routing',offset=OFFSET,done=len(completed),total=len(cases)-OFFSET,elapsed=round(time.monotonic()-START),statistics=stats)
        c.write_json(STATUS,state);print(json.dumps(state),flush=True);lastprint=time.monotonic()
c.base.bridge=default
state=dict(stage='routing',status='completed' if len(completed)==len(cases)-OFFSET else 'chunk_complete',
           offset=OFFSET,done=len(completed),total=len(cases)-OFFSET,elapsed=round(time.monotonic()-START),statistics=stats)
c.write_json(STATUS,state);print(json.dumps(state),flush=True)
sys.exit(0 if state['status']=='completed' else 3)
