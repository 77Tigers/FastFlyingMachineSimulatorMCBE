from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
BASE=Flyer.load(ROOT/'flyers/WIP/two_push_crosslayer_pl13.flyer')
OUT=Path(__file__).resolve().parent/'hybrid';OUT.mkdir(exist_ok=True)
RUN=Path(os.environ['TEMP'])/'flyer_measure.exe'
for rem in [None]+[p for p,b in BASE._cells.items() if b.kind==Kind.SLIME]:
 for lim in (12,20):
  f=Flyer(rng_state=2,push_limit=lim);f._cells=BASE._cells.copy()
  del f._cells[(15,2,17)]
  f._cells[(17,1,18)]=Block.piston(1,sticky=True)
  f._cells[(18,1,17)]=Block.observer(4)
  if rem is not None:del f._cells[rem]
  tag='none' if rem is None else '_'.join(map(str,rem))
  p=OUT/f'r{tag}_pl{lim}.flyer'
  try:f.save(p)
  except Exception as e:print('save fail',tag,lim,e);continue
  q=subprocess.run([str(RUN),'80',str(p)],capture_output=True,text=True)
  print(tag,lim,q.stdout.strip().split('\t')[1:7],flush=True)
