"""Certify a selected three-move/five-slot candidate at its measured load."""
from pathlib import Path
import sys,subprocess,re
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer
HERE=Path(__file__).resolve().parent;RUNNER=ROOT/'flyers/WIP/experiments/bin/research_runner.exe'
def main():
    source=Path(sys.argv[1]);prefix=sys.argv[2];f=Flyer.load(source);f.push_limit=1000
    diagnostic=HERE/(prefix+'_diagnostic.flyer');f.save(diagnostic)
    r=subprocess.run([str(RUNNER),'verify',str(diagnostic),'10000','--period','10','--advance','3'],capture_output=True,text=True)
    diagnostic.with_suffix('.verify.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True);assert r.returncode==0
    f.push_limit=int(re.search(r'max_successful_action=(\d+)',r.stdout)[1]);path=HERE/f'{prefix}_pl{f.push_limit}.flyer';f.save(path)
    commands=[('verify',[str(path),'10000','--period','10','--advance','3']),('audit',[str(path),'10000','10'])]
    if '--samples' in sys.argv:commands.append(('samples',[str(path),'--period','10','--advance','3','--out',str(path.with_suffix('.samples.csv'))]))
    for name,args in commands:
        r=subprocess.run([str(RUNNER),name,*args],capture_output=True,text=True);path.with_suffix('.'+name+'.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True);assert r.returncode==0
if __name__=='__main__':main()
