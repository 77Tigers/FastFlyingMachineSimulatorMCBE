"""Jointly relocate T1 observer pull and its mixed-recovery push column.

Source observer remains on G0; one-glue H0 recovery is supplied. Ordinary
push columns use one X1 motor and one T0 motor. This is a bounded component
construction search, not complete-flyer acceptance. No overlapping children.
"""
import argparse,json,subprocess,sys,time
from pathlib import Path
from assemble import Flyer,body_of
from fastflyer import Block,Kind
from search_T1_two_pushes import D,add,adj,dist,dump
from search_T1_pull_routes import offsets

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--seconds',type=float,default=150);ap.add_argument('--extend-X1',action='store_true');ap.add_argument('--free-X1',action='store_true');a=ap.parse_args();a.extend_X1=a.extend_X1 or a.free_X1;a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 f=Flyer.load(a.base/'problem.flyer');c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'));ports={p['name']:p for p in c['ports']};oldq=tuple(ports['T1_front']['at']);oldh=tuple(ports['H0_front']['at']);oldobs=(18,6,11);oldsticky=add(oldq,(2,0,0));removed={oldq,oldh,oldobs,oldsticky};fixed=set(f._cells)-removed
 assert oldq==(15,6,10) and oldh==(17,7,10) and f._cells[oldobs]==Block.observer(5,powered=False)
 g0=body_of(f._cells,tuple(ports['G0']['at']));x1=body_of(f._cells,tuple(ports['X1_front']['at']));t0=body_of(f._cells,tuple(ports['T0']['at']));others=[]
 for p in c['ports']:
  if p['name'] not in ['T0','T1_front','H0_front'] and not(a.free_X1 and p['name']=='X1_front'):others.append((body_of(f._cells,tuple(p['at'])),f._cells[tuple(p['at'])].kind,p['word']))
 choices=[]
 for obs in sorted(set().union(*(set(adj(p)) for p in g0))-fixed):
  for di in [1,2,3,4,5]:
   q=add(obs,(-3+D[di][0],D[di][1],D[di][2]));sticky=add(q,(2,0,0))
   if q in fixed or sticky in fixed or min(q[1],obs[1],sticky[1])<0 or len({q,obs,sticky})!=3:continue
   if min(dist(q,p) for p in t0|x1)>4:continue
   for hr in adj(sticky):
    if hr in fixed or hr in {q,obs,sticky,add(sticky,(-1,0,0))} or hr[1]<0:continue
    for hk in [Kind.SLIME,Kind.HONEY]:
     if any(hk==mat and any(dist(add(hr,(k,0,0)),p)<=1 for k in offsets('mmwwm',word) for p in shape) for shape,mat,word in others):continue
     choices.append((obs,di,q,sticky,hr,hk))
 choices.sort(key=lambda v:(min(dist(v[2],p) for p in t0)+min(dist(v[2],p) for p in x1),v[2],v[0],v[1],v[4],int(v[5])))
 records=[];passed=None
 for i,(obs,di,q,sticky,hr,hk) in enumerate(choices):
  remaining=a.seconds-(time.monotonic()-start)
  if remaining<1:break
  case=a.out/f'placement{i:03}';case.mkdir();base=case/'input';base.mkdir();ff=Flyer.load(a.base/'problem.flyer')
  for p in removed:ff.remove(p)
  for p,b in [(q,Block(Kind.HONEY)),(hr,Block(hk)),(obs,Block.observer(di,powered=False)),(sticky,Block.piston(1,sticky=True))]:assert p not in ff._cells;ff.set(p,b)
  ff.save(base/'problem.flyer');loaded=Flyer.load(base/'problem.flyer');assert loaded._cells==ff._cells and loaded._piston_blocks==ff._piston_blocks
  cc=json.loads(json.dumps(c));next(p for p in cc['ports'] if p['name']=='T1_front')['at']=list(q);next(p for p in cc['ports'] if p['name']=='H0_front')['at']=list(hr);rows=[]
  for p in cc['ports']:
   for cy in range(3):
    for slot,v in enumerate(p['provenance']):
     if v=='supplied':rows.append((10*cy+2*slot,p['at'][0]+3*cy+p['word'][:slot].count('m'),*p['at'][1:],12))
  (base/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
  for order in ['before_natural','after_natural','interleaved']:dump(base/f'{order}.json',{**cc,'prescribed_order':order})
  # Input placements are unverified seeds; only a full combined native pass counts.
  run=subprocess.run([sys.executable,str(Path(__file__).with_name('search_T1_two_pushes.py')),str(base),str(case/'search'),'--mixed-recovery','--seconds',str(min(8 if a.extend_X1 else 5,remaining))]+(['--free-X1'] if a.free_X1 else ['--extend-X1'] if a.extend_X1 else []),capture_output=True,text=True)
  if run.returncode:raise RuntimeError(run.stderr)
  r=json.loads((case/'search/report.json').read_text(encoding='utf-8'));records.append({'placement':i,'observer':obs,'direction':di,'target':q,'sticky':sticky,'H0_root':hr,'H0_kind':hk.name,'models':len(r['records']),'native_tests':r['tests'],'passed':r['passed']})
  if r['passed']:passed=r['passed']
  dump(a.out/'report.json',{'scope':__doc__,'records':records,'domain_placements':len(choices),'passed':passed,'seconds':time.monotonic()-start})
  if passed:break
 dump(a.out/'report.json',{'scope':__doc__,'records':records,'domain_placements':len(choices),'passed':passed,'seconds':time.monotonic()-start});(a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'placements':len(records),'models':sum(r['models'] for r in records),'native_tests':sum(r['native_tests'] for r in records),'passed':passed,'seconds':time.monotonic()-start}),flush=True)
if __name__=='__main__':main()
