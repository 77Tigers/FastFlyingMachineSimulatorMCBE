"""Three sticky cells with a shared own redstone normal group.

The puller is powered by an existing front segment redstone, axially from+X.
There is no added helper source, rod or glazed terminal. All original driver
cells are preserved and the complete encoded assembly is capped at24.
"""
from pathlib import Path
import sys,csv,json,random,heapq,functools,subprocess,itertools,collections
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import three_cell_mixed as base
from fastflyer import Flyer,Block,Kind
D=base.D;BODY=base.BODY;FRAMES=base.FRAMES;add=base.add;shift=base.shift;dist=base.dist;connected=base.connected
OLD_S=base.S[:5];OLD_DISP=base.DISP[:5];KINDS=base.KINDS[:5]

def build(front_source,phase,swap,sy,sz,seed=0,diagonal=False):
 rng=random.Random(seed);S=OLD_S+[[int((t+phase)%5<3) for t in range(5)]];DISP=OLD_DISP+[[sum(S[5][:t]) for t in range(6)]]
 kinds=KINDS+[Kind.HONEY if KINDS[(phase+3)%5]==Kind.SLIME else Kind.SLIME]
 source_dx=OLD_DISP[4][phase]-OLD_DISP[0][phase]
 origin=shift(front_source,-5-source_dx)
 if diagonal:origin=add(origin,(0,-sy,-sz))
 def tr(p,dx=0):
  x,y,z=p
  if swap:y,z=z,y
  return add((x+dx,sy*y,sz*z),origin)
 target={(0,0,0),(0,0,1),(0,1,0),(0,1,1)} if diagonal else {(0,0,z) for z in (-1,0,1)}
 ss=[s.copy() for s in BODY]+[{tr(p) for p in target}];added=[set() for _ in range(6)]
 owners=[(2+phase)%5,(3+phase)%5];patches={2:[(3,2,1)],3:[(-1,1,1)]} if diagonal else {2:[(3,-1,0)],3:[(-1,-1,-1),(-1,-1,0),(-1,-1,1)]}
 for old,points in patches.items():
  owner=(old+phase)%5
  for p in points:
   q=tr(p,OLD_DISP[old][phase]-OLD_DISP[0][phase]);ss[owner].add(q);added[owner].add(q)
 ps=[]
 for p,dp,f,sticky in [((-1,0,1),[0,0,0,1,2],0,False),((-1,1,0) if diagonal else (-1,0,-1),[0,1,1,1,2],1,False),((3,1,1) if diagonal else (3,0,0),[0,1,1,1,2],2,True)]:
  ps.append((tr(p,dp[phase]-OLD_DISP[0][phase]),[3*((phase+t)//5)+dp[(phase+t)%5]-dp[phase] for t in range(5)],(f-phase)%5,sticky))
 red=tr((-1,0,0));fixed=[]
 for t in range(5):
  w={p:b for p,b in FRAMES[t].items() if b.kind not in (Kind.SLIME,Kind.HONEY)}
  q=shift(red,DISP[5][t])
  if q in w:return None,'source_overlap'
  w[q]=Block(Kind.REDSTONE_BLOCK)
  for p,dp,f,sticky in ps:
   q=shift(p,dp[t]);state=2 if (t==f if sticky else (t-f)%5==1) else 0
   if q in w:return None,'piston_overlap'
   w[q]=Block.piston(1 if sticky else 0,sticky=sticky,state=state)
   if state:
    arm=shift(q,-1 if sticky else 1)
    if arm in w:return None,'arm_overlap'
    w[arm]=Block(Kind.PISTON_ARM)
  fixed.append(w)
 # New target redstone must not power any old actuator.
 for t in range(5):
  r=shift(red,DISP[5][t])
  for p,b in FRAMES[t].items():
   if b.kind==Kind.PISTON and r!=add(p,D[b.direction]) and dist(r,p)==1:return None,'driver_cross_power'
 @functools.lru_cache(None)
 def legal(p,i):
  for t in range(5):
   q=shift(p,DISP[i][t])
   if q in fixed[t]:return False
   for j,body in enumerate(ss):
    if j==i:continue
    for delta in range(-S[j][t],S[i][t]+1):
     rel=shift(q,-DISP[j][t]+delta)
     if rel in body or (kinds[i]==kinds[j] and any(add(rel,d) in body for d in D)):return False
   for pp,dp,f,sticky in ps:
    r=shift(pp,dp[t]);near=dist(q,r)==1
    ext=(f-1)%5 if sticky else f
    # Either normal member can win; both are ready before the first push.
    if sticky and t==ext and q==shift(r,-1):return False
    if sticky and t==ext and near and S[i][t]:return False
    if not sticky and t==f and near and S[i][t] and i!=5:return False
    if t not in ((f,ext) if sticky else (f,(f+1)%5)) and near and S[i][t]:
     for j,body in enumerate(ss):
      if j!=i and shift(r,1-DISP[j][t]) in body:return False
   r=shift(red,DISP[5][t])
   if i!=5 and S[i][t] and any(dist(q,shift(r,delta))==1 or shift(q,1)==shift(r,delta) for delta in range(S[5][t]+1)):return False
   if S[i][t]:
    for d in D:
     r=add(q,d);b=FRAMES[t].get(r)
     if b is None or b.kind not in (Kind.PISTON,Kind.REDSTONE_BLOCK,Kind.OBSERVER,Kind.ROD):continue
     if b.kind==Kind.PISTON and b.state:continue
     oldowners={j for j,body in enumerate(BODY) if S[j][t] and any(shift(add(r,e),-DISP[j][t]) in body for e in D)}
     if i not in oldowners:return False
  return True
 if any(not legal(p,i) for i in range(6) for p in (ss[i] if i==5 else added[i])):return None,'mandatory'
 for i in owners:
  while len(connected(ss[i]))<len(ss[i]):
   legal.cache_clear();reached=connected(ss[i]);targets=ss[i]-reached;budget=(19 if i==owners[0] else 18)-len(ss[i])
   if budget<0:return None,'capacity_bound'
   pq=[(0,rng.random(),p) for p in reached];heapq.heapify(pq);cost={p:0 for p in reached};prev={};end=None
   while pq:
    c,_,p=heapq.heappop(pq)
    if c!=cost[p]:continue
    if p in targets:end=p;break
    for d in rng.sample(D,6):
     q=add(p,d)
     if not(6<=q[0]<=26 and -5<=q[1]<=14 and 6<=q[2]<=30):continue
     if q not in ss[i] and not legal(q,i):continue
     nc=c+int(q not in ss[i])
     if nc<=budget and nc<cost.get(q,1000):cost[q]=nc;prev[q]=p;heapq.heappush(pq,(nc,rng.random(),q))
   if end is None:return None,'route'
   while end not in reached:ss[i].add(end);end=prev[end]
 f=Flyer.load(ROOT/'flyers/bank/pl18/n3_five_body.flyer');f.push_limit=24
 for p,b in fixed[0].items():f._cells[p]=b
 for i,body in enumerate(ss):
  for p in body:
   if p in fixed[0]:return None,'final_overlap'
   f._cells[p]=Block(kinds[i])
 return (f,dict(origin=origin,phase=phase,diagonal=diagonal,transform=[swap,sy,sz],front_source=front_source,segments=[sorted(s) for s in ss],pistons=ps,counts=list(map(len,ss)))),None

def main():
 diagonal='--diagonal' in sys.argv;prefix='shared_red_mixed'+('_diagonal' if diagonal else '');out=HERE/prefix;out.mkdir(exist_ok=True);stats=collections.Counter();manifest=[]
 for phase in range(5):
  owner=(4+phase)%5
  sources=[p for p,b in FRAMES[0].items() if b.kind==Kind.REDSTONE_BLOCK and any(add(p,d) in BODY[owner] for d in D)]
  for source in sources:
   for rot in itertools.product((0,1),(-1,1),(-1,1)):
    ans,reason=build(source,phase,*rot,diagonal=diagonal);row=dict(phase=phase,source=source,transform=rot,reason=reason)
    if ans:
     f,data=ans;name=f'c{len(manifest):04}.flyer';f.save(out/name);row.update(file=name,**data);stats['routed']+=1
    else:stats[reason]+=1
    manifest.append(row)
  print('shared_red',phase,dict(stats),flush=True)
 (HERE/f'{prefix}.manifest.json').write_text(json.dumps(dict(stats=stats,candidates=manifest),indent=2))
 runner=ROOT/'flyers/WIP/experiments/bin/research_runner.exe';p=subprocess.run([str(runner),'screen',str(out),'240','--out',str(HERE/f'{prefix}.screen.csv')],capture_output=True,text=True);(HERE/f'{prefix}.screen.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)

if __name__=='__main__':main()
