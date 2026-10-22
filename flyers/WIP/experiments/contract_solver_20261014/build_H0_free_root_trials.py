"""Construct bounded H0 dual-RB integrations from root-free support survivors; native decides."""
import argparse,itertools,json,subprocess,time,hashlib
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
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=90);ap.add_argument('--max-native',type=int,default=8);ap.add_argument('--source',default='H0_free_root_preflight');ap.add_argument('--out',default='H0_free_root_native_trials');ap.add_argument('--preserve-parent-passengers',action='store_true');ap.add_argument('--protect-RB-carriers',action='store_true');ap.add_argument('--pulse-first-source',action='store_true');ap.add_argument('--observer-direction',type=int,choices=range(6),default=1);ap.add_argument('--avoid-source-cross-power',action='store_true');a=ap.parse_args();start=time.monotonic()
 base=HERE/'out/quarter_ring_contacts/T1_sticky_on_G1_transfer';report=HERE/'out/quarter_ring_contacts'/a.source/'report.json';out=HERE/'out/quarter_ring_contacts'/a.out;out.mkdir(exist_ok=False)
 f=Flyer.load(base/'problem.flyer');contract=json.loads((base/'before_natural.json').read_text(encoding='utf-8'));ports={p['name']:p for p in contract['ports']};old=body_of(f._cells,tuple(ports['H0_front']['at']));fixed=set(f._cells)-old
 others=[(body_of(f._cells,tuple(p['at'])),f._cells[tuple(p['at'])].kind,p['word']) for name,p in ports.items() if name!='H0_front'];recs=[];tests=0
 passengers=[]
 if a.preserve_parent_passengers:
  sweep=json.loads((HERE/'out/quarter_ring_contacts/H0_passenger_sweeps/report.json').read_text(encoding='utf-8'))['records'];origins={tuple(q['origin']) for q in sweep}
  for origin in sorted(origins):
   if f._cells[origin].kind not in [Kind.OBSERVER,Kind.REDSTONE_BLOCK]:continue
   words=[''.join('m' if any(tuple(q['origin'])==origin and q['order']==order and q['slot']==s for q in sweep) else 'w' for s in range(5)) for order in ['before','after','interleaved']]
   if len(set(words))==1:passengers.append((origin,words[0]))
 candidates=[r for r in json.loads(report.read_text(encoding='utf-8'))['records'] if r['status']=='survivor'];candidates.sort(key=lambda r:(r['minimum'],r['motors'],r['RBs'],r['material']))
 for i,r in enumerate(candidates):
  if time.monotonic()-start>a.seconds or tests>=a.max_native:break
  pins={tuple(p) for p in r['pins']};RBs=[tuple(p) for p in r['RBs']];motors=[tuple(p) for p in r['motors']];head=tuple(r['head']);hardware=set(RBs+motors+[head]);mat=Kind[r['material']]
  observer=add(RBs[0],tuple(-v for v in D[a.observer_direction])) if a.pulse_first_source else None;cap=7 if a.pulse_first_source else 8
  if observer is not None:
   if observer in fixed|hardware|pins:recs.append({'index':i,'status':'pulse_observer_occupied'});continue
   hardware.add(observer)
  if a.avoid_source_cross_power:
   forbidden=[];pwords=['wwmmm','mwwmm','wmmmw']
   for k,slots in [(0,[2,3,4]),(1,[3,4])]:
    for s in slots:
     source=add(RBs[1],('mmwwm'[:s].count('m'),0,0));motor=add(motors[k],(pwords[k][:s].count('m'),0,0))
     if dist(source,motor)==1 and source!=add(motor,(1,0,0)):forbidden.append({'source':source,'motor':k,'slot':s,'kind':'late_RB_powers_early_motor'})
   if a.pulse_first_source:
    for s in [1,2]:
     stone=add(RBs[0],('mmwwm'[:s].count('m'),0,0));motor=add(motors[2],(pwords[2][:s].count('m'),0,0))
     if dist(stone,motor)==1 and stone!=add(motor,(1,0,0)):forbidden.append({'source':stone,'motor':2,'slot':s,'kind':'early_pulse_powers_late_motor'})
   if forbidden:recs.append({'index':i,'status':'source_cross_power_excluded','witness':forbidden});continue
  if a.protect_RB_carriers:
   witness=next(({'RB':rb,'foreign_glue':q,'slot':s,'foreign_word':word,'reason':'foreign_glue_recruits_stationary_source'} for rb in RBs for shape,_,word in others for q in shape for s in range(5) if 'mmwwm'[s]=='w' and word[s]=='m' and dist(add(rb,('mmwwm'[:s].count('m'),0,0)),add(q,(word[:s].count('m'),0,0)))<=1),None)
   if witness:recs.append({'index':i,'status':'RB_foreign_carrier_excluded','witness':witness});continue
  ranges=[range(max(p[k] for p in pins)-7,min(p[k] for p in pins)+8) for k in range(3)]
  domain={q for q in itertools.product(*ranges) if q not in fixed|hardware and all(dist(q,p)<=7 for p in pins) and all(dist(x,q)+dist(q,y)+dist(x,y)<=14 for x in pins for y in pins)}
  domain={q for q in domain if not any(any(dist(add(q,(k,0,0)),v)<=(1 if mat==kind else 0) for k in offsets('mmwwm',word) for v in shape) for shape,kind,word in others)}
  # These movable ordinary passengers adhere to either glue kind. A different
  # word requires separation whenever H0 moves and the passenger stays put.
  domain={q for q in domain if not any(any(dist(add(q,('mmwwm'[:s].count('m'),0,0)),add(p,(word[:s].count('m'),0,0)))<=1 for s in range(5) if 'mmwwm'[s]=='m' and word[s]=='w') for p,word in passengers)}
  if not pins<=domain:recs.append({'index':i,'status':'passenger_mandatory_excluded'});continue
  model=cp_model.CpModel();cells={q:model.NewBoolVar(str(q)) for q in domain};root=min(pins)
  for q in pins:model.Add(cells[q]==1)
  for rb in RBs:model.Add(sum(cells[q] for q in adj(rb) if q in cells)>=1)
  if observer is not None:model.Add(sum(cells[q] for q in adj(observer) if q in cells)>=1)
  model.Add(sum(cells.values())<=cap);connectivity(model,cells,root,cap);model.Minimize(sum(cells.values()));solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=1;solver.parameters.num_search_workers=2;status=solver.Solve(model)
  if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):recs.append({'index':i,'status':solver.StatusName(status)});continue
  shape=sorted(q for q,v in cells.items() if solver.Value(v));case=out/f'case{tests:03}';case.mkdir();tests+=1;ff=Flyer.load(base/'problem.flyer')
  for q in old:ff.remove(q)
  for q in shape:assert q not in ff._cells;ff.set(q,Block(mat))
  sources=[(RBs[0],Block(Kind.SMOOTH_STONE if a.pulse_first_source else Kind.REDSTONE_BLOCK)),(RBs[1],Block(Kind.REDSTONE_BLOCK))]
  if observer is not None:sources.append((observer,Block.observer(a.observer_direction,powered=True)))
  for q,b in sources+[(motors[0],Block.piston(0)),(motors[1],Block.piston(0)),(motors[2],Block.piston(0,state=2)),(head,Block(Kind.PISTON_ARM))]:assert q not in ff._cells;ff.set(q,b)
  ff.set_piston_blocks(motors[2],[head]);canonical=ff.canonicalize();delta=tuple(min(q[k] for q in canonical._cells)-min(q[k] for q in ff._cells) for k in range(3));canonical.save(case/'problem.flyer');loaded=Flyer.load(case/'problem.flyer');assert loaded._cells==canonical._cells and loaded._piston_blocks==canonical._piston_blocks
  cc=json.loads(json.dumps(contract));cc['name']=case.name;cc['boundary_envelope']={'min':[0,0,0],'max':[100,100,100]};rows=[]
  for p in cc['ports']:
   at=root if p['name']=='H0_front' else tuple(p['at']);p['at']=[v+delta[k] for k,v in enumerate(at)]
   if p['name']=='H0_front':p['provenance']=['internal','internal',None,None,'internal']
   for cy in range(3):
    for t,v in enumerate(p['provenance']):
     if v=='supplied':rows.append((10*cy+2*t,p['at'][0]+3*cy+p['word'][:t].count('m'),*p['at'][1:],12))
  (case/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
  for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
  prep={'scope':__doc__+' Fifteen natural/fifteen supplied strokes attempted; not complete flyer.','avoid_source_cross_power':a.avoid_source_cross_power,'observer_direction':a.observer_direction,'pulse_first_source':a.pulse_first_source,'pulse_observer':observer,'glue_cap':cap,'protect_RB_carriers':a.protect_RB_carriers,'preserve_parent_passengers':a.preserve_parent_passengers,'passenger_words':passengers,'source_record':r,'H0_shape':shape,'normalization_delta':delta,'base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest()};dump(case/'preparation.json',prep)
  subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,check=False,stdout=subprocess.DEVNULL,timeout=40)
  native=json.loads((case/'native.json').read_text(encoding='utf-8'));rec={'index':i,'case':str(case),'shape':shape,'native':native};recs.append(rec);dump(out/'progress.json',{'seconds':time.monotonic()-start,'records':recs})
  if native['verified']:break
 dump(out/'report.json',{'scope':__doc__,'seconds':time.monotonic()-start,'records':recs});(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'seconds':time.monotonic()-start,'native_trials':tests,'passes':[r['case'] for r in recs if r.get('native',{}).get('verified')]}))
if __name__=='__main__':main()
