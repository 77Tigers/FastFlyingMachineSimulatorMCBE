"""Test X0 pull2 using an existing T1 source and a T0-carried sticky.

Add T0 honey17,3,12 and sticky17,3,11. At fire1 the sticky is18,3,11
next to the natural T1 RB18,2,11. At pull2 it reaches X0 glue16,3,11.
Only X0 slot2 is removed from supplied inputs. Other loaded hardware stays.
"""
import os as _research_os
import argparse,hashlib,json,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
ROOT=Path(__file__).resolve().parents[4]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    ap.add_argument('--lower',action='store_true',help='Use existing T0 glue and swap one X0 leaf, avoiding the upper X1 glue merge')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    f=Flyer.load(a.base/'problem.flyer');added={(17,3,12):Block(Kind.HONEY),(17,3,11):Block.piston(1,sticky=True)}
    removed=[];target=(14,3,11)
    if a.lower:
        removed=[(14,2,9)];target=(14,1,11)
        assert f._cells.pop(removed[0]).kind==Kind.SLIME
        added={(14,1,11):Block(Kind.SLIME),(17,1,11):Block.piston(1,sticky=True)}
    assert not set(added)&set(f._cells)
    for p,b in added.items():f.set(p,b)
    f.save(a.out/'problem.flyer');assert Flyer.load(a.out/'problem.flyer')._cells==f._cells
    c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
    p=next(p for p in c['ports'] if p['name']=='X0');assert p['word']=='mmmww'
    remove={(10*cy+4,p['at'][0]+3*cy+2,p['at'][1],p['at'][2]) for cy in range(3)}
    rows=[tuple(map(int,s.split())) for s in (a.base/'drive.txt').read_text(encoding='utf-8').splitlines()]
    assert sum(row[:4] in remove for row in rows)==3
    (a.out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in rows if row[:4] not in remove),encoding='utf-8')
    for order in ('before_natural','after_natural','interleaved'):
        c=json.loads((a.base/f'{order}.json').read_text(encoding='utf-8'));c['name']=a.out.name
        next(p for p in c['ports'] if p['name']=='X0')['provenance'][2]='internal'
        (a.out/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
    prep={'scope':__doc__,'base':str(a.base),'added_cells':[[*p,b.encode()] for p,b in added.items()],
          'target_contact':target,'source':[18,2,11],'removed_cells':removed,'lower_variant':a.lower,
          'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                    [a.base/'problem.flyer',a.base/'drive.txt',a.base/'before_natural.json',Path(__file__)]}}
    (a.out/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n',encoding='utf-8')
    run=subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(a.out/'before_natural.json'),str(a.out/'native.json'),'90','2'],cwd=ROOT,capture_output=True,text=True)
    assert (a.out/'native.json').exists(),run.stderr
    print((a.out/'native.json').read_text(encoding='utf-8'))


if __name__=='__main__':main()
