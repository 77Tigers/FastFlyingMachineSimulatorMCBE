"""Bounded shared-RB H1 three-push construction; fixed G1/H0 recovery roles.

Whole39 H1 permanent9 = at most7 glue, retained observer, one RB.
Optimistic layout filters are not physical acceptance; native all-order tests decide.
"""
import argparse,hashlib,itertools,json,subprocess,time,collections
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer,body_of
from fastflyer import Block,Kind
from search_T1_two_pushes import D,add,adj,dist
from search_T1_pull_routes import offsets
from model_recovery_layout import connectivity
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=60);ap.add_argument('--max-native',type=int,default=8);ap.add_argument('--free-connector',action='store_true');a=ap.parse_args();start=time.monotonic()
 base=HERE/'out/quarter_ring_contacts/G1_pull_X2_gate_slime_hard_forward_hook';out=HERE/('out/quarter_ring_contacts/H1_shared_source'+('_free_connector' if a.free_connector else ''));out.mkdir(exist_ok=False);f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'));ports={p['name']:p for p in c['ports']};old=body_of(f._cells,tuple(ports['H1_power']['at']));fixed=set(f._cells)-old;g=body_of(f._cells,tuple(ports['G1_front']['at']));h=body_of(f._cells,tuple(ports['H0_front']['at']));root=(20,0,15) if a.free_connector else tuple(ports['H1_power']['at']);cap=7
 others=[(body_of(f._cells,tuple(p['at'])),f._cells[tuple(p['at'])].kind,p['word']) for n,p in ports.items() if n!='H1_power'];counts=collections.Counter();records=[];tests=0;complete=True
 supp2={v for q in g for v in adj(q)}-set(f._cells);supp3={v for q in h for v in adj(q)}-set(f._cells);supp4={v for q in h for v in adj(add(q,(1,0,0)))}-set(f._cells)
 candidates=[]
 for q2,q3 in itertools.product(sorted(supp2),sorted(supp3)):
  if q2==q3:continue
  rbs={add(add(q2,(2,0,0)),d) for d in D[2:]}&{add(add(q3,(2,0,0)),d) for d in D[2:]}
  for rb,q4 in itertools.product(sorted(rbs-set(f._cells)),sorted(supp4)):
   if rb not in {add(add(q4,(1,0,0)),d) for d in D[2:]} or len({rb,q2,q3,q4,add(q4,(1,0,0))})!=5:continue
   if a.free_connector and q4 in {add(q,(1,0,0)) for q in h}:counts['learned_H0_destination']+=1;continue
   pins=(old-{(20,1,15)} if a.free_connector else old)|{add(q2,(3,0,0)),add(q3,(3,0,0)),add(q4,(2,0,0))};hw={rb,q2,q3,q4,add(q4,(1,0,0))}
   if pins&fixed or hw&set(f._cells) or pins&hw:counts['occupied']+=1;continue
   if any(dist(x,y)>cap-1 for x in pins for y in pins):counts['diameter']+=1;continue
   candidates.append((sum(dist(root,p) for p in pins),q2,q3,q4,rb,pins,hw))
 for _,q2,q3,q4,rb,pins,hw in sorted(candidates,key=lambda v:v[:5]):
  if time.monotonic()-start>a.seconds or tests>=a.max_native:complete=False;break
  ranges=[range(max(q[k] for q in pins)-cap+1,min(q[k] for q in pins)+cap) for k in range(3)];domain={q for q in itertools.product(*ranges) if q not in fixed|hw and all(dist(q,p)<=cap-1 for p in pins)}
  domain={q for q in domain if not any(any(dist(add(q,(k,0,0)),p)<=(1 if kind==Kind.HONEY else 0) for k in offsets('wwmmm',word) for p in shape) for shape,kind,word in others)}
  if a.free_connector:domain-={add(q,(k,0,0)) for q in [q2,q3] for k in [1,2]}|{add(q4,(1,0,0))}
  rec={'motors':[q2,q3,q4],'RB':rb}
  if not pins<=domain:counts['phase_pins']+=1;continue
  model=cp_model.CpModel();v={q:model.NewBoolVar(str(q)) for q in domain}
  for q in pins:model.Add(v[q]==1)
  model.Add(sum(v.values())<=cap);model.Add(sum(v[q] for q in adj(rb) if q in v)>=1);connectivity(model,v,root,cap);model.Minimize(sum(v.values()));solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=.5;solver.parameters.num_search_workers=2;status=solver.Solve(model)
  if status not in [cp_model.OPTIMAL,cp_model.FEASIBLE]:counts[solver.StatusName(status)]+=1;continue
  shape=sorted(q for q,b in v.items() if solver.Value(b));case=out/f'case{tests:03}';case.mkdir();tests+=1;ff=Flyer.load(base/'problem.flyer')
  for q in old:ff.remove(q)
  for q in shape:ff.set(q,Block(Kind.HONEY))
  for q,b in [(q2,Block.piston(0)),(q3,Block.piston(0)),(q4,Block.piston(0,state=2)),(add(q4,(1,0,0)),Block(Kind.PISTON_ARM)),(rb,Block(Kind.REDSTONE_BLOCK))]:assert q not in ff._cells;ff.set(q,b)
  ff.set_piston_blocks(q4,[add(q4,(1,0,0))]);canonical=ff.canonicalize();delta=tuple(min(q[k] for q in canonical._cells)-min(q[k] for q in ff._cells) for k in range(3));canonical.save(case/'problem.flyer');loaded=Flyer.load(case/'problem.flyer');assert loaded._cells==canonical._cells and loaded._piston_blocks==canonical._piston_blocks
  cc=json.loads(json.dumps(c));cc['name']=case.name;rows=[]
  for p in cc['ports']:
   if p['name']=='H1_power':p['provenance']=[None,None,'internal','internal','internal'];p['at']=list(root)
   p['at']=[x+delta[k] for k,x in enumerate(p['at'])]
   for cy in range(3):
    for s,x in enumerate(p['provenance']):
     if x=='supplied':rows.append((cy*10+s*2,p['at'][0]+cy*3+p['word'][:s].count('m'),*p['at'][1:],12))
  (case/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
  for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
  budget=json.loads((base/'whole39_source_budget.json').read_text(encoding='utf-8'));assert budget['permanent_masses']['H1_power']==9;budget['source_allocation']['H1_power']={'glue':len(shape),'observer':1,'RB':1,'future_glue_reserve':7-len(shape),'mass':9};budget['scope']=__doc__+' All whole39 carrier masks/masses/loads retained; native still required.';dump(case/'whole39_source_budget.json',budget);dump(case/'preparation.json',{'scope':__doc__,'source_record':rec,'H1_glue':shape,'normalization_delta':delta,'base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest()});(case/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
  subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=40);native=json.loads((case/'native.json').read_text(encoding='utf-8'));records.append({**rec,'shape':shape,'case':str(case),'native':native});counts['native_pass' if native['verified'] else 'native_fail']+=1;dump(out/'progress.json',{'counts':dict(counts),'records':records})
  if native['verified']:complete=False;break
 dump(out/'report.json',{'scope':__doc__,'complete':complete,'seconds':time.monotonic()-start,'candidate_count':len(candidates),'counts':dict(counts),'records':records});(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'complete':complete,'candidates':len(candidates),'seconds':time.monotonic()-start,'counts':dict(counts)}))
if __name__=='__main__':main()
