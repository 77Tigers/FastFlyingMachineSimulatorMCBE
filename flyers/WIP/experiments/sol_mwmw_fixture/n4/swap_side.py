"""Bounded local reroute: one sticky moved to a neighboring empty cell."""
from pathlib import Path
import csv,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Kind
HERE=Path(__file__).resolve().parent
RUNNER=Path(os.environ['TEMP'])/'flyer_measure.exe'
DIR=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))

def run(f,limit,ticks):
    f.push_limit=limit
    p=HERE/'swap_screen.flyer'
    try:f.save(p)
    except Exception:return (-1,-1)
    q=subprocess.run([str(RUNNER),str(ticks),str(p)],capture_output=True,text=True)
    a=q.stdout.strip().split('\t')
    return (int(a[1]),int(a[5])) if q.returncode==0 and len(a)>5 else (-1,-1)

def main():
    src=Flyer.load(HERE/'c7_s1_m19_d40.flyer'); count=len(src._cells)
    rows=[]; start=time.monotonic(); n=0
    for p,b in sorted(src._cells.items()):
        if b.kind not in (Kind.SLIME,Kind.HONEY):continue
        for d in DIR:
            q=tuple(p[i]+d[i] for i in range(3))
            if q in src._cells:continue
            if n>=500 or time.monotonic()-start>600:break
            n+=1
            f=Flyer(src.phase_x,src.phase_z,src.rng_state,23)
            f._cells={r:v for r,v in src._cells.items() if r!=p}
            f._cells[q]=b
            if f.validate():continue
            d120,c120=run(f,23,120)
            d1000,c1000=run(f,23,1000) if d120>=39 and c120==count else (-1,-1)
            d10000,c10000=run(f,23,10000) if d1000>=330 and c1000==count else (-1,-1)
            d22,c22=run(f,22,120) if d120>=39 else (-1,-1)
            rows.append((p,q,d120,c120,d1000,c1000,d10000,c10000,d22,c22))
            if d120>=39:
                name=f'swap_{p[0]}_{p[1]}_{p[2]}__{q[0]}_{q[1]}_{q[2]}.flyer'
                f.push_limit=23;f.save(HERE/name)
                print('LEAD',name,d120,c120,d1000,c1000,d10000,c10000,'PL22',d22,c22,flush=True)
        if n>=500 or time.monotonic()-start>600:break
    with (HERE/'swaps.csv').open('w',newline='') as out:
        w=csv.writer(out);w.writerow(('from','to','d120_pl23','end_count120','d1000_pl23','end_count1000','d10000_pl23','end_count10000','d120_pl22','end_count22'));w.writerows(rows)
    print('DONE',n,'valid',len(rows),'elapsed',round(time.monotonic()-start,1),flush=True)
if __name__=='__main__':main()
