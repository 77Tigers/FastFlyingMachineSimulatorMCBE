"""Joint source-first T1 push/pull/H0 power gate, fixed accepted59 rear.

Full budget: T0<=8,X1<=6,T1<=7/noRB, local H0<=2/two observers;
H0 retains four future own-source glue+RB (permanent9 total). Whole39
allocation unchanged by default. --split-source-carrier transfers the source
observer to G1 (H0/G1 permanent8/8) and H1 push4 recovery to H0;
see T1_split_source_budget. --front-stone-gate uses G0 gate observer,
G1 stone, H0/G1/X1 masses7/9/7 (T1_front_stone_budget).
--T1-on-X1 gives T0 nine glue and both T1 normal recoveries to X1;
see T1_both_on_X1_budget. --same-front-material explores H0/G1
same glue kind (default opposite); phase collision/adhesion checks remain.
--G0-on-T0 trades the first one/two G0 normal recoveries to T0,
for matching future X2 recovery on X1 (G0_T0_recovery_trade_budget).
--T1-self-RB replaces the external G1 observer with a T1-carried RB
and six glue, keeping full39 T1 mass7 and reducing G1 mass to8.
H0/X0/X1/G2/X2/G1 drives remain supplied.
"""
import os as _research_os
import argparse,copy,itertools,json,time,subprocess,collections,hashlib
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer,body_of
from fastflyer import Block,Kind
from search_T1_two_pushes import D,add,adj,dist,connectivity_roots,dump,witnessed_sticky_pickup
from search_T1_pull_routes import offsets
from model_recovery_layout import connectivity
from steiner_glue_bound import connected_glue_minimum
from phase_glue_bound import phase_witness
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]

def components(cells):
 unseen=set(cells);answer=[]
 while unseen:
  todo=[unseen.pop()];cc=set(todo)
  while todo:
   for q in adj(todo.pop()):
    if q in unseen:unseen.remove(q);cc.add(q);todo.append(q)
  answer.append(cc)
 return answer

def gate_actors(h,u,general=False):
 sticky=add(h,u)
 if not general:
  for d in D[2:]:
   if sum(x*y for x,y in zip(u,d)):continue
   yield D.index(u),add(h,tuple(-x for x in d)),sticky,add(add(sticky,(1,0,0)),tuple(-x for x in d))
 else:
  # At slot2 H0 has moved twice and X1 once. A powered stone at
  # A+X+d starts adjacent to the sticky's side/back after those moves.
  # The observer may use a different output face and the second H0 glue.
  legacy=set(gate_actors(h,u,False))
  for d in [D[0],*D[2:]]:
   P=add(add(sticky,(1,0,0)),d)
   for gdi,v in enumerate(D):
    obs=add(add(P,(-1,0,0)),tuple(-x for x in v))
    if obs==sticky or obs==h or dist(obs,h)>2:continue
    actor=(gdi,obs,sticky,P)
    if actor not in legacy:yield actor

