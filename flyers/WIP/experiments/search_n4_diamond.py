"""Check omitted Manhattan-4 third-interface placements at PL21."""
from __future__ import annotations

import csv
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from flyers.WIP.astra_ringgen_safe import make

OUT=Path(__file__).resolve().parent/"n4_diamond"
RUNNER=Path(os.environ["TEMP"])/"flyer_measure.exe"


def main():
    OUT.mkdir(exist_ok=True)
    centers=[(y,z) for y in range(-4,5) for z in range(-4,5)
             if abs(y)+abs(z)==4 and (y,z)!=(0,4)]
    rows=[];t0=time.monotonic()
    for cy,cz in centers:
        for seed in range(4):
            ans=make(4,[(0,0),(0,4),(cy,cz)],seed,21)
            if ans is None:
                rows.append((cy,cz,seed,-1,-1,-1,-1))
                continue
            f,counts,_=ans
            path=OUT/f"y{cy}z{cz}_s{seed}.flyer"
            f.save(path)
            proc=subprocess.run([str(RUNNER),"120",str(path)],capture_output=True,text=True)
            parts=proc.stdout.strip().split("\t")
            d=int(parts[1]) if proc.returncode==0 and len(parts)>1 else -1
            rows.append((cy,cz,seed,*counts,d))
            if d<36:path.unlink()
            else:print("LEAD",(cy,cz),seed,counts,d,flush=True)
    with (OUT/"summary.csv").open("w",newline="") as stream:
        writer=csv.writer(stream)
        writer.writerow(("center_y","center_z","seed","sticky0","sticky1","sticky2","distance120"))
        writer.writerows(rows)
    print("DONE",len(rows),"attempts",round(time.monotonic()-t0,1),"seconds",flush=True)


if __name__=="__main__":main()
