"""Co-design X1<=6 and a forward H0/X1 gate under a T1 source lower bound.

Keeps accepted59 G0/T0/X0/H2/G2 hardware; regenerates only X1 glue.
All three G0 normals remain on X1; ordinary T1 source connector bound<=6
is necessary only. New gate has supplied H0 drive/T1 pushes, not closure.
"""
import os as _research_os
import argparse,copy,itertools,json,subprocess,time
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer,body_of
from fastflyer import Block,Kind
from search_H0_X1_stone_gate import add,dump,push_connector_bound,ledger
from search_T1_two_pushes import connectivity_roots,adj,dist
from search_T1_pull_routes import offsets
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
TRANS=[(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]

def gate_supports(stone,d,transverse):
 sticky=add(add(stone,(-1,0,0)),d)
 if transverse:
  for di,u in enumerate(TRANS,2):
   if sum(x*y for x,y in zip(d,u)):continue
   # Observer output is P-X; the diagonal side support A-u holds both
   # actors without occupying the output or the sticky -X head corridor.
   obs=add(add(stone,(-1,0,0)),tuple(-v for v in u))
   yield obs,sticky,[add(sticky,tuple(-v for v in u))],di
 else:
  obs=add(stone,(-2,0,0))
  for e in TRANS:
   if sum(x*y for x,y in zip(d,e)):continue
   yield obs,sticky,[add(obs,e),add(add(obs,e),(1,0,0)),add(sticky,e)],0

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--seconds',type=float,default=110);ap.add_argument('--cp-seconds',type=float,default=.5);ap.add_argument('--only-indices',nargs='+',type=int);ap.add_argument('--transverse-observer',action='store_true');ap.add_argument('--X1-glue',type=int,choices=[5,6],default=6);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();ledger(a.out)
 f=Flyer.load(a.base/'problem.flyer');contract=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'));xp=next(p for p in contract['ports'] if p['name']=='X1_front');old=body_of(f._cells,tuple(xp['at']));fixed=set(f._cells)-old;motors={(16,4,11),(16,4,13),(16,5,12)}
 others=[(body_of(f._cells,tuple(p['at'])),f._cells[tuple(p['at'])].kind,p['word']) for p in contract['ports'] if p['name']!='X1_front']
 g0_shape=body_of(f._cells,tuple(next(p['at'] for p in contract['ports'] if p['name']=='G0')))
 g0_opening=g0_shape|{(17,4,12),(17,3,13),(17,5,10)}
 domain=list(itertools.product(range(12,23),range(0,9),range(8,18)));bounds={};choices=[];rejected={};records=[];passed=None;tests=0
 for stone in itertools.product(range(15,21),range(1,8),range(9,16)):
  for d in TRANS:
   q=add(add(stone,(-3,0,0)),d)
   if q not in bounds:bounds[q]=push_connector_bound(q)
   if not bounds[q]['survivors']:rejected['source_bound']=rejected.get('source_bound',0)+1;continue
   # Witness459: waiting X1 stone at P+X must not join G0's first move1.
   if any(dist(add(stone,(1,0,0)),p)<=1 for p in g0_shape):continue
   for obs,sticky,hs,di in gate_supports(stone,d,a.transverse_observer):
    sites={stone,obs,sticky,q,*hs}
    if len(sites)!=4+len(hs) or sites&fixed:continue
    if any(add(p,(1,0,0)) in g0_opening for p in [obs,sticky,*hs]):continue
    for hk,tk in [(Kind.HONEY,Kind.SLIME),(Kind.SLIME,Kind.HONEY)]:
     if any(hk==mat and any(dist(add(p,(k,0,0)),v)<=1 for k in offsets('mmwwm',word) for p in hs for v in sh) for sh,mat,word in others):continue
     if any(tk==mat and any(dist(add(q,(k,0,0)),v)<=1 for k in offsets('wmmmw',word) for v in sh) for sh,mat,word in others):continue
     # Witness593: X0 acquires the H0 sticky before H0 moves0. Protect
     # initial H0 hardware ownership from every existing foreign glue body.
     if any(dist(v,hw)<=1 for sh,_,_ in others for v in sh for hw in (obs,sticky)):continue
     choices.append((stone,obs,sticky,q,hs,hk,tk,di))
 choices.sort(key=lambda r:(bounds[r[3]]['minimum_pairwise_T1_glue_lower_bound'],sum(min(dist(v,m) for m in motors) for v in [r[0],r[3]]),r[0],r[3]))
 dump(a.out/'domain.json',{'choices':len(choices),'pre_rejections':rejected,'scope':__doc__});(a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
 for index,(stone,obs,sticky,q,hs,hk,tk,di) in enumerate(choices):
  if a.only_indices is not None and index not in a.only_indices:continue
  if time.monotonic()-start>a.seconds:break
  blocked=fixed|{stone,obs,sticky,q,*hs};model=cp_model.CpModel();cells={p:model.NewBoolVar(str(p)) for p in domain if p not in blocked and all(dist(p,m)<=a.X1_glue for m in motors) and dist(p,stone)<=a.X1_glue}
  model.Add(sum(cells.values())<=a.X1_glue);roots=connectivity_roots(model,cells,set().union(*(set(adj(m)) for m in motors)),a.X1_glue)
  for motor in motors:model.Add(sum(cells[p] for p in adj(motor) if p in cells)>=1)
  model.Add(sum(cells[p] for p in adj(stone) if p in cells)>=1)
  for p,v in cells.items():
   if any(dist(p,hw)<=1 for hw in (obs,sticky)):model.Add(v==0)
   # Witness603: X1 moves0 while G0 waits; it must not push directly into
   # waiting G0 glue (e.g. X1 17,4,11 -> G0 honey18,4,11).
   if add(p,(1,0,0)) in g0_shape:model.Add(v==0)
   if any(mat==Kind.SLIME and any(dist(add(p,(k,0,0)),vv)<=1 for k in offsets('mwwmm',word) for vv in sh) for sh,mat,word in others):model.Add(v==0)
   if hk==Kind.SLIME and any(dist(add(p,(k,0,0)),vv)<=1 for k in offsets('mwwmm','mmwwm') for vv in hs):model.Add(v==0)
   if tk==Kind.SLIME and any(dist(add(p,(k,0,0)),q)<=1 for k in offsets('mwwmm','wmmmw')):model.Add(v==0)
   # G0 waits0. Avoid forward obstruction into its RB/two pulse observers.
   if p in {(16,4,12),(16,3,13),(16,5,10)}:model.Add(v==0)
  model.Minimize(sum(cells.values()));solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=min(a.cp_seconds,max(.01,a.seconds-(time.monotonic()-start)));solver.parameters.num_search_workers=2;status=solver.Solve(model)
  rec={'index':index,'status':solver.StatusName(status),'seconds':solver.WallTime(),'stone':stone,'observer':obs,'direction':di,'sticky':sticky,'T1_root':q,'H0_shape':hs,'H0_kind':hk.name,'T1_kind':tk.name,'X1_glue_cap':a.X1_glue,'T1_source_pairwise_lower_bound':bounds[q]['minimum_pairwise_T1_glue_lower_bound']}
  if status in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
   shape=sorted(p for p,v in cells.items() if solver.Value(v));root=next(p for p,v in roots.items() if solver.Value(v));case=a.out/f'case{index:03}';case.mkdir();ff=Flyer.load(a.base/'problem.flyer')
   for p in old:ff.remove(p)
   for p,b in [*[(p,Block(Kind.SLIME)) for p in shape],*[(p,Block(hk)) for p in hs],(stone,Block(Kind.SMOOTH_STONE)),(obs,Block.observer(di,powered=False)),(sticky,Block.piston(1,sticky=True)),(q,Block(tk))]:assert p not in ff._cells;ff.set(p,b)
   ff.save(case/'problem.flyer');loaded=Flyer.load(case/'problem.flyer');assert loaded._cells==ff._cells and loaded._piston_blocks==ff._piston_blocks
   cc=copy.deepcopy(contract);next(p for p in cc['ports'] if p['name']=='X1_front')['at']=list(root);next(p for p in cc['ports'] if p['name']=='T1_front')['name']='X2_front'
   cc['ports'] += [{'name':'H0_front','at':list(hs[0]),'word':'mmwwm','role':'input','provenance':['supplied','supplied',None,None,'supplied']},{'name':'T1_front','at':list(q),'word':'wmmmw','role':'input','provenance':[None,'supplied','supplied','internal',None]}]
   cc['name']=case.name;cc['boundary_envelope']={'min':[0,0,0],'max':[40,20,30]};rows=[]
   for p in cc['ports']:
    for cy in range(3):
     for slot,v in enumerate(p['provenance']):
      if v=='supplied':rows.append((10*cy+2*slot,p['at'][0]+3*cy+p['word'][:slot].count('m'),*p['at'][1:],12))
   (case/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
   for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
   rec['X1_shape']=shape;rec['X1_anchor']=root;dump(case/'preparation.json',rec);dump(case/'T1_push_connector_bound.json',bounds[q]);tests+=1
   subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,capture_output=True,check=False);rec['native']=json.loads((case/'native.json').read_text(encoding='utf-8'))
   if rec['native']['verified']:passed=str(case)
  records.append(rec);dump(a.out/'report.json',{'scope':__doc__,'choices':len(choices),'records':records,'tests':tests,'passed':passed,'seconds':time.monotonic()-start})
  if passed:break
 dump(a.out/'report.json',{'scope':__doc__,'choices':len(choices),'records':records,'tests':tests,'passed':passed,'seconds':time.monotonic()-start});print(json.dumps({'models':len(records),'choices':len(choices),'tests':tests,'passed':passed,'seconds':time.monotonic()-start}),flush=True)
if __name__=='__main__':main()
