"""Free T2's own power and normal targets before another observer-pull search.

Enumerate initial normal/source choices from retained X2 pickup geometry.
First T2 normal follows wwmmm (X2 moves2/3, T2 move4); late follows wmmmw.
For each choice CP-SAT finds connected T2 glue<=6 with both push targets,
source attachment and retained X2-sticky support. This omits the G2 normals,
observer, arms after startup and full physics; leads are not flyers.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
from ortools.sat.python import cp_model
from assemble import Flyer
from model_recovery_layout import connectivity
from screen_helper_column import add, move, near

D = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
POWER = [(-1,0,0),*D[2:]]
X2 = {(17,6,11),(17,6,12),(18,6,12),(18,6,13),(18,5,12),
      (18,5,13),(18,4,13),(18,4,14),(19,6,12)}
OLD_T2 = {(21,4,13),(21,4,14),(21,5,13),(21,6,13),(22,5,13),(21,7,13),(22,7,13)}
OLD_G2 = {(25,6,12),(25,5,12),(25,7,12),(25,6,13),(22,5,12),(22,7,12),(23,6,13),(24,6,13)}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    ap.add_argument('--seconds',type=float,default=90)
    ap.add_argument('--max-leads',type=int,default=24)
    a=ap.parse_args();start=time.monotonic()
    f=Flyer.load(a.base/'problem.flyer')
    freed=OLD_T2|OLD_G2|{(20,4,13),(20,5,13),(19,4,14),(20,4,14)}
    fixed=set(f._cells)-freed
    root=(21,6,13)
    firsts={add(add(g,(1,0,0)),d) for g in X2 for d in D}-fixed
    lates={add(g,d) for g in X2 for d in D}-fixed
    choices=[]
    for b in sorted(firsts):
      if any(near(b,g) for g in X2):continue  # first pickup is2, not1
      for off in POWER:
       rb=add(b,off)
       if rb in fixed or rb==b:continue
       for l in sorted(lates):
        arm=add(l,(1,0,0));qb=add(b,(1,0,0));ql=add(l,(2,0,0))
        if not any(add(add(l,(1,0,0)),d)==rb for d in POWER):continue
        hardware={b,rb,l,arm}
        if len(hardware)!=4 or hardware&fixed:continue
        targets={root,qb,ql}
        if targets&(fixed|hardware):continue
        valid=True
        for t in range(5):
         xx={move(g,'wmmmw',t) for g in X2}
         bp=move(b,'wwmmm',t);lp=move(l,'wmmmw',t);rp=move(rb,'mmwwm',t)
         if len({bp,lp,rp})!=3 or {bp,lp,rp}&xx:valid=False;break
        if valid:choices.append((b,l,rb,targets))
    # Positive calibration: retained own targets admit the known four-glue core.
    assert any(b==(20,5,13) and l==(19,4,14) and rb==(20,4,13)
               for b,l,rb,targets in choices)
    choices.sort(key=lambda c:(c[:3]==((20,5,13),(19,4,14),(20,4,13)),c[:3]))
    leads=[];tested=0;complete=True
    for b,l,rb,targets in choices:
      if time.monotonic()-start>a.seconds:complete=False;break
      model=cp_model.CpModel();blocked=fixed|{b,l,add(l,(1,0,0)),rb}
      cells={p:model.NewBoolVar(str(p)) for x in range(19,25) for y in range(3,9)
             for z in range(10,16) if (p:=(x,y,z)) not in blocked and
             all(move(p,'mmwwm',t)!=move(g,'wmmmw',t) for g in X2 for t in range(5))}
      if not targets<=cells.keys():continue
      for p in targets:model.Add(cells[p]==1)
      model.Add(sum(cells.values())<=6)
      support=[cells[add(rb,d)] for d in D if add(rb,d) in cells]
      if not support:continue
      model.Add(sum(support)>=1)
      connectivity(model,cells,root,6)
      model.Minimize(sum(cells.values()))
      solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=min(0.5,max(0.01,a.seconds-(time.monotonic()-start)))
      solver.parameters.num_search_workers=1
      result=solver.Solve(model);tested+=1
      if result in (cp_model.OPTIMAL,cp_model.FEASIBLE):
       leads.append({'first':b,'late':l,'RB':rb,'T2_glue':[p for p,v in cells.items() if solver.Value(v)],
                     'solver_status':solver.StatusName(result),'scope':'Own-column necessary geometry only; G2 normals/observer unmodeled.'})
       if len(leads)>=a.max_leads:complete=False;break
    report={'scope':__doc__,'choices':len(choices),'solved_choices':tested,'complete':complete,
            'elapsed_seconds':time.monotonic()-start,'known_pickup_fixture':True,'leads':leads,
            'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.base/'problem.flyer',Path(__file__)]}}
    a.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['leads','sha256']}))
    print('Unverified own-column leads:',len(leads))


if __name__=='__main__':main()
