"""Refine the new six-body PL21 lead, jointly balancing axial spans and ports.

This is distinct from exhausted three-body safe-router center perturbations.
Reject adhesive counts>15: every simulated candidate aims atPL20 (max24).
"""
from pathlib import Path
import sys,json,csv,random,subprocess
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from search_layouts import generator,checkpoint
BASE=[(0,0),(-1,4),(2,5),(6,6),(6,1),(3,0)]
SPANS=[4,3,4,3,2,4]

def main():
 make=generator();out=HERE/'n4_six_refine';out.mkdir(exist_ok=True);rows=[];seen=set();rng=random.Random(60121)
 for attempt in range(180):
  centers=BASE.copy();spans=SPANS.copy()
  if attempt<24:
   i=attempt//4;dy,dz=((1,0),(-1,0),(0,1),(0,-1))[attempt%4];centers[i]=(centers[i][0]+dy,centers[i][1]+dz)
  elif attempt<48:
   a,b=rng.sample(range(6),2)
   if spans[a]>2 and spans[b]<5:spans[a]-=1;spans[b]+=1
  else:
   for _ in range(rng.randrange(1,4)):
    i=rng.randrange(6);dy,dz=rng.choice(((1,0),(-1,0),(0,1),(0,-1)));centers[i]=(centers[i][0]+dy,centers[i][1]+dz)
   if attempt%2:
    a,b=rng.sample(range(6),2)
    if spans[a]>2 and spans[b]<5:spans[a]-=1;spans[b]+=1
  seed=82084 if attempt<48 else rng.randrange(100000)
  ans=make(4,centers,seed,24,spans);row=dict(attempt=attempt,centers=centers,spans=spans,seed=seed,routed=ans is not None)
  if ans:
   f,counts,(ss,ph)=ans;row['counts']=counts
   if max(counts)<=15 and f.content_hash() not in seen:
    seen.add(f.content_hash());name=f'c{attempt:04}.flyer';f.push_limit=20;f.save(out/name);row.update(file=name,segments=[sorted(s) for s in ss],phases=ph)
  rows.append(row);checkpoint(HERE/'n4_six_refine.manifest.json',rows)
  if (attempt+1)%24==0:print('refine',attempt+1,'target20_candidates',len(seen),flush=True)
 runner=ROOT/'flyers/WIP/experiments/bin/research_runner.exe';p=subprocess.run([str(runner),'screen',str(out),'240','--out',str(HERE/'n4_six_refine.screen.csv')],capture_output=True,text=True);(HERE/'n4_six_refine.screen.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)

if __name__=='__main__':main()
