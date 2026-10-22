"""Joint G1 first/late motor placement with one RB, cap5 glue, future observer reserved."""
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
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=80);ap.add_argument('--max-native',type=int,default=12);ap.add_argument('--out',default='G1_joint_shared_source');ap.add_argument('--control',choices=['none','omit-H0-motor','omit-passengers','omit-both'],default='none');a=ap.parse_args();start=time.monotonic()
 base=HERE/'out/quarter_ring_contacts/G1_late_push_search/case000';out=HERE/'out/quarter_ring_contacts'/a.out;out.mkdir(exist_ok=False);f=Flyer.load(base/'problem.flyer');c=json.loads((base/'before_natural.json').read_text(encoding='utf-8'));ports={p['name']:p for p in c['ports']};root=tuple(ports['G1_front']['at']);old=body_of(f._cells,root);remove=old|{(15,1,14),(16,1,14),(16,0,14)};fixed=set(f._cells)-remove;others=[(name,body_of(f._cells,tuple(p['at'])),f._cells[tuple(p['at'])].kind,p['word']) for name,p in ports.items() if name!='G1_front'];tshape=body_of(f._cells,tuple(ports['T1_front']['at']));support={}
 budget=json.loads((base/'whole39_source_budget.json').read_text(encoding='utf-8'));assert budget['permanent_masses']['G1_power']==8;assert [(q['slot'],q['kind']) for q in budget['actions'] if q['target']=='G1_power']==[(0,'push'),(1,'pull'),(4,'push')]
 for slot,pword,carry in [(0,'wwmmm',[2,3]),(4,'wmmmw',[1,2,3])]:
  ss=None
  for s in carry:
   dx='wmmmw'[:s].count('m')-pword[:s].count('m');choices={n for q in tshape for n in adj(add(q,(dx,0,0)))};ss=choices if ss is None else ss&choices
  support[slot]=ss
 trace=json.loads((base/'failure_audit_0_0_7_after.json').read_text(encoding='utf-8'));passengers=[]
 for p,b in f._cells.items():
  if b.kind not in [Kind.REDSTONE_BLOCK,Kind.OBSERVER] or p in remove:continue
  word=''.join('m' if any(q['tick']==2*s and any(v[4] is not None and tuple(v[4])==p for v in q['identities']) for q in trace['actions']) else 'w' for s in range(5));passengers.append((p,word))
 counts=collections.Counter();records=[];tests=0;complete=True;seen=set()
 for m0 in sorted(support[0]-fixed):
  for d0 in D[2:]:
   rb=add(m0,tuple(-v for v in d0))
   for d4 in D[2:]:
    if time.monotonic()-start>a.seconds or tests>=a.max_native:complete=False;break
    m4=add(add(rb,(-1,0,0)),d4);head=add(m4,(1,0,0));hardware={rb,m0,m4,head};pins={root,add(m0,(1,0,0)),add(m4,(2,0,0))};key=(rb,m0,m4)
    if key in seen:continue
    seen.add(key)
    if m4 not in support[4] or len(hardware)!=4 or hardware&fixed or hardware&pins or pins&fixed:counts['occupied_or_support']+=1;continue
    if any(dist(x,y)>4 for x in pins for y in pins):counts['diameter']+=1;continue
    witness=next(({'body':name,'slot':s,'glue':q} for name,shape,_,word in others for q in shape for s in [2,3] if word[s]=='m' and dist(add(rb,(2,0,0)),add(q,(word[:s].count('m'),0,0)))<=1),None)
    if witness:counts['foreign_RB_pickup']+=1;continue
    ranges=[range(max(q[k] for q in pins)-4,min(q[k] for q in pins)+5) for k in range(3)];domain={q for q in itertools.product(*ranges) if q not in fixed|hardware and all(dist(q,p)<=4 for p in pins) and all(dist(x,q)+dist(q,y)+dist(x,y)<=8 for x in pins for y in pins)}
    for mat in [Kind.HONEY,Kind.SLIME]:
     rec={'first_motor':m0,'late_motor':m4,'RB':rb,'head':head,'material':mat.name}
     cells={q for q in domain if not any(any(dist(add(q,(k,0,0)),p)<=(1 if kind==mat else 0) for k in offsets('mmwwm',word) for p in shape) for _,shape,kind,word in others)}
     glue_missing=sorted(pins-cells)
     if a.control not in ['omit-passengers','omit-both']:cells={q for q in cells if not any(any(dist(add(q,('mmwwm'[:s].count('m'),0,0)),add(p,(word[:s].count('m'),0,0)))<=1 for s in [0,1,4] if word[s]=='w') for p,word in passengers)}
     passenger_missing=sorted(pins-cells)
     # Learned H0 late-normal pickup on4; retain its validated carrier assignment.
     if a.control not in ['omit-H0-motor','omit-both']:cells={q for q in cells if dist(add(q,(2,0,0)),(19,3,15))>1}
     if not pins<=cells:counts['phase_mandatory']+=1;records.append({**rec,'status':'phase_mandatory','glue_missing':glue_missing,'passenger_missing':passenger_missing,'all_missing':sorted(pins-cells)});continue
     model=cp_model.CpModel();v={q:model.NewBoolVar(str(q)) for q in cells}
     for q in pins:model.Add(v[q]==1)
     for group in [adj(rb),adj((17,2,14))]:model.Add(sum(v[q] for q in group if q in v)>=1)
     model.Add(sum(v.values())<=5);connectivity(model,v,root,5);model.Minimize(sum(v.values()));solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=.3;solver.parameters.num_search_workers=2;status=solver.Solve(model)
     if status not in [cp_model.OPTIMAL,cp_model.FEASIBLE]:counts[solver.StatusName(status)]+=1;records.append({**rec,'status':solver.StatusName(status)});continue
     shape=sorted(q for q,b in v.items() if solver.Value(b));case=out/f'case{tests:03}';case.mkdir();tests+=1;ff=Flyer.load(base/'problem.flyer')
     if a.control!='none':counts['geometry_only_control']+=1;records.append({**rec,'status':'geometry_only_control','shape':shape,'minimum':len(shape) if status==cp_model.OPTIMAL else None});continue
     for q in remove:ff.remove(q)
     for q in shape:assert q not in ff._cells;ff.set(q,Block(mat))
     for q,b in [(rb,Block(Kind.REDSTONE_BLOCK)),(m0,Block.piston(0)),(m4,Block.piston(0,state=2)),(head,Block(Kind.PISTON_ARM))]:assert q not in ff._cells;ff.set(q,b)
     ff.set_piston_blocks(m4,[head]);canonical=ff.canonicalize();delta=tuple(min(q[k] for q in canonical._cells)-min(q[k] for q in ff._cells) for k in range(3));canonical.save(case/'problem.flyer');loaded=Flyer.load(case/'problem.flyer');assert loaded._cells==canonical._cells and loaded._piston_blocks==canonical._piston_blocks
     cc=json.loads(json.dumps(c));cc['name']=case.name;cc['boundary_envelope']={'min':[0,0,0],'max':[100,100,100]};rows=[]
     for p in cc['ports']:
      p['at']=[x+delta[k] for k,x in enumerate(p['at'])]
      if p['name']=='G1_front':p['provenance']=['internal','supplied',None,None,'internal']
      for cy in range(3):
       for s,source in enumerate(p['provenance']):
        if source=='supplied':rows.append((10*cy+2*s,p['at'][0]+3*cy+p['word'][:s].count('m'),*p['at'][1:],12))
     (case/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
     for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
     prep={'scope':__doc__+' Seventeen natural/thirteen supplied attempted; not complete flyer.','source_record':rec,'G1_shape':shape,'normalization_delta':delta,'base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest(),'budget':'G1 <=5glue+sharedRB+stone+future observer=8; all39 masses/roles/load sums unchanged.'};dump(case/'preparation.json',prep)
     subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,check=False,stdout=subprocess.DEVNULL,timeout=40);native=json.loads((case/'native.json').read_text(encoding='utf-8'));records.append({**rec,'shape':shape,'case':str(case),'native':native});counts['native_pass' if native['verified'] else 'native_fail']+=1;dump(out/'progress.json',{'counts':dict(counts),'records':records})
     if native['verified']:complete=False;break
    if not complete:break
   if not complete:break
  if not complete:break
 dump(out/'report.json',{'scope':__doc__+' Fixed-parent passenger cuts are conditional grammar restrictions, not global lower bounds. Controls never construct/native-test an invalid relaxation.','control':a.control,'complete':complete,'seconds':time.monotonic()-start,'counts':dict(counts),'records':records});(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'complete':complete,'seconds':time.monotonic()-start,'counts':dict(counts),'passes':[q['case'] for q in records if q.get('native',{}).get('verified')]}))
if __name__=='__main__':main()
