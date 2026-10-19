"""Load an existing supplied interface with another scaffold's natural column.

Use exact scaffold normals/initial arms, retain existing hardware, and change
only the added target's two pushes (or selected --slots) from supplied to
internal. Its third stroke remains supplied. No hardware or budget is relaxed.
"""
import argparse
import hashlib
import json
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind

HERE=Path(__file__).resolve().parent


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('scaffold',type=Path);ap.add_argument('target');ap.add_argument('out',type=Path)
    ap.add_argument('--slots',type=int,nargs='+',choices=range(5),help='Load only these scaffold push slots')
    ap.add_argument('--slime',type=int,nargs=3,action='append',default=[],metavar=('X','Y','Z'),help='Add an explicitly budgeted carrier pickup cell')
    a=ap.parse_args(); read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    r=read(a.scaffold);c=read(a.base/'before_natural.json')
    port=next(p for p in c['ports'] if p['name']==a.target)
    reference=c['ports'][0];root=r['glue'][reference['name']][0]
    delta=tuple(x-y for x,y in zip(reference['at'],root))
    actors=[x for x in r['actors'] if x['target']==a.target and x['kind']=='push'];assert len(actors)==2
    if a.slots is not None:
        actors=[x for x in actors if x['slot'] in a.slots]
        assert {x['slot'] for x in actors}==set(a.slots),'requested slot is not a scaffold push'
    slots={x['slot'] for x in actors}
    assert all(port['provenance'][slot]=='supplied' for slot in slots)
    f=Flyer.load(a.base/'problem.flyer');added=[]
    def put(p,b):
        assert p not in f._cells,f'overwriting {p}'
        f.set(p,b);added.append([*p,b.encode()])
    for actor in actors:
        p=tuple(x+d for x,d in zip(actor['at'],delta))
        extended=actor['slot']==4
        put(p,Block.piston(0,state=2 if extended else 0))
        if extended:put((p[0]+1,p[1],p[2]),Block(Kind.PISTON_ARM))
    for p in a.slime:put(tuple(p),Block(Kind.SLIME))
    a.out.mkdir(parents=True,exist_ok=False)
    f.save(a.out/'problem.flyer');assert Flyer.load(a.out/'problem.flyer')._cells==f._cells,'coordinate frame changed'
    remove={(cycle*10+2*slot,port['at'][0]+3*cycle+port['word'][:slot].count('m'),port['at'][1],port['at'][2])
            for cycle in range(c['cycles']) for slot in slots}
    rows=[tuple(map(int,line.split())) for line in (a.base/'drive.txt').read_text(encoding='utf-8').splitlines()]
    assert len([row for row in rows if row[:4] in remove])==len(remove)
    (a.out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in rows if row[:4] not in remove),encoding='utf-8')
    for order in ('before_natural','after_natural','interleaved'):
        c=read(a.base/f'{order}.json');c['name']=a.out.name
        p=next(p for p in c['ports'] if p['name']==a.target)
        for slot in slots:p['provenance'][slot]='internal'
        (a.out/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
    (a.out/'preparation.json').write_text(json.dumps({'scope':__doc__,'base':str(a.base),
        'base_flyer_sha256':hashlib.sha256((a.base/'problem.flyer').read_bytes()).hexdigest(),
        'scaffold_sha256':hashlib.sha256(a.scaffold.read_bytes()).hexdigest(),'added_target':a.target,
        'added_cells':added,'added_slime':a.slime,'normalization_delta':delta,
        'constructor_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'internal_strokes':{p['name']:[i for i,v in enumerate(p['provenance']) if v=='internal'] for p in c['ports']}},indent=2)+'\n',encoding='utf-8')
    print(f'Loaded exact {a.target} column; {len(f._cells)} cells at PL{f.push_limit}')


if __name__=='__main__':main()
