"""Bounded reduced-contact two-carrier topology screen."""
from pathlib import Path
import os,sys,subprocess,time,csv
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'flyers/WIP/experiments'))
from n2_maskgen import make
out=Path(os.environ['TEMP'])/'n2_masks';out.mkdir(exist_ok=True)
rows=[];start=time.monotonic()
for y,z in [(0,2),(0,3),(0,4),(1,2),(1,3),(1,4),(2,2),(2,3),(3,1),(3,2),(4,0)]:
 for seed in range(5):
  for fm in (3,5,6,7):
   for rm in (3,5,6,7):
    ans=make(2,[(0,0),(y,z)],seed,12,fm,rm)
    if not ans:continue
    f,counts,_=ans
    p=out/f'y{y}z{z}_s{seed}_f{fm}r{rm}.flyer';f.save(p)
    rows.append((p.name,*counts))
print('generated',len(rows),'seconds',round(time.monotonic()-start,1),flush=True)
batch=Path(os.environ['TEMP'])/'flyer_batch.exe'
p=subprocess.run([str(batch),'80',str(out)],capture_output=True,text=True)
scores=[]
for line in p.stdout.splitlines():
 parts=line.split('\t')
 if len(parts)>1:
  try:scores.append((int(parts[1]),line))
  except:pass
print('top',*sorted(scores,reverse=True)[:35],sep='\n')
