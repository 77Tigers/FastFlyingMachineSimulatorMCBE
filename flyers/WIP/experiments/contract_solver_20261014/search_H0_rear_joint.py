"""Bounded H0 motor rerowing and joint rear glue/contact construction.

Retain G0's six glue cells and sticky, regenerate H0 RB/three own normals,
<=8 H0 glue and <=8 rear glue. Add rear RB/two +X normals. A necessary
initial-contact CP model proposes layouts; strict native checking decides
physics. No negative result excludes changed G0/rear-root/carrier roles.
"""
import argparse,hashlib,itertools,json,subprocess,time
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer
from fastflyer import Block,Kind
from model_recovery_layout import connectivity
from screen_rear_motor_contacts import REAR,FRONT,adj,distance

ROOT=Path(__file__).resolve().parents[4]
G={(19,0,14),(19,1,13),(19,1,14),(19,2,14),(19,3,13),(19,3,14)}
OLD_ACTORS={(21,2,13),(21,1,13),(21,3,13),(20,2,14),(21,2,14)}
POWER=[(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
SOURCES=[(21,2,13),(20,1,13),(20,3,13),(20,2,12),(20,2,14)]
def add(p,d):return tuple(x+y for x,y in zip(p,d))
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    ap.add_argument('--seconds',type=float,default=180);ap.add_argument('--cp-seconds',type=float,default=5)
    ap.add_argument('--max-tests',type=int,default=12)
    ap.add_argument('--front-cap',type=int,default=8)
    ap.add_argument('--geometry-only',action='store_true')
    ap.add_argument('--relax-obstacles',action='store_true',help='Necessary obstacle-free relaxation; no native construction')
    ap.add_argument('--calibrate',action='store_true',help='Positive over-budget19-front-glue contact witness; no physical claim')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    assert a.front_cap>=8 and (not a.relax_obstacles or a.geometry_only)
    assert a.front_cap==8 or a.geometry_only
    assert not a.calibrate or (a.geometry_only and a.front_cap>=19)
    start=time.monotonic();f=Flyer.load(a.base/'problem.flyer');fixed=set(f._cells)-(REAR|FRONT|OLD_ACTORS)
    allocations=[]
    for rb in SOURCES:
        early=[add(rb,tuple(-v for v in d)) for d in POWER]
        early=[p for p in early if p not in fixed and any(distance(add(p,(-1,0,0)),q)==1 for q in G) and not any(distance(p,q)==1 for q in G)]
        late=[add(rb,(-1-d[0],-d[1],-d[2])) for d in POWER]
        late=[p for p in late if p not in fixed and add(p,(1,0,0)) not in fixed and any(distance(p,q)==1 for q in G)]
        for es in itertools.combinations(early,2):
            for l in late:
                acts={rb,*es,l,add(l,(1,0,0))};targets={*(add(p,(1,0,0)) for p in es),add(l,(2,0,0))}
                if len(acts)==5 and not acts&fixed and not targets&(acts|fixed):allocations.append((rb,es,l,targets))
    assert any(rb==(21,2,13) and set(es)=={(21,1,13),(21,3,13)} and l==(20,2,14) for rb,es,l,t in allocations)
    if a.calibrate:allocations=allocations[:1]
    records=[];tests=0
    for index,(rb,es,late,targets) in enumerate(allocations):
        if time.monotonic()-start>a.seconds or tests>=a.max_tests:break
        model=cp_model.CpModel();blocked=(set() if a.relax_obstacles else fixed)|{rb,*es,late,add(late,(1,0,0))};root=(13,3,11);pull=(13,4,12);obs=(16,4,13)
        rg={p:model.NewBoolVar(f'r{p}') for p in itertools.product(range(6,21),range(-4,11),range(4,19))
            if p not in blocked and distance(p,root)<=7 and distance(p,root)+distance(p,pull)+distance(root,pull)<=14}
        hr=min(targets);edges=a.front_cap-1
        hg={p:model.NewBoolVar(f'h{p}') for p in itertools.product(*(range(v-edges,v+edges+1) for v in hr))
            if p not in blocked and all(distance(p,hr)+distance(p,t)+distance(hr,t)<=2*edges for t in targets)}
        if a.calibrate:
            control=FRONT|{(x,3,14) for x in range(10,23)}|{(10,3,13),(10,3,12)}
            assert len(control)==19 and not control&blocked
            for p,v in hg.items():model.Add(v==int(p in control))
            for p,v in rg.items():model.Add(v==int(p in REAR))
        rec={'index':index,'H0_RB':rb,'early':es,'late':late,'targets':sorted(targets)}
        if not targets<=hg.keys() or not {root,pull}<=rg.keys():rec['status']='mandatory blocked';records.append(rec);continue
        for p in targets:model.Add(hg[p]==1)
        model.Add(rg[pull]==1)
        for cells,r,cap in [(rg,root,8),(hg,hr,a.front_cap)]:model.Add(sum(cells.values())<=cap);connectivity(model,cells,r,cap)
        model.Add(sum(hg[p] for p in adj(rb) if p in hg)>=1)
        model.Add(sum(rg[p] for p in adj(obs) if p in rg)>=1)
        for p in rg.keys()&hg.keys():model.Add(rg[p]+hg[p]<=1)
        qs={}
        for q in rg:
            p=add(q,(-3,0,0));touches=[hg[v] for v in adj(p) if v in hg]
            if p in blocked or not touches:continue
            v=model.NewBoolVar(f'q{q}');qs[q]=v;model.Add(rg[q]>=v);model.Add(sum(touches)>=v)
            if p in rg:model.Add(rg[p]+v<=1)
            if p in hg:model.Add(hg[p]+v<=1)
        ss={}
        for q in qs:
            for off in POWER:
                s=add(add(q,(-1,0,0)),off)
                if s in blocked or s in ss:continue
                supports=[rg[p] for p in adj(s) if p in rg]
                if len([t for t in qs if s in adj(add(t,(-1,0,0)))-{t}])<2 or not supports:continue
                v=model.NewBoolVar(f's{s}');ss[s]=v;model.Add(sum(supports)>=v)
                if s in rg:model.Add(rg[s]+v<=1)
                if s in hg:model.Add(hg[s]+v<=1)
        model.Add(sum(qs.values())==2);model.Add(sum(ss.values())==1)
        if a.calibrate:
            for p,v in qs.items():model.Add(v==int(p in {(13,3,11),(13,4,12)}))
            for p,v in ss.items():model.Add(v==int(p==(12,3,12)))
        for q,v in qs.items():
            model.Add(v<=sum(ss[s] for s in (adj(add(q,(-1,0,0)))-{q}) if s in ss))
            p=add(q,(-3,0,0))
            if p in ss:model.Add(v+ss[p]<=1)
        model.Minimize(sum(rg.values())+sum(hg.values()))
        solver=cp_model.CpSolver();solver.parameters.num_search_workers=2;solver.parameters.max_time_in_seconds=min(a.cp_seconds,max(.01,a.seconds-(time.monotonic()-start)))
        result=solver.Solve(model);rec.update(status=solver.StatusName(result),seconds=solver.WallTime(),bound=solver.BestObjectiveBound())
        if result in (cp_model.OPTIMAL,cp_model.FEASIBLE):
            rear={p for p,v in rg.items() if solver.Value(v)};front={p for p,v in hg.items() if solver.Value(v)}
            normals={add(q,(-3,0,0)) for q,v in qs.items() if solver.Value(v)};source=next(p for p,v in ss.items() if solver.Value(v))
            rec.update(rear=sorted(rear),front=sorted(front),normals=sorted(normals),rear_RB=source)
            if a.geometry_only:
                records.append(rec);dump(a.out/'report.json',{'scope':__doc__,'front_cap':a.front_cap,'relax_obstacles':a.relax_obstacles,'allocations':len(allocations),'records':records,'native_tests':tests,'elapsed_seconds':time.monotonic()-start})
                print(json.dumps({'index':index,'status':rec['status'],'front_glue':len(front),'rear_glue':len(rear)}),flush=True)
                continue
            case=a.out/f'case{index:02}';case.mkdir();ff=Flyer.load(a.base/'problem.flyer')
            for p in REAR|FRONT|OLD_ACTORS:ff._cells.pop(p)
            for shape,k in [(rear,Kind.HONEY),(front,Kind.SLIME)]:
                for p in shape:ff.set(p,Block(k))
            for p in [rb,source]:ff.set(p,Block(Kind.REDSTONE_BLOCK))
            for p in set(es)|normals:ff.set(p,Block.piston(0))
            ff.set(late,Block.piston(0,state=2));ff.set(add(late,(1,0,0)),Block(Kind.PISTON_ARM));ff.set_piston_blocks(late,[add(late,(1,0,0))])
            ff.save(case/'problem.flyer');loaded=Flyer.load(case/'problem.flyer')
            delta=tuple(min(p[k] for p in loaded._cells)-min(p[k] for p in ff._cells) for k in range(3))
            assert loaded._cells=={add(p,delta):b for p,b in ff._cells.items()}
            (case/'drive.txt').write_text('',encoding='utf-8')
            for order in ['before_natural','after_natural','interleaved']:
                c=json.loads((a.base/f'{order}.json').read_text(encoding='utf-8'));c['name']=case.name
                next(p for p in c['ports'] if p['name']=='H0')['at']=hr
                next(p for p in c['ports'] if p['name']=='rear_pickup')['provenance']=[None,None,'internal','internal','internal']
                for p in c['ports']:p['at']=add(p['at'],delta)
                c['boundary_envelope']={'min':[min(p[k] for p in loaded._cells) for k in range(3)],'max':[max(p[k] for p in loaded._cells) for k in range(3)]};dump(case/f'{order}.json',c)
            rec.update(rear=sorted(rear),front=sorted(front),normals=sorted(normals),rear_RB=source,case=str(case));dump(case/'preparation.json',rec)
            subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(case/'before_natural.json'),str(case/'native.json'),'20','2'],cwd=ROOT,capture_output=True,check=True)
            rec['native']=json.loads((case/'native.json').read_text(encoding='utf-8'));tests+=1
        records.append(rec);dump(a.out/'report.json',{'scope':__doc__,'allocations':len(allocations),'records':records,'native_tests':tests,'elapsed_seconds':time.monotonic()-start})
        print(json.dumps({'index':index,'status':rec['status'],'native':rec.get('native',{}).get('verified')}),flush=True)
        if rec.get('native',{}).get('verified'):break
    dump(a.out/'report.json',{'scope':__doc__,'front_cap':a.front_cap,'relax_obstacles':a.relax_obstacles,'allocations':len(allocations),'records':records,'native_tests':tests,'elapsed_seconds':time.monotonic()-start})
    (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    dump(a.out/'inputs.json',{'base_sha256':hashlib.sha256((a.base/'problem.flyer').read_bytes()).hexdigest(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'arguments':{k:str(v) if isinstance(v,Path) else v for k,v in vars(a).items()}})


if __name__=='__main__':main()
