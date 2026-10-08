"""Three phased all-negative-X sticky carriers; temporal routing, Rust validation."""
from pathlib import Path
import sys,random,heapq,json,subprocess
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
OUT=Path(__file__).parent;D=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sh(p,x):return(p[0]+x,p[1],p[2])
DISP=((0,0,0),(0,0,1),(0,1,1));MOVES=(2,1,0)
def make(seed,span=3):
 rng=random.Random(seed); centers=[(0,0),(0,span),(span,0)]
 if seed%2:centers=[(0,0),(0,span),(0,2*span)]
 ps=[(x,*c) for x,c in zip((2,2,1),centers)];target=[1,2,0]
 support=[];obs=[];dirs=[];ss=[set() for _ in range(3)]
 for i,p in enumerate(ps):
  d=rng.choice(D[2:]);h=add(p,d);support.append(h);ss[i].add(h);obs.append(add(h,d));dirs.append(D.index(tuple(-v for v in d)))
  ss[target[i]].add((0,p[1],p[2]))
 fixeds=[];owners=[]
 for t in range(3):
  fixed={};own={}
  for i,p in enumerate(ps):
   q=sh(p,DISP[t][i]);state=2 if i==(1,0,2)[t] else 0
   fixed[q]=Block.piston(1,sticky=True,state=state);own[q]=i
   if state:fixed[sh(q,-1)]=Block(Kind.PISTON_ARM)
   q=sh(obs[i],DISP[t][i]);fixed[q]=Block.observer(dirs[i],powered=i==(0,2,1)[t]);own[q]=i
  if len(fixed)!=7:return
  fixeds.append(fixed);owners.append(own)
 def legal(p,i):
  for t in range(3):
   q=sh(p,DISP[t][i]);fix=fixeds[t]
   if q in fix:return False
   for j in range(3):
    if i==j:continue
    oth={sh(v,DISP[t][j]) for v in ss[j]}
    if q in oth:return False
    if i%2==j%2 and any(add(q,d) in oth for d in D):return False
   if MOVES[t]==i:
    # carrier moves +X during this slot; non-own movable hardware cannot adhere
    for d in D:
     n=add(q,d);b=fix.get(n)
     if b and b.kind!=Kind.PISTON_ARM and not(b.kind==Kind.PISTON and b.state) and owners[t].get(n)!=i:return False
    dest=sh(q,1)
    if dest in fix and fix[dest].kind!=Kind.PISTON_ARM and owners[t].get(dest)!=i:return False
  return True
 for i in range(3):
  if any(not legal(p,i) for p in ss[i]):return
 for i in rng.sample(range(3),3):
  while True:
   conn={min(ss[i])};stack=list(conn)
   while stack:
    p=stack.pop()
    for d in D:
     q=add(p,d)
     if q in ss[i] and q not in conn:conn.add(q);stack.append(q)
   targets=ss[i]-conn
   if not targets:break
   pq=[(0,rng.random(),p) for p in conn];heapq.heapify(pq);dist={p:0 for p in conn};prev={};end=None
   while pq:
    cost,_,p=heapq.heappop(pq)
    if cost!=dist[p]:continue
    if p in targets:end=p;break
    if cost>24:continue
    for d in rng.sample(D,6):
     q=add(p,d)
     if not(-2<=q[0]<=4 and -4<=q[1]<=span+4 and -4<=q[2]<=2*span+4):continue
     if q not in ss[i] and not legal(q,i):continue
     nc=cost+(q not in ss[i])
     if nc<dist.get(q,999):dist[q]=nc;prev[q]=p;heapq.heappush(pq,(nc,rng.random(),q))
   if end is None:return
   while end not in conn:ss[i].add(end);end=prev[end]
 f=Flyer(push_limit=100,rng_state=5);f._cells=fixeds[0].copy()
 for i,s in enumerate(ss):
  for p in s:f.set(p,Block(Kind.SLIME if i%2==0 else Kind.HONEY))
 return f
if __name__=='__main__':
 dest=OUT/'ring3';dest.mkdir(exist_ok=True);n=0
 for seed in range(600):
  f=make(seed,2+seed%3)
  if f:f.save(dest/f'c{seed}.flyer');n+=1
  if seed%50==0:print(seed,n,flush=True)
 print('total',n,flush=True)
 p=subprocess.run([str(ROOT/'target/release/fastflyer-research.exe'),'batch',str(dest),'180'],capture_output=True,text=True)
 (OUT/'ring3_screen.txt').write_text(p.stdout);print(p.stdout[:2000])

