"""Add T1 pushes1/2 while retaining its verified observer pull3.

Regenerate T1<=6 and T0<=8 glue, with a transverse two-normal column.
Mixed recovery spends the complete ledger's X1<=6-glue reserve; otherwise
both normals use T0. Optional X1 extension is solved in the same model,
retaining its four-cell core. Native acceptance is component-only.
"""
import argparse,itertools,json,subprocess,time
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer
from fastflyer import Block,Kind
from model_recovery_layout import connectivity
from search_T1_pull_routes import offsets
ROOT=Path(__file__).resolve().parents[4]
D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(p,d):return tuple(a+b for a,b in zip(p,d))
def adj(p):return [add(p,d) for d in D]
def dist(p,q):return sum(abs(a-b) for a,b in zip(p,q))
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def connectivity_roots(model,cells,roots,cap):
 # One selected root injects one flow unit per selected glue cell.
 picks={p:model.NewBoolVar('root'+str(p)) for p in roots if p in cells};model.Add(sum(picks.values())==1)
 injections={};flows={}
 for p,v in picks.items():
  model.Add(v<=cells[p]);injections[p]=model.NewIntVar(0,cap,'inject'+str(p));model.Add(injections[p]<=cap*v)
 for p,v in cells.items():
  for q in adj(p):
   if q in cells:
    flow=model.NewIntVar(0,cap,'xf'+str((p,q)));model.Add(flow<=cap*v);model.Add(flow<=cap*cells[q]);flows[p,q]=flow
 for p,v in cells.items():model.Add(sum(flows[p,q] for q in adj(p) if (p,q) in flows)-sum(flows[q,p] for q in adj(p) if (q,p) in flows)==injections.get(p,0)-v)
 model.Add(sum(injections.values())==sum(cells.values()));return picks
