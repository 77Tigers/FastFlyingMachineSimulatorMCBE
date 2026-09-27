"""Five-carrier N3 ring: two +X pushers and a -X sticky per interface.

The sticky at interface j pulls carrier j-2, sharing j's redstone timing.
All generated candidates require independent Rust validation.
"""
from pathlib import Path
import sys,random,heapq,functools,itertools,subprocess,os,json,time
from collections import Counter
REJECT=Counter()
def reject(reason):REJECT[reason]+=1
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
D=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
ARMS=[(1,0),(0,1),(-1,0),(0,-1)]
PH=[0,2,4,1,3]
def add(p,q):return tuple(a+b for a,b in zip(p,q))
def shift(p,x):return(p[0]+x,p[1],p[2])
def make(centers,fronts,seed,cap=18,n=3):
 rng=random.Random(seed);k=len(centers);length=n+2;ph=[2*i%length for i in range(k)]
 hh=[fronts[i]-1-min(ph[i],n) for i in range(k)]
 shapes=[];corners=[]
 for i in range(k):
  if n==3:
   a=rng.randrange(4);b=(a+rng.choice([-1,1]))%4
   s=rng.choice([j for j in range(4) if j not in (a,b)])
   shapes.append([ARMS[a],ARMS[b],ARMS[s]])
  else:shapes.append(rng.sample(ARMS,4))
  corners.append(rng.choice([[(1,1),(-1,-1)],[(1,-1),(-1,1)]]))
 seam=rng.randrange(k);kinds=[Kind.SLIME if ((i-seam)%k)%2==0 else Kind.HONEY for i in range(k)]
 worlds=[];disps=[];mandatory=[];hardware_owners=[]
 for t in range(length):
  fixed={};ss=[set() for _ in range(k)];dd=[];stickypos=[];owners={}
  def put(q,b):
   if q in fixed:return False
   fixed[q]=b;return True
  for i,((cy,cz),h,aa) in enumerate(zip(centers,hh,shapes)):
   cyc,p=divmod(ph[i]+t,length);off=h+n*cyc;front=off+1+min(p,n);rear=off+max(0,p-2);dd.append(front-fronts[i])
   for dy,dz in [(0,0)]+aa[:n-1]:ss[i].add((front,cy+dy,cz+dz))
   for dy,dz in corners[i]:ss[(i-1)%k].add((rear,cy+dy,cz+dz))
   if not put((front-1,cy,cz),Block(Kind.REDSTONE_BLOCK)):return
   owners[(front-1,cy,cz)]=i
   for j,(dy,dz) in enumerate(aa):
    jj=j if j<n-1 else 0
    px=off+(p if jj>=p else max(jj,p-2));state=2 if p==jj+1 else 0
    direction=0 if j<n-1 else 1
    pos=(px,cy+dy,cz+dz)
    if not put(pos,Block.piston(direction,sticky=(j==n-1),state=state)):return
    owners[pos]=(i-1)%k if j==n-1 or p>j else i
    if j==n-1:stickypos.append(pos)
    if state and not put(shift(pos,1 if j<n-1 else -1),Block(Kind.PISTON_ARM)):return
  for i in range(k):
   # Derive initial contact from its pulling sticky and shift it with the target.
   if t==0:
    p=ph[i];gap=3+min(p,n-2)+max(0,p-n)-min(p,n)
    ss[i].add(shift(stickypos[(i+2)%k],-gap))
   else:
    contact=contacts[i];ss[i].add(shift(contact,dd[i]))
  if t==0:contacts=[shift(stickypos[(i+2)%k],-(3+min(ph[i],n-2)+max(0,ph[i]-n)-min(ph[i],n))) for i in range(k)]
  allcells=set()
  for s in ss:
   if s&set(fixed):return reject('mandatory_hardware')
   if s&allcells:return reject('mandatory_overlap')
   allcells|=s
  for i in range(k):
   for j in range(i):
    if kinds[i]==kinds[j] and any(add(p,d) in ss[j] for p in ss[i] for d in D):return reject('mandatory_samekind_adhesion')
  worlds.append(fixed);disps.append(dd);mandatory.append(ss);hardware_owners.append(owners)
 ss=[set(s) for s in mandatory[0]]
 @functools.lru_cache(None)
 def legal(p,i):
  for t,fixed in enumerate(worlds):
   q=shift(p,disps[t][i])
   if q in fixed:return False
   if (ph[i]+t)%length<n:
    for d in D:
     nb=add(q,d);b=fixed.get(nb)
     if b is not None and b.kind in (Kind.PISTON,Kind.REDSTONE_BLOCK):
      if b.kind==Kind.PISTON and b.state!=0:continue
      if hardware_owners[t][nb]!=i:return False
   for j,s in enumerate(ss):
    if j==i:continue
    r=shift(q,-disps[t][j])
    if r in s:return False
    if kinds[i]==kinds[j] and any(add(r,d) in s for d in D):return False
  return True
 for i in rng.sample(range(k),k):
  legal.cache_clear()
  for _ in range(8):
   conn={min(ss[i])};stack=list(conn)
   while stack:
    p=stack.pop()
    for d in D:
     q=add(p,d)
     if q in ss[i] and q not in conn:conn.add(q);stack.append(q)
   targets=ss[i]-conn
   if not targets:break
   heap=[(0,rng.random(),p) for p in conn];heapq.heapify(heap);cost={p:0 for p in conn};prev={};end=None
   while heap:
    v,_,p=heapq.heappop(heap)
    if v!=cost[p]:continue
    if p in targets:end=p;break
    if v>cap-len(ss[i]):continue
    for d in rng.sample(D,6):
     q=add(p,d)
     if not(-9<=q[0]<=7 and -5<=q[1]<=10 and -5<=q[2]<=10):continue
     if q not in ss[i] and not legal(q,i):continue
     w=v+(q not in ss[i])
     if w<cost.get(q,1000):cost[q]=w;prev[q]=p;heapq.heappush(heap,(w,rng.random(),q))
   if end is None:return reject('route_unreachable')
   while end not in conn:ss[i].add(end);end=prev[end]
   if len(ss[i])>cap:return reject('route_cap')
  else:return
 f=Flyer(rng_state=5,push_limit=100);f._cells=worlds[0].copy()
 for i,s in enumerate(ss):
  for p in s:
   if p in f._cells:return
   f._cells[p]=Block(kinds[i])
 return f,[len(s) for s in ss],dict(centers=centers,fronts=fronts,seed=seed,shapes=shapes,corners=corners,seam=seam,segments=[sorted(s) for s in ss])
