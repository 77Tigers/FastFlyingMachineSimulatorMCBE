"""Bounded repeated-phase-block ring baselines; original generators unchanged."""
from pathlib import Path
import sys, math, json, subprocess, csv, os
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
HERE=Path(__file__).resolve().parent
source=(ROOT/'flyers/WIP/astra_ringgen_hexsmart.py').read_text()
# Repeat closure spans and permit larger transverse rings, keeping the same temporal router.
source=source[:source.index("if __name__=='__main__':")]
source=source.replace('spans=([3,3,4]*(k//3)) if n==4 and k%3==0 else [3]*(k-1)+[sum(2+min(p,n)-max(0,p-2) for p in ph)-3*(k-1)]','spans=([3,3,4]*(k//3)) if n==4 else ([3,3,3,3,4]*(k//5))')
source=source.replace('and -5<=q[1]<=10 and -5<=q[2]<=10','and min(c[0] for c in centers)-4<=q[1]<=max(c[0] for c in centers)+4 and min(c[1] for c in centers)-4<=q[2]<=max(c[1] for c in centers)+4')
ns={};exec(compile(source,str(HERE/'derived_generator.py'),'exec'),ns)
(HERE/'derived_generator.py').write_text(source)
runner=HERE.parents[3]/'target/release/fastflyer-research.exe'
rows=[];meta=[]
for n in (3,4):
 for copies in (1,2,4):
  k=(5 if n==3 else 3)*copies
  if copies==1: centers=[(0,0),(0,4),(3,5),(5,2),(3,-1)] if n==3 else [(0,0),(0,4),(3,1)]
  elif n==4 and copies==2: centers=[(0,0),(0,4),(2,6),(6,6),(6,2),(4,0)]
  else:
   r=4/(2*math.sin(math.pi/k)); centers=[(round(r*math.cos(2*math.pi*i/k)),round(r*math.sin(2*math.pi*i/k))) for i in range(k)]
  for seed in range(8):
   ans=ns['make'](n,centers,seed,100)
   if ans is None:
    rows.append(dict(n=n,copies=copies,seed=seed,status='route_rejected')); continue
   f,counts,(ss,ph)=ans
   path=HERE/f'n{n}_copies{copies}_s{seed}.flyer';f.save(path)
   p=subprocess.run([str(runner),'audit',str(path),'160',str(2*(n+2))],capture_output=True,text=True)
   rows.append(dict(n=n,copies=copies,seed=seed,status='simulated',output=p.stdout.strip()))
   minxs=[min(q[0] for q in s) for s in ss]
   reach=[]
   for i in range(k):
    ds=[]
    for t in range(n+2):
     def displacement(j):
      cyc,p=divmod(ph[j]+t,n+2)
      return n*cyc+min(p,n)-min(ph[j],n)
     ds.append(minxs[i]+displacement(i)-minxs[(i-1)%k]-displacement((i-1)%k))
    reach.append(dict(carrier=i,previous=(i-1)%k,min_delta=min(ds),max_delta=max(ds),deltas=ds,all_phases_at_least_as_far_back=max(ds)<=0))
   meta.append(dict(n=n,copies=copies,seed=seed,path=str(path),centers=centers,phases=ph,sticky_counts=counts,minxs=minxs,reach=reach))
   print(n,copies,seed,p.stdout.strip(),flush=True)
   if 'distance=' in p.stdout and f'distance={160*n//(2*(n+2))}' in p.stdout and 'conservation_mismatch_ticks=0' in p.stdout:
    p2=subprocess.run([str(runner),'audit',str(path),'10000',str(2*(n+2))],capture_output=True,text=True)
    (HERE/f'n{n}_copies{copies}_s{seed}_full.txt').write_text(p2.stdout+p2.stderr)
    rows[-1]['full']=p2.stdout.strip();break
  (HERE/'chain_results.json').write_text(json.dumps(rows,indent=2));(HERE/'chain_metadata.json').write_text(json.dumps(meta,indent=2))
