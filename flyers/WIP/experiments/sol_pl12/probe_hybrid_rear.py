from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
BASE=Flyer.load(ROOT/'flyers/WIP/experiments/sol_pl12/hybrid/rnone_pl20.flyer')
OUT=Path(__file__).resolve().parent/'rear_probe';OUT.mkdir(exist_ok=True)
RUN=Path(os.environ['TEMP'])/'flyer_measure.exe'
for p,b in BASE._cells.items():
 if b.kind not in (Kind.HONEY,Kind.ROD):continue
 f=Flyer(rng_state=2,push_limit=20);f._cells=BASE._cells.copy();del f._cells[p]
 q=OUT/f'rem{p[0]}_{p[1]}_{p[2]}.flyer'
 try:f.save(q)
 except Exception as e:print(e);continue
 r=subprocess.run([str(RUN),'10000',str(q)],capture_output=True,text=True)
 print(p,r.stdout.strip().split('\t')[1:7],flush=True)
