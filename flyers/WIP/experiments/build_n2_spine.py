"""Construct and screen a compact shared-spine PL12 candidate family."""
from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
base=Flyer.load(ROOT/'flyers/WIP/two_push_crosslayer_pl13.flyer')
out=Path(__file__).resolve().parent/'n2_spine';out.mkdir(exist_ok=True)
def put(f,p,b):
 if p in f._cells:print('overwrite',p,f._cells[p],b)
 f._cells[p]=b
for variant in range(4):
 f=Flyer(rng_state=2,push_limit=12);f._cells=base._cells.copy()
 for p in [(16,0,16),(16,0,18),(16,0,17),(17,0,16),(17,0,17),(17,0,18),(16,0,15),(17,0,15),(17,1,15)]:del f._cells[p]
 put(f,(16,1,15),Block.piston(0));put(f,(16,1,17),Block.piston(0))
 put(f,(16,0,16),Block.rod(2))
 put(f,(17,1,15),Block(Kind.SLIME));put(f,(17,1,17),Block(Kind.SLIME))
 put(f,(16,1,14),Block(Kind.HONEY))
 if variant==0:route=[(16,2,14),(17,2,14)]
 elif variant==1:route=[(17,1,14),(17,2,14)]
 elif variant==2:route=[(16,1,13),(17,1,13),(17,1,14),(17,2,14)]
 else:route=[(16,2,14),(16,2,15)]
 for p in route:put(f,p,Block(Kind.HONEY))
 p=out/f'v{variant}.flyer'
 try:f.save(p)
 except Exception as e:print('invalid',variant,e)
for limit in (12,13,20):
 for variant in range(4):
  p=out/f'v{variant}.flyer';f=Flyer.load(p);f.push_limit=limit;f.save(out/f'v{variant}_pl{limit}.flyer')
run=Path(os.environ['TEMP'])/'flyer_measure.exe'
for p in sorted(out.glob('*_pl*.flyer')):
 q=subprocess.run([str(run),'80',str(p)],capture_output=True,text=True)
 print(p.name,q.stdout.strip().split('\t')[1:])
