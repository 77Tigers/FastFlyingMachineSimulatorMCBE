"""Realize a joint normal-column model with G moves supplied, then certify it.

G input capacity9 reserves two body cells for later power/hardware integration.
This is an interface, not a closed natural flyer.
"""
import os as _research_os
import argparse
import json
import subprocess
from pathlib import Path

from assemble import Flyer, ROOT, port_pos
from fastflyer import Block


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("model",type=Path)
    ap.add_argument("output",type=Path)
    a=ap.parse_args()
    if a.output.exists(): raise ValueError("existing scaffold")
    data=json.loads(a.model.read_text());m=data['results'][-1]
    assert m['status'] in ['OPTIMAL','FEASIBLE'] and m['normal_H_column'] and m['G_all_supplied']
    a.output.mkdir(parents=True)
    src=Path(data['source']);c=json.loads((src/'problem.json').read_text());f=Flyer.load(src/c['flyer'])
    sh=lambda p:tuple(v+d for v,d in zip(p,m['source_translation']))
    f._cells={sh(p):b for p,b in f._cells.items()}
    for p in c['ports']:p['at']=list(sh(p['at']))
    oldtip=next(p for p in c['ports'] if p['name']=='tip')
    removed={tuple(p['at']) for p in c['ports'] if p['name'].startswith('G') or p['name']=='tip'}
    removed |= {p for p,b in f._cells.items() if (p[0]==17 and b.kind==9 and b.direction==0)
                or (p[0]==18 and b.kind==6) or (p[0]==22 and b.kind==7)}
    removed.add((21,2,17))
    for p in removed:f.remove(p)
    for p in m['G']:f.set(tuple(p),Block.decode(2))
    for p in m['H']:f.set(tuple(p),Block.decode(1))
    column=m['H_column'][0]
    for p in column['early']:f.set(tuple(p),Block.piston(0))
    f.set(tuple(column['late']),Block.piston(0,state=2))
    f.set(tuple(column['arm']),Block.decode(10))
    f.set(tuple(column['source']),Block.decode(6))
    f.save(a.output/'problem.flyer');g=Flyer.load(a.output/'problem.flyer')
    minimum=lambda cells:tuple(min(p[k] for p in cells) for k in range(3))
    delta=tuple(b-v for v,b in zip(minimum(f._cells),minimum(g._cells)))
    norm=lambda p:[v+d for v,d in zip(p,delta)]
    assert {tuple(norm(p)):b.encode() for p,b in f._cells.items()}=={p:b.encode() for p,b in g._cells.items()}
    ports=[p for p in c['ports'] if not p['name'].startswith('G') and p['name']!='tip']
    groot=[19,2,17]
    ports += [{'name':f'G{i}','at':p,'word':'wmmmw','role':'input'} for i,p in enumerate([groot]+[p for p in m['G'] if p!=groot])]
    hroot=[21,2,16]
    ports += [{'name':'tip' if i==0 else f'tip_extra{i}','at':p,'word':'mmwwm','role':'output'}
              for i,p in enumerate([hroot]+[p for p in m['H'] if p!=hroot])]
    rows=[(t,*sh((x,y,z)),cap) for t,x,y,z,cap in [map(int,s.split()) for s in (src/c['prescribed_script']).read_text().splitlines()]]
    omitted={(t,*port_pos(oldtip,t,10,3)) for t in range(30) if t%10 in (0,2,8)}
    rows=[row for row in rows if tuple(row[:4]) not in omitted]
    gp=next(p for p in ports if p['name']=='G0')
    rows += [(t,*port_pos(gp,t,10,3),9) for t in range(30) if t%10 in (2,4,6)]
    for p in ports:p['at']=norm(p['at'])
    c.update(name='joint_normal_pair_G_supplied',ports=ports,flyer='problem.flyer',prescribed_script='drive.txt')
    c['required_cells']=[{'at':list(p),'cell':b.encode()} for p,b in g._cells.items() if b.kind!=10]
    c['boundary_envelope']={'min':[min(p[k] for p in g._cells)-5 for k in range(3)],'max':[max(p[k] for p in g._cells)+5 for k in range(3)]}
    (a.output/'problem.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
    (a.output/'drive.txt').write_text('\n'.join(' '.join(map(str,(t,*norm((x,y,z)),cap))) for t,x,y,z,cap in sorted(rows))+'\n',encoding='utf-8')
    (a.output/'construction.json').write_text(json.dumps({'scope':'T all moves/back slot2/H all3 pushes natural; G all moves, rear0/1, neighbor supplied; not a natural flyer','model':str(a.model),'G_input_limit':9,'reserved_G_body_cells':2},indent=2)+'\n',encoding='utf-8')
    subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(a.output/'problem.json'),str(a.output/'result.json'),'30','4'],capture_output=True)
    print((a.output/'result.json').read_text())


if __name__=='__main__':main()
