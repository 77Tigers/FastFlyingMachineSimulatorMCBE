"""One-cell pickup repair around the sticky-pull near miss."""
from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
src=Flyer.load(Path(os.environ['TEMP'])/'n2_sticky_delete/p0_15_m3.flyer')
out=Path(os.environ['TEMP'])/'n2_sticky_add';out.mkdir(exist_ok=True)
for x in range(14,19):
 for y in range(-1,5):
  for z in range(13,21):
   q=(x,y,z)
   if q in src._cells:continue
   for k in (Kind.HONEY,Kind.SLIME):
    f=Flyer(rng_state=2,push_limit=12);f._cells=src._cells.copy();f._cells[q]=Block(k)
    try:f.save(out/f'x{x}y{y}z{z}k{int(k)}.flyer')
    except:pass
run=Path(os.environ['TEMP'])/'flyer_batch.exe'
p=subprocess.run([str(run),'160',str(out)],capture_output=True,text=True)
rows=[]
for line in p.stdout.splitlines():
 a=line.split('\t')
 if len(a)>1:
  try:rows.append((int(a[1]),line))
  except:pass
print('tested',len(rows),'top',*sorted(rows,reverse=True)[:40],sep='\n')
