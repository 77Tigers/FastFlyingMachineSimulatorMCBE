"""Friend's architecture: five back carriers, each with middle/front helpers.

Two sources on each middle keep its axial center empty for back pickup travel.
No simulation is implemented here: every file is screened by Rust.
"""
from pathlib import Path
import sys,random,heapq,functools,itertools,subprocess,os,json,time
from collections import Counter
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
D=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
PH=[0,2,4,1,3];REJECT=Counter()
def reject(s):REJECT[s]+=1
def add(p,q):return tuple(a+b for a,b in zip(p,q))
def shift(p,x):return(p[0]+x,p[1],p[2])
def make(centers,fronts,seed,cap=11):
 rng=random.Random(seed);rot=[rng.randrange(8) for _ in range(5)];seam=rng.randrange(5)
 def tr(i,p):
  x,y,z=p;r=rot[i]
  if r&4:y,z=z,y
  if r&1:y=-y
  if r&2:z=-z
  cy,cz=centers[i];return(x,y+cy,z+cz)
 kinds=[];ph=[];basefront=[];mshapes=[];fshapes=[]
 for i in range(5):
  p=PH[i];kind=Kind.SLIME if ((i-seam)%5)%2==0 else Kind.HONEY
  kinds.extend([kind,Kind.HONEY if kind==Kind.SLIME else Kind.SLIME,kind]);ph.extend([p,(p+2)%5,(p+4)%5])
  dm=[0,1,1,1,2][p];df=[0,0,1,2,3][p]
  basefront.extend([fronts[i],fronts[i]+2+dm-min(p,3),fronts[i]+5+df-min(p,3)])
  mshapes.append(rng.sample([(-1,0),(0,-1),(0,1)],3));fshapes.append(rng.sample([(-1,0),(0,-1),(0,1)],3))
 hh=[f-1-min(p,3) for f,p in zip(basefront,ph)]
 worlds=[];disps=[];mandatory=[];hardware=[]
 for t in range(5):
  fixed={};ss=[set() for _ in range(15)];owners={};dd=[]
  def put(q,b,owner=None):
   if q in fixed:return False
   fixed[q]=b
   if owner is not None:owners[q]=owner
   return True
  for i in range(5):
   for role in range(3):
    index=3*i+role;cyc,p=divmod(ph[index]+t,5);off=hh[index]+3*cyc;front=off+1+min(p,3);rear=off+max(0,p-2);dd.append(front-basefront[index])
    if role==0:
     for y,z in [(1,0),(2,0),(2,-1),(0,0)]:ss[index].add(tr(i,(front,y,z)))
     ss[index].add(tr(i,(front-1,0,0)))
     ss[3*((i-1)%5)].add(tr(i,(rear,1,-1)))
     if not put(tr(i,(front-1,2,0)),Block(Kind.REDSTONE_BLOCK),index):return reject('duplicate_hardware')
     shapes=[(1,0),(2,-1)];support=3*((i-1)%5)
    elif role==1:
     for y,z in [(-1,0),(-1,-1),(0,-1),(-1,1),(0,1),(1,1)]:ss[index].add(tr(i,(front,y,z)))
     ss[index].add(tr(i,(front+1,1,1)))
     for y,z in [(-1,1),(-1,-1)]:
      if not put(tr(i,(front-1,y,z)),Block(Kind.REDSTONE_BLOCK),index):return reject('duplicate_hardware')
     shapes=mshapes[i];support=3*i
    else:
     for y,z in [(0,0),(-1,0),(0,-1),(0,1)]:ss[index].add(tr(i,(front,y,z)))
     if not put(tr(i,(front-1,0,0)),Block(Kind.REDSTONE_BLOCK),index):return reject('duplicate_hardware')
     shapes=fshapes[i]+[(1,0)];support=3*i+1
    for j,(y,z) in enumerate(shapes):
     sticky=role==2 and j==3;jj=0 if sticky else j
     px=off+(p if jj>=p else max(jj,p-2));state=2 if p==jj+1 else 0
     pos=tr(i,(px,y,z));owner=support if sticky or p>j else index
     if not put(pos,Block.piston(1 if sticky else 0,sticky=sticky,state=state),owner):return reject('duplicate_hardware')
     if state and not put(shift(pos,-1 if sticky else 1),Block(Kind.PISTON_ARM)):return reject('duplicate_arm')
  occupied=set(fixed)
  for s in ss:
   if occupied&s:return reject('mandatory_collision')
   occupied|=s
  for i in range(15):
   for j in range(i):
    if kinds[i]==kinds[j] and any(add(p,d) in ss[j] for p in ss[i] for d in D):return reject('mandatory_adhesion')
  worlds.append(fixed);disps.append(dd);mandatory.append(ss);hardware.append(owners)
 ss=[set(s) for s in mandatory[0]]
 @functools.lru_cache(None)
 def legal(p,i):
  for t,fixed in enumerate(worlds):
   q=shift(p,disps[t][i])
   if q in fixed:return False
   if (ph[i]+t)%5<3:
    for d in D:
     nb=add(q,d);b=fixed.get(nb)
     if b and b.kind in (Kind.REDSTONE_BLOCK,Kind.PISTON):
      if b.kind==Kind.PISTON and b.state:continue
      if hardware[t][nb]!=i:return False
   for j,s in enumerate(ss):
    if j==i:continue
    r=shift(q,-disps[t][j])
    if r in s:return False
    if kinds[i]==kinds[j] and any(add(r,d) in s for d in D):return False
  return True
 for i in rng.sample([0,3,6,9,12],5):
  legal.cache_clear()
  for _ in range(4):
   conn={min(ss[i])};stack=list(conn)
   while stack:
    p=stack.pop()
    for d in D:
     q=add(p,d)
     if q in ss[i] and q not in conn:conn.add(q);stack.append(q)
   targets=ss[i]-conn
   if not targets:break
   if min(sum(abs(x-y) for x,y in zip(a,b)) for a in conn for b in targets)-1>cap-len(ss[i]):return reject('distance_cap')
   heap=[(0,rng.random(),p) for p in conn];heapq.heapify(heap);cost={p:0 for p in conn};prev={};end=None
   while heap:
    v,_,p=heapq.heappop(heap)
    if v!=cost[p]:continue
    if p in targets:end=p;break
    if v>cap-len(ss[i]):continue
    for d in rng.sample(D,6):
     q=add(p,d)
     if not(-6<=q[0]<=8 and -5<=q[1]<=12 and -5<=q[2]<=12):continue
     if q not in ss[i] and not legal(q,i):continue
     w=v+(q not in ss[i])
     if w<cost.get(q,1000):cost[q]=w;prev[q]=p;heapq.heappush(heap,(w,rng.random(),q))
   if end is None:return reject('route_unreachable')
   while end not in conn:ss[i].add(end);end=prev[end]
   if len(ss[i])>cap:return reject('route_cap')
  else:return reject('component_limit')
 f=Flyer(rng_state=5,push_limit=100);f._cells=worlds[0].copy()
 for i,s in enumerate(ss):
  for p in s:
   if p in f._cells:return reject('final_collision')
   f._cells[p]=Block(kinds[i])
 return f,[len(s) for s in ss],dict(centers=centers,fronts=fronts,seed=seed,rot=rot,seam=seam,mshapes=mshapes,fshapes=fshapes,segments=[sorted(s) for s in ss])
