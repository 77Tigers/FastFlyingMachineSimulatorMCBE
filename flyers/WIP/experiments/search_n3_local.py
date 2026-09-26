"""Local center perturbations of the verified five-segment N3 ring at PL18."""
from pathlib import Path
import csv,os,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from flyers.WIP.astra_ringgen_safe import make

OUT=Path(__file__).resolve().parent/'n3_local'
RUNNER=Path(os.environ['TEMP'])/'flyer_measure.exe'
BASE=((0,0),(0,4),(3,5),(5,2),(3,-1))
DELTAS=((0,1),(0,-1),(1,0),(-1,0))

def main():
    OUT.mkdir(exist_ok=True)
    rows=[];start=time.monotonic()
    for i in (4,3,2,1):
        for dy,dz in DELTAS:
            centers=list(BASE)
            centers[i]=(centers[i][0]+dy,centers[i][1]+dz)
            if len(set(centers))<5:continue
            for seed in range(8):
                if time.monotonic()-start>120:break
                ans=make(3,centers,seed,18)
                if ans is None:
                    rows.append((i,dy,dz,seed,-1,-1,-1,-1,-1,-1))
                    continue
                f,counts,_=ans
                label=f'i{i}_dy{dy}dz{dz}_s{seed}'
                path=OUT/f'{label}.flyer';f.save(path)
                proc=subprocess.run([str(RUNNER),'120',str(path)],capture_output=True,text=True)
                fields=proc.stdout.strip().split('\t')
                d=int(fields[1]) if proc.returncode==0 and len(fields)>1 else -1
                rows.append((i,dy,dz,seed,*counts,d))
                if d<33:path.unlink()
                else:print('LEAD',label,counts,d,flush=True)
            if time.monotonic()-start>120:break
        print('CENTER',i,'elapsed',round(time.monotonic()-start,1),flush=True)
        if time.monotonic()-start>120:break
    with (OUT/'summary.csv').open('w',newline='') as stream:
        w=csv.writer(stream);w.writerow(('center_index','delta_y','delta_z','seed','sticky0','sticky1','sticky2','sticky3','sticky4','distance120'));w.writerows(rows)
    print('DONE',len(rows),'attempts',round(time.monotonic()-start,1),'seconds',flush=True)

if __name__=='__main__':main()
