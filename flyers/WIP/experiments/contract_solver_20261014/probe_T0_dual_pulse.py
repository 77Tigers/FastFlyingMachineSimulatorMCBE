"""One T0 observer powers a G0 -X sticky and G0-carried +X late normal.

Isolated timing fixture: T0 pull0/push4 natural; T0 push3 and G0 1/2/3
supplied. Optional reversed slot3 injection tests a same-stroke obstruction
before calling the supplied interface evidence for natural integration.
"""
import os as _research_os
import argparse,hashlib,json,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
ROOT=Path(__file__).resolve().parents[4]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    ap.add_argument('--reverse-slot3',action='store_true');ap.add_argument('--compact-route',action='store_true')
    ap.add_argument('--solid-bridge',action='store_true',help='Use a honey output cell between the two actors; pistons do not conduct hard power')
    ap.add_argument('--nonsticky-relay',action='store_true',help='Stone output cell avoids picking up the unfired sticky; alternate carrier/support route')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    f=Flyer.load(a.base/'problem.flyer');old=(17,0,11);f.remove(old)
    carrier=(17,0,10)
    for p in [(17,0,10),(17,1,10)]:f.set(p,Block(Kind.SLIME))
    f.set(old,Block.piston(0,state=2));f.set((18,0,11),Block(Kind.PISTON_ARM));f.set_piston_blocks(old,[(18,0,11)])
    for p in [(19,0,11),(19,1,11),(19,2,11),(19,3,11)]:f.set(p,Block(Kind.HONEY))
    if a.compact_route:
        for p,b in list(f._cells.items()):
            if b.kind==Kind.HONEY:f.remove(p)
        for p in [(15,1,11),(15,1,12),(16,1,12),(17,1,12),(18,1,12),(18,2,12),(19,0,11),(19,1,11),(19,1,12)]:f.set(p,Block(Kind.HONEY))
    target=(15,1,11)
    if a.solid_bridge:
        f=Flyer(push_limit=12);carrier=(17,1,10);target=(15,0,11)
        for p in [(17,0,10),(17,1,10),(17,2,10)]:f.set(p,Block(Kind.SLIME))
        for p in [(15,0,11),(15,1,11),(16,1,11),(17,1,11),(18,1,11),(19,1,11),(19,2,11)]:f.set(p,Block(Kind.HONEY))
        f.set((18,1,12),Block.decode(423)) # powered -Z observer; preserves phase-boundary pulse flag
        for p,d,arm in [((17,0,11),1,(16,0,11)),((17,2,11),0,(18,2,11))]:
            f.set(p,Block.piston(d,sticky=d==1,state=2));f.set(arm,Block(Kind.PISTON_ARM));f.set_piston_blocks(p,[arm])
    if a.nonsticky_relay:
        f=Flyer(push_limit=12);carrier=(16,1,10);target=(15,0,11)
        for p in [(17,0,10),(16,0,10),(16,1,10),(16,2,10),(17,2,10)]:f.set(p,Block(Kind.SLIME))
        for p in [(15,0,11),(15,1,11),(16,1,11),(16,1,12),(17,1,12),(18,1,12),(19,1,12),(19,1,11),(19,2,11)]:f.set(p,Block(Kind.HONEY))
        f.set((18,1,11),Block(Kind.SMOOTH_STONE));f.set((17,1,11),Block.observer(0,powered=True))
        for p,d,arm in [((17,0,11),1,(16,0,11)),((17,2,11),0,(18,2,11))]:
            f.set(p,Block.piston(d,sticky=d==1,state=2));f.set(arm,Block(Kind.PISTON_ARM));f.set_piston_blocks(p,[arm])
    f.save(a.out/'problem.flyer');assert Flyer.load(a.out/'problem.flyer')._cells==f._cells
    spec=[('G0_carrier',carrier,'wmmmw',[None,'supplied','supplied','supplied',None]),
          ('T0_target',target,'mwwmm',['internal',None,None,'supplied','internal'])]
    rows=[]
    for name,p,word,prov in spec:
        for cycle in range(3):
            for slot,v in enumerate(prov):
                if v=='supplied':rows.append((10*cycle+2*slot,p[0]+3*cycle+word[:slot].count('m'),*p[1:],12))
    rows.sort(key=lambda r:(r[0],-r[1] if a.reverse_slot3 and r[0]%10==6 else r[1]))
    (a.out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in rows),encoding='utf-8')
    c={'version':1,'name':a.out.name,'flyer':'problem.flyer','period_ticks':10,'advance':3,'cycles':3,'recurrence':'bounded',
       'ports':[{'name':n,'at':p,'role':'input','word':w,'provenance':v} for n,p,w,v in spec],
       'required_cells':[],'boundary_envelope':{'min':[10,0,9],'max':[26,5,13]},'prescribed_script':'drive.txt'}
    for order in ['before_natural','after_natural','interleaved']:(a.out/f'{order}.json').write_text(json.dumps({**c,'prescribed_order':order},indent=2)+'\n',encoding='utf-8')
    (a.out/'preparation.json').write_text(json.dumps({'scope':__doc__,'reverse_slot3':a.reverse_slot3,'compact_route':a.compact_route,'solid_bridge':a.solid_bridge,'nonsticky_relay':a.nonsticky_relay,'base':str(a.base),'base_sha256':hashlib.sha256((a.base/'problem.flyer').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')
    (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    proc=subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(a.out/'before_natural.json'),str(a.out/'native.json'),'30','2'],cwd=ROOT,capture_output=True)
    assert (a.out/'native.json').exists(),proc.stderr
    print((a.out/'native.json').read_text(encoding='utf-8'))


if __name__=='__main__':main()
