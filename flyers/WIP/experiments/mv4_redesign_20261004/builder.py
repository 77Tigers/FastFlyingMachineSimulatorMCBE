"""Parameterized copy of the six-core builder; original synthesis/six.py stays unchanged."""
from search import OUT,ROOT,D,COMPETITION,add,shift,connected,canonical
from fastflyer import Flyer,Block,Kind
import random,heapq,json,collections,subprocess,sys
N=6
K=[Kind.SLIME if i%2==0 else Kind.HONEY for i in range(N)]
OWN=((1,1),(-2,0),(1,1),(1,1))
PREVIOUS=((2,0),(-1,1),(-1,1),(2,0))
DEFAULT=dict(piston_sites=((1,0),(-1,0),(0,1),(2,1)),
             own=OWN,previous=PREVIOUS,
             following_ribbons=((0,0),(0,0),(0,0),(3,1)),
             observers=((0,-1,0,1),(3,2,0,-1)),
             following=tuple((i+1)%N for i in range(N)),
             previous_carrier=tuple((i+2)%N for i in range(N)))
def disp(t,i):return (t+2-(i%3))//3

def shortest_component_bridge(cells,blocked,bounds,rng):
 groups=[];left=set(cells)
 while left:
  root=min(left);part={root};stack=[root];left.remove(root)
  while stack:
   p=stack.pop()
   for d in D:
    q=add(p,d)
    if q in left:left.remove(q);part.add(q);stack.append(q)
  groups.append(part)
 if len(groups)==1:return set()
 pq=[];dist={};owner={};prev={}
 for j,part in enumerate(groups):
  for p in sorted(part):dist[p]=0;owner[p]=j;prev[p]=None;heapq.heappush(pq,(0,rng.random(),p))
 bestcost=100000;meeting=None
 while pq:
  cost,_,p=heapq.heappop(pq)
  if cost!=dist[p]:continue
  if cost>bestcost:break
  for d in D:
   q=add(p,d)
   if not all(bounds[2*k]<=q[k]<=bounds[2*k+1] for k in range(3)):continue
   if q not in cells and q in blocked:continue
   if q in owner and owner[q]!=owner[p]:
    total=cost+dist[q]
    if total<bestcost:bestcost=total;meeting=(p,q)
   elif cost+int(q not in cells)<dist.get(q,100000):
    dist[q]=cost+int(q not in cells);owner[q]=owner[p];prev[q]=p;heapq.heappush(pq,(dist[q],rng.random(),q))
 if meeting is None:return None
 path=set()
 for p in meeting:
  while p is not None:
   if p not in cells:path.add(p)
   p=prev[p]
 return path

