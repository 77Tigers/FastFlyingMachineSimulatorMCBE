"""Three-block target: helper-red push, own observer push, aligned helper pull.

Attach to the bankedPL18 driver without editing any original cell. Whole
assembly is always encoded24; route/collision failures are retained. This
tests a new interface, not a smaller whole-engine speed record.
"""
from pathlib import Path
import sys,csv,json,heapq,random,functools,subprocess,itertools,collections
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
HERE=Path(__file__).resolve().parent
D=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
S=[[int((t+p)%5<3) for t in range(5)] for p in range(5)]+[[1,1,1,0,0]]
DISP=[[sum(s[:t]) for t in range(6)] for s in S]
def add(p,q):return tuple(a+b for a,b in zip(p,q))
def shift(p,x):return p[0]+x,p[1],p[2]
def dist(p,q):return sum(abs(a-b) for a,b in zip(p,q))
def connected(s):
 reached={min(s)};stack=list(reached)
 while stack:
  p=stack.pop()
  for d in D:
   q=add(p,d)
   if q in s and q not in reached:reached.add(q);stack.append(q)
 return reached
FRAMES=[{} for _ in range(5)]
for row in csv.DictReader((HERE/'n3_driver_phases.csv').open()):
 t=int(row['tick'])//2
 if t<5:FRAMES[t][tuple(int(row[k]) for k in ('x','y','z'))]=Block.decode(int(row['cell']))
BODY=[None]*5;KINDS=[None]*5
for kind in (Kind.SLIME,Kind.HONEY):
 remaining={p for p,b in FRAMES[0].items() if b.kind==kind}
 while remaining:
  body=connected(remaining);remaining-=body
  matching=[phase for phase in range(5) if all(all(FRAMES[t].get(shift(p,DISP[phase][t]),Block(Kind.GLASS)).kind==kind for p in body) for t in range(5))]
  assert len(matching)==1,(kind,matching)
  phase=matching[0];assert BODY[phase] is None;BODY[phase]=body;KINDS[phase]=kind
KINDS.append(Kind.HONEY if KINDS[3]==Kind.SLIME else Kind.SLIME)

