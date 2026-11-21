"""Screen one independent deletion from each overloaded body of the six-body control."""
from tempfile import TemporaryDirectory
import subprocess
from close import *
from screen import TOOL
from search import normalize


def deletion_options(r,i):
    return [('glue',p) for p in sorted(r.glue[i])] + [('red',p) for p in r.mods[i]['R']]


def main():
    doc=json.loads((HERE/'screw6_pl18.json').read_text())
    data=[shape(*([tuple(x) for x in group] for group in m)) for m in doc['templates']]
    def build(): return candidate(data,doc['edges'],2,2)
    r=build()
    # Removing a cell cannot create overlap, adhesion to an RB, a powered spent
    # piston, or a blocked +X destination in any of the six prescribed slots.
    # The simulator decides whether each remaining contact can drive its load.
    assert not first_issue(r)
    counts=Counter()
    with TemporaryDirectory(dir=HERE) as tmp:
        path=Path(tmp)/'trial.flyer'
        for options in itertools.product(deletion_options(r,0),deletion_options(r,3)):
            trial=build()
            for i,(kind,p) in zip((0,3),options):
                if kind=='glue': trial.glue[i].remove(p)
                else:
                    m=dict(trial.mods[i]); m['R']=[c for c in m['R'] if c!=p]
                    trial.mods[i]=m
            save_flyer(trial,17,path)
            audit=subprocess.run([TOOL,'audit',path,'240','0'],capture_output=True,text=True)
            verify=subprocess.run([TOOL,'verify',path,'1000','--period','12','--advance','4'],capture_output=True,text=True)
            counts['screened']+=1
            if 'distance=80 ' in audit.stdout and 'extension_failures=0 ' in audit.stdout and 'movement_failures=0' in audit.stdout and 'conservation_mismatch_ticks=0 ' in audit.stdout:
                target=HERE/f'trim_pl17_{counts["pass"]}.flyer'
                save_flyer(trial,17,target)
                counts['pass']+=1
                print(target,verify.stdout.strip(),flush=True)
    print(counts)


if __name__=='__main__': main()
