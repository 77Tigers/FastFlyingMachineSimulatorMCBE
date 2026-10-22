"""Ordinary own-RB three-push H0 (mmwwm) phase/startup calibration; neighbor supplied."""
import os as _research_os
import json,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]

def main():
 out=HERE/'out/quarter_ring_contacts/H0_three_push_phase_calibration';out.mkdir(exist_ok=False);f=Flyer();body={(5,2,2),(5,2,1),(5,2,3),(5,3,2)};carrier={(2,2,2),(2,2,1),(2,2,3),(2,3,2)}
 for shape,mat in [(body,Kind.HONEY),(carrier,Kind.SLIME)]:
  for q in shape:assert q not in f._cells;f.set(q,Block(mat))
 for q,b in [((4,2,2),Block(Kind.REDSTONE_BLOCK)),((4,2,1),Block.piston(0)),((4,2,3),Block.piston(0)),((3,3,2),Block.piston(0,state=2)),((4,3,2),Block(Kind.PISTON_ARM))]:assert q not in f._cells;f.set(q,b)
 f.set_piston_blocks((3,3,2),[(4,3,2)]);outf=f.canonicalize();delta=tuple(min(q[i] for q in outf._cells)-min(q[i] for q in f._cells) for i in range(3));outf.save(out/'problem.flyer');loaded=Flyer.load(out/'problem.flyer');assert loaded._cells==outf._cells and loaded._piston_blocks==outf._piston_blocks
 c=json.loads((HERE/'out/quarter_ring_contacts/front_stone_gate_fixed_calibration/before_natural.json').read_text(encoding='utf-8'));c['name']='H0_three_push_phase_calibration';c['boundary_envelope']={'min':[0,0,0],'max':[40,20,20]};c['ports']=[]
 for name,at,w,prov in [('H0',[5,2,2],'mmwwm',['internal','internal',None,None,'internal']),('front',[2,2,2],'wmmmw',[None,'supplied','supplied','supplied',None])]:c['ports'].append({'name':name,'at':[v+delta[i] for i,v in enumerate(at)],'word':w,'role':'input','provenance':prov})
 rows=[]
 for q in c['ports']:
  for cy in range(3):
   for t,v in enumerate(q['provenance']):
    if v=='supplied':rows.append((10*cy+2*t,q['at'][0]+3*cy+q['word'][:t].count('m'),*q['at'][1:],12))
 (out/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
 for order in ['before_natural','after_natural','interleaved']:(out/f'{order}.json').write_text(json.dumps({**c,'prescribed_order':order},indent=2)+'\n',encoding='utf-8')
 (out/'preparation.json').write_text(json.dumps({'scope':__doc__+' Three natural H0 moves, three supplied neighbor moves; full39 actual carrier split G0/T1 still unbuilt.','normalization_delta':delta,'H0_glue':sorted(body),'RB':[4,2,2],'front_carrier':sorted(carrier),'extended_normal':[3,3,2],'head':[4,3,2],'budget_reference':'T1_self_RB_budget/full39.json','H0_glue_budget':6,'H0_RB_budget':1},indent=2)+'\n',encoding='utf-8');(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
 subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(out/'before_natural.json'),str(out/'native.json'),'30','2'],cwd=ROOT,check=False);print((out/'native.json').read_text(encoding='utf-8'))
if __name__=='__main__':main()
