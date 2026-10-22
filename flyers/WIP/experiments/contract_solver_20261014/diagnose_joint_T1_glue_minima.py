"""Optimistic per-body minima in saved joint domains; no physical acceptance."""
import argparse,itertools,json,time
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer,body_of
from fastflyer import Kind
from search_T1_two_pushes import add,adj,dist,connectivity_roots,dump,witnessed_sticky_pickup
from model_recovery_layout import connectivity
from steiner_glue_bound import connected_glue_minimum
from phase_glue_bound import phase_witness


def main():
 ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);ap.add_argument('--seconds',type=float,default=2);ap.add_argument('--T1-H0-contact-control',action='store_true');ap.add_argument('--only-indices',nargs='+',type=int);ap.add_argument('--cap-feasibility',action='store_true');ap.add_argument('--exact-steiner',action='store_true');ap.add_argument('--phase-witnesses',action='store_true');a=ap.parse_args();assert not a.phase_witnesses or a.exact_steiner
 limits=json.loads((a.run/'input_manifest.json').read_text(encoding='utf-8'))['limits'];base=Path(limits['base']);f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'));ports={p['name']:p for p in c['ports']};tr=tuple(ports['T0']['at']);r=json.loads((a.run/'report.json').read_text(encoding='utf-8'));assert not r.get('T1_self_RB',False),'self-RB source/terminal geometry must be implemented before this diagnostic';tl=tuple(r['T0_late_target']);gm={tuple(x) for x in r.get('G0_X1_normals',r['G0_normals'])};gm_t0={tuple(x) for x in r.get('G0_T0_normals',[])};g0=body_of(f._cells,tuple(ports['G0']['at']));fixed=set(f._cells)-body_of(f._cells,tr)-body_of(f._cells,tuple(ports['X1_front']['at']));wait=g0|{p for p,b in f._cells.items() if b.kind in [Kind.REDSTONE_BLOCK,Kind.OBSERVER] and any(dist(p,q)==1 for q in g0)};domain=list(itertools.product(range(11,24),range(0,11),range(7,19)));answer=[];seen=set();split=r.get('split_source_carrier',False);front=r.get('front_stone_gate',False);both=r.get('T1_on_X1',False);tcap=r.get('T0_cap',8);source_only=r.get('source_only_G1_control',False);others=[(p['name'],body_of(f._cells,tuple(p['at'])),f._cells[tuple(p['at'])].kind,p['word']) for p in c['ports'] if p['name'] not in ['T0','X1_front']]
 for rec in r['records']:
  if rec['status']!='INFEASIBLE' or (a.only_indices is not None and rec['index'] not in a.only_indices):continue
  key=tuple(json.dumps(rec[k],sort_keys=True) for k in ['center','normals','source_observer','source_direction','H0_root','T1_root','gate_observer','gate_direction','sticky','stone']+(['H0_kind','T1_kind','G1_kind'] if a.phase_witnesses else []))
  if key in seen:continue
  seen.add(key);C=tuple(rec['center']);ms={tuple(x) for x in rec['normals']};src,gate,sticky,P,h,Q=[tuple(rec[k]) for k in ['source_observer','gate_observer','sticky','stone','H0_root','T1_root']];out=add(C,(-1,0,0));targets={C,Q,*[add(m,(2,0,0)) for m in ms]};blocked=fixed|ms|{src,gate,sticky,P,out};waiting=wait|({gate} if front else set());bodies={
   'T0':{p for p in domain if p not in blocked and dist(tr,p)+dist(p,tl)+dist(tr,tl)<=2*(tcap-1)},
   'T1':{p for p in domain if p not in blocked and all(dist(p,Q)+dist(p,q)+dist(Q,q)<=12 for q in targets) and p not in {add(m,(1,0,0)) for m in ms}},
   'H0':{p for p in domain if p not in blocked and dist(p,h)<=1},
   'X1':{p for p in domain if p not in blocked and all(dist(p,m)<=6 for m in (gm|ms if both else gm)) and (front or dist(p,P)<=6)}}
  if split:bodies['G1']={p for p in domain if p not in blocked and dist(p,src)<=5 and (not front or source_only or dist(p,P)<=5)}
  row={'index':rec['index'],'center':C,'bodies':{}}
  for n,cs in bodies.items():
   if a.T1_H0_contact_control and n!='T1':continue
   cs={p for p in cs if not(not(a.T1_H0_contact_control and n=='T1') and any(dist(p,hw)<=1 for hw in ([gate,sticky] if n=='G1' else [src,gate] if n=='H0' and front else [src] if n=='H0' and split else [] if n=='H0' else [src,gate,sticky]))) and not(n in ['H0','G1'] and any(dist(p,m)<=1 for m in ms)) and not(n!='T1' and add(p,(1,0,0)) in waiting) and not(n=='T0' and witnessed_sticky_pickup(p)) and not(gm_t0 and any(dist(p,m)<=1 for m in (gm if n=='T0' else gm_t0 if n=='X1' else set())))};model=cp_model.CpModel();vs={p:model.NewBoolVar(str(p)) for p in cs};pins={'T0':{tr,tl},'T1':targets,'H0':{h},'X1':set(),'G1':set()}[n]
   assert pins<=cs
   if a.exact_steiner:
    groups=[{p} for p in pins]
    if n=='T0':groups += [set(adj(m)) for m in gm_t0]
    if n=='X1':groups += [set(adj(m)) for m in (gm|ms if both else gm if front else gm|{P})]
    if n=='H0':groups += [set(adj(o)) for o in ([] if front else [gate] if split else [src,gate])]
    if n=='G1':groups += [set(adj(src))]+([set(adj(P))] if front and not source_only else [])
    val=connected_glue_minimum(cs,groups);cap={'T0':tcap,'T1':7,'H0':2,'X1':6,'G1':5}[n];row['bodies'][n]={'status':'EXACT_STEINER_DP','optimal_minimum':val,'cap':cap,'cap_feasible':val is not None and val<=cap,'domain_cells':len(cs)}
    if a.phase_witnesses:
     mats={'T0':Kind.SLIME,'X1':Kind.SLIME,'T1':Kind[rec['T1_kind']],'H0':Kind[rec['H0_kind']],'G1':Kind[rec['G1_kind']] if split else None};words={'T0':'mwwmm','X1':'mwwmm','T1':'wmmmw','H0':'mmwwm','G1':'mmwwm'};pins_by={'T0':{tr,tl},'T1':targets,'H0':{h},'X1':set(),'G1':set()}
     controls={'fixed_material':[(bn,sh,bk,bw) for bn,sh,bk,bw in others if bk==mats[n]]}
     controls.update({'mandatory_'+bn:[(bn,ps,mats[bn],words[bn])] for bn,ps in pins_by.items() if bn!=n and ps})
     row['bodies'][n]['phase_controls']={label:phase_witness(cs,groups,cap,words[n],mats[n],obs) for label,obs in controls.items()}
    continue
   for p in pins:model.Add(vs[p]==1)
   if n=='T0':
    for m in gm_t0:model.Add(sum(vs[p] for p in adj(m) if p in vs)>=1)
   if n=='X1':
    connectivity_roots(model,vs,set().union(*(set(adj(m)) for m in gm)),len(cs))
    for m in (gm|ms if both else gm if front else gm|{P}):model.Add(sum(vs[p] for p in adj(m) if p in vs)>=1)
   elif n=='G1':
    connectivity_roots(model,vs,set(adj(src)),len(cs))
    if front and not source_only:model.Add(sum(vs[p] for p in adj(P) if p in vs)>=1)
   else:connectivity(model,vs,{'T0':tr,'T1':Q,'H0':h}[n],len(cs))
   if n=='H0':
    for observer in ([] if front else [gate] if split else [src,gate]):model.Add(sum(vs[p] for p in adj(observer) if p in vs)>=1)
   cap={'T0':tcap,'T1':7,'H0':2,'X1':6,'G1':5}[n]
   if a.cap_feasibility:model.Add(sum(vs.values())<=cap)
   else:model.Minimize(sum(vs.values()))
   s=cp_model.CpSolver();s.parameters.max_time_in_seconds=a.seconds;s.parameters.num_search_workers=2;st=s.Solve(model);item={'status':s.StatusName(st),'bound':s.BestObjectiveBound(),'seconds':s.WallTime(),'domain_cells':len(cs)}
   if st in [cp_model.FEASIBLE,cp_model.OPTIMAL]:item.update(glue_count=sum(s.Value(v) for v in vs.values()),optimal_minimum=s.ObjectiveValue() if st==cp_model.OPTIMAL and not a.cap_feasibility else None,cells=sorted(p for p,v in vs.items() if s.Value(v)))
   if a.cap_feasibility:item.update(cap=cap,cap_feasible=True if st in [cp_model.OPTIMAL,cp_model.FEASIBLE] else False if st==cp_model.INFEASIBLE else None)
   row['bodies'][n]=item
  answer.append(row)
 report={'scope':'Independent per-body connected minima omit material/interbody constraints by default; named phase_controls add only the recorded fixed/mandatory-cell exclusions. Explicit glue caps and new motor recovery remain omitted. Size-derived domains remain fixed; bounds are local, not global architecture impossibility.','phase_witnesses':a.phase_witnesses,'source_only_G1_control':source_only,'T1_H0_contact_control':a.T1_H0_contact_control,'split_source_carrier':split,'front_stone_gate':front,'selected_indices':a.only_indices,'cap_feasibility_query':a.cap_feasibility,'exact_steiner':a.exact_steiner,'records':answer};dump(a.run/('per_body_phase_witnesses.json' if a.phase_witnesses else 'per_body_exact_steiner.json' if a.exact_steiner else 'per_body_cap_feasibility.json' if a.cap_feasibility else 'T1_H0_contact_minima_control.json' if a.T1_H0_contact_control else 'per_body_glue_minima.json'),report);print(json.dumps(report))
if __name__=='__main__':main()
