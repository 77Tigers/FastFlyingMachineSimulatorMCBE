"""Actual negative-X open mv4 layers. No rearward recovery dependencies.

Each bank retains its own target pickup, but both other recovery carriers and
its observer source belong to the layer AHEAD. The driver is the saved ring.
Routing an interior/tail prototype is followed by literal 1/2/4/8-layer tests.
This file does not modify the simulator or the earlier loop builder.
"""
import argparse, collections, importlib.util, json, random, sys, time
from pathlib import Path
import ring as r

spec=importlib.util.spec_from_file_location('backward_builder',r.EXPERIMENTS/'mv4_redesign_20261004/builder.py')
b=importlib.util.module_from_spec(spec)
source=Path(spec.origin).read_text()
source=source.replace('planes=[0]*N',"planes=cfg.get('planes',[0]*N)")
source=source.replace('bounds=(-5,5,','bounds=(min(planes)-6,max(planes)+6,')
source=source.replace('refresh()\n for i,cells in enumerate(ss):',
    'refresh()\n globals()["LAST_MANDATORY"]=[set(v) for v in ss]\n for i,cells in enumerate(ss):')
exec(compile(source,spec.origin,'exec'),b.__dict__)
BASE=json.loads((r.HERE/'ring_winner.json').read_text())


