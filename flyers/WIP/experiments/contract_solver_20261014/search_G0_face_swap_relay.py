"""Swap G0's upper transverse drive to the lower face and relocate the T0 upper relay.

Complete39 T1_both_on_X1_budget unchanged: T0<=9, X0<=6,
G0<=6 plus RB/two observers, X1<=6. All G0 motor recoveries remain
on X1. New T1/H0/G1 sources and full natural closure remain unbuilt.
Native tests decide source timing, switch-off, recovery and loads.
"""
import os as _research_os
import argparse,itertools,json,subprocess,time
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer,body_of
from fastflyer import Block,Kind
from model_recovery_layout import connectivity
from phase_glue_bound import phase_witness
from search_T1_two_pushes import D,add,adj,dist,dump,connectivity_roots,witnessed_sticky_pickup
from search_T1_pull_routes import offsets
ROOT=Path(__file__).resolve().parents[4]

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--glue-relay-root',action='store_true');ap.add_argument('--G0-center',type=int,nargs=3,default=[18,5,12]);ap.add_argument('--missing-face',type=int,choices=[2,3,4,5],default=2);ap.add_argument('--seconds',type=float,default=100);ap.add_argument('--cp-seconds',type=float,default=.4);ap.add_argument('--only-unknown-from',type=Path);ap.add_argument('--only-indices',type=int,nargs='+');ap.add_argument('--G0-glue',type=int,default=6);ap.add_argument('--root-pulse-plan',action='store_true',help='Historical rejected root-pulse hypothesis; component-only seventh-glue control.');ap.add_argument('--H0-gate-plan',action='store_true',help='One G0 normal recovered by T0, two by X1; reserves X1 stone and H0 observer in transformed full budget.');ap.add_argument('--G0-motor-on-T0',type=int,nargs=3);a=ap.parse_args();assert a.G0_glue==6 and not a.root_pulse_plan and not a.H0_gate_plan and not a.G0_motor_on_T0;a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pending=None
 if a.only_unknown_from:pending={r['index']:r for r in json.loads(a.only_unknown_from.read_text(encoding='utf-8'))['records'] if r['status']=='UNKNOWN'}
 f=Flyer.load(a.base/'problem.flyer');c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'));ports={p['name']:p for p in c['ports']};freed=['T0','X0','G0','X1_front'];removed=set().union(*(body_of(f._cells,tuple(ports[n]['at'])) for n in freed))|{(17,5,12),(16,5,11),(16,5,13),(16,6,12),(17,4,11),(18,4,11),(15,4,12),(16,4,12),(17,4,12),(17,4,13)};fixed=set(f._cells)-removed
 center=tuple(a.G0_center);rb=add(center,(-1,0,0));star={center,*[add(center,d) for j,d in enumerate(D) if j>=2 and j!=a.missing_face]};gm={add(q,(-2,0,0)) for q in star-{center}};assert not (star|gm|{rb})&fixed;tr=(15,3,11);lower=(17,3,13);choices=[]
 for y,z in itertools.product(range(1,8),range(9,15)):
  late=(17,y,z);head=add(late,(1,0,0));target=add(late,(2,0,0))
  for side in D[2:]:
   output=add(late,side);chain=[add(output,(-2,0,0)),add(output,(-1,0,0)),output];pusher=chain[0] if a.glue_relay_root else add(output,(-3,0,0));relay=chain[1:] if a.glue_relay_root else chain
   for di,d in enumerate(D):
    obs=add(output,tuple(-v for v in d));actors=[late,head,*relay,obs,rb,*gm];required=set(actors)|star|{tr,target,pusher}
    if len(set(actors))!=len(actors) or required&fixed or set(actors)&(star|{tr,target,pusher}) or dist(tr,target)>8:continue
    if any(add(m,(1,0,0)) in {obs,lower} for m in gm):continue
    choices.append((late,head,target,chain,pusher,obs,di))
 choices.sort(key=lambda v:(dist(tr,v[2]),min(dist(v[5],p) for p in star),v[0],v[5],v[6]));domain=list(itertools.product(range(11,23),range(0,9),range(8,17)));records=[];passed=None;tests=0
 others=[(body_of(f._cells,tuple(p['at'])),f._cells[tuple(p['at'])].kind,p['word']) for p in c['ports'] if p['name'] not in freed]
 for i,(late,head,target,chain,pusher,obs,di) in enumerate(choices):
  if pending is not None and i not in pending:continue
  if a.only_indices is not None and i not in a.only_indices:continue
  if time.monotonic()-start>a.seconds:break
  rec={'index':i,'late':late,'target':target,'chain':chain,'observer':obs,'direction':di,'G0_glue_cap':a.G0_glue,'G0_center':center,'G0_missing_face':a.missing_face,'glue_relay_root':a.glue_relay_root,'root_pulse_plan':a.root_pulse_plan,'H0_gate_plan':a.H0_gate_plan};blocked=fixed|{late,head,*(chain[1:] if a.glue_relay_root else chain),obs,rb,*gm};m=cp_model.CpModel();shapes={}
  if pending is not None:
   for key in ['late','target','chain','observer','direction']:assert json.loads(json.dumps(rec[key]))==pending[i][key],(i,key)
  if obs==add(chain[-1],(1,0,0)):
   rec['status']='witnessed opening relay/observer conflict';records.append(rec);continue
  specs=[('T0',Kind.SLIME,'mwwmm',9,{tr,target},tr),('X0',Kind.HONEY,'mmmww',7 if a.glue_relay_root else 6,{pusher},pusher),('G0',Kind.HONEY,'wmmmw',a.G0_glue,star,center),('X1_front',Kind.SLIME,'mwwmm',6,set(),None)]
  for name,mat,word,cap,pins,root in specs:
   eligible=[p for p in domain if p not in blocked and (all(dist(p,q)<=cap-1 for q in pins) if pins else all(dist(p,q)<=cap for q in gm))]
   shapes[name]={p:m.NewBoolVar(name+str(p)) for p in eligible}
  if any(not pins<=shapes[n].keys() for n,_,_,_,pins,_ in specs):rec['status']='mandatory excluded';records.append(rec);continue
  allowed={name:set(cells) for name,cells in shapes.items()}
  for name,mat,word,cap,pins,root in specs:
   cells=shapes[name];m.Add(sum(cells.values())<=cap)
   for p in pins:m.Add(cells[p]==1)
   if root is not None:connectivity(m,cells,root,cap)
   for p,v in cells.items():
    if any(mat==other and any(dist(add(p,(k,0,0)),q)<=1 for k in offsets(word,w) for q in sh) for sh,other,w in others):m.Add(v==0);allowed[name].discard(p)
   if word[0]=='m':
    # G0 waits0: its RB and pulse observers must not be pushed by another body.
    for obstacle in [rb,lower,obs]:
     q=add(obstacle,(-1,0,0))
     if q in cells:m.Add(cells[q]==0);allowed[name].discard(q)
  # A split pickup may assign the first motor to T0. X1's anchor must then
  # be free to lie beside either of its own motors, not the transferred one.
  root_domain=set().union(*(set(adj(p)) for p in gm))
  roots=connectivity_roots(m,shapes['X1_front'],root_domain,6)
  # X0 pushes the complete relay on move0; its output must not push G0's
  # waiting glue. This obstruction is separate from glue/body separation.
  output_delivery=add(chain[-1],(1,0,0))
  if output_delivery in shapes['G0']:m.Add(shapes['G0'][output_delivery]==0);allowed['G0'].discard(output_delivery)
  pickup_picks={}
  if a.H0_gate_plan:
   for motor in sorted(gm):
    v=m.NewBoolVar('T0_pickup'+str(motor));pickup_picks[motor]=v
    t=sum(shapes['T0'][p] for p in adj(motor) if p in shapes['T0']);x=sum(shapes['X1_front'][p] for p in adj(motor) if p in shapes['X1_front'])
    m.Add(t>=1).OnlyEnforceIf(v);m.Add(x==0).OnlyEnforceIf(v);m.Add(x>=1).OnlyEnforceIf(v.Not());m.Add(t==0).OnlyEnforceIf(v.Not())
    # A parallel-column motor may fire third under another RNG/order. Before
    # its slot3 extension it has advanced three cells and is still movable.
    # T0 has advanced only one: prevent the witnessed pre-extension pickup
    # that pushes the motor forward into the waiting G0 body.
    before_third=add(motor,(2,0,0))
    for p,u in shapes['T0'].items():
     if dist(p,before_third)<=1:m.Add(u==0).OnlyEnforceIf(v)
   m.Add(sum(pickup_picks.values())==1)
   if a.G0_motor_on_T0:m.Add(pickup_picks[tuple(a.G0_motor_on_T0)]==1)
  else:
   for motor in gm:m.Add(sum(shapes['X1_front'][p] for p in adj(motor) if p in shapes['X1_front'])>=1)
  for q in [lower,obs]:m.Add(sum(shapes['G0'][p] for p in adj(q) if p in shapes['G0'])>=1)
  for q in [(12,3,11),add(late,(-1,0,0))]:m.Add(sum(shapes['X0'][p] for p in adj(q) if p in shapes['X0'])>=1)
  if add(late,(-1,0,0)) in shapes['X0']:m.Add(shapes['X0'][add(late,(-1,0,0))]==0);allowed['X0'].discard(add(late,(-1,0,0)))
  for p,v in shapes['T0'].items():
   if witnessed_sticky_pickup(p):m.Add(v==0);allowed['T0'].discard(p)
  bounds={}
  for name,mat,word,cap,pins,_ in specs:
   groups=[{q} for q in pins]
   if name=='X1_front':groups += [set(adj(q)) for q in gm]
   if name=='G0':groups += [set(adj(q)) for q in [lower,obs]]
   if name=='X0':groups += [set(adj(q)) for q in [(12,3,11),add(late,(-1,0,0))]]
   v=phase_witness(allowed[name],groups,cap,word,mat,[(bn,bpins,bmat,bword) for bn,bmat,bword,_,bpins,_ in specs if bn!=name and bpins])
   if not v['cap_feasible']:bounds[name]={k:v[k] for k in ['minimum','cap','cap_feasible']}|{'empty_groups':[g['cells'] for g in v['contact_groups'] if not g['allowed']]}
  if bounds:
   rec.update(status='NECESSARY_GLUE_BOUND',bounds=bounds);records.append(rec);continue
  for ai,(an,ak,aw,*_) in enumerate(specs):
   for bn,bk,bw,*_ in specs[ai+1:]:
    aa,bb=shapes[an],shapes[bn]
    for p,v in aa.items():
     bad=set()
     for k in offsets(aw,bw):
      q=add(p,(k,0,0));bad.add(q)
      if ak==bk:bad.update(adj(q))
     for q in bad:
      if q in bb:m.Add(v+bb[q]<=1)
  m.Minimize(sum(v for sh in shapes.values() for v in sh.values()));s=cp_model.CpSolver();s.parameters.max_time_in_seconds=min(a.cp_seconds,max(.01,a.seconds-(time.monotonic()-start)));s.parameters.num_search_workers=2;status=s.Solve(m);rec.update(status=s.StatusName(status),seconds=s.WallTime())
  if status in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
   tests+=1;case=a.out/f'case{i:03}';case.mkdir();ff=Flyer.load(a.base/'problem.flyer')
   for p in removed:ff.remove(p)
   selected={n:sorted(p for p,v in sh.items() if s.Value(v)) for n,sh in shapes.items()}
   if pickup_picks:rec['G0_motor_on_T0']=next(p for p,v in pickup_picks.items() if s.Value(v))
   added={p:Block(mat) for n,mat,*_ in specs for p in selected[n]};hardware={rb:Block(Kind.REDSTONE_BLOCK),**{p:Block.piston(0) for p in gm},late:f._cells[(17,4,11)],head:f._cells[(18,4,11)],**({} if a.glue_relay_root else {chain[0]:Block(Kind.GLAZED_TERRACOTTA)}),chain[1]:Block.observer(3,powered=False),chain[2]:Block(Kind.GLAZED_TERRACOTTA),obs:Block.observer(di,powered=False)}
   assert not set(added)&hardware.keys() and not (set(added)|hardware.keys())&ff._cells.keys()
   for p,b in {**added,**hardware}.items():ff.set(p,b)
   ff.set_piston_blocks(late,[head]);out=ff.canonicalize();delta=tuple(min(p[j] for p in out._cells)-min(p[j] for p in ff._cells) for j in range(3));out.save(case/'problem.flyer');loaded=Flyer.load(case/'problem.flyer');assert loaded._cells==out._cells and loaded._piston_blocks==out._piston_blocks
   cc=json.loads(json.dumps(c));anchors={'G0':center,'X0':pusher,'X1_front':next(p for p,v in roots.items() if s.Value(v))};rows=[]
   for p in cc['ports']:
    p['at']=list(add(anchors.get(p['name'],tuple(p['at'])),delta))
    for cy in range(3):
     for slot,v in enumerate(p['provenance']):
      if v=='supplied':rows.append((10*cy+2*slot,p['at'][0]+3*cy+p['word'][:slot].count('m'),*p['at'][1:],12))
   (case/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
   for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
   rec['shapes']=selected;dump(case/'preparation.json',rec);(case/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,capture_output=True);rec['native']=json.loads((case/'native.json').read_text(encoding='utf-8'));print(json.dumps({'index':i,'native':rec['native']}),flush=True)
   if rec['native']['verified']:passed=str(case)
  records.append(rec);dump(a.out/'report.json',{'scope':__doc__,'records':records,'choices':len(choices),'passed':passed,'tests':tests,'budget_reference':'G0_face_swap_preflight/glue_root_budget.json' if a.glue_relay_root else 'T1_both_on_X1_budget','seconds':time.monotonic()-start})
  if passed:break
 dump(a.out/'report.json',{'scope':__doc__,'records':records,'choices':len(choices),'passed':passed,'tests':tests,'budget_reference':'G0_face_swap_preflight/glue_root_budget.json' if a.glue_relay_root else 'T1_both_on_X1_budget','seconds':time.monotonic()-start});(a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'models':len(records),'passed':passed,'seconds':time.monotonic()-start}),flush=True)
if __name__=='__main__':main()
