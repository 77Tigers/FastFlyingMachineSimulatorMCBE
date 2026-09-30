"""Four coplanar drive ports per mmwmmw body; physically route recovery contacts."""
from pathlib import Path
import sys,json,random,heapq,collections,subprocess,importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
spec=importlib.util.spec_from_file_location('m',HERE/'derived_mmw.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source=(HERE/'mixed_role_ring_legal.py').read_text().replace('range(5)','range(6)').replace('%5','%6')
m.S=((1,1,1,1,0,0),(0,0,1,1,1,1),(1,1,0,0,1,1));m.DISP=[[sum(word[:t]) for t in range(7)] for word in m.S]
ns=m.__dict__.copy();exec(compile(source,'mmmm_planar_legal','exec'),ns)
def build(seed,centers):
 rng=random.Random(seed);ss=[set() for _ in range(3)];ps=[];sources=[]
 for i,phase in enumerate((0,4,2)):
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
   oldowner=0 if f<2 else 1;owner=i if f<2 else (i+1)%3
   sourcex=(-1 if f<2 else 1)+m.DISP[oldowner][phase]-m.DISP[0][phase]
   sources.append((point((sourcex,2*y,2*z)),owner,f in (1,3),direction))
 legal=ns['make_legal'](ss,ps,sources)
 if not callable(legal):return None,legal[1]
 # Each foreign source gets a physical helper-owned sticky attachment.
 for p,owner,observer,direction in sources:
  if any(m.add(p,d) in ss[owner] for d in m.D):continue
  options=[m.add(p,d) for d in m.D if legal(m.add(p,d),owner)]
  if not options:return None,'source_attachment'
  q=min(options,key=lambda q:(min(sum(abs(a-b) for a,b in zip(q,v)) for v in ss[owner]),rng.random()));ss[owner].add(q);legal.cache_clear()
 witnesses=[]
 def capture(frame,event,arg):
  if frame.f_code.co_name=='legal' and event=='return' and arg is False:
   witnesses.append(dict(line=frame.f_lineno,locals={k:v for k,v in frame.f_locals.items() if k in ('p','i','t','q','r','j','delta','pp','f','target','rp','owner','observer','direction')}))
  return capture
 sys.settrace(capture)
 bad=[(i,p) for i,body in enumerate(ss) for p in body if not legal(p,i)]
 sys.settrace(None)
 if bad:
  (HERE/'mmmm_planar_mandatory_witness.json').write_text(json.dumps(dict(bad=bad,witnesses=witnesses,segments=[sorted(x) for x in ss],pistons=ps,sources=sources),indent=2));return None,'mandatory'

 for pp,dp,f,target,sticky in rng.sample(ps,len(ps)):
  recovery={t for t in range(6) if (t-f)%6 not in (0,1)}
  while recovery:
   opts=[]
   for t in recovery:
    for i in range(3):
     if not m.S[i][t]:continue
     for d in m.D[2:]:
      p=m.shift(m.add(pp,d),dp[t]-m.DISP[i][t])
      if not legal(p,i):continue
      cover={u for u in recovery if m.S[i][u] and sum(abs(a-b) for a,b in zip(m.shift(p,m.DISP[i][u]),m.shift(pp,dp[u])))==1}
      distance=min(sum(abs(a-b) for a,b in zip(p,v)) for v in ss[i])
      opts.append((-len(cover),p not in ss[i],distance,rng.random(),p,i,cover))
   if not opts:return None,'pickup'
   *_,p,i,cover=min(opts);ss[i].add(p);recovery-=cover;legal.cache_clear()
 for i in rng.sample(range(3),3):
  while len(m.conn(ss[i]))<len(ss[i]):
   legal.cache_clear();reached=m.conn(ss[i]);targets=ss[i]-reached;pq=[(0,rng.random(),p) for p in reached];heapq.heapify(pq);dist={p:0 for p in reached};prev={};end=None
   while pq:
    cost,_,p=heapq.heappop(pq)
    if cost!=dist[p]:continue
    if p in targets:end=p;break
    if cost>50-len(ss[i]):continue
    for d in rng.sample(m.D,6):
     v=m.add(p,d)
     if not(-6<=v[0]<=7 and -5<=v[1]<=12 and -5<=v[2]<=10):continue
     if v not in ss[i] and not legal(v,i):continue
     nc=cost+int(v not in ss[i])
     if nc<dist.get(v,10000):dist[v]=nc;prev[v]=p;heapq.heappush(pq,(nc,rng.random(),v))
   if end is None:return None,'route'
   while end not in reached:ss[i].add(end);end=prev[end]
   if len(ss[i])>50:return None,'cap'
 f=Flyer(rng_state=5,push_limit=1000)
 for p,owner,observer,direction in sources:f._cells[p]=Block.observer(direction,powered=bool(m.S[owner][5])) if observer else Block(Kind.REDSTONE_BLOCK)
 for p,dp,phase,target,sticky in ps:
  state=2 if (0-phase)%6==1 else 0;f._cells[p]=Block.piston(0,state=state)
  if state:f._cells[m.shift(p,1)]=Block(Kind.PISTON_ARM)
 for i,s in enumerate(ss):
  for p in s:assert p not in f._cells;f._cells[p]=Block(m.K[i])
 return (f,dict(segments=[sorted(s) for s in ss],pistons=ps,sources=sources,counts=list(map(len,ss)))),None
def main():
 out=HERE/'mmmm_planar_candidates';out.mkdir(exist_ok=True);stats=collections.Counter();manifest=[]
 for name,centers in [('medium',[(0,0),(0,5),(4,2)]),('safe',[(0,0),(0,6),(5,3)])]:
  for seed in range(16):
   ans,reason=build(seed,centers)
   if ans:
    f,data=ans;file=f'{name}_s{seed:03}.flyer';f.save(out/file);data.update(file=file,seed=seed,centers=centers);manifest.append(data);stats['routed']+=1
   else:stats[reason]+=1
   (HERE/'mmmm_planar_manifest.json').write_text(json.dumps(dict(stats=stats,candidates=manifest),indent=2));print(name,seed,dict(stats),flush=True)
 runner=ROOT/'flyers/WIP/experiments/bin/research_runner.exe';r=subprocess.run([str(runner),'screen',str(out),'240','--out',str(HERE/'mmmm_planar_screen.csv')],capture_output=True,text=True);(HERE/'mmmm_planar_screen.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)
ans,reason=build(0,[(0,0),(0,6),(5,3)]);print('diagnostic',reason)
