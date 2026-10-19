"""Bounded X1 rear-pull test using four screened, supplied G1 power cells.

Keep the four natural columns and add the exact scaffold X1 sticky. Replace
the supplied X1 third stroke by natural pulling. G1 is a one-cell supplied
power interface, not constructed front hardware or a complete flyer.
"""
import argparse
import json
from pathlib import Path
import subprocess
import time
from assemble import Flyer
from fastflyer import Block,Kind

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    ap.add_argument('--source-index',type=int,choices=range(4),help='Test one previously screened position only')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    info=json.loads((a.base/'rear_power_screen.json').read_text(encoding='utf-8'))['options']['X1']
    ports=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))['ports'];xp=next(p for p in ports if p['name']=='X1')
    deadline=time.monotonic()+120;results=[]
    for i,rb in enumerate(info['source_candidates']):
        if a.source_index is not None and i!=a.source_index:continue
        if time.monotonic()>=deadline:break
        out=a.out/f'case{i:02d}';out.mkdir()
        f=Flyer.load(a.base/'problem.flyer')
        q=tuple(info['sticky_at']);assert q not in f._cells and (q[0]-1,q[1],q[2]) not in f._cells and tuple(rb) not in f._cells
        f.set(q,Block.piston(1,sticky=True,state=2));f.set((q[0]-1,q[1],q[2]),Block(Kind.PISTON_ARM));f.set(tuple(rb),Block(Kind.REDSTONE_BLOCK))
        f.save(out/'problem.flyer');assert Flyer.load(out/'problem.flyer')._cells==f._cells
        remove={(cy*10+2*info['sticky_slot'],xp['at'][0]+3*cy+xp['word'][:info['sticky_slot']].count('m'),xp['at'][1],xp['at'][2]) for cy in range(3)}
        rows=[tuple(map(int,s.split())) for s in (a.base/'drive.txt').read_text(encoding='utf-8').splitlines()]
        rows=[row for row in rows if row[:4] not in remove]
        for cy in range(3):
            for slot,c in enumerate(info['source_word']):
                if c=='m':rows.append((10*cy+2*slot,rb[0]+3*cy+info['source_word'][:slot].count('m'),rb[1],rb[2],1))
        (out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
        for order in ('before_natural','after_natural','interleaved'):
            c=json.loads((a.base/f'{order}.json').read_text(encoding='utf-8'));c['name']=f'natural_X1_rear_source{i}'
            p=next(p for p in c['ports'] if p['name']=='X1');p['provenance'][info['sticky_slot']]='internal'
            c['ports'].append({'name':'G1_power','at':rb,'role':'input','word':info['source_word'],'provenance':['supplied' if v=='m' else None for v in info['source_word']]})
            (out/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
        (out/'preparation.json').write_text(json.dumps({'scope':__doc__,'base':str(a.base),'source_at':rb,'sticky_at':q,'source_word':info['source_word']},indent=2)+'\n',encoding='utf-8')
        p=subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(out/'before_natural.json'),str(out/'native.json'),str(max(1,deadline-time.monotonic())),'2'],capture_output=True,text=True,cwd=ROOT)
        r=json.loads((out/'native.json').read_text(encoding='utf-8'));results.append({'case':i,'source_at':rb,**r})
        print(json.dumps({'case':i,'verified':r['verified'],'failure':r['failure']}),flush=True)
        if r['verified']:break
    (a.out/'report.json').write_text(json.dumps({'scope':__doc__,'candidates':results},indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
