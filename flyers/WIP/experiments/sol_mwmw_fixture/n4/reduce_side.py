"""Single-cell reductions of sustained diagonal rear-pickup N4 layouts."""
from pathlib import Path
import csv,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Kind
HERE=Path(__file__).resolve().parent
RUNNER=Path(os.environ['TEMP'])/'flyer_measure.exe'

def run(f,limit,ticks):
    f.push_limit=limit
    p=HERE/'reduce_screen.flyer'
    try:f.save(p)
    except Exception:return (-1,-1)
    q=subprocess.run([str(RUNNER),str(ticks),str(p)],capture_output=True,text=True)
    a=q.stdout.strip().split('\t')
    return (int(a[1]),int(a[5])) if q.returncode==0 and len(a)>5 else (-1,-1)

def main():
    rows=[]
    for basename in ('c7_s1_m19_d40','c9_s2_m19_d40','c13_s1_m19_d40'):
        src=Flyer.load(HERE/(basename+'.flyer'))
        count=len(src._cells)
        cells=[p for p,b in src._cells.items() if b.kind in (Kind.SLIME,Kind.HONEY)]
        for p in cells:
            f=Flyer(src.phase_x,src.phase_z,src.rng_state,23)
            f._cells={q:b for q,b in src._cells.items() if q!=p}
            d120,c120=run(f,23,120)
            d1000,c1000=run(f,23,1000) if d120>=39 and c120==count-1 else (-1,-1)
            d10000,c10000=run(f,23,10000) if d1000>=330 and c1000==count-1 else (-1,-1)
            d22,c22=run(f,22,120) if d120>=39 else (-1,-1)
            rows.append((basename,p,d120,c120,d1000,c1000,d10000,c10000,d22,c22))
            if d120>=39:
                name=f'{basename}_remove_{p[0]}_{p[1]}_{p[2]}.flyer'
                f.push_limit=23;f.save(HERE/name)
                print('LEAD',name,d120,c120,d1000,c1000,d10000,c10000,'PL22',d22,c22,flush=True)
    with (HERE/'reduction.csv').open('w',newline='') as out:
        w=csv.writer(out);w.writerow(('source','removed','d120_pl23','end_count120','d1000_pl23','end_count1000','d10000_pl23','end_count10000','d120_pl22','end_count22'));w.writerows(rows)
    print('DONE',len(rows),flush=True)
if __name__=='__main__':main()
