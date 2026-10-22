"""T1 two-push column with mixed T0/X1 recovery, retaining upper pull3.
Full budget reduces X1 reserved glue7->6; physical X1 still uses four.
"""
import os as _research_os
import argparse,json,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
ROOT=Path(__file__).resolve().parents[4]
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 f=Flyer.load(a.base/'problem.flyer');f.remove((16,3,10));assert (15,4,10) not in f._cells;f.set((15,4,10),Block(Kind.SLIME))
 shape={(15,6,10),(16,6,10),(16,5,10),(17,5,10),(17,5,9),(17,4,9)}
 for p in shape-{(15,6,10)}:assert p not in f._cells;f.set(p,Block(Kind.HONEY))
 rb=(16,5,9);motors={(15,5,10),(15,4,9)}
 assert rb not in f._cells;f.set(rb,Block(Kind.REDSTONE_BLOCK))
 for p in motors:assert p not in f._cells;f.set(p,Block.piston(0))
 out=f.canonicalize();out.save(a.out/'problem.flyer');loaded=Flyer.load(a.out/'problem.flyer');assert out._cells==loaded._cells and out._piston_blocks==loaded._piston_blocks
 c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'));next(p for p in c['ports'] if p['name']=='T1_front')['provenance']=[None,'internal','internal','internal',None];c['name']=a.out.name;rows=[]
 for p in c['ports']:
  for cy in range(3):
   for slot,v in enumerate(p['provenance']):
    if v=='supplied':rows.append((10*cy+2*slot,p['at'][0]+3*cy+p['word'][:slot].count('m'),*p['at'][1:],12))
 (a.out/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
 for order in ['before_natural','after_natural','interleaved']:dump(a.out/f'{order}.json',{**c,'prescribed_order':order})
 dump(a.out/'preparation.json',{'scope':__doc__,'T1_shape':sorted(shape),'RB':rb,'motors':sorted(motors),'T0_remove':[16,3,10],'T0_add':[15,4,10]});(a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
 subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(a.out/'before_natural.json'),str(a.out/'native.json'),'30','2'],cwd=ROOT,capture_output=True);print((a.out/'native.json').read_text(encoding='utf-8'))
if __name__=='__main__':main()
