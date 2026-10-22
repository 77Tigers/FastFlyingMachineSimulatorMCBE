"""Replace T1 RB with H0 observer powering its own glue on1/2.

T1<=7 glue/no RB, T0<=8, local H0<=2 glue/two observers. Full budget
retains H0's four future source glue+RB:6glue+RB+2obs=9. Other drivers
remain supplied. All construction is component-only until full proof.
"""
import argparse,copy,itertools,json,subprocess,time
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer,body_of
from fastflyer import Block,Kind
from search_T1_two_pushes import D,add,adj,dist,dump,witnessed_sticky_pickup
from search_T1_pull_routes import offsets
from model_recovery_layout import connectivity
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--seconds',type=float,default=85);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 f=Flyer.load(a.base/'problem.flyer');c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'));ports={p['name']:p for p in c['ports']};tr=tuple(ports['T0']['at']);tl=(19,4,9);pull=tuple(ports['T1_front']['at']);hr=tuple(ports['H0_front']['at']);oldt=body_of(f._cells,tr);oldh=body_of(f._cells,hr);assert len(oldt)==8 and len(oldh)==1
 removed=oldt|oldh|{pull};fixed=set(f._cells)-removed;others=[(body_of(f._cells,tuple(p['at'])),f._cells[tuple(p['at'])].kind,p['word']) for p in c['ports'] if p['name'] not in ['T0','T1_front','H0_front']];choices=[]
 for center in itertools.product(range(13,21),range(1,9),range(9,17)):
  for ds in itertools.combinations(D[2:],2):
   targets={center,pull,*[add(add(center,(1,0,0)),d) for d in ds]};motors={add(add(center,(-1,0,0)),d) for d in ds};output=add(center,(-1,0,0))
   if targets&fixed or motors&fixed or targets&motors or len(targets)!=4 or output in fixed:continue
   if any(dist(p,q)>6 for p in targets for q in targets):continue
   if not all(any(dist(tr,p)+dist(p,tl)==dist(tr,tl) for p in adj(m)) for m in motors):continue
   for di,u in enumerate(D):
    obs=add(output,tuple(-v for v in u))
    if obs in fixed|targets|motors or obs==output or dist(obs,hr)>2:continue
    if any(dist(obs,p)<=1 for shape,_,_ in others for p in shape):continue
    choices.append((center,targets,motors,output,obs,di))
 choices.sort(key=lambda x:(dist(x[0],pull),dist(x[4],hr),x[0],x[4]));domain=list(itertools.product(range(12,23),range(0,10),range(8,18)));records=[];tests=0;passed=None
 dump(a.out/'domain.json',{'choices':len(choices),'scope':__doc__});(a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
 for index,(center,targets,motors,output,obs,di) in enumerate(choices):
  for kind in [Kind.HONEY,Kind.SLIME]:
   if time.monotonic()-start>a.seconds:break
   rec={'index':index,'center':center,'motors':sorted(motors),'observer':obs,'direction':di,'T1_kind':kind.name};blocked=fixed|motors|{obs,output};model=cp_model.CpModel()
   t={p:model.NewBoolVar('t'+str(p)) for p in domain if p not in blocked and dist(p,tr)+dist(p,tl)==dist(tr,tl)}
   g={p:model.NewBoolVar('g'+str(p)) for p in domain if p not in blocked and all(dist(p,pull)+dist(p,q)+dist(pull,q)<=12 for q in targets) and p not in {add(m,(1,0,0)) for m in motors}}
   hh={p:model.NewBoolVar('h'+str(p)) for p in domain if p not in blocked and dist(p,hr)<=1}
   if not targets<=g.keys() or not {tr,tl}<=t.keys() or hr not in hh:rec['status']='mandatory excluded';records.append(rec);continue
   specs=[('T0',t,Kind.SLIME,'mwwmm',8,{tr,tl},tr),('T1',g,kind,'wmmmw',7,targets,pull),('H0',hh,Kind.SLIME,'mmwwm',2,{hr},hr)]
   for name,cells,mat,word,cap,pins,root in specs:
    model.Add(sum(cells.values())<=cap);connectivity(model,cells,root,cap)
    for p in pins:model.Add(cells[p]==1)
    for p,v in cells.items():
     if any(mat==other and any(dist(add(p,(k,0,0)),q)<=1 for k in offsets(word,w) for q in shape) for shape,other,w in others):model.Add(v==0)
     if name!='H0' and dist(p,obs)<=1:model.Add(v==0)
   for m in motors:model.Add(sum(t[p] for p in adj(m) if p in t)>=1)
   model.Add(sum(hh[p] for p in adj(obs) if p in hh)>=1)
   for p,v in t.items():
    if witnessed_sticky_pickup(p):model.Add(v==0)
   for ai,(_,aa,ak,aw,*_) in enumerate(specs):
    for _,bb,bk,bw,*_ in specs[ai+1:]:
     for p,v in aa.items():
      bad=set()
      for k in offsets(aw,bw):
       q=add(p,(k,0,0));bad.add(q)
       if ak==bk:bad.update(adj(q))
      for q in bad:
       if q in bb:model.Add(v+bb[q]<=1)
   model.Minimize(sum(t.values())+sum(g.values())+sum(hh.values()));s=cp_model.CpSolver();s.parameters.max_time_in_seconds=.4;s.parameters.num_search_workers=2;status=s.Solve(model);rec.update(status=s.StatusName(status),seconds=s.WallTime())
   if status in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
    case=a.out/f'case{index:03}_{kind.name}';case.mkdir();tests+=1;ff=Flyer.load(a.base/'problem.flyer')
    for p in removed:ff.remove(p)
    shapes={name:sorted(p for p,v in cells.items() if s.Value(v)) for name,cells,*_ in specs}
    for name,cells,mat,*_ in specs:
     for p in shapes[name]:assert p not in ff._cells;ff.set(p,Block(mat))
    for p,b in [(obs,Block.observer(di,powered=False)),*[(m,Block.piston(0)) for m in motors]]:assert p not in ff._cells;ff.set(p,b)
    ff.save(case/'problem.flyer');loaded=Flyer.load(case/'problem.flyer');assert loaded._cells==ff._cells and loaded._piston_blocks==ff._piston_blocks
    cc=copy.deepcopy(c);next(p for p in cc['ports'] if p['name']=='T1_front')['provenance']=[None,'internal','internal','internal',None];cc['name']=case.name;rows=[]
    for p in cc['ports']:
     for cy in range(3):
      for slot,v in enumerate(p['provenance']):
       if v=='supplied':rows.append((10*cy+2*slot,p['at'][0]+3*cy+p['word'][:slot].count('m'),*p['at'][1:],12))
    (case/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
    for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
    rec['shapes']=shapes;dump(case/'preparation.json',rec);subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,capture_output=True,check=False);rec['native']=json.loads((case/'native.json').read_text(encoding='utf-8'))
    if rec['native']['verified']:passed=str(case)
   records.append(rec);dump(a.out/'report.json',{'scope':__doc__,'choices':len(choices),'records':records,'tests':tests,'passed':passed,'seconds':time.monotonic()-start})
   if passed:break
  if passed or time.monotonic()-start>a.seconds:break
 dump(a.out/'report.json',{'scope':__doc__,'choices':len(choices),'records':records,'tests':tests,'passed':passed,'seconds':time.monotonic()-start});print(json.dumps({'models':len(records),'choices':len(choices),'tests':tests,'passed':passed,'seconds':time.monotonic()-start}),flush=True)
if __name__=='__main__':main()
