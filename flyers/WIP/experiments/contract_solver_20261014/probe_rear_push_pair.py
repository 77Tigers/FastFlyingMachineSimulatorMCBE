"""Native calibration of two rear pushes with front-carried normal recovery.

Front mmwwm carries both normals at0/1 and the spent first actor at4.
Rear wwmmm carries its source and the unfired normal at2. Rear pushes2/3
are natural; front moves and rear4 stay supplied. Nominal normal firing
identities may exchange. This is an isolated interface, not a complete flyer.
"""
import os as _research_os
import argparse,hashlib,json,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
ROOT=Path(__file__).resolve().parents[4]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('out',type=Path)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    f=Flyer(push_limit=12);front=(11,0,11);rear=(15,2,11)
    fg={(12,0,11),(12,4,11),*((11,y,11) for y in range(5))}
    rg={(15,y,11) for y in [1,2,3]}
    for p in fg:f.set(p,Block(Kind.SLIME))
    for p in rg:f.set(p,Block(Kind.HONEY))
    f.set((14,2,11),Block(Kind.REDSTONE_BLOCK))
    for p in [(12,1,11),(12,3,11)]:f.set(p,Block.piston(0))
    f.save(a.out/'problem.flyer');assert Flyer.load(a.out/'problem.flyer')._cells==f._cells
    rows=[]
    for cy in range(3):
        for slot in [0,1,4]:rows.append((10*cy+2*slot,front[0]+3*cy+[0,1,2,2,2][slot],*front[1:],12))
        rows.append((10*cy+8,rear[0]+3*cy+2,*rear[1:],12))
    (a.out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
    contract={'version':1,'name':a.out.name,'flyer':'problem.flyer','period_ticks':10,'advance':3,'cycles':3,'recurrence':'bounded',
              'ports':[{'name':'front_carrier','role':'input','at':front,'word':'mmwwm','provenance':['supplied','supplied',None,None,'supplied']},
                       {'name':'rear_pickup','role':'input','at':rear,'word':'wwmmm','provenance':[None,None,'internal','internal','supplied']}],
              'required_cells':[],'boundary_envelope':{'min':[9,0,9],'max':[19,6,13]},'prescribed_script':'drive.txt'}
    for order in ['before_natural','after_natural','interleaved']:
        (a.out/f'{order}.json').write_text(json.dumps({**contract,'prescribed_order':order},indent=2)+'\n',encoding='utf-8')
    (a.out/'preparation.json').write_text(json.dumps({'scope':__doc__,'front_glue':sorted(fg),'rear_glue':sorted(rg),'source':[14,2,11],
        'normal_origins':[[12,1,11],[12,3,11]],'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')
    (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(a.out/'before_natural.json'),str(a.out/'native.json'),'30','2'],cwd=ROOT,capture_output=True)
    print((a.out/'native.json').read_text(encoding='utf-8'))


if __name__=='__main__':main()
