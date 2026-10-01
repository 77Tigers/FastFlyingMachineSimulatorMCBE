"""6-body (two bodies per timing word) mmwmmw generator, adapted from overnight mmw_planar.py.
Each body has its own 9-cell cross with 4 coplanar pistons (24 pistons total); any body may carry any piston.
usage: python gen6.py LAYOUT NSEEDS [START]   -> candidates in cands_LAYOUT/
"""
from pathlib import Path
import sys,json,random,heapq,collections,importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];sys.path.insert(0,str(ROOT))
OV=ROOT/'flyers/WIP/experiments/overnight_20260930'
from fastflyer import Flyer,Block,Kind
spec=importlib.util.spec_from_file_location('m',OV/'derived_mmw.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
NB=6
S6=[m.S[i%3] for i in range(NB)]
DISP6=[m.DISP[i%3] for i in range(NB)]
PH=[(0,2,1)[i%3] for i in range(NB)]
# bodies 0..2 = words 0,1,2 ; bodies 3..5 twins.  materials: twins differ.
K6=[Kind.SLIME,Kind.HONEY,Kind.SLIME,Kind.HONEY,Kind.SLIME,Kind.HONEY]
source=(OV/'mixed_role_ring_legal.py').read_text().replace('range(5)','range(6)').replace('%5','%6')
ns=m.__dict__.copy();ns['S']=S6;ns['DISP']=DISP6;ns['K']=K6
exec(compile(source,'mmw6_legal','exec'),ns)
LAYOUTS={
 # (y,z) centers of bodies 0..5 ; twin of i is i+3
 'grid23':[(0,0),(0,6),(0,12),(6,0),(6,6),(6,12)],
 'grid23t':[(0,0),(0,6),(0,12),(6,12),(6,6),(6,0)],
 'hex':[(0,0),(0,6),(5,9),(10,6),(10,0),(5,-3)],
 'hexalt2':[(0, 0), (5, 9), (0, 6), (10, 6), (5, -3), (10, 0)],
 'pairs':[(0,0),(0,6),(0,12),(6,0),(6,6),(6,12)],
}
def build(seed,centers,cap=80,span=8,twinperm=None,pickup_only=False,fq=None):
 rng=random.Random(seed);ss=[set() for _ in range(NB)];ps=[];sources=[]
 for i in range(NB):
  phase=PH[i];cy,cz=centers[i];front=rng.choice((-1,0,1));q=rng.randrange(4)
  if fq is not None:q,front=fq[i]
  def point(p):
   x,y,z=p
   for _ in range(q):y,z=-z,y
   return x+front,y+cy,z+cz
  for y,z in ((0,0),(0,1),(0,2),(0,-1),(0,-2),(1,0),(2,0),(-1,0),(-2,0)):ss[i].add(point((0,y,z)))
  for f,y,z in ((0,0,1),(1,0,-1),(3,1,0),(4,-1,0)):
   dp=[sum((t-f)%6 not in (0,1) for t in range(s)) for s in range(6)]
   base=-1 if f<2 else -2
   newdp=[4*((phase+t)//6)+dp[(phase+t)%6]-dp[phase] for t in range(6)]
   ps.append((point((base+dp[phase]-m.DISP[0][phase],y,z)),newdp,(f-phase)%6,i,False))
   out=point((0,-y,-z));origin=point((0,0,0));direction=m.D.index(tuple(a-b for a,b in zip(out,origin)))
   sources.append((point((-1,2*y,2*z)),i,f in (1,4),direction))
 legal=ns['make_legal'](ss,ps,sources)
 if not callable(legal):return None,legal[1]
 if any(not legal(p,i) for i,s in enumerate(ss) for p in s):return None,'mandatory'
 for pp,dp,f,target,sticky in rng.sample(ps,len(ps)):
  recovery={t for t in range(6) if (t-f)%6 not in (0,1)}
  while recovery:
   opts=[]
   for t in recovery:
    for i in range(NB):
     if not S6[i][t]:continue
     for d in m.D[2:]:
      p=m.shift(m.add(pp,d),dp[t]-DISP6[i][t])
      if not legal(p,i):continue
      cover={u for u in recovery if S6[i][u] and sum(abs(a-b) for a,b in zip(m.shift(p,DISP6[i][u]),m.shift(pp,dp[u])))==1}
      distance=min(sum(abs(a-b) for a,b in zip(p,v)) for v in ss[i])
      opts.append((-len(cover),p not in ss[i],distance,rng.random(),p,i,cover))
   if not opts:return None,'pickup'
   *_,p,i,cover=min(opts);ss[i].add(p);recovery-=cover;legal.cache_clear()
 if pickup_only:return ([len(x) for x in ss],0,[set(x) for x in ss]),None
 ys=[c[0] for c in centers];zs=[c[1] for c in centers]
 for i in rng.sample(range(NB),NB):
  while len(m.conn(ss[i]))<len(ss[i]):
   legal.cache_clear();reached=m.conn(ss[i]);targets=ss[i]-reached;pq=[(0,rng.random(),p) for p in reached];heapq.heapify(pq);dist={p:0 for p in reached};prev={};end=None
   while pq:
    cost,_,p=heapq.heappop(pq)
    if cost!=dist[p]:continue
    if p in targets:end=p;break
    if cost>cap-len(ss[i]):continue
    for d in rng.sample(m.D,6):
     v=m.add(p,d)
     if not(-9<=v[0]<=10 and min(ys)-span<=v[1]<=max(ys)+span and min(zs)-span<=v[2]<=max(zs)+span):continue
     if v not in ss[i] and not legal(v,i):continue
     nc=cost+int(v not in ss[i])
     if nc<dist.get(v,10000):dist[v]=nc;prev[v]=p;heapq.heappush(pq,(nc,rng.random(),v))
   if end is None:return None,'route'
   while end not in reached:ss[i].add(end);end=prev[end]
   if len(ss[i])>cap:return None,'cap'
 f=Flyer(rng_state=5,push_limit=1000)
 for p,owner,observer,direction in sources:f._cells[p]=Block.observer(direction,powered=bool(S6[owner][5])) if observer else Block(Kind.REDSTONE_BLOCK)
 for p,dp,phase,target,sticky in ps:
  state=2 if (0-phase)%6==1 else 0;f._cells[p]=Block.piston(0,state=state)
  if state:f._cells[m.shift(p,1)]=Block(Kind.PISTON_ARM)
 for i,s in enumerate(ss):
  for p in s:
   if p in f._cells:return None,'overlap'
   f._cells[p]=Block(K6[i])
 return (f,dict(segments=[sorted(s) for s in ss],counts=list(map(len,ss)))),None
def main():
 name=sys.argv[1];n=int(sys.argv[2]);start=int(sys.argv[3]) if len(sys.argv)>3 else 0
 fq=None
 if name.startswith('L'):
  import json;c,cen,a=json.load(open(HERE/'layouts.json'))[int(name[1:])];centers=[tuple(cen[str(i)]) for i in range(6)];fq=[tuple(a[str(i)]) for i in range(6)]
 else:centers=LAYOUTS[name]
 out=HERE/f'cands_{name}';out.mkdir(exist_ok=True);stats=collections.Counter()
 for seed in range(start,start+n):
  ans,reason=build(seed,centers,fq=fq)
  if ans:
   f,data=ans;f.save(out/f'{name}_s{seed:03}.flyer');stats['routed']+=1;print(seed,'ok',data['counts'],flush=True)
  else:stats[reason]+=1;print(seed,reason,flush=True)
 print(name,dict(stats))
if __name__=='__main__':main()
