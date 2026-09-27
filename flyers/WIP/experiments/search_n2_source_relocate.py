"""Replace the pull observer with a rod/redstone source that changes alignment on motion."""
from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
base=Flyer.load(ROOT/'flyers/WIP/experiments/sol_pl12/rear_route/lead1_pl14.flyer')
out=Path(os.environ['TEMP'])/'n2_source_relocate';out.mkdir(exist_ok=True)
run=Path(os.environ['TEMP'])/'flyer_batch.exe'
for limit in (12,20):
 folder=out/f'pl{limit}';folder.mkdir(exist_ok=True)
 for frontdel in (False,True):
  for x in range(15,20):
   for y in range(0,5):
    for z in range(14,20):
     p=(x,y,z)
     if p in base._cells and p!=(18,1,17):continue
     for typ in range(7):
      f=Flyer(rng_state=2,push_limit=limit);f._cells=base._cells.copy()
      del f._cells[(18,1,17)]
      if frontdel:del f._cells[(14,1,17)]
      f._cells[p]=Block(Kind.REDSTONE_BLOCK) if typ==6 else Block.rod(typ)
      dest=folder/f'fd{int(frontdel)}_p{x}_{y}_{z}_t{typ}.flyer'
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
