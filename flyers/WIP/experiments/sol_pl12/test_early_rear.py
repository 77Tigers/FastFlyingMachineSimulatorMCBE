from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
BASE=Flyer.load(ROOT/'flyers/WIP/experiments/sol_pl12/rear_route/lead1_pl20.flyer')
OUT=Path(__file__).resolve().parent/'early_rear';OUT.mkdir(exist_ok=True)
RUN=Path(os.environ['TEMP'])/'flyer_measure.exe'
for rodpos in [(16,3,15),(16,2,14),(16,1,15),(16,2,16)]:
 for target in [(16,2,15),(16,1,15),(16,0,15)]:
  for lim in (12,20):
   f=Flyer(rng_state=2,push_limit=lim);f._cells=BASE._cells.copy()
   if rodpos!=(16,3,16):del f._cells[(16,3,16)]
   f._cells[rodpos]=Block.rod(3 if rodpos[1]==3 else 0)
   if target not in f._cells:f._cells[target]=Block(Kind.HONEY)
   name='r'+'_'.join(map(str,rodpos))+'_t'+'_'.join(map(str,target))+f'_pl{lim}'
   p=OUT/f'{name}.flyer'
   try:f.save(p)
   except:continue
   r=subprocess.run([str(RUN),'80',str(p)],capture_output=True,text=True)
   print(name,r.stdout.strip().split('\t')[1:7],flush=True)
