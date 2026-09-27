"""Replace one N3 last push with a middle-carrier sticky timed by front redstone."""
from pathlib import Path
import sys,random,heapq,functools,itertools,subprocess,os,json
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
from flyers.WIP.astra_ringgen_safe import make
D=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
CENTERS=[(0,0),(0,4),(3,5),(5,2),(3,-1)]
PH=[0,2,4,1,3];F=[0,1,1,1,2];H=[-1,-2,-3,-1,-2]
def add(p,q):return tuple(a+b for a,b in zip(p,q))
def shift(p,x):return(p[0]+x,p[1],p[2])
def delta(i,t):
 c,p=divmod(PH[i]+t,5);return 3*c+min(p,3)-min(PH[i],3)
@functools.lru_cache(None)
def reference():return make(3,CENTERS,3,100)
def generate(sp,removed,seed):
 base,_,(segs,_)=reference()
 segs=[set(s) for s in segs];rng=random.Random(3);shapes=[]
 for _ in range(5):
  aa=[(1,0),(0,1),(-1,0),(0,-1)];rng.shuffle(aa);shapes.append(aa[:3])
 worlds=[]
 for t in range(5):
  fixed={}
  for i,((cy,cz),hh,aa) in enumerate(zip(CENTERS,H,shapes)):
   cyc,p=divmod(PH[i]+t,5);off=hh+3*cyc;front=off+1+min(p,3)
   fixed[(front-1,cy,cz)]=Block(Kind.REDSTONE_BLOCK)
   for j,(dy,dz) in enumerate(aa):
    if i==0 and j==removed:continue
    px=off+(p if j>=p else max(j,p-2));state=2 if p==j+1 else 0
    # With two normal pistons their firing order is unconstrained; subsequent Rust is authoritative.
    if i==0 and j>removed:
     jj=j-1;px=off+(p if jj>=p else max(jj,p-2));state=2 if p==jj+1 else 0
    fixed[(px,cy+dy,cz+dz)]=Block.piston(0,state=state)
    if state:fixed[(px+1,cy+dy,cz+dz)]=Block(Kind.PISTON_ARM)
  q=shift(sp,delta(1,t));state=2 if t==2 else 0
  if q in fixed:return
  fixed[q]=Block.piston(1,sticky=True,state=state)
  if state:fixed[shift(q,-1)]=Block(Kind.PISTON_ARM)
  worlds.append(fixed)
 if sp in segs[1]:segs[1].remove(sp)
 elif any(sp in s for s in segs):return
 contact=shift(sp,-3)
 if contact in worlds[0] or any(contact in s for s in segs[1:]):return
 segs[0].add(contact)
 rng=random.Random(seed)
 @functools.lru_cache(None)
 def legal(p,i):
  for t,fixed in enumerate(worlds):
   q=shift(p,delta(i,t))
   if q in fixed:return False
   for j,s in enumerate(segs):
    if j==i:continue
    r=shift(q,-delta(j,t))
    if r in s:return False
    if i%2==j%2 and any(add(r,d) in s for d in D):return False
   for d in D:
    nb=add(q,d);b=fixed.get(nb)
    if b is None:continue
    if b.kind==Kind.PISTON:
     # New target slime must not grab active hardware; support may carry its sticky.
     if not(i==1 and nb==shift(sp,delta(1,t))):return False
    if b.kind==Kind.REDSTONE_BLOCK:return False
  return True
 # Attach S from a side or behind, never through its arm sweep.
 neighbors=[add(sp,d) for d in D if d!=(-1,0,0)]
 options=[p for p in neighbors if p in segs[1] or legal(p,1)]
 if not options:return
 anchor=rng.choice(options);segs[1].add(anchor)
 for i in rng.sample([0,1],2):
  legal.cache_clear()
  for _ in range(6):
   conn={next(iter(segs[i]))};stack=list(conn)
   while stack:
    p=stack.pop()
    for d in D:
     q=add(p,d)
     if q in segs[i] and q not in conn:conn.add(q);stack.append(q)
   targets=segs[i]-conn
   if not targets:break
   heap=[(0,rng.random(),p) for p in conn];heapq.heapify(heap);cost={p:0 for p in conn};prev={};end=None
   while heap:
    v,_,p=heapq.heappop(heap)
    if v!=cost[p]:continue
    if p in targets:end=p;break
    if v>1800:continue
    for d in rng.sample(D,6):
     q=add(p,d)
     if not(-8<=q[0]<=4 and -3<=q[1]<=8 and -3<=q[2]<=8):continue
     if q not in segs[i] and not legal(q,i):continue
     w=v+(0 if q in segs[i] else 100+rng.randrange(15))
     # Weighted routes are bounded in cells below.
     if w<cost.get(q,100000):cost[q]=w;prev[q]=p;heapq.heappush(heap,(w,rng.random(),q))
   if end is None:return
   while end not in conn:segs[i].add(end);end=prev[end]
  else:return
 f=Flyer(rng_state=5,push_limit=100);f._cells=worlds[0].copy()
 for i,s in enumerate(segs):
  for p in s:
   if p in f._cells:return
   f._cells[p]=Block(Kind.SLIME if i%2==0 else Kind.HONEY)
 return f,[len(s) for s in segs]
if __name__=='__main__':
 out=Path(__file__).parent/'one_hybrid';out.mkdir(exist_ok=True)
 meta=[]
 for sp,rem,seed in itertools.product([(-2,3,5),(-1,4,5)],range(3),range(20)):
  ans=generate(sp,rem,seed)
  if ans:
   f,counts=ans;name=f's{sp[0]}_{sp[1]}_{sp[2]}r{rem}g{seed}';f.save(out/(name+'.flyer'));meta.append((name,counts));print(name,counts,flush=True)
 (out.parent/'retrofit_meta.json').write_text(json.dumps(meta,indent=2))
 run=subprocess.run([str(Path(os.environ['TEMP'])/'flyer_batch.exe'),'160',str(out)],capture_output=True,text=True)
 (out.parent/'retrofit_results.tsv').write_text(run.stdout);print(run.stdout)
