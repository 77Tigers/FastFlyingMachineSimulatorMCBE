"""Isolate late-RB cross-power: retain its mass as stone and supply only H0 move4."""
import os as _research_os
import json,subprocess,hashlib
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def main():
 base=HERE/'out/quarter_ring_contacts/H0_pulsed_source_trials/case000';out=HERE/'out/quarter_ring_contacts/H0_pulse_late_source_control';out.mkdir(exist_ok=False);f=Flyer.load(base/'problem.flyer');prep=json.loads((base/'preparation.json').read_text(encoding='utf-8'));q=tuple(v+prep['normalization_delta'][i] for i,v in enumerate(prep['source_record']['RBs'][1]));assert f._cells[q].kind==Kind.REDSTONE_BLOCK;f.set(q,Block(Kind.SMOOTH_STONE));f.save(out/'problem.flyer');g=Flyer.load(out/'problem.flyer');assert g._cells==f._cells and g._piston_blocks==f._piston_blocks
 c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'));c['name']=out.name;rows=[]
 for p in c['ports']:
  if p['name']=='H0_front':p['provenance']=['internal','internal',None,None,'supplied']
  for cy in range(3):
   for s,v in enumerate(p['provenance']):
    if v=='supplied':rows.append((10*cy+2*s,p['at'][0]+3*cy+p['word'][:s].count('m'),*p['at'][1:],12))
 (out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
 for order in ['before_natural','after_natural','interleaved']:(out/f'{order}.json').write_text(json.dumps({**c,'prescribed_order':order},indent=2)+'\n',encoding='utf-8')
 prep.update(scope=__doc__+' Fourteen natural/sixteen supplied strokes attempted; late H0 driver explicitly unbuilt. Not complete flyer.',base_sha256=hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest(),late_RB_replaced_by_stone=q,H0_natural_slots=[0,1],H0_supplied_slots=[4]);(out/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n',encoding='utf-8');(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
 subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(out/'before_natural.json'),str(out/'native.json'),'30','2'],cwd=ROOT,check=False);print((out/'native.json').read_text(encoding='utf-8'))
if __name__=='__main__':main()
