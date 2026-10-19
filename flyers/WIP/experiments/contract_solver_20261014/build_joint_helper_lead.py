"""Construct the first split-power lead with an explicit seven-glue H1 route.

This is a concrete bounded hypothesis, not verification. H1's three normal
pushes are internal; neighbor X0/T0/X2/T2 strokes remain explicitly supplied.
"""
import argparse,hashlib,json
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('screen',type=Path);ap.add_argument('out',type=Path)
    ap.add_argument('--lead-index',type=int,choices=(0,2),default=0,help='Lead2 moves early piston lanes away from the G1 observer connector')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    lead=json.loads(a.screen.read_text(encoding='utf-8'))['leads'][a.lead_index]
    assert lead['H1_power_glue']==[25,3,10] and lead['H1_column_RB']==([24,1,9] if a.lead_index==0 else [24,5,9])
    hglue=[(25,3,10),(25,3,9),(25,2,9),(25,1,9),(25,1,10),(25,3,11),(25,4,11)]
    if a.lead_index==2:hglue=[(25,3,10),(25,3,9),(25,4,9),(25,5,9),(25,5,10),(25,3,11),(25,4,11)]
    assert set(map(tuple,lead['H1_required_glue']))<=set(hglue)
    f=Flyer.load(a.base/'problem.flyer')
    for p in [(23,4,10),(24,4,10),(24,4,11),(25,4,11),(25,3,11),(25,3,10),(25,2,11),(22,2,11)]:f._cells.pop(p)
    added={tuple(p):Block(Kind.SLIME) for p in lead['G1_glue'] if tuple(p) not in f._cells}
    added.update({p:Block(Kind.HONEY) for p in hglue})
    for name in ['H1_RB','H1_column_RB']:added[tuple(lead[name])]=Block(Kind.REDSTONE_BLOCK)
    for name in ['T1_sticky','H1_sticky']:added[tuple(lead[name])]=Block.piston(1,sticky=True)
    added[tuple(lead['observer'])]=Block.observer(lead['observer_direction'],powered=True)
    normals=lead['normal_assignments'][0]
    for name in ['first','second','late']:added[tuple(normals[name])]=Block.piston(0,state=2 if name=='late' else 0)
    p=normals['late'];added[(p[0]+1,p[1],p[2])]=Block(Kind.PISTON_ARM)
    assert not set(added)&set(f._cells)
    for p,b in added.items():f.set(p,b)
    f.save(a.out/'problem.flyer');assert Flyer.load(a.out/'problem.flyer')._cells==f._cells
    c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'));h=next(p for p in c['ports'] if p['name']=='H1_power')
    remove={(10*cy+2*s,h['at'][0]+3*cy+s-2,h['at'][1],h['at'][2]) for cy in range(3) for s in [2,3,4]}
    rows=[tuple(map(int,s.split())) for s in (a.base/'drive.txt').read_text(encoding='utf-8').splitlines()]
    assert sum(row[:4] in remove for row in rows)==9
    (a.out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in rows if row[:4] not in remove),encoding='utf-8')
    for order in ['before_natural','after_natural','interleaved']:
        c=json.loads((a.base/f'{order}.json').read_text(encoding='utf-8'));c['name']='joint_H1_split_power'
        p=next(p for p in c['ports'] if p['name']=='H1_power');p['at']=[25,3,10];p['provenance']=[None,None,'internal','internal','internal']
        (a.out/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
    info={'scope':__doc__,'lead_index':a.lead_index,'lead':lead,'H1_glue':hglue,'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.base/'problem.flyer',a.screen,Path(__file__)]}}
    (a.out/'preparation.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8')
    print(f'Constructed {len(f._cells)} cells at12; H1 no longer supplied; verification pending')

if __name__=='__main__':main()
