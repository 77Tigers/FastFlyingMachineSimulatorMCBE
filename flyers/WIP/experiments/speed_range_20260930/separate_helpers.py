"""Two new normals on existing PL18 side contacts; helpers are separate bodies.

Old body3 drives new helper0 twice, helper0 pulls old body3 once. New helper2
pulls helper0 and powers its sticky. Helper2 initially retains a three-normal
drive, powered by its own redstone; its pulling sticky is powered by existing
body4. No glue is added to any original body. Whole flyer cap24.
"""
from pathlib import Path
import sys,itertools,random,heapq,functools,json,collections,subprocess
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import retrofit_front_pull as b
from fastflyer import Flyer,Block,Kind
ROOT=b.ROOT;D=b.D;add=b.add;shift=b.shift;dist=b.dist;conn=b.connected
if '--main0' in sys.argv:
 # Rotate the existing PL18 boundary by three slots. Original body0 (the
 # segment after original body3 in the back-drive chain) becomes body3.
 original_body=b.BODY;original_kind=b.KINDS;original_frames=b.FR
 b.BODY=[None]*5;b.KINDS=[None]*5
 for q in range(5):
  b.BODY[(q+3)%5]={shift(p,b.DP[q][3]) for p in original_body[q]}
  b.KINDS[(q+3)%5]=original_kind[q]
 b.FR=[{shift(p,3*((3+t)//5)):x for p,x in original_frames[(3+t)%5].items()} for t in range(5)]
S=b.S+[[1,1,1,0,0],[1,0,0,1,1]];DP=[[sum(s[:t]) for t in range(6)] for s in S]
K=b.KINDS+[Kind.HONEY,Kind.HONEY if '--same-kind' in sys.argv else Kind.SLIME]

def build(anchor,dy,dz,oldcontact,power,frontpower,arms,seed=0):
 rng=random.Random(seed);rH=add(anchor,add(dy,dz));n1=add(anchor,dy);n2=add(anchor,dz)
 hfront={shift(rH,1),shift(n1,1),shift(n2,1)}
 # Pull reach is base-2: at slot4 target3 has advanced2 and helper0
 # has advanced3, hence base_initial = contact_initial +2+2-3.
 st=shift(oldcontact,1)
 rHH=add(shift(st,2),power)
 sn=add(shift(b.source(4),-1),tuple(-v for v in frontpower))
 hcontact=shift(sn,-3)
 ss=[s.copy() for s in b.BODY]+[hfront|{hcontact}, {shift(rHH,1)}|{shift(add(rHH,a),1) for a in arms}]
 for a in [(0,0,0),*arms]:ss[5].add(add(shift(rHH,-3),a))
 # Side pickup choices are chosen by cheapest connection to each helper.
 hs=min((add(st,d) for d in D[2:]),key=lambda p:min(dist(p,a) for a in ss[5]))
 ns=min((add(sn,d) for d in D[2:]),key=lambda p:min(dist(p,a) for a in ss[6]))
 ss[5].add(hs);ss[6].add(ns)
 ps=[(n1,[0,0,0,1,2],0,False,5),(n2,[0,1,1,1,2],1,False,5),(st,DP[5][:5],4,True,3),(sn,DP[6][:5],2,True,5)]
 for j,a in enumerate(arms):
  dp=([0,1,2,3,3],[0,0,1,2,3],[0,0,0,1,2])[j]
  ps.append((add(shift(rHH,-2+j),a),dp,(3+j)%5,False,6))
 src=[(rH,5),(rHH,6)];removed=b.old_member(3);fixed=[]
 for t in range(5):
  w={p:x for p,x in b.FR[t].items() if x.kind not in (Kind.SLIME,Kind.HONEY)}
  ob=w.pop(removed[t]);
  if ob.state:w.pop(shift(removed[t],1))
  for p,owner in src:
   a=shift(p,DP[owner][t])
   if a in w:return None,'source_overlap'
   w[a]=Block(Kind.REDSTONE_BLOCK)
  for p,dp,f,sticky,target in ps:
   a=shift(p,dp[t]);state=2 if (t==f if sticky else (t-f)%5==1) else 0
   if a in w:return None,'piston_overlap'
   w[a]=Block.piston(1 if sticky else 0,sticky=sticky,state=state)
   if state:
    ar=shift(a,-1 if sticky else 1)
    if ar in w:return None,'arm_overlap'
    w[ar]=Block(Kind.PISTON_ARM)
  # Allow either of the two normals to fire first; forbid foreign powering.
  for p,dp,f,sticky,target in ps:
   a=shift(p,dp[t]);ext=(f-1)%5 if sticky else f
   ownsource=rH if target==5 and not sticky else rHH if target==6 else None
   for r,x in w.items():
    if x.kind!=Kind.REDSTONE_BLOCK or dist(r,a)!=1 or r==shift(a,-1 if sticky else 1):continue
    group_source=shift(rH,DP[5][t]) if target==5 else shift(rHH,DP[6][t])
    group_window=(0,1) if target==5 else (0,3,4)
    if t!=ext and not (not sticky and r==group_source and t in group_window):return None,'power_contract'
   if not any(x.kind==Kind.REDSTONE_BLOCK and dist(r,a)==1 and r!=shift(a,-1 if sticky else 1) for r,x in w.items()) and t==ext:return None,'missing_power'
  for r,owner in src:
   at=shift(r,DP[owner][t])
   for p,x in b.FR[t].items():
    if p!=removed[t] and x.kind==Kind.PISTON and dist(p,at)==1 and at!=shift(p,1):return None,'old_cross_power'
  fixed.append(w)
 @functools.lru_cache(None)
 def legal(p,i):
  for t in range(5):
   a=shift(p,DP[i][t])
   if a in fixed[t]:return False
   for j,body in enumerate(ss):
    if j==i:continue
    for delta in range(-S[j][t],S[i][t]+1):
     rel=shift(a,-DP[j][t]+delta)
     if rel in body or (K[i]==K[j] and any(add(rel,d) in body for d in D)):return False
   for pp,dp,f,sticky,target in ps:
    r=shift(pp,dp[t]);ext=(f-1)%5 if sticky else f
    if t==ext:
     if sticky and a==shift(r,-1):return False
     if dist(a,r)==1 and S[i][t] and (sticky or i!=target):return False
    if t not in ((ext,f) if sticky else (f,(f+1)%5)) and dist(a,r)==1 and S[i][t]:
     if any(shift(r,1-DP[j][t]) in body for j,body in enumerate(ss) if j!=i):return False
   for pp,owner in src:
    r=shift(pp,DP[owner][t])
    if i!=owner and S[i][t] and any(dist(a,shift(r,k))==1 or shift(a,1)==shift(r,k) for k in range(S[owner][t]+1)):return False
   if i>=5 and S[i][t]:
    for d in D:
     r=add(a,d);x=b.FR[t].get(r)
     if x is None or r==removed[t] or x.kind not in (Kind.PISTON,Kind.REDSTONE_BLOCK,Kind.ROD,Kind.OBSERVER):continue
     if x.kind==Kind.PISTON and x.state:continue
     return False
  return True
 for i,body in enumerate(ss):
  for p in sorted(body):
   if not legal(p,i):return None,f'mandatory:{i}:{p}'
 for i in (5,6):
  while len(conn(ss[i]))<len(ss[i]):
   legal.cache_clear();reached=conn(ss[i]);targets=ss[i]-reached;budget=18-len(ss[i])
   if budget<0:return None,'capacity_bound'
   pq=[(0,rng.random(),p) for p in reached];heapq.heapify(pq);cost={p:0 for p in reached};prev={};end=None
   while pq:
    c,_,p=heapq.heappop(pq)
    if c!=cost[p]:continue
    if p in targets:end=p;break
    for d in rng.sample(D,6):
     a=add(p,d)
     if not(8<=a[0]<=25 and -4<=a[1]<=10 and 10<=a[2]<=27):continue
     if a not in ss[i] and not legal(a,i):continue
     nc=c+int(a not in ss[i])
     if nc<=budget and nc<cost.get(a,1000):cost[a]=nc;prev[a]=p;heapq.heappush(pq,(nc,rng.random(),a))
   if end is None:return None,'route'
   while end not in reached:ss[i].add(end);end=prev[end]
 flyer=Flyer.load(ROOT/'flyers/bank/pl18/n3_five_body.flyer');flyer.push_limit=24;flyer._cells=fixed[0].copy()
 for i,body in enumerate(ss):
  for p in body:flyer._cells[p]=Block(K[i])
 return (flyer,dict(anchor=anchor,normal_sites=[n1,n2],helper_source=rH,helper_helper_source=rHH,old_pull_contact=oldcontact,helper_pull_contact=hcontact,counts=list(map(len,ss)))),None

def main():
 prefix='separate_helpers'+('_main0' if '--main0' in sys.argv else '')+('_same_kind' if '--same-kind' in sys.argv else '')+('_front' if '--front' in sys.argv else '')
 out=HERE/prefix;out.mkdir(exist_ok=True);stats=collections.Counter();rows=[];tries=0
 # Only existing side cells, no adhesive additions to the original five.
 anchors=sorted(b.BODY[3],key=lambda p:(sum(add(p,d) in b.BODY[3] for d in D),-p[0],p[1],p[2])) if '--front' in sys.argv else sorted(b.BODY[3])
 for anchor,ys,zs in itertools.product(anchors,(-1,1),(-1,1)):
  dy=(0,ys,0);dz=(0,0,zs);r=add(anchor,add(dy,dz))
  sites=[add(anchor,dy),add(anchor,dz),r]
  if any(p in b.FR[0] for p in sites):continue
  for oldcontact,power,frontpower in itertools.product(sorted(b.BODY[3]),(D[0],*D[2:]),(D[0],*D[2:])):
   st=shift(oldcontact,1);rhh=add(shift(st,2),power)
   # Normal arms remain free; enumerate the omitted arm and rotate order.
   armset=((0,1,0),(0,0,1),(0,-1,0),(0,0,-1))
   for omit in range(4):
    arms=tuple(a for j,a in enumerate(armset) if j!=omit)
    ans,reason=build(anchor,dy,dz,oldcontact,power,frontpower,arms)
    tries+=1;stats[reason.split(':')[0] if reason else 'routed']+=1
    if ans:
     flyer,data=ans;name=f'c{tries:05}.flyer';flyer.save(out/name);rows.append(dict(file=name,**data))
    if tries%500==0:
     (HERE/f'{prefix}.manifest.json').write_text(json.dumps(dict(attempts=tries,stats=stats,routed=rows),indent=2));print(tries,dict(stats),flush=True)
    if tries>=18000:break
   if tries>=18000:break
  if tries>=18000:break
 (HERE/f'{prefix}.manifest.json').write_text(json.dumps(dict(attempts=tries,stats=stats,routed=rows),indent=2));print(tries,dict(stats),flush=True)
 runner=ROOT/'target/release/fastflyer-research.exe'
 p=subprocess.run([str(runner),'screen',str(out),'240','--out',str(HERE/f'{prefix}.screen.csv')],capture_output=True,text=True)
 (HERE/f'{prefix}.screen.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)
if __name__=='__main__':main()
