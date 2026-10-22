"""Fixed seven-cell G0 observer/G1 stone gate calibration, supplied drivers."""
import os as _research_os
import copy,json,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def main():
 out=HERE/'out/quarter_ring_contacts/front_stone_gate_fixed_calibration';out.mkdir(exist_ok=False);f=Flyer()
 for p,b in [((4,0,0),Block(Kind.SLIME)),((4,1,0),Block.piston(1,sticky=True)),((4,1,2),Block(Kind.SLIME)),((4,1,1),Block(Kind.SMOOTH_STONE)),((5,0,2),Block(Kind.HONEY)),((5,0,1),Block.observer(2,powered=False)),((2,1,0),Block(Kind.HONEY))]:f.set(p,b)
 f.save(out/'problem.flyer');loaded=Flyer.load(out/'problem.flyer');assert loaded._cells==f._cells and loaded._piston_blocks==f._piston_blocks
 c=json.loads((HERE/'out/quarter_ring_contacts/G0_front_recovery_upper/before_natural.json').read_text(encoding='utf-8'));c['name']='front_stone_gate_fixed_calibration';c['boundary_envelope']={'min':[0,0,0],'max':[20,20,20]};c['ports']=[]
 for name,at,word,prov in [('G0',[5,0,2],'wmmmw',[None,'supplied','supplied','supplied',None]),('G1',[4,1,2],'mmwwm',['supplied','supplied',None,None,'supplied']),('H0',[4,0,0],'mmwwm',['supplied','supplied',None,None,'supplied']),('T1',[2,1,0],'wmmmw',[None,'supplied','supplied','internal',None])]:c['ports'].append({'name':name,'at':at,'word':word,'role':'input','provenance':prov})
 rows=[]
 for p in c['ports']:
  for cy in range(3):
   for slot,v in enumerate(p['provenance']):
    if v=='supplied':rows.append((cy*10+2*slot,p['at'][0]+3*cy+p['word'][:slot].count('m'),*p['at'][1:],12))
 (out/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
 for order in ['before_natural','after_natural','interleaved']:(out/f'{order}.json').write_text(json.dumps({**c,'prescribed_order':order},indent=2)+'\n',encoding='utf-8')
 (out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(out/'before_natural.json'),str(out/'native.json'),'30','2'],cwd=ROOT,check=True);r=json.loads((out/'native.json').read_text(encoding='utf-8'));print({k:r.get(k) for k in ['verified','passed','max_action','orders_per_sample']})
if __name__=='__main__':main()
