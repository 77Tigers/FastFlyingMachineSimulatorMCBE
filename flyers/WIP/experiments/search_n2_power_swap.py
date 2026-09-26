"""Coordinated power-source swaps on the verified PL13 two-carrier flyer."""
from pathlib import Path
import os, subprocess, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind

BASE=Flyer.load(ROOT/'flyers/WIP/two_push_crosslayer_pl13.flyer')
OUT=Path(__file__).resolve().parent/'n2_power_swap';OUT.mkdir(exist_ok=True)
RUN=Path(os.environ['TEMP'])/'flyer_measure.exe'

def score(cells,tag):
 f=Flyer(rng_state=2,push_limit=12);f._cells=cells
 try: f.validate();f.save(OUT/f'{tag}.flyer')
 except Exception:return -1
 p=subprocess.run([str(RUN),'80',str(OUT/f'{tag}.flyer')],capture_output=True,text=True)
 try: val=int(p.stdout.strip().split('\t')[1])
 except:val=-1
 if val<18:(OUT/f'{tag}.flyer').unlink()
 return val

best=[]
rod=(16,3,16);source=(16,0,17)
for new_pos in sorted(BASE._cells):
 for d in range(6):
  cells=BASE._cells.copy();del cells[rod]
  cells[new_pos]=Block.rod(d)
  if new_pos!=source:del cells[source]
  s=score(cells,f'r{new_pos[0]}_{new_pos[1]}_{new_pos[2]}_d{d}')
  best.append((s,new_pos,d))
for remove in [rod,source]:
 cells=BASE._cells.copy();del cells[remove]
 s=score(cells,'remove_'+str(remove).replace(' ','_'))
 best.append((s,remove,-1))
print(sorted(best,reverse=True)[:20])
