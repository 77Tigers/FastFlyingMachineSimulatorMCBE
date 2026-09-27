"""Exhaustive 10-cell honey/slime material masks on the verified PL13 geometry."""
from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
base=Flyer.load(ROOT/'flyers/WIP/two_push_crosslayer_pl13.flyer')
honey=sorted(p for p,b in base._cells.items() if b.kind==Kind.HONEY)
out=Path(os.environ['TEMP'])/'n2_honey_mix';out.mkdir(exist_ok=True)
for mask in range(1<<len(honey)):
 f=Flyer(rng_state=2,push_limit=12);f._cells=base._cells.copy()
 for i,p in enumerate(honey):
  if mask>>i&1:f._cells[p]=Block(Kind.SLIME)
 f.save(out/f'm{mask}.flyer')
run=Path(os.environ['TEMP'])/'flyer_batch.exe'
p=subprocess.run([str(run),'80',str(out)],capture_output=True,text=True)
rows=[]
for line in p.stdout.splitlines():
 parts=line.split('\t')
 if len(parts)>1:
  try:rows.append((int(parts[1]),line))
  except:pass
print('tested',len(rows),'top',*sorted(rows,reverse=True)[:40],sep='\n')