def build(origin,swap,sy,sz,seed=0,glazed=False,phase=0):
 rng=random.Random(seed)
 S[5]=[int((t+phase)%5<3) for t in range(5)];DISP[5]=[sum(S[5][:t]) for t in range(6)]
 KINDS[5]=Kind.HONEY if KINDS[(phase+3)%5]==Kind.SLIME else Kind.SLIME
 def tr(p,dx=0):
  x,y,z=p
  if swap:y,z=z,y
  return add((x+dx,sy*y,sz*z),origin)
 def direction(d):
  x,y,z=D[d]
  if swap:y,z=z,y
  return D.index((x,sy*y,sz*z))
 ss=[b.copy() for b in BODY]+[{tr((0,0,z)) for z in (-1,0,1)}]
 additions=[set() for _ in range(6)]
 # R3 moves2/3/4 and picks both normal members from below. M2 moves0/3/4
 # and carries the puller and first source; F4 moves1/2/3 and shuts off pull.
 patches={2:([(-2,1,1),(-2,2,1),(3,-1,0)] if glazed else [(-1,2,1),(3,-1,0)]),3:[(-1,-1,-1),(-1,-1,0),(-1,-1,1)],4:[(4,2,0)]}
 for owner,points in patches.items():
  actual=(owner+phase)%5
  for p in points:
   q=tr(p,DISP[owner][phase]-DISP[0][phase]);ss[actual].add(q);additions[actual].add(q)
 ps=[(tr((-1,0,1)),[0,0,0,1,2],0,False),(tr((-1,0,-1)),[0,1,1,1,2],1,False),(tr((3,0,0)),[0,1,1,1,2],2,True)]
 sources=[(tr((-1,2,1) if glazed else (-1,1,1)),2,'rod' if glazed else False,direction(3)),(tr((-1,0,0)),5,True,direction(5)),(tr((4,1,0)),4,False,0)]
 ps=[(shift(p,dp[phase]-DISP[0][phase]),[3*((phase+t)//5)+dp[(phase+t)%5]-dp[phase] for t in range(5)],(f-phase)%5,sticky) for p,dp,f,sticky in ps]
 sources=[(shift(p,DISP[0 if owner==5 else owner][phase]-DISP[0][phase]),5 if owner==5 else (owner+phase)%5,observer,d) for p,owner,observer,d in sources]
 fixed=[]
 for t in range(5):
  w={p:b for p,b in FRAMES[t].items() if b.kind not in (Kind.SLIME,Kind.HONEY)}
  if glazed:
   terminal=shift(tr((-1,1,1),DISP[2][phase]-DISP[0][phase]),DISP[(2+phase)%5][t])
   if terminal in w:return None,'terminal_overlap'
   w[terminal]=Block(Kind.GLAZED_TERRACOTTA)
  for p,owner,observer,d in sources:
   q=shift(p,DISP[owner][t])
   if q in w:return None,'fixed_overlap'
   w[q]=Block.rod(d) if observer=='rod' else Block.observer(d,powered=bool(S[owner][(t-1)%5])) if observer else Block(Kind.REDSTONE_BLOCK)
  for p,dp,f,sticky in ps:
   q=shift(p,dp[t]);state=2 if (t==f if sticky else (t-f)%5==1) else 0
   if q in w:return None,'fixed_overlap'
   w[q]=Block.piston(1 if sticky else 0,sticky=sticky,state=state)
   if state:
    arm=shift(q,-1 if sticky else 1)
    if arm in w:return None,'arm_overlap'
    w[arm]=Block(Kind.PISTON_ARM)
  fixed.append(w)
 # Direct foreign power to any original driver actuator is forbidden.
 for t in range(5):
  for rp,owner,observer,direction in sources:
   if observer is True and not S[owner][(t-1)%5]:continue
   q=shift(rp,DISP[owner][t])
   for p,b in FRAMES[t].items():
    if b.kind==Kind.PISTON and q!=add(p,D[b.direction]):
     if (add(q,D[direction])==p if observer is True else dist(q,p)==1):return None,'driver_cross_power'
     if observer=='rod':
      terminal=add(q,D[direction])
      if terminal in fixed[t] and dist(terminal,p)==1 and terminal!=add(p,D[b.direction]):return None,'terminal_cross_power'
 @functools.lru_cache(None)
 def legal(p,i):
  for t in range(5):
   q=shift(p,DISP[i][t])
   if q in fixed[t]:return False
   for j,body in enumerate(ss):
    if j==i:continue
    for delta in range(-S[j][t],S[i][t]+1):
     rel=shift(q,-DISP[j][t]+delta)
     if rel in body or (KINDS[i]==KINDS[j] and any(add(rel,d) in body for d in D)):return False
   for pp,dp,f,sticky in ps:
    r=shift(pp,dp[t]);near=dist(q,r)==1
    if (t==(f-1)%5 if sticky else t==f) and near and S[i][t] and (sticky or i!=5):return False
    if sticky and t==(f-1)%5 and q==shift(r,-1):return False
    if t not in ((f,(f-1)%5) if sticky else (f,(f+1)%5)) and near and S[i][t]:
     for j,body in enumerate(ss):
      if j!=i and shift(r,1-DISP[j][t]) in body:return False
   for rp,owner,observer,direction in sources:
    r=shift(rp,DISP[owner][t])
    if i!=owner and S[i][t]:
     # Adhesion is discovered BEFORE this body's move. Check source-first
     # ordering, but do not reject adjacency created only after own settling
     # when the next phase loses contact before another movement begins.
     if any(dist(q,shift(r,delta))==1 or shift(q,1)==shift(r,delta) for delta in range(S[owner][t]+1)):return False
   # Original ready driver hardware must retain its movement owner.
   if S[i][t]:
    for d in D:
     r=add(q,d);b=FRAMES[t].get(r)
     if b is None or b.kind not in (Kind.PISTON,Kind.REDSTONE_BLOCK,Kind.OBSERVER,Kind.ROD):continue
     if b.kind==Kind.PISTON and b.state:continue
     owners={j for j,body in enumerate(BODY) if S[j][t] and any(shift(add(r,e),-DISP[j][t]) in body for e in D)}
     if i not in owners:return False
  return True
 if any(not legal(p,i) for i in range(6) for p in (ss[i] if i==5 else additions[i])):return None,'mandatory'
 for i in ((2+phase)%5,(3+phase)%5,(4+phase)%5):
  while len(connected(ss[i]))<len(ss[i]):
   legal.cache_clear();reached=connected(ss[i]);targets=ss[i]-reached;budget=18-len(ss[i])
   if budget<0:return None,'capacity_bound'
   pq=[(0,rng.random(),p) for p in reached];heapq.heapify(pq);cost={p:0 for p in reached};prev={};end=None
   while pq:
    c,_,p=heapq.heappop(pq)
    if c!=cost[p]:continue
    if p in targets:end=p;break
    for d in rng.sample(D,6):
     q=add(p,d)
     if not(8<=q[0]<=26 and -4<=q[1]<=12 and 8<=q[2]<=28):continue
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
   f._cells[p]=Block(KINDS[i])
 return (f,dict(origin=origin,phase=phase,transform=[swap,sy,sz],segments=[sorted(b) for b in ss],pistons=ps,sources=sources,counts=list(map(len,ss)))),None

def main():
 glazed='--glazed' in sys.argv;prefix='three_cell_mixed'+('_glazed' if glazed else '');out=HERE/prefix;out.mkdir(exist_ok=True);stats=collections.Counter();manifest=[]
 # Try placements adjacent to existing helper cells, not arbitrary long rails.
 offsets=set()
 for phase in range(5):
  for p in BODY[(2+phase)%5]:
   for rot in itertools.product((0,1),(-1,1),(-1,1)):
    swap,sy,sz=rot;local=(3+DISP[2][phase]-DISP[0][phase],-1,0);x,y,z=local
    if swap:y,z=z,y
    offsets.add((tuple(a-b for a,b in zip(p,(x,sy*y,sz*z))),rot,phase))
 for attempt,(origin,rot,phase) in enumerate(sorted(offsets)):
  ans,reason=build(origin,*rot,glazed=glazed,phase=phase)
  row=dict(attempt=attempt,origin=origin,phase=phase,transform=rot,reason=reason)
  if ans:
   f,data=ans;name=f'c{attempt:04}.flyer';f.save(out/name);row.update(file=name,**data);stats['routed']+=1
  else:stats[reason]+=1
  manifest.append(row)
  if (attempt+1)%24==0:print('three_cell',attempt+1,dict(stats),flush=True)
 (HERE/f'{prefix}.manifest.json').write_text(json.dumps(dict(stats=stats,candidates=manifest,scope='unchangedPL18 driver plus local three-cell target'),indent=2))
 runner=ROOT/'flyers/WIP/experiments/bin/research_runner.exe';p=subprocess.run([str(runner),'screen',str(out),'240','--out',str(HERE/f'{prefix}.screen.csv')],capture_output=True,text=True);(HERE/f'{prefix}.screen.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)

if __name__=='__main__':main()
