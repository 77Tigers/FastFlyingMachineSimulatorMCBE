from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
base=Flyer.load(ROOT/'flyers/WIP/two_push_crosslayer_pl13.flyer')
sites=[p for p,b in base._cells.items() if b.kind==Kind.PISTON]
out=Path(os.environ['TEMP'])/'n2_sticky';out.mkdir(exist_ok=True)
for bits in range(16):
 f=Flyer(rng_state=2,push_limit=12);f._cells=base._cells.copy()
 for i,p in enumerate(sites):
  if bits>>i&1:f._cells[p]=Block.piston(0,sticky=True)
 f.save(out/f's{bits}.flyer')
run=Path(os.environ['TEMP'])/'flyer_measure.exe'
for p in sorted(out.glob('*.flyer')):
 q=subprocess.run([str(run),'80',str(p)],capture_output=True,text=True)
 print(p.name,q.stdout.strip().split('\t')[1])
