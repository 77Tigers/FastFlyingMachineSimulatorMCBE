"""Quarter-turn symmetric 12-core mv4 loop, no timing-helper bodies.

Reuses the existing four-actuator competition builder without changing it.
All three templates are copied four times, swapping slime/honey each turn.
Local carrier graph is F=i+1, P=i-1; this is not the old six-body route sweep.
One summary is overwritten, and only a screened winner is retained.
Usage: python ring.py --seconds 180 --route-seconds 2
Rebuild verified payload from saved geometry: python ring.py --rebuild
"""
import argparse, collections, importlib.util, itertools, json, random
import sys, time, tempfile, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
EXPERIMENTS=HERE.parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(EXPERIMENTS/'mv4_easy_20261004'))
import common as common
spec=importlib.util.spec_from_file_location('tile_builder',EXPERIMENTS/'mv4_redesign_20261004/builder.py')
b=importlib.util.module_from_spec(spec)
# Expose the prototype's formerly fixed axial planes in this experiment only.
# Original builder file is unchanged; every other instruction is reused verbatim.
builder_source=Path(spec.origin).read_text()
assert builder_source.count('planes=[0]*N')==1
exec(compile(builder_source.replace('planes=[0]*N',"planes=cfg.get('planes',[0]*N)"),spec.origin,'exec'),b.__dict__)
base=common.base
N=12
b.N=N
b.K=[b.Kind.SLIME if i%2==0 else b.Kind.HONEY for i in range(N)]
CFG=dict(following=tuple((i+1)%N for i in range(N)),
         previous_carrier=tuple((i-1)%N for i in range(N)))
SHIFTS={(i,j):{b.disp(t,j)-b.disp(t,i)+v-u for t in range(3)
              for u in ((0,1) if t%3==i%3 else (0,))
              for v in ((0,1) if t%3==j%3 else (0,))}
        for i in range(N) for j in range(N) if i!=j}


def rotate(p,k=1):
    x,y,z=p
    for _ in range(k%4):y,z=-z,y
    return x,y,z


def rotated(cells,k):return {rotate(p,k) for p in cells}


def obstacles(cells,j,i):
    result=set()
    for p in cells:
        for dx in SHIFTS[i,j]:
            q=b.shift(p,dx);result.add(q)
            if b.K[i]==b.K[j]:result.update(b.add(q,d) for d in b.D)
    return result


def add_payload(meta, length=3):
    """Add matching outward glue fingers, including one below all hardware.

    Checks compiled movement/adhesion keepouts; still requires real simulation.
    Returns a fresh flyer/metadata pair; never overwrites the input artifact.
    """
    routes=[set(map(tuple,s)) for s in meta['segments']]
    capture={}
    def take(must,fixed,bounds,*args):capture.update(must=must,fixed=fixed,bounds=bounds)
    placement=(meta['centers'],meta['rotations'],meta['reflections'])
    b.build(0,placement,cap=200,joint_router=take,config=meta['config'])
    bottom=min(p[1] for cells in routes for p in cells)
    for j in range(N):
        for p in sorted(routes[j]):
            if p[1]!=bottom:continue
            template=j%3;quarter=j//3
            stem={rotate((p[0],p[1]-d,p[2]),-quarter) for d in range(1,length+1)}
            trial=list(map(set,routes))
            for q in range(4):trial[template+3*q].update(rotated(stem,q))
            if any(trial[i]&capture['fixed'][i] for i in range(N)):continue
            if any(trial[i]&obstacles(trial[k],k,i) for i in range(N) for k in range(i)):continue
            ans,why=b.build(0,placement,cap=200,joint_router=lambda *args:trial,config=meta['config'])
            if ans:
                flyer,newmeta=ans;newmeta['payload']=dict(length=length,template=template,base_point=p,bottom_body=j)
                return flyer,newmeta
    return None


