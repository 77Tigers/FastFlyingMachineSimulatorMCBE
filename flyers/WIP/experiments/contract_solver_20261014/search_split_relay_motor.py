"""Bounded split-relay search with free T0 first motor and T0/X0/G2 glue.

H2 keeps a fixed four-honey lower-relay source star; the upper glazed-root
relay moves on X0. Native verification decides every constructed candidate.
G0/X0/G2 remain supplied: a positive result is still a component.
"""
import os as _research_os
import argparse, itertools, json, subprocess, time
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer
from fastflyer import Block,Kind
from model_recovery_layout import connectivity
ROOT=Path(__file__).resolve().parents[4]
D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(p,d): return tuple(a+b for a,b in zip(p,d))
def adj(p): return [add(p,d) for d in D]
def dist(p,q): return sum(abs(a-b) for a,b in zip(p,q))
def dump(p,x): p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
 ap.add_argument('--seconds',type=float,default=100);ap.add_argument('--cp-seconds',type=float,default=.5)
 ap.add_argument('--five-glue-H2',action='store_true',help='Move H2 drive sideways; retain relay via a fifth honey cell')
 ap.add_argument('--lower-five-glue-H2',action='store_true',help='Lower the five-glue source to avoid the witnessed G0 forward obstruction')
 ap.add_argument('--start-index',type=int,default=0,help='Resume a recorded allocation boundary in an unchanged choice ordering')
 a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 original=Flyer.load(a.base/'problem.flyer');c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
 oldx={p for p,b in original._cells.items() if b.kind==Kind.HONEY and p[1]==3}
 oldg={(13,2,11),(13,2,12)}
 g0={(17,0,11),(18,0,11),(18,0,12),(18,0,13),(18,1,13),(18,2,13)}
 oldt={p for p,b in original._cells.items() if b.kind==Kind.SLIME}-g0-oldg
 removed=oldx|oldg|oldt|{(12,2,10),(14,2,11),(15,2,12)}
 base=Flyer.load(a.base/'problem.flyer')
 for p in removed:base.remove(p)
 h2={(15,1,12),(15,0,12),(15,-1,12),(15,0,13)};hm={(14,1,12),(14,-1,12),(14,0,13)}
 source=(14,0,12);gr=(13,0,12)
 if a.five_glue_H2:
  h2={(15,1,12),(15,0,12),(15,0,11),(15,-1,11),(15,0,10)}
  hm={(14,0,12),(14,-1,11),(14,0,10)};source=(14,0,11);gr=(13,0,11)
 if a.lower_five_glue_H2:
  h2={(15,1,12),(15,0,12),(15,-1,12),(15,-2,12),(15,-1,11)}
  hm={(14,0,12),(14,-2,12),(14,-1,11)};source=(14,-1,12);gr=(13,-1,12)
 for p in h2:
  assert p not in base._cells or p==(15,1,12);base.set(p,Block(Kind.HONEY))
 for p in hm:assert p not in base._cells;base.set(p,Block.piston(0))
 base.set(source,Block(Kind.REDSTONE_BLOCK));base.set((15,2,12),Block(Kind.GLAZED_TERRACOTTA))
 fixed=set(base._cells);root=(15,1,11);late=(19,2,11);xr=(14,2,12)
 choices=[]
 for m in itertools.product(range(11,18),range(-1,5),range(9,15)):
  targets={root,late,add(m,(3,0,0))}
  if any(dist(p,q)>7 for p in targets for q in targets):continue
  if m in fixed or add(m,(1,0,0)) in fixed:continue
  for di in [2,3,4,5]:
   d=D[di];o=add(m,(2-d[0],-d[1],-d[2]))
   if o not in fixed and o!=m:choices.append((m,di,o))
 choices.sort(key=lambda v:dist(v[2],gr)+dist(v[0],xr))
 domain=list(itertools.product(range(10,22),range(-2,7),range(8,16)))
 records=[];passed=None
 for index,(motor,di,obs) in enumerate(choices):
  if index<a.start_index:continue
  if time.monotonic()-start>a.seconds:break
  rec={'index':index,'motor':motor,'observer':obs,'direction':di};blocked=fixed|{motor,obs};tt={root,late,add(motor,(3,0,0))}
  model=cp_model.CpModel()
  t={p:model.NewBoolVar(f't{p}') for p in domain if p not in blocked and all(dist(p,root)+dist(p,q)+dist(root,q)<=14 for q in tt) and dist(p,(18,1,11))>1 and p!=(16,2,11) and p not in {add(motor,(1,0,0)),add(motor,(2,0,0))}}
  x={p:model.NewBoolVar(f'x{p}') for p in domain if p not in blocked and dist(p,xr)<6}
  g={p:model.NewBoolVar(f'g{p}') for p in domain if p not in blocked and dist(p,gr)<6}
  if not tt<=t.keys() or xr not in x or gr not in g:rec['status']='mandatory excluded';records.append(rec);continue
  for cells,targets,cap in [(t,tt,8),(x,{xr},6),(g,{gr},6)]:
   for p in targets:model.Add(cells[p]==1)
   model.Add(sum(cells.values())<=cap);connectivity(model,cells,min(targets),cap)
  for target in [motor,(16,2,11)]:model.Add(sum(x[p] for p in adj(target) if p in x)>=1)
  for target in hm|{obs}:model.Add(sum(g[p] for p in adj(target) if p in g)>=1)
  for p,v in x.items():
   if any(dist(p,q)<=1 for q in h2) or any(dist(p,add(obs,(k,0,0)))<=1 for k in [-2,-1,0]) or p==(16,2,11) or dist(p,(17,2,11))==1:model.Add(v==0)
   for cells in [g,t]:
    if p in cells:model.Add(v+cells[p]<=1)
  for cells,ks in [(t,[-2,-1,0,1]),(g,[-2,-1,0])]:
   for p,v in cells.items():
    if any(dist(add(p,(k,0,0)),q)<=1 for k in ks for q in g0):model.Add(v==0)
  for p,v in g.items():
   for k in [-1,0,1]:
    for q in [add(p,(k,0,0)),*adj(add(p,(k,0,0)))]:
     if q in t:model.Add(v+t[q]<=1)
  model.Minimize(sum(t.values())+sum(x.values())+sum(g.values()))
  solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=min(a.cp_seconds,max(.01,a.seconds-(time.monotonic()-start)));solver.parameters.num_search_workers=2
  result=solver.Solve(model);rec.update(status=solver.StatusName(result),seconds=solver.WallTime())
  if result in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
   case=a.out/f'case{index:03}';case.mkdir();ff=Flyer.load(a.base/'problem.flyer')
   for p in removed:ff.remove(p)
   for p,b in base._cells.items():ff.set(p,b)
   shapes={name:sorted(p for p,v in cells.items() if solver.Value(v)) for name,cells in [('T0',t),('X0',x),('G2',g)]}
   for name,shape in shapes.items():
    for p in shape:ff.set(p,Block(Kind.HONEY if name=='X0' else Kind.SLIME))
   ff.set(motor,Block.piston(0));ff.set(obs,Block.observer(di,powered=False))
   # Canonicalize cells AND piston-arm ownership; propagate the actual shift.
   shifted=ff.canonicalize()
   delta=tuple(min(p[i] for p in shifted._cells)-min(p[i] for p in ff._cells) for i in range(3))
   shifted.save(case/'problem.flyer');reloaded=Flyer.load(case/'problem.flyer')
   assert reloaded._cells==shifted._cells and reloaded._piston_blocks==shifted._piston_blocks
   cc=json.loads(json.dumps(c));cc['name']=case.name
   for port in cc['ports']:
    if port['name']=='X0':port['at']=list(xr)
    if port['name']=='G2':port['at']=list(gr)
    if port['name']=='H2':port['provenance']=['internal']*3+[None,None]
    port['at']=[v+delta[i] for i,v in enumerate(port['at'])]
   cc['boundary_envelope']={'min':[10,0,8],'max':[30,10,17]};rows=[]
   for port in cc['ports']:
    for cy in range(3):
     for slot,v in enumerate(port['provenance']):
      if v=='supplied':rows.append((cy*10+slot*2,port['at'][0]+cy*3+port['word'][:slot].count('m'),*port['at'][1:],12))
   (case/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
   for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
   rec['shapes']=shapes;dump(case/'preparation.json',rec)
   (case/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
   native_run=subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,capture_output=True)
   assert (case/'native.json').exists(),native_run.stderr
   rec['native']=json.loads((case/'native.json').read_text(encoding='utf-8'))
   (case/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
   print(json.dumps({'index':index,'native':rec['native']}),flush=True)
   if rec['native']['verified']:passed=str(case)
  records.append(rec);dump(a.out/'report.json',{'scope':__doc__,'records':records,'passed':passed,'seconds':time.monotonic()-start,'choices':len(choices)})
  if passed:break
 dump(a.out/'report.json',{'scope':__doc__,'records':records,'passed':passed,'seconds':time.monotonic()-start,'choices':len(choices)})
 (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'records':len(records),'passed':passed,'seconds':time.monotonic()-start}),flush=True)
if __name__=='__main__':main()
