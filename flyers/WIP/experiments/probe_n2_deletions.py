from pathlib import Path
import os, subprocess, sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Kind
f=Flyer.load(ROOT/'flyers/WIP/two_push_crosslayer_pl13.flyer');out=Path(__file__).resolve().parent/'n2_deletions';out.mkdir(exist_ok=True)
run=Path(os.environ['TEMP'])/'flyer_measure.exe'
for pos,block in sorted(f._cells.items()):
 if block.kind not in (Kind.HONEY,Kind.SLIME,Kind.REDSTONE_BLOCK,Kind.ROD):continue
 g=Flyer(rng_state=2,push_limit=12);g._cells=f._cells.copy();del g._cells[pos]
 p=out/('r_'+'_'.join(map(str,pos))+'.flyer');g.save(p)
 q=subprocess.run([str(run),'32',str(p)],capture_output=True,text=True)
 print(pos,block.kind.name,q.stdout.strip().split('\t')[1])
