"""Optimistic G0 source-face preflight; upper relay and complete flyer remain unbuilt."""
import hashlib,itertools,json
from pathlib import Path
from assemble import Flyer,body_of
from fastflyer import Kind
from search_T1_two_pushes import D,add,adj,dist
from search_T1_pull_routes import offsets
from steiner_glue_bound import connected_glue_minimum
HERE=Path(__file__).resolve().parent

def main():
 base=HERE/'out/quarter_ring_contacts/G0_front_recovery_upper';f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'));ports={q['name']:q for q in c['ports']};freed=['T0','X0','G0','X1_front'];removed=set().union(*(body_of(f._cells,tuple(ports[n]['at'])) for n in freed))|{(17,5,12),(16,5,11),(16,5,13),(16,6,12),(17,4,11),(18,4,11),(15,4,12),(16,4,12),(17,4,12),(17,4,13)};fixed=set(f._cells)-removed;others=[(body_of(f._cells,tuple(q['at'])),f._cells[tuple(q['at'])].kind,q['word']) for q in c['ports'] if q['name'] not in freed];domain=list(itertools.product(range(11,23),range(0,9),range(8,17)));lower=(17,3,13);rows=[]
 for center in itertools.product([18],range(3,7),range(10,15)):
  for missing in range(2,6):
   rb=add(center,(-1,0,0));star={center,*[add(center,d) for j,d in enumerate(D) if j>=2 and j!=missing]};gm={add(q,(-2,0,0)) for q in star-{center}}
   if (star|gm|{rb})&fixed:continue
   if any(add(m,(1,0,0))==lower for m in gm):continue
   cs={q for q in domain if q not in fixed|gm|{rb} and all(dist(q,t)<=5 for t in star)}
   cs={q for q in cs if not any(mat==Kind.HONEY and any(dist(add(q,(k,0,0)),v)<=1 for k in offsets('wmmmw',w) for v in sh) for sh,mat,w in others)}
   minimum=connected_glue_minimum(cs,[{q} for q in star]+[set(adj(lower))]);rows.append({'center':center,'missing_face':missing,'minimum_G0_lower_support':minimum,'cap':6,'cap_feasible':minimum is not None and minimum<=6,'normals':sorted(gm)})
 rows.sort(key=lambda v:(v['minimum_G0_lower_support'] if v['minimum_G0_lower_support'] is not None else 999,sum(dist(q,(15,3,11)) for q in v['normals']),v['center'],v['missing_face']))
 assert any(v['center']==(18,5,12) and v['missing_face']==3 and v['cap_feasible'] for v in rows)
 out=HERE/'out/quarter_ring_contacts/G0_face_swap_preflight/source_pose_bounds.json';out.write_text(json.dumps({'scope':__doc__+' Fixed rear hardware/material retained. Omits upper relay, variable-body geometry and sources.','base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest(),'records':rows},indent=2)+'\n',encoding='utf-8');print(json.dumps({'records':len(rows),'survivors':[v for v in rows if v['cap_feasible']][:12]}))
if __name__=='__main__':main()
