from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
BASE=Flyer.load(ROOT/'flyers/WIP/two_push_crosslayer_pl13.flyer')
OUT=Path(__file__).resolve().parent/'hybrid_del';OUT.mkdir(exist_ok=True)
RUN=Path(os.environ['TEMP'])/'flyer_measure.exe'
front=[p for p,b in BASE._cells.items() if b.kind==Kind.SLIME]
rear=[p for p,b in BASE._cells.items() if b.kind in (Kind.HONEY,Kind.ROD)]
rows=[]
for a in front:
 for b in rear:
  f=Flyer(rng_state=2,push_limit=12);f._cells=BASE._cells.copy()
  del f._cells[(15,2,17)]
  f._cells[(17,1,18)]=Block.piston(1,sticky=True)
  f._cells[(18,1,17)]=Block.observer(4)
  del f._cells[a];del f._cells[b]
  name=f'f{a[0]}_{a[1]}_{a[2]}_b{b[0]}_{b[1]}_{b[2]}'
  p=OUT/f'{name}.flyer'
  try:f.save(p)
  except:continue
  q=subprocess.run([str(RUN),'80',str(p)],capture_output=True,text=True)
  try:score=int(q.stdout.strip().split('\t')[1])
  except:score=-1
  rows.append((score,name))
  if score>=20:print(score,name,flush=True)
print('top',*sorted(rows,reverse=True)[:25],sep='\n')