def witnessed_sticky_pickup(p):
 # Search heuristic restricted to the new low-row contacts implicated by
 # the near-T0 native failure. Do not forbid accepted pull/delivery cells
 # by taking every transient relative offset as an adhesion event.
 return p in {(17,3,10),(18,3,10)}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--seconds',type=float,default=100);ap.add_argument('--no-pickup-control',action='store_true');ap.add_argument('--mixed-recovery',action='store_true',help='One normal recovered by X1, the other by T0; either firing identity permitted.');ap.add_argument('--extend-X1',action='store_true',help='Jointly solve connected X1<=6, retaining the original four glue cells.');ap.add_argument('--free-X1',action='store_true',help='Replace X1 core while retaining all three G0 normal pickups.');ap.add_argument('--geometry-only',action='store_true');ap.add_argument('--T0-glue',type=int,default=8);ap.add_argument('--T1-glue',type=int,default=6);ap.add_argument('--X1-glue',type=int,default=6);a=ap.parse_args();a.extend_X1=a.extend_X1 or a.free_X1;assert not(a.mixed_recovery and a.no_pickup_control);assert not a.extend_X1 or a.mixed_recovery;assert a.geometry_only or (a.T0_glue,a.T1_glue,a.X1_glue)==(8,6,6),'relaxed masses are geometry controls only';a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 f=Flyer.load(a.base/'problem.flyer');c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'));pull=tuple(next(p['at'] for p in c['ports'] if p['name']=='T1_front'));tr=(15,3,11)
 from assemble import body_of
 oldt=body_of(f._cells,tr);assert len(oldt)==8
 # Both accepted upper-relay interfaces have an explicitly owned initial
 # late +X head. Derive its required target rather than retaining stale Z11.
 late_heads=[tuple(q) for owner,qs in f._piston_blocks.items() for q in qs if tuple(owner) in {(17,4,11),(17,4,9)} and tuple(q)==add(tuple(owner),(1,0,0))]
 assert len(late_heads)==1,late_heads
 tl=add(late_heads[0],(1,0,0));assert tl in oldt
 removed=oldt|{pull};fixed=set(f._cells)-removed
 assert not any(witnessed_sticky_pickup(p) for p in oldt),'pruning excludes known-good T0 geometry'
 # Glue components and words independently recovered from accepted ports.
 x1=body_of(f._cells,tuple(next(p['at'] for p in c['ports'] if p['name']=='X1_front')))
 if a.extend_X1:assert len(x1)==4,'joint extension requires the four-cell accepted core'
 g0_motors={(16,4,11),(16,4,13),(16,5,12)} if tl==(19,4,9) else {(16,5,11),(16,5,13),(16,6,12)}
 if a.free_X1:
  assert all(f._cells[p].kind==Kind.PISTON for p in g0_motors)
  removed|=x1;fixed-=x1
 bodies=[]
 for port in c['ports']:
  if port['name'] in ['T0','T1_front'] or (a.extend_X1 and port['name']=='X1_front'):continue
  shape=body_of(f._cells,tuple(port['at']));bodies.append((shape,f._cells[tuple(port['at'])].kind,port['word']))
 choices=[]
 for center in itertools.product(range(12 if tl==(19,4,9) else 16,21),range(1,8),range(9,17)):
  rb=add(center,(-1,0,0))
  if rb in fixed or rb==pull or any(dist(rb,p)<=1 for p in [(17,3,11),add(tl,(-2,0,0)),(17,3,12),(17,4,10) if tl==(19,4,9) else (17,4,12),add(pull,(2,0,0))]):continue
  for ds in itertools.combinations(D[2:],2):
   targets={center,pull,*[add(center,d) for d in ds]};motors={add(add(center,d),(-2,0,0)) for d in ds}
   if targets&fixed or motors&fixed or rb in targets or len(targets|motors|{rb})!=len(targets)+3:continue
   # Existing redstone may not fire a new normal on the opening stroke.
   sources={p for p,b in f._cells.items() if b.kind==Kind.REDSTONE_BLOCK}
   if any(dist(m,p)==1 and p!=add(m,(1,0,0)) for m in motors for p in sources):continue
   if any(dist(p,q)>a.T1_glue-1 for p in targets for q in targets):continue
   if any(add(m,(1,0,0)) in targets for m in motors):continue
   if a.mixed_recovery and not a.free_X1 and not any(min(dist(m,q) for q in x1)<=(a.X1_glue-len(x1)+1 if a.extend_X1 else 1) for m in motors):continue
   choices.append((center,rb,targets,motors))
 choices.sort(key=lambda v:sum(min(dist(m,p) for p in oldt) for m in v[3]));records=[];tests=0;passed=None;domain=list(itertools.product(range(12,23),range(0,9),range(8,18)))
 for index,(center,rb,targets,motors) in enumerate(choices):
  for kind in [Kind.SLIME,Kind.HONEY]:
   if time.monotonic()-start>a.seconds:break
   rec={'index':index,'center':center,'RB':rb,'motors':sorted(motors),'kind':kind.name,'mixed_recovery':a.mixed_recovery,'extend_X1':a.extend_X1,'free_X1':a.free_X1,'glue_caps':{'T0':a.T0_glue,'T1':a.T1_glue,'X1':a.X1_glue},'geometry_only':a.geometry_only};blocked=fixed|motors|{rb};model=cp_model.CpModel()
   t={p:model.NewBoolVar('t'+str(p)) for p in domain if p not in blocked and p!=(16,4,11) and dist(p,tr)+dist(p,tl)+dist(tr,tl)<=2*(a.T0_glue-1)}
   g={p:model.NewBoolVar('g'+str(p)) for p in domain if p not in blocked and all(dist(p,pull)+dist(p,q)+dist(pull,q)<=2*(a.T1_glue-1) for q in targets) and p not in {add(m,(1,0,0)) for m in motors}}
   x={p:model.NewBoolVar('x'+str(p)) for p in domain if p not in blocked and all(dist(p,q)<=a.X1_glue for q in g0_motors) and min(dist(p,m) for m in motors)<=a.X1_glue} if a.free_X1 else ({p:model.NewBoolVar('x'+str(p)) for p in domain if (p in x1 or p not in blocked) and min(dist(p,q) for q in x1)<=a.X1_glue-len(x1)} if a.extend_X1 else {})
   if not targets<=g.keys() or not {tr,tl}<=t.keys():rec['status']='mandatory excluded';records.append(rec);continue
   for cells,ts,root,cap in [(t,{tr,tl},tr,a.T0_glue),(g,targets,pull,a.T1_glue)]:
    for p in ts:model.Add(cells[p]==1)
    model.Add(sum(cells.values())<=cap);connectivity(model,cells,root,cap)
   root_picks={}
   if x:
    model.Add(sum(x.values())<=a.X1_glue)
    if a.free_X1:
     for motor in g0_motors:model.Add(sum(x[p] for p in adj(motor) if p in x)>=1)
     root_picks=connectivity_roots(model,x,adj(min(g0_motors)),a.X1_glue)
    else:
     assert x1<=x.keys()
     for p in x1:model.Add(x[p]==1)
     connectivity(model,x,min(x1),a.X1_glue)
   elif a.free_X1:model.Add(False)
   if not a.no_pickup_control:
    if a.mixed_recovery:
     assignments=[]
     for motor in sorted(motors):
      if not a.extend_X1 and not set(adj(motor))&x1:continue
      other=next(m for m in motors if m!=motor)
      if not a.extend_X1 and set(adj(other))&x1:continue
      pick=model.NewBoolVar('X1_motor'+str(motor));assignments.append(pick)
      if x:
       model.Add(sum(x[p] for p in adj(motor) if p in x)>=1).OnlyEnforceIf(pick)
       model.Add(sum(x[p] for p in adj(other) if p in x)==0).OnlyEnforceIf(pick)
      model.Add(sum(t[p] for p in adj(other) if p in t)>=1).OnlyEnforceIf(pick)
      model.Add(sum(t[p] for p in adj(motor) if p in t)==0).OnlyEnforceIf(pick)
     model.Add(sum(assignments)==1)
    else:
     for motor in motors:model.Add(sum(t[p] for p in adj(motor) if p in t)>=1)
   for cells,mat,word in [(t,Kind.SLIME,'mwwmm'),(g,kind,'wmmmw'),(x,Kind.SLIME,'mwwmm')]:
    for p,v in cells.items():
     if any(mat==other and any(dist(add(p,(k,0,0)),q)<=1 for k in offsets(word,w) for q in shape) for shape,other,w in bodies):model.Add(v==0)
   for q,v in x.items():
    for p,u in t.items():
     if any(dist(add(q,(k,0,0)),p)<=1 for k in offsets('mwwmm','mwwmm')):model.Add(v+u<=1)
    for p,u in g.items():
     if p==q or p==add(q,(1,0,0)) or (kind==Kind.SLIME and any(dist(add(p,(k,0,0)),q)<=1 for k in offsets('wmmmw','mwwmm'))):model.Add(v+u<=1)
   for q,v in t.items():
    if witnessed_sticky_pickup(q):model.Add(v==0)
    # This observer belongs to G0; T0 must not acquire it along a reroute.
    if any(b.kind==Kind.OBSERVER and dist(q,p)==1 for p,b in f._cells.items() if p==(18,6,11)):model.Add(v==0)
    for p,u in g.items():
     if p==q or p==add(q,(1,0,0)) or (kind==Kind.SLIME and any(dist(add(p,(k,0,0)),q)<=1 for k in offsets('wmmmw','mwwmm'))):model.Add(v+u<=1)
   model.Minimize(sum(t.values())+sum(g.values())+sum(x.values()));s=cp_model.CpSolver();s.parameters.max_time_in_seconds=.3;s.parameters.num_search_workers=2;status=s.Solve(model);rec.update(status=s.StatusName(status),seconds=s.WallTime())
   if status in [cp_model.OPTIMAL,cp_model.FEASIBLE] and root_picks:rec['X1_anchor']=next(p for p,v in root_picks.items() if s.Value(v))
   if status in [cp_model.OPTIMAL,cp_model.FEASIBLE] and (a.no_pickup_control or a.geometry_only):
    rec['shapes']={name:sorted(p for p,v in cells.items() if s.Value(v)) for name,cells in [('T0',t),('T1',g)]+([('X1',x)] if x else [])};rec['scope']='Pickup contacts omitted; necessary geometry only, not a flyer.' if a.no_pickup_control else 'Joint pickup geometry control; relaxed mass caps if requested. No flyer or physics acceptance.'
    records.append(rec);dump(a.out/'report.json',{'scope':rec['scope'],'records':records,'passed':None,'tests':0,'geometry_witness':rec,'choices':len(choices),'seconds':time.monotonic()-start});(a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(rec));return
   if status in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
    case=a.out/f'case{tests:03}';case.mkdir();tests+=1;ff=Flyer.load(a.base/'problem.flyer')
    for p in removed:ff.remove(p)
    if x and not a.free_X1:
     for p in x1:ff.remove(p)
    shapes={name:sorted(p for p,v in cells.items() if s.Value(v)) for name,cells in [('T0',t),('T1',g)]+([('X1',x)] if x else [])}
    for name,shape in shapes.items():
     for p in shape:assert p not in ff._cells;ff.set(p,Block(Kind.SLIME if name in ['T0','X1'] else kind))
    for p in motors:assert p not in ff._cells;ff.set(p,Block.piston(0))
    assert rb not in ff._cells;ff.set(rb,Block(Kind.REDSTONE_BLOCK));out=ff.canonicalize();delta=tuple(min(p[i] for p in out._cells)-min(p[i] for p in ff._cells) for i in range(3));out.save(case/'problem.flyer');loaded=Flyer.load(case/'problem.flyer');assert loaded._cells==out._cells and loaded._piston_blocks==out._piston_blocks
    cc=json.loads(json.dumps(c));next(p for p in cc['ports'] if p['name']=='T1_front')['provenance']=[None,'internal','internal','internal',None]
    if a.free_X1:next(p for p in cc['ports'] if p['name']=='X1_front')['at']=list(rec['X1_anchor'])
    for p in cc['ports']:p['at']=list(add(tuple(p['at']),delta))
    cc['name']=case.name;cc['boundary_envelope']={'min':[10,0,7],'max':[35,14,22]};rows=[]
    for p in cc['ports']:
     for cy in range(3):
      for slot,v in enumerate(p['provenance']):
       if v=='supplied':rows.append((10*cy+2*slot,p['at'][0]+3*cy+p['word'][:slot].count('m'),*p['at'][1:],12))
    (case/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
    for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
    rec['shapes']=shapes;dump(case/'preparation.json',rec);(case/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,capture_output=True);rec['native']=json.loads((case/'native.json').read_text(encoding='utf-8'));print(json.dumps({'index':index,'native':rec['native']}),flush=True)
    if rec['native']['verified']:passed=str(case)
   records.append(rec);dump(a.out/'report.json',{'scope':__doc__,'records':records,'passed':passed,'tests':tests,'choices':len(choices),'seconds':time.monotonic()-start})
   if passed:break
  if passed or time.monotonic()-start>a.seconds:break
 dump(a.out/'report.json',{'scope':__doc__,'records':records,'passed':passed,'tests':tests,'choices':len(choices),'seconds':time.monotonic()-start});(a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'records':len(records),'tests':tests,'passed':passed,'seconds':time.monotonic()-start}),flush=True)
if __name__=='__main__':main()
