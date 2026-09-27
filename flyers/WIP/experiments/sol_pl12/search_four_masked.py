from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'flyers/WIP/experiments'))
from n2_maskgen import make
OUT=Path(__file__).resolve().parent/'four_masked';OUT.mkdir(exist_ok=True)
RUN=Path(os.environ['TEMP'])/'flyer_measure.exe'
rows=[]
for a,b,lean in [(3,2,-1),(3,3,-1),(3,3,0),(4,3,0),(4,4,0)]:
 centers=[(0,0),(0,a),(b,a+lean),(b,lean)]
 for seed in range(6):
  for fm in (3,5,6,7):
   for rm in (3,5,6):
    ans=make(2,centers,seed,30,fm,rm)
    if ans is None:continue
    f,counts,_=ans
    name=f'a{a}b{b}l{lean}_s{seed}_f{fm}r{rm}'
    p=OUT/f'{name}.flyer'
    try:f.save(p)
    except:continue
    r=subprocess.run([str(RUN),'120',str(p)],capture_output=True,text=True)
    try:score=int(r.stdout.strip().split('\t')[1])
    except:score=-1
    rows.append((score,max(counts),counts,name))
    if score>=30 and max(counts)<=11:print(score,counts,name,flush=True)
print('generated',len(rows),'top',*sorted(rows,reverse=True)[:25],sep='\n')
