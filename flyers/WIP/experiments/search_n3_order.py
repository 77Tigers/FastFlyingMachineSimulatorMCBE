"""Rotate/reverse the five-ring center order to move phase and material seams."""
from pathlib import Path
import csv,os,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from flyers.WIP.astra_ringgen_safe import make

OUT=Path(__file__).resolve().parent/'n3_order'
RUNNER=Path(os.environ['TEMP'])/'flyer_measure.exe'
BASE=((0,0),(0,4),(3,5),(5,2),(3,-1))

def main():
    OUT.mkdir(exist_ok=True)
    rows=[];t0=time.monotonic()
    for reverse in (0,1):
        ring=BASE[::-1] if reverse else BASE
        for shift in range(5):
            centers=ring[shift:]+ring[:shift]
            for seed in range(8):
                if time.monotonic()-t0>100:break
                ans=make(3,centers,seed,18)
                if ans is None:
                    rows.append((reverse,shift,seed,-1,-1,-1,-1,-1,-1,-1))
                    continue
                f,counts,_=ans
                path=OUT/f'rev{reverse}_shift{shift}_s{seed}.flyer';f.save(path)
                p=subprocess.run([str(RUNNER),'120',str(path)],capture_output=True,text=True)
                parts=p.stdout.strip().split('\t')
                d120=int(parts[1]) if p.returncode==0 and len(parts)>1 else -1
                d10000=-1
                if d120>=34:
                    q=subprocess.run([str(RUNNER),'10000',str(path)],capture_output=True,text=True)
                    fields=q.stdout.strip().split('\t')
                    d10000=int(fields[1]) if q.returncode==0 and len(fields)>1 else -1
                    print('LEAD',reverse,shift,seed,counts,d120,d10000,flush=True)
                if d120<34:path.unlink()
                rows.append((reverse,shift,seed,*counts,d120,d10000))
            if time.monotonic()-t0>100:break
        if time.monotonic()-t0>100:break
    with (OUT/'summary.csv').open('w',newline='') as stream:
        w=csv.writer(stream);w.writerow(('reversed','shift','seed','sticky0','sticky1','sticky2','sticky3','sticky4','distance120','distance10000'));w.writerows(rows)
    print('DONE',len(rows),'attempts',round(time.monotonic()-t0,1),'seconds',flush=True)

if __name__=='__main__':main()
