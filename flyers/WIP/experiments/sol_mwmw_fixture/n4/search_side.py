"""Bounded N4 diagonal rear-corner screen; geometry only, Rust measures motion."""
from pathlib import Path
import csv, itertools, os, subprocess, sys, time

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from flyers.WIP.astra_ringgen_side import make

HERE = Path(__file__).resolve().parent
RUNNER = Path(os.environ['TEMP']) / 'flyer_measure.exe'
DIRS = ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))

def connected(cells):
    if not cells: return False
    seen={next(iter(cells))}; todo=list(seen)
    while todo:
        x,y,z=todo.pop()
        for dx,dy,dz in DIRS:
            p=(x+dx,y+dy,z+dz)
            if p in cells and p not in seen: seen.add(p);todo.append(p)
    return len(seen)==len(cells)

def measure(f, ticks, limit):
    f.push_limit=limit
    path=HERE/'screen.flyer'
    try: f.save(path)
    except Exception: return -1
    p=subprocess.run([str(RUNNER),str(ticks),str(path)],capture_output=True,text=True)
    parts=p.stdout.strip().split('\t')
    return int(parts[1]) if p.returncode==0 and len(parts)>1 else -1

def main():
    assert RUNNER.exists(), RUNNER
    HERE.mkdir(parents=True,exist_ok=True)
    rows=[]; started=time.monotonic(); tested=0
    centers_list=[[(0,0),(0,4),(y,z)] for y,z in itertools.product(range(2,6),range(-1,4))]
    for ci,centers in enumerate(centers_list):
        for seed in range(5):
            if tested>=100 or time.monotonic()-started>600: break
            tested+=1
            ans=make(4,centers,seed,30)
            if ans is None:
                rows.append((ci,centers[-1],seed,'invalid','','','','',''))
                continue
            f,counts,(segments,_)=ans
            if not all(map(connected,segments)) or f.validate():
                rows.append((ci,centers[-1],seed,'disconnected_or_format',str(counts),'','','',''))
                continue
            d120=measure(f,120,30)
            d1000=measure(f,1000,30) if d120>=39 else -1
            d10000=measure(f,10000,30) if d1000>=330 else -1
            d21=measure(f,120,21) if d120>=39 else -1
            d20=measure(f,120,20) if d120>=39 else -1
            rows.append((ci,centers[-1],seed,'valid',str(counts),d120,d1000,d10000,f'{d21}/{d20}'))
            if d120>=39 or max(counts)<=16:
                name=f'c{ci}_s{seed}_m{max(counts)}_d{d120}.flyer'
                f.push_limit=30;f.save(HERE/name)
                print('LEAD',name,counts,d120,d1000,d10000,'PL21/20',d21,d20,flush=True)
        if tested>=100 or time.monotonic()-started>600: break
        print('PROGRESS',ci,centers[-1],'tested',tested,'elapsed',round(time.monotonic()-started,1),flush=True)
    with (HERE/'summary.csv').open('w',newline='') as stream:
        w=csv.writer(stream);w.writerow(('center_index','third_center','seed','status','sticky_counts','distance120_pl30','distance1000_pl30','distance10000_pl30','distance120_pl21_pl20'));w.writerows(rows)
    print('DONE',tested,'elapsed',round(time.monotonic()-started,1),flush=True)

if __name__=='__main__': main()
