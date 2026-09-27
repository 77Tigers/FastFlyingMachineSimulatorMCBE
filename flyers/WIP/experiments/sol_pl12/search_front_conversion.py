from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
BASE=Flyer.load(ROOT/'flyers/WIP/experiments/sol_pl12/rear_route/lead1_frontdel_pl12.flyer')
OUT=Path(__file__).resolve().parent/'front_conversion';OUT.mkdir(exist_ok=True)
RUN=Path(os.environ['TEMP'])/'flyer_measure.exe'
opts=[Kind.HONEY,Kind.GLASS,Kind.GLAZED_TERRACOTTA,Kind.REDSTONE_BLOCK,Kind.SMOOTH_STONE]
rows=[]
for p,b in BASE._cells.items():
 if b.kind!=Kind.SLIME:continue
 for kind in opts:
  f=Flyer(rng_state=2,push_limit=12);f._cells=BASE._cells.copy();f._cells[p]=Block(kind)
  name=f'{p[0]}_{p[1]}_{p[2]}_{kind.name}'
  q=OUT/f'{name}.flyer'
  try:f.save(q)
  except:continue
  r=subprocess.run([str(RUN),'1000',str(q)],capture_output=True,text=True)
  try:s=int(r.stdout.strip().split('\t')[1])
  except:s=-1
  rows.append((s,name))
  if s>=20:print(s,name,flush=True)
print(*sorted(rows,reverse=True)[:20],sep='\n')
