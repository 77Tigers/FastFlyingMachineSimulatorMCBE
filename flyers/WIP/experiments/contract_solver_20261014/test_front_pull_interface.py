"""Replace T1's supplied third stroke with a G1-carried sticky and H1 RB input.

Three existing G1 glue lanes permit attached sticky bases two cells ahead of
T1's target. Screen five direct H1 power positions per lane. H1 source motion
remains supplied (wwmmm, cap1); H1 geometry and a complete flyer are not claimed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
from assemble import Flyer
from fastflyer import Block,Kind

ROOT=Path(__file__).resolve().parents[4]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    initial=Flyer.load(a.base/'problem.flyer')
    c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
    target=next(p for p in c['ports'] if p['name']=='T1')
    remove={(cy*10+6,target['at'][0]+3*cy+2,target['at'][1],target['at'][2]) for cy in range(3)}
    old_rows=[tuple(map(int,s.split())) for s in (a.base/'drive.txt').read_text(encoding='utf-8').splitlines()]
    assert sum(row[:4] in remove for row in old_rows)==3
    offsets=[(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]
    deadline=time.monotonic()+120;results=[]
    for i,(y,off) in enumerate((y,off) for y in [2,3,4] for off in offsets):
        if time.monotonic()>=deadline:break
        sticky=(22,y,11);rb=(24+off[0],y+off[1],11+off[2])
        if sticky in initial._cells or rb in initial._cells:continue
        assert (22,y,10) in initial._cells
        out=a.out/f'case{i:02d}';out.mkdir()
        f=Flyer.load(a.base/'problem.flyer')
        f.set(sticky,Block.piston(1,sticky=True));f.set(rb,Block(Kind.REDSTONE_BLOCK))
        f.save(out/'problem.flyer');assert Flyer.load(out/'problem.flyer')._cells==f._cells
        rows=[row for row in old_rows if row[:4] not in remove]
        for cy in range(3):
            for slot in [2,3,4]:rows.append((cy*10+2*slot,rb[0]+3*cy+slot-2,rb[1],rb[2],1))
        (out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
        for order in ['before_natural','after_natural','interleaved']:
            c=json.loads((a.base/f'{order}.json').read_text(encoding='utf-8'));c['name']=f'G1_T1_pull_{i}'
            next(p for p in c['ports'] if p['name']=='T1')['provenance'][3]='internal'
            c['ports'].append({'name':'H1_power','at':rb,'role':'input','word':'wwmmm','provenance':[None,None,'supplied','supplied','supplied']})
            (out/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
        (out/'preparation.json').write_text(json.dumps({'scope':__doc__,'base':str(a.base),'sticky_at':sticky,'source_at':rb,
            'source_word':'wwmmm','sticky_word':'mmwwm','fire_slot':2,'pull_slot':3,
            'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.base/'problem.flyer',a.base/'before_natural.json',a.base/'drive.txt',Path(__file__)]}},indent=2)+'\n',encoding='utf-8')
        run=subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(out/'before_natural.json'),str(out/'native.json'),str(max(1,deadline-time.monotonic())),'2'],cwd=ROOT,capture_output=True,text=True)
        assert (out/'native.json').exists(),run.stderr
        r=json.loads((out/'native.json').read_text(encoding='utf-8'));results.append({'case':i,'sticky_at':sticky,'source_at':rb,**r})
        print(json.dumps({'case':i,'verified':r['verified'],'failure':r['failure']}),flush=True)
        if r['verified']:break
    (a.out/'report.json').write_text(json.dumps({'scope':__doc__,'results':results},indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
