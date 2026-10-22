"""Bounded G0/T0 shared four-motor source construction on the accepted dual relay.
Regenerate <=6 G0 and <=8 T0 slime, retain relay/H2 drive and X0 carrier.
Only native success is physical evidence; CP negatives apply to this domain.
"""
import os as _research_os
import argparse,hashlib,itertools,json,subprocess,time
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer
from fastflyer import Block,Kind
from model_recovery_layout import connectivity
ROOT=Path(__file__).resolve().parents[4]
D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
SIDE=D[2:]
def add(p,q):return tuple(x+y for x,y in zip(p,q))
def adj(p):return [add(p,d) for d in D]
def dist(p,q):return sum(abs(x-y) for x,y in zip(p,q))
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
 ap.add_argument('--seconds',type=float,default=150);ap.add_argument('--cp-seconds',type=float,default=2)
 ap.add_argument('--free-X0',action='store_true',help='Regenerate up to six X0 honey for the first T0 motor pickup instead of keeping one contact fixed')
 ap.add_argument('--external-pulses',action='store_true',help='T1 wmmmw supplies the two observers; regenerate up to seven G0 glue and keep its pulse contacts clear')
 a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 f=Flyer.load(a.base/'problem.flyer');c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
 if a.external_pulses:
  for p in [(17,1,14),(17,2,14)]:
   assert p not in f._cells;f.set(p,Block(Kind.HONEY))
  c['ports'].append({'name':'T1_pulse','at':[17,1,14],'role':'input','word':'wmmmw','provenance':[None,'supplied','supplied','supplied',None]})
 oldg={(17,0,11),(18,0,11),(18,0,12),(18,0,13),(18,1,13),(18,2,13)}
 oldt={(15,1,11),(15,1,10),(15,2,10),(16,2,10),(17,2,10),(18,2,10),(19,2,10),(19,2,11)}
 assert all(f._cells[p].kind==Kind.SLIME for p in oldg|oldt)
 fixed=set(f._cells)-(oldg|oldt);g2={p for p in fixed if f._cells[p].kind==Kind.SLIME}
 root=(15,1,11);late=(19,2,11);sticky=(17,1,11);observers=[(17,1,13),(17,2,13)];x0=(16,3,11)
 gcap=7 if a.external_pulses else 6
 records=[];passed=None
 firsts=[p for p in itertools.product(range(12,19),range(-1,6),range(8,15)) if dist(add(p,(3,0,0)),root)<=7 and dist(add(p,(3,0,0)),late)<=7 and dist(p,x0)<=6] if a.free_X0 else adj(x0)
 firsts=sorted(firsts,key=lambda p:(dist(p,x0),p))
 for index,(motor,off) in enumerate(itertools.product(firsts,SIDE)):
  if time.monotonic()-start>a.seconds:break
  rb=add(add(motor,(1,0,0)),off)
  normals={add(add(rb,(-1,0,0)),tuple(-v for v in d)) for d in SIDE}-{motor}
  actors={rb,motor,*normals};gt={add(n,(2,0,0)) for n in normals};tt={root,late,add(motor,(3,0,0))}
  rec={'index':index,'rb':rb,'first_T0':motor,'G0_normals':sorted(normals)}
  if len(actors)!=5 or actors&fixed or gt&(fixed|actors) or tt&(fixed|actors):rec['status']='initial occupancy';records.append(rec);continue
  m=cp_model.CpModel();blocked=(fixed-({x0} if a.free_X0 else set()))|actors;domain=list(itertools.product(range(12,22),range(-1,6),range(8,16)))
  gg={p:m.NewBoolVar(f'g{p}') for p in domain if p not in blocked and all(dist(p,q)<=gcap-1 for q in gt)}
  tg={p:m.NewBoolVar(f't{p}') for p in domain if p not in blocked and all(dist(p,root)+dist(p,q)+dist(root,q)<=14 for q in tt) and dist(p,add(sticky,(1,0,0)))>1}
  xg={p:m.NewBoolVar(f'x{p}') for p in domain if p not in blocked and dist(p,x0)<=5} if a.free_X0 else {}
  if not gt<=gg.keys() or not tt<=tg.keys():rec['status']='mandatory excluded';records.append(rec);continue
  for cells,targets,cap in [(gg,gt,gcap),(tg,tt,8)]:
   for p in targets:m.Add(cells[p]==1)
   m.Add(sum(cells.values())<=cap);connectivity(m,cells,min(targets),cap)
  for p in [sticky,rb]+([] if a.external_pulses else observers):m.Add(sum(gg[q] for q in adj(p) if q in gg)>=1)
  for p in normals:m.Add(sum(tg[q] for q in adj(p) if q in tg)>=1)
  for p,v in gg.items():
   if a.external_pulses and any(dist(p,q)<=1 for q in observers):m.Add(v==0)
   for delta in [-1,0,1,2]:
    for q in [add(p,(delta,0,0)),*adj(add(p,(delta,0,0)))]:
     if q in tg:m.Add(v+tg[q]<=1)
   if any(dist(add(p,(d,0,0)),q)<=1 for d in [0,1,2] for q in g2):m.Add(v==0)
  for p,v in tg.items():
   if any(dist(add(p,(d,0,0)),q)<=1 for d in [-1,0,1] for q in g2):m.Add(v==0)
  if a.free_X0:
   m.Add(sum(xg.values())<=6);connectivity(m,xg,x0,6)
   m.Add(sum(xg[q] for q in adj(motor) if q in xg)>=1)
   late_motor=(17,2,11)
   m.Add(sum(xg[q] for q in adj(add(late_motor,(-1,0,0))) if q in xg)>=1)
   honey={p for p in fixed if p!=x0 and f._cells[p].kind==Kind.HONEY}
   for p,v in xg.items():
    if dist(p,late_motor)==1 or any(dist(add(p,(d,0,0)),q)<=1 for d in [-1,0,1] for q in honey):m.Add(v==0)
   for cells in [gg,tg]:
    for p in cells.keys()&xg.keys():m.Add(cells[p]+xg[p]<=1)
  m.Minimize(sum(gg.values())+sum(tg.values())+sum(xg.values()))
  solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=min(a.cp_seconds,max(.01,a.seconds-(time.monotonic()-start)));solver.parameters.num_search_workers=2
  result=solver.Solve(m);rec.update(status=solver.StatusName(result),seconds=solver.WallTime())
  if result in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
   g={p for p,v in gg.items() if solver.Value(v)};t={p for p,v in tg.items() if solver.Value(v)};case=a.out/f'case{index:02}';case.mkdir()
   ff=Flyer.load(a.base/'problem.flyer')
   if a.external_pulses:
    for p in [(17,1,14),(17,2,14)]:ff.set(p,Block(Kind.HONEY))
   for p in oldg|oldt:ff.remove(p)
   if a.free_X0:
    ff.remove(x0)
    for p,v in xg.items():
     if solver.Value(v):ff.set(p,Block(Kind.HONEY))
   for p in g|t:ff.set(p,Block(Kind.SLIME))
   ff.set(rb,Block(Kind.REDSTONE_BLOCK))
   for p in normals|{motor}:ff.set(p,Block.piston(0))
   ff.save(case/'problem.flyer');delta=tuple(min(p[k] for p in Flyer.load(case/'problem.flyer')._cells)-min(p[k] for p in ff._cells) for k in range(3))
   assert Flyer.load(case/'problem.flyer')._cells=={add(p,delta):b for p,b in ff._cells.items()}
   cc=json.loads(json.dumps(c));cc['name']=case.name;next(p for p in cc['ports'] if p['name']=='G0')['at']=min(g)
   next(p for p in cc['ports'] if p['name']=='G0')['provenance']=[None,'internal','internal','internal',None]
   next(p for p in cc['ports'] if p['name']=='T0')['provenance']=['internal',None,None,'internal','internal']
   for p in cc['ports']:p['at']=add(p['at'],delta)
   cc['boundary_envelope']={'min':[min(p[k] for p in Flyer.load(case/'problem.flyer')._cells) for k in range(3)],'max':[max(p[k] for p in Flyer.load(case/'problem.flyer')._cells) for k in range(3)]}
   rows=[]
   for p in cc['ports']:
    for cy in range(3):
     for slot,v in enumerate(p['provenance']):
      if v=='supplied':rows.append((cy*10+slot*2,p['at'][0]+cy*3+p['word'][:slot].count('m'),*p['at'][1:],12))
   (case/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
   for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
   rec.update(X0_glue=sorted(p for p,v in xg.items() if solver.Value(v)) if a.free_X0 else [x0],G0_glue=sorted(g),T0_glue=sorted(t),delta=delta,case=str(case));dump(case/'preparation.json',rec)
   proc=subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,capture_output=True)
   assert (case/'native.json').exists(),proc.stderr
   rec['native']=json.loads((case/'native.json').read_text(encoding='utf-8'))
   (case/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
   if rec['native']['verified']:passed=str(case)
  records.append(rec);dump(a.out/'report.json',{'scope':__doc__,'records':records,'passed':passed,'seconds':time.monotonic()-start,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
  print(json.dumps({'index':index,'status':rec['status'],'native':rec.get('native',{}).get('verified')}),flush=True)
  if passed:break
 dump(a.out/'report.json',{'scope':__doc__,'records':records,'passed':passed,'seconds':time.monotonic()-start,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
 (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
 print(json.dumps({'tested':len(records),'passed':passed,'seconds':time.monotonic()-start}),flush=True)

if __name__=='__main__':main()
