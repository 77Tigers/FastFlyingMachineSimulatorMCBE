"""Test sticky-pull retractions on the two PL12 three-block deletion near misses."""
from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
base=Flyer.load(ROOT/'flyers/WIP/two_push_crosslayer_pl13.flyer')
sites=sorted(p for p,b in base._cells.items() if b.kind==Kind.PISTON)
out=Path(os.environ['TEMP'])/'n2_sticky_delete';out.mkdir(exist_ok=True)
for pivot in ((16,0,15),(16,1,18)):
 for mask in range(16):
  f=Flyer(rng_state=2,push_limit=12);f._cells=base._cells.copy();del f._cells[pivot]
  for i,p in enumerate(sites):
   if mask>>i&1:f._cells[p]=Block.piston(0,sticky=True)
  f.save(out/f'p{pivot[1]}_{pivot[2]}_m{mask}.flyer')
run=Path(os.environ['TEMP'])/'flyer_batch.exe'
p=subprocess.run([str(run),'80',str(out)],capture_output=True,text=True)
rows=[]
for line in p.stdout.splitlines():
 a=line.split('\t')
 if len(a)>1:
  try:rows.append((int(a[1]),line))
  except:pass
print('top',*sorted(rows,reverse=True)[:32],sep='\n')
