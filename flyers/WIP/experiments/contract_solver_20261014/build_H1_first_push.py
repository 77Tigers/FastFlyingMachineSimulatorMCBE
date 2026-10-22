"""Calibrate H1 push2 with a G1-recovered normal and H1-carried RB.

H1 actual five glue/source cells plus observer and sticky passenger fits its
permanent9 plus whole39 motor budget. Two later H1 pushes remain supplied.
"""
import os as _research_os
import json,hashlib,subprocess,sys
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
 pulse='--front-pulse' in sys.argv
 hard='--hard-target' in sys.argv
 base=HERE/'out/quarter_ring_contacts/G1_pull_X2_gate_slime_hard_forward_hook';out=HERE/(('out/quarter_ring_contacts/H1_first_front_pulse'+('_hard' if hard else '')) if pulse else 'out/quarter_ring_contacts/H1_first_push');out.mkdir(exist_ok=False)
 f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'))
 # Coordinates in saved102 frame. The retained H1 glue at20,0,15 is the target.
 added=[((17,0,15),Block.piston(0)),((20,-1,15),Block(Kind.HONEY)),((19,-1,15),Block(Kind.REDSTONE_BLOCK))]
 if pulse:added=[((17,0,15),Block.piston(0)),((17,0,13),Block.observer(4)),((19,0,14),Block(Kind.HONEY))]
 if pulse and hard:added[-1]=((19,0,14),Block(Kind.SMOOTH_STONE))
 for q,b in added:assert q not in f._cells,q;f.set(q,b)
 budget=json.loads((base/'whole39_source_budget.json').read_text(encoding='utf-8'))
 action=next(a for a in budget['actions'] if a['target']=='H1_power' and a['slot']==2)
 assert action['piston_word']=='mmwwm' and action['contacts'][0]['body']=='G1_power' and action['contacts'][0]['carries_at']==[0,1,4]
 assert budget['permanent_masses']['H1_power']==9 and max(v for ds in budget['loads'].values() for v in ds.values())==12
 budget['source_allocation']['H1_power']={'glue':4,'observer':1,'RB':1,'future_glue_reserve':3,'mass':9}
 if pulse:
  budget['source_allocation']['H1_power']={'glue':4,'observer':1,'future_source_or_glue_reserve':4,'mass':9}
  if hard:budget['source_allocation']['H1_power']={'glue':3,'hard_target_stone':1,'observer':1,'future_source_or_glue_reserve':4,'mass':9}
  budget['source_allocation']['G1_power']={'glue':4,'shared_RB':1,'stone':1,'H1_first_source_observer':1,'future_observer_or_glue_reserve':1,'mass':8}
 budget['scope']=__doc__+' Whole39 masses/contact masks/loads unchanged. G1 recovers new first H1 normal on014; H1 RB powers it at2 then withdraws with push2. Native off/recovery is required; source/contact budget alone is not acceptance.'
 if pulse:budget['scope']='Front-capacity tradeoff: G1-carried observer pulses through H1 honey target only at2; H1 keeps one fewer permanent source cell than the RB construction. Whole39 masses/motor roles/loads unchanged12. Source/off/recovery require native validation; component only.'
 canonical=f.canonicalize();delta=tuple(min(q[k] for q in canonical._cells)-min(q[k] for q in f._cells) for k in range(3));canonical.save(out/'problem.flyer');g=Flyer.load(out/'problem.flyer');assert g._cells==canonical._cells and g._piston_blocks==canonical._piston_blocks
 c['name']=out.name;rows=[]
 for p in c['ports']:
  if p['name']=='H1_power':p['provenance'][2]='internal'
  p['at']=[v+delta[k] for k,v in enumerate(p['at'])]
  for cy in range(3):
   for s,v in enumerate(p['provenance']):
    if v=='supplied':rows.append((10*cy+2*s,p['at'][0]+3*cy+p['word'][:s].count('m'),*p['at'][1:],12))
 (out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
 for order in ['before_natural','after_natural','interleaved']:dump(out/f'{order}.json',{**c,'prescribed_order':order})
 dump(out/'whole39_source_budget.json',budget);dump(out/'preparation.json',{'scope':__doc__,'source_record':{'motors':[[17,0,15]]},'added':[[*q,b.encode()] for q,b in added],'normalization_delta':delta,'base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest()});(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
 subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(out/'before_natural.json'),str(out/'native.json'),'30','2'],cwd=ROOT,check=False);print((out/'native.json').read_text(encoding='utf-8'))
if __name__=='__main__':main()
