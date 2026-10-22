"""Minimum T0 glue with current own actors/source, X0 sticky and G0 pickups.

A necessary contact-only bound; changed actors, carriers, sources or pull
anchor are not excluded. The proposed observer is not even included, so a
minimum7 already excludes paying for it by trimming to6 under this allocation.
"""
import argparse,hashlib,json,itertools
from pathlib import Path
from assemble import Flyer
from ortools.sat.python import cp_model
from model_recovery_layout import connectivity
from route_recovery_observer_pull import adj

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    f=Flyer.load(a.base/'problem.flyer');old={(17,0,12),(17,0,13),(17,1,11),(17,1,12),(17,2,11),(17,2,12),(17,2,13)}
    root=(17,2,13);targets={root,(17,1,12),(17,2,11)};required=[(16,1,11),(17,3,11),(17,0,14),(17,1,13),(17,2,14)]
    reports=[]
    for obstacles in [False,True]:
        m=cp_model.CpModel();blocked=set(f._cells)-old if obstacles else set(required)
        cells={p:m.NewBoolVar(str(p)) for p in itertools.product(range(11,24),range(-4,9),range(7,20))
               if p not in blocked and sum(abs(x-y) for x,y in zip(p,root))<=6}
        for p in targets:m.Add(cells[p]==1)
        for p in required:m.Add(sum(cells[q] for q in adj(p) if q in cells)>=1)
        m.Add(sum(cells.values())<=7);connectivity(m,cells,root,7);m.Minimize(sum(cells.values()))
        s=cp_model.CpSolver();s.parameters.max_time_in_seconds=5;s.parameters.num_search_workers=2;result=s.Solve(m)
        rec={'obstacles':obstacles,'status':s.StatusName(result),'bound':s.BestObjectiveBound(),'seconds':s.WallTime()}
        if result in [cp_model.OPTIMAL,cp_model.FEASIBLE]:rec.update(glue=sorted(p for p,v in cells.items() if s.Value(v)),objective=s.ObjectiveValue())
        reports.append(rec)
    (a.out/'report.json').write_text(json.dumps({'scope':__doc__,'root':root,'own_targets':sorted(targets),'source_and_passenger_contacts':required,'records':reports,
       'base_sha256':hashlib.sha256((a.base/'problem.flyer').read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')
    (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(reports))
if __name__=='__main__':main()
