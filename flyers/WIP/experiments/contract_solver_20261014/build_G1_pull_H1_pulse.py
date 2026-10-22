"""Calibrate G1 pull1 with a supplied H1/wwmmm observer carrier; complete flyer unbuilt."""
import json,hashlib,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
 base=HERE/'out/quarter_ring_contacts/joint_G1_H0_lower_source';out=HERE/'out/quarter_ring_contacts/G1_pull_H1_pulse';out.mkdir(exist_ok=False);f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'))
 for q,b in [((20,0,14),Block.piston(1,sticky=True)),((20,0,15),Block(Kind.HONEY)),((20,0,16),Block.observer(5,powered=True))]:assert q not in f._cells;f.set(q,b)
 canonical=f.canonicalize();delta=tuple(min(q[k] for q in canonical._cells)-min(q[k] for q in f._cells) for k in range(3));canonical.save(out/'problem.flyer');g=Flyer.load(out/'problem.flyer');assert g._cells==canonical._cells and g._piston_blocks==canonical._piston_blocks;c['name']=out.name;c['ports'].append({'name':'H1_power','at':[20,0,15],'word':'wwmmm','role':'input','provenance':[None,None,'supplied','supplied','supplied']});rows=[]
 for p in c['ports']:
  if p['name']=='G1_front':p['provenance']=['internal','internal',None,None,'internal']
  p['at']=[v+delta[k] for k,v in enumerate(p['at'])]
  for cy in range(3):
   for s,v in enumerate(p['provenance']):
    if v=='supplied':rows.append((10*cy+2*s,p['at'][0]+3*cy+p['word'][:s].count('m'),*p['at'][1:],12))
 (out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
 for order in ['before_natural','after_natural','interleaved']:dump(out/f'{order}.json',{**c,'prescribed_order':order})
 budget=json.loads((base/'whole39_source_budget.json').read_text(encoding='utf-8'));budget['scope']='G1 pull1 via H1 own observer pulse and supplied H1 recovery. H1 actual glue+OBS2 within permanent9, future hardware7 reserved. Other masses/39 contacts/load sums unchanged. Native timing hypothesis; not full flyer.';dump(out/'whole39_source_budget.json',budget)
 dump(out/'preparation.json',{'scope':__doc__+' Eighteen natural/fifteen supplied strokes attempted (new H1 port).','sticky':[20,0,14],'H1_glue':[20,0,15],'H1_observer':[20,0,16],'observer_direction':5,'normalization_delta':delta,'base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest()});(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(out/'before_natural.json'),str(out/'native.json'),'30','2'],cwd=ROOT,check=False);print((out/'native.json').read_text(encoding='utf-8'))
if __name__=='__main__':main()
