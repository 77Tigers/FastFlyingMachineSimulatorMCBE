"""Close two alternating pull interfaces; Rust is the validator."""
from pathlib import Path
import sys,os,itertools,heapq,random,subprocess,json,functools
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
D=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
def add(p,q):return tuple(a+b for a,b in zip(p,q))
def shift(p,x):return (p[0]+x,p[1],p[2])
RAIL={(2,0,0),(1,0,0),(0,0,0),(0,0,1),(0,1,0)}
DISP=((0,1,1,2),(0,0,1,1))
def interface(t,material,observer_axis=0):
 c,s=divmod(t,4);a=2*c+(s+1)//2;b=2*c+s//2
 rail={shift(p,a) for p in RAIL};h=(2+b,1,1)
 o=(2+a,-1,0) if observer_axis==0 else (2+a,0,-1)
 fixed={o:Block.observer(2 if observer_axis==0 else 4,powered=(s%2==1))}
 for p,st in [((((2,2,3,4)[s]+2*c),0,1),2 if s==0 else 0),((((2,3,3,3)[s]+2*c),1,0),2 if s==2 else 0)]:
  fixed[p]=Block.piston(1,sticky=True,state=st)
  if st:fixed[shift(p,-1)]=Block(Kind.PISTON_ARM)
 return rail,h,fixed

def transform(p,swap,sy,sz,off):
 x,y,z=p
 if swap:y,z=z,y
 return add((x,sy*y,sz*z),off)
def make(off,rot,oa,ob,seed,cap=24):
 swap,sy,sz=rot
 def tr(p):return transform(p,swap,sy,sz,off)
 worlds=[]
 for t in range(4):
  ra,hb,fa=interface(t,0,oa);rb,ha,fb=interface(t+1,1,ob)
  rb={tr(p) for p in rb};ha=tr(ha)
  nb={}
  for p,b in fb.items():
   if b.kind==Kind.OBSERVER:
    v=transform(D[b.direction],swap,sy,sz,(0,0,0));b=Block.observer(D.index(v),powered=b.powered)
   nb[tr(p)]=b
  if set(fa)&set(nb):return
  fixed=fa|nb;ss=[ra|{ha},rb|{hb}]
  if ss[0]&ss[1] or any(set(fixed)&s for s in ss):return
  worlds.append((fixed,ss))
 ss=[set(s) for s in worlds[0][1]];rng=random.Random(seed)
 for i in range(2):
  conn={next(iter(ss[i]))};stack=list(conn)
  while stack:
   p=stack.pop()
   for d in D:
    q=add(p,d)
    if q in ss[i] and q not in conn:conn.add(q);stack.append(q)
  targets=ss[i]-conn
  if targets and min(sum(abs(a-b) for a,b in zip(p,q)) for p in conn for q in targets)-1>cap-len(ss[i]):return
 observers=[{p for p,b in interface(t,0,oa)[2].items() if b.kind==Kind.OBSERVER} for t in range(4)]
 @functools.lru_cache(None)
 def legal(p,i):
  for t,(fixed,base) in enumerate(worlds):
   q=shift(p,DISP[i][t]);other=1-i
   if q in fixed or shift(q,-DISP[other][t]) in ss[other]:return False
   # Observers must retain their intended owner.
   for d in D:
    b=fixed.get(add(q,d))
    if b and b.kind==Kind.OBSERVER:
     # O from first interface belongs to A; O from second belongs to B.
     if (add(q,d) in observers[t])!=(i==0):return False
  return True
 for i in rng.sample([0,1],2):
  legal.cache_clear()
  while True:
   conn={next(iter(ss[i]))};stack=list(conn)
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
    if cost>cap-len(ss[i]):continue
    dirs=rng.sample(D,6)
    for d in dirs:
     q=add(p,d)
     if not(-5<=q[0]<=5 and -5<=q[1]<=5 and -5<=q[2]<=5):continue
     if q not in ss[i] and not legal(q,i):continue
     nc=cost+(q not in ss[i])
     if nc<dist.get(q,100):dist[q]=nc;prev[q]=p;heapq.heappush(pq,(nc,rng.random(),q))
   if end is None:return
   while end not in conn:ss[i].add(end);end=prev[end]
   if len(ss[i])>cap:return
 f=Flyer(rng_state=5,push_limit=100);f._cells=worlds[0][0].copy()
 for i,s in enumerate(ss):
  for p in s:f._cells[p]=Block(Kind.SLIME if i==0 else Kind.HONEY)
 return f,[len(s) for s in ss]
if __name__=='__main__':
 out=ROOT/'flyers/WIP/experiments/astra_pullonly_20260927/mwmw';out.mkdir(exist_ok=True)
 seen=set();n=0;meta=[]
 params=list(itertools.product(range(-3,4),range(-3,4),range(-3,4)));random.Random(5).shuffle(params)
 for dx,dy,dz in params:
  for rot in itertools.product((0,1),(-1,1),(-1,1)):
   for oa,ob in itertools.product(range(2),repeat=2):
    ans=make((dx,dy,dz),rot,oa,ob,0)
    if ans is None:continue
    f,counts=ans;key=tuple(sorted((p,b.encode()) for p,b in f._cells.items()))
    if key in seen:continue
    seen.add(key);path=out/f'c{n}.flyer';f.save(path)
    meta.append(dict(id=n,offset=(dx,dy,dz),rot=rot,oa=oa,ob=ob,seed=0,counts=counts));n+=1
  if n:print('offset',dx,dy,dz,'candidates',n,flush=True)
  if n>=500:break
 (out.parent/'mwmw_metadata.json').write_text(json.dumps(meta,indent=2))
 p=subprocess.run([str(ROOT/'flyers/WIP/experiments/bin/research_runner.exe'),'batch',str(out),'160'],capture_output=True,text=True)
 (out.parent/'mwmw_screen.txt').write_text(p.stdout)
 print('TESTED',n,flush=True)
