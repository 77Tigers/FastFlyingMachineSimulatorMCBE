"""Native partial interface: one generated two-normal column, other strokes supplied.

Keep the scaffold's glue and reserved RBs. Retain only the chosen target's two
normal pistons; omit all other actors explicitly. The target's third stroke
and every neighboring body's moves are supplied, with per-slot provenance.
This tests a column on generated geometry, not the loaded scaffold or a flyer.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from fastflyer import Block,Flyer,Kind
from check_quarter_contacts import check,shift,pref


def build(source,target,out):
    r=json.loads(source.read_text(encoding='utf-8')); check(r)
    assert r.get('local_modules') and r.get('conservative_compatibility')
    assert target in r['glue']
    plan=json.loads((HERE/'results/quarter_ring20_role_plan.json').read_text(encoding='utf-8'))
    actors=[a for a in r['actors'] if a['target']==target and a['kind']=='push']
    assert len(actors)==2
    natural={a['slot'] for a in actors}
    f=Flyer(phase_x=0,phase_z=0,rng_state=0,push_limit=12)
    def put(p,b):
        p=tuple(p); assert p not in f._cells
        f.set(p,b)
    for name,cells in r['glue'].items():
        for p in cells: put(p,Block(Kind.SLIME if r['materials'][name]==0 else Kind.HONEY))
    for p in r['redstone_sources'].values(): put(p,Block(Kind.REDSTONE_BLOCK))
    for a in actors:
        fslot=next(x['firing_slot'] for x in plan['actions'] if (x['target'],x['slot'])==(target,a['slot']))
        put(a['at'],Block.piston(0,state=2 if fslot==4 else 0))
        if fslot==4: put(shift(a['at'],1),Block(Kind.PISTON_ARM))
    out.mkdir(parents=True,exist_ok=False)
    f.save(out/'problem.flyer'); g=Flyer.load(out/'problem.flyer')
    delta=tuple(min(p[k] for p in g._cells)-min(p[k] for p in f._cells) for k in range(3))
    translated=lambda p:[x+d for x,d in zip(p,delta)]
    ports=[]; rows=[]
    for name,cells in r['glue'].items():
        word=plan['words'][name]; at=translated(cells[0]); provenance=[]
        for t,c in enumerate(word):
            supplied=c=='m' and not (name==target and t in natural)
            provenance.append(None if c=='w' else 'supplied' if supplied else 'internal')
            if supplied:
                for cycle in range(3): rows.append((cycle*10+2*t,at[0]+cycle*3+pref(word,t),at[1],at[2],12))
        ports.append({'name':name,'role':'input','at':at,'word':word,'provenance':provenance})
    (out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
    contract={'version':1,'name':f'generated_{target}_column_only','flyer':'problem.flyer',
              'period_ticks':10,'advance':3,'cycles':3,'recurrence':'bounded',
              'prescribed_script':'drive.txt','ports':ports,'required_cells':[],
              'boundary_envelope':{'min':[min(p[k] for p in g._cells)-2 for k in range(3)],
                                   'max':[max(p[k] for p in g._cells)+4 for k in range(3)]}}
    for order in ('before_natural','after_natural','interleaved'):
        contract['prescribed_order']=order
        (out/f'{order}.json').write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')
    (out/'preparation.json').write_text(json.dumps({'scope':__doc__,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'target':target,'natural_slots':sorted(natural),'retained_normal_actors':actors,
        'omitted_actor_count':len(r['actors'])-2,'normalization_delta':delta},indent=2)+'\n',encoding='utf-8')
    print(f'Built {target}: two natural pushes, third/neighbor moves supplied; {len(g._cells)} cells')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('source',type=Path);ap.add_argument('target');ap.add_argument('out',type=Path)
    a=ap.parse_args();build(a.source,a.target,a.out)
