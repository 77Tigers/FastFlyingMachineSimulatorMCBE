"""T0 first push3 powered directly by a supplied G2 wwmmm observer.
Regenerate T0<=8, X0<=6 and G2<=6 glue, retain H2 drive and G0 pulse hardware.
Only native proof accepts physics; G0/X0/G2 strokes remain supplied inputs.
"""
import argparse,itertools,json,subprocess,time,hashlib
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
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--seconds',type=float,default=100)
 ap.add_argument('--free-recovery',action='store_true',help='Regenerate G2 recovery contacts within six glue rather than retaining the four-cell star')
 ap.add_argument('--geometry-control',action='store_true',help='Remove foreign hardware occupancy/contacts; save a necessary geometric witness only, never construct or native-test')
 ap.add_argument('--retain-essential',action='store_true',help='In geometry control, retain the two T0 piston bases and their initial arms')
 ap.add_argument('--supply-H2',action='store_true',help='Diagnostic component: remove H2 own-drive scaffold and supply its moves, retaining both relays')
 ap.add_argument('--clear-initial-and-source',action='store_true',help='Learned conflicts: clear initial extended destinations and keep X0 glue off the G2 observer track')
 a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 f=Flyer.load(a.base/'problem.flyer');c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
 if a.supply_H2:
  for p in [(15,2,11),(15,3,12),(14,2,12),(14,1,12),(14,2,11),(14,3,12)]:f.remove(p)
  next(p for p in c['ports'] if p['name']=='H2')['provenance']=['supplied']*3+[None,None]
 oldt={(15,1,11),(15,1,10),(15,2,10),(16,2,10),(17,2,10),(18,2,10),(19,2,10),(19,2,11)}
 oldg={(13,2,12),(13,1,12),(13,3,12),(13,2,11)};xroot=(16,3,11);groot=(13,2,12);root=(15,1,11);late=(19,2,11)
 fixed=set(f._cells)-(oldt|oldg|{xroot});g0={p for p in fixed if f._cells[p].kind==Kind.SLIME};honey={p for p in fixed if f._cells[p].kind==Kind.HONEY}
 essential={(17,1,11),(16,1,11),(17,2,11),(18,2,11)} if a.retain_essential else set()
 occupancy=essential if a.geometry_control else fixed
 motors=[p for p in itertools.product(range(11,18),range(0,6),range(8,15)) if p not in occupancy and dist(add(p,(3,0,0)),root)<=7 and dist(add(p,(3,0,0)),late)<=7 and dist(p,xroot)<=6]
 choices=[(p,di,add(p,(2-d[0],-d[1],-d[2]))) for p in motors for di,d in enumerate(D) if di!=1]
 choices.sort(key=lambda v:dist(v[2],groot)+dist(v[0],xroot));records=[];passed=None;geometry_witness=None
 for index,(motor,direction,obs) in enumerate(choices):
  if time.monotonic()-start>a.seconds:break
  if a.clear_initial_and_source and (direction==0 or add(motor,(1,0,0)) in {(17,1,11),(16,1,11),(17,2,11),(18,2,11)}):continue
  rec={'index':index,'motor':motor,'observer':obs,'direction':direction}
  if obs in occupancy or obs==motor:rec['status']='occupied';records.append(rec);continue
  blocked=occupancy|{motor,obs};tt={root,late,add(motor,(3,0,0))};model=cp_model.CpModel()
  domain=list(itertools.product(range(11,22),range(0,7),range(8,16)))
  t={p:model.NewBoolVar(f't{p}') for p in domain if p not in blocked and all(dist(p,root)+dist(p,q)+dist(root,q)<=14 for q in tt) and dist(p,(18,1,11))>1 and (not a.clear_initial_and_source or p!=(16,2,11)) and p not in {add(motor,(1,0,0)),add(motor,(2,0,0))}}
  g={p:model.NewBoolVar(f'g{p}') for p in domain if p not in blocked and dist(p,groot)<=5}
  x={p:model.NewBoolVar(f'x{p}') for p in domain if p not in blocked and dist(p,xroot)<=5}
  if not tt<=t.keys() or not ({groot} if a.free_recovery else oldg)<=g.keys() or xroot not in x:rec['status']='mandatory excluded';records.append(rec);continue
  for cells,targets,cap in [(t,tt,8),(g,{groot} if a.free_recovery else oldg,6),(x,{xroot},6)]:
   for p in targets:model.Add(cells[p]==1)
   model.Add(sum(cells.values())<=cap);connectivity(model,cells,min(targets),cap)
  if a.free_recovery and not a.supply_H2:
   for motor_base in [(14,1,12),(14,2,11),(14,3,12)]:model.Add(sum(g[p] for p in adj(motor_base) if p in g)>=1)
  model.Add(sum(g[p] for p in adj(obs) if p in g)>=1)
  model.Add(sum(x[p] for p in adj(motor) if p in x)>=1)
  model.Add(sum(x[p] for p in adj((16,2,11)) if p in x)>=1)
  for cells,delta in [(t,[-2,-1,0,1]),(g,[-2,-1,0])]:
   for p,v in cells.items():
    if not a.geometry_control and any(dist(add(p,(k,0,0)),q)<=1 for k in delta for q in g0):model.Add(v==0)
  for p,v in g.items():
   if not a.geometry_control and any(dist(p,add(q,(k,0,0)))<=1 for k in [0,1,2] for q in [(17,1,13),(17,2,13)]):model.Add(v==0)
   for k in [-1,0,1]:
    for q in [add(p,(k,0,0)),*adj(add(p,(k,0,0)))]:
     if q in t:model.Add(v+t[q]<=1)
  for p,v in x.items():
   if a.clear_initial_and_source and (p==(16,2,11) or any(dist(p,add(obs,(k,0,0)))<=1 for k in [-2,-1,0])):model.Add(v==0)
   if dist(p,(17,2,11))==1 or (not a.geometry_control and any(dist(add(p,(k,0,0)),q)<=1 for k in [-1,0,1] for q in honey)):model.Add(v==0)
   for cells in [g,t]:
    if p in cells:model.Add(v+cells[p]<=1)
  model.Minimize(sum(g.values())+sum(t.values())+sum(x.values()))
  solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=min(.5,max(.01,a.seconds-(time.monotonic()-start)));solver.parameters.num_search_workers=2
  result=solver.Solve(model);rec.update(status=solver.StatusName(result),seconds=solver.WallTime())
  if result in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
   if a.geometry_control:
    shapes={name:sorted(p for p,v in cells.items() if solver.Value(v)) for name,cells in [('G2',g),('T0',t),('X0',x)]}
    rec.update(shapes=shapes,foreign_occupied={name:sorted(set(map(tuple,shape))&fixed) for name,shape in shapes.items()},scope='Necessary geometry only, foreign hardware/contact constraints removed; not a flyer.')
    geometry_witness=rec;records.append(rec);break
   case=a.out/f'case{index:03}';case.mkdir();ff=Flyer.load(a.base/'problem.flyer')
   if a.supply_H2:
    for p in [(15,2,11),(15,3,12),(14,2,12),(14,1,12),(14,2,11),(14,3,12)]:ff.remove(p)
   for p in oldg|oldt|{xroot}:ff.remove(p)
   shapes=[]
   for cells,kind in [(g,Kind.SLIME),(t,Kind.SLIME),(x,Kind.HONEY)]:
    shape={p for p,v in cells.items() if solver.Value(v)};shapes.append(sorted(shape))
    for p in shape:ff.set(p,Block(kind))
   ff.set(motor,Block.piston(0));ff.set(obs,Block.observer(direction,powered=False))
   ff.save(case/'problem.flyer');assert Flyer.load(case/'problem.flyer')._cells==ff._cells
   cc=json.loads(json.dumps(c));cc['name']=case.name;next(p for p in cc['ports'] if p['name']=='T0')['provenance']=['internal',None,None,'internal','internal']
   cc['boundary_envelope']={'min':[11,0,8],'max':[27,7,16]};rows=[]
   for p in cc['ports']:
    for cy in range(3):
     for slot,v in enumerate(p['provenance']):
      if v=='supplied':rows.append((cy*10+slot*2,p['at'][0]+cy*3+p['word'][:slot].count('m'),*p['at'][1:],12))
   (case/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
   for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
   rec['shapes_G2_T0_X0']=shapes;dump(case/'preparation.json',rec)
   subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,capture_output=True)
   rec['native']=json.loads((case/'native.json').read_text(encoding='utf-8'));(case/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
   if rec['native']['verified']:passed=str(case)
  records.append(rec);dump(a.out/'report.json',{'scope':__doc__,'records':records,'passed':passed,'seconds':time.monotonic()-start})
  if 'native' in rec:print(json.dumps({'index':index,'native':rec['native']}),flush=True)
  if passed:break
 dump(a.out/'report.json',{'scope':__doc__,'records':records,'passed':passed,'seconds':time.monotonic()-start,'choices':len(choices),'geometry_only':a.geometry_control,'retained_essential':a.retain_essential,'H2_supplied_diagnostic':a.supply_H2,'geometry_witness':geometry_witness})
 (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'records':len(records),'passed':passed,'seconds':time.monotonic()-start}),flush=True)

if __name__=='__main__':main()
