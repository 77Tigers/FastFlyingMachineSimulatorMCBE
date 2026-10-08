"""Bounded period-12 mv4 assembly attempt; no simulation or format changes.

Nominal identity trajectories include all abstract reset/settle order branches.
Core pulses may recruit a different eligible member: actual Rust screening is
therefore essential and nominal identity closure is not claimed.
"""
from pathlib import Path
import sys, random, heapq, json, collections, itertools, subprocess
ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'contacts'))
from fastflyer import Flyer,Block,Kind
from competition_contract_snapshot import tick as competition_tick
from observer_contract_snapshot import INITIAL as COMPETITION_INITIAL
OUT=Path(__file__).resolve().parent
D=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
PORTS=((1,-1),(0,-1),(2,0),(1,0))
K=(Kind.SLIME,Kind.HONEY,Kind.SLIME)
def add(p,q):return tuple(a+b for a,b in zip(p,q))
def shift(p,x):return (p[0]+x,p[1],p[2])
def disp(t,i):return (t+2-i)//3
def connected(cells):
 if not cells:return set()
 got={min(cells)};todo=list(got)
 while todo:
  p=todo.pop()
  for d in D:
   q=add(p,d)
   if q in cells and q not in got:got.add(q);todo.append(q)
 return got

# All reachable competition trajectories, normalized against the target core,
# symmetrized across interchangeable members. Include the transient prefix.
COMPETITION=[set() for _ in range(3)]
joint={tuple(COMPETITION_INITIAL)}
for t in range(21):
 for bank in joint:
  for x,s,owner in bank:
   ph=None if owner is None else PORTS[owner][0]
   COMPETITION[t%3].add((x-disp(t,0),s,ph))
 following=set()
 for bank in joint:
  results,failure=competition_tick(bank,t)
  assert failure is None,failure
  following.update(results)
 joint=following
def before(t,f,anchor):
 phase=f%3;base=anchor-disp(f,phase)
 return [(base+disp(t,phase)+x,s,None if owner is None else (owner+phase)%3)
         for x,s,owner in COMPETITION[(t-phase)%3]]
def canonical(t,f,anchor):
 cycle,r=divmod(t-f,12)
 x=sum(u<r for u in (4,6,8,10))
 owner=((r-1)+f)%3 if r in (5,7,9,11) else None
 return (anchor+4*cycle+x,(0,1,2,3)[r] if r<4 else 0,owner)

