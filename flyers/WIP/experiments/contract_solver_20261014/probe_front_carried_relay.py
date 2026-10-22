"""Four-body front-carried stone relay; T0 pull0/push4 natural.

G0 wmmmw carries only the sticky. X0 mmmww carries late normal1/2,
then T0 mwwmm recovers it at3. H2 mmmww carries the nonsticky output
stone. Nominal normal/sticky pickups on H2 may exchange; native loads
must account for them. All remaining body moves are explicitly supplied.
"""
import os as _research_os
import argparse,hashlib,json,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
ROOT=Path(__file__).resolve().parents[4]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('out',type=Path)
    ap.add_argument('--glazed-relay',action='store_true',help='Push the glazed output from behind without side adhesion to T0')
    ap.add_argument('--clear-input-lane',action='store_true',help='Route T0 around H2 initial position so pull0 cannot supply the H2 move')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    f=Flyer(push_limit=12)
    t={(15,0,11),(15,1,11),(15,1,12),(16,1,12),(17,1,12),(17,2,12),(18,2,12),(19,2,12),(19,2,11)}
    if a.clear_input_lane:t.remove((15,1,11));t.add((15,0,12))
    for p in t:f.set(p,Block(Kind.SLIME))
    f.set((17,0,10),Block(Kind.SLIME))
    for p in [(16,3,11),(16,1,11)]:f.set(p,Block(Kind.HONEY))
    f.set((17,1,11),Block(Kind.GLAZED_TERRACOTTA if a.glazed_relay else Kind.SMOOTH_STONE));f.set((18,1,12),Block.observer(5,powered=True))
    for p,d,arm in [((17,0,11),1,(16,0,11)),((17,2,11),0,(18,2,11))]:
        f.set(p,Block.piston(d,sticky=d==1,state=2));f.set(arm,Block(Kind.PISTON_ARM));f.set_piston_blocks(p,[arm])
    f.save(a.out/'problem.flyer');assert Flyer.load(a.out/'problem.flyer')._cells==f._cells
    spec=[('G0',(17,0,10),'wmmmw',[None,'supplied','supplied','supplied',None]),
          ('T0',(15,0,11),'mwwmm',['internal',None,None,'supplied','internal']),
          ('X0',(16,3,11),'mmmww',['supplied']*3+[None]*2),
          ('H2',(16,1,11),'mmmww',['supplied']*3+[None]*2)]
    rows=[]
    for name,p,word,prov in spec:
        for cy in range(3):
            for slot,v in enumerate(prov):
                if v=='supplied':rows.append((cy*10+slot*2,p[0]+cy*3+word[:slot].count('m'),*p[1:],12))
    (a.out/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
    c={'version':1,'name':a.out.name,'flyer':'problem.flyer','period_ticks':10,'advance':3,'cycles':3,'recurrence':'bounded',
       'ports':[{'name':n,'at':p,'role':'input','word':w,'provenance':v} for n,p,w,v in spec],
       'required_cells':[],'boundary_envelope':{'min':[10,0,8],'max':[27,6,15]},'prescribed_script':'drive.txt'}
    for order in ['before_natural','after_natural','interleaved']:(a.out/f'{order}.json').write_text(json.dumps({**c,'prescribed_order':order},indent=2)+'\n',encoding='utf-8')
    (a.out/'preparation.json').write_text(json.dumps({'scope':__doc__,'glazed_relay':a.glazed_relay,'clear_input_lane':a.clear_input_lane,'T0_glue':sorted(t),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')
    (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    proc=subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(a.out/'before_natural.json'),str(a.out/'native.json'),'30','2'],cwd=ROOT,capture_output=True)
    assert (a.out/'native.json').exists(),proc.stderr
    print((a.out/'native.json').read_text(encoding='utf-8'))


if __name__=='__main__':main()
