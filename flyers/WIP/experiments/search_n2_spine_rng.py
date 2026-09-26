from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer
src=Flyer.load(ROOT/'flyers/WIP/experiments/n2_spine/v0.flyer')
out=Path(os.environ['TEMP'])/'n2_spine_rng';out.mkdir(exist_ok=True)
for seed in range(256):
 f=Flyer(rng_state=seed,push_limit=20);f._cells=src._cells.copy();f.save(out/f's{seed}.flyer')
run=Path(os.environ['TEMP'])/'flyer_batch.exe'
p=subprocess.run([str(run),'80',str(out)],capture_output=True,text=True)
rows=[]
for line in p.stdout.splitlines():
 a=line.split('\t')
 if len(a)>1:
  try:rows.append((int(a[1]),line))
  except:pass
print('top',*sorted(rows,reverse=True)[:30],sep='\n')
