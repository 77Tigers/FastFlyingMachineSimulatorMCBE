"""Close T2 pull1 with a G2 sticky and explicitly supplied H2 mmmww power.

Correct contact uses sticky=q+3: T2 has advanced once before pull1, while
G2 has not advanced. This adds a boundary source, not a complete flyer.
No T2 observer/passenger is added to its full twelve-cell stroke.
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
    f=Flyer.load(a.base/'problem.flyer');sticky=(25,5,13);rb=(26,5,13)
    for p,b in [(sticky,Block.piston(1,sticky=True)),(rb,Block(Kind.REDSTONE_BLOCK))]:
        assert p not in f._cells;f.set(p,b)
    f.save(a.out/'problem.flyer');assert Flyer.load(a.out/'problem.flyer')._cells==f._cells
    c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
    target=next(p for p in c['ports'] if p['name']=='T2')
    remove={(10*cy+2,target['at'][0]+3*cy+1,target['at'][1],target['at'][2]) for cy in range(3)}
    rows=[tuple(map(int,s.split())) for s in (a.base/'drive.txt').read_text(encoding='utf-8').splitlines()]
    assert sum(row[:4] in remove for row in rows)==3
    rows=[row for row in rows if row[:4] not in remove]
    for cy in range(3):
        for slot in (0,1,2):rows.append((10*cy+2*slot,rb[0]+3*cy+slot,rb[1],rb[2],1))
    (a.out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
    for order in ('before_natural','after_natural','interleaved'):
        c=json.loads((a.base/f'{order}.json').read_text(encoding='utf-8'));c['name']=a.out.name
        next(p for p in c['ports'] if p['name']=='T2')['provenance'][1]='internal'
        c['ports'].append({'name':'H2_power','role':'input','at':rb,'word':'mmmww',
                           'provenance':['supplied','supplied','supplied',None,None]})
        (a.out/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
    prep={'scope':__doc__,'base':str(a.base),'sticky':sticky,'H2_source':rb,
          'target_contact':[22,5,13],'fire_slot':0,'pull_slot':1,
          'contact_check':{'T2_prefix_at_pull':1,'G2_prefix_at_pull':0,'sticky_minus_two':23,'target_after_prefix':23},
          'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                    [a.base/'problem.flyer',a.base/'drive.txt',a.base/'before_natural.json',Path(__file__)]}}
    (a.out/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n',encoding='utf-8')
    run=subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(a.out/'before_natural.json'),str(a.out/'native.json'),'90','2'],cwd=ROOT,capture_output=True,text=True)
    assert (a.out/'native.json').exists(),run.stderr
    print((a.out/'native.json').read_text(encoding='utf-8'))


if __name__=='__main__':main()
