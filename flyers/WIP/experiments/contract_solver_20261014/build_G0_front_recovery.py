"""Test a budgeted G0 drive with supplied X1 recovery and T1 sticky carrier.

X1 has four recovery glue (within seven reserved in the whole budget), T1
one glue (within six reserved). Their own drives remain supplied. G0's
six-glue upper column retains both existing pulse observers.
"""
import argparse,json,subprocess,hashlib
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
ROOT=Path(__file__).resolve().parents[4]
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 f=Flyer.load(a.base/'problem.flyer');c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
 old={(17,2,11),(18,2,11),(18,2,12),(18,2,13),(18,3,13),(18,4,13)}
 for p in old:assert f._cells[p].kind==Kind.SLIME;f.remove(p)
 g0={(18,5,12),(18,5,11),(18,5,13),(18,6,12),(18,4,13),(18,3,13)}
 x1={(15,5,12),(15,5,11),(15,5,13),(15,6,12)};t1={(17,2,11)}
 motors={(16,5,11),(16,5,13),(16,6,12)};rb=(17,5,12)
 for shape,kind in [(g0,Kind.HONEY),(x1,Kind.SLIME),(t1,Kind.SLIME)]:
  for p in shape:assert p not in f._cells;f.set(p,Block(kind))
 assert rb not in f._cells;f.set(rb,Block(Kind.REDSTONE_BLOCK))
 for p in motors:assert p not in f._cells;f.set(p,Block.piston(0))
 out=f.canonicalize();delta=tuple(min(p[i] for p in out._cells)-min(p[i] for p in f._cells) for i in range(3));out.save(a.out/'problem.flyer');loaded=Flyer.load(a.out/'problem.flyer');assert loaded._cells==out._cells and loaded._piston_blocks==out._piston_blocks
 next(p for p in c['ports'] if p['name']=='G0').update(at=[18,5,12],provenance=[None,'internal','internal','internal',None])
 c['ports'] += [{'name':'X1_front','at':[15,5,12],'role':'input','word':'mwwmm','provenance':['supplied',None,None,'supplied','supplied']},{'name':'T1_front','at':[17,2,11],'role':'input','word':'wmmmw','provenance':[None,'supplied','supplied','supplied',None]}]
 for p in c['ports']:p['at']=[v+delta[i] for i,v in enumerate(p['at'])]
 c['boundary_envelope']={'min':[10,0,7],'max':[32,12,19]};c['name']=a.out.name;rows=[]
 for p in c['ports']:
  for cy in range(3):
   for slot,v in enumerate(p['provenance']):
    if v=='supplied':rows.append((10*cy+2*slot,p['at'][0]+3*cy+p['word'][:slot].count('m'),*p['at'][1:],12))
 (a.out/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
 for order in ['before_natural','after_natural','interleaved']:dump(a.out/f'{order}.json',{**c,'prescribed_order':order})
 dump(a.out/'preparation.json',{'scope':__doc__,'G0':sorted(g0),'X1':sorted(x1),'T1':sorted(t1),'motors':sorted(motors),'RB':rb,'base':str(a.base),'base_sha256':hashlib.sha256((a.base/'problem.flyer').read_bytes()).hexdigest()})
 (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
 subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(a.out/'before_natural.json'),str(a.out/'native.json'),'30','2'],cwd=ROOT,capture_output=True)
 print((a.out/'native.json').read_text(encoding='utf-8'))
if __name__=='__main__':main()
