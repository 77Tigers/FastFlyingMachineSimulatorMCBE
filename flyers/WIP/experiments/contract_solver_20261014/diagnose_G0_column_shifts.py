"""Optimistic glue-only diagnostic for moving the G0 source column.

Keep the two existing T0-relay observer locations, free X1 and the added
T1 pull interface, and minimize connected G0 glue. No phase/power/native
acceptance is inferred; occupied source sites are explicit fixed conflicts.
"""
import argparse,json,itertools
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer,body_of
from model_recovery_layout import connectivity
from search_T1_two_pushes import add,adj,dist,dump

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False);f=Flyer.load(a.base/'problem.flyer')
 removed=body_of(f._cells,(18,5,12))|body_of(f._cells,(15,5,12))|{(17,5,12),(16,5,11),(16,5,13),(16,6,12),(15,6,10),(17,6,10),(17,7,10),(18,6,11)};fixed=set(f._cells)-removed;records=[]
 for center in [(18,5,12),(17,5,12),(18,4,12),(18,5,11)]:
  rb=add(center,(-1,0,0));targets={center,add(center,(0,0,1)),add(center,(0,0,-1)),add(center,(0,1,0))};motors={add(p,(-2,0,0)) for p in targets-{center}};conflicts=(targets|motors|{rb})&fixed;rec={'center':center,'RB':rb,'source_conflicts':[{ 'at':p,'kind':f._cells[p].kind.name} for p in sorted(conflicts)]}
  if conflicts:rec['status']='fixed source conflict';records.append(rec);continue
  blocked=fixed|motors|{rb};m=cp_model.CpModel();cells={p:m.NewBoolVar(str(p)) for p in itertools.product(range(13,23),range(0,9),range(8,18)) if p not in blocked and dist(p,center)<=8}
  for p in targets:m.Add(cells[p]==1)
  for obs in [(17,3,13),(17,4,13)]:m.Add(sum(cells[p] for p in adj(obs) if p in cells)>=1)
  m.Add(sum(cells.values())<=12);connectivity(m,cells,center,12);m.Minimize(sum(cells.values()));s=cp_model.CpSolver();s.parameters.max_time_in_seconds=1;s.parameters.num_search_workers=2;status=s.Solve(m);rec.update(status=s.StatusName(status),seconds=s.WallTime(),lower_bound=s.BestObjectiveBound())
  if status in [cp_model.OPTIMAL,cp_model.FEASIBLE]:rec.update(glue=int(s.ObjectiveValue()),shape=sorted(p for p,v in cells.items() if s.Value(v)))
  records.append(rec)
 dump(a.out/'report.json',{'scope':__doc__,'records':records});(a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(records),flush=True)
if __name__=='__main__':main()
