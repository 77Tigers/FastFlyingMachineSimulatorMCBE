from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'flyers/WIP'))
from astra_ringgen_safe import make
OUT=Path(__file__).resolve().parent/'four_compact';OUT.mkdir(exist_ok=True)
RUN=Path(os.environ['TEMP'])/'flyer_measure.exe'
rows=[]
for a in (2,3,4):
 for b in (2,3,4):
  for lean in (-1,0,1):
   centers=[(0,0),(0,a),(b,a+lean),(b,lean)]
   for seed in range(6):
    ans=make(2,centers,seed,30)
    if ans is None:continue
    f,counts,_=ans
    name=f'a{a}b{b}l{lean}_s{seed}'
    p=OUT/f'{name}.flyer'
    try:f.save(p)
    except:continue
    r=subprocess.run([str(RUN),'120',str(p)],capture_output=True,text=True)
    try:score=int(r.stdout.strip().split('\t')[1])
    except:score=-1
    rows.append((score,max(counts),counts,name))
    if score>=30:print(score,counts,name,flush=True)
print('generated',len(rows),'top',*sorted(rows,reverse=True)[:25],sep='\n')