if __name__=='__main__':
 out=Path(__file__).parent/'helper_ring_v2';out.mkdir(exist_ok=True)
 configs=[[(0,0),(0,4),(3,5),(5,2),(3,-1)],[(0,0),(0,5),(4,6),(6,2),(3,-2)],[(0,0),(0,3),(3,4),(5,1),(2,-2)]]
 start=time.monotonic();meta=[];attempts=0
 for ci,seed in itertools.product(range(len(configs)),range(2000)):
  if time.monotonic()-start>500 or len(meta)>=500:break
  attempts+=1;a=make(configs[ci],[0,1,1,1,2],seed)
  if a:
   f,counts,m=a;name=f'c{ci}s{seed}';f.save(out/(name+'.flyer'));meta.append(m|{'name':name,'counts':counts});print(name,counts,flush=True)
 (out.parent/'helper_ring_v2_meta.json').write_text(json.dumps(meta,indent=2))
 p=subprocess.run([str(Path(os.environ['TEMP'])/'flyer_batch.exe'),'160',str(out)],capture_output=True,text=True)
 (out.parent/'helper_ring_v2_results.tsv').write_text(p.stdout);print('ATTEMPTS',attempts,'REJECT',REJECT,'ELAPSED',time.monotonic()-start);print(p.stdout)
