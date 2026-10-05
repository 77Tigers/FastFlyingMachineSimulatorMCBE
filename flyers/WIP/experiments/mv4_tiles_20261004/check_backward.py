"""Rebuild saved interfaces and check them with the UNCHANGED Rust simulator.

Uses explicit core phases, so a tail without observers is not misclassified.
One consolidated JSON retains all 80 sample rows; temporary flyers/tags/CSV
are removed automatically. No full passenger identity recurrence requirement.
"""
import argparse,csv,importlib,json,subprocess,tempfile
from pathlib import Path
import backward as w
HERE=w.r.HERE
CASES={
 'backward_prototype':('backward',512),
 'all_sticky':('sticky_backward',160),
 'sticky_prototype':('sticky_backward',256),
 'sticky_clock':('sticky_clock',256),
 'sticky_push':('sticky_push',512),
}


def rebuild(name,limit=None):
    module,encoded=CASES[name];mod=importlib.import_module(module)
    meta=json.loads((HERE/(name+'.json')).read_text());b=mod.b
    n=len(meta['segments']);b.N=n
    b.K=[b.Kind.SLIME if ((i%2)^(i//12%2))==0 else b.Kind.HONEY for i in range(n)]
    if module=='sticky_backward':b.ROOT_BANKS=0 if meta.get('all_sticky') else 12
    routes=[set(map(tuple,cells)) for cells in meta['segments']]
    def reuse(must,fixed,*args):
        assert all(must[i]<=routes[i] and not routes[i]&fixed[i] and len(w.r.base.components(routes[i]))==1 for i in range(n))
        return routes
    ans,why=b.build(meta['seed'],(meta['centers'],meta['rotations'],meta['reflections']),
        cap=1000,joint_router=reuse,config=meta['config'])
    assert ans,why
    flyer,unused=ans;flyer.push_limit=encoded if limit is None else limit
    existing=HERE/(name+'.flyer')
    if limit is None and existing.exists():assert flyer.content_hash()==b.Flyer.load(existing).content_hash(),'saved geometry hash changed'
    return flyer,meta


def check(name,ticks=300,limit=None):
    f,m=rebuild(name,limit);passed=0
    with tempfile.TemporaryDirectory(prefix='mv4_check_') as tmp:
        tmp=Path(tmp);flyer=tmp/'candidate.flyer';f.save(flyer)
        tags=tmp/'phases.tsv';w.write_tags(f,m,tags,w.b.Flyer.load(flyer));out=tmp/'samples.csv'
        proc=subprocess.run([str(w.r.EXPERIMENTS/'bin/mv4_chain_audit.exe'),str(flyer),str(ticks),str(out),str(f.push_limit),str(tags)],capture_output=True,text=True)
        rows=list(csv.DictReader(out.open()));passed=sum(row['pass']=='true' for row in rows)
    record=dict(case=name,ticks=ticks,encoded_limit=f.push_limit,hash=f.content_hash(),
        passed=passed,total=len(rows),exit_code=proc.returncode,samples=rows)
    path=HERE/'BACKWARD_CHECKS.json';previous=json.loads(path.read_text()) if path.exists() else []
    previous=[row for row in previous if (row['case'],row['ticks'],row['encoded_limit'])!=(name,ticks,f.push_limit)]
    previous.append(record);path.write_text(json.dumps(previous,indent=2))
    first=next((row['first_failure'] for row in rows if row['pass']!='true'),None)
    print(json.dumps(dict(case=name,ticks=ticks,limit=f.push_limit,passed=passed,total=len(rows),first_failure=first)),flush=True)
    return record


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case',choices=list(CASES));p.add_argument('--ticks',type=int,default=300)
    p.add_argument('--limit',type=int);p.add_argument('--rebuild',action='store_true');args=p.parse_args()
    if args.rebuild:
        f,m=rebuild(args.case,args.limit);f.save(HERE/(args.case+'.flyer'));print('Rebuilt',args.case,f.content_hash())
    else:check(args.case,args.ticks,args.limit)