def configure(depth,pitch,mask=0,rotation=0,reflection=1,radius=10,spacing=6):
    n=12*(depth+1);b.N=n;b.K=[b.Kind.SLIME if (i%2)^(i//12%2)==0 else b.Kind.HONEY for i in range(n)]
    f=list(BASE['config']['following']);p=list(BASE['config']['previous_carrier'])
    for layer in range(1,depth+1):
        for j in range(12):
            # Alternating layer materials keep same-phase runs separate.
            # Pick opposite-material recovery cores in adjacent symmetry copies.
            df=-3 if mask&(1<<(j%3)) else 3
            dp=-3 if mask&(1<<(3+j%3)) else 3
            f.append((layer-1)*12+(j+1+df)%12)
            p.append((layer-1)*12+(j-1+dp)%12)
    cfg=BASE['config'] | dict(following=f,previous_carrier=p,
        planes=[BASE['config']['planes'][j]-pitch*l for l in range(depth+1) for j in range(12)])
    rots=list(BASE['rotations'])+[(v+rotation)%4 for l in range(depth) for v in BASE['rotations']]
    refs=list(BASE['reflections'])+[v*reflection for l in range(depth) for v in BASE['reflections']]
    centers=[]
    for q in range(4):
        for j in range(3):
            _,y,z=r.rotate((0,radius,(j-1)*spacing),q);centers.append((y,z))
    placement=(BASE['centers']+centers*depth,rots,refs)
    global SHIFTS
    SHIFTS={(i,j):{b.disp(t,j)-b.disp(t,i)+v-u for t in range(3)
        for u in ((0,1) if t%3==i%3 else (0,))
        for v in ((0,1) if t%3==j%3 else (0,))} for i in range(n) for j in range(n) if i!=j}
    return n,cfg,placement


def obstacles(cells,j,i):
    result=set()
    shifts=SHIFTS[i,j]
    for p in cells:
        for dx in shifts:
            q=b.shift(p,dx);result.add(q)
            if b.K[i]==b.K[j]:result.update(b.add(q,d) for d in b.D)
    return result


def route(must,fixed,bounds,cap,rng,deadline,report):
    n=len(must);must=list(map(set,must));routes=list(map(set,must))
    reps=[12*l+p for l in range(n//12) for p in range(3)]
    orbits={i:[(i+3*q,q) for q in range(4)] for i in reps}
    blocked=list(map(set,fixed))
    for i in range(n):
        for j in range(n):
            if i!=j:blocked[i].update(obstacles(must[j],j,i))
    for i in reps:
        for j,q in orbits[i]:blocked[i].update(r.rotated(blocked[j],-q))
    history={i:collections.Counter() for i in reps};best=None
    for iteration in range(80):
        if time.monotonic()>deadline:break
        for i in rng.sample(reps,len(reps)):
            weights=collections.Counter({p:v*.5 for p,v in history[i].items()})
            for member,q in orbits[i]:
                for j in range(n):
                    if j==member:continue
                    for p in obstacles(routes[j]-must[j],j,member):weights[r.rotate(p,-q)]+=2+iteration*.7
            candidate=set(must[i])
            while len(r.base.components(candidate))>1:
                path=r.base.bridge(candidate,blocked[i],weights,bounds,rng,deadline)
                if path is None or len(candidate)+len(path)>cap:break
                candidate.update(path)
            if len(r.base.components(candidate))==1:
                for j,q in orbits[i]:routes[j]=r.rotated(candidate,q)
        hits=0
        for i in range(n):
            for j in range(i):
                hit=routes[i]&obstacles(routes[j],j,i);hits+=len(hit)
                rep=12*(i//12)+i%3;history[rep].update(r.rotated(hit,-((i%12)//3)))
                rep=12*(j//12)+j%3
                history[rep].update(r.rotated(routes[j]&obstacles(routes[i],i,j),-((j%12)//3)))
        missing=sum(len(r.base.components(s))-1 for s in routes)
        score=(missing,hits,max(map(len,routes)),sum(map(len,routes)))
        if best is None or score<best:
            best=score;report.update(best=score,iteration=iteration)
            print('route',iteration,score,flush=True)
        if not missing and not hits:return routes
    return None


def build(depth,pitch,seconds=90,seed=0,cap=300,mask=0,rotation=0,reflection=1):
    n,cfg,placement=configure(depth,pitch,mask,rotation,reflection);report={}
    def joint(must,fixed,bounds,limit,rng):
        report['mandatory']=list(map(len,must))
        return route(must,fixed,bounds,limit,rng,time.monotonic()+seconds,report)
    ans,why=b.build(seed,placement,cap=cap,joint_router=joint,config=cfg)
    return ans,dict(depth=depth,pitch=pitch,seed=seed,mask=mask,rotation=rotation,reflection=reflection,rejection=why,**report)


def assemble(depth,payload=3):
    """Copy the SAME interior and end geometry; never reroute after growth."""
    assert depth>=1
    meta=json.loads((r.HERE/'backward_prototype.json').read_text())
    pitch=meta['pitch'];n,cfg,placement=configure(depth,pitch)
    source=[set(map(tuple,s)) for s in meta['segments']]
    routes=source[:12]
    for layer in range(1,depth+1):
        src=24 if layer==depth else 12
        offset=-pitch*(layer-(2 if src==24 else 1))
        routes.extend({b.shift(p,offset) for p in source[src+j]} for j in range(12))
    capture={}
    def take(must,fixed,bounds,*args):capture.update(must=must,fixed=fixed,bounds=bounds)
    ans,why=b.build(0,placement,cap=500,joint_router=take,config=cfg)
    assert why==('joint_route',),why
    def valid(candidate):
        return (all(capture['must'][i]<=candidate[i] and not candidate[i]&capture['fixed'][i]
                    and len(r.base.components(candidate[i]))==1 for i in range(n))
                and not any(candidate[i]&obstacles(candidate[j],j,i) for i in range(n) for j in range(i)))
    assert valid(routes),'literal copied geometry collision'
    payload_info=None
    if payload:
        # Search only the end's downward finger, not the repeating hardware.
        # The other three fingers are exact quarter-turn images.
        hardware_bottom=min([p['y'] for p in meta['pistons']]+[s['pos'][1] for s in meta['sources']])
        for j in range(n-12,n):
            if payload_info:break
            for p in sorted(routes[j],key=lambda p:p[1]):
                if p[1]>hardware_bottom:continue
                q=(j%12)//3;rep=n-12+j%3
                stem=r.rotated({(p[0],y,p[2]) for y in range(hardware_bottom-payload,p[1])},-q)
                trial=list(map(set,routes))
                for k in range(4):trial[rep+3*k].update(r.rotated(stem,k))
                if valid(trial):
                    routes=trial;payload_info=dict(template=j%3,base=p,hardware_bottom=hardware_bottom,
                        free_cells_below_hardware=payload,added_per_copy=len(stem));break
        assert payload_info,'no clear end payload finger'
    ans,why=b.build(0,placement,cap=500,joint_router=lambda *args:routes,config=cfg)
    assert ans,why
    flyer,result=ans;flyer.push_limit=160
    result.update(depth=depth,pitch=pitch,payload=payload_info,
        source='backward_prototype.json',literal_repeat=True)
    return flyer,result


def write_tags(flyer,meta,path,saved):
    """Explicit phases handle end cores without their own observers."""
    offset=tuple(min(p[k] for p in saved._cells)-min(p[k] for p in flyer._cells) for k in range(3))
    tags={tuple(p):i%3 for i,s in enumerate(meta['segments']) for p in s}
    tags.update({tuple(s['pos']):s['owner']%3 for s in meta['sources']})
    path.write_text(''.join('%d %d %d %d\n'%(*(p[k]+offset[k] for k in range(3)),phase) for p,phase in sorted(tags.items())))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=int,default=90)
    parser.add_argument('--depth',type=int,default=2);parser.add_argument('--pitch',type=int,default=10)
    parser.add_argument('--seed',type=int,default=0);args=parser.parse_args()
    ans,report=build(args.depth,args.pitch,args.seconds,args.seed)
    path=r.HERE/'backward_status.json'
    previous=json.loads(path.read_text()) if path.exists() else []
    if ans:
        f,m=ans;f.push_limit=512;f.save(r.HERE/'backward_prototype.flyer')
        m.update(depth=args.depth,pitch=args.pitch)
        (r.HERE/'backward_prototype.json').write_text(json.dumps(m,indent=2))
        report.update(routed=True,counts=m['counts'])
    previous.append(report);path.write_text(json.dumps(previous,indent=2))
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
