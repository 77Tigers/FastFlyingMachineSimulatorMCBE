"""T1 pull3 from a G0 observer pulse2 and supplied H0 mmwwm recovery.

G0's seventh reserved glue slot is used for the new observer instead.
T1 push1/2 and H0 drives remain supplied. Native proof decides contacts.
"""
import argparse,json,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
ROOT=Path(__file__).resolve().parents[4]
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--front-detour',action='store_true');ap.add_argument('--split-front-carrier',action='store_true');ap.add_argument('--near-T0',action='store_true');ap.add_argument('--upper-observer',action='store_true');a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 f=Flyer.load(a.base/'problem.flyer');added={}
 route=[(18,2,11),(18,2,12),(18,2,13),(17,2,13),(16,2,13)] if a.front_detour else [(17,2,12),(17,2,13),(16,2,13)]
 obs=(19,3,13);di=3;sticky=(18,2,13);hroot=(18,1,13);target=(16,2,13)
 if a.split_front_carrier:route=[(16,4,14)];obs=(19,4,13);di=4;sticky=(18,4,14);hroot=(18,5,14);target=(16,4,14)
 if a.near_T0:
  assert a.split_front_carrier
  route=[(15,5,9)];obs=(18,5,10);di=5;sticky=(17,5,9);hroot=(17,6,9);target=(15,5,9)
  oldt={(15,3,10),(15,3,11),(16,3,10),(16,4,10),(17,4,10),(18,4,10),(19,4,10),(19,4,11)}
  newt={(15,3,10),(15,3,11),(16,3,10),(17,3,10),(18,3,10),(19,3,10),(19,3,11),(19,4,11)}
  for p in oldt:f.remove(p)
  for p in newt:assert p not in f._cells;f.set(p,Block(Kind.SLIME))
 if a.upper_observer:
  assert a.split_front_carrier and not a.near_T0
  route=[(15,6,10)];obs=(18,6,11);di=5;sticky=(17,6,10);hroot=(17,7,10);target=(15,6,10)
 for p in route:added[p]=Block(Kind.HONEY if a.near_T0 or a.upper_observer else Kind.SLIME)
 added[hroot]=Block(Kind.SLIME)
 assert obs not in added and sticky not in added,'route overlaps new actor/source'
 added[obs]=Block.observer(di,powered=False);added[sticky]=Block.piston(1,sticky=True)
 assert not set(added)&f._cells.keys()
 for p,b in added.items():f.set(p,b)
 out=f.canonicalize();delta=tuple(min(p[i] for p in out._cells)-min(p[i] for p in f._cells) for i in range(3));out.save(a.out/'problem.flyer');loaded=Flyer.load(a.out/'problem.flyer');assert loaded._cells==out._cells and loaded._piston_blocks==out._piston_blocks
 c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
 if a.split_front_carrier:
  next(p for p in c['ports'] if p['name']=='T1_front')['name']='X2_front'
  c['ports'].append({'name':'T1_front','at':list(target),'word':'wmmmw','role':'input','provenance':[None,'supplied','supplied','internal',None]})
 else:next(p for p in c['ports'] if p['name']=='T1_front')['provenance'][3]='internal'
 c['ports'].append({'name':'H0_front','at':list(hroot),'role':'input','word':'mmwwm','provenance':['supplied','supplied',None,None,'supplied']})
 for p in c['ports']:p['at']=[v+delta[i] for i,v in enumerate(p['at'])]
 c['name']=a.out.name;rows=[]
 for p in c['ports']:
  for cy in range(3):
   for slot,v in enumerate(p['provenance']):
    if v=='supplied':rows.append((10*cy+2*slot,p['at'][0]+3*cy+p['word'][:slot].count('m'),*p['at'][1:],12))
 (a.out/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
 for order in ['before_natural','after_natural','interleaved']:dump(a.out/f'{order}.json',{**c,'prescribed_order':order})
 dump(a.out/'preparation.json',{'scope':__doc__,'added':[[*p,b.encode()] for p,b in added.items()]});(a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
 subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(a.out/'before_natural.json'),str(a.out/'native.json'),'30','2'],cwd=ROOT,capture_output=True);print((a.out/'native.json').read_text(encoding='utf-8'))
if __name__=='__main__':main()
