import sys, subprocess, pathlib, os
ROOT=str(pathlib.Path(__file__).resolve().parents[5])
sys.path.insert(0, ROOT)
from fastflyer import Flyer, Block, Kind
BASE=ROOT+'/flyers/bank/pl15/exclusive_roles_3bps.flyer'
LH=ROOT+'/flyers/WIP/experiments/tm_smol_rebalance_20261001/loadhist.exe'
WD=ROOT+'/flyers/WIP/experiments/tm_smol_rebalance_20261001/j_mmwmw2/work'
os.makedirs(WD,exist_ok=True)
def base(): return Flyer.load(BASE)
def run(flyers, ticks=600, limit=20):
    paths=[]
    for name,f in flyers.items():
        p=f'{WD}/{name}.flyer'; f.save(p); paths.append(p)
    out=subprocess.run([LH,str(ticks),'100',str(limit)]+paths,capture_output=True,text=True).stdout
    return out
if __name__=='__main__':
    f=base(); print(run({'base':f}))
    f=base(); f.remove((9,4,12)); print(run({'nosticky':f}))
