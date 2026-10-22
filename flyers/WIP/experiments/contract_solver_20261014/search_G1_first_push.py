"""Add budgeted G1 push0 and its own observer; push4 retained, pull1 stays supplied."""
import argparse,collections,itertools,json,hashlib,subprocess,time
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
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=90);ap.add_argument('--max-native',type=int,default=12);ap.add_argument('--material',choices=['HONEY','SLIME'],default='HONEY');ap.add_argument('--out',default='G1_first_push_search');ap.add_argument('--free-connector',action='store_true');ap.add_argument('--allow-front-stone',action='store_true');ap.add_argument('--diagnose-minimum',action='store_true');a=ap.parse_args();start=time.monotonic();material=Kind[a.material]
 base=HERE/'out/quarter_ring_contacts/G1_late_push_search/case000';out=HERE/'out/quarter_ring_contacts'/a.out;out.mkdir(exist_ok=False);f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'));ports={p['name']:p for p in c['ports']};root=tuple(ports['G1_front']['at']);old=body_of(f._cells,root);fixed=set(f._cells)-old;others=[(name,body_of(f._cells,tuple(p['at'])),f._cells[tuple(p['at'])].kind,p['word']) for name,p in ports.items() if name!='G1_front'];budget=json.loads((base/'whole39_source_budget.json').read_text(encoding='utf-8'));action=next(q for q in budget['actions'] if q['target']=='G1_power' and q['slot']==0);assert action['kind']=='push' and action['piston_word']=='wwmmm';assert budget['source_allocation']['G1_power']['mass']==8
 support=None;tshape=body_of(f._cells,tuple(ports['T1_front']['at']))
 for s in [2,3]:
  dx='wmmmw'[:s].count('m')-action['piston_word'][:s].count('m');ss={n for q in tshape for n in adj(add(q,(dx,0,0)))};support=ss if support is None else support&ss
 parent_prep=json.loads((base/'preparation.json').read_text(encoding='utf-8'));parent_delta=tuple(parent_prep['normalization_delta']);late_motor=add(tuple(parent_prep['source_record']['motor']),parent_delta);late_rb=add(tuple(parent_prep['source_record']['RB']),parent_delta);basepins={root,add(late_motor,(2,0,0))} if a.free_connector else old;cap=8 if a.diagnose_minimum else 5
 records=[];counts=collections.Counter();tests=0;complete=True
 for motor in sorted(support-fixed):
  for side in D[2:]:
   hard=add(motor,side);target=add(motor,(1,0,0))
   if a.allow_front_stone and target in fixed and f._cells[target].kind==Kind.SMOOTH_STONE:target=add(motor,(2,0,0))
   pins=basepins|{hard,target}
   if pins&fixed or len(pins)>cap:counts['pins_occupied_or_cap']+=1;continue
   if any(dist(x,y)>cap-1 for x in pins for y in pins):counts['diameter']+=1;continue
   for direction,d in enumerate(D):
    if time.monotonic()-start>a.seconds or tests>=a.max_native:complete=False;break
    obs=add(hard,tuple(-v for v in d));hardware={motor,obs};rec={'motor':motor,'observer':obs,'direction':direction,'hard_target':hard,'material':a.material}
    if len(hardware)!=2 or hardware&fixed or hardware&pins:counts['hardware_occupied']+=1;continue
    ranges=[range(max(q[k] for q in pins)-cap+1,min(q[k] for q in pins)+cap) for k in range(3)];domain={q for q in itertools.product(*ranges) if q not in fixed|hardware and all(dist(q,p)<=cap-1 for p in pins) and all(dist(x,q)+dist(q,y)+dist(x,y)<=2*(cap-1) for x in pins for y in pins)}
    domain={q for q in domain if not any(any(dist(add(q,(k,0,0)),p)<=(1 if kind==material else 0) for k in offsets('mmwwm',word) for p in shape) for _,shape,kind,word in others)}
    if not pins<=domain:counts['phase_mandatory_excluded']+=1;continue
    model=cp_model.CpModel();v={q:model.NewBoolVar(str(q)) for q in domain}
    for q in pins:model.Add(v[q]==1)
    model.Add(sum(v[q] for q in adj(late_rb) if q in v)>=1);model.Add(sum(v.values())<=cap);connectivity(model,v,root,cap);model.Minimize(sum(v.values()));solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=.35;solver.parameters.num_search_workers=2;status=solver.Solve(model)
    if status not in [cp_model.OPTIMAL,cp_model.FEASIBLE]:counts[solver.StatusName(status)]+=1;records.append({**rec,'status':solver.StatusName(status)});continue
    shape=sorted(q for q,b in v.items() if solver.Value(b))
    if len(shape)>5:counts['over_budget_minimum']+=1;records.append({**rec,'status':'over_budget_minimum','shape':shape,'minimum':len(shape) if status==cp_model.OPTIMAL else None,'lower_bound':solver.BestObjectiveBound()});continue
    case=out/f'case{tests:03}';case.mkdir();tests+=1;ff=Flyer.load(base/'problem.flyer')
    for q in old:ff.remove(q)
    for q in shape:assert q not in ff._cells;ff.set(q,Block(material))
    for q,b in [(motor,Block.piston(0)),(obs,Block.observer(direction,powered=True))]:assert q not in ff._cells;ff.set(q,b)
    canonical=ff.canonicalize();delta=tuple(min(q[k] for q in canonical._cells)-min(q[k] for q in ff._cells) for k in range(3));canonical.save(case/'problem.flyer');loaded=Flyer.load(case/'problem.flyer');assert loaded._cells==canonical._cells and loaded._piston_blocks==canonical._piston_blocks
    cc=json.loads(json.dumps(c));cc['name']=case.name;cc['boundary_envelope']={'min':[0,0,0],'max':[100,100,100]};rows=[]
    for p in cc['ports']:
     p['at']=[x+delta[k] for k,x in enumerate(p['at'])]
     if p['name']=='G1_front':p['provenance']=['internal','supplied',None,None,'internal']
     for cy in range(3):
      for s,source in enumerate(p['provenance']):
       if source=='supplied':rows.append((10*cy+2*s,p['at'][0]+3*cy+p['word'][:s].count('m'),*p['at'][1:],12))
    (case/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
    for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
    dump(case/'preparation.json',{'scope':__doc__+' Seventeen natural/thirteen supplied strokes attempted; not complete flyer.','source_record':rec,'G1_shape':shape,'normalization_delta':delta,'base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest(),'budget':'G1 five glue+stone+RB+own observer=8; full39 mass unchanged.'})
    subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,check=False,stdout=subprocess.DEVNULL,timeout=40);native=json.loads((case/'native.json').read_text(encoding='utf-8'));records.append({**rec,'shape':shape,'case':str(case),'native':native});counts['native_pass' if native['verified'] else 'native_fail']+=1;dump(out/'progress.json',{'counts':dict(counts),'records':records})
    if native['verified']:complete=False;break
   if not complete:break
  if not complete:break
 dump(out/'report.json',{'scope':__doc__,'complete':complete,'seconds':time.monotonic()-start,'counts':dict(counts),'records':records});(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'complete':complete,'seconds':time.monotonic()-start,'counts':dict(counts),'passes':[q['case'] for q in records if q.get('native',{}).get('verified')]}))
if __name__=='__main__':main()
