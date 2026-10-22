"""Four bounded G1 constructions: two supported normal pairs, two glue materials.

Adds a real three-glue G1 carrier and its two normal pushes to the relocated
rear power interface. Only G1's third stroke stays supplied (cap12). No front
puller or full flyer is claimed. Native verification is a screen only.
"""
import os as _research_os
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from assemble import Flyer
from fastflyer import Block,Kind

ROOT=Path(__file__).resolve().parents[4]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    ap.add_argument('--reroute-t1',action='store_true',help='Replace the obstructing T1 bridge and trim its tail')
    ap.add_argument('--retain-tail',action='store_true',help='Keep the T2 recovery rail; optionally remove its one leaf')
    ap.add_argument('--transfer-t2-pusher',action='store_true',help='Add X2 pickup at18,4,14 for the T2 first pusher')
    ap.add_argument('--lateral-handoff',action='store_true',help='Use original rear source and a six-glue T1 lateral pickup')
    ap.add_argument('--forward-bridge',action='store_true',help='Keep the new T1 bridge ahead of the X1 pull corridor')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    report=[]
    variants=([(20,2,11),k,tail] for k in [Kind.SLIME,Kind.HONEY] for tail in [True,False]) if a.reroute_t1 else ((p,k,None) for p in [(20,2,11),(20,3,10)] for k in [Kind.SLIME,Kind.HONEY])
    if a.lateral_handoff:variants=(( (21,4,10),k,None) for k in [Kind.SLIME,Kind.HONEY])
    for i,(second,material,tail) in enumerate(variants):
        out=a.out/f'case{i:02d}';out.mkdir()
        f=Flyer.load(a.base/'problem.flyer')
        if a.transfer_t2_pusher:
            assert (18,4,14) not in f._cells
            f.set((18,4,14),Block(Kind.SLIME))
        reroute=None
        if a.lateral_handoff:
            removed=[(19,3,14),(19,2,14),(19,2,13)]
            bridge=[(19,3,11),(19,4,11),(20,4,11)]
            if a.forward_bridge:bridge=[(20,2,11),(20,3,11),(20,4,11)]
            for p in removed:assert f._cells.pop(p).kind==Kind.SLIME
            for p in bridge:
                assert p not in f._cells
                f.set(p,Block(Kind.SLIME))
            reroute={'removed':removed,'added':bridge,'resulting_T1_glue':6}
        elif a.reroute_t1:
            removed=([(19,2,11)]+([] if tail else [(19,3,14)])) if a.retain_tail else [(19,2,11),(19,2,14),(19,3,14)]+([] if tail else [(19,2,13)])
            bridge=[(19,1,10),(19,1,11),(19,1,12),(18,1,11)]
            for p in removed:
                assert f._cells.pop(p).kind==Kind.SLIME
            for p in bridge:
                assert p not in f._cells
                f.set(p,Block(Kind.SLIME))
            reroute={'removed':removed,'added':bridge,'resulting_T1_glue':6-len(removed)+len(bridge)}
        glue=[(21,3,11),(21,3,12),(second[0]+1,second[1],second[2])]
        first=(19,3,12)
        if a.lateral_handoff:
            glue=[(22,2,10),(22,3,10),(22,4,10)]
            first=(20,2,10)
        added={p:Block(material) for p in glue}
        added.update({first:Block.piston(0,state=2),(first[0]+1,first[1],first[2]):Block(Kind.PISTON_ARM),second:Block.piston(0)})
        assert not set(added)&set(f._cells)
        for p,b in added.items():f.set(p,b)
        f.save(out/'problem.flyer');assert Flyer.load(out/'problem.flyer')._cells==f._cells
        c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
        port=next(p for p in c['ports'] if p['name']=='G1_power');rb=port['at']
        remove={(10*cy+2*s,rb[0]+3*cy+port['word'][:s].count('m'),rb[1],rb[2]) for cy in range(3) for s in [0,4]}
        rows=[tuple(map(int,s.split())) for s in (a.base/'drive.txt').read_text(encoding='utf-8').splitlines()]
        rows=[row[:4]+(12,) if row[1:4]==(rb[0]+3*(row[0]//10)+port['word'][:(row[0]%10)//2].count('m'),rb[1],rb[2]) else row for row in rows if row[:4] not in remove]
        (out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in rows),encoding='utf-8')
        for order in ['before_natural','after_natural','interleaved']:
            c=json.loads((a.base/f'{order}.json').read_text(encoding='utf-8'));c['name']=f'G1_three_glue_{i}'
            port=next(p for p in c['ports'] if p['name']=='G1_power')
            for s in [0,4]:port['provenance'][s]='internal'
            (out/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
        (out/'preparation.json').write_text(json.dumps({'scope':__doc__,'base':str(a.base),'glue':glue,'material':material.name,'first_normal':first,'second_normal':second,'T1_reroute':reroute,'X2_T2_pickup':[18,4,14] if a.transfer_t2_pusher else None,
            'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.base/'problem.flyer',a.base/'before_natural.json',a.base/'drive.txt',Path(__file__)]}},indent=2)+'\n',encoding='utf-8')
        run=subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(out/'before_natural.json'),str(out/'native.json'),'45','2'],cwd=ROOT,capture_output=True,text=True)
        assert (out/'native.json').exists(),run.stderr
        r=json.loads((out/'native.json').read_text(encoding='utf-8'));report.append({'case':i,**r})
        print(json.dumps({'case':i,'verified':r['verified'],'failure':r['failure']}),flush=True)
        if r['verified']:break
    (a.out/'report.json').write_text(json.dumps({'scope':__doc__,'results':report},indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
