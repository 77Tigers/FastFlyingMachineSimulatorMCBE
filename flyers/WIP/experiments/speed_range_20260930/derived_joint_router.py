import functools
import sys,os,heapq,random
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from fastflyer import Flyer,Block,Kind
DIR=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def make(n,centers,seed,limit=24,spans=None):
 rng=random.Random(seed);L=n+2;k=len(centers);ph=[2*i%L for i in range(k)]
 if spans is None:spans=([3,3,4]*(k//3)) if n==4 else [3,3,3,3,4]*(k//5)
 if len(spans)!=k or sum(spans)!=sum(2+min(p,n)-max(0,p-2) for p in ph):raise ValueError('closure')
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
   for dy,dz in [(0,0)]+aa:
    ss[i].add((front,cy+dy,cz+dz));ss[(i-1)%k].add((rear,cy+dy,cz+dz))
   fixed[(front-1,cy,cz)]=Block(Kind.REDSTONE_BLOCK)
   for j,(dy,dz) in enumerate(aa):
    px=off+(p if j>=p else max(j,p-2));state=2 if p==j+1 else 0
    fixed[(px,cy+dy,cz+dz)]=Block.piston(0,state=state)
    if state:fixed[(px+1,cy+dy,cz+dz)]=Block(Kind.PISTON_ARM)
  world.append((fixed,ss));disp.append(dd)
  if t==0:
   f._cells.update(fixed);sticky=ss
 @functools.lru_cache(None)
 def legal(pt,i):
  for t in range(L):
   q=(pt[0]+disp[t][i],pt[1],pt[2]);fixed,_=world[t]
   if q in fixed:return False
   for j,((cy,cz),p0,hh,aa) in enumerate(zip(centers,ph,h,shapes)):
    cyc,p=divmod(p0+t,L);off=hh+n*cyc
    rp=(off+min(p,n),cy,cz)
    if j!=i and sum(abs(q[a]-rp[a]) for a in range(3))==1:return False
    possibilities=[]
    if p<n:possibilities.append((off+p,j,False))
    if p>=2:possibilities.append((off+p-2,(j-1)%k,False))
    if 1<=p<=n:
     possibilities.append((off+p-1,-1,True));possibilities.append((off+p,-1,True))
    for px,owner,imm in possibilities:
     for dy,dz in aa:
      pp=(px,cy+dy,cz+dz);dist=sum(abs(q[a]-pp[a]) for a in range(3))
      if dist==0:return False
      if dist==1 and not imm and owner!=i and (ph[i]+t)%L<n:return False
   for j,cells in enumerate(sticky):
    if j==i:continue
    r=(q[0]-disp[t][j],q[1],q[2])
    if r in cells:return False
    if kinds[i]==kinds[j] and any(add(r,d) in cells for d in DIR):return False
  return True
 order=list(range(k));rng.shuffle(order)
 for i in order:
  legal.cache_clear()
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
    if not(min(F)-8<=q[0]<=max(F)+5 and min(c[0] for c in centers)-3<=q[1]<=max(c[0] for c in centers)+3 and min(c[1] for c in centers)-3<=q[2]<=max(c[1] for c in centers)+3):continue
    if q not in sticky[i] and not legal(q,i):continue
    nc=c+(0 if q in sticky[i] else 1)
    if nc<cost.get(q,1000):cost[q]=nc;prev[q]=p;heapq.heappush(pq,(nc,rng.random(),q))
  if end is None:return None
  while end not in connected:sticky[i].add(end);end=prev[end]
 if max(map(len,sticky))+n+1>24:return None
 for i,ss in enumerate(sticky):
  for p in ss:
   if p in f._cells:return None
   f._cells[p]=Block(kinds[i])
 return f,[len(s) for s in sticky],(sticky,ph)
