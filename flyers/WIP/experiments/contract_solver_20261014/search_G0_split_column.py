"""Bounded G0 ordinary-column closure on the verified split-relay component.

Regenerate connected G0<=6 and T0<=8 glue, keep both pulse observers and
all verified T0/H2 motors/sources. G0 motor initial positions are center-2X
so T0 move0 delivers them to its source plane before G0 first1.
Geometric exclusions are scoped separated-body hypotheses. Native tests
decide firing, switch-off, recovery and loads; X0/G2 remain supplied.
"""
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

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
 ap.add_argument('--seconds',type=float,default=150);ap.add_argument('--cp-seconds',type=float,default=.3)
 ap.add_argument('--max-native',type=int,default=16)
 ap.add_argument('--front-sticky',action='store_true',help='T1 supplied front carrier takes sticky transport; G0 gets seven glue in independently feasible whole12 budget')
 ap.add_argument('--geometry-control-no-pickups',action='store_true',help='Necessary geometry diagnostic: omit T0 motor contacts, never construct or native-test')
 a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 # Optional changed role hypothesis: a front T1 input carries the sticky.
 f=Flyer.load(a.base/'problem.flyer');c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
 front=(17,2,11);gcap=7 if a.front_sticky else 6
 if a.front_sticky:
  # This replaces an old G0 root, so it is added after removing old glue below.
  c['ports'].append({'name':'T1_front','at':list(front),'role':'input','word':'wmmmw','provenance':[None,'supplied','supplied','supplied',None]})
 # Work in the accepted artifact's saved (Y+2) coordinates.
 g0old={(17,2,11),(18,2,11),(18,2,12),(18,2,13),(18,3,13),(18,4,13)}
 t0old={(15,3,10),(15,3,11),(16,3,10),(16,4,10),(17,4,10),(18,4,10),(19,4,10),(19,4,11)}
 assert all(f._cells[p].kind==Kind.SLIME for p in g0old|t0old)
 fixed=set(f._cells)-(g0old|t0old);observers={(17,3,13),(17,4,13)};troot=(15,3,11);tlate=(19,4,11)
 foreign={kind:{p for p in fixed if f._cells[p].kind==kind} for kind in [Kind.HONEY,Kind.SLIME]}
 if a.front_sticky:fixed.add(front);foreign[Kind.SLIME].add(front)
 choices=[]
 for center in itertools.product(range(17,21),range(1,7),range(9,16)):
  rb=add(center,(-1,0,0))
  for ds in itertools.combinations(D[2:],3):
   targets={center,*[add(center,d) for d in ds]};motors={add(q,(-2,0,0)) for q in targets-{center}}
   if (targets|motors|{rb})&fixed or len(targets|motors|{rb})!=8:continue
   if any(min(dist(o,q) for q in targets)>3 for o in observers):continue
   if any(min(dist(m,troot),dist(m,tlate))>7 for m in motors):continue
   choices.append((center,rb,targets,motors))
 choices.sort(key=lambda v:sum(min(dist(m,t) for t in t0old) for m in v[3])+sum(min(dist(o,p) for p in v[2]) for o in observers))
 records=[];passed=None;tests=0;domain=list(itertools.product(range(13,23),range(0,8),range(8,17)))
 for index,(center,rb,targets,motors) in enumerate(choices):
  for kind in [Kind.HONEY,Kind.SLIME]:
   if a.front_sticky and kind!=Kind.HONEY:continue
   if time.monotonic()-start>=a.seconds or tests>=a.max_native:break
   rec={'index':index,'center':center,'RB':rb,'motors':sorted(motors),'material':kind.name};model=cp_model.CpModel();blocked=fixed|motors|{rb}
   t={p:model.NewBoolVar(f't{p}') for p in domain if p not in blocked and dist(p,troot)+dist(p,tlate)+dist(troot,tlate)<=14 and p!=(16,4,11)}
   g={p:model.NewBoolVar(f'g{p}') for p in domain if p not in blocked and dist(p,center)<gcap}
   if not targets<=g.keys() or not {troot,tlate}<=t.keys():rec['status']='mandatory excluded';records.append(rec);continue
   for cells,ts,cap,root in [(t,{troot,tlate},8,troot),(g,targets,gcap,center)]:
    for p in ts:model.Add(cells[p]==1)
    model.Add(sum(cells.values())<=cap);connectivity(model,cells,root,cap)
   if not a.geometry_control_no_pickups:
    for motor in motors:model.Add(sum(t[p] for p in adj(motor) if p in t)>=1)
   for observer in observers:model.Add(sum(g[p] for p in adj(observer) if p in g)>=1)
   for p,v in t.items():
    if any(dist(p,q)<=1 for q in foreign[Kind.SLIME]):model.Add(v==0)
    if a.front_sticky and any(dist(p,add(front,(k,0,0)))<=1 for k in [-1,0,1]):model.Add(v==0)
    for k in [-1,0,1]:
     for q in [add(p,(k,0,0)),*adj(add(p,(k,0,0)))]:
      if q in g and (kind==Kind.SLIME or q==p):model.Add(v+g[q]<=1)
   for p,v in g.items():
    if a.front_sticky and dist(p,(17,3,11))==1:model.Add(v==0)
    if any(dist(add(p,(k,0,0)),q)<=1 for k in [-1,0,1] for q in foreign[kind]):model.Add(v==0)
    if p in t:model.Add(v+t[p]<=1)
   model.Minimize(sum(t.values())+sum(g.values()));s=cp_model.CpSolver();s.parameters.max_time_in_seconds=min(a.cp_seconds,max(.01,a.seconds-(time.monotonic()-start)));s.parameters.num_search_workers=2
   result=s.Solve(model);rec.update(status=s.StatusName(result),seconds=s.WallTime())
   if result in [cp_model.OPTIMAL,cp_model.FEASIBLE] and a.geometry_control_no_pickups:
    rec['shapes']={name:sorted(p for p,v in cells.items() if s.Value(v)) for name,cells in [('G0',g),('T0',t)]}
    rec['scope']='Motor recovery contacts omitted: geometry witness only, not a flyer.';records.append(rec)
    dump(a.out/'report.json',{'scope':rec['scope'],'records':records,'passed':None,'tests':0,'choices':len(choices),'seconds':time.monotonic()-start,'geometry_witness':rec})
    (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(rec),flush=True);return
   if result in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
    case=a.out/f'case{tests:03}';case.mkdir();tests+=1;ff=Flyer.load(a.base/'problem.flyer')
    for p in g0old|t0old:ff.remove(p)
    if a.front_sticky:ff.set(front,Block(Kind.SLIME))
    shapes={name:sorted(p for p,v in cells.items() if s.Value(v)) for name,cells in [('G0',g),('T0',t)]}
    for name,shape in shapes.items():
     for p in shape:ff.set(p,Block(kind if name=='G0' else Kind.SLIME))
    ff.set(rb,Block(Kind.REDSTONE_BLOCK))
    for p in motors:ff.set(p,Block.piston(0))
    out=ff.canonicalize();delta=tuple(min(p[i] for p in out._cells)-min(p[i] for p in ff._cells) for i in range(3));out.save(case/'problem.flyer');reload=Flyer.load(case/'problem.flyer');assert reload._cells==out._cells and reload._piston_blocks==out._piston_blocks
    cc=json.loads(json.dumps(c));cc['name']=case.name
    for port in cc['ports']:
     if port['name']=='G0':port['at']=list(center);port['provenance']=[None,'internal','internal','internal',None]
     port['at']=list(add(tuple(port['at']),delta))
    cc['boundary_envelope']={'min':[10,0,7],'max':[32,12,19]};rows=[]
    for port in cc['ports']:
     for cy in range(3):
      for slot,v in enumerate(port['provenance']):
       if v=='supplied':rows.append((cy*10+slot*2,port['at'][0]+cy*3+port['word'][:slot].count('m'),*port['at'][1:],12))
    (case/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
    for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
    rec['shapes']=shapes;dump(case/'preparation.json',rec);(case/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    native=subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,capture_output=True)
    assert (case/'native.json').exists(),native.stderr;rec['native']=json.loads((case/'native.json').read_text(encoding='utf-8'));print(json.dumps({'index':index,'kind':kind.name,'native':rec['native']}),flush=True)
    if rec['native']['verified']:passed=str(case)
   records.append(rec);dump(a.out/'report.json',{'scope':__doc__,'records':records,'passed':passed,'tests':tests,'choices':len(choices),'seconds':time.monotonic()-start})
   if passed:break
  if passed or time.monotonic()-start>=a.seconds or tests>=a.max_native:break
 dump(a.out/'report.json',{'scope':__doc__,'records':records,'passed':passed,'tests':tests,'choices':len(choices),'seconds':time.monotonic()-start});(a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'records':len(records),'passed':passed,'tests':tests,'seconds':time.monotonic()-start}),flush=True)
if __name__=='__main__':main()
