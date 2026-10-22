"""Isolated native timing test: X0-carried sticky, recovery-carried observer.

The rear carrier's first2 moves and all3 X0 moves remain supplied. No claim
of complete-flyer integration or long verification. Glue detours avoid the
observer's trailing support joining its sticky at pull4.
"""
import os as _research_os
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind

ROOT=Path(__file__).resolve().parents[4]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('out',type=Path)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    f=Flyer();f.push_limit=12
    carrier=(14,0,11);sticky=(14,1,11);target=(13,1,11);observer=(16,2,11)
    f.set(carrier,Block(Kind.SLIME));f.set(sticky,Block.piston(1,sticky=True))
    glue=[target,(13,2,11),(13,3,11),(14,3,11),(15,3,11),(16,3,11)]
    for p in glue:f.set(p,Block(Kind.HONEY))
    f.set(observer,Block.decode(103)) # -Y output
    f.save(a.out/'problem.flyer');assert Flyer.load(a.out/'problem.flyer')._cells==f._cells
    rows=[]
    for cy in range(3):
        for slot in [0,1,2]:rows.append((10*cy+2*slot,carrier[0]+3*cy+slot,*carrier[1:],12))
        for slot in [2,3]:rows.append((10*cy+2*slot,target[0]+3*cy+slot-2,*target[1:],12))
    (a.out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
    contract={'version':1,'name':a.out.name,'flyer':'problem.flyer','period_ticks':10,'advance':3,'cycles':3,'recurrence':'bounded',
              'ports':[{'name':'X0_carrier','at':carrier,'role':'input','word':'mmmww','provenance':['supplied']*3+[None]*2},
                       {'name':'rear_pickup','at':target,'role':'input','word':'wwmmm','provenance':[None,None,'supplied','supplied','internal']}],
              'required_cells':[],'boundary_envelope':{'min':[10,0,9],'max':[20,5,13]},'prescribed_script':'drive.txt'}
    for order in ['before_natural','after_natural','interleaved']:
        c={**contract,'prescribed_order':order};(a.out/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
    prep={'scope':__doc__,'sticky':sticky,'observer':observer,'glue':glue,'fire':3,'pull':4,
          'budget':{'X0_fixture':2,'rear_fixture':7},'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (a.out/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n',encoding='utf-8')
    p=subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(a.out/'before_natural.json'),str(a.out/'native.json'),'45','2'],cwd=ROOT,capture_output=True,text=True)
    assert (a.out/'native.json').exists(),p.stderr
    print((a.out/'native.json').read_text(encoding='utf-8'))


if __name__=='__main__':main()
