"""Move the pull observer one cell rearward so its activation precedes the rear push."""
from itertools import combinations
from pathlib import Path
import os, subprocess, sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
base=Flyer.load(ROOT/'flyers/WIP/experiments/sol_pl12/rear_route/lead1_pl14.flyer')
out=Path(os.environ['TEMP'])/'n2_early_observer';out.mkdir(exist_ok=True)
run=Path(os.environ['TEMP'])/'flyer_batch.exe'
front=[p for p,b in base._cells.items() if b.kind==Kind.SLIME]
for limit in (12,20):
 folder=out/f'pl{limit}';folder.mkdir(exist_ok=True)
 for count in (0,1,2,3):
  for rem in combinations(front,count):
   f=Flyer(rng_state=2,push_limit=limit);f._cells=base._cells.copy()
   del f._cells[(18,1,17)]
   f._cells[(17,1,17)]=Block.observer(4)
   for p in rem:del f._cells[p]
   p=folder/('r'+','.join('_'.join(map(str,x)) for x in rem)+'.flyer')
   try:f.save(p)
   except:pass
 q=subprocess.run([str(run),'160',str(folder)],capture_output=True,text=True)
 rows=[]
 for line in q.stdout.splitlines():
  a=line.split('\t')
  if len(a)>1:
   try:rows.append((int(a[1]),line))
   except:pass
 print(limit,len(rows),*sorted(rows,reverse=True)[:12],sep='\n',flush=True)
