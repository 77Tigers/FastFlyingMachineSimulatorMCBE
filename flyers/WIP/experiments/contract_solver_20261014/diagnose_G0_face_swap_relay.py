"""Independent necessary glue/phase bounds for the lower-face relay experiment."""
import argparse,itertools,json,time,hashlib
from pathlib import Path
from assemble import Flyer,body_of
from fastflyer import Kind
from search_T1_two_pushes import D,add,adj,dist,witnessed_sticky_pickup
from search_T1_pull_routes import offsets
from steiner_glue_bound import connected_glue_minimum
from phase_glue_bound import phase_witness

def main():
 ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);ap.add_argument('--seconds',type=float,default=50);a=ap.parse_args();start=time.monotonic();here=Path(__file__).resolve().parent;base=here/'out/quarter_ring_contacts/G0_front_recovery_upper';f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'));ports={q['name']:q for q in c['ports']};freed=['T0','X0','G0','X1_front']
 removed=set().union(*(body_of(f._cells,tuple(ports[n]['at'])) for n in freed))|{(17,5,12),(16,5,11),(16,5,13),(16,6,12),(17,4,11),(18,4,11),(15,4,12),(16,4,12),(17,4,12),(17,4,13)};fixed=set(f._cells)-removed
 others=[(q['name'],body_of(f._cells,tuple(q['at'])),f._cells[tuple(q['at'])].kind,q['word']) for q in c['ports'] if q['name'] not in freed];domain=list(itertools.product(range(11,23),range(0,9),range(8,17)));gm={(16,5,11),(16,5,13),(16,4,12)};center=(18,5,12);rb=(17,5,12);star={center,(18,5,11),(18,5,13),(18,4,12)};tr=(15,3,11);lower=(17,3,13);report=json.loads((a.run/'report.json').read_text(encoding='utf-8'));answer=[]
 for r in report['records']:
  if r['status'] not in ['INFEASIBLE','UNKNOWN']:continue
  if time.monotonic()-start>a.seconds:break
  center=tuple(r.get('G0_center',[18,5,12]));missing=r.get('G0_missing_face',2);rb=add(center,(-1,0,0));star={center,*[add(center,d) for j,d in enumerate(D) if j>=2 and j!=missing]};gm={add(q,(-2,0,0)) for q in star-{center}}
  late=tuple(r['late']);target=tuple(r['target']);chain=list(map(tuple,r['chain']));obs=tuple(r['observer']);head=add(late,(1,0,0));glue_root=r.get('glue_relay_root',False);pusher=chain[0] if glue_root else add(chain[-1],(-3,0,0));blocked=fixed|{late,head,*(chain[1:] if glue_root else chain),obs,rb,*gm};row={'index':r['index'],'original_status':r['status'],'glue_relay_root':glue_root,'bodies':{}}
  specs=[('T0',Kind.SLIME,'mwwmm',9,{tr,target}),('X0',Kind.HONEY,'mmmww',7 if glue_root else 6,{pusher}),('G0',Kind.HONEY,'wmmmw',6,star),('X1',Kind.SLIME,'mwwmm',6,set())]
  for n,mat,w,cap,pins in specs:
   cells={p for p in domain if p not in blocked and (all(dist(p,q)<=cap-1 for q in pins) if pins else all(dist(p,q)<=cap for q in gm))}
   cells={p for p in cells if not any(mat==kind and any(dist(add(p,(k,0,0)),q)<=1 for k in offsets(w,ow) for q in sh) for _,sh,kind,ow in others) and not(w[0]=='m' and any(p==add(hw,(-1,0,0)) for hw in [rb,lower,obs])) and not(n=='G0' and p==add(chain[-1],(1,0,0))) and not(n=='X0' and p==add(late,(-1,0,0))) and not(n=='T0' and witnessed_sticky_pickup(p))}
   groups=[{p} for p in pins]
   if n=='X1':groups += [set(adj(m)) for m in gm]
   if n=='G0':groups += [set(adj(o)) for o in [lower,obs]]
   if n=='X0':groups += [set(adj(m)) for m in [(12,3,11),add(late,(-1,0,0))]]
   minimum=connected_glue_minimum(cells,groups);item={'minimum':minimum,'cap':cap,'cap_feasible':minimum is not None and minimum<=cap,'domain_cells':len(cells)}
   if item['cap_feasible']:
    v=phase_witness(cells,groups,cap,w,mat,[(bn,ps,bmat,bw) for bn,bmat,bw,_,ps in specs if bn!=n and ps]);item['mandatory_phase']={k:v[k] for k in ['minimum','cap','cap_feasible']};item['mandatory_phase']['empty_groups']=[g['cells'] for g in v['contact_groups'] if not g['allowed']]
   row['bodies'][n]=item
  answer.append(row)
 result={'scope':__doc__+' Optimistic independent-body necessary bounds; hard actor domains retained, variable-body separation only against mandatory pins. Not physical acceptance.','complete':len(answer)==sum(r['status'] in ['INFEASIBLE','UNKNOWN'] for r in report['records']),'seconds':time.monotonic()-start,'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'records':answer};(a.run/'per_body_bounds.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'complete':result['complete'],'records':len(answer),'seconds':result['seconds']}))
if __name__=='__main__':main()
