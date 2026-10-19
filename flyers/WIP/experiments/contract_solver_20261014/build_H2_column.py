"""Load the exact budgeted H2 mmmww ordinary-column hypothesis.

H2's provided source is retained, with real glue and three normal pistons.
G2 gains two carrier cells. Remaining left-boundary moves stay supplied.
Native verification, not nominal piston roles, decides whether it works.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
ROOT=Path(__file__).resolve().parents[4]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    spec_path=a.base/'H2_natural_column_hypothesis.json'
    spec=json.loads(spec_path.read_text(encoding='utf-8'))
    f=Flyer.load(a.base/'problem.flyer');added={}
    for key,kind in [('G2_added_HONEY',Kind.HONEY),('H2_SLIME',Kind.SLIME)]:
        for p in spec[key]:added[tuple(p)]=Block(kind)
    for p in spec['normals_initial_state0_facing_X']:added[tuple(p)]=Block.piston(0)
    assert not set(added)&set(f._cells)
    for p,b in added.items():f.set(p,b)
    f.save(a.out/'problem.flyer');assert Flyer.load(a.out/'problem.flyer')._cells==f._cells
    c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
    port=next(p for p in c['ports'] if p['name']=='H2_power')
    assert port['word']=='mmmww' and port['at']==spec['H2_retained_RB']
    remove={(10*cy+2*s,port['at'][0]+3*cy+s,port['at'][1],port['at'][2]) for cy in range(3) for s in range(3)}
    rows=[tuple(map(int,s.split())) for s in (a.base/'drive.txt').read_text(encoding='utf-8').splitlines()]
    assert sum(row[:4] in remove for row in rows)==9
    (a.out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in rows if row[:4] not in remove),encoding='utf-8')
    for order in ('before_natural','after_natural','interleaved'):
        c=json.loads((a.base/f'{order}.json').read_text(encoding='utf-8'));c['name']=a.out.name
        next(p for p in c['ports'] if p['name']=='H2_power')['provenance']=['internal']*3+[None,None]
        for axis in range(3):
            c['boundary_envelope']['min'][axis]=min(c['boundary_envelope']['min'][axis],min(p[axis] for p in f._cells))
            c['boundary_envelope']['max'][axis]=max(c['boundary_envelope']['max'][axis],max(p[axis] for p in f._cells))
        (a.out/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
    info={'scope':__doc__,'base':str(a.base),'added_cells':[[*p,b.encode()] for p,b in added.items()],
          'hypothesis':spec,'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
          [a.base/'problem.flyer',a.base/'drive.txt',a.base/'before_natural.json',spec_path,Path(__file__)]}}
    (a.out/'preparation.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8')
    run=subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(a.out/'before_natural.json'),str(a.out/'native.json'),'90','2'],cwd=ROOT,capture_output=True,text=True)
    assert (a.out/'native.json').exists(),run.stderr
    print((a.out/'native.json').read_text(encoding='utf-8'))


if __name__=='__main__':main()