def route(must,fixed,bounds,cap,rng,deadline,report):
    must=list(map(set,must));routes=list(map(set,must))
    assert all(rotated(must[i%3],i//3)==must[i] for i in range(N))
    blocked=list(map(set,fixed))
    for i in range(N):
        for j in range(N):
            if i!=j:blocked[i].update(obstacles(must[j],j,i))
    for i in range(3):
        for q in range(1,4):blocked[i].update(rotated(blocked[i+3*q],-q))
    history=[collections.Counter() for _ in range(3)]
    best=None
    for iteration in range(32):
        if time.monotonic()>deadline:break
        for i in rng.sample(range(3),3):
            weights=collections.Counter({p:v*.5 for p,v in history[i].items()})
            for q in range(4):
                member=i+3*q
                for j in range(N):
                    if j==member:continue
                    for p in obstacles(routes[j]-must[j],j,member):
                        weights[rotate(p,-q)]+=2+iteration*.6
            candidate=set(must[i])
            while len(base.components(candidate))>1:
                path=base.bridge(candidate,blocked[i],weights,bounds,rng,deadline)
                if path is None or len(candidate)+len(path)>cap:break
                candidate.update(path)
            if len(base.components(candidate))==1:
                for q in range(4):routes[i+3*q]=rotated(candidate,q)
        hits=0
        for i in range(N):
            for j in range(i):
                hit=routes[i]&obstacles(routes[j],j,i)
                hits+=len(hit)
                history[i%3].update(rotated(hit,-(i//3)))
                history[j%3].update(rotated(routes[j]&obstacles(routes[i],i,j),-(j//3)))
        missing=sum(len(base.components(s))-1 for s in routes)
        score=(missing,hits,max(map(len,routes)),sum(map(len,routes)))
        if best is None or score<best:best=score;report['best']=score
        if not missing and not hits:return routes
    return None


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=int,default=180)
    parser.add_argument('--route-seconds',type=float,default=2)
    parser.add_argument('--compact',action='store_true')
    parser.add_argument('--stagger',action='store_true')
    parser.add_argument('--cap',type=int,default=30)
    parser.add_argument('--limit',type=int,default=36)
    parser.add_argument('--replay',action='store_true')
    parser.add_argument('--rebuild',action='store_true')
    args=parser.parse_args();start=time.monotonic();end=start+args.seconds
    if args.rebuild:
        meta=json.loads((HERE/'ring_payload.json').read_text())
        routes=[set(map(tuple,s)) for s in meta['segments']]
        placement=(meta['centers'],meta['rotations'],meta['reflections'])
        capture={}
        def take(must,fixed,*args):capture.update(must=must,fixed=fixed)
        b.build(0,placement,cap=200,joint_router=take,config=meta['config'])
        assert all(capture['must'][i]<=routes[i] and not routes[i]&capture['fixed'][i]
                   and len(base.components(routes[i]))==1 for i in range(N))
        assert not any(routes[i]&obstacles(routes[j],j,i) for i in range(N) for j in range(i))
        ans,why=b.build(0,placement,cap=200,joint_router=lambda *args:routes,config=meta['config'])
        assert ans,why
        flyer,_=ans;flyer.push_limit=64
        path=HERE/'ring_payload.flyer'
        if path.exists():assert flyer.content_hash()==b.Flyer.load(path).content_hash()
        flyer.save(path)
        print('Rebuilt verified payload geometry at encoded PL64',flush=True)
        return
    choices=list(itertools.product(range(4),repeat=3))
    reflections=list(itertools.product((-1,1),repeat=3))
    dimensions=((4,2),(5,3),(6,4)) if args.compact else ((5,2),(6,3),(7,3),(7,4),(8,4),(9,5))
    planes=list(itertools.product((-1,0,1),repeat=2)) if args.stagger else [(0,0)]
    cases=list(itertools.product(dimensions,choices,reflections,planes))
    random.Random(711).shuffle(cases)
    if args.replay:
        prior=json.loads((HERE/'ring_summary.json').read_text())
        seen=set();cases=[]
        for run in reversed(prior):
            for row in run['static_survivors']:
                key=((row['radius'],row['spacing']),tuple(row['rotations']),tuple(row['reflections']),tuple(row.get('axial',(0,0))))
                if key not in seen:seen.add(key);cases.append(key)
    stats=collections.Counter();survivors=[];best=None;done=0;last=start
    with tempfile.TemporaryDirectory(prefix='mv4_ring_') as tmp:
        tmp=Path(tmp)
        for case,((radius,spacing),rots,refs,axial) in enumerate(cases):
            if time.monotonic()>=end:break
            centers=[];rotations=[];refl=[]
            for q in range(4):
                for i in range(3):
                    _,y,z=rotate((0,radius,(i-1)*spacing),q)
                    centers.append((y,z));rotations.append((rots[i]+q)%4);refl.append(refs[i])
            placement=(centers,rotations,refl);info={}
            def joint(must,fixed,bounds,cap,rng):
                info['mandatory']=list(map(len,must))
                # Cheap independent connection screen before negotiated routing.
                counts=[]
                for i in range(3):
                    cells=set(must[i]);blocked=set(fixed[i])
                    for j in range(N):
                        if j!=i:blocked.update(obstacles(must[j],j,i))
                    while len(base.components(cells))>1:
                        path=base.bridge(cells,blocked,{},bounds,rng,min(end,time.monotonic()+2))
                        if path is None:
                            info['independent_failure']=dict(body=i,reason='no_path_or_timeout',count=len(cells));return None
                        cells.update(path)
                        if len(cells)>cap:
                            info['independent_failure']=dict(body=i,reason='cap',count=len(cells));return None
                    counts.append(len(cells))
                info['independent_counts']=counts
                return route(must,fixed,bounds,cap,rng,min(end,time.monotonic()+args.route_seconds),info)
            config=CFG | dict(planes=(0,*axial)*4)
            ans,why=b.build(case,placement,cap=args.cap,joint_router=joint,config=config)
            done+=1;stats[why[0] if why else 'routed']+=1
            if 'mandatory' in info:
                row=dict(case=case,radius=radius,spacing=spacing,rotations=rots,reflections=refs,axial=axial,**info)
                survivors.append(row)
                score=tuple(info.get('best',(999,999,info.get('independent_failure',{}).get('count',999),999)))
                if best is None or score<tuple(best['score']):best=dict(score=score,**row)
            if ans:
                flyer,meta=ans;flyer.push_limit=args.limit;candidate=tmp/'candidate.flyer';flyer.save(candidate)
                result=subprocess.run([str(common.AUDIT),str(candidate),'300',str(tmp/'audit.csv')],capture_output=True,text=True)
                stats['screen_pass' if result.returncode==0 else 'screen_fail']+=1
                # Audit status is checked explicitly below; its executable also prints counts.
                passed='passed 80/80' in result.stdout or '80/80' in result.stdout
                if passed and result.returncode==0:
                    flyer.save(HERE/'ring_working.flyer')
                    (HERE/'ring_winner.json').write_text(json.dumps(meta,indent=2))
                    print('WINNER',result.stdout,flush=True);break
            if time.monotonic()-last>25:
                print(json.dumps(dict(done=done,outcomes=stats,best=best)),flush=True);last=time.monotonic()
        summary=dict(done=done,total=len(cases),elapsed=round(time.monotonic()-start,1),outcomes=stats,best=best,
                     static_survivors=survivors,scope='12-core quarter-turn loop; no helpers; finite placement screen',glue_cap=args.cap,encoded_limit=args.limit)
        summary['dimensions']=dimensions
        summary['axial_choices']=planes
        log=HERE/'ring_summary.json'
        previous=json.loads(log.read_text()) if log.exists() else []
        if isinstance(previous,dict):previous=[previous]
        log.write_text(json.dumps(previous+[summary],indent=2))
        print(json.dumps({k:v for k,v in summary.items() if k!='static_survivors'}),flush=True)


if __name__=='__main__':main()
