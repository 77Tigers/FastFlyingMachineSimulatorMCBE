import sys,os,heapq,random
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from fastflyer import Flyer,Block,Kind
DIR=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def make(n,centers,seed,limit=100,front_mask=7,rear_mask=7):
 rng=random.Random(seed);L=n+2;k=len(centers);ph=[2*i%L for i in range(k)]
 spans=[3]*k;spans[-1]=sum(2+min(p,n)-max(0,p-2) for p in ph)-3*(k-1)
 F=[0]
 for i in range(k-1):F.append(F[-1]+2+min(ph[i+1],n)-max(0,ph[i+1]-2)-spans[i])
 h=[F[i]-1-min(ph[i],n) for i in range(k)]
 arms=[(1,0),(0,1),(-1,0),(0,-1)]
 shapes=[]
 for i in range(k):
  aa=arms.copy();rng.shuffle(aa);shapes.append(aa[:n])
 kinds=[Kind.SLIME if i%2==0 else Kind.HONEY for i in range(k)]
 sticky=[set() for _ in range(k)];f=Flyer(rng_state=5,push_limit=limit)
 world=[];disp=[]
 for t in range(L+1):
  fixed={};ss=[set() for _ in range(k)];dd=[]
  for i,((cy,cz),p0,hh,aa) in enumerate(zip(centers,ph,h,shapes)):
   cyc,p=divmod(p0+t,L);off=hh+n*cyc;front=off+1+min(p,n);rear=off-1+max(0,p-2);dd.append(front-F[i])
   for bit,(dy,dz) in enumerate([(0,0)]+aa):
    if front_mask & (1<<bit):ss[i].add((front,cy+dy,cz+dz))
    if rear_mask & (1<<bit):ss[(i-1)%k].add((rear,cy+dy,cz+dz))
   fixed[(front-1,cy,cz)]=Block(Kind.REDSTONE_BLOCK)
   for j,(dy,dz) in enumerate(aa):
    px=off+(p if j>=p else max(j,p-2));state=2 if p==j+1 else 0
    fixed[(px,cy+dy,cz+dz)]=Block.piston(0,state=state)
    if state:fixed[(px+1,cy+dy,cz+dz)]=Block(Kind.PISTON_ARM)
  world.append((fixed,ss));disp.append(dd)
  if t==0:
   f._cells.update(fixed);sticky=ss
 def legal(pt,i):
  for t in range(L):
   q=(pt[0]+disp[t][i],pt[1],pt[2]);fixed,_=world[t]
   if q in fixed:return False
   for d in DIR:
    nb=fixed.get(add(q,d))
    if nb is not None and nb.kind in (Kind.PISTON,Kind.REDSTONE_BLOCK):return False
   for j,cells in enumerate(sticky):
    if j==i:continue
    r=(q[0]-disp[t][j],q[1],q[2])
    if r in cells:return False
    if kinds[i]==kinds[j] and any(add(r,d) in cells for d in DIR):return False
  return True
 order=list(range(k));rng.shuffle(order)
 for i in order:
  # component closure among own mandatory front and rear
  start=next(p for p in sticky[i] if p[0]==F[i]);connected={start};stack=[start]
  while stack:
   q=stack.pop()
   for d in DIR:
    r=add(q,d)
    if r in sticky[i] and r not in connected:connected.add(r);stack.append(r)
  target=sticky[i]-connected
  pq=[];prev={};cost={}
  for p in connected:cost[p]=0;heapq.heappush(pq,(0,rng.random(),p))
  end=None
  while pq:
   c,_,p=heapq.heappop(pq)
   if c!=cost[p]:continue
   if p in target:end=p;break
   if c>20:continue
   dirs=DIR.copy();rng.shuffle(dirs)
   for d in dirs:
    q=add(p,d)
    if not(-7<=q[0]<=6 and -5<=q[1]<=10 and -5<=q[2]<=10):continue
    if q not in sticky[i] and not legal(q,i):continue
    nc=c+(0 if q in sticky[i] else 1)
    if nc<cost.get(q,1000):cost[q]=nc;prev[q]=p;heapq.heappush(pq,(nc,rng.random(),q))
  if end is None:return None
  while end not in connected:sticky[i].add(end);end=prev[end]
 for i,ss in enumerate(sticky):
  for p in ss:
   if p in f._cells:return None
   f._cells[p]=Block(kinds[i])
 return f,[len(s) for s in sticky],(sticky,ph)
if __name__=='__main__':
 n=int(sys.argv[1]);count=int(sys.argv[2]);out=Path(os.environ['TEMP'])/f'astra_ring{n}_safe';out.mkdir(exist_ok=True)
 centers=[(0,0),(0,4),(2,2)] if n==4 else [(0,0),(0,4),(3,5),(5,2),(3,-1)]
 for seed in range(count):
  ans=make(n,centers,seed)
  if ans:
   f,l,shapes=ans;f.save(out/f's{seed}.flyer');print(seed,l)
