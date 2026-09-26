"""Repair deletion near misses through a second coordinated material change."""
from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
base=Flyer.load(ROOT/'flyers/WIP/two_push_crosslayer_pl13.flyer')
out=Path(os.environ['TEMP'])/'n2_conversion';out.mkdir(exist_ok=True)
for pivot in ((16,0,15),(16,1,18)):
 for pos,b in base._cells.items():
  if pos==pivot or b.kind not in (Kind.HONEY,Kind.SLIME,Kind.REDSTONE_BLOCK,Kind.ROD):continue
  for kind in (Kind.HONEY,Kind.SLIME,Kind.GLAZED_TERRACOTTA,Kind.REDSTONE_BLOCK):
   if b.kind==kind:continue
   f=Flyer(rng_state=2,push_limit=12);f._cells=base._cells.copy();del f._cells[pivot];f._cells[pos]=Block(kind)
   try:f.save(out/f'p{pivot[1]}_{pivot[2]}_c{pos[0]}_{pos[1]}_{pos[2]}_{kind.name}.flyer')
   except:pass
batch=Path(os.environ['TEMP'])/'flyer_batch.exe'
p=subprocess.run([str(batch),'80',str(out)],capture_output=True,text=True)
rows=[]
for line in p.stdout.splitlines():
 fields=line.split('\t')
 if len(fields)>=2:
  try:rows.append((int(fields[1]),line))
  except:pass
print('tested',len(rows),'top',*sorted(rows,reverse=True)[:40],sep='\n')
