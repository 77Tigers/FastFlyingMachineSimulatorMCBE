"""The local builder gate uses one RNG seed and two phase settings."""
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import subprocess
from fastflyer import Flyer

HERE=Path(__file__).resolve().parent
TOOL=HERE.parents[4]/'target/release/fastflyer-research'


def screen(path):
    original=Flyer.load(str(path))
    bounds=original.bounds()
    print('blocks',original.occupied_count(),'dimensions',tuple(b-a+1 for a,b in zip(*bounds)),flush=True)
    with TemporaryDirectory(dir=HERE) as work:
        for limit,phase in [(original.push_limit,0),(original.push_limit,7),(original.push_limit-1,0)]:
            f=Flyer.load(str(path))
            f.push_limit=limit
            f.phase_x=phase
            f.phase_z=phase
            f.rng_state=0
            temp=Path(work)/f'pl{limit}_phase{phase}.flyer'
            f.save(str(temp))
            runs=[('audit','240','0'),('verify','1000','--period','12','--advance','4')]
            if limit==original.push_limit: runs.append(('audit','10000','0'))
            for command,*args in runs:
                result=subprocess.run([TOOL,command,temp,*args],capture_output=True,text=True)
                print(limit,phase,result.stdout.strip().replace(str(temp),path.name),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('flyer',type=Path)
    screen(ap.parse_args().flyer)
