"""Connected-rail deletion search on the new 89-block PL18 seed39 lead."""
from pathlib import Path
import sys,subprocess,re,json,random
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Kind
HERE=Path(__file__).resolve().parent;RUNNER=ROOT/'flyers/WIP/experiments/bin/research_runner.exe'
D=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
def connected(s):
 if not s:return False
 seen={min(s)};stack=list(seen)
 while stack:
  p=stack.pop()
  for d in D:
   q=tuple(a+b for a,b in zip(p,d))
   if q in s and q not in seen:seen.add(q);stack.append(q)
 return seen==s
def components(f):
 groups=[]
 for kind in (Kind.SLIME,Kind.HONEY):
  todo={p for p,b in f._cells.items() if b.kind==kind}
  while todo:
   seen={min(todo)};stack=list(seen)
   while stack:
    p=stack.pop()
    for d in D:
     q=tuple(a+b for a,b in zip(p,d))
     if q in todo and q not in seen:seen.add(q);stack.append(q)
   groups.append(seen);todo-=seen
 return groups
def main():
 out=HERE/'trim_n3';out.mkdir(exist_ok=True)
 f=Flyer.load(HERE/'n3_copies1_s039_pl18.flyer');f.push_limit=100;groups=components(f);log=[]
 for cycle in range(4):
  sites=[p for s in groups for p in s];random.Random(30+cycle).shuffle(sites);removed=0
  for p in sites:
   i=next(i for i,s in enumerate(groups) if p in s)
   if not connected(groups[i]-{p}):continue
   b=f._cells.pop(p);probe=out/'probe.flyer';f.save(probe)
   r=subprocess.run([str(RUNNER),'audit',str(probe),'1000','10'],capture_output=True,text=True)
   text=r.stdout;ok=all(token in text for token in ('distance=300 ','extension_failures=0 ','movement_failures=0','conservation_mismatch_ticks=0 '))
   log.append(dict(cycle=cycle,position=p,accepted=ok,result=text.strip()))
   if ok:groups[i].remove(p);removed+=1;f.save(out/'best.flyer')
   else:f._cells[p]=b
  (out/'results.json').write_text(json.dumps(log,indent=2));print('trim round',cycle,'removed',removed,'cells',len(f._cells),flush=True)
  if removed==0:break
 f.save(out/'best.flyer')
 p=subprocess.run([str(RUNNER),'audit',str(out/'best.flyer'),'10000','10'],capture_output=True,text=True)
 (out/'best_audit.txt').write_text(p.stdout+p.stderr);print(p.stdout.strip(),flush=True)
 load=int(re.search(r'max_successful_action=(\d+)',p.stdout)[1]);f.push_limit=load;f.save(out/f'best_pl{load}.flyer')

if __name__=='__main__':main()
