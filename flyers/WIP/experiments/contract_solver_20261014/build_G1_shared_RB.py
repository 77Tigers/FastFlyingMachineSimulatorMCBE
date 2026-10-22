"""One shared RB for G1 push0/push4; retain supplied pull1 and test actor permutation."""
import os as _research_os
import argparse,json,subprocess,hashlib
from pathlib import Path
from assemble import Flyer,body_of
from fastflyer import Block,Kind
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--alternate-site',action='store_true');a=ap.parse_args()
 base=HERE/'out/quarter_ring_contacts/G1_late_push_search/case000';out=HERE/'out/quarter_ring_contacts'/('G1_shared_RB_side_site' if a.alternate_site else 'G1_shared_RB_first_late');out.mkdir(exist_ok=True);assert not (out/'preparation.json').exists();f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'));port=next(p for p in c['ports'] if p['name']=='G1_front');old=body_of(f._cells,tuple(port['at']));old_rb=(16,0,14);assert f._cells[old_rb].kind==Kind.REDSTONE_BLOCK
 for q in old|{old_rb}:f.remove(q)
 shape={(17,1,13),(17,1,14),(17,1,15),(17,2,15)} if a.alternate_site else {(17,1,13),(17,1,14),(18,1,13),(18,2,13)};shared=(16,1,15) if a.alternate_site else (16,1,13);first=(16,2,15) if a.alternate_site else (16,2,13)
 for q in shape:assert q not in f._cells;f.set(q,Block(Kind.SLIME))
 for q,b in [(shared,Block(Kind.REDSTONE_BLOCK)),(first,Block.piston(0))]:assert q not in f._cells;f.set(q,b)
 canonical=f.canonicalize();delta=tuple(min(q[k] for q in canonical._cells)-min(q[k] for q in f._cells) for k in range(3));canonical.save(out/'problem.flyer');loaded=Flyer.load(out/'problem.flyer');assert loaded._cells==canonical._cells and loaded._piston_blocks==canonical._piston_blocks
 c['name']=out.name;rows=[]
 for p in c['ports']:
  p['at']=[v+delta[k] for k,v in enumerate(p['at'])]
  if p['name']=='G1_front':p['provenance']=['internal','supplied',None,None,'internal']
  for cy in range(3):
   for s,source in enumerate(p['provenance']):
    if source=='supplied':rows.append((10*cy+2*s,p['at'][0]+3*cy+p['word'][:s].count('m'),*p['at'][1:],12))
 (out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
 for order in ['before_natural','after_natural','interleaved']:(out/f'{order}.json').write_text(json.dumps({**c,'prescribed_order':order},indent=2)+'\n',encoding='utf-8')
 budget=json.loads((base/'whole39_source_budget.json').read_text(encoding='utf-8'));budget['scope']='G1 shared-RB two-push hypothesis; four glue+stone+sharedRB=6 actual permanent cells, two reserved cells within mass8. First and late motor roles may permute; full natural verification required. Pull1 supplied; not a complete flyer.';budget['source_allocation']['G1_power']={'glue':4,'shared_RB':1,'stone':1,'future_hardware_or_glue_reserve':2,'mass':8};(out/'whole39_source_budget.json').write_text(json.dumps(budget,indent=2)+'\n',encoding='utf-8')
 prep={'scope':__doc__+' Seventeen natural/thirteen supplied strokes attempted; not complete flyer.','alternate_site':a.alternate_site,'base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest(),'removed_G1_glue':sorted(old),'removed_RB':old_rb,'G1_shape':sorted(shape),'shared_RB':shared,'new_first_normal':first,'retained_late_normal':[15,1,14],'retained_late_head':[16,1,14],'gate_stone':[17,2,13],'push0_uses_gate_stone':not a.alternate_site,'normalization_delta':delta};(out/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n',encoding='utf-8');(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
 subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(out/'before_natural.json'),str(out/'native.json'),'30','2'],cwd=ROOT,check=False);print((out/'native.json').read_text(encoding='utf-8'))
if __name__=='__main__':main()
