"""Small capped routing batch for the surviving balanced 2+2 interface."""
import sys,json,time,itertools,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent
EASY=HERE.parent/'mv4_easy_20261004'
sys.path.insert(0,str(EASY))
import common as c
import builder
choices=json.loads((HERE/'two_hubs_results.json').read_text())['selected']
graphs=json.loads((HERE/'graph_results.json').read_text())['selected']
raw=json.loads((EASY.parent/'mv4_elegant_20261004/survey.json').read_text())['ranked']
placements=[];seen=set()
for q in raw:
    key=json.dumps(q['placement'])
    if key not in seen:seen.add(key);placements.append(q['placement'])
OUT=HERE/'hub_routes';OUT.mkdir(exist_ok=True)
records=[]
for ci,cap,seed in itertools.product(range(len(choices)),(32,29,25),range(2)):
    ch=choices[ci]
    for gi in ch['valid_graphs']:
        parent=graphs[gi];config=dict(ch['config'],following=parent['following'],previous_carrier=parent['previous'])
        place=placements[parent['placement']];report={};mode={'value':'general'}
        def joint(must,fixed,bounds,cap,rng):
            router=c.base.route
            if parent['symmetric'] and all(c.paired_router.mirrored(must[i])==must[i+3] for i in range(3)):
                router=c.paired_router.route;mode['value']='paired'
            return router(must,fixed,bounds,cap,rng,time.monotonic()+3,report)
        case=len(records)
        ans,why=builder.build(500000+case,place,cap=cap,joint_router=joint,config=config)
        rec=dict(case=case,choice=ci,graph=gi,cap=cap,seed=seed,mode=mode['value'],
                 report=report,outcome=why[0] if why else 'routed')
        if ans:
            f,m=ans;counts=m['counts'];f.push_limit=max(counts)+10
            path=OUT/f'case{case:03d}_pl{f.push_limit}.flyer';f.save(path)
            m.update(parent=ch,graph=parent,encoded_limit=f.push_limit)
            c.write_json(path.with_suffix('.json'),m)
            rec.update(path=str(path),limit=f.push_limit,counts=counts)
            rec['outcome']='short80_pass' if c.screen(path) else 'short80_fail'
        records.append(rec)
        print(json.dumps(rec),flush=True)
report=dict(status='completed',cases=len(records),outcomes=dict(collections.Counter(r['outcome'] for r in records)),
            short_passes=[r for r in records if r['outcome']=='short80_pass'])
c.write_json(OUT/'status.json',report)
