"""Test G0 first normal carried by X0 at0 and G0 at2/3, not T0.

All X0 moves and G0 moves2/3 supplied. Only G0 push1 natural. A proposed
passenger transfer, not loaded integration or a complete flyer.
"""
import os as _research_os
import argparse,hashlib,json,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
ROOT=Path(__file__).resolve().parents[4]

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    f=Flyer(push_limit=12);x=(14,1,12);g=(16,1,13);normal=(14,1,13);source=(15,0,13)
    honey={g,(16,0,13),(16,2,13),(15,2,13),(14,2,13)}
    f.set(x,Block(Kind.SLIME))
    for p in honey:f.set(p,Block(Kind.HONEY))
    f.set(normal,Block.piston(0));f.set(source,Block(Kind.REDSTONE_BLOCK));f.save(a.out/'problem.flyer')
    assert Flyer.load(a.out/'problem.flyer')._cells==f._cells
    spec=[('X0',x,'mmmww',['supplied']*3+[None]*2),('G0',g,'wmmmw',[None,'internal','supplied','supplied',None])]
    rows=[]
    for name,p,word,provenance in spec:
        for cy in range(3):
            for slot,v in enumerate(provenance):
                if v=='supplied':rows.append((cy*10+slot*2,p[0]+cy*3+word[:slot].count('m'),*p[1:],12))
    (a.out/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
    c={'version':1,'name':a.out.name,'flyer':'problem.flyer','period_ticks':10,'advance':3,'cycles':3,'recurrence':'bounded',
       'ports':[{'name':n,'at':p,'role':'input','word':w,'provenance':v} for n,p,w,v in spec],
       'required_cells':[],'boundary_envelope':{'min':[10,0,9],'max':[23,6,17]},'prescribed_script':'drive.txt'}
    for order in ['before_natural','after_natural','interleaved']:(a.out/f'{order}.json').write_text(json.dumps({**c,'prescribed_order':order},indent=2)+'\n',encoding='utf-8')
    (a.out/'preparation.json').write_text(json.dumps({'scope':__doc__,'honey':sorted(honey),'normal':normal,'source':source,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')
    (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    proc=subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(a.out/'before_natural.json'),str(a.out/'native.json'),'30','2'],cwd=ROOT,capture_output=True)
    assert (a.out/'native.json').exists(),proc.stderr
    print((a.out/'native.json').read_text(encoding='utf-8'))
if __name__=='__main__':main()
