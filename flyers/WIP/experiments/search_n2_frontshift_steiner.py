"""Exact small-grid Steiner routes for the four fixed return-carrier terminals."""
from pathlib import Path
import csv,heapq,os,random,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
base=Flyer.load(ROOT/'flyers/WIP/experiments/n2_frontshift_base.flyer')
base.rng_state=0
old_h={p for p,b in base._cells.items() if b.kind==Kind.HONEY}
fixed={p for p in base._cells if p not in old_h}
front_sources=((14,1,15),(14,1,16),(14,1,17),(14,2,15),(15,1,16),(16,0,16),(16,0,17),(16,1,16),(17,0,15),(17,0,16),(17,0,17),(17,1,16))
front_sweep={(x+d,y,z) for x,y,z in front_sources for d in (1,2)}
front_sweep.add((16,2,17))  # second return piston is picked up only on the second front stroke
fixed|=front_sweep-old_h
terminals=((16,0,14),(16,0,18),(16,2,16),(17,2,15))
nodes=[(x,y,z) for x in range(15,19) for y in range(0,4) for z in range(13,20) if (x,y,z) not in fixed]
nodeindex={p:i for i,p in enumerate(nodes)};n=len(nodes);ti=[nodeindex[p] for p in terminals]
adj=[]
for x,y,z in nodes:
 adj.append([nodeindex[q] for q in ((x+1,y,z),(x-1,y,z),(x,y+1,z),(x,y-1,z),(x,y,z+1),(x,y,z-1)) if q in nodeindex])
out=Path(os.environ['TEMP'])/'n2_frontshift_steiner';out.mkdir(exist_ok=True)
rows=[];seen=set()
for seed in range(300):
 rng=random.Random(seed);w=[100+rng.randrange(20) for _ in nodes]
 for k in ti:w[k]=100
 dp=[[10**9]*n for _ in range(16)];back=[[None]*n for _ in range(16)]
 for j,v in enumerate(ti):dp[1<<j][v]=w[v]
 for mask in range(1,16):
  sub=(mask-1)&mask
  while sub:
   other=mask^sub
   for v in range(n):
    cost=dp[sub][v]+dp[other][v]-w[v]
    if cost<dp[mask][v]:dp[mask][v]=cost;back[mask][v]=('merge',sub,other)
   sub=(sub-1)&mask
  pq=[(d,v) for v,d in enumerate(dp[mask]) if d<10**9];heapq.heapify(pq)
  while pq:
   d,v=heapq.heappop(pq)
   if d!=dp[mask][v]:continue
   for u in adj[v]:
    nd=d+w[u]
    if nd<dp[mask][u]:dp[mask][u]=nd;back[mask][u]=('edge',v);heapq.heappush(pq,(nd,u))
 end=min(range(n),key=lambda v:dp[15][v]);selected=set();stack=[(15,end)];visited=set()
 while stack:
  mask,v=stack.pop()
  if (mask,v) in visited:continue
  visited.add((mask,v));selected.add(nodes[v]);b=back[mask][v]
  if b is None:continue
  if b[0]=='edge':stack.append((mask,b[1]))
  else:stack.extend([(b[1],v),(b[2],v)])
 key=frozenset(selected)
 if key in seen:continue
 seen.add(key)
 f=Flyer(rng_state=0,push_limit=12);f._cells={p:b for p,b in base._cells.items() if p not in old_h}
 for p in selected:f._cells[p]=Block(Kind.HONEY)
 path=out/f's{seed}_h{len(selected)}.flyer'
 try:f.save(path)
 except:continue
 rows.append((seed,len(selected),str(path)))
run=Path(os.environ['TEMP'])/'flyer_batch.exe'
p=subprocess.run([str(run),'80',str(out)],capture_output=True,text=True)
scores=[]
for line in p.stdout.splitlines():
 fields=line.split('\t')
 if len(fields)>1:
  try:scores.append((int(fields[1]),line))
  except:pass
print('unique',len(rows),'min_h',min((r[1] for r in rows),default=-1),'top',*sorted(scores,reverse=True)[:30],sep='\n')
