"""All-sticky +X bank: hold extended through the next core move, then retract
into air. All hardware is accounted for; no simulator changes. Unlike -X
pullers this is a push interface, an explicitly different research alternative.
Six members per core give time for six transports in an 18-tick bank cycle.
"""
import importlib.util,json,time
from pathlib import Path
import backward as w
r=w.r
spec=importlib.util.spec_from_file_location('sticky_push_builder',r.EXPERIMENTS/'mv4_redesign_20261004/builder.py')
b=importlib.util.module_from_spec(spec);src=Path(spec.origin).read_text()
def replace(a,z):
    global src
    assert a in src,a
    src=src.replace(a,z)
replace('planes=[0]*N',"planes=cfg.get('planes',[0]*N)")
replace('len(q)!=4','len(q)!=6')
replace('pid=4*bank+m','pid=6*bank+m')
replace("for owner,x,site in ((bank,-1,own),(previous_carrier[bank],0,previous)):",
        "for owner,x,site in ((bank,-2,own),(bank,-1,own),(previous_carrier[bank],-1,previous),(previous_carrier[bank],0,previous)):")
# Source specs may have an explicit carrier relative phase: 0 self or 1 F.
replace('for spec in observers:',"for spec,rel in observers:")
replace("owner=following[bank];rp=local(owner,x,y,z)","owner=bank if rel==0 else following[bank];rp=local(owner,x,y,z)")
a=src.index(' fixed=[]');z=src.index(' fixedbad=',a)
src=src[:a]+''' fixed=[]
 for t in range(18):
  entries=[]
  for pspec in ps:
   bank=pspec['bank'];x,state,ophase=canonical(t,pspec['f'],pspec['anchor'])
   owner=None if ophase is None else carrier(bank,(ophase-bank%3)%3)
   entries.append(((x,pspec['y'],pspec['z']),state,owner,pspec['pid'],bank))
  fixed.append(entries)
''' +src[z:]
replace('for t in range(3):','for t in range(18):')
replace('bounds=(-5,5,','bounds=(min(planes)-8,max(planes)+8,')
replace("min(y for y,z in centers)-6,max(y for y,z in centers)+6,min(z for y,z in centers)-6,max(z for y,z in centers)+6", "min(y for y,z in centers)-14,max(y for y,z in centers)+14,min(z for y,z in centers)-14,max(z for y,z in centers)+14")
replace('Block.piston(0,state=s,moving=owner is not None)','Block.piston(0,sticky=True,state=s,moving=owner is not None)')
replace("pspec['f']==11","pspec['f']==17")
replace("refresh()\n for i,cells in enumerate(ss):","refresh()\n globals()['LAST_MANDATORY']=[set(v) for v in ss]\n for i,cells in enumerate(ss):")
replace(' bodybad=[set() for _ in range(N)]', ''' # Empty extensions are permitted only into protected actuator lanes.
 # No foreign glue or own return path may be pushed/pulled there.
 for i in range(N):
  for pspec in ps:
   bank=pspec['bank']
   for x in range(planes[bank]-7,planes[bank]+8):
    if i==bank and x==planes[bank]:continue
    fixedbad[i].add((x,pspec['y'],pspec['z']))
 bodybad=[set() for _ in range(N)]''')
exec(compile(src,spec.origin,'exec'),b.__dict__)
def canonical(t,f,anchor):
    cycle,rel=divmod(t-f,18)
    x=anchor+6*cycle+sum(u<rel for u in (6,8,10,12,14,16))
    owner=(rel-1+f)%3 if rel in (7,9,11,13,15,17) else None
    state=(0,1,2,2,2,3)[rel] if rel<6 else 0
    return x,state,owner
b.canonical=canonical


def configure(depth=0,pitch=12,radius=24,spacing=14):
    _,cfg,large=w.configure(max(depth,1),pitch,radius=radius,spacing=spacing)
    n=12*(depth+1);b.N=n;b.K=list(w.b.K[:n]);w.b.N=n;w.b.K=list(b.K)
    centers=large[0][12:24]*(depth+1);rots=w.BASE['rotations']*(depth+1);refs=w.BASE['reflections']*(depth+1)
    spots=[(4*(m%3),4*(m//3)) for m in range(6)]
    own=[(y+1,z) for y,z in spots];previous=[(y-1,z) for y,z in spots];ribbons=[(y,z+1) for y,z in spots]
    observers=[]
    for y,z in spots:
        for x in (-1,0):observers.append(((x,y,z+2,0,0,-1),1))
        observers.append(((0,y+1,z,-1,0,0),0))
    following=[];prev=[]
    for layer in range(depth+1):
        for j in range(12):
            following.append((j+1)%12 if layer==0 else (layer-1)*12+(j+1+3)%12)
            prev.append((j-1)%12 if layer==0 else (layer-1)*12+(j-1+3)%12)
    cfg=cfg|dict(piston_sites=spots,own=own,previous=previous,following_ribbons=ribbons,
        observers=observers,following=following,previous_carrier=prev,
        planes=[w.BASE['config']['planes'][j]-pitch*l for l in range(depth+1) for j in range(12)])
    return n,cfg,(centers,rots,refs)


def build(depth=0,seconds=120,seed=0):
    n,cfg,place=configure(depth);report={}
    def route(must,fixed,bounds,cap,rng):
        report['mandatory']=list(map(len,must))
        return w.route(must,fixed,bounds,cap,rng,time.monotonic()+seconds,report)
    ans,why=b.build(seed,place,cap=500,joint_router=route,config=cfg)
    return ans,dict(depth=depth,seed=seed,rejection=why,**report)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--depth',type=int,default=0);p.add_argument('--seconds',type=int,default=120)
    args=p.parse_args();ans,report=build(args.depth,args.seconds)
    if ans:
        f,m=ans;f.push_limit=512;f.save(r.HERE/'sticky_push.flyer')
        m.update(depth=args.depth,pitch=12)
        (r.HERE/'sticky_push.json').write_text(json.dumps(m,indent=2));report['counts']=m['counts']
    (r.HERE/'sticky_push_status.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
