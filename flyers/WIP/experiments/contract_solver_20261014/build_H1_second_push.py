"""Use forward source capacity to fit H1 push3 pulse within its permanent9.

G1 supplies push2 power; a second H1 observer pulses push3 after push2.
H0 recovers the second normal on01, H1 recovers it on2; push4 stays supplied.
"""
import json,hashlib,subprocess,sys
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
 side='--side-row' in sys.argv
 base=HERE/'out/quarter_ring_contacts/H1_first_front_pulse_hard';out=HERE/('out/quarter_ring_contacts/H1_second_push'+('_side' if side else ''));out.mkdir(exist_ok=False);f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'))
 added=[((21,1,15),Block(Kind.HONEY)),((21,2,15),Block(Kind.HONEY)),((21,3,15),Block(Kind.HONEY)),((20,2,15),Block.observer(2)),((18,3,15),Block.piston(0))]
 if side:added=[((21,1,15),Block(Kind.HONEY)),((21,2,15),Block(Kind.HONEY)),((21,2,16),Block(Kind.HONEY)),((20,2,15),Block.observer(4)),((18,2,16),Block.piston(0))]
 for q,b in added:assert q not in f._cells,q;f.set(q,b)
 budget=json.loads((base/'whole39_source_budget.json').read_text(encoding='utf-8'));a=next(a for a in budget['actions'] if a['target']=='H1_power' and a['slot']==3);assert a['piston_word']=='mmmww' and a['contacts'][0]['body']=='H0' and a['contacts'][0]['carries_at']==[0,1] and a['contacts'][1]['carries_at']==[2]
 budget['source_allocation']['H1_power']={'glue':6,'hard_target_stone':1,'observers':2,'mass':9};budget['scope']=__doc__+' All39 permanent masses/motor carrier masks/loads unchanged12; actual H1 fills9, G1 uses one extra source observer within8. Native timing/passenger checks required; component only.'
 canonical=f.canonicalize();delta=tuple(min(q[k] for q in canonical._cells)-min(q[k] for q in f._cells) for k in range(3));canonical.save(out/'problem.flyer');g=Flyer.load(out/'problem.flyer');assert g._cells==canonical._cells and g._piston_blocks==canonical._piston_blocks
 c['name']=out.name;rows=[]
 for p in c['ports']:
  if p['name']=='H1_power':p['provenance'][3]='internal'
  p['at']=[v+delta[k] for k,v in enumerate(p['at'])]
  for cy in range(3):
   for s,v in enumerate(p['provenance']):
    if v=='supplied':rows.append((10*cy+2*s,p['at'][0]+3*cy+p['word'][:s].count('m'),*p['at'][1:],12))
 (out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
 for order in ['before_natural','after_natural','interleaved']:dump(out/f'{order}.json',{**c,'prescribed_order':order})
 dump(out/'whole39_source_budget.json',budget);dump(out/'preparation.json',{'scope':__doc__,'source_record':{'motors':[[17,0,15],[18,2,16] if side else [18,3,15]]},'added':[[*q,b.encode()] for q,b in added],'normalization_delta':delta,'base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest()});(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
 subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(out/'before_natural.json'),str(out/'native.json'),'30','2'],cwd=ROOT,check=False);print((out/'native.json').read_text(encoding='utf-8'))
if __name__=='__main__':main()
