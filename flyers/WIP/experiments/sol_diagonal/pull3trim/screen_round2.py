"""One additional slime/honey deletion after the two proven trims."""
from pathlib import Path
import sys, subprocess, os, csv

ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Kind

base=Flyer.load(Path(__file__).resolve().parent/'double_d11_d55.flyer')
out=Path(__file__).resolve().parent/'round2'
out.mkdir(exist_ok=True)
meta=[]
for i,(p,b) in enumerate(sorted(base._cells.items())):
 if b.kind not in (Kind.SLIME,Kind.HONEY):continue
 f=Flyer(rng_state=base.rng_state,push_limit=100,
         phase_x=base.phase_x,phase_z=base.phase_z)
 f._cells=base._cells.copy();del f._cells[p]
 path=out/f'd{i}.flyer';f.save(path)
 meta.append((f'd{i}',p,b.kind.name))
batch=Path(os.environ['TEMP'])/'flyer_batch.exe'
p=subprocess.run([str(batch),'160',str(out)],capture_output=True,text=True,check=True)
score={a[0]:a[1:] for line in p.stdout.splitlines() if (a:=line.split('\t')) and len(a)>=4}
with (out.parent/'round2_results.tsv').open('w',newline='') as fh:
 w=csv.writer(fh,delimiter='\t');w.writerow(['id','cell','kind','distance','extensions','end_blocks'])
 for name,cell,kind in meta:w.writerow([name,cell,kind,*score.get(name,('','',''))])
print('tested',len(meta))
for name,cell,kind in meta:
 if int(score.get(name,('0',))[0])>=48:print('survivor',name,cell,kind,score[name])
