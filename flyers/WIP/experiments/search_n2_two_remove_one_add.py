"""Alternate honey/rod pickup route around the two exposed PL12 near misses."""
from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
base=Flyer.load(ROOT/'flyers/WIP/two_push_crosslayer_pl13.flyer')
out=Path(os.environ['TEMP'])/'n2_two_remove_one_add';out.mkdir(exist_ok=True)
rems=[p for p,b in base._cells.items() if b.kind in (Kind.HONEY,Kind.ROD)]
count=0
for pivot in ((16,0,15),(16,1,18)):
 for other in rems:
  if other==pivot:continue
  for x in range(15,19):
   for y in range(-1,5):
    for z in range(14,20):
     q=(x,y,z)
     if q in base._cells or q in (pivot,other):continue
     f=Flyer(rng_state=2,push_limit=12);f._cells=base._cells.copy();del f._cells[pivot];del f._cells[other]
     f._cells[q]=Block(Kind.HONEY)
     try:f.save(out/f'p{pivot[1]}_{pivot[2]}_r{other[0]}_{other[1]}_{other[2]}_a{x}_{y}_{z}.flyer');count+=1
     except:pass
batch=Path(os.environ['TEMP'])/'flyer_batch.exe'
p=subprocess.run([str(batch),'80',str(out)],capture_output=True,text=True)
rows=[]
for line in p.stdout.splitlines():
 fields=line.split('\t')
 if len(fields)>=2:
  try:rows.append((int(fields[1]),line))
  except:pass
print('generated',count,'tested',len(rows),'top',*sorted(rows,reverse=True)[:30],sep='\n')
