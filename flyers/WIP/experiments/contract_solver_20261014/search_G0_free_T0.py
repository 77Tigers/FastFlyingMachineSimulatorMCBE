"""Regenerate T0 source, own normals and glue around an actual G0/H0 macro.

Free the source corner implicated by the rigid-placement screen. T0 first
normal follows mmmww, late wmmmw; X0 supplies their initial pickups. CP-SAT
only finds connected glue<=7 and required contacts. Strict native tests at
PL12 reject wrong timing, power, passenger loads or foreign interactions.
Only X0 pushes0/1 remain supplied in a passing component, not a full flyer.
"""
import os as _research_os
import argparse,hashlib,itertools,json,subprocess,time
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer
from fastflyer import Block,Kind
from model_recovery_layout import connectivity

ROOT=Path(__file__).resolve().parents[4]
D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
POWER=[(-1,0,0),*D[2:]]
OLD={(17,1,12),(17,1,13),(17,2,13),(17,3,13),(17,0,13),(18,3,13),
     (16,1,13),(14,2,13),(15,0,13),(16,0,13)}
X0={(14,2,10),(14,2,11),(14,2,12),(14,3,11),(14,1,12),(14,0,12),(14,1,11)}


def add(p,q):return tuple(x+y for x,y in zip(p,q))
def near(p,q):return sum(abs(x-y) for x,y in zip(p,q))==1


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base',type=Path);ap.add_argument('macro',type=Path);ap.add_argument('out',type=Path)
    ap.add_argument('--seconds',type=float,default=180);ap.add_argument('--max-tests',type=int,default=24)
    ap.add_argument('--max-models',type=int,default=1000)
    ap.add_argument('--cp-seconds',type=float,default=2)
    ap.add_argument('--rear-pickup-budget',action='store_true',help='Target <=12 pull0 loads including the observed stationary X1 normal passenger; this is a bounded carrier hypothesis, not a universal exclusion.')
    ap.add_argument('--separate-macro-glue',action='store_true',help='Keep unflipped G0 honey separate from T0 honey before G0 move1; target the observed cross-body merge.')
    ap.add_argument('--clear-x0-sweeps',action='store_true',help='Exclude initial extended-actor blockers and target source allocations without the witnessed X0 pull2/RB obstruction; not a bound on alternative carrier allocations.')
    ap.add_argument('--macro-index',type=int,help='Test just one indexed calibrated macro placement.')
    ap.add_argument('--carry-t1-normal',action='store_true',help='Preserve the accepted T0 move0 transport of normal17,2,12; otherwise it remains in X0 pull2 path and misses its next carrier.')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    f=Flyer.load(a.base/'problem.flyer');fixed=set(f._cells)-OLD
    macros=json.loads(a.macro.read_text(encoding='utf-8'))['results']
    firsts={add(g,d) for g in X0 for d in D}-fixed
    choices=[];sweep_rejections=0
    for first in sorted(firsts):
      for off in POWER:
       rb=add(add(first,(2,0,0)),off)
       for off2 in POWER:
        late=add(rb,(-1-off2[0],-off2[1],-off2[2]));arm=add(late,(1,0,0))
        actors={first,rb,late,arm}
        if len(actors)!=4 or actors&fixed:continue
        if a.clear_x0_sweeps:
            # Before-natural X0 move0 cannot move into an extended piston/arm.
            # At pull2 X0's target destination is glue+3, T0 RB is rb+1.
            # Avoid source cargo in this witnessed lane; other reallocations
            # are outside this explicitly separated-carrier hypothesis.
            if {late,arm}&{add(g,(1,0,0)) for g in X0} or rb in {add(g,(2,0,0)) for g in X0}:
                sweep_rejections+=1;continue
        if not any(near(late,add(g,(1,0,0))) for g in X0):continue
        qfirst=add(first,(3,0,0));qlate=add(late,(2,0,0))
        if {qfirst,qlate}&(fixed|actors):continue
        choices.append((first,late,rb,qfirst,qlate))
    assert any(c[:3]==((14,2,13),(15,0,13),(16,1,13)) for c in choices)
    choices.sort(key=lambda c:(sum(abs(x-y) for x,y in zip(c[2],(16,1,13))),c))
    results=[];models=0;complete=True;statuses={};model_records=[]
    def remaining():return a.seconds-(time.monotonic()-start)
    for mi,m in enumerate(macros):
      if a.macro_index is not None and mi!=a.macro_index:continue
      cells={tuple(c[:3]):c[3] for c in m['macro_cells']}
      if cells.keys()&fixed:continue
      for first,late,rb,qfirst,qlate in choices:
       if remaining()<=0 or models>=a.max_models or len(results)>=a.max_tests:complete=False;break
       actors={first,late,rb,add(late,(1,0,0))};targets={tuple(m['target']),qfirst,qlate}
       if actors&cells.keys() or targets&(fixed|actors|cells.keys()):continue
       model=cp_model.CpModel();blocked=fixed|actors|cells.keys()
       root=tuple(m['target'])
       distance=lambda p,q:sum(abs(x-y) for x,y in zip(p,q))
       # Any selected cell belongs to a <=6-edge connected tree containing
       # every target. The three-terminal L1 tree lower bound cannot exceed6.
       gs={p:model.NewBoolVar(str(p)) for x in range(13,21) for y in range(-2,6) for z in range(9,16)
           if (p:=(x,y,z)) not in blocked and all(distance(root,p)+distance(p,t)+distance(root,t)<=12 for t in targets)}
       if not targets<=gs.keys():continue
       if a.separate_macro_glue:
        # T0 has moved0, G0 has not yet moved1. case020 showed that
        # honey contact at this phase recruits the entire stationary T0.
        g0={p for p,v in cells.items() if v&15==int(Kind.HONEY)}
        for p,var in gs.items():
            if any(near(add(p,(1,0,0)),g) for g in g0):model.Add(var==0)
       if a.clear_x0_sweeps:
        # Keep T0 glue out of the whole X0 assembly's pull2 destinations,
        # including its two carried T0 normals and two fixed X1 normals.
        # T0 glue has prefix1, first normal prefix2, late prefix1.
        lanes={add(g,(2,0,0)) for g in X0}|{add(first,(2,0,0)),add(late,(1,0,0)),(16,3,10),(16,4,11)}
        for p in lanes:
            if p in gs:model.Add(gs[p]==0)
       for p in targets:model.Add(gs[p]==1)
       model.Add(sum(gs.values())<=7)
       required=[rb,(17,1,11),*map(tuple,m['G0_normals_at_initial'])]
       if any(not any(add(p,d) in gs for d in D) for p in required):continue
       for p in required:model.Add(sum(gs[add(p,d)] for d in D if add(p,d) in gs)>=1)
       if a.carry_t1_normal:
        touches=[gs[add((17,2,12),d)] for d in D if add((17,2,12),d) in gs]
        if not touches:continue
        model.Add(sum(touches)>=1)
       if a.rear_pickup_budget:
        # case002 pull0 discovers >=13: 7 glue, RB, X0 sticky, 3 G0
        # normals and the pre-existing X1 normal at (17,2,12).
        # Preserve that observed stationary-pickup allocation and budget it.
        # Other power/immobility/reallocation hypotheses remain unsearched.
        riders=[]
        for origin in [(17,2,12),(17,2,10)]:
            # Both stationary passengers have exact native identity witnesses.
            rider=model.NewBoolVar(f'foreign_normal_{origin}')
            touches=[gs[add(origin,d)] for d in D if add(origin,d) in gs]
            if touches:model.AddMaxEquality(rider,touches)
            else:model.Add(rider==0)
            riders.append(rider)
        model.Add(sum(gs.values())+sum(riders)<=7)
       connectivity(model,gs,tuple(m['target']),7)
       model.Minimize(sum(gs.values()))
       solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=min(a.cp_seconds,max(0.01,remaining()))
       solver.parameters.num_search_workers=1
       solved=solver.Solve(model);models+=1;key=solver.StatusName(solved);statuses[key]=statuses.get(key,0)+1
       model_records.append({'macro':mi,'first':first,'late':late,'RB':rb,'status':key})
       if solved not in (cp_model.OPTIMAL,cp_model.FEASIBLE):continue
       shape={p for p,v in gs.items() if solver.Value(v)}
       for flip in ([False] if a.separate_macro_glue else [False,True]):
        if remaining()<=0 or len(results)>=a.max_tests:complete=False;break
        out=a.out/f'case{len(results):03d}';out.mkdir()
        ff=Flyer.load(a.base/'problem.flyer')
        for p in OLD:ff._cells.pop(p)
        for p in shape:ff.set(p,Block(Kind.HONEY))
        ff.set(rb,Block(Kind.REDSTONE_BLOCK));ff.set(first,Block.piston(0));ff.set(late,Block.piston(0,state=2));ff.set(add(late,(1,0,0)),Block(Kind.PISTON_ARM))
        for p,value in cells.items():
            b=Block.decode(value)
            if flip and b.kind in (Kind.SLIME,Kind.HONEY):b=Block(Kind.HONEY if b.kind==Kind.SLIME else Kind.SLIME)
            ff.set(p,b)
        owned={}
        for owner,block in m['macro_owners']:owned.setdefault(tuple(owner),[]).append(tuple(block))
        for owner,blocks in owned.items():ff.set_piston_blocks(owner,blocks)
        ff.save(out/'problem.flyer');loaded=Flyer.load(out/'problem.flyer')
        delta=tuple(min(p[k] for p in loaded._cells)-min(p[k] for p in ff._cells) for k in range(3))
        assert loaded._cells=={add(p,delta):b for p,b in ff._cells.items()}
        old=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'));tp=next(p for p in old['ports'] if p['name']=='T0')
        remove={(10*cy,tp['at'][0]+3*cy,tp['at'][1],tp['at'][2]) for cy in range(3)}
        rows=[tuple(map(int,s.split())) for s in (a.base/'drive.txt').read_text(encoding='utf-8').splitlines()]
        assert sum(row[:4] in remove for row in rows)==3
        (out/'drive.txt').write_text(''.join(' '.join(map(str,(row[0],*add(row[1:4],delta),row[4])))+'\n' for row in rows if row[:4] not in remove),encoding='utf-8')
        for order in ('before_natural','after_natural','interleaved'):
            c=json.loads((a.base/f'{order}.json').read_text(encoding='utf-8'));c['name']=out.name
            tp=next(p for p in c['ports'] if p['name']=='T0');tp['at']=m['target'];tp['provenance'][0]='internal'
            for name,kind,word in [('G0',2,'wmmmw'),('H0',1,'mmwwm')]:
                at=next(p for p,v in cells.items() if v&15==kind)
                c['ports'].append({'name':name,'at':at,'role':'input','word':word,'provenance':['internal' if ch=='m' else None for ch in word]})
            for axis in range(3):
                c['boundary_envelope']['min'][axis]=min(c['boundary_envelope']['min'][axis],min(p[axis] for p in ff._cells))
                c['boundary_envelope']['max'][axis]=max(c['boundary_envelope']['max'][axis],max(p[axis] for p in ff._cells))
            for port in c['ports']:port['at']=add(port['at'],delta)
            for side in ('min','max'):c['boundary_envelope'][side]=add(c['boundary_envelope'][side],delta)
            (out/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
        prep={'scope':__doc__,'base':str(a.base),'macro_index':mi,'flip':flip,'T0_glue':sorted(shape),'first':first,'late':late,'RB':rb,'normalization_delta':delta,
              'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.base/'problem.flyer',a.macro,Path(__file__)]}}
        (out/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n',encoding='utf-8')
        proc=subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(out/'before_natural.json'),str(out/'native.json'),str(max(1,min(30,remaining()))),'2'],cwd=ROOT,capture_output=True,text=True)
        assert (out/'native.json').exists(),proc.stderr
        result=json.loads((out/'native.json').read_text(encoding='utf-8'));results.append({'case':str(out),'macro':mi,'T0_glue':sorted(shape),**result})
        print(json.dumps({'case':len(results)-1,'verified':result['verified'],'failure':result['failure']}),flush=True)
        if result['verified']:complete=False;break
       if not complete:break
      if not complete:break
    report={'scope':__doc__,'complete':complete,'macro_index':a.macro_index,'clear_X0_sweeps':a.clear_x0_sweeps,'sweep_rejections':sweep_rejections,'own_column_choices':len(choices),'models':models,'statuses':statuses,'CP_seconds':a.cp_seconds,'three_terminal_distance_pruning':True,'rear_pickup_budget':a.rear_pickup_budget,'separate_macro_glue':a.separate_macro_glue,'native_cases':results,'elapsed_seconds':time.monotonic()-start}
    (a.out/'model_records.json').write_text(json.dumps(model_records,indent=2)+'\n',encoding='utf-8')
    (a.out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['native_cases','scope']}),flush=True)


if __name__=='__main__':main()
