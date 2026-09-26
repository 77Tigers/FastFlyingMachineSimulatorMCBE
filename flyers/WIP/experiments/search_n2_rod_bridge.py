"""Try to route the front spine around a return power rod moved into the old honey cell."""
from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
base=Flyer.load(ROOT/'flyers/WIP/two_push_crosslayer_pl13.flyer')
front=[p for p,b in base._cells.items() if b.kind==Kind.SLIME and p!=(16,1,16)]
out=Path(os.environ['TEMP'])/'n2_rod_bridge';out.mkdir(exist_ok=True)
for old in front:
 for x in range(14,18):
  for y in range(-1,3):
   for z in range(14,20):
    q=(x,y,z)
    if q in base._cells or q==old:continue
    f=Flyer(rng_state=2,push_limit=12);f._cells=base._cells.copy()
    for p in [(16,3,16),(16,1,16),old]:del f._cells[p]
    f._cells[(16,2,16)]=Block.rod(0);f._cells[q]=Block(Kind.SLIME)
    try:f.save(out/f'r{old[0]}_{old[1]}_{old[2]}_a{x}_{y}_{z}.flyer')
    except:pass
batch=Path(os.environ['TEMP'])/'flyer_batch.exe'
p=subprocess.run([str(batch),'80',str(out)],capture_output=True,text=True)
rows=[]
for line in p.stdout.splitlines():
 parts=line.split('\t')
 if len(parts)>1:
  try:rows.append((int(parts[1]),line))
  except:pass
print('tested',len(rows),'top',*sorted(rows,reverse=True)[:40],sep='\n')
