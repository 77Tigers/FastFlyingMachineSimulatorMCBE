"""Combine G1 shared source and relocated H0 late motor with a seven-glue reroute."""
import argparse,json,hashlib,subprocess
from pathlib import Path
from assemble import Flyer,body_of
from fastflyer import Block,Kind
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--lower-source',action='store_true');a=ap.parse_args()
 base=HERE/'out/quarter_ring_contacts/G1_late_push_search/case000';out=HERE/'out/quarter_ring_contacts'/('joint_G1_H0_lower_source' if a.lower_source else 'joint_G1_H0_reroute');out.mkdir(exist_ok=False);f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'));ports={p['name']:p for p in c['ports']};proposal=json.loads((HERE/'out/quarter_ring_contacts/H0_joint_reroute_hypothesis/proposal.json').read_text(encoding='utf-8'));H0={tuple(q) for q in proposal['H0_glue']};G1={(17,1,13),(17,1,14),(17,1,15),(17,2,15)}
 if a.lower_source:H0.remove((18,5,16));H0.add((18,3,16))
 remove=body_of(f._cells,tuple(ports['H0_front']['at']))|body_of(f._cells,tuple(ports['G1_front']['at']))|{(16,3,15),(17,3,15),(17,3,16),(16,0,14)}
 for q in remove:f.remove(q)
 for q in H0|G1:assert q not in f._cells;f.set(q,Block(Kind.SLIME))
 new_hardware=[((16,1,15),Block(Kind.REDSTONE_BLOCK)),((16,2,15),Block.piston(0)),((16,4,16),Block.piston(0,state=2)),((17,4,16),Block(Kind.PISTON_ARM)),((17,3,16) if a.lower_source else (17,5,16),Block(Kind.REDSTONE_BLOCK))]
 for q,b in new_hardware:assert q not in f._cells;f.set(q,b)
 f.set_piston_blocks((16,4,16),[(17,4,16)]);canonical=f.canonicalize();delta=tuple(min(q[k] for q in canonical._cells)-min(q[k] for q in f._cells) for k in range(3));canonical.save(out/'problem.flyer');loaded=Flyer.load(out/'problem.flyer');assert loaded._cells==canonical._cells and loaded._piston_blocks==canonical._piston_blocks
 rows=[];c['name']=out.name
 for p in c['ports']:
  if p['name']=='H0_front':p['at']=[20,4,14]
  if p['name']=='G1_front':p['provenance']=['internal','supplied',None,None,'internal']
  p['at']=[v+delta[k] for k,v in enumerate(p['at'])]
  for cy in range(3):
   for s,v in enumerate(p['provenance']):
    if v=='supplied':rows.append((10*cy+2*s,p['at'][0]+3*cy+p['word'][:s].count('m'),*p['at'][1:],12))
 (out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
 for order in ['before_natural','after_natural','interleaved']:dump(out/f'{order}.json',{**c,'prescribed_order':order})
 budget=json.loads((base/'whole39_source_budget.json').read_text(encoding='utf-8'));budget['scope']='Joint H0 relocation/G1 shared-RB hypothesis; unchanged39 roles/masses/loads/peak12. H0 permanent10, G1 actual6 plus2future reserve within8. G1 pull1 still supplied; not complete flyer.';budget['source_allocation']['G1_power']={'glue':4,'shared_RB':1,'stone':1,'future_observer_or_glue_reserve':2,'mass':8};dump(out/'whole39_source_budget.json',budget)
 dump(out/'preparation.json',{'scope':__doc__+' Seventeen natural/thirteen supplied strokes attempted; not complete flyer.','lower_source':a.lower_source,'base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest(),'H0_glue':sorted(H0),'G1_glue':sorted(G1),'removed':sorted(remove),'added_hardware':[[*q,b.encode()] for q,b in new_hardware],'normalization_delta':delta,'H0_port_before_normalization':[20,4,14]});(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
 subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(out/'before_natural.json'),str(out/'native.json'),'30','2'],cwd=ROOT,check=False);print((out/'native.json').read_text(encoding='utf-8'))
if __name__=='__main__':main()
