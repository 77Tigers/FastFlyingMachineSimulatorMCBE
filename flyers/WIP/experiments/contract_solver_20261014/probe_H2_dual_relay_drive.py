"""Add a real H2 three-normal drive to the accepted dual-relay component.
G2 recovery carrier remains supplied; complete natural-flyer closure is unproved.
"""
import argparse,json,hashlib,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
ROOT=Path(__file__).resolve().parents[4]

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
 ap.add_argument('--four-recovery',action='store_true',help='Four-cell recovery star supports all three actual fired motor positions')
 ap.add_argument('--clear-observer-lane',action='store_true',help='Use the +Y motor instead of +Z to avoid recruiting a G0 observer before its supplied move')
 a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 f=Flyer.load(a.base/'problem.flyer');shift=lambda p:(p[0],p[1]+1,p[2]);add={}
 targets=[(15,1,11),(15,2,12)] if a.clear_observer_lane else [(15,1,11),(15,1,13)]
 for p in targets:add[shift(p)]=Block(Kind.HONEY)
 recovery=[(13,1,13),(13,1,12),(13,1,11),(13,0,12)] if a.four_recovery else [(13,1,13),(13,0,13)]
 if a.clear_observer_lane:recovery=[(13,1,12),(13,0,12),(13,2,12),(13,1,11)]
 for p in recovery:add[shift(p)]=Block(Kind.SLIME)
 add[shift((14,1,12))]=Block(Kind.REDSTONE_BLOCK)
 normals=[(14,0,12),(14,1,11),(14,2,12)] if a.clear_observer_lane else [(14,0,12),(14,1,11),(14,1,13)]
 for p in normals:add[shift(p)]=Block.piston(0)
 assert not set(add)&set(f._cells)
 for p,b in add.items():f.set(p,b)
 f.save(a.out/'problem.flyer');assert Flyer.load(a.out/'problem.flyer')._cells==f._cells
 c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
 next(p for p in c['ports'] if p['name']=='H2')['provenance']=['internal']*3+[None,None]
 c['ports'].append({'name':'G2','at':shift((13,1,12) if a.clear_observer_lane else (13,1,13)),'role':'input','word':'wwmmm','provenance':[None,None]+['supplied']*3})
 c['name']=a.out.name;c['boundary_envelope']={'min':[10,0,8],'max':[27,7,16]}
 rows=[]
 for p in c['ports']:
  for cy in range(3):
   for slot,v in enumerate(p['provenance']):
    if v=='supplied':rows.append((cy*10+slot*2,p['at'][0]+cy*3+p['word'][:slot].count('m'),*p['at'][1:],12))
 (a.out/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
 for order in ['before_natural','after_natural','interleaved']:(a.out/f'{order}.json').write_text(json.dumps({**c,'prescribed_order':order},indent=2)+'\n',encoding='utf-8')
 (a.out/'preparation.json').write_text(json.dumps({'scope':__doc__,'base':str(a.base),'added':[[*p,b.encode()] for p,b in add.items()],'four_recovery':a.four_recovery,'clear_observer_lane':a.clear_observer_lane,'budget':'H2 4 honey + RB + two observer pushers + two glazed outputs =9 permanent, G2 up to four recovery glue within existing six-glue allowance; source geometry for G2 remains supplied.','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')
 (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
 run=subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(a.out/'before_natural.json'),str(a.out/'native.json'),'30','2'],cwd=ROOT,capture_output=True)
 assert (a.out/'native.json').exists(),run.stderr
 print((a.out/'native.json').read_text(encoding='utf-8'))

if __name__=='__main__':main()
