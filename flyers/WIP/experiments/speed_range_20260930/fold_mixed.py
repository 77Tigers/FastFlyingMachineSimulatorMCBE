"""Fold the checked five-cell mixed interfaces by their actual helper graph.

No high-limit driver is used. Ten bodies discharge every motion obligation.
Layouts are optimized before routing; route budget20 adhesive/body and all
simulations use24. Surrogate placement scores are not movement-load claims.
"""
from pathlib import Path
import sys,json,random,math,heapq,functools,collections,subprocess,argparse,time
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
HERE=Path(__file__).resolve().parent;OLD=HERE.parent/'overnight_20260930'
D=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
S=[[(t+3*i)%5<3 for t in range(5)] for i in range(10)]
DISP=[[sum(s[:t]) for t in range(6)] for s in S]
K=[Kind.SLIME if i%2==0 else Kind.HONEY for i in range(10)]
COVER=json.loads((OLD/'compact_mixed_tile_contact_cover.json').read_text())
def add(p,q):return tuple(a+b for a,b in zip(p,q))
def shift(p,x):return p[0]+x,p[1],p[2]
def distance(a,b):return sum(abs(x-y) for x,y in zip(a,b))
def rotate(p,q):
 x,y,z=p
 for _ in range(q):y,z=-z,y
 return x,y,z
def conn(s):
 reached={min(s)};stack=list(reached)
 while stack:
  p=stack.pop()
  for d in D:
   q=add(p,d)
   if q in s and q not in reached:reached.add(q);stack.append(q)
 return reached

source=(OLD/'mixed_role_ring_legal.py').read_text()
ns=dict(D=D,S=S,DISP=DISP,K=K,Block=Block,Kind=Kind,shift=shift,add=add,functools=functools)
exec(compile(source,'checked_mixed_role_legal','exec'),ns)

