"""Construct G1's third pull with an H1 carrier and a G1-carried observer.

H1 motion stays supplied, cap12. Observer moves mmwwm and faces -Y into H1
glue, avoiding the earlier co-carried wwmmm pulse hazard. H1 RB still powers
the T1 pull. This is an unverified construction until checked independently.
"""
import argparse
import hashlib
import json
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    f=Flyer.load(a.base/'problem.flyer')
    added={(23,4,10):Block(Kind.SLIME),(24,4,10):Block(Kind.SLIME),(24,4,11):Block(Kind.SLIME),
           (25,4,11):Block.observer(3,powered=True),(25,3,11):Block(Kind.HONEY),
           (25,3,10):Block.piston(1,sticky=True)}
    assert not set(added)&set(f._cells)
    for p,b in added.items():f.set(p,b)
    f.save(a.out/'problem.flyer');assert Flyer.load(a.out/'problem.flyer')._cells==f._cells
    c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
    g=next(p for p in c['ports'] if p['name']=='G1_power')
    h=next(p for p in c['ports'] if p['name']=='H1_power')
    remove={(10*cy+2,g['at'][0]+3*cy+1,g['at'][1],g['at'][2]) for cy in range(3)}
    h_events={(10*cy+2*slot,h['at'][0]+3*cy+slot-2,h['at'][1],h['at'][2]) for cy in range(3) for slot in [2,3,4]}
    rows=[tuple(map(int,s.split())) for s in (a.base/'drive.txt').read_text(encoding='utf-8').splitlines()]
    assert sum(row[:4] in remove for row in rows)==3
    # A supplied RB alone does not adhere to side glue. Drive the real H1 glue
    # representative so every H1 stroke carries its source and sticky together.
    rows=[(row[0],row[1],3,11,12) if row[:4] in h_events else row for row in rows if row[:4] not in remove]
    (a.out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in rows),encoding='utf-8')
    for order in ['before_natural','after_natural','interleaved']:
        c=json.loads((a.base/f'{order}.json').read_text(encoding='utf-8'));c['name']='G1_H1_observer_pull'
        next(p for p in c['ports'] if p['name']=='G1_power')['provenance'][1]='internal'
        next(p for p in c['ports'] if p['name']=='H1_power')['at']=[25,3,11]
        (a.out/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
    info={'scope':__doc__,'base':str(a.base),'added_cells':[[*p,b.encode()] for p,b in added.items()],
          'optimistic_G1_permanent_mass':9,'H1_supplied_cells':3,
          'pending':'H1 three natural pushes; X2/T2 third moves; neighboring closure and loaded budgets',
          'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.base/'problem.flyer',a.base/'before_natural.json',a.base/'drive.txt',Path(__file__)]}}
    (a.out/'preparation.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8')
    print(f'Constructed {len(f._cells)} cells; H1 moves still supplied; no verification claim')


if __name__=='__main__':main()
