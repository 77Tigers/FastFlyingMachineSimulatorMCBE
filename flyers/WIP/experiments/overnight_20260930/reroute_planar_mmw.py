"""Reconnect fixed planar timing ports with smaller rails; exact-cycle gate."""
from pathlib import Path
import sys,json,random,heapq,subprocess,re
from mmw_planar import build,m,ns
from fastflyer import Flyer,Block
H=Path(__file__).resolve().parent;RUNNER=H.parents[3]/'target/release/fastflyer-research.exe'
def main():
 g=json.loads((H/'trim_planar_mmw/geometry.json').read_text());ss=[set(map(tuple,s)) for s in g['segments']];ps=g['pistons'];sources=g['sources'];ports=[]
 line=next(i for i,x in enumerate((H/'mmw_planar.py').read_text().splitlines(),1) if 'for i in rng.sample(range(3),3)' in x)
 class Captured(Exception):pass
 def capture(frame,event,arg):
  if frame.f_code is build.__code__ and event=='line' and frame.f_lineno==line:ports.extend(set(s) for s in frame.f_locals['ss']);raise Captured()
  return capture
 sys.settrace(capture)
 try:build(1,[(0,0),(0,6),(5,3)])
 except Captured:pass
 finally:sys.settrace(None)
 assert len(ports)==3
 # Connected pruning already removed redundant selected contacts. Keep only
 # surviving ports; every reconstructed body must pass the exact simulator.
 ports=[ports[i]&ss[i] for i in range(3)]
 out=H/'reroute_planar_mmw';out.mkdir(exist_ok=True);records=[];best=36
 def flyer(sets):
  f=Flyer(rng_state=5,push_limit=1000)
  for p,owner,observer,direction in sources:f._cells[tuple(p)]=Block.observer(direction,powered=bool(m.S[owner][5])) if observer else Block(m.Kind.REDSTONE_BLOCK)
  for p,dp,phase,target,sticky in ps:
   state=2 if (0-phase)%6==1 else 0;f._cells[tuple(p)]=Block.piston(0,state=state)
   if state:f._cells[m.shift(p,1)]=Block(m.Kind.PISTON_ARM)
  for i,s in enumerate(sets):
   for p in s:assert p not in f._cells;f._cells[p]=Block(m.K[i])
  return f
 for round in range(2):
  for i in sorted(range(3),key=lambda i:-len(ss[i])):
   for seed in range(24):
    rng=random.Random(1000*round+100*i+seed);candidate=ports[i].copy();legal=ns['make_legal'](ss,ps,sources);assert callable(legal)
    failed=False
    while len(m.conn(candidate))<len(candidate):
     reached=m.conn(candidate);targets=candidate-reached;pq=[(0,rng.random(),p) for p in reached];heapq.heapify(pq);dist={p:0 for p in reached};prev={};end=None
     while pq:
      cost,_,p=heapq.heappop(pq)
      if cost!=dist[p]:continue
      if p in targets:end=p;break
      if cost>len(ss[i])-len(candidate):continue
      for d in rng.sample(m.D,6):
       v=m.add(p,d)
       if not(-6<=v[0]<=7 and -5<=v[1]<=12 and -5<=v[2]<=10):continue
       if v not in candidate and not legal(v,i):continue
       nc=cost+int(v not in candidate)
       if nc<dist.get(v,10000):dist[v]=nc;prev[v]=p;heapq.heappush(pq,(nc,rng.random(),v))
     if end is None:failed=True;break
     while end not in reached:candidate.add(end);end=prev[end]
    if failed or len(candidate)>=len(ss[i]):continue
    trial=ss.copy();trial[i]=candidate;f=flyer(trial);probe=out/'probe.flyer';f.save(probe)
    r=subprocess.run([str(RUNNER),'verify',str(probe),'240','--period','12','--advance','4'],capture_output=True,text=True);load=int(re.search(r'max_successful_action=(\d+)',r.stdout)[1]);ok=r.returncode==0 and load<=best
    records.append(dict(round=round,body=i,seed=seed,old=len(ss[i]),new=len(candidate),accepted=ok,result=r.stdout.strip()))
    if ok:ss=trial;best=load;f.save(out/'best.flyer');print('accepted',round,i,seed,list(map(len,ss)),best,flush=True)
    (out/'results.json').write_text(json.dumps(records,indent=2))
 f=flyer(ss);f.save(out/'best.flyer');(out/'geometry.json').write_text(json.dumps(dict(segments=[sorted(s) for s in ss],pistons=ps,sources=sources),indent=2))
 r=subprocess.run([str(RUNNER),'verify',str(out/'best.flyer'),'10000','--period','12','--advance','4'],capture_output=True,text=True);(out/'diagnostic_full.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True);assert r.returncode==0
 f.push_limit=int(re.search(r'max_successful_action=(\d+)',r.stdout)[1]);f.save(H/f'mmw_planar_reroute_pl{f.push_limit}.flyer')
if __name__=='__main__':main()
