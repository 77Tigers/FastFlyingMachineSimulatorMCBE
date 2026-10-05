"""Survey two 2+2 hub motifs with <=3-cell own/previous pickup covers.

Only mandatory physical checks run here. Routing is a separate finite batch.
"""
import sys,json,time,itertools,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent
EASY=HERE.parent/'mv4_easy_20261004'
sys.path.insert(0,str(EASY))
import common as c
import builder
START=time.monotonic();DEADLINE=START+min(2700,int(sys.argv[1]) if len(sys.argv)>1 else 2700)
graph_results=json.loads((HERE/'graph_results.json').read_text())['selected'][:3]
raw=json.loads((EASY.parent/'mv4_elegant_20261004/survey.json').read_text())['ranked']
placements=[];seen=set()
for r in raw:
    key=json.dumps(r['placement'])
    if key not in seen:seen.add(key);placements.append(r['placement'])
motifs=[dict(name='square_columns',sites=((-1,-1),(-1,1),(1,-1),(1,1)),
             ribbons=((-1,0),(-1,0),(1,0),(1,0)),
             observers=((-2,0,1,0),(2,0,-1,0))),
        dict(name='offset_pairs',sites=((-1,0),(0,1),(2,1),(3,0)),
             ribbons=((0,0),(0,0),(2,0),(2,0)),
             observers=((0,-1,0,1),(2,-1,0,1)))]
steps=((1,0),(-1,0),(0,1),(0,-1))
def covers(sites):
    sets={}
    for offsets in itertools.product(steps,repeat=4):
        points=frozenset((site[0]+d[0],site[1]+d[1]) for site,d in zip(sites,offsets))
        if len(points)<=3 and points not in sets:sets[points]=tuple((site[0]+d[0],site[1]+d[1]) for site,d in zip(sites,offsets))
    return [dict(sites=sorted(s),assignment=a) for s,a in sorted(sets.items(),key=lambda q:(len(q[0]),sorted(q[0])))]
cover_sets=[covers(m['sites']) for m in motifs]
space=list((g,mi,oi,pi) for g in range(3) for mi in range(2)
           for oi in range(len(cover_sets[mi])) for pi in range(len(cover_sets[mi])))
ledger=HERE/'two_hubs_attempts.jsonl'
rows=[json.loads(s) for s in ledger.read_text().splitlines()] if ledger.exists() else []
done={(r['graph'],r['motif'],r['own'],r['previous']) for r in rows}
stats=collections.Counter(r['outcome'] for r in rows)
lastprint=0
for g,mi,oi,pi in space:
    key=(g,mi,oi,pi)
    if key in done:continue
    if time.monotonic()+4>=DEADLINE:break
    graph=graph_results[g];motif=motifs[mi]
    config=dict(piston_sites=motif['sites'],own=cover_sets[mi][oi]['assignment'],
                previous=cover_sets[mi][pi]['assignment'],
                following_ribbons=motif['ribbons'],observers=motif['observers'],
                following=graph['following'],previous_carrier=graph['previous'])
    capture={}
    def inspect(must,fixed,bounds,cap,rng):
        capture.update(must=[set(s) for s in must],fixed=fixed)
        return None
    _,why=builder.build(0,placements[graph['placement']],cap=39,joint_router=inspect,config=config)
    rec=dict(graph=g,motif=mi,own=oi,previous=pi,
             outcome='interface_valid' if capture else why[0])
    if not capture:rec['detail']=why
    if capture:
        must=capture['must'];counts=[len(s) for s in must]
        comps=[len(c.base.components(s)) for s in must]
        rec.update(counts=counts,components=comps,
                   score=[max(counts),sum(counts),max(comps),sum(comps)])
    with ledger.open('a') as fp:fp.write(json.dumps(rec)+'\n')
    rows.append(rec);done.add(key);stats[rec['outcome']]+=1
    if time.monotonic()-lastprint>30:
        report=dict(done=len(done),total=len(space),elapsed=round(time.monotonic()-START),outcomes=stats)
        c.write_json(HERE/'two_hubs_status.json',report);print(json.dumps(report),flush=True);lastprint=time.monotonic()

valid={}
for r in rows:
    if r['outcome']=='interface_valid':
        key=r['motif'],r['own'],r['previous']
        valid.setdefault(key,[]).append(r)
ranked=sorted(valid.items(),key=lambda q:(-len(q[1]),
              min(tuple(r['score']) for r in q[1]),
              len(cover_sets[q[0][0]][q[0][1]]['sites'])+len(cover_sets[q[0][0]][q[0][2]]['sites'])))
selected=[]
for (mi,oi,pi),recs in ranked:
    if len(selected)>=3:break
    selected.append(dict(motif=mi,motif_name=motifs[mi]['name'],
                         own=oi,previous=pi,valid_graphs=[r['graph'] for r in recs],
                         score=min((r['score'] for r in recs)),
                         config=dict(piston_sites=motifs[mi]['sites'],
                                     following_ribbons=motifs[mi]['ribbons'],
                                     observers=motifs[mi]['observers'],
                                     own=cover_sets[mi][oi]['assignment'],
                                     previous=cover_sets[mi][pi]['assignment'])))
result=dict(status='completed' if len(done)==len(space) else 'chunk_complete',
            done=len(done),total=len(space),elapsed=round(time.monotonic()-START),
            motifs=[m['name'] for m in motifs],cover_counts=list(map(len,cover_sets)),
            outcomes=stats,valid_face_pairs=len(valid),selected=selected,
            first_failure=next((r for r in rows if r['outcome']!='interface_valid'),None))
c.write_json(HERE/'two_hubs_results.json',result)
c.write_json(HERE/'two_hubs_status.json',{k:v for k,v in result.items() if k!='selected'})
print(json.dumps({k:v for k,v in result.items() if k!='selected'}),flush=True)
