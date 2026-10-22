"""Necessary connected-glue screen for a split X0/H2 relay; never physics acceptance.

Fix the accepted T0 motors, move the upper relay onto X0 behind a glazed
root, and retain an ordinary four-honey H2 drive for the lower relay.
Regenerate X0 and G2 glue and the transverse G2 pulse observer.
"""
import argparse, itertools, json, time
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer
from fastflyer import Kind
from model_recovery_layout import connectivity

D = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(p,d): return tuple(a+b for a,b in zip(p,d))
def adj(p): return [add(p,d) for d in D]
def dist(p,q): return sum(abs(a-b) for a,b in zip(p,q))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base',type=Path); ap.add_argument('out',type=Path)
    ap.add_argument('--x-cap',type=int,default=6); ap.add_argument('--g-cap',type=int,default=6)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic(); f=Flyer.load(a.base/'problem.flyer')
    oldx={p for p,b in f._cells.items() if b.kind==Kind.HONEY and p[1]==3}
    oldg={(13,2,11),(13,2,12)}; oldobs=(14,2,11)
    fixed=set(f._cells)-(oldx|oldg|{oldobs})
    # The upper honey root becomes glazed; the lower root remains honey.
    h2={(15,1,12),(15,0,12),(15,-1,12),(15,0,13)}
    motors={(14,1,12),(14,-1,12),(14,0,13)}
    additions=h2|motors|{(14,0,12)}
    overlap=sorted((additions-{(15,1,12)}) & fixed)
    fixed |= additions
    g0={(17,0,11),(18,0,11),(18,0,12),(18,0,13),(18,1,13),(18,2,13)}
    t0={p for p,b in f._cells.items() if b.kind==Kind.SLIME} - g0 - oldg
    records=[]
    for di in [2,3,4,5]:
        motor=(12,2,10); d=D[di]; obs=add(motor,(2-d[0],-d[1],-d[2]))
        rec={'direction':di,'observer':obs,'initial_overlap':overlap}
        if overlap or obs in fixed: rec['status']='occupied'; records.append(rec); continue
        model=cp_model.CpModel(); domain=list(itertools.product(range(10,20),range(-2,6),range(8,16)))
        blocked=fixed|{obs}
        x={p:model.NewBoolVar(f'x{p}') for p in domain if p not in blocked and dist(p,(14,2,12))<a.x_cap}
        g={p:model.NewBoolVar(f'g{p}') for p in domain if p not in blocked and dist(p,(13,0,12))<a.g_cap}
        if (14,2,12) not in x or (13,0,12) not in g: rec['status']='root excluded'; records.append(rec); continue
        for cells,root,cap in [(x,(14,2,12),a.x_cap),(g,(13,0,12),a.g_cap)]:
            model.Add(cells[root]==1); model.Add(sum(cells.values())<=cap)
            connectivity(model,cells,root,cap)
        for target in [motor,(16,2,11)]: model.Add(sum(x[p] for p in adj(target) if p in x)>=1)
        for target in motors|{obs}: model.Add(sum(g[p] for p in adj(target) if p in g)>=1)
        for p,v in x.items():
            # Same-phase honey contact joins H2 to X0; observer track must clear.
            if any(dist(p,q)<=1 for q in h2) or any(dist(p,add(obs,(k,0,0)))<=1 for k in [-2,-1,0]) or p==(16,2,11): model.Add(v==0)
            if p in g: model.Add(v+g[p]<=1)
        for p,v in g.items():
            if any(dist(add(p,(k,0,0)),q)<=1 for k in [-2,-1,0] for q in g0): model.Add(v==0)
            if any(dist(add(p,(k,0,0)),q)<=1 for k in [-1,0,1] for q in t0): model.Add(v==0)
        model.Minimize(sum(x.values())+sum(g.values()))
        s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=3; s.parameters.num_search_workers=2
        result=s.Solve(model); rec.update(status=s.StatusName(result),seconds=s.WallTime())
        if result in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
            rec['shapes']={name:sorted(p for p,v in cells.items() if s.Value(v)) for name,cells in [('X0',x),('G2',g)]}
        records.append(rec)
    report={'scope':__doc__,'records':records,'seconds':time.monotonic()-start,'caps':{'X0':a.x_cap,'G2':a.g_cap},
            'limits':'Fixed four-honey H2 star and T0 motor position; static necessary contacts only. No constructed flyer or timing/physics acceptance.'}
    (a.out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(report))
if __name__=='__main__': main()
