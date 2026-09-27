"""Screen the best sticky near miss across simulation RNG and chunk X phase."""
from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer
inp=Path(os.environ['TEMP'])/'n2_sticky_delete'
out=Path(os.environ['TEMP'])/'n2_sticky_phase';out.mkdir(exist_ok=True)
for m in (3,7):
 src=Flyer.load(inp/f'p0_15_m{m}.flyer')
 for seed in range(256):
  for phase in (0,7,8,15):
   f=Flyer(phase_x=phase,rng_state=seed,push_limit=12);f._cells=src._cells.copy()
   f.save(out/f'm{m}_s{seed}_x{phase}.flyer')
run=Path(os.environ['TEMP'])/'flyer_batch.exe'
p=subprocess.run([str(run),'160',str(out)],capture_output=True,text=True)
rows=[]
for line in p.stdout.splitlines():
 a=line.split('\t')
 if len(a)>1:
  try:rows.append((int(a[1]),line))
  except:pass
print('tested',len(rows),'max',max((r[0] for r in rows),default=-1),'top',*sorted(rows,reverse=True)[:40],sep='\n')
