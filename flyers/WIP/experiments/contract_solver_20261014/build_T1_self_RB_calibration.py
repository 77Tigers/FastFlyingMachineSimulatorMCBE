"""Fixed self-RB T1 push1/push2/pull3 calibration; four neighboring drives supplied."""
import argparse,json,subprocess,hashlib
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--clear-delivery-lane',action='store_true');a=ap.parse_args()
 out=HERE/('out/quarter_ring_contacts/T1_self_RB_clear_delivery' if a.clear_delivery_lane else 'out/quarter_ring_contacts/T1_self_RB_fixed_calibration');out.mkdir(exist_ok=False);f=Flyer()
 gate=[((4,0,0),Block(Kind.SLIME)),((4,1,0),Block.piston(1,sticky=True)),((4,1,2),Block(Kind.SLIME)),((4,1,1),Block(Kind.SMOOTH_STONE)),((5,0,2),Block(Kind.HONEY)),((5,0,1),Block.observer(2,powered=False))]
 t1={(2,1,0),(2,2,0),(2,2,-1),(3,2,-1),(3,1,-1),(3,0,-1)};x1={(0,0,-1),(0,1,-1),(0,2,-1)};motors={(1,0,-1),(1,2,-1)}
 if a.clear_delivery_lane:t1.remove((2,2,-1));t1.add((3,2,0))
 for p,b in gate+[(p,Block(Kind.HONEY)) for p in t1]+[(p,Block(Kind.SLIME)) for p in x1]+[(p,Block.piston(0)) for p in motors]+[((2,1,-1),Block(Kind.REDSTONE_BLOCK))]:
  assert p not in f._cells;f.set(p,b)
 norm=f.canonicalize();delta=tuple(min(p[i] for p in norm._cells)-min(p[i] for p in f._cells) for i in range(3));norm.save(out/'problem.flyer');loaded=Flyer.load(out/'problem.flyer');assert loaded._cells==norm._cells and loaded._piston_blocks==norm._piston_blocks
 c=json.loads((HERE/'out/quarter_ring_contacts/front_stone_gate_fixed_calibration/before_natural.json').read_text(encoding='utf-8'));c['name']='T1_self_RB_fixed_calibration';c['boundary_envelope']={'min':[0,0,0],'max':[40,20,20]}
 next(q for q in c['ports'] if q['name']=='T1')['provenance']=[None,'internal','internal','internal',None]
 c['ports'].append({'name':'X1','at':[0,1,-1],'word':'mwwmm','role':'input','provenance':['supplied',None,None,'supplied','supplied']})
 for q in c['ports']:q['at']=[v+delta[i] for i,v in enumerate(q['at'])]
 rows=[]
 for q in c['ports']:
  for cy in range(3):
   for slot,prov in enumerate(q['provenance']):
    if prov=='supplied':rows.append((10*cy+2*slot,q['at'][0]+3*cy+q['word'][:slot].count('m'),*q['at'][1:],12))
 (out/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
 for order in ['before_natural','after_natural','interleaved']:(out/f'{order}.json').write_text(json.dumps({**c,'prescribed_order':order},indent=2)+'\n',encoding='utf-8')
 prep={'scope':__doc__+' All three T1 moves natural, other twelve moves supplied; no complete-flyer claim.','clear_delivery_lane':a.clear_delivery_lane,'normalization_delta':delta,'T1_glue':sorted(t1),'RB':[2,1,-1],'normals':sorted(motors),'X1_glue':sorted(x1),'budget':'T1_self_RB_budget/full39.json'};(out/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n',encoding='utf-8');(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
 subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(out/'before_natural.json'),str(out/'native.json'),'30','2'],cwd=ROOT,check=False);print((out/'native.json').read_text(encoding='utf-8'))
if __name__=='__main__':main()
