"""Targeted X1 column/source relocation to free the rear observer corridor.

Keep seven X1 honey, its rear pull target and foreign-normal pickup. Move
both own normal rows and source together; replace X0 leaf by the planned
sticky. Rear motion stays entirely supplied: this is not pull integration.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
from assemble import Flyer,body_of
from fastflyer import Block,Kind
ROOT=Path(__file__).resolve().parents[4]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    ap.add_argument('--x0-control',choices=['sticky','remove'],default='sticky')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    f=Flyer.load(a.base/'problem.flyer')
    c=json.loads((a.base/'before_natural.json').read_text())
    p=next(p for p in c['ports'] if p['name']=='X1');oldglue=body_of(f._cells,tuple(p['at']))
    assert len(oldglue)==7
    removed=oldglue|{(14,5,10),(15,6,11),(16,6,11),(16,6,10)}
    for q in removed:f._cells.pop(q)
    glue={(16,6,12),(17,6,12),(17,5,12),(17,5,11),(17,5,10),(17,5,9),(17,4,9)}
    added={**{q:Block(Kind.HONEY) for q in glue},(16,5,9):Block(Kind.REDSTONE_BLOCK),
           (14,4,9):Block.piston(0),(15,5,10):Block.piston(0,state=2),(16,5,10):Block(Kind.PISTON_ARM)}
    assert not set(added)&f._cells.keys()
    assert f._cells[(14,5,11)].kind==Kind.SLIME
    if a.x0_control=='sticky':f.set((14,5,11),Block.piston(1,sticky=True))
    else:f._cells.pop((14,5,11))
    for q,b in added.items():f.set(q,b)
    assert body_of(f._cells,(17,6,12))==glue
    assert len(body_of(f._cells,(14,4,11)))==6
    f.save(a.out/'problem.flyer');assert Flyer.load(a.out/'problem.flyer')._cells==f._cells
    (a.out/'drive.txt').write_bytes((a.base/'drive.txt').read_bytes())
    for order in ['before_natural','after_natural','interleaved']:
        c=json.loads((a.base/f'{order}.json').read_text());c['name']=a.out.name
        next(p for p in c['ports'] if p['name']=='X1')['at']=[17,6,12]
        (a.out/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
    prep={'scope':__doc__,'base':str(a.base),'old_X1_glue':sorted(oldglue),'new_X1_glue':sorted(glue),
          'first_normal':[14,4,9],'late_normal':[15,5,10],'source':[16,5,9],
          'X0_leaf_replaced':[14,5,11],'X0_control':a.x0_control,'rear_inputs_still_supplied':[2,3,4],
          'carriage':'first on X0 at0/1/2; late on X0 at1/2 and X1 at3; source on X1 at0/3/4',
          'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.base/'problem.flyer',Path(__file__)]}}
    (a.out/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n',encoding='utf-8')
    (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(a.out/'before_natural.json'),str(a.out/'native.json'),'45','2'],cwd=ROOT,capture_output=True)
    print((a.out/'native.json').read_text())


if __name__=='__main__':main()