def build(seed,compact=False,corecap=None):
 rng=random.Random(seed);ss=[set() for _ in range(3)];ps=[];sources=[]
 gap=(3,4,5)[seed%3];phaseorder=list(range(12));rng.shuffle(phaseorder)
 # The bounded family also varies target axial planes and module orientations.
 planes=[0,0,0] if seed<9 else [rng.randrange(-2,3) for _ in range(3)]
 pickup=[set() for _ in range(3)];memberpickup={}
 for j,f in enumerate(phaseorder if not compact else []):
  cy=(j%4)*gap;cz=(j//4)*gap
  anchor=disp(f,f%3)+planes[f%3]-1
  p=(anchor,cy,cz);ps.append((p,f,anchor))
  ss[f%3].add((planes[f%3],cy,cz))
  faces=list(D[2:]);rng.shuffle(faces)
  # Two phase-1 ports share an axial ribbon on one transverse face.
  for rel,off,face in ((1,-1,faces[0]),(1,0,faces[0]),(0,-1,faces[1]),(2,0,faces[2])):
   i=(f+rel)%3;q=shift(add(p,face),off-disp(f,i))
   ss[i].add(q);pickup[i].add(q);memberpickup.setdefault((i,f),set()).add(q)
  i=(f+1)%3;face=faces[3];q=shift(add(p,face),-disp(f,i))
  facing=D.index(tuple(-v for v in face));sources.append((q,i,facing,f))

 if compact:
  gap=(6 if seed<18 else 4)+(seed%2);planes=[rng.randrange(-1,2) for _ in range(3)]
  if 18<=seed<24:planes=[0,0,0]
  centers=[(0,0),(gap,0),(gap//2,gap)]
  rotate=[rng.randrange(4) for _ in range(3)]
  reflect=[rng.choice((-1,1)) for _ in range(3)]
  for ph,(cy,cz) in enumerate(centers):
   base=planes[ph]-1
   def yz(y,z):
    y*=reflect[ph]
    for _ in range(rotate[ph]):y,z=-z,y
    return cy+y,cz+z
   def local(i,x,y,z):
    yy,zz=yz(y,z);return (base+x-disp(ph,i),yy,zz)
   spots=((1,0),(-1,0),(0,1),(2,1))
   ownside=((1,1),(-2,0),(1,1),(1,1))
   previous=((2,0),(-1,1),(-1,1),(2,0))
   for member,(y,z) in enumerate(spots):
    f=ph+3*member;a=base+member;yy,zz=yz(y,z);ps.append(((a,yy,zz),f,a))
    ss[ph].add(local(ph,1,y,z))
    for i,x,site in ((ph,-1,ownside[member]),((ph+2)%3,0,previous[member])):
     p=local(i,x,*site);ss[i].add(p);memberpickup.setdefault((i,f),set()).add(p);pickup[i].add(p)
    following=(ph+1)%3
    ribbon=(0,0) if member<3 else (3,1)
    for x in (-1,0):
     p=local(following,x,*ribbon);ss[following].add(p);memberpickup.setdefault((following,f),set()).add(p);pickup[following].add(p)
   for y,z,dy,dz in ((0,-1,0,1),(3,2,0,-1)):
    rp=local((ph+1)%3,0,y,z);yy,zz=yz(y+dy,z+dz);ry,rz=yz(y,z)
    face=D.index((0,yy-ry,zz-rz));sources.append((rp,(ph+1)%3,face,ph))

 # Phase-aware piston/arm positions and source positions before every tick.
 fixed=[]
 for t in range(12):
  pist=[]
  for p,f,a in ps:
   for x,s,o in before(t,f,a):pist.append(((x,p[1],p[2]),s,o,f))
  fixed.append(pist)
 # Compile time-labelled hardware keepouts into local-frame sparse sets.
 fixedbad=[set() for _ in range(3)]
 for i in range(3):
  for t in range(12):
   dx=disp(t,i);starts=t%3==i
   for pp,s,owner,f in fixed[t]:
    fixedbad[i].add(shift(pp,-dx))
    if s in (1,2):fixedbad[i].add(shift(pp,1-dx))
    if starts and s==0 and (owner is None or owner==(t-1)%3):
     for d in D:
      p=shift(add(pp,d),-dx)
      redundant=i==f%3 and shift(pp,1-dx) in ss[i]
      if p in memberpickup.get((i,f),()) or (i==f%3 and d==D[0]) or redundant:continue
      fixedbad[i].add(p)
   for rp,j,face,f in sources:
    r=shift(rp,disp(t,j)-dx)
    if i==j:fixedbad[i].add(r)
    else:
     for a in (0,1) if starts else (0,):
      for b in (0,1) if t%3==j else (0,):
       q=shift(r,b-a);fixedbad[i].add(q)
       fixedbad[i].update(add(q,d) for d in D)
 bodybad=[set() for _ in range(3)]
 def refresh():
  for i in range(3):
   forbidden=set()
   for j,cells in enumerate(ss):
    if i==j:continue
    shifts={disp(t,j)-disp(t,i)+b-a for t in range(12)
            for a in ((0,1) if t%3==i else (0,))
            for b in ((0,1) if t%3==j else (0,))}
    for p in cells:
     for dx in shifts:
      q=shift(p,dx);forbidden.add(q)
      if K[i]==K[j]:forbidden.update(add(q,d) for d in D)
   bodybad[i]=forbidden
 refresh()
 def legal(p,i,mandatory=False):
  if not mandatory:
   return p not in fixedbad[i] and p not in bodybad[i],('compiled_keepout',i,p)
  for t in range(12):
   q=shift(p,disp(t,i));moving=(t-1)%3==i;starts=t%3==i
   for j,cells in enumerate(ss):
    if j==i:continue
    for a in (0,1) if starts else (0,):
     for b in (0,1) if t%3==j else (0,):
      rel=shift(q,a-disp(t,j)-b)
      if rel in cells:return False,('body_overlap',t,i,j,p)
      if K[i]==K[j] and any(add(rel,d) in cells for d in D):return False,('same_material_contact',t,i,j,p)
   for rp,j,face,f in sources:
    r=shift(rp,disp(t,j))
    if i==j:
     if q==r:return False,('source_overlap',t,i,p)
    else:
     for a in (0,1) if starts else (0,):
      for b in (0,1) if t%3==j else (0,):
       if sum(abs(v-w) for v,w in zip(shift(q,a),shift(r,b)))<=1:return False,('foreign_source_contact',t,i,j,p)
   for pp,s,owner,f in fixed[t]:
    if q==pp:return False,('piston_overlap',t,i,f,p)
    if s in (1,2) and q==shift(pp,1):return False,('arm_overlap',t,i,f,p)
    adjacent=sum(abs(v-w) for v,w in zip(q,pp))==1
    if adjacent and starts and s==0 and (owner is None or owner==(t-1)%3):
     if p in memberpickup.get((i,f),()):continue
     # A competitor can transport an eligible member through its drive face.
     # This is a real extra pickup omitted by the side-port abstraction.
     if i==f%3 and q==shift(pp,1):continue
     if i==f%3 and shift(pp,1-disp(t,i)) in ss[i]:continue
     return False,('unplanned_pickup',t,i,f,p)
  return True,None
 for i,cells in enumerate(ss):
  for p in cells:
   ok,why=legal(p,i,True)
   if not ok:return None,why
 # Source owners receive shortest admissible sticky attachment.
 for rp,i,face,f in sources:
  opts=[]
  for d in D:
   p=add(rp,d);ok,why=legal(p,i)
   if ok:opts.append((min(sum(abs(a-b) for a,b in zip(p,q)) for q in ss[i]),rng.random(),p))
  if not opts:return None,('source_attachment',f,i,rp)
  ss[i].add(min(opts)[-1])
  refresh()
 bounds=(-7,7,-5,3*gap+5,-5,2*gap+5)
 for i in rng.sample(range(3),3):
  refresh()
  while len(connected(ss[i]))<len(ss[i]):
   reached=connected(ss[i]);goals=ss[i]-reached
   todo=[(0,rng.random(),p) for p in reached];heapq.heapify(todo)
   best={p:0 for p in reached};prev={};end=None;cache={}
   while todo:
    cost,_,p=heapq.heappop(todo)
    if cost!=best[p]:continue
    if p in goals:end=p;break
    if cost>(corecap if corecap is not None else ((28 if seed<18 else 25) if compact else 180))-len(ss[i]):continue
    for d in rng.sample(D,6):
     q=add(p,d)
     if not all(bounds[2*k]<=q[k]<=bounds[2*k+1] for k in range(3)):continue
     if q not in ss[i]:
      if q not in cache:cache[q]=legal(q,i)[0]
      if not cache[q]:continue
     nc=cost+int(q not in ss[i])
     if nc<best.get(q,10000):best[q]=nc;prev[q]=p;heapq.heappush(todo,(nc,rng.random(),q))
   if end is None:return None,('route',i,len(ss[i]),len(reached))
   while end not in reached:ss[i].add(end);end=prev[end]
 # Derive the cycle-boundary moving flags and real owner list.
 flyer=Flyer(rng_state=5,push_limit=512);ownerpos={}
 for p,f,a in ps:
  x,s,o=canonical(0,f,a);q=(x,p[1],p[2]);ownerpos[f]=q
  if q in flyer._cells:return None,('initial_overlap',q)
  flyer._cells[q]=Block.piston(0,state=s,moving=o is not None)
  if s in (1,2):flyer._cells[shift(q,1)]=Block(Kind.PISTON_ARM)
 for i,cells in enumerate(ss):
  for p in cells:
   if p in flyer._cells:return None,('initial_overlap',p)
   flyer._cells[p]=Block(K[i],moving=i==2)
 for rp,i,face,f in sources:
  if rp in flyer._cells:return None,('initial_overlap',rp)
  flyer._cells[rp]=Block.observer(face,powered=i==1,moving=i==2)
 moving=[q for q,b in flyer._cells.items() if b.moving]
 flyer.set_piston_blocks(ownerpos[11],moving)
 return (flyer,dict(seed=seed,gap=gap,planes=planes,compact=compact,counts=list(map(len,ss)),segments=[sorted(s) for s in ss],pistons=ps,sources=sources,initial_owner=ownerpos[11],initial_moving=moving)),None

if __name__=='__main__':
 revision=sys.argv[2] if len(sys.argv)>2 else 'v2'
 out=OUT/f'candidates_{revision}';out.mkdir(parents=True,exist_ok=True);stats=collections.Counter();records=[]
 for seed in range(min(30,int(sys.argv[1]) if len(sys.argv)>1 else 30)):
  ans,why=build(seed)
  if ans:
   f,m=ans;f.save(out/f's{seed}_diagnostic_pl512.flyer');records.append(m);stats['routed']+=1
  else:stats[str(why[0])]+=1;records.append(dict(seed=seed,failure=why))
  print(seed,dict(stats),flush=True)
 (OUT/f'manifest_{revision}.json').write_text(json.dumps(dict(stats=stats,layouts=records),indent=2))
 if stats['routed']:
  result=subprocess.run([str(ROOT/'target/release/fastflyer-research.exe'),'screen',str(out),'120','--out',str(OUT/f'screen_{revision}.csv')],capture_output=True,text=True)
  (OUT/f'screen_{revision}.txt').write_text(result.stdout+result.stderr);print(result.stdout,result.stderr)
