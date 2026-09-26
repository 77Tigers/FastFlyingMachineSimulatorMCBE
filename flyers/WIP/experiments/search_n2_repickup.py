"""Search alternate one-cell pickup after removing overloaded honey cells."""
from pathlib import Path
import os,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
base=Flyer.load(ROOT/'flyers/WIP/two_push_crosslayer_pl13.flyer')
out=Path(os.environ['TEMP'])/'n2_repickup';out.mkdir(exist_ok=True)
for rem in ((16,0,15),(16,1,18)):
 for x in range(14,19):
  for y in range(-1,5):
   for z in range(13,21):
    q=(x,y,z)
    if q==rem or q in base._cells:continue
    f=Flyer(rng_state=2,push_limit=12);f._cells=base._cells.copy();del f._cells[rem];f._cells[q]=Block(Kind.HONEY)
    try:f.save(out/f'r{rem[1]}_{rem[2]}_a{x}_{y}_{z}.flyer')
    except:pass
batch=Path(os.environ['TEMP'])/'flyer_batch.exe'
p=subprocess.run([str(batch),'80',str(out)],capture_output=True,text=True)
rows=[]
for line in p.stdout.splitlines():
 fields=line.split('\t')
 if len(fields)>=2:
  try:rows.append((int(fields[1]),line))
  except:pass
print('tested',len(rows),'top',*sorted(rows,reverse=True)[:30],sep='\n')
