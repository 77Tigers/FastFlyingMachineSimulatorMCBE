"""Bounded T1 pull3 source/recovery routing on accepted56-cell component.

One added G0 observer replaces its unused seventh-glue mass reserve.
Connected T1<=6 glue must carry the existing T0 sticky and include its new
pull target. H0 recovery has one supplied glue cell. Native tests decide
timing/loads; neither H0's drive nor T1 push1/2 are constructed here.
"""
import os as _research_os
import argparse,itertools,json,subprocess,time
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer
from fastflyer import Block,Kind
from model_recovery_layout import connectivity
ROOT=Path(__file__).resolve().parents[4]
D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(p,d):return tuple(a+b for a,b in zip(p,d))
def adj(p):return [add(p,d) for d in D]
def dist(p,q):return sum(abs(a-b) for a,b in zip(p,q))
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def offsets(a,b):
 return {a[:s].count('m')+i-b[:s].count('m')-j for s in range(5) for i in range(1+(a[s]=='m')) for j in range(1+(b[s]=='m'))}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--seconds',type=float,default=130);ap.add_argument('--max-native',type=int,default=20);ap.add_argument('--clear-T0-opening',action='store_true');ap.add_argument('--free-T0',action='store_true');a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 f=Flyer.load(a.base/'problem.flyer');c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'));old=(17,2,11);fixed=set(f._cells)-{old}
 bodies={'G0':({(18,5,12),(18,5,11),(18,5,13),(18,6,12),(18,4,13),(18,3,13)},Kind.HONEY,'wmmmw'),'H2':({(15,3,12),(15,2,12),(15,1,12),(15,0,12),(15,1,11)},Kind.HONEY,'mmmww'),'X0':({(12,4,11),(13,4,11),(13,4,12),(14,4,11),(14,4,12),(15,4,11)},Kind.HONEY,'mmmww'),'T0':({(15,3,10),(15,3,11),(16,3,10),(16,4,10),(17,4,10),(18,4,10),(19,4,10),(19,4,11)},Kind.SLIME,'mwwmm'),'X1':({(15,5,12),(15,5,11),(15,5,13),(15,6,12)},Kind.SLIME,'mwwmm'),'G2':({(13,0,12),(13,1,11),(13,1,12),(13,2,11),(13,2,12)},Kind.SLIME,'wwmmm')}
 for shape,kind,_ in bodies.values():assert all(f._cells[p].kind==kind for p in shape)
 if a.free_T0:fixed-=bodies['T0'][0]
 roots=[p for p in adj((17,3,11)) if p not in fixed];choices=[]
 for obs in sorted(set().union(*(set(adj(p)) for p in bodies['G0'][0]))-fixed):
  for di in [1,2,3,4,5]:
   target=add(obs,(-3+D[di][0],D[di][1],D[di][2]));piston=add(target,(2,0,0))
   if target in fixed or piston in fixed or len({obs,target,piston})<3:continue
   for root in roots:
    if dist(root,target)>5:continue
    for hroot in adj(piston):
     if hroot in fixed or hroot in {obs,target,piston,root}:continue
     for tk,hk in itertools.product([Kind.SLIME,Kind.HONEY],repeat=2):choices.append((obs,di,target,piston,root,hroot,tk,hk))
 choices.sort(key=lambda v:(dist(v[4],v[2]),v[0],v[1],v[4],v[5],int(v[6]),int(v[7])))
 records=[];tests=0;passed=None;domain=list(itertools.product(range(11,23),range(0,9),range(8,17)))
 for index,(obs,di,target,piston,root,hroot,tk,hk) in enumerate(choices):
  if time.monotonic()-start>a.seconds or tests>=a.max_native:break
  rec={'index':index,'observer':obs,'direction':di,'target':target,'sticky':piston,'root':root,'H0_root':hroot,'T1_kind':tk.name,'H0_kind':hk.name}
  if any(kind==hk and any(dist(add(hroot,(k,0,0)),p)<=1 for k in offsets('mmwwm',word) for p in shape) for name,(shape,kind,word) in bodies.items() if not(a.free_T0 and name=='T0')):rec['status']='H0 contact excluded';records.append(rec);continue
  blocked=fixed|{obs,piston,hroot};model=cp_model.CpModel()
  cells={p:model.NewBoolVar(str(p)) for p in domain if p not in blocked and dist(p,root)+dist(p,target)+dist(root,target)<=10}
  if root not in cells or target not in cells:rec['status']='mandatory excluded';records.append(rec);continue
  for p in [root,target]:model.Add(cells[p]==1)
  model.Add(sum(cells.values())<=6);connectivity(model,cells,root,6)
  t={}
  if a.free_T0:
   tr=(15,3,11);tl=(19,4,11)
   t={p:model.NewBoolVar('T0'+str(p)) for p in domain if p not in blocked and p!=(16,4,11) and dist(p,tr)+dist(p,tl)+dist(tr,tl)<=14}
   if tr not in t or tl not in t:rec['status']='T0 mandatory excluded';records.append(rec);continue
   model.Add(t[tr]==1);model.Add(t[tl]==1);model.Add(sum(t.values())<=8);connectivity(model,t,tr,8)
   for q,v in t.items():
    if any(kind==Kind.SLIME and any(dist(add(q,(k,0,0)),p)<=1 for k in offsets('mwwmm',word) for p in shape) for name,(shape,kind,word) in bodies.items() if name!='T0'):model.Add(v==0)
    if hk==Kind.SLIME and any(dist(add(q,(k,0,0)),hroot)<=1 for k in offsets('mwwmm','mmwwm')):model.Add(v==0)
    if dist(q,obs)==1:model.Add(v==0)
    for p,u in cells.items():
     if p==q or p==add(q,(1,0,0)) or (tk==Kind.SLIME and any(dist(add(p,(k,0,0)),q)<=1 for k in offsets('wmmmw','mwwmm'))):model.Add(v+u<=1)
  for p,v in cells.items():
   if any(kind==tk and any(dist(add(p,(k,0,0)),q)<=1 for k in offsets('wmmmw',word) for q in shape) for name,(shape,kind,word) in bodies.items() if not(a.free_T0 and name=='T0')):model.Add(v==0)
   if tk==hk and any(dist(add(p,(k,0,0)),hroot)<=1 for k in offsets('wmmmw','mmwwm')):model.Add(v==0)
   # Learned lower H2 obstruction, all relevant relative one-step destinations.
   if any(p==add(q,(k,0,0)) for q in bodies['H2'][0] for k in [1,2]):model.Add(v==0)
   if a.clear_T0_opening and not a.free_T0 and any(p==add(q,(1,0,0)) for q in bodies['T0'][0]):model.Add(v==0)
  model.Minimize(sum(cells.values())+sum(t.values()));s=cp_model.CpSolver();s.parameters.max_time_in_seconds=.3;s.parameters.num_search_workers=2;result=s.Solve(model);rec.update(status=s.StatusName(result),seconds=s.WallTime())
  if result in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
   case=a.out/f'case{tests:03}';case.mkdir();tests+=1;ff=Flyer.load(a.base/'problem.flyer');ff.remove(old);shape=sorted(p for p,v in cells.items() if s.Value(v))
   if a.free_T0:
    for p in bodies['T0'][0]:ff.remove(p)
    rec['T0_shape']=sorted(p for p,v in t.items() if s.Value(v))
    for p in rec['T0_shape']:ff.set(p,Block(Kind.SLIME))
   for p in shape:assert p not in ff._cells;ff.set(p,Block(tk))
   for p,b in [(obs,Block.observer(di,powered=False)),(piston,Block.piston(1,sticky=True)),(hroot,Block(hk))]:assert p not in ff._cells;ff.set(p,b)
   out=ff.canonicalize();delta=tuple(min(p[i] for p in out._cells)-min(p[i] for p in ff._cells) for i in range(3));out.save(case/'problem.flyer');loaded=Flyer.load(case/'problem.flyer');assert loaded._cells==out._cells and loaded._piston_blocks==out._piston_blocks
   cc=json.loads(json.dumps(c));port=next(p for p in cc['ports'] if p['name']=='T1_front');port['at']=list(root);port['provenance'][3]='internal'
   cc['ports'].append({'name':'H0_front','at':list(hroot),'word':'mmwwm','role':'input','provenance':['supplied','supplied',None,None,'supplied']})
   for p in cc['ports']:p['at']=list(add(tuple(p['at']),delta))
   cc['boundary_envelope']={'min':[10,0,7],'max':[35,13,20]};cc['name']=case.name;rows=[]
   for p in cc['ports']:
    for cy in range(3):
     for slot,v in enumerate(p['provenance']):
      if v=='supplied':rows.append((10*cy+2*slot,p['at'][0]+3*cy+p['word'][:slot].count('m'),*p['at'][1:],12))
   (case/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
   for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
   rec['shape']=shape;dump(case/'preparation.json',rec);(case/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
   subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,capture_output=True)
   rec['native']=json.loads((case/'native.json').read_text(encoding='utf-8'));print(json.dumps({'index':index,'native':rec['native']}),flush=True)
   if rec['native']['verified']:passed=str(case)
  records.append(rec);dump(a.out/'report.json',{'scope':__doc__,'records':records,'passed':passed,'tests':tests,'choices':len(choices),'seconds':time.monotonic()-start})
  if passed:break
 dump(a.out/'report.json',{'scope':__doc__,'records':records,'passed':passed,'tests':tests,'choices':len(choices),'seconds':time.monotonic()-start});(a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'records':len(records),'tests':tests,'passed':passed,'seconds':time.monotonic()-start}),flush=True)
if __name__=='__main__':main()
