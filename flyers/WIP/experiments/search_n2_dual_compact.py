"""Two coupled six-block observer engines, arranged in a small 3D grid."""
from pathlib import Path
import os,sys,subprocess
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
unit=Flyer.load(ROOT/'flyers/bank/pl12/compact_slime.flyer')
out=Path(os.environ['TEMP'])/'n2_dual_compact';out.mkdir(exist_ok=True)
for dx in range(-3,4):
 for dy in range(-2,3):
  for dz in range(-3,4):
   if (dx,dy,dz)==(0,0,0):continue
   for material in (Kind.SLIME,Kind.HONEY):
    for pulse in (0,1):
     for mirror in (0,1):
      f=Flyer(rng_state=2,push_limit=12);f._cells=unit._cells.copy();valid=True
      for (x,y,z),b in unit._cells.items():
       q=(x+dx,y+dy,(1-z if mirror else z)+dz)
       if q in f._cells:valid=False;break
       if b.kind==Kind.SLIME:b=Block(material)
       elif b.kind==Kind.OBSERVER:b=Block.observer(b.direction,powered=(not b.powered if pulse else b.powered))
       f._cells[q]=b
      if not valid:continue
      try:f.save(out/f'x{dx}y{dy}z{dz}_m{int(material)}p{pulse}r{mirror}.flyer')
      except:pass
run=Path(os.environ['TEMP'])/'flyer_batch.exe'
p=subprocess.run([str(run),'80',str(out)],capture_output=True,text=True)
scores=[]
for line in p.stdout.splitlines():
 a=line.split('\t')
 if len(a)>1:
  try:scores.append((int(a[1]),line))
  except:pass
print('tested',len(scores),'top',*sorted(scores,reverse=True)[:35],sep='\n')
