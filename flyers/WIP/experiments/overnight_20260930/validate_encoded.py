"""Validate an already encoded lead without repeating its diagnostic run."""
from pathlib import Path
import sys,subprocess
ROOT=Path(__file__).resolve().parents[4];RUNNER=ROOT/'target/release/fastflyer-research.exe'
def main():
    path=Path(sys.argv[1]);period=int(sys.argv[2]);advance=int(sys.argv[3])
    commands=[('verify',[str(path),'10000','--period',str(period),'--advance',str(advance)]),('audit',[str(path),'10000',str(period)])]
    if '--samples' in sys.argv:commands.append(('samples',[str(path),'--period',str(period),'--advance',str(advance),'--out',str(path.with_suffix('.samples.csv'))]))
    for name,args in commands:
        r=subprocess.run([str(RUNNER),name,*args],capture_output=True,text=True);path.with_suffix('.'+name+'.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True);assert r.returncode==0
if __name__=='__main__':main()
