"""Budgeted G1 push4 integration: preserve supplied push0/pull1; no complete-flyer claim."""
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
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=90);ap.add_argument('--max-native',type=int,default=8);a=ap.parse_args();start=time.monotonic()
 base=HERE/'out/quarter_ring_contacts/H0_pulse_cross_power_dir0/case002';out=HERE/'out/quarter_ring_contacts/G1_late_push_search';out.mkdir(exist_ok=False);f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'));ports={p['name']:p for p in c['ports']};root=tuple(ports['G1_front']['at']);old=body_of(f._cells,root);fixed=set(f._cells)-old;others=[(name,body_of(f._cells,tuple(p['at'])),f._cells[tuple(p['at'])].kind,p['word']) for name,p in ports.items() if name!='G1_front']
 budget=json.loads((base/'whole39_source_budget.json').read_text(encoding='utf-8'));action=next(q for q in budget['actions'] if q['target']=='G1_power' and q['slot']==4);assert action['kind']=='push' and action['piston_word']=='wmmmw';assert budget['source_allocation']['G1_power']['mass']==8
 # G1 is push0, PULL1, push4. Reusing a three-push mmwwm driver would change roles.
 assert [(q['slot'],q['kind']) for q in budget['actions'] if q['target']=='G1_power']==[(0,'push'),(1,'pull'),(4,'push')]
 support=None;tshape=body_of(f._cells,tuple(ports['T1_front']['at']))
 for s in [1,2,3]:
  dx='wmmmw'[:s].count('m')-action['piston_word'][:s].count('m');ss={n for q in tshape for n in adj(add(q,(dx,0,0)))};support=ss if support is None else support&ss
 records=[];tests=0;counts=collections.Counter();complete=True
 for motor in sorted(support):
  for d in D[2:]:
   rb=add(add(motor,(1,0,0)),tuple(-v for v in d));head=add(motor,(1,0,0));hardware={motor,head,rb};pins=old|{add(motor,(2,0,0))}
   if hardware&fixed or hardware&pins or pins&fixed or len(hardware)!=3:counts['occupied']+=1;continue
   if any(dist(x,y)>4 for x in pins for y in pins):counts['terminal_diameter']+=1;continue
   ranges=[range(max(q[k] for q in pins)-4,min(q[k] for q in pins)+5) for k in range(3)];domain={q for q in itertools.product(*ranges) if q not in fixed|hardware and all(dist(q,p)<=4 for p in pins) and all(dist(x,q)+dist(q,y)+dist(x,y)<=8 for x in pins for y in pins)}
   for mat in [Kind.HONEY,Kind.SLIME]:
    if time.monotonic()-start>a.seconds or tests>=a.max_native:complete=False;break
    rec={'motor':motor,'RB':rb,'head':head,'material':mat.name}
    # New source must not be stolen by stationary G1's foreign movers.
    witness=next(({'body':name,'slot':s,'glue':q} for name,shape,_,word in others for q in shape for s in [2,3] if word[s]=='m' and dist(add(rb,(2,0,0)),add(q,(word[:s].count('m'),0,0)))<=1),None)
    if witness:counts['RB_foreign_carrier']+=1;records.append({**rec,'status':'RB_foreign_carrier','witness':witness});continue
    cells={q for q in domain if not any(any(dist(add(q,(k,0,0)),p)<=(1 if mat==kind else 0) for k in offsets('mmwwm',word) for p in shape) for _,shape,kind,word in others)}
    if not pins<=cells:counts['mandatory_excluded']+=1;continue
    model=cp_model.CpModel();v={q:model.NewBoolVar(str(q)) for q in cells}
    for q in pins:model.Add(v[q]==1)
    model.Add(sum(v[q] for q in adj(rb) if q in v)>=1);model.Add(sum(v.values())<=5);connectivity(model,v,root,5);model.Minimize(sum(v.values()));solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=.4;solver.parameters.num_search_workers=2;status=solver.Solve(model)
    if status not in [cp_model.OPTIMAL,cp_model.FEASIBLE]:counts[solver.StatusName(status)]+=1;records.append({**rec,'status':solver.StatusName(status)});continue
    shape=sorted(q for q,b in v.items() if solver.Value(b));case=out/f'case{tests:03}';case.mkdir();tests+=1;ff=Flyer.load(base/'problem.flyer')
    for q in old:ff.remove(q)
    for q in shape:assert q not in ff._cells;ff.set(q,Block(mat))
    for q,b in [(rb,Block(Kind.REDSTONE_BLOCK)),(motor,Block.piston(0,state=2)),(head,Block(Kind.PISTON_ARM))]:assert q not in ff._cells;ff.set(q,b)
    ff.set_piston_blocks(motor,[head]);canonical=ff.canonicalize();delta=tuple(min(q[k] for q in canonical._cells)-min(q[k] for q in ff._cells) for k in range(3));canonical.save(case/'problem.flyer');loaded=Flyer.load(case/'problem.flyer');assert loaded._cells==canonical._cells and loaded._piston_blocks==canonical._piston_blocks
    cc=json.loads(json.dumps(c));cc['name']=case.name;cc['boundary_envelope']={'min':[0,0,0],'max':[100,100,100]};rows=[]
    for p in cc['ports']:
     p['at']=[x+delta[k] for k,x in enumerate(p['at'])]
     if p['name']=='G1_front':p['provenance']=['supplied','supplied',None,None,'internal']
     for cy in range(3):
      for s,source in enumerate(p['provenance']):
       if source=='supplied':rows.append((10*cy+2*s,p['at'][0]+3*cy+p['word'][:s].count('m'),*p['at'][1:],12))
    (case/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
    for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
    dump(case/'preparation.json',{'scope':__doc__+' Sixteen natural/fourteen supplied strokes attempted.','source_record':rec,'G1_shape':shape,'normalization_delta':delta,'base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest(),'budget':'G1 five glue+stone+RB+future observer=8; full39 mass unchanged.'})
    subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,check=False,stdout=subprocess.DEVNULL,timeout=40);native=json.loads((case/'native.json').read_text(encoding='utf-8'));records.append({**rec,'case':str(case),'shape':shape,'native':native});counts['native_pass' if native['verified'] else 'native_fail']+=1;dump(out/'progress.json',{'counts':dict(counts),'records':records})
    if native['verified']:complete=False;break
   if not complete:break
  if not complete:break
 dump(out/'report.json',{'scope':__doc__,'complete':complete,'seconds':time.monotonic()-start,'counts':dict(counts),'records':records});(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'complete':complete,'seconds':time.monotonic()-start,'counts':dict(counts),'passes':[r['case'] for r in records if r.get('native',{}).get('verified')]}))
if __name__=='__main__':main()
