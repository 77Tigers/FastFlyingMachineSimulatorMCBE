"""Compact four-carrier pure-push N2 ring layouts at PL12."""
from pathlib import Path
import os,sys,subprocess,time
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from flyers.WIP.astra_ringgen_safe import make
out=Path(os.environ['TEMP'])/'n2_fourseg_compact';out.mkdir(exist_ok=True)
rows=[];t=time.monotonic()
for y in (2,3,4):
 for z in (2,3,4):
  for seed in range(12):
   ans=make(2,[(0,0),(0,z),(y,z),(y,0)],seed,12)
   if ans is None:continue
   f,counts,_=ans;p=out/f'y{y}z{z}_s{seed}.flyer';f.save(p);rows.append((p.name,counts))
print('generated',len(rows),'minmax',min((max(c) for _,c in rows),default=-1),'seconds',round(time.monotonic()-t,1),flush=True)
run=Path(os.environ['TEMP'])/'flyer_batch.exe'
p=subprocess.run([str(run),'120',str(out)],capture_output=True,text=True)
scores=[]
for line in p.stdout.splitlines():
 a=line.split('\t')
 if len(a)>1:
  try:scores.append((int(a[1]),line))
  except:pass
print('top',*sorted(scores,reverse=True)[:25],sep='\n')
