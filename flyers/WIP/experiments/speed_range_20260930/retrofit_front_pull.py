"""Replace a last normal push by a side-carried sticky powered from ahead.

Existing N3 body trajectories remain the contract. Whole assemblies capped24.
This tests the helper-helper tip against the compact PL18 host, without adding
power hardware or importing any high-limit flyer.
"""
from pathlib import Path
import sys,random,heapq,functools,json,collections,itertools,subprocess
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import three_cell_mixed as base
from fastflyer import Flyer,Block,Kind
ROOT=base.ROOT;BODY=base.BODY;KINDS=base.KINDS[:5];S=base.S[:5];DP=base.DISP[:5]
D=base.D;add=base.add;shift=base.shift;dist=base.dist;connected=base.connected
FR=base.FRAMES

def source(q):
 return next(p for p,b in FR[0].items() if b.kind==Kind.REDSTONE_BLOCK and any(add(p,d) in BODY[q] for d in D) and all(FR[t].get(shift(p,DP[q][t]),Block(Kind.GLASS)).kind==Kind.REDSTONE_BLOCK for t in range(5)))

def old_member(q):
 r=source(q);t=(3-q)%5;rt=shift(r,DP[q][t])
 yz=next((p[1],p[2]) for p,b in FR[t].items() if b.kind==Kind.PISTON and b.state==2 and p[0]==rt[0]-1 and abs(p[1]-rt[1])+abs(p[2]-rt[2])==1)
 off=r[0]-min(q,3)
 px=lambda t:off+3*((q+t)//5)+( (q+t)%5 if 2>=(q+t)%5 else max(2,(q+t)%5-2))
 # Normal firing order may permute between rounds. Remove the observed
 # transverse member rather than asserting a permanent j=2 identity.
 return [min((p for p,b in FR[t].items() if b.kind==Kind.PISTON and p[1:]==yz),key=lambda p:abs(p[0]-px(t))) for t in range(5)]

def build(q,side,seed,prune,chosen=None,source_side=None,power_delta=(1,0,0)):
 rng=random.Random(seed);h=(q+2)%5;g=(q+4)%5;f=(2-q)%5;ext=(f-1)%5
 r=source(g);p=shift(r,DP[g][ext]-DP[h][ext]-1)
 if chosen is not None:
  p=shift(chosen,DP[q][f]+2-DP[h][f]);r=add(shift(p,DP[h][ext]-DP[g][ext]),power_delta)
 contact=shift(p,DP[h][f]-2-DP[q][f]);support=add(p,side)
 old=old_member(q);ss=[s.copy() for s in BODY]
 if prune:
  # Delete only sticky leaves beside the obsolete member, preserving every
  # other original mandatory port. A failed attempt cannot change the host.
  for owner in (q,(q-2)%5):
   for a in list(ss[owner]):
    if any(dist(a,old[0])<=2 for _ in [0]) and sum(add(a,d) in ss[owner] for d in D)==1:
     rest=ss[owner]-{a}
     if len(connected(rest))==len(rest):ss[owner]=rest
 ss[q].add(contact);ss[h].add(support)
 if chosen is not None:ss[g].add(add(r,source_side))
 fixed=[]
 for t in range(5):
  w={a:b for a,b in FR[t].items() if b.kind not in (Kind.SLIME,Kind.HONEY)}
  ob=w.pop(old[t]);assert ob.kind==Kind.PISTON
  if ob.state:w.pop(shift(old[t],1))
  if chosen is not None:
   rr=shift(r,DP[g][t])
   if rr in w:return None,'source_overlap'
   w[rr]=Block(Kind.REDSTONE_BLOCK)
  pp=shift(p,DP[h][t]);state=2 if t==f else 0
  if pp in w:return None,'piston_overlap'
  w[pp]=Block.piston(1,sticky=True,state=state)
  if state:
   arm=shift(pp,-1)
   if arm in w:return None,'arm_overlap'
   w[arm]=Block(Kind.PISTON_ARM)
  # The new sticky must receive exactly the one intended extension pulse.
  powered=any(b.kind==Kind.REDSTONE_BLOCK and dist(a,pp)==1 and a!=shift(pp,-1) for a,b in w.items())
  if powered!=(t==ext):return None,'power_contract'
  if chosen is not None:
   for a,b in w.items():
    if a!=pp and b.kind==Kind.PISTON and dist(a,rr)==1 and rr!=shift(a,1):return None,'cross_power'
  fixed.append(w)
 @functools.lru_cache(None)
 def legal(a,i):
  for t in range(5):
   at=shift(a,DP[i][t]);pp=shift(p,DP[h][t])
   if at in fixed[t]:return False
   for j,body in enumerate(ss):
    if j==i:continue
    for delta in range(-S[j][t],S[i][t]+1):
     rel=shift(at,-DP[j][t]+delta)
     if rel in body or (KINDS[i]==KINDS[j] and any(add(rel,d) in body for d in D)):return False
   if t==ext and (at==shift(pp,-1) or (dist(at,pp)==1 and S[i][t])):return False
   # At the pull the sticky is already extended/immovable, so side adhesion
   # cannot steal it. Destination occupancy is checked separately.
   if t not in (ext,f) and dist(at,pp)==1 and S[i][t] and i!=h:return False
   if chosen is not None and i!=g:
    rr=shift(r,DP[g][t])
    if S[i][t] and any(dist(at,shift(rr,k))==1 or shift(at,1)==shift(rr,k) for k in range(S[g][t]+1)):return False
    if dist(at,rr)==0:return False
   if S[i][t]:
    for d in D:
     a2=add(at,d);b=FR[t].get(a2)
     if a2==old[t] or b is None or b.kind not in (Kind.PISTON,Kind.REDSTONE_BLOCK,Kind.OBSERVER,Kind.ROD):continue
     if b.kind==Kind.PISTON and b.state:continue
     owners={j for j,body in enumerate(BODY) if S[j][t] and any(shift(add(a2,e),-DP[j][t]) in body for e in D)}
     if i not in owners:return False
  return True
 for i in range(5):
  for a in ss[i]:
   if not legal(a,i):return None,f'mandatory:{i}:{a}'
 for i in ((q,h,g) if chosen is not None else (q,h)):
  while len(connected(ss[i]))<len(ss[i]):
   legal.cache_clear();reached=connected(ss[i]);targets=ss[i]-reached;budget=19-len(ss[i])
   if budget<0:return None,'capacity_bound'
   pq=[(0,rng.random(),a) for a in reached];heapq.heapify(pq);cost={a:0 for a in reached};prev={};end=None
   while pq:
    c,_,a=heapq.heappop(pq)
    if c!=cost[a]:continue
    if a in targets:end=a;break
    for d in rng.sample(D,6):
     b=add(a,d)
     if not(5<=b[0]<=28 and -5<=b[1]<=14 and 5<=b[2]<=30):continue
     if b not in ss[i] and not legal(b,i):continue
     nc=c+int(b not in ss[i])
     if nc<=budget and nc<cost.get(b,1000):cost[b]=nc;prev[b]=a;heapq.heappush(pq,(nc,rng.random(),b))
   if end is None:return None,'route'
   while end not in reached:ss[i].add(end);end=prev[end]
 flyer=Flyer.load(ROOT/'flyers/bank/pl18/n3_five_body.flyer');flyer.push_limit=24;flyer._cells=fixed[0].copy()
 for i,body in enumerate(ss):
  for a in body:flyer._cells[a]=Block(KINDS[i])
 return (flyer,dict(q=q,h=h,g=g,sticky=p,contact=contact,support=support,power_source=r,power_delta=power_delta,new_source=chosen is not None,removed=old[0],prune=prune,counts=list(map(len,ss)))),None

def main():
 flexible='--flexible' in sys.argv;transverse='--transverse' in sys.argv;prefix='retrofit_front_pull'+('_transverse' if transverse else '_flexible' if flexible else '')
 out=HERE/prefix;out.mkdir(exist_ok=True);rows=[];stats=collections.Counter()
 trials=[]
 if flexible:
  for q in sorted(range(5),key=lambda q:-len(BODY[q])):
   h=(q+2)%5;g=(q+4)%5;f=(2-q)%5;ext=(f-1)%5
   ranked=[]
   for chosen,side,source_side,power_delta in itertools.product(BODY[q],D[2:],D[2:],D[2:] if transverse else (D[0],)):
    p=shift(chosen,DP[q][f]+2-DP[h][f]);r=add(shift(p,DP[h][ext]-DP[g][ext]),power_delta)
    score=min(dist(add(p,side),a) for a in BODY[h])+min(dist(add(r,source_side),a) for a in BODY[g])
    ranked.append((score,chosen,side,source_side,power_delta))
   for score,chosen,side,source_side,power_delta in sorted(ranked):
    if transverse and score>6:continue
    trials.append((q,side,True,chosen,source_side,power_delta))
 else:trials=[(q,s,p,None,None,D[0]) for q,s,p in itertools.product(range(5),D[2:],(False,True))]
 for q,side,prune,chosen,source_side,power_delta in trials:
  ans,reason=build(q,side,0,prune,chosen,source_side,power_delta);row=dict(q=q,side=side,prune=prune,contact=chosen,source_side=source_side,power_delta=power_delta,reason=reason)
  if ans:
   flyer,data=ans;name=f'c{len(rows):03}.flyer';flyer.save(out/name);row.update(file=name,**data);stats['routed']+=1
  else:stats[reason.split(':')[0]]+=1
  rows.append(row)
  if len(rows)%32==0:
   (HERE/f'{prefix}.manifest.json').write_text(json.dumps(dict(stats=stats,attempts=rows),indent=2));print(len(rows),dict(stats),flush=True)
 (HERE/f'{prefix}.manifest.json').write_text(json.dumps(dict(stats=stats,attempts=rows),indent=2));print(dict(stats),flush=True)
 runner=ROOT/'target/release/fastflyer-research.exe'
 p=subprocess.run([str(runner),'screen',str(out),'240','--out',str(HERE/f'{prefix}.screen.csv')],capture_output=True,text=True)
 (HERE/f'{prefix}.screen.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)
if __name__=='__main__':main()
