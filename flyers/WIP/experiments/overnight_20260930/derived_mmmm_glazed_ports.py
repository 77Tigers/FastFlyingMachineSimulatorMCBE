"""Four coplanar drive ports per mmwmmw body; physically route recovery contacts."""
from pathlib import Path
import sys,json,random,heapq,collections,subprocess,importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
spec=importlib.util.spec_from_file_location('m',HERE/'derived_mmw.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.S=((1,1,1,1,0,0),(0,0,1,1,1,1),(1,1,0,0,1,1))*2
m.DISP=[[sum(word[:t]) for t in range(7)] for word in m.S];m.K=[Kind.SLIME if i%2==0 else Kind.HONEY for i in range(6)]
source=(HERE/'mixed_role_ring_legal.py').read_text().replace('range(5)','range(6)').replace('%5','%6')
source=source.replace('observer,direction in sources','observer,direction,rod in sources')
source=source.replace('else Block(Kind.REDSTONE_BLOCK)','else (Block.rod(direction) if rod else Block(Kind.REDSTONE_BLOCK))')
source=source.replace('  w={}','  w={shift(p,DISP[owner][t]):Block(Kind.GLAZED_TERRACOTTA) for p,owner in GLAZED}')
source=source.replace('if observer and S[owner][(t-1)%6] and','if (rod or (observer and S[owner][(t-1)%6])) and')
where=source.index(' @functools.lru_cache(None)')
source=source[:where]+""" for t in range(6):
  for pp,dp,f,target,sticky in ps:
   if t==f:continue
   base=shift(pp,dp[t])
   for gp,gowner in GLAZED:
    solid=shift(gp,DISP[gowner][t])
    if sum(abs(a-b) for a,b in zip(base,solid))!=1:continue
    for rp,owner,observer,direction,rod in sources:
     if (rod or (observer and S[owner][(t-1)%6])) and add(shift(rp,DISP[owner][t]),D[direction])==solid:return None,'glazed_cross_power'
"""+source[where:]
ns=m.__dict__.copy();ns['GLAZED']=[];exec(compile(source,'mmmm_glazed_legal','exec'),ns)
(HERE/'mmmm_glazed_legal.py').write_text(source)
def build(seed,centers):
 rng=random.Random(seed);ss=[set() for _ in range(6)];ps=[];sources=[];glazed=[];ns['GLAZED']=glazed
 for i,phase in enumerate((0,4,2)*2):
  cy,cz=centers[i];front=rng.choice((-1,0,1));q=rng.randrange(4)
  def point(p):
   x,y,z=p
   for _ in range(q):y,z=-z,y
   return x+front,y+cy,z+cz
  for y,z in ((0,0),(0,1),(0,2),(0,-1),(0,-2),(1,0),(-1,0)):ss[i].add(point((0,y,z)))
  for f,y,z in ((0,0,1),(1,0,-1),(2,1,0),(3,-1,0)):
   dp=[sum((t-f)%6 not in (0,1) for t in range(s)) for s in range(6)]
   base=-1
   newdp=[4*((phase+t)//6)+dp[(phase+t)%6]-dp[phase] for t in range(6)]
   ps.append((point((base+dp[phase]-m.DISP[0][phase],y,z)),newdp,(f-phase)%6,i,False))
   out=point((0,-y,-z));origin=point((0,0,0));direction=m.D.index(tuple(a-b for a,b in zip(out,origin)))
   if f<2:sources.append((point((-1,2*y,2*z)),i,f==1,direction,False))
   else:
    owner=(i+1)%6;sourcex=1+m.DISP[1][phase]-m.DISP[0][phase]
    glazed.append((point((sourcex,2*y,2*z)),owner))
    ss[owner].add(point((sourcex-1,2*y,2*z)));ss[owner].add(point((sourcex-1,3*y,3*z)))
    sources.append((point((sourcex,3*y,3*z)),owner,f==3,direction,f==2))
 legal=ns['make_legal'](ss,ps,sources)
 if not callable(legal):return None,legal[1]
 if any(not legal(p,i) for i,s in enumerate(ss) for p in s):return None,'mandatory'
 for pp,dp,f,target,sticky in rng.sample(ps,len(ps)):
  recovery={t for t in range(6) if (t-f)%6 not in (0,1)}
  while recovery:
   opts=[]
   for t in recovery:
    for i in range(6):
     if not m.S[i][t]:continue
     for d in m.D[2:]:
      p=m.shift(m.add(pp,d),dp[t]-m.DISP[i][t])
      if not legal(p,i):continue
      cover={u for u in recovery if m.S[i][u] and sum(abs(a-b) for a,b in zip(m.shift(p,m.DISP[i][u]),m.shift(pp,dp[u])))==1}
      distance=min(sum(abs(a-b) for a,b in zip(p,v)) for v in ss[i])
      opts.append((-len(cover),p not in ss[i],distance,rng.random(),p,i,cover))
   if not opts:return None,'pickup'
   *_,p,i,cover=min(opts);ss[i].add(p);recovery-=cover;legal.cache_clear()
 for i in rng.sample(range(6),6):
  while len(m.conn(ss[i]))<len(ss[i]):
   legal.cache_clear();reached=m.conn(ss[i]);targets=ss[i]-reached;pq=[(0,rng.random(),p) for p in reached];heapq.heapify(pq);dist={p:0 for p in reached};prev={};end=None
   while pq:
    cost,_,p=heapq.heappop(pq)
    if cost!=dist[p]:continue
    if p in targets:end=p;break
    if cost>50-len(ss[i]):continue
    for d in rng.sample(m.D,6):
     v=m.add(p,d)
     if not(-6<=v[0]<=7 and -5<=v[1]<=22 and -5<=v[2]<=22):continue
     if v not in ss[i] and not legal(v,i):continue
     nc=cost+int(v not in ss[i])
     if nc<dist.get(v,10000):dist[v]=nc;prev[v]=p;heapq.heappush(pq,(nc,rng.random(),v))
   if end is None:return None,'route'
   while end not in reached:ss[i].add(end);end=prev[end]
   if len(ss[i])>50:return None,'cap'
 assert all(len(m.conn(body))==len(body) for body in ss), 'unrouted body'
 f=Flyer(rng_state=5,push_limit=1000)
 for p,owner in glazed:f._cells[p]=Block(Kind.GLAZED_TERRACOTTA)
 for p,owner,observer,direction,rod in sources:f._cells[p]=Block.observer(direction,powered=bool(m.S[owner][5])) if observer else (Block.rod(direction) if rod else Block(Kind.REDSTONE_BLOCK))
 for p,dp,phase,target,sticky in ps:
  state=2 if (0-phase)%6==1 else 0;f._cells[p]=Block.piston(0,state=state)
  if state:f._cells[m.shift(p,1)]=Block(Kind.PISTON_ARM)
 for i,s in enumerate(ss):
  for p in s:assert p not in f._cells;f._cells[p]=Block(m.K[i])
 return (f,dict(segments=[sorted(s) for s in ss],pistons=ps,sources=sources,glazed=glazed,counts=list(map(len,ss)))),None
def main():
 out=HERE/'mmmm_glazed_compact_short_candidates';out.mkdir(exist_ok=True);stats=collections.Counter();manifest=[]
 for name,centers in [('hex7',[(0,3),(0,10),(6,14),(12,10),(12,3),(6,-1)]),('hex8',[(0,4),(0,12),(7,16),(14,12),(14,4),(7,0)])]:
  for seed in range(8):
   ans,reason=build(seed,centers)
   if ans:
    f,data=ans;file=f'{name}_s{seed:03}.flyer';f.save(out/file);data.update(file=file,seed=seed,centers=centers);manifest.append(data);stats['routed']+=1
   else:stats[reason]+=1
   (HERE/'mmmm_glazed_compact_short_manifest.json').write_text(json.dumps(dict(stats=stats,candidates=manifest),indent=2));print(name,seed,dict(stats),flush=True)
 runner=ROOT/'target/release/fastflyer-research.exe';r=subprocess.run([str(runner),'screen',str(out),'240','--out',str(HERE/'mmmm_glazed_compact_short_screen.csv')],capture_output=True,text=True);(HERE/'mmmm_glazed_compact_short_screen.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)
if __name__=='__main__':main()
