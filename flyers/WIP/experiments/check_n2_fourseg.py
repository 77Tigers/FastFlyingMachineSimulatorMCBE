"""Small full-horizon robustness sample for the four-segment PL15 N2 flyer."""
from pathlib import Path
import csv,os,subprocess,sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from fastflyer import Flyer

OUT=Path(__file__).resolve().parent/'n2_fourseg'
RUNNER=Path(os.environ['TEMP'])/'flyer_measure.exe'
SOURCE=OUT/'pl15.flyer'

def main():
    rows=[]
    for rng in (0,1,2,5,42):
        for phase in (0,7,8,15):
            f=Flyer.load(SOURCE);f.rng_state=rng;f.phase_x=phase;f.phase_z=phase
            path=OUT/'screen.flyer';f.save(path)
            p=subprocess.run([str(RUNNER),'10000',str(path)],capture_output=True,text=True)
            parts=p.stdout.strip().split('\t')
            d=int(parts[1]) if p.returncode==0 and len(parts)>1 else -1
            rows.append((rng,phase,phase,d))
    with (OUT/'phase_sample.csv').open('w',newline='') as stream:
        w=csv.writer(stream);w.writerow(('rng','phase_x','phase_z','distance10000'));w.writerows(rows)
    print('runs',len(rows),'successes',sum(r[-1]==2500 for r in rows),'scores',sorted(set(r[-1] for r in rows)))

if __name__=='__main__':main()
