"""Bounded c244 observer reroutes to avoid powering the A return piston."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind

base=Flyer.load(ROOT/'flyers/WIP/experiments/astra_diagonal/mwmw/c244.flyer')
out=Path(__file__).resolve().parent
for name,obs,bridge in [
    ('direct_below',(14,0,16),(14,1,16)),
    ('direct_above',(14,-1,17),(14,0,17)),
]:
 for limit in (10,11,20):
  f=Flyer(rng_state=base.rng_state,push_limit=limit,
          phase_x=base.phase_x,phase_z=base.phase_z)
  f._cells=base._cells.copy()
  del f._cells[(14,1,16)]
  if bridge not in f._cells:f._cells[bridge]=Block(Kind.SLIME)
  f._cells[obs]=Block.observer(4 if name=='direct_below' else 2)
  path=out/f'c244_{name}_pl{limit}.flyer'
  try:
   f.save(path)
   print(path.name,Flyer.load(path).validate())
  except Exception as e:print(name,limit,e)
