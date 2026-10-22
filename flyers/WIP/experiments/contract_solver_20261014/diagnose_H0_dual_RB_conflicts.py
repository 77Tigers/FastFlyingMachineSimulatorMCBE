"""Causal geometry/phase controls for dual-RB H0; never physical acceptance."""
import collections,itertools,json,time
from pathlib import Path
from assemble import Flyer,body_of
from fastflyer import Kind
from search_T1_two_pushes import add,adj,dist
from search_T1_pull_routes import offsets
from steiner_glue_bound import connected_glue_minimum
HERE=Path(__file__).resolve().parent

def main():
 out=HERE/'out/quarter_ring_contacts/H0_dual_RB_preflight';report=json.loads((out/'report.json').read_text(encoding='utf-8'));base=HERE/'out/quarter_ring_contacts/joint_T1_self_RB_shifted_search/case5167';f=Flyer.load(base/'problem.flyer');ports={q['name']:q for q in json.loads((base/'before_natural.json').read_text(encoding='utf-8'))['ports']};root=tuple(ports['H0_front']['at']);fixed=set(f._cells)-body_of(f._cells,root);others=[(name,body_of(f._cells,tuple(q['at'])),f._cells[tuple(q['at'])].kind,q['word']) for name,q in ports.items() if name!='H0_front'];domain=list(itertools.product(range(14,24),range(-1,8),range(10,19)));unique={}
 for r in report['records']:unique.setdefault(json.dumps({k:r[k] for k in ['RBs','motors','head','pins']},sort_keys=True),r)
 raw=[];hist=collections.Counter()
 for r in unique.values():
  RBs=list(map(tuple,r['RBs']));motors=list(map(tuple,r['motors']));head=tuple(r['head']);pins=set(map(tuple,r['pins']));hardware=set(RBs+motors+[head]);cells={q for q in domain if q not in fixed|hardware and all(dist(root,q)+dist(q,t)+dist(root,t)<=12 for t in pins)};groups=[{q} for q in pins]+[set(adj(q)) for q in RBs];minimum=connected_glue_minimum(cells,groups);hist[str(minimum)]+=1;raw.append((minimum,r,cells,groups))
 raw.sort(key=lambda x:x[0] if x[0] is not None else 999);answer=[]
 for minimum,r,cells,groups in raw[:8]:
  for mat in [Kind.HONEY,Kind.SLIME]:
   blocked={}
   for pin in map(tuple,r['pins']):
    for name,shape,kind,w in others:
     hit=next(((q,k) for k in sorted(offsets('mmwwm',w)) for q in sorted(shape) if dist(add(pin,(k,0,0)),q)<=(1 if mat==kind else 0)),None)
     if hit:blocked.setdefault(str(pin),[]).append({'body':name,'cell':hit[0],'offset_x':hit[1],'same_material':mat==kind})
   controls={}
   for omitted in [set(),{'G0'},{'T1_front'},{'G0','T1_front'}]:
    cs={q for q in cells if not any(any(dist(add(q,(k,0,0)),v)<=(1 if mat==kind else 0) for k in offsets('mmwwm',w) for v in sh) for name,sh,kind,w in others if name not in omitted)};controls[','.join(sorted(omitted)) or 'none']=connected_glue_minimum(cs,groups)
   answer.append({'RBs':r['RBs'],'motors':r['motors'],'pins':r['pins'],'material':mat.name,'raw_minimum':minimum,'blocked_pins':blocked,'minimum_omitting_phase_bodies':controls})
 result={'scope':__doc__+' Hardware/initial occupancy unchanged even in omitted-body phase controls; fixed domains retained.','pose_count':len(raw),'raw_minimum_histogram':dict(hist),'selected_best_poses':8,'records':answer};(out/'causal_controls.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'pose_count':len(raw),'raw_histogram':dict(hist),'controls':[(r['material'],r['raw_minimum'],r['minimum_omitting_phase_bodies']) for r in answer]}))
if __name__=='__main__':main()
