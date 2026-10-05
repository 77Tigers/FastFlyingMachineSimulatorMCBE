"""All-sticky mv4: observers transported by collision ahead of rider pistons.

Members 0/2 and 1/3 clock each other. Nominally the opposite member's
observer pulses at exactly the desired extension, despite four transports.
No rigid auxiliary timing body. Simulation, not this nominal argument, decides.
"""
import importlib.util,json,time
from pathlib import Path
import sticky_backward as s
w=s.w;r=s.r
spec=importlib.util.spec_from_file_location('clock_builder',r.EXPERIMENTS/'mv4_redesign_20261004/builder.py')
b=importlib.util.module_from_spec(spec)
src=s.src
a=src.index('  for spec in observers:');z=src.index(' fixed=[]',a)
src=src[:a]+src[z:]
start=src.index(' fixed=[]');end=src.index(' fixedbad=',start)
src=src[:start]+''' fixed=[]
 for t in range(12):
  entries=[]
  for pspec in ps:
   bank=pspec['bank'];ph=(bank%3+1)%3
   x,state,ophase=canonical(t,pspec['f'],pspec['anchor'])
   owner=None if ophase is None else carrier(bank,(ophase-ph)%3)
   entries.append(((x,pspec['y'],pspec['z']),state,owner,pspec['pid'],bank))
  fixed.append(entries)
''' +src[end:]
src=src.replace('for t in range(3):','for t in range(12):')
# Keep source faces clear of glue. The source is a rider passenger, never an
# unaccounted autonomous body. It is pushed forward by its piston on each ride.
src=src.replace(' bodybad=[set() for _ in range(N)]', ''' for i in range(N):
  for t in range(12):
   dx=disp(t,i)
   for pp,state,owner,pid,bank in fixed[t]:
    observer=shift(pp,1-dx)
    fixedbad[i].add(observer)
    rel=(t-ps[pid]['f'])%12
    intended=rel in (4,6,8,10) and i==carrier(bank,(rel%3))
    if t%3==i%3 and not intended:fixedbad[i].update(add(observer,d) for d in D)
    mate=ps[pid^2]
    face=(0,mate['y']-ps[pid]['y'],mate['z']-ps[pid]['z'])
    fixedbad[i].add(add(observer,face))
 bodybad=[set() for _ in range(N)]''')
needle=' for i,cells in enumerate(ss):\n  for p in cells:\n   if p in flyer._cells:'
assert needle in src
src=src.replace(needle,''' clocks=[]
 for pspec in ps:
  bank=pspec['bank'];x,state,ophase=canonical(0,pspec['f'],pspec['anchor'])
  owner=None if ophase is None else carrier(bank,(ophase-(bank%3+1)%3)%3)
  q=(x+1,pspec['y'],pspec['z']);mate=ps[pspec['pid']^2]
  direction=D.index((0,mate['y']-pspec['y'],mate['z']-pspec['z']))
  if q in flyer._cells:return None,('clock_overlap',q)
  flyer._cells[q]=Block.observer(direction,powered=(0-pspec['f'])%12 in (0,6,8,10),moving=owner is not None)
  if owner is not None:movingowners[q]=owner
  clocks.append(dict(pos=q,member=pspec['pid'],direction=direction))
''' +needle)
src=src.replace('sources=sources,config=cfg','sources=sources,clocks=clocks,config=cfg')
src=src.replace("globals()['LAST_MANDATORY']=[set(v) for v in ss]", "globals()['LAST_MANDATORY']=[set(v) for v in ss];globals()['LAST_FIXED']=fixed;globals()['LAST_PS']=ps;globals()['LAST_PORTS']=ports")
exec(compile(src,spec.origin,'exec'),b.__dict__)
b.ROOT_BANKS=0
CFG=dict(piston_sites=[(0,0),(0,4),(1,0),(1,4)],
    own=[(-1,0),(-1,4),(2,0),(2,4)],
    previous=[(0,-1),(0,3),(1,-1),(1,3)],
    following_ribbons=[(0,1),(0,5),(1,1),(1,5)],observers=[])


def configure(depth=0,pitch=10,radius=12,spacing=8):
    n,cfg,large=w.configure(max(depth,1),pitch,radius=radius,spacing=spacing)
    n=12*(depth+1);b.N=n;b.K=list(w.b.K[:n]);w.b.N=n;w.b.K=list(b.K)
    centers=large[0][12:24]*(depth+1)
    rots=w.BASE['rotations']*(depth+1);refs=w.BASE['reflections']*(depth+1)
    following=[];previous=[]
    for layer in range(depth+1):
        for j in range(12):
            if layer==0:
                following.append((j-1)%12);previous.append((j+1)%12)
            else:
                following.append((layer-1)*12+(j-1+3)%12)
                previous.append((layer-1)*12+(j+1+3)%12)
    cfg=cfg|CFG|dict(following=following,previous_carrier=previous,
        planes=[w.BASE['config']['planes'][j]-pitch*l for l in range(depth+1) for j in range(12)])
    return n,cfg,(centers,rots,refs)


def build(depth=0,seconds=90,seed=0,pitch=10,radius=12,spacing=8):
    n,cfg,placement=configure(depth,pitch,radius,spacing);report={}
    def route(must,fixed,bounds,cap,rng):
        report['mandatory']=list(map(len,must))
        return w.route(must,fixed,bounds,cap,rng,time.monotonic()+seconds,report)
    ans,why=b.build(seed,placement,cap=500,joint_router=route,config=cfg)
    return ans,dict(depth=depth,pitch=pitch,radius=radius,spacing=spacing,seed=seed,rejection=why,**report)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--depth',type=int,default=0);p.add_argument('--seconds',type=int,default=90)
    p.add_argument('--seed',type=int,default=0);args=p.parse_args()
    ans,report=build(args.depth,args.seconds,args.seed)
    if ans:
        f,m=ans;f.push_limit=256;f.save(r.HERE/'sticky_clock.flyer')
        m.update(depth=args.depth,pitch=10)
        (r.HERE/'sticky_clock.json').write_text(json.dumps(m,indent=2))
        report.update(counts=m['counts'])
    (r.HERE/'sticky_clock_status.json').write_text(json.dumps(report,indent=2))
    print(report,flush=True)