def build(seed,placement=None,cap=25,joint_router=None,config=None):
 cfg=DEFAULT | (config or {})
 spots=tuple(map(tuple,cfg['piston_sites']))
 ownfaces=tuple(map(tuple,cfg['own']))
 prevfaces=tuple(map(tuple,cfg['previous']))
 ribbons=tuple(map(tuple,cfg['following_ribbons']))
 observers=tuple(map(tuple,cfg['observers']))
 following=tuple(cfg['following']);previous_carrier=tuple(cfg['previous_carrier'])
 if any(len(q)!=4 for q in (spots,ownfaces,prevfaces,ribbons)) or len(following)!=N or len(previous_carrier)!=N:
  raise ValueError('Expected four piston-member entries and six carrier assignments')
 if any(following[i]%3!=(i+1)%3 or previous_carrier[i]%3!=(i+2)%3 for i in range(N)):
  raise ValueError('Carrier phase mismatch')
 def carrier(bank,rel):return (bank,following[bank],previous_carrier[bank])[rel]
 rng=random.Random(seed);ss=[set() for _ in range(N)];ports={};ps=[];sources=[]
 if placement is None:
  radius=4+(seed%2)
  centers=[(0,radius),(radius,radius//2),(radius,-radius//2),(0,-radius),(-radius,-radius//2),(-radius,radius//2)]
  rotations=[rng.randrange(4) for _ in range(N)];reflections=[rng.choice((-1,1)) for _ in range(N)]
 else:centers,rotations,reflections=placement
 planes=[0]*N
 for bank,(cy,cz) in enumerate(centers):
  ph=bank%3;base=planes[bank]-1
  def yz(y,z):
   y*=reflections[bank]
   for _ in range(rotations[bank]):y,z=-z,y
   return cy+y,cz+z
  def local(owner,x,y,z):
   yy,zz=yz(y,z);return (base+x-disp(ph,owner),yy,zz)
  for m,((y,z),own,previous) in enumerate(zip(spots,ownfaces,prevfaces)):
   pid=4*bank+m;f=ph+3*m;a=base+m;yy,zz=yz(y,z);ps.append(dict(pid=pid,bank=bank,f=f,anchor=a,y=yy,z=zz))
   ss[bank].add(local(bank,1,y,z))
   for owner,x,site in ((bank,-1,own),(previous_carrier[bank],0,previous)):
    p=local(owner,x,*site);ss[owner].add(p);ports.setdefault((owner,pid),set()).add(p)
   owner=following[bank];site=ribbons[m]
   for x in (-1,0):p=local(owner,x,*site);ss[owner].add(p);ports.setdefault((owner,pid),set()).add(p)
  for spec in observers:
   if len(spec)==4:
    y,z,dy,dz=spec;x=dx=0
   elif len(spec)==6:
    x,y,z,dx,dy,dz=spec
   else:raise ValueError('Observer uses (y,z,dy,dz) or (x,y,z,dx,dy,dz)')
   owner=following[bank];rp=local(owner,x,y,z);a,b=yz(y+dy,z+dz);c,d=yz(y,z)
   sources.append(dict(pos=rp,owner=owner,direction=D.index((dx,a-c,b-d)),bank=bank))
 fixed=[]
 for t in range(3):
  entries=[]
  for pspec in ps:
   bank=pspec['bank'];ph=bank%3
   for x,s,rel in COMPETITION[(t-ph)%3]:
    q=(planes[bank]-1+disp(t,bank)+x,pspec['y'],pspec['z'])
    owner=None if rel is None else carrier(bank,rel)
    entries.append((q,s,owner,pspec['pid'],bank))
  fixed.append(entries)
 fixedbad=[set() for _ in range(N)]
 for i in range(N):
  for t in range(3):
   dx=disp(t,i);starts=t%3==i%3
   for pp,s,owner,pid,bank in fixed[t]:
    fixedbad[i].add(shift(pp,-dx))
    if s in (1,2):fixedbad[i].add(shift(pp,1-dx))
    if starts and s==0 and (owner is None or owner%3==(t-1)%3):
     redundant=i==bank and shift(pp,1-dx) in ss[i]
     for d in D:
      p=shift(add(pp,d),-dx)
      equivalent_side=d[0]==0 and any(q[0]==p[0] for q in ports.get((i,pid),()))
      if equivalent_side or redundant:continue
      fixedbad[i].add(p)
   for source in sources:
    j=source['owner'];r=shift(source['pos'],disp(t,j)-dx)
    if i==j:fixedbad[i].add(r)
    else:
     for a in (0,1) if starts else (0,):
      for b in (0,1) if t%3==j%3 else (0,):
       q=shift(r,b-a);fixedbad[i].add(q);fixedbad[i].update(add(q,d) for d in D)
 bodybad=[set() for _ in range(N)]
 def refresh():
  for i in range(N):
   forbidden=set()
   for j,cells in enumerate(ss):
    if i==j:continue
    shifts={disp(t,j)-disp(t,i)+b-a for t in range(3)
            for a in ((0,1) if t%3==i%3 else (0,))
            for b in ((0,1) if t%3==j%3 else (0,))}
    for p in cells:
     for dx in shifts:
      q=shift(p,dx);forbidden.add(q)
      if K[i]==K[j]:forbidden.update(add(q,d) for d in D)
   bodybad[i]=forbidden
 refresh()
 for i,cells in enumerate(ss):
  for p in cells:
   if p in fixedbad[i]:return None,('hardware',i,p)
   if p in bodybad[i]:return None,('body_contact',i,p)
 # All observers already touch the hub/ribbon they hard-power.
 for source in sources:
  p=add(source['pos'],D[source['direction']])
  if p not in ss[source['owner']]:return None,('source_attachment',source)
 bounds=(-5,5,min(y for y,z in centers)-6,max(y for y,z in centers)+6,min(z for y,z in centers)-6,max(z for y,z in centers)+6)
 if joint_router is not None:
  routed=joint_router(ss,fixedbad,bounds,cap,rng)
  if routed is None:return None,('joint_route',)
  ss=routed
 # Interleave short connections so one completed body cannot monopolize all
 # corridors around the other bodies' mandatory terminals.
 for i in (rng.sample(range(N),N)*16 if joint_router is None else []):
  refresh()
  if len(connected(ss[i]))<len(ss[i]):
   reached=connected(ss[i]);goals=ss[i]-reached
   path=shortest_component_bridge(ss[i],fixedbad[i]|bodybad[i],bounds,rng)
   if path is None or len(ss[i])+len(path)>cap:
    report=dict(seed=seed,carrier=i,counts=list(map(len,ss)),segments=[sorted(s) for s in ss],centers=centers,rotations=rotations,reflections=reflections,pistons=ps,sources=sources,unreached=sorted(goals),neighbor_reasons=[dict(point=q,hardware=q in fixedbad[i],body=q in bodybad[i]) for p in goals for q in [add(p,d) for d in D]])
    (OUT/f'six_route_failure_s{seed}.json').write_text(json.dumps(report,indent=2));return None,('route',i,len(ss[i]),len(reached))
   ss[i].update(path)
 flyer=Flyer(rng_state=5,push_limit=512);owners={};movingowners={}
 for pspec in ps:
  bank=pspec['bank'];x,s,ophase=canonical(0,pspec['f'],pspec['anchor']);q=(x,pspec['y'],pspec['z'])
  owner=None if ophase is None else carrier(bank,(ophase-bank%3)%3)
  flyer._cells[q]=Block.piston(0,state=s,moving=owner is not None)
  if owner is not None:movingowners[q]=owner
  if s in (1,2):flyer._cells[shift(q,1)]=Block(Kind.PISTON_ARM)
  if bank%3==2 and pspec['f']==11:owners[bank]=q
 for i,cells in enumerate(ss):
  for p in cells:
   if p in flyer._cells:return None,('initial_overlap',p)
   flyer._cells[p]=Block(K[i],moving=i%3==2)
   if i%3==2:movingowners[p]=i
 for source in sources:
  p=source['pos'];i=source['owner']
  if p in flyer._cells:return None,('initial_overlap',p)
  flyer._cells[p]=Block.observer(source['direction'],powered=i%3==1,moving=i%3==2)
  if i%3==2:movingowners[p]=i
 for i,pos in owners.items():flyer.set_piston_blocks(pos,[q for q,j in movingowners.items() if j==i])
 return (flyer,dict(seed=seed,counts=list(map(len,ss)),centers=centers,rotations=rotations,reflections=reflections,segments=[sorted(s) for s in ss],pistons=ps,sources=sources,config=cfg)),None

if __name__=='__main__':
 out=OUT/'six_candidates';out.mkdir(exist_ok=True);stats=collections.Counter();records=[]
 for seed in range(12):
  ans,why=build(seed)
  if ans:
   f,m=ans;f.save(out/f's{seed}_diagnostic_pl512.flyer');records.append(m);stats['routed']+=1
  else:stats[why[0]]+=1;records.append(dict(seed=seed,failure=why))
  print(seed,dict(stats),records[-1].get('counts',why),flush=True)
 (OUT/'six_manifest.json').write_text(json.dumps(dict(stats=stats,layouts=records),indent=2))
