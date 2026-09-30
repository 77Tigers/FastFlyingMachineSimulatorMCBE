"""Certify the first saturated pulling-only lead without changing simulation."""
from pathlib import Path
import sys, subprocess
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Kind
HERE=Path(__file__).resolve().parent
RUNNER=ROOT/'flyers/WIP/experiments/bin/research_runner.exe'
def main():
    f=Flyer.load(HERE/'pull3_10body_candidates/g4_s003.flyer')
    pistons=[b for b in f._cells.values() if b.kind==Kind.PISTON]
    # Encoded member audit is also retained by the traced runner below.
    f.push_limit=127;path=HERE/'pull3_10body_g4_s003_pl127.flyer';f.save(path)
    commands=[('verify',[str(path),'10000','--period','10','--advance','3']),
              ('audit',[str(path),'10000','10']),
              ('samples',[str(path),'--period','10','--advance','3','--out',str(path.with_suffix('.samples.csv'))])]
    for name,args in commands:
        r=subprocess.run([str(RUNNER),name,*args],capture_output=True,text=True)
        path.with_suffix('.'+name+'.txt').write_text(r.stdout+r.stderr)
        print(r.stdout,flush=True)
        assert r.returncode==0,(name,r.stdout,r.stderr)
if __name__=='__main__':main()
