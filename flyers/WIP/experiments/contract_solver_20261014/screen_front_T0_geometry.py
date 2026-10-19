"""Relaxed connected-glue screen for H0 carrying the two T0 normals.

Keep H0's source and direct-powered +X three-row architecture, but allow
three of four lateral firing rows and replace its entire glue shape.
Ignore other bodies, recovery, switch-off and foreign adhesion. Feasibility
is only a contact hypothesis; INFEASIBLE applies to this bounded family.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from ortools.sat.python import cp_model

D = ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))


def adjacent(p):
    return [tuple(a+b for a,b in zip(p,d)) for d in D]


def solve(extra, seconds, source_x=21):
    source = (source_x,2,13)
    normal_rows = [(source_x,1,13),(source_x,3,13),(source_x,2,12),(source_x,2,14)]
    # Include the complete coordinate box around all terminals, plus one
    # cell in every transverse direction. No external occupancy is imposed.
    domain = list(itertools.product(range(13,source_x+3),range(0,5),range(10,16)))
    model = cp_model.CpModel()
    cells = {p:model.NewBoolVar(f'g{p}') for p in domain if p != source}
    count = sum(cells.values())
    model.Add(count <= 9)
    rows = [model.NewBoolVar(f'row{p}') for p in normal_rows]
    model.Add(sum(rows) == 3)
    for p,chosen in zip(normal_rows,rows):
        model.Add(cells[p] == 0).OnlyEnforceIf(chosen)
        model.Add(cells[(p[0]+1,*p[1:])] == 1).OnlyEnforceIf(chosen)
    for p in extra:
        model.Add(cells[p] == 0)
        model.Add(sum(cells[q] for q in adjacent(p) if q in cells) >= 1)
    roots = {p:model.NewBoolVar(f'root{p}') for p in adjacent(source) if p in cells}
    model.Add(sum(roots.values()) == 1)
    for p,v in roots.items(): model.Add(v <= cells[p])
    flows = {}
    for p in cells:
        for q in adjacent(p):
            if q in cells:
                f = model.NewIntVar(0,9,f'f{p}{q}')
                model.Add(f <= 9*cells[p]);model.Add(f <= 9*cells[q])
                flows[p,q] = f
    for p in cells:
        balance = sum(flows[p,q]-flows[q,p] for q in adjacent(p) if q in cells)
        if p in roots:
            model.Add(balance == count-1).OnlyEnforceIf(roots[p])
            model.Add(balance == -cells[p]).OnlyEnforceIf(roots[p].Not())
        else: model.Add(balance == -cells[p])
    model.Minimize(count)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 4
    status = solver.Solve(model)
    result = {'status':solver.StatusName(status),'seconds':solver.WallTime(),
              'best_bound':solver.BestObjectiveBound(),'requested_contacts_saved':extra}
    if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        shape = [p for p,v in cells.items() if solver.Value(v)]
        chosen = [p for p,v in zip(normal_rows,rows) if solver.Value(v)]
        # Independent connectivity/terminal calibration of every witness.
        seen = {shape[0]};pending = list(seen);s = set(shape)
        while pending:
            for q in adjacent(pending.pop()):
                if q in s and q not in seen: seen.add(q);pending.append(q)
        assert seen == s and any(q in s for q in adjacent(source))
        assert all(any(q in s for q in adjacent(p)) for p in extra)
        assert all((p[0]+1,*p[1:]) in s and p not in s for p in chosen)
        result.update(glue=shape,glue_count=len(shape),normal_rows=chosen,
                      independently_checked_contacts=True)
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('out',type=Path);ap.add_argument('--seconds',type=float,default=12)
    ap.add_argument('--source-x',type=int,default=21)
    ap.add_argument('--cases',nargs='+',choices=['calibration','first','late','both'],default=['calibration','first','late','both'])
    a=ap.parse_args()
    # Same per-slot motion as the accepted recovery component; subtract
    # H0's prefix at contact time. Both first-normal contacts reduce to
    # (14,1,12); the late-normal slot1 contact reduces to (15,2,11).
    first=(14,1,12);late=(15,2,11)
    results={}
    for name,contacts in [('calibration',[]),('first',[first]),('late',[late]),('both',[first,late])]:
        if name in a.cases: results[name]=solve(contacts,a.seconds,a.source_x)
    out={'scope':__doc__,'source_saved':[a.source_x,2,13],'maximum_glue':9,
         'budget':'H0 baseline4 glue and peak7; transfer yields peak<=7 before connectors, so <=9 glue at PL12.',
         'omitted':['other-body occupancy and material contacts','all piston recovery','source switch-off and stray power','native physical verification'],
         'results':results,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    a.out.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:{n:v[n] for n in ['status','seconds','best_bound','glue_count'] if n in v} for k,v in results.items()}))


if __name__=='__main__':main()
