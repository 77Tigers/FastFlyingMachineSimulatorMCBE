"""Bounded one-cell reduction of the N3 seed's 19-block load carrier."""
from pathlib import Path
import csv, os, subprocess, sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from fastflyer import Flyer
from flyers.WIP.astra_ringgen_safe import make

OUT=Path(__file__).resolve().parent/'n3_reduction'
RUNNER=Path(os.environ['TEMP'])/'flyer_measure.exe'
CENTERS=[(0,0),(0,4),(3,5),(5,2),(3,-1)]

def main():
    OUT.mkdir(exist_ok=True)
    base,counts,(segments,_)=make(3,CENTERS,3,18)
    assert counts==[14,14,14,14,15]
    rows=[]
    for i,p in enumerate(sorted(segments[4])):
        f=Flyer(base.phase_x,base.phase_z,base.rng_state,18)
        f._cells=base._cells.copy()
        f.remove(p)
        path=OUT/f'delete_{i:02}.flyer';f.save(path)
        proc=subprocess.run([str(RUNNER),'120',str(path)],capture_output=True,text=True)
        fields=proc.stdout.strip().split('\t')
        d=int(fields[1]) if proc.returncode==0 and len(fields)>1 else -1
        rows.append((i,*p,d))
        if d<30:path.unlink()
        else:print('LEAD',i,p,d,flush=True)
    with (OUT/'summary.csv').open('w',newline='') as stream:
        w=csv.writer(stream);w.writerow(('index','x','y','z','distance120'));w.writerows(rows)
    print('DONE',len(rows),'best',max(r[-1] for r in rows))

if __name__=='__main__':main()
