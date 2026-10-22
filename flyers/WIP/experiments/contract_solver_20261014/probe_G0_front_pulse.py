"""Seven-glue T0 with a G0-carried observer and an H2 glazed relay.

Relative motion should suppress the early G0 observer pulses. All moves
except T0 pull0 and push4 are supplied; this is a component experiment.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
ROOT=Path(__file__).resolve().parents[4]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('out',type=Path)
    ap.add_argument('--insulated-pusher',action='store_true')
    ap.add_argument('--deep-G0-route',action='store_true',help='Replace the fixed G0 root by a five-cell detour avoiding the passive pusher')
    ap.add_argument('--front-insulated',action='store_true',help='Face the passive pusher toward the powered relay so front-side power is excluded')
    ap.add_argument('--observer-pusher',action='store_true',help='Use a nonconducting observer aimed into the clear -Y lane instead of an activating piston')
    ap.add_argument('--T0-detour',action='store_true',help='Nine-cell T0 route keeps the sticky out of the late normal push set')
    ap.add_argument('--T0-glazed-bridge',action='store_true',help='Make the forward-obstruction bridge nonadhesive to avoid recruiting the sticky at late push4')
    ap.add_argument('--dual-output',action='store_true',help='Separate sticky/normal power contacts; eight T0 cells and six G0 glue')
    ap.add_argument('--dual-clear-support',action='store_true',help='Move the sticky support out of T0 late-target contact')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    f=Flyer(push_limit=12)
    shift=lambda p:(p[0],p[1]+(2 if a.deep_G0_route and not a.dual_output else 1),p[2])
    t={(15,0,11),(15,1,11),(16,1,11),(17,1,11),(18,1,11),(19,1,11),(19,1,12)}
    if a.T0_detour:t={(15,0,11),(15,1,11),(16,1,11),(16,2,11),(17,2,11),(18,2,11),(19,2,11),(19,1,11),(19,1,12)}
    g={(17,0,10),(17,-1,10),(17,-1,11),(17,-1,12),(17,-1,13)}
    if a.deep_G0_route:g={(17,-1,11),(17,-2,11),(17,-2,12),(17,-2,13),(17,-1,13)}
    for p in t|g:f.set(shift(p),Block(Kind.SLIME))
    if a.T0_glazed_bridge:f.set(shift((18,1,11)),Block(Kind.GLAZED_TERRACOTTA))
    h=(15,0,12) if a.insulated_pusher else (16,0,12)
    if a.insulated_pusher:f.set(shift((16,0,12)),Block.observer(3,powered=False) if a.observer_pusher else Block.piston(0 if a.front_insulated else 4,sticky=False,state=0))
    for p in [(16,2,12),h]:f.set(shift(p),Block(Kind.HONEY))
    f.set(shift((17,0,12)),Block(Kind.GLAZED_TERRACOTTA))
    f.set(shift((17,0,13)),Block.observer(5,powered=False))
    for p,d,arm in [((17,0,11),1,(16,0,11)),((17,1,12),0,(18,1,12))]:
        f.set(shift(p),Block.piston(d,sticky=d==1,state=2));f.set(shift(arm),Block(Kind.PISTON_ARM));f.set_piston_blocks(shift(p),[shift(arm)])
    if a.dual_output:
        assert a.insulated_pusher and a.deep_G0_route and a.observer_pusher
        f=Flyer(push_limit=12)
        t={(15,0,11),(15,0,10),(15,1,10),(16,1,10),(17,1,10),(18,1,10),(19,1,10),(19,1,11)}
        g={(18,0,11),(18,-1,11),(18,-1,12),(18,-1,13),(18,0,13),(18,1,13)}
        if a.dual_clear_support:g.remove((18,0,11));g.add((17,-1,11))
        for p in t|g:f.set(shift(p),Block(Kind.SLIME))
        h=(15,0,12)
        for y in (0,1):
            f.set(shift((15,y,12)),Block(Kind.HONEY))
            f.set(shift((16,y,12)),Block.observer(3,powered=False))
            f.set(shift((17,y,12)),Block(Kind.GLAZED_TERRACOTTA))
            f.set(shift((17,y,13)),Block.observer(5,powered=False))
        f.set(shift((16,2,11)),Block(Kind.HONEY))
        for p,d,arm in [((17,0,11),1,(16,0,11)),((17,1,11),0,(18,1,11))]:
            f.set(shift(p),Block.piston(d,sticky=d==1,state=2));f.set(shift(arm),Block(Kind.PISTON_ARM));f.set_piston_blocks(shift(p),[shift(arm)])
    f.save(a.out/'problem.flyer');assert Flyer.load(a.out/'problem.flyer')._cells==f._cells
    spec=[('G0',shift((17,-1,11) if a.deep_G0_route else (17,-1,10)),'wmmmw',[None,'supplied','supplied','supplied',None]),
          ('T0',shift((15,0,11)),'mwwmm',['internal',None,None,'supplied','internal']),
          ('X0',shift((16,2,12)),'mmmww',['supplied']*3+[None]*2),
          ('H2',shift(h),'mmmww',['supplied']*3+[None]*2)]
    if a.dual_output:
        spec[0]=(spec[0][0],shift((17,-1,11) if a.dual_clear_support else (18,-1,11)),spec[0][2],spec[0][3])
        spec[2]=(spec[2][0],shift((16,2,11)),spec[2][2],spec[2][3])
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
    (a.out/'preparation.json').write_text(json.dumps({'scope':__doc__,'glazed_relay':True,'T0_glue':sorted(map(shift,t)),'G0_glue':sorted(map(shift,g)),'observer_carrier':'G0','insulated_pusher':a.insulated_pusher,'deep_G0_route':a.deep_G0_route,'front_insulated':a.front_insulated,'observer_pusher':a.observer_pusher,'T0_detour':a.T0_detour,'T0_glazed_bridge':a.T0_glazed_bridge,'dual_output':a.dual_output,'dual_clear_support':a.dual_clear_support,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')
    (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    proc=subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(a.out/'before_natural.json'),str(a.out/'native.json'),'30','2'],cwd=ROOT,capture_output=True)
    assert (a.out/'native.json').exists(),proc.stderr
    print((a.out/'native.json').read_text(encoding='utf-8'))


if __name__=='__main__':main()
