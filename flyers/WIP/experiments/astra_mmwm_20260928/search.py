"""Three-phase mmw temporal contact synthesis; unmodified Rust validates results."""
from pathlib import Path
import sys,random,itertools,heapq,json,subprocess,collections,functools
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
OUT=Path(__file__).resolve().parent
D=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
S=((1,1,0,1,1,0),(0,1,1,0,1,1),(1,0,1,1,0,1))
DISP=[[sum(s[:t]) for t in range(7)] for s in S]
K=(Kind.SLIME,Kind.HONEY,Kind.SLIME)
def add(p,q):return tuple(a+b for a,b in zip(p,q))
def shift(p,x):return (p[0]+x,p[1],p[2])
def conn(s):
 if not s:return set()
 reached={min(s)};stack=list(reached)
 while stack:
  p=stack.pop()
  for d in D:
   q=add(p,d)
   if q in s and q not in reached:reached.add(q);stack.append(q)
 return reached

def build(seed,spacing=5,cap=140):
 rng=random.Random(seed);ss=[set() for _ in range(3)];ps=[];reds=[]
 # Each drive has an owned source: redstone for first move, observer for second.
 phases=list(range(6));rng.shuffle(phases)
 for j,f in enumerate(phases):
  cy=(j%3)*spacing;cz=(j//3)*spacing
  base=rng.choice((-1,0,1));src=f%3
  dp=[sum((t-f)%6 not in (0,1) for t in range(s)) for s in range(6)]
  targets=[i for i in range(3) if S[i][f]]
  rng.shuffle(targets)
  for target,dy in zip(targets,(-1,1)):
   p=(base,cy+dy,cz);ps.append((p,dp,f,target))
   ss[target].add((base+dp[f]+1-DISP[target][f],cy+dy,cz))
   rx=base+dp[f]-DISP[target][f]
   observer=bool(S[target][(f-1)%6])
   reds.append(((rx,cy+dy,cz+1),target,observer))
 fixed=[]
 for t in range(6):
  w={}
  for p,owner,observer in reds:
   q=shift(p,DISP[owner][t])
   if q in w:return None,'fixed_overlap'
   w[q]=Block.observer(5,powered=bool(S[owner][(t-1)%6])) if observer else Block(Kind.REDSTONE_BLOCK)
  for p,dp,f,target in ps:
   q=shift(p,dp[t]);state=2 if (t-f)%6==1 else 0
   if q in w:return None,'fixed_overlap'
   w[q]=Block.piston(0,state=state)
   if state:
    if shift(q,1) in w:return None,'arm_overlap'
    w[shift(q,1)]=Block(Kind.PISTON_ARM)
  fixed.append(w)
 @functools.lru_cache(None)
 def legal(p,i,strict=False):
  for t in range(6):
   q=shift(p,DISP[i][t])
   if q in fixed[t]:return False
   for j,cells in enumerate(ss):
    if j==i:continue
    for delta in range(-S[j][t],S[i][t]+1):
     rel=shift(q,-DISP[j][t]+delta)
     if rel in cells or (K[i]==K[j] and any(add(rel,d) in cells for d in D)):return False
   for rp,owner,observer in reds:
    r=shift(rp,DISP[owner][t])
    if i!=owner:
     for delta in range(-S[owner][t],S[i][t]+1):
      if sum(abs(a-b) for a,b in zip(shift(q,delta),r))<=1:return False
   for pp,dp,f,target in ps:
    r=shift(pp,dp[t]);near=sum(abs(a-b) for a,b in zip(q,r))==1
    if strict and near:return False
    if t==f and near and S[i][t] and i!=target:return False
    if (t-f)%6 not in (0,1):
     if near and S[i][t]:
      for j,cells in enumerate(ss):
       if j!=i and shift(r,1-DISP[j][t]) in cells:return False
     if q==shift(r,1):
      if not S[i][t]:return False
      for j,cells in enumerate(ss):
       if j!=i and S[j][t] and any(shift(add(r,d),-DISP[j][t]) in cells for d in D):return False
  return True
 if any(not legal(p,i) for i,s in enumerate(ss) for p in s):return None,'mandatory_conflict'
 # Cover all four recovery actions with legal side contacts, sharing cells when possible.
 for pp,dp,f,target in rng.sample(ps,len(ps)):
  recovery={t for t in range(6) if (t-f)%6 not in (0,1)}
  while recovery:
   opts=[]
   for t in recovery:
    for i in range(3):
     if not S[i][t]:continue
     for d in D[2:]:
      p=shift(add(pp,d),dp[t]-DISP[i][t])
      if not legal(p,i):continue
      covered={u for u in recovery if S[i][u] and sum(abs(a-b) for a,b in zip(shift(p,DISP[i][u]),shift(pp,dp[u])))==1}
      distance=min((sum(abs(a-b) for a,b in zip(p,q)) for q in ss[i]),default=2)
      opts.append((-len(covered),p not in ss[i],distance,rng.random(),p,i,covered))
   if not opts:return None,'no_pickup'
   *_,p,i,covered=min(opts);ss[i].add(p);recovery-=covered;legal.cache_clear()
 # Ensure every source has a stable owner.
 for rp,i,observer in reds:
  opts=[(min((sum(abs(a-b) for a,b in zip(add(rp,d),q)) for q in ss[i]),default=0),rng.random(),add(rp,d)) for d in D if legal(add(rp,d),i)]
  if not opts:return None,'source_attach'
  ss[i].add(min(opts)[-1]);legal.cache_clear()
 # Route around all piston lanes; all-time material separation is mandatory.
 for i in rng.sample(range(3),3):
  legal.cache_clear()
  while len(conn(ss[i]))<len(ss[i]):
   reached=conn(ss[i]);targets=ss[i]-reached
   pq=[(0,rng.random(),p) for p in reached];heapq.heapify(pq);dist={p:0 for p in reached};prev={};end=None
   while pq:
    cost,_,p=heapq.heappop(pq)
    if cost!=dist[p]:continue
    if p in targets:end=p;break
    if cost>cap-len(ss[i]):continue
    for d in rng.sample(D,6):
     q=add(p,d)
     if not(-5<=q[0]<=7 and -4<=q[1]<=2*spacing+4 and -4<=q[2]<=spacing+4):continue
     if q not in ss[i] and not legal(q,i):continue
     nc=cost+(q not in ss[i])
     if nc<dist.get(q,10000):dist[q]=nc;prev[q]=p;heapq.heappush(pq,(nc,rng.random(),q))
   if end is None:
    (OUT/'last_route_failure.json').write_text(json.dumps(dict(seed=seed,carrier=i,reached=sorted(reached),targets=sorted(targets),segments=[sorted(s) for s in ss],pistons=ps,sources=reds),indent=2))
    return None,'route'
   while end not in reached:ss[i].add(end);end=prev[end]
   if len(ss[i])>cap:return None,'cap'
 flyer=Flyer(rng_state=5,push_limit=512);flyer._cells=fixed[0].copy()
 for i,s in enumerate(ss):
  for p in s:
   if p in flyer._cells:return None,'final_overlap'
   flyer._cells[p]=Block(K[i])
 return (flyer,dict(seed=seed,spacing=spacing,counts=list(map(len,ss)),phases=phases,segments=[sorted(s) for s in ss],pistons=ps,sources=reds)),None

if __name__=='__main__':
 spacing=int(sys.argv[2]) if len(sys.argv)>2 else 5
 out=OUT/f'candidates_v3_gap{spacing}';out.mkdir(parents=True,exist_ok=True);stats=collections.Counter();meta=[]
 for seed in range(int(sys.argv[1]) if len(sys.argv)>1 else 100):
  ans,reason=build(seed,spacing=spacing)
  if ans:
   f,m=ans;path=out/f's{seed}.flyer';f.save(path);meta.append(m);stats['routed']+=1
  else:stats[reason]+=1
  print(seed,dict(stats),flush=True)
 (OUT/f'manifest_v3_gap{spacing}.json').write_text(json.dumps(dict(stats=stats,candidates=meta),indent=2))