def assemble(layout):
 ss=[set() for _ in S];ps=[];sources=[]
 for node,(x,y,z,q) in enumerate(layout):
  phase=3*node%5
  def point(raw,dx=0):
   p=rotate(tuple(raw[a]-COVER['delta'][a] for a in range(3)),q)
   return p[0]+x+dx,p[1]+y,p[2]+z
  for p in COVER['patches'][5]:ss[node].add(point(p))
  for old,owner in ((2,(node-1)%10),(3,(node+1)%10),(4,(node+3)%10)):
   for p in COVER['patches'][old]:ss[owner].add(point(p,DISP[(2*old)%10][phase]-DISP[0][phase]))
  # Original phase table in the cover is phase0,1,2,3,4. Our node phase
  # is3*n; locate the matching schedule rather than identify equal bodies.
  def olddisp(old,t):return sum((u+old)%5<3 for u in range(t))
  for p,dp,f,target,sticky in COVER['pistons']:
   newdp=[3*((phase+t)//5)+dp[(phase+t)%5]-dp[phase] for t in range(5)]
   ps.append((point(p,dp[phase]-olddisp(0,phase)),newdp,(f-phase)%5,node,sticky))
  direction=D.index(rotate((0,-1,0),q))
  for p,owner,observer in COVER['sources']:
   old=0 if owner==5 else owner;new=node if owner==5 else (node+3)%10
   sources.append((point(p,olddisp(old,phase)-olddisp(0,phase)),new,observer,direction))
 return ss,ps,sources

def score(layout):
 ss,ps,sources=assemble(layout);penalty=0
 for t in range(5):
  cells={}
  for i,body in enumerate(ss):
   for p in body:
    q=shift(p,DISP[i][t])
    if q in cells:penalty+=10
    cells[q]=i
  for q,i in cells.items():
   for d in D:
    j=cells.get(add(q,d))
    if j is not None and j!=i and K[i]==K[j]:penalty+=2
  fixed=[]
  for p,owner,obs,direction in sources:
   q=shift(p,DISP[owner][t]);fixed.append(q)
   if q in cells:penalty+=10
   for d in D:
    other=cells.get(add(q,d))
    if other is not None and other!=owner:penalty+=2
  for p,dp,f,target,sticky in ps:
   q=shift(p,dp[t]);fixed.append(q)
   if q in cells:penalty+=10
   if t==f if sticky else (t-f)%5==1:
    arm=shift(q,-1 if sticky else 1);fixed.append(arm)
    if arm in cells:penalty+=10
  penalty+=10*(len(fixed)-len(set(fixed)))
 costs=[]
 for body in ss:
  reached=conn(body);remaining=body-reached;added=0
  while remaining:
   a,b=min(((a,b) for a in reached for b in remaining),key=lambda pair:distance(*pair));added+=max(0,distance(a,b)-1)
   component=conn({b}|remaining);reached|=component;remaining-=component
  costs.append(len(body)+added)
 return 40*penalty+4*max(costs)+sum(costs),costs,penalty

def route(layout,seed):
 ss,ps,sources=assemble(layout);legal=ns['make_legal'](ss,ps,sources)
 if not callable(legal):return None,legal[1]
 if any(not legal(p,i) for i,body in enumerate(ss) for p in body):return None,'mandatory'
 rng=random.Random(seed)
 for i in rng.sample(range(10),10):
  while len(conn(ss[i]))<len(ss[i]):
   legal.cache_clear();reached=conn(ss[i]);targets=ss[i]-reached;budget=20-len(ss[i])
   if budget<0:return None,'capacity_bound'
   pq=[(0,rng.random(),p) for p in reached];heapq.heapify(pq);cost={p:0 for p in reached};prev={};end=None
   while pq:
    c,_,p=heapq.heappop(pq)
    if c!=cost[p]:continue
    if p in targets:end=p;break
    if c>budget:continue
    for d in rng.sample(D,6):
     q=add(p,d)
     if not(-9<=q[0]<=9 and -11<=q[1]<=11 and -11<=q[2]<=11):continue
     if q not in ss[i] and not legal(q,i):continue
     nc=c+int(q not in ss[i])
     if nc<=budget and nc<cost.get(q,1000):cost[q]=nc;prev[q]=p;heapq.heappush(pq,(nc,rng.random(),q))
   if end is None:return None,'route'
   while end not in reached:ss[i].add(end);end=prev[end]
 f=Flyer(rng_state=5,push_limit=24)
 for p,owner,observer,direction in sources:f._cells[p]=Block.observer(direction,powered=bool(S[owner][4])) if observer else Block(Kind.REDSTONE_BLOCK)
 for p,dp,phase,target,sticky in ps:
  state=2 if (phase==0 if sticky else (0-phase)%5==1) else 0
  f._cells[p]=Block.piston(1 if sticky else 0,sticky=sticky,state=state)
  if state:f._cells[shift(p,-1 if sticky else 1)]=Block(Kind.PISTON_ARM)
 for i,body in enumerate(ss):
  for p in body:
   if p in f._cells:return None,'final_overlap'
   f._cells[p]=Block(K[i])
 return (f,dict(segments=[sorted(b) for b in ss],pistons=ps,sources=sources,layout=layout,counts=list(map(len,ss)))),None

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seeds',type=int,default=12);ap.add_argument('--steps',type=int,default=600);a=ap.parse_args()
 out=HERE/'fold_mixed';out.mkdir(exist_ok=True);manifest=[];stats=collections.Counter()
 for seed in range(a.seeds):
  rng=random.Random(7719+seed)
  # Fold cycle order into a two-row cluster. Optimizer moves all coordinates
  # and rotations independently, minimizing helper routes rather than radius.
  order=rng.sample(range(10),10);layout=[(rng.choice((-1,0,1)),(order[i]%5)*3-6,(order[i]//5)*4-2,rng.randrange(4)) for i in range(10)]
  current=score(layout)[0];best=(current,layout.copy())
  for step in range(a.steps):
   trial=layout.copy();i=rng.randrange(10);p=list(trial[i]);axis=rng.randrange(4)
   if axis==3:p[3]=(p[3]+rng.choice((-1,1)))%4
   else:p[axis]=max(-3 if axis==0 else -7,min(3 if axis==0 else 7,p[axis]+rng.choice((-1,1))))
   trial[i]=tuple(p);value=score(trial)[0];temp=max(3,150*(1-step/a.steps))
   if value<current or rng.random()<math.exp(min(0,(current-value)/temp)):layout=trial;current=value
   if current<best[0]:best=(current,layout.copy())
  val,costs,penalty=score(best[1]);ans,reason=route(best[1],seed)
  row=dict(seed=seed,score=val,predicted_routes=costs,collision_penalty=penalty,layout=best[1],reason=reason)
  if ans:
   f,data=ans;file=f'c{seed:03}.flyer';f.save(out/file);row.update(file=file,**data);stats['routed']+=1
  else:stats[reason]+=1
  manifest.append(row);(HERE/'fold_mixed.manifest.json').write_text(json.dumps(dict(stats=stats,candidates=manifest),indent=2))
  print('fold',seed,'surrogate',costs,'penalty',penalty,'result',reason,dict(stats),flush=True)
 runner=ROOT/'flyers/WIP/experiments/bin/research_runner.exe';r=subprocess.run([str(runner),'screen',str(out),'240','--out',str(HERE/'fold_mixed.screen.csv')],capture_output=True,text=True);(HERE/'fold_mixed.screen.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)

if __name__=='__main__':main()
