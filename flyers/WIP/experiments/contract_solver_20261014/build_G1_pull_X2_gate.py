"""Filter supplied H1 observer pulses through a different-word X2 hard plate.

Component calibration only: X2/H1 own drives and wider closure remain unbuilt.
"""
import json, hashlib, subprocess, importlib.util, sys
from pathlib import Path
from assemble import Flyer
from fastflyer import Block, Kind
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]
def dump(p,x): p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
 base=HERE/'out/quarter_ring_contacts/joint_G1_H0_lower_source'
 material=Kind.SLIME if '--slime' in sys.argv else Kind.HONEY
 hard='--hard-plate' in sys.argv
 shift='--shift-root' in sys.argv
 hook='--recovery-hook' in sys.argv
 assert not hook or shift
 out=HERE/('out/quarter_ring_contacts/G1_pull_X2_gate'+('_slime' if material==Kind.SLIME else '')+('_hard' if hard else '')+('_forward' if shift else '')+('_hook' if hook else ''));out.mkdir(exist_ok=False)
 f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'))
 x2=[(17,2,11),(17,1,11),(17,0,11),(18,0,11),(19,0,11),(20,0,11),(20,0,12),(20,0,13)]
 h1=[(20,0,15),(20,-1,15),(20,-1,14)]
 assert f._cells[x2[0]].kind==Kind.SLIME
 if shift:
  f._cells.pop(x2[0]);x2=[(18,2,11),(18,1,11),(18,0,11),(19,0,11),(20,0,11),(20,0,12),(20,0,13)]
  assert x2[0] not in f._cells
 if hook:x2.insert(-1,(18,3,11))
 for q in x2[1:]+h1+[(20,0,14),(20,-1,13)]: assert q not in f._cells, q
 for q in x2:f.set(q,Block(material))
 if hard:f.set(x2[-1],Block(Kind.SMOOTH_STONE))
 for q in h1:f.set(q,Block(Kind.HONEY))
 f.set((20,0,14),Block.piston(1,sticky=True));f.set((20,-1,13),Block.observer(2,powered=True))
 budget=json.loads((base/'whole39_source_budget.json').read_text(encoding='utf-8'))
 # Preserve all 39 carrier masks and full permanent loads, reserving source hardware.
 spec=importlib.util.spec_from_file_location('roles',HERE.parent/'tm_smol_rebalance_20261001/j2_front_smol/layered.py');role=importlib.util.module_from_spec(spec);spec.loader.exec_module(role)
 loads={b:{str(s):budget['permanent_masses'][b] for s,v in enumerate(w) if v=='m'} for b,w in budget['words'].items()}
 for action in budget['actions']:
  tr=role.trajectory(role.moves(budget['words'][action['target']]),action['kind'],action['slot'])
  for contact in action['contacts']:
   assert contact['touch'] in [list(o) for o in role.options(role.moves(budget['words'][action['target']]),role.moves(budget['words'][contact['body']]),contact['body']==action['target'],action['kind'],*tr[:2],*tr[2:])]
   actual=[s for s in range(5) if action['piston_word'][s]=='m' and budget['words'][contact['body']][s]=='m' and contact['touch'][s]];assert actual==contact['carries_at']
   for s in actual:loads[contact['body']][str(s)]+=1
  for s,v in enumerate(action['piston_word']):assert any(s in q['carries_at'] for q in action['contacts'])==(v=='m')
 assert len(budget['actions'])==39 and loads==budget['loads'] and max(v for ds in loads.values() for v in ds.values())==12
 budget['source_allocation']['X2']={'glue':len(x2)-int(hard),'hard_plate':int(hard),'future_RB':1,'future_observer':1,'future_glue_reserve':int(shift)-int(hook),'mass':10,'status':'Source placement and own drives unbuilt; two reserved hardware cells, not acceptance'}
 budget['source_allocation']['H1_power']={'glue':3,'observer':1,'future_source_or_glue_reserve':5,'mass':9}
 budget['scope']=__doc__+f' Whole39 carrier coverage/loads recomputed unchanged at12; X2 {len(x2)-int(hard)} {material.name} plus {int(hard)} hard plate and two unbuilt hardware reserves, H1 three honey plus observer plus five reserves.'
 canonical=f.canonicalize();delta=tuple(min(q[k] for q in canonical._cells)-min(q[k] for q in f._cells) for k in range(3));canonical.save(out/'problem.flyer');g=Flyer.load(out/'problem.flyer');assert g._cells==canonical._cells and g._piston_blocks==canonical._piston_blocks
 c['name']=out.name;c['ports'].append({'name':'H1_power','at':[20,0,15],'word':'wwmmm','role':'input','provenance':[None,None,'supplied','supplied','supplied']});rows=[]
 for p in c['ports']:
  if p['name']=='G1_front':p['provenance']=['internal','internal',None,None,'internal']
  if p['name']=='X2_front' and shift:p['at']=[18,2,11]
  p['at']=[v+delta[k] for k,v in enumerate(p['at'])]
  for cy in range(3):
   for s,v in enumerate(p['provenance']):
    if v=='supplied':rows.append((10*cy+2*s,p['at'][0]+3*cy+p['word'][:s].count('m'),*p['at'][1:],12))
 (out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
 for order in ['before_natural','after_natural','interleaved']:dump(out/f'{order}.json',{**c,'prescribed_order':order})
 dump(out/'whole39_source_budget.json',budget);dump(out/'preparation.json',{'scope':__doc__,'X2_glue':x2,'H1_glue':h1,'sticky':[20,0,14],'observer':[20,-1,13],'observer_direction':2,'normalization_delta':delta,'base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest()});(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
 subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(out/'before_natural.json'),str(out/'native.json'),'30','2'],cwd=ROOT,check=False);print((out/'native.json').read_text(encoding='utf-8'))
if __name__=='__main__':main()
