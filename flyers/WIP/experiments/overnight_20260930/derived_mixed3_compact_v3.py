"""Five-body saturated pull lifecycle: three moves per five two-tick slots.

Each of15 sticky pistons extends in f-1, pulls in f, and must be carried
in the other three slots. Separate power/helper bodies discharge those
transport obligations; the old single-support burst is not reused.
"""
from pathlib import Path
import sys,random,heapq,functools,collections,json,subprocess,csv
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
HERE=Path(__file__).resolve().parent
RUNNER=ROOT/'target/release/fastflyer-research.exe'
D=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
S=[[(t+p)%5<3 for t in range(5)] for p in range(5)]
DISP=[[sum(s[:t]) for t in range(6)] for s in S]
K=[Kind.SLIME,Kind.HONEY,Kind.SLIME,Kind.HONEY,Kind.SLIME]
def add(p,q):return tuple(a+b for a,b in zip(p,q))
def shift(p,x):return(p[0]+x,p[1],p[2])
def conn(s):
 if not s:return set()
 reached={min(s)};stack=list(reached)
 while stack:
  p=stack.pop()
  for d in D:
   q=add(p,d)
   if q in s and q not in reached:reached.add(q);stack.append(q)
 return reached

def build(seed,spacing=4,cap=220):
 rng=random.Random(seed);ss=[set() for _ in S];ps=[];sources=[];fronts=[rng.choice((-1,0,1)) for _ in S]
 for target in range(5):
  for j,f in enumerate(t for t in range(5) if S[target][t]):
   # Read-only identity contract: all three recovery slots move this member.
   sticky=(f+target)%5==2
   dp=[sum((t-f)%5 not in ((0,4) if sticky else (0,1)) for t in range(u)) for u in range(5)]
   base=fronts[target]+DISP[target][f]-dp[f]-(-2 if sticky else 1);p=(base,CENTERS[target][0]+PORTS[j][0],CENTERS[target][1]+PORTS[j][1])
   ps.append((p,dp,f,target,sticky));ss[target].add((base+dp[f]+(-2 if sticky else 1)-DISP[target][f],p[1],p[2]))
   # Observer pulses may come from a distinct helper body. Redstone is only
   # allowed when its body waits before extension and moves during extension.
   choices=[(i,True) for i in range(5) if S[i][((f-2) if sticky else (f-1))%5]]
   choices += [(i,False) for i in range(5) if not S[i][((f-2) if sticky else (f-1))%5] and S[i][((f-1) if sticky else f)%5]]
   ext=(f-1)%5 if sticky else f
   viable=[]
   for owner,observer in choices:
    rx=base+dp[ext]-DISP[owner][ext]
    source0=base+dp[f]+(-2 if sticky else 1)-DISP[target][f]
    if any((rx+DISP[owner][t]==base+dp[t]) and (not observer or S[owner][(t-1)%5]) and t!=ext for t in range(5)):continue
    if owner!=target and any(rx+DISP[owner][t]==source0+DISP[target][t]+delta for t in range(5) for delta in range(-int(S[owner][t]),int(S[target][t])+1)):continue
    viable.append((owner,observer,rx))
   if not viable:return None,'power_contract'
   owner,observer,rx=rng.choice(viable)
   # Observer faces -Z into a side support cell; redstone soft-powers directly.
   sources.append(((rx,p[1]+POWER[0],p[2]+POWER[1]),owner,observer))
 fixed=[]
 for t in range(5):
  w={}
  for p,owner,observer in sources:
   q=shift(p,DISP[owner][t])
   if q in w:return None,'source_overlap'
   w[q]=Block.observer(POWER_DIR,powered=bool(S[owner][(t-1)%5])) if observer else Block(Kind.REDSTONE_BLOCK)
  for p,dp,f,target,sticky in ps:
   q=shift(p,dp[t]);state=2 if (t==f if sticky else (t-f)%5==1) else 0
   if q in w:return None,'fixed_overlap'
   w[q]=Block.piston(1 if sticky else 0,sticky=sticky,state=state)
   if state:
    if shift(q,-1 if sticky else 1) in w:return None,'arm_overlap'
    w[shift(q,-1 if sticky else 1)]=Block(Kind.PISTON_ARM)
  fixed.append(w)

 for t in range(5):
  for pp,dp,f,target,sticky in ps:
   basepos=shift(pp,dp[t]);ext=(f-1)%5 if sticky else f
   if t==ext:continue
   for rp,owner,observer in sources:
    if observer and not S[owner][(t-1)%5]:continue
    sourcepos=shift(rp,DISP[owner][t])
    direct=(add(sourcepos,D[POWER_DIR])==basepos if observer else sum(abs(a-b) for a,b in zip(sourcepos,basepos))==1)
    if direct and sourcepos!=shift(basepos,-1 if sticky else 1):return None,'cross_power'
 @functools.lru_cache(None)
 def legal(p,i):
  for t in range(5):
   q=shift(p,DISP[i][t])
   if q in fixed[t]:return False
   for j,cells in enumerate(ss):
    if j==i:continue
    for delta in range(-int(S[j][t]),int(S[i][t])+1):
     rel=shift(q,-DISP[j][t]+delta)
     if rel in cells or (K[i]==K[j] and any(add(rel,d) in cells for d in D)):return False
   for rp,owner,observer in sources:
    r=shift(rp,DISP[owner][t])
    if i!=owner:
     for delta in range(-int(S[owner][t]),int(S[i][t])+1):
      if sum(abs(a-b) for a,b in zip(shift(q,delta),r))<=1:return False
   for pp,dp,f,target,sticky in ps:
    r=shift(pp,dp[t]);near=sum(abs(a-b) for a,b in zip(q,r))==1
    if (t==(f-1)%5 if sticky else t==f):
     if sticky and q==shift(r,-1):return False # Empty extension is part of the contract.
     if near and S[i][t] and (sticky or i!=target):return False # Cannot rely on extension winning order.

    if t!=((f-1)%5 if sticky else f) and near and q!=shift(r,-1 if sticky else 1):
     for rp,owner,observer in sources:
      if observer and S[owner][(t-1)%5] and add(shift(rp,DISP[owner][t]),D[POWER_DIR])==q:return False
    if t not in ((f,(f-1)%5) if sticky else (f,(f+1)%5)):
     if near and S[i][t]:
      for j,cells in enumerate(ss):
       if j==i:continue
       if shift(r,1-DISP[j][t]) in cells:return False
       # Two bodies moving +X may both be adjacent to the same ready
       # passenger. Either can carry it once; after that move the other
       # loses its starting contact. The destination must still be clear.
     if q==shift(r,1):
      for j,cells in enumerate(ss):
       if j!=i and S[j][t] and any(shift(add(r,d),-DISP[j][t]) in cells for d in D):return False
  return True
 if any(not legal(p,i) for i,s in enumerate(ss) for p in s):return None,'mandatory_conflict'
 for pp,dp,f,target,sticky in rng.sample(ps,len(ps)):
  recovery={t for t in range(5) if t not in ((f,(f-1)%5) if sticky else (f,(f+1)%5))}
  while recovery:
   opts=[]
   for t in recovery:
    for i in range(5):
     if not S[i][t]:continue
     for d in D[2:]:
      p=shift(add(pp,d),dp[t]-DISP[i][t])
      if not legal(p,i):continue
      covered={u for u in recovery if S[i][u] and sum(abs(a-b) for a,b in zip(shift(p,DISP[i][u]),shift(pp,dp[u])))==1}
      distance=min((sum(abs(a-b) for a,b in zip(p,q)) for q in ss[i]),default=2)
      opts.append((-len(covered),p not in ss[i],distance,rng.random(),p,i,covered))
   if not opts:
    (HERE/'last_mixed3_pickup_failure.json').write_text(json.dumps(dict(seed=seed,spacing=spacing,piston=pp,trajectory=dp,action_slot=f,target=target,recovery_remaining=sorted(recovery),segments=[sorted(s) for s in ss],pistons=ps,sources=sources),indent=2))
    return None,'no_pickup'
   *_,p,i,covered=min(opts);ss[i].add(p);recovery-=covered;legal.cache_clear()
 # Observer output must have a same-owner solid that is adjacent to the piston.
 # A transverse output straight into the base is sufficient direct observer
 # power, while the moving source's attachment is supplied on another face.
 for rp,i,observer in sources:
  opts=[(min((sum(abs(a-b) for a,b in zip(add(rp,d),q)) for q in ss[i]),default=0),rng.random(),add(rp,d)) for d in D if legal(add(rp,d),i)]
  if not opts:return None,'source_attach'
  ss[i].add(min(opts)[-1]);legal.cache_clear()
 for i in rng.sample(range(5),5):
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
     if not(-5<=q[0]<=6 and -6<=q[1]<=max(c[0] for c in CENTERS)+5 and -6<=q[2]<=max(c[1] for c in CENTERS)+5):continue
     if q not in ss[i] and not legal(q,i):continue
     nc=cost+(q not in ss[i])
     if nc<dist.get(q,10000):dist[q]=nc;prev[q]=p;heapq.heappush(pq,(nc,rng.random(),q))
   if end is None:return None,'route'
   while end not in reached:ss[i].add(end);end=prev[end]
   if len(ss[i])>cap:return None,'cap'
 flyer=Flyer(rng_state=5,push_limit=1000);flyer._cells=fixed[0].copy()
 for i,s in enumerate(ss):
  for p in s:flyer._cells[p]=Block(K[i])
 return (flyer,dict(seed=seed,spacing=spacing,counts=list(map(len,ss)),segments=[sorted(s) for s in ss],pistons=ps,sources=sources)),None

def main():
 out=HERE/'mixed3_v2_candidates';out.mkdir(exist_ok=True);stats=collections.Counter();manifest=[]
 for spacing in (3,4):
  for seed in range(32):
   ans,reason=build(seed,spacing)
   if ans is None:stats[reason]+=1
   else:
    f,m=ans;f.save(out/f'g{spacing}_s{seed:03}.flyer');manifest.append(m);stats['routed']+=1
   (HERE/'mixed3_v2_manifest.json').write_text(json.dumps(dict(stats=stats,candidates=manifest,current_spacing=spacing,next_seed=seed+1),indent=2))
   print('pull3',spacing,seed,dict(stats),flush=True)
 p=subprocess.run([str(RUNNER),'screen',str(out),'200','--out',str(HERE/'mixed3_v2_screen.csv')],capture_output=True,text=True)
 (HERE/'mixed3_v2_screen.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)