def front_stone_gate_actors(h,u,g0):
 A=add(h,u)
 for d in [D[0],*D[2:]]:
  P=add(A,d)
  for di,v in enumerate(D):
   obs=add(add(P,(1,0,0)),tuple(-x for x in v))
   if obs in [A,h,P] or not any(dist(obs,q)==1 for q in g0):continue
   yield di,obs,A,P

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--seconds',type=float,default=360);ap.add_argument('--max-models',type=int,default=3000);ap.add_argument('--cp-seconds',type=float,default=.6);ap.add_argument('--mixed-recovery',action='store_true');ap.add_argument('--resume-from',type=Path);ap.add_argument('--only-indices',nargs='+',type=int);ap.add_argument('--omit-motor-recovery-control',action='store_true');ap.add_argument('--diagnostic-cores',action='store_true');ap.add_argument('--minimize-cores',action='store_true');ap.add_argument('--general-gate',action='store_true');ap.add_argument('--split-source-carrier',action='store_true');ap.add_argument('--front-stone-gate',action='store_true');ap.add_argument('--T1-on-X1',action='store_true');ap.add_argument('--same-front-material',action='store_true');ap.add_argument('--source-only-G1-control',action='store_true');ap.add_argument('--T1-self-RB',action='store_true');ap.add_argument('--G0-on-T0',type=int,choices=[0,1,2],default=0);a=ap.parse_args();assert not a.T1_self_RB or (a.T1_on_X1 and not a.G0_on_T0 and not a.source_only_G1_control);assert not a.G0_on_T0 or a.T1_on_X1;assert not(a.resume_from and a.only_indices);assert not a.minimize_cores or a.diagnostic_cores;assert not a.front_stone_gate or (a.split_source_carrier and not a.general_gate);assert not a.T1_on_X1 or a.front_stone_gate;assert not a.same_front_material or a.split_source_carrier;assert not a.source_only_G1_control or a.front_stone_gate;a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 f=Flyer.load(a.base/'problem.flyer');c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'));ports={p['name']:p for p in c['ports']};tr=tuple(ports['T0']['at'])
 t0_existing=body_of(f._cells,tr);late_heads=[tuple(q) for owner,qs in f._piston_blocks.items() for q in qs if tuple(owner) in f._cells and f._cells[tuple(owner)].kind==Kind.PISTON and f._cells[tuple(owner)].direction==0 and tuple(q)==add(tuple(owner),(1,0,0)) and add(tuple(q),(1,0,0)) in t0_existing];assert len(late_heads)==1,late_heads;tl=add(late_heads[0],(1,0,0));assert tl in t0_existing
 g0=body_of(f._cells,tuple(ports['G0']['at']));gm={p for p,b in f._cells.items() if b.kind==Kind.PISTON and b.direction==0 and add(p,(2,0,0)) in g0};assert len(gm)==3
 gm_t0=set([(16,6,12),(16,5,13)][:a.G0_on_T0]);assert gm_t0<=gm;gm_x1=gm-gm_t0
 removed=body_of(f._cells,tr)|body_of(f._cells,tuple(ports['X1_front']['at']));fixed=set(f._cells)-removed
 others=[(body_of(f._cells,tuple(p['at'])),f._cells[tuple(p['at'])].kind,p['word']) for p in c['ports'] if p['name'] not in ['T0','X1_front']];g0wait=g0|{p for p,b in f._cells.items() if b.kind in [Kind.REDSTONE_BLOCK,Kind.OBSERVER] and any(dist(p,q)==1 for q in g0)}
 tcap=9 if a.T1_on_X1 else 8;t1cap=6 if a.T1_self_RB else 7
 shortest={p for p in itertools.product(range(11,24),range(0,11),range(7,19)) if dist(tr,p)+dist(p,tl)+dist(tr,tl)<=2*(tcap-1)};source_choices=[]
 for C in itertools.product(range(13,21),range(1,9),range(8,16)):
  for ds in itertools.combinations(D[2:],2):
   star={C,*[add(add(C,(1,0,0)),d) for d in ds]};ms={add(add(C,(-1,0,0)),d) for d in ds};out=add(C,(-1,0,0))
   if star&fixed or ms&fixed or star&ms or out in fixed or len(star)!=3:continue
   eligible=[bool(set(adj(m))&shortest) for m in ms]
   if a.T1_on_X1:
    if max(dist(p,q) for p in gm_x1|ms for q in gm_x1|ms)>7:continue
   elif not (any(eligible) if a.mixed_recovery else all(eligible)):continue
   source_choices.append((C,star-{C} if a.T1_self_RB else star,ms,out))
 source_choices.sort(key=lambda r:(sum(min(dist(m,p) for p in (gm_x1 if a.T1_on_X1 else shortest)) for m in r[2]),r[0],sorted(r[2])))
 domain=list(itertools.product(range(11,24),range(0,11),range(7,19)));prior=json.loads(a.resume_from.read_text(encoding='utf-8')) if a.resume_from else {};records=copy.deepcopy(prior.get('records',[]));resume_count=len(records);skips=collections.Counter();tests=prior.get('tests',0);passed=prior.get('passed');actors_seen=0;geometry_witness=None
 assert not passed,'Preserved passing candidate must be verified, not searched again'
 assert not prior or prior.get('mixed_recovery')==a.mixed_recovery
 assert not prior or prior.get('general_gate',False)==a.general_gate
 assert not prior or prior.get('split_source_carrier',False)==a.split_source_carrier
 assert not prior or prior.get('front_stone_gate',False)==a.front_stone_gate
 assert not prior or prior.get('T1_on_X1',False)==a.T1_on_X1
 assert not prior or prior.get('same_front_material',False)==a.same_front_material
 assert not prior or prior.get('source_only_G1_control',False)==a.source_only_G1_control
 assert not prior or prior.get('G0_on_T0',0)==a.G0_on_T0
 assert not prior or prior.get('T1_self_RB',False)==a.T1_self_RB
 last_saved=0
 def save(complete=False):
  nonlocal last_saved
  if not complete and time.monotonic()-last_saved<1:return
  last_saved=time.monotonic()
  elapsed=time.monotonic()-start;termination=('candidate' if passed else 'time_limit' if elapsed>=a.seconds else 'model_limit' if len(records)>=a.max_models else 'selected_domain_exhausted' if a.only_indices is not None else 'domain_exhausted') if complete else None
  dump(a.out/'report.tmp',{'scope':__doc__,'complete':complete,'termination':termination,'T0_late_target':tl,'T0_endpoint_distance':dist(tr,tl),'G0_normals':sorted(gm),'T1_self_RB':a.T1_self_RB,'G0_on_T0':a.G0_on_T0,'G0_T0_normals':sorted(gm_t0),'G0_X1_normals':sorted(gm_x1),'mixed_recovery':a.mixed_recovery,'general_gate':a.general_gate,'split_source_carrier':a.split_source_carrier,'front_stone_gate':a.front_stone_gate,'T1_on_X1':a.T1_on_X1,'T0_cap':tcap,'same_front_material':a.same_front_material,'source_only_G1_control':a.source_only_G1_control,'selected_indices':a.only_indices,'omit_motor_recovery_control':a.omit_motor_recovery_control,'geometry_witness':geometry_witness,'resumed_models':resume_count,'source_choices':len(source_choices),'actors_seen':actors_seen,'skips':dict(skips),'records':records,'tests':tests,'passed':passed,'seconds':elapsed})
  try:(a.out/'report.tmp').replace(a.out/'report.json')
  except PermissionError:
   # Windows readers may deny replacement. Preserve latest complete temp
   # snapshot and attempt the ordinary overwrite used by older runners.
   try:(a.out/'report.json').write_bytes((a.out/'report.tmp').read_bytes())
   except PermissionError:pass
 (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());dump(a.out/'input_manifest.json',{'base_sha256':hashlib.sha256((a.base/'problem.flyer').read_bytes()).hexdigest(),'budget_reference':'T1_self_RB_budget/full39.json' if a.T1_self_RB else 'G0_T0_recovery_trade_budget' if a.G0_on_T0 else 'T1_both_on_X1_budget' if a.T1_on_X1 else 'T1_front_stone_budget' if a.front_stone_gate else 'T1_split_source_budget' if a.split_source_carrier else 'joint_T1_mixed_recovery_budget' if a.mixed_recovery else 'T1_H0_glue_power/full39_power_budget.json','limits':vars(a)|{'base':str(a.base),'out':str(a.out),'resume_from':str(a.resume_from) if a.resume_from else None}})
 def layouts():
  nonlocal actors_seen
  for C,star,ms,out in source_choices:
   for sdi,v in ([(0,D[0])] if a.T1_self_RB else enumerate(D)):
    srcobs=C if a.T1_self_RB else add(out,tuple(-x for x in v))
    if srcobs in fixed|star|ms:continue
    for h in sorted((p for p in domain if (dist(p,C)<=5 if a.split_source_carrier else 1<=dist(p,srcobs)<=2)),key=lambda p:(dist(p,C),p) if a.split_source_carrier else p):
     if time.monotonic()-start>a.seconds:return
     for gdi,u in enumerate(D[2:],2):
      Q=add(add(h,(-2,0,0)),u)
      if Q in fixed|star|ms or any(dist(Q,p)>6 for p in star) or (a.split_source_carrier and dist(Q,C)>3):continue
      for gdi,gateobs,sticky,P in (front_stone_gate_actors(h,u,g0) if a.front_stone_gate else gate_actors(h,u,a.general_gate)):
       actors_seen+=1;hardware={srcobs,gateobs,sticky,P};pins=star|{Q,h}
       if len(hardware)!=4 or hardware&fixed or hardware&pins or hardware&ms or pins&ms or len(pins)!=(4 if a.T1_self_RB else 5):skips['occupied actors']+=1;continue
       if out in hardware|pins:skips['opening output occupied']+=1;continue
       if any(dist(add(P,(1,0,0)),p)<=1 or (a.front_stone_gate and dist(P,p)<=1) for p in g0):skips['stone joins G0 first']+=1;continue
       if any(add(p,(1,0,0)) in g0wait for p in ((sticky,h) if a.T1_self_RB else (srcobs,sticky,h) if a.front_stone_gate else (srcobs,gateobs,sticky,h))):skips['H0 pushes waiting G0']+=1;continue
       if any(dist(p,hw)<=1 for shape,_,_ in others for p in shape for hw in (srcobs,gateobs,sticky) if not(a.front_stone_gate and hw==gateobs and shape==g0)):skips['H0 hardware foreign pickup']+=1;continue
       for hk,tk in itertools.product([Kind.SLIME,Kind.HONEY],repeat=2):yield C,star,ms,out,srcobs,sdi,h,Q,gateobs,gdi,sticky,P,hk,tk
 hard_cache={};cap_cache={}
 model_index=-1
 for C,star,ms,out,srcobs,sdi,h,Q,gateobs,gdi,sticky,P,hk,tk in layouts():
  model_index+=1
  if a.only_indices is not None and model_index>max(a.only_indices):break
  if model_index<resume_count:
   old=records[model_index]
   for key,value in [('center',C),('normals',sorted(ms)),('source_observer',None if a.T1_self_RB else srcobs),('source_direction',None if a.T1_self_RB else sdi),('H0_root',h),('T1_root',Q),('gate_observer',gateobs),('gate_direction',gdi),('sticky',sticky),('stone',P),('H0_kind',hk.name),('T1_kind',tk.name)]:assert old[key]==json.loads(json.dumps(value)),(model_index,key)
   continue
  if a.only_indices is not None and model_index not in a.only_indices:continue
  if time.monotonic()-start>a.seconds or len(records)>=a.max_models:break
  rec={'index':model_index,'center':C,'normals':sorted(ms),'source_observer':None if a.T1_self_RB else srcobs,'source_position':srcobs,'source_direction':None if a.T1_self_RB else sdi,'source_kind':'REDSTONE_BLOCK' if a.T1_self_RB else 'OBSERVER','H0_root':h,'T1_root':Q,'gate_observer':gateobs,'gate_direction':gdi,'sticky':sticky,'stone':P,'H0_kind':hk.name,'T1_kind':tk.name,'G1_kind':(hk if a.same_front_material else Kind.HONEY if hk==Kind.SLIME else Kind.SLIME).name if a.split_source_carrier else None}
  # Six connected glue cells can touch terminals at L1 distance at most7:
  # terminal -> glue, at most5 internal edges, glue -> terminal.
  far=max(((dist(p,q),p,q) for p in (gm_x1|ms if a.T1_on_X1 else gm if a.front_stone_gate else gm|{P}) for q in (gm_x1|ms if a.T1_on_X1 else gm if a.front_stone_gate else gm|{P})),key=lambda x:x[0])
  if far[0]>7:
   rec.update(status='X1_TERMINAL_DISTANCE_BOUND',terminal_pair=[far[1],far[2]],minimum_X1_glue=far[0]-1);records.append(rec);save();continue
  hard_key=json.dumps({k:v for k,v in rec.items() if k not in ['index','H0_kind','T1_kind','G1_kind']},sort_keys=True)
  if hard_key in cap_cache:
   rec.update(status='HARD_GLUE_CAP_BOUND',glue_cap_bounds=cap_cache[hard_key],hard_graph_cached=True);records.append(rec);save();continue
  if hard_key in hard_cache:
   rec.update(status='HARD_DOMAIN_DISCONNECTED',disconnected_bodies=hard_cache[hard_key],hard_graph_cached=True);records.append(rec);save();continue
  waiting_g0=g0wait|({gateobs} if a.front_stone_gate else set())
  targets=star|{Q};blocked=fixed|ms|{srcobs,gateobs,sticky,P,out};model=cp_model.CpModel();shapes={
   'T0':{p:model.NewBoolVar('t'+str(p)) for p in shortest if p not in blocked},
   'T1':{p:model.NewBoolVar('g'+str(p)) for p in domain if p not in blocked and all(dist(p,Q)+dist(p,q)+dist(Q,q)<=2*(t1cap-1) for q in targets) and p not in {add(m,(1,0,0)) for m in ms}},
   'H0':{p:model.NewBoolVar('h'+str(p)) for p in domain if p not in blocked and dist(p,h)<=1},
   'X1':{p:model.NewBoolVar('x'+str(p)) for p in domain if p not in blocked and all(dist(p,m)<=6 for m in (gm_x1|ms if a.T1_on_X1 else gm)) and (a.front_stone_gate or dist(p,P)<=6)}}
  specs=[('T0',Kind.SLIME,'mwwmm',tcap,{tr,tl},tr),('T1',tk,'wmmmw',t1cap,targets,Q),('H0',hk,'mmwwm',2,{h},h),('X1',Kind.SLIME,'mwwmm',6,set(),None)]
  if a.split_source_carrier:
   shapes['G1']={p:model.NewBoolVar('g1'+str(p)) for p in domain if p not in blocked and (a.T1_self_RB or dist(p,srcobs)<=5) and (not a.front_stone_gate or a.source_only_G1_control or dist(p,P)<=5)}
   specs.append(('G1',hk if a.same_front_material else Kind.HONEY if hk==Kind.SLIME else Kind.SLIME,'mmwwm',5,set(),None))
  def foreign_hw(n):
   if a.T1_self_RB and n=='T1':return (gateobs,sticky)
   if a.T1_self_RB and n=='G1':return (srcobs,gateobs,sticky)
   return (gateobs,sticky) if n=='G1' else (srcobs,gateobs) if n=='H0' and a.front_stone_gate else (srcobs,) if n=='H0' and a.split_source_carrier else () if n=='H0' else (srcobs,gateobs,sticky)
  assumptions={}
  def guarded(constraint,label):
   if a.diagnostic_cores:
    if label not in assumptions:
     assumptions[label]=model.NewBoolVar('assume_'+label);model.AddAssumption(assumptions[label])
    constraint.OnlyEnforceIf(assumptions[label])
  if any(not pins<=shapes[n].keys() for n,_,_,_,pins,_ in specs):rec['status']='mandatory excluded';records.append(rec);continue
  # Necessary graph cut on the same hard domain constraints used below.
  # Ignore caps, material separation and new-motor pickup, so a rejection
  # cannot discard a candidate that the full model could connect.
  disconnected=[];cap_violations={};phase_violations={}
  for n,mat,w,cap,pins,_ in specs:
   cells={p for p in shapes[n] if not(any(dist(p,hw)<=1 for hw in foreign_hw(n))) and not((n in ['H0','G1'] or (n=='X1' and not(a.mixed_recovery or a.T1_on_X1))) and any(dist(p,m)<=1 for m in ms)) and not(w[0]=='m' and add(p,(1,0,0)) in waiting_g0) and not(n=='T0' and witnessed_sticky_pickup(p)) and not(a.G0_on_T0 and any(dist(p,m)<=1 for m in (gm_x1 if n=='T0' else gm_t0 if n=='X1' else set())))}
   cc=components(cells)
   if n in ['T0','T1']:ok=any(pins<=x for x in cc)
   elif n=='H0':ok=any(h in x and (a.split_source_carrier or bool(x&set(adj(srcobs)))) and (a.front_stone_gate or bool(x&set(adj(gateobs)))) for x in cc)
   elif n=='G1':ok=any((a.T1_self_RB or bool(x&set(adj(srcobs)))) and (not a.front_stone_gate or a.source_only_G1_control or bool(x&set(adj(P)))) for x in cc)
   else:ok=any(all(x&set(adj(m)) for m in (gm_x1|ms if a.T1_on_X1 else gm if a.front_stone_gate else gm|{P})) for x in cc)
   if not ok:disconnected.append(n)
   else:
    groups=[{p} for p in pins]
    if n=='T0':groups += [set(adj(m)) for m in gm_t0]
    if n=='X1':groups += [set(adj(m)) for m in (gm_x1|ms if a.T1_on_X1 else gm if a.front_stone_gate else gm|{P})]
    if n=='H0':groups += [set(adj(o)) for o in ([] if a.front_stone_gate else [gateobs] if a.split_source_carrier else [srcobs,gateobs])]
    if n=='T1' and a.T1_self_RB:groups += [set(adj(srcobs))]
    if n=='G1':groups += ([] if a.T1_self_RB else [set(adj(srcobs))])+([set(adj(P))] if a.front_stone_gate and not a.source_only_G1_control else [])
    minimum=connected_glue_minimum(cells,groups);cap=next(s[3] for s in specs if s[0]==n)
    if minimum is None or minimum>cap:cap_violations[n]={'minimum':minimum,'cap':cap}
    if not a.diagnostic_cores and not cap_violations:
     obstacles=[('fixed_'+str(i),os,om,ow) for i,(os,om,ow) in enumerate(others) if mat==om]+[(bn,bpins,bmat,bword) for bn,bmat,bword,_,bpins,_ in specs if bn!=n and bpins]
     witness=phase_witness(cells,groups,cap,w,mat,obstacles)
     if not witness['cap_feasible']:phase_violations[n]={k:witness[k] for k in ['minimum','cap','cap_feasible']}|{'allowed_count':len(witness['allowed_cells']),'excluded_count':len(witness['excluded_cells']),'empty_contact_groups':[g['cells'] for g in witness['contact_groups'] if not g['allowed']],'excluded_preview':witness['excluded_cells'][:8]}
  if disconnected:
   hard_cache[hard_key]=disconnected
   rec.update(status='HARD_DOMAIN_DISCONNECTED',disconnected_bodies=disconnected);records.append(rec);save();continue
  if cap_violations:
   cap_cache[hard_key]=cap_violations;rec.update(status='HARD_GLUE_CAP_BOUND',glue_cap_bounds=cap_violations);records.append(rec);save();continue
  if phase_violations:
   rec.update(status='PHASE_GLUE_CAP_BOUND',phase_bounds=phase_violations);records.append(rec);save();continue
  for n,mat,w,cap,pins,root in specs:
   cells=shapes[n];guarded(model.Add(sum(cells.values())<=cap),'cap_'+n)
   for p in pins:model.Add(cells[p]==1)
   if root is not None:connectivity(model,cells,root,cap)
   for p,var in cells.items():
    if any(mat==om and any(dist(add(p,(k,0,0)),q)<=1 for k in offsets(w,ow) for q in os) for os,om,ow in others):guarded(model.Add(var==0),'fixed_material_'+n)
    if any(dist(p,hw)<=1 for hw in foreign_hw(n)):model.Add(var==0)
    if (n in ['H0','G1'] or (n=='X1' and not(a.mixed_recovery or a.T1_on_X1))) and any(dist(p,m)<=1 for m in ms):model.Add(var==0)
    if w[0]=='m' and add(p,(1,0,0)) in waiting_g0:model.Add(var==0)
  roots=connectivity_roots(model,shapes['X1'],set().union(*(set(adj(m)) for m in gm_x1)),6)
  for m in gm_x1:model.Add(sum(shapes['X1'][p] for p in adj(m) if p in shapes['X1'])>=1)
  if a.G0_on_T0:
   for motor in gm:
    for n,required in [('T0',motor in gm_t0),('X1',motor in gm_x1)]:
     contact=sum(shapes[n][p] for p in adj(motor) if p in shapes[n]);model.Add(contact>=1 if required else contact==0)
  if not a.front_stone_gate:model.Add(sum(shapes['X1'][p] for p in adj(P) if p in shapes['X1'])>=1)
  pickup_choices={}
  if a.omit_motor_recovery_control:pass
  elif a.T1_on_X1:
   for motor in ms:
    guarded(model.Add(sum(shapes['X1'][p] for p in adj(motor) if p in shapes['X1'])>=1),'new_motor_recovery')
    guarded(model.Add(sum(shapes['T0'][p] for p in adj(motor) if p in shapes['T0'])==0),'new_motor_recovery')
  elif a.mixed_recovery:
   for m in sorted(ms):
    other=next(x for x in ms if x!=m);pick=model.NewBoolVar('T0_pick'+str(m));pickup_choices[m]=pick
    for n,motor,minimum in [('T0',m,1),('X1',other,1),('T0',other,0),('X1',m,0)]:
     contact=sum(shapes[n][p] for p in adj(motor) if p in shapes[n])
     model.Add(contact>=1 if minimum else contact==0).OnlyEnforceIf(pick)
   model.Add(sum(pickup_choices.values())==1)
  else:
   for m in ms:model.Add(sum(shapes['T0'][p] for p in adj(m) if p in shapes['T0'])>=1)
  if a.T1_self_RB:model.Add(sum(shapes['T1'][p] for p in adj(srcobs) if p in shapes['T1'])>=1)
  if a.split_source_carrier:
   g1roots=connectivity_roots(model,shapes['G1'],set(adj(P if a.T1_self_RB else srcobs)),5)
   if a.front_stone_gate and not a.source_only_G1_control:model.Add(sum(shapes['G1'][p] for p in adj(P) if p in shapes['G1'])>=1)
  else:model.Add(sum(shapes['H0'][p] for p in adj(srcobs) if p in shapes['H0'])>=1)
  if not a.front_stone_gate:model.Add(sum(shapes['H0'][p] for p in adj(gateobs) if p in shapes['H0'])>=1)
  for p,var in shapes['T0'].items():
   if witnessed_sticky_pickup(p):model.Add(var==0)
  for ai,(an,ak,aw,*_) in enumerate(specs):
   for bn,bk,bw,*_ in specs[ai+1:]:
    for p,var in shapes[an].items():
     bad=set()
     for k in offsets(aw,bw):
      q=add(p,(k,0,0));bad.add(q)
      if ak==bk:bad.update(adj(q))
     for q in bad:
      if q in shapes[bn]:guarded(model.Add(var+shapes[bn][q]<=1),'separation_'+an+'_'+bn)
  model.Minimize(sum(v for sh in shapes.values() for v in sh.values()));s=cp_model.CpSolver();s.parameters.max_time_in_seconds=min(a.cp_seconds,max(.01,a.seconds-(time.monotonic()-start)));s.parameters.num_search_workers=2;status=s.Solve(model);rec.update(status=s.StatusName(status),seconds=s.WallTime())
  if status==cp_model.INFEASIBLE and a.diagnostic_cores:
   names={v.Index():k for k,v in assumptions.items()};rec['sufficient_unsat_core']=[names.get(i,str(i)) for i in s.SufficientAssumptionsForInfeasibility()]
   if a.minimize_cores:
    # Diagnostic only: delete assumption groups, never weaken a native trial.
    # Caps also enter connectivity/domain construction, so a cap label is
    # only the explicit cardinality constraint, not the entire size bound.
    core=list(rec['sufficient_unsat_core']);trials=[]
    for label in list(core):
     if time.monotonic()-start>=a.seconds:break
     trial=[k for k in core if k!=label];model.ClearAssumptions();model.AddAssumptions([assumptions[k] for k in trial]);ds=cp_model.CpSolver();ds.parameters.max_time_in_seconds=min(a.cp_seconds,max(.01,a.seconds-(time.monotonic()-start)));ds.parameters.num_search_workers=2;st=ds.Solve(model);trials.append({'removed':label,'status':ds.StatusName(st),'seconds':ds.WallTime()})
     if st==cp_model.INFEASIBLE:core=trial
    rec['reduced_unsat_core']=core;rec['core_deletion_trials']=trials;rec['core_subset_minimal']=len(trials)==len(rec['sufficient_unsat_core']) and all(t['status']!='UNKNOWN' for t in trials)
  if status in [cp_model.OPTIMAL,cp_model.FEASIBLE] and (a.omit_motor_recovery_control or a.source_only_G1_control):
   rec['shapes']={n:sorted(p for p,v in cells.items() if s.Value(v)) for n,cells in shapes.items()};geometry_witness=rec;records.append(rec);save(True);print(json.dumps({'control_geometry_witness':model_index,'native_acceptance':False}),flush=True);return
  if status in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
   case=a.out/f'case{len(records):04}';case.mkdir();tests+=1;ff=Flyer.load(a.base/'problem.flyer')
   for p in removed:ff.remove(p)
   selected={n:sorted(p for p,v in cells.items() if s.Value(v)) for n,cells in shapes.items()}
   if pickup_choices:rec['normal_on_T0']=next(p for p,v in pickup_choices.items() if s.Value(v))
   for n,mat,*_ in specs:
    for p in selected[n]:assert p not in ff._cells;ff.set(p,Block(mat))
   for p,b in [(srcobs,Block(Kind.REDSTONE_BLOCK) if a.T1_self_RB else Block.observer(sdi,powered=False)),(gateobs,Block.observer(gdi,powered=False)),(sticky,Block.piston(1,sticky=True)),(P,Block(Kind.SMOOTH_STONE)),*[(m,Block.piston(0)) for m in ms]]:assert p not in ff._cells;ff.set(p,b)
   ff.save(case/'problem.flyer');loaded=Flyer.load(case/'problem.flyer');assert loaded._cells==ff._cells and loaded._piston_blocks==ff._piston_blocks
   cc=copy.deepcopy(c);next(p for p in cc['ports'] if p['name']=='X1_front')['at']=list(next(p for p,v in roots.items() if s.Value(v)));next(p for p in cc['ports'] if p['name']=='T1_front')['name']='X2_front'
   cc['ports'] += [{'name':'T1_front','at':list(Q),'word':'wmmmw','role':'input','provenance':[None,'internal','internal','internal',None]},{'name':'H0_front','at':list(h),'word':'mmwwm','role':'input','provenance':['supplied','supplied',None,None,'supplied']}];cc['name']=case.name;cc['boundary_envelope']={'min':[0,0,0],'max':[40,20,30]};rows=[]
   if a.split_source_carrier:cc['ports'].append({'name':'G1_front','at':list(next(p for p,v in g1roots.items() if s.Value(v))),'word':'mmwwm','role':'input','provenance':['supplied','supplied',None,None,'supplied']})
   for p in cc['ports']:
    for cy in range(3):
     for slot,v in enumerate(p['provenance']):
      if v=='supplied':rows.append((10*cy+2*slot,p['at'][0]+3*cy+p['word'][:slot].count('m'),*p['at'][1:],12))
   (case/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
   for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
   rec['shapes']=selected;dump(case/'preparation.json',rec);subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,capture_output=True,check=False);rec['native']=json.loads((case/'native.json').read_text(encoding='utf-8'))
   if rec['native']['verified']:passed=str(case)
  records.append(rec);save()
  if passed:break
 save(True);print(json.dumps({'models':len(records),'source_choices':len(source_choices),'actors_seen':actors_seen,'tests':tests,'passed':passed,'seconds':time.monotonic()-start}),flush=True)
if __name__=='__main__':main()
