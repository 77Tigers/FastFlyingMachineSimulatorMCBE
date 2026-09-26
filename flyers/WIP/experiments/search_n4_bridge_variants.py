"""Try short third-segment bridges on several verified PL22 geometries."""
from __future__ import annotations

import csv
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from fastflyer import Block, Flyer, Kind
from flyers.WIP.astra_ringgen_safe import make

OUT = Path(__file__).resolve().parent / "n4_bridge_variants"
RUNNER = Path(os.environ["TEMP"]) / "flyer_measure.exe"
CENTERS = ((3,1),(3,3),(4,2))
DIRS = ((1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))


def distance(a,b):
    return sum(abs(a[i]-b[i]) for i in range(3))


def add(a,b):
    return tuple(a[i]+b[i] for i in range(3))


def measure(f, ticks, path):
    f.save(path)
    p = subprocess.run([str(RUNNER),str(ticks),str(path)],capture_output=True,text=True)
    parts = p.stdout.strip().split("\t")
    return int(parts[1]) if p.returncode == 0 and len(parts)>1 else -1


def main():
    OUT.mkdir(exist_ok=True)
    rows=[]
    started=time.monotonic()
    for ci,(cy,cz) in enumerate(CENTERS):
        for seed in (0,1):
            base,counts,(segments,_) = make(4,[(0,0),(0,4),(cy,cz)],seed,21)
            rear={(-2,-1,0),(-2,0,-1),(-2,0,0),(-2,0,1),(-2,1,0)}
            front={(2,cy,cz),(2,cy-1,cz),(2,cy+1,cz),(2,cy,cz-1),(2,cy,cz+1)}
            if not rear|front <= segments[2]:
                print("BAD_TERMINALS",ci,seed,flush=True)
                continue
            old=segments[2]-rear-front
            occupied=set(base._cells)-old
            limit=min(distance(a,b) for a in rear for b in front)
            if limit-1 >= len(old):
                print("NO_CELL_SAVING",ci,seed,"old",len(old),"shortest",limit-1,flush=True)
                continue
            routes=set()

            def walk(path,end):
                if len(path)-1 == limit:
                    if path[-1]==end:
                        cells=frozenset(path[1:-1])
                        if len(cells)==limit-1 and not cells & occupied:
                            routes.add(cells)
                    return
                remaining=limit-(len(path)-1)
                for d in DIRS:
                    q=add(path[-1],d)
                    if q in path or q in occupied and q!=end or distance(q,end)>remaining-1:
                        continue
                    walk(path+[q],end)

            for a in rear:
                for b in front:
                    if distance(a,b)==limit:
                        walk([a],b)
            print("ROUTES",ci,seed,"sticky",counts,"old",len(old),"short",limit-1,"count",len(routes),flush=True)
            for ri,cells in enumerate(sorted(routes,key=lambda x:sorted(x))):
                for mask in range(8):
                    f=Flyer(base.phase_x,base.phase_z,base.rng_state,21)
                    f._cells={p:b for p,b in base._cells.items() if p not in old}
                    for i,segment in enumerate(segments):
                        kind=Kind.HONEY if mask&(1<<i) else Kind.SLIME
                        for p in segment-old:
                            f.set(p,Block(kind))
                    kind=Kind.HONEY if mask&4 else Kind.SLIME
                    for p in cells:
                        f.set(p,Block(kind))
                    screen=OUT/"screen.flyer"
                    d120=measure(f,120,screen)
                    d1000=measure(f,1000,screen) if d120>=36 else -1
                    d10000=measure(f,10000,screen) if d1000>=300 else -1
                    rows.append((ci,seed,ri,mask,*counts,len(old),len(cells),d120,d1000,d10000))
                    if d120>=36:
                        name=f"c{ci}_s{seed}_r{ri}_m{mask}.flyer"
                        f.save(OUT/name)
                        print("LEAD",name,d120,d1000,d10000,flush=True)
            if time.monotonic()-started > 180:
                break
        if time.monotonic()-started > 180:
            break
    with (OUT/"summary.csv").open("w",newline="") as stream:
        writer=csv.writer(stream)
        writer.writerow(("center_index","seed","route","material_mask","sticky0","sticky1","sticky2","old_connector","new_connector","distance120","distance1000","distance10000"))
        writer.writerows(rows)
    print("DONE",len(rows),"tests",round(time.monotonic()-started,1),"seconds",flush=True)


if __name__=="__main__":
    main()
