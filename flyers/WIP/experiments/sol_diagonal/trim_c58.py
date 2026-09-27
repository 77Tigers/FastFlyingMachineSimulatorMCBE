"""Single A-slime deletion screen at PL10 and high-limit diagnostic."""
from pathlib import Path
import sys, subprocess, os

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Kind
base=Flyer.load(ROOT/'flyers/WIP/experiments/astra_diagonal/mwmw/c58.flyer')
out=Path(__file__).resolve().parent/'trim_c58'
out.mkdir(exist_ok=True)
positions=[p for p,b in sorted(base._cells.items()) if b.kind==Kind.SLIME]
for i,p in enumerate(positions):
 for limit in (10,20):
  f=Flyer(rng_state=base.rng_state,push_limit=limit,
          phase_x=base.phase_x,phase_z=base.phase_z)
  f._cells=base._cells.copy()
  del f._cells[p]
  f.save(out/f'd{i}_pl{limit}.flyer')
run=Path(os.environ['TEMP'])/'flyer_measure.exe'
for i,p in enumerate(positions):
 print('delete',i,p)
 for limit in (10,20):
  a=subprocess.run([str(run),'160',str(out/f'd{i}_pl{limit}.flyer')],capture_output=True,text=True)
  print(limit,a.stdout.strip())
