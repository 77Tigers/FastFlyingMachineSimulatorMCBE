"""Put the hybrid timing observer in a honey carrier cell instead of the front tip."""
from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
base=Flyer.load(ROOT/'flyers/WIP/experiments/sol_pl12/rear_route/lead1_pl14.flyer')
out=Path(os.environ['TEMP'])/'n2_rear_observer';out.mkdir(exist_ok=True)
run=Path(os.environ['TEMP'])/'flyer_batch.exe'
for limit in (12,20):
 folder=out/f'pl{limit}';folder.mkdir(exist_ok=True)
 for frontdel in (False,True):
  for p,b in base._cells.items():
   if b.kind not in (Kind.HONEY,Kind.ROD,Kind.SLIME):continue
   for direction in range(6):
    for power in (False,True):
     f=Flyer(rng_state=2,push_limit=limit);f._cells=base._cells.copy()
     del f._cells[(18,1,17)]
     if frontdel and p!=(14,1,17):del f._cells[(14,1,17)]
     f._cells[p]=Block.observer(direction,powered=power)
     dest=folder/f'fd{int(frontdel)}_p{p[0]}_{p[1]}_{p[2]}_d{direction}_on{int(power)}.flyer'
     try:f.save(dest)
     except:pass
 q=subprocess.run([str(run),'160',str(folder)],capture_output=True,text=True)
 rows=[]
 for line in q.stdout.splitlines():
  a=line.split('\t')
  if len(a)>1:
   try:rows.append((int(a[1]),line))
   except:pass
 print(limit,len(rows),*sorted(rows,reverse=True)[:15],sep='\n',flush=True)