if __name__=='__main__':
 out=Path(__file__).parent/'hybrid_ring';out.mkdir(exist_ok=True)
 configurations=[[(0,0),(0,4),(3,5),(5,2),(3,-1)],[(0,0),(0,3),(2,4),(4,2),(2,-1)],[(0,0),(0,2),(2,3),(3,1),(2,-1)],[(0,0),(0,3),(3,3),(3,0),(1,-2)]]
 frontsets=[[0,1,1,1,2],[0,0,0,0,0],[0,1,0,1,0],[0,-1,0,-1,0]]
 start=time.monotonic();meta=[];n=0
 for ci,fi,seed in itertools.product(range(len(configurations)),range(len(frontsets)),range(100)):
  if time.monotonic()-start>500 or n>=500:break
  ans=make(configurations[ci],frontsets[fi],seed)
  if ans:
   f,counts,m=ans;name=f'c{ci}f{fi}s{seed}';f.save(out/(name+'.flyer'));m.update(name=name,counts=counts);meta.append(m);n+=1
   print(name,counts,'elapsed',round(time.monotonic()-start,1),flush=True)
 (out.parent/'hybrid_ring_meta.json').write_text(json.dumps(meta,indent=2))
 p=subprocess.run([str(Path(os.environ['TEMP'])/'flyer_batch.exe'),'160',str(out)],capture_output=True,text=True)
 (out.parent/'hybrid_ring_results.tsv').write_text(p.stdout)
 print('TESTED',n,'ELAPSED',time.monotonic()-start,'REJECT',REJECT,flush=True);print(p.stdout)
