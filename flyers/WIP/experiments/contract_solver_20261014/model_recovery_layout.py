"""Bounded necessary geometry model for joint G/H recovery (not physics proof).

Free G/H glue and G pulse placement, fixed rear/T interface and G puller contact.
Two runs distinguish baseline geometry from adding a wwmmm tip puller recovery.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time

from ortools.sat.python import cp_model
from assemble import Flyer
from repair_sticky_pickup import adjacent


def connectivity(model, cells, root, cap):
    flows = {}
    for p in cells:
        for q in adjacent(p):
            if q in cells:
                f = model.NewIntVar(0, cap, f"flow{p}{q}")
                model.Add(f <= cap * cells[p])
                model.Add(f <= cap * cells[q])
                flows[p, q] = f
    for p in cells:
        outgoing = sum(flows[p, q] for q in adjacent(p) if (p, q) in flows)
        incoming = sum(flows[q, p] for q in adjacent(p) if (q, p) in flows)
        model.Add(outgoing - incoming == (sum(cells.values()) - 1 if p == root else -cells[p]))
    model.Add(cells[root] == 1)


def run(source, cap, recovery, seconds, pin_fixture=False, free_puller=False, normal_column=False, supply_g=False):
    c = json.loads((source / "problem.json").read_text())
    f = Flyer.load(source / c["flyer"])
    tip = next(p["at"] for p in c["ports"] if p["name"] == "tip")
    delta = tuple(b-a for a,b in zip(tip,(21,2,16)))
    shift = lambda p: tuple(v+d for v,d in zip(p,delta))
    f._cells = {shift(p):b for p,b in f._cells.items()}
    for p in c["ports"]: p["at"] = shift(p["at"])
    assert f._cells[(21,2,16)].kind == 1 and f._cells[(21,2,17)].sticky
    oldg = {tuple(p["at"]) for p in c["ports"] if p["name"].startswith("G")}
    removed = oldg | {p for p,b in f._cells.items() if (p[0] == 17 and b.kind == 9 and b.direction == 0)
                     or (p[0] == 18 and b.kind == 6) or (p[0] == 22 and b.kind == 7)}
    if free_puller:
        removed.add((21,2,17))
    fixed = set(f._cells) - removed
    root, hr, qg = (19,2,17), (21,2,16), (2,17)
    model = cp_model.CpModel()
    domain = [(x,y,z) for x in range(18,24) for y in range(-1,6) for z in range(14,21)]
    g = {p:model.NewBoolVar(f"G{p}") for p in domain if p not in fixed}
    h = {(21,y,z):model.NewBoolVar(f"H{y,z}") for y in range(-1,6) for z in range(14,21)
         if (21,y,z) not in fixed or (21,y,z) == hr}
    model.Add(sum(g.values()) <= cap)
    model.Add(sum(h.values()) <= 5)
    if pin_fixture:
        for p,v in g.items(): model.Add(v == int(p in oldg))
        for p,v in h.items(): model.Add(v == int(p == hr))
    connectivity(model, g, root, cap)
    connectivity(model, h, hr, 5)
    # Actual G/H words wmmmw/mmwwm imply these distinct permanent-cell lanes.
    for hp,hv in h.items():
        for x in (20,21,22):
            gp = (x,*hp[1:])
            if gp in g:
                model.Add(g[gp] + hv <= 1)
    # G-carried observer pulses after move2, powers a H cell beside G's H-carried
    # sticky at slot2, then moves away so that sticky retracts at slot3.
    powers = []
    for hp,hv in h.items():
        choices = [p[1:] for p in adjacent(hp) if p[0] == 21] if free_puller else [qg]
        for contact in choices:
            if abs(hp[1]-contact[0]) + abs(hp[2]-contact[1]) != 1:
                continue
            target, sticky = (19,*contact), (21,*contact)
            if target not in g or (free_puller and sticky in fixed):
                continue
            for op in adjacent(hp):
                if op[0] != 21 or op[1:] == contact:
                    continue
                support, observer = op, (22,*op[1:])
                if support not in g or observer in fixed:
                    continue
                b = model.NewBoolVar(f"power{hp}{op}{contact}")
                model.Add(hv == 1).OnlyEnforceIf(b)
                model.Add(g[support] == 1).OnlyEnforceIf(b)
                model.Add(g[target] == 1).OnlyEnforceIf(b)
                if observer in g:
                    model.Add(g[observer] == 0).OnlyEnforceIf(b)
                if free_puller:
                    if sticky in h:
                        model.Add(h[sticky] == 0).OnlyEnforceIf(b)
                    for x in (20,21,22):
                        if (x,*contact) in g:
                            model.Add(g[(x,*contact)] == 0).OnlyEnforceIf(b)
                    if pin_fixture and contact != qg:
                        model.Add(b == 0)
                powers.append((b, hp, observer, sticky))
    model.Add(sum(b for b,_,_,_ in powers) == (0 if supply_g else 1))
    pulls = []
    if recovery:
        for hp,hv in h.items():
            actor, pulse = (24,*hp[1:]), (25,*hp[1:])
            if actor in fixed or pulse in fixed:
                continue
            contacts = [(p[0]-1,*p[1:]) for p in adjacent(actor)]
            reachable = [g[p] for p in contacts if p in g]
            if not reachable:
                continue
            b = model.NewBoolVar(f"recovery{hp}")
            model.Add(hv == 1).OnlyEnforceIf(b)
            model.Add(sum(reachable) >= 1).OnlyEnforceIf(b)
            # Sticky is still at24 after G's first move; no shared position.
            if (23,*hp[1:]) in g:
                model.Add(g[(23,*hp[1:])] == 0).OnlyEnforceIf(b)
            pulls.append((b,actor,pulse))
        model.Add(sum(b for b,_,_ in pulls) == 1)
    columns = []
    if normal_column:
        for hp,hv in h.items():
            source_at = (20,*hp[1:])
            if source_at in fixed:
                continue
            lanes = [p for p in adjacent(hp) if p in h]
            for chosen in itertools.combinations(lanes,3):
                for late in chosen:
                    early = [p for p in chosen if p != late]
                    actors = [(20,*p[1:]) for p in early] + [(19,*late[1:])]
                    arm = (20,*late[1:])
                    if any(p in fixed for p in actors+[arm]):
                        continue
                    supports = []
                    for p in chosen:
                        side = [(19,*q[1:]) for q in adjacent(p) if q[0] == 21]
                        side += [(18,*p[1:])]
                        supports.append([g[q] for q in side if q in g])
                    if not all(supports):
                        continue
                    b = model.NewBoolVar(f"column{hp}{chosen}{late}")
                    model.Add(hv == 1).OnlyEnforceIf(b)
                    for p in chosen:
                        model.Add(h[p] == 1).OnlyEnforceIf(b)
                    for support in supports:
                        model.Add(sum(support) >= 1).OnlyEnforceIf(b)
                    # Both early identities must survive either first firing.
                    # G's first move cannot collide with their extended bases.
                    for p in chosen:
                        if (19,*p[1:]) in g:
                            model.Add(g[(19,*p[1:])] == 0).OnlyEnforceIf(b)
                    for p in actors+[arm,source_at,(19,*hp[1:])]:
                        if p in g:
                            model.Add(g[p] == 0).OnlyEnforceIf(b)
                    columns.append((b,source_at,actors,arm))
        model.Add(sum(b for b,_,_,_ in columns) == 1)
    model.Minimize(sum(g.values()))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 4
    solver.parameters.random_seed = 0
    start = time.monotonic()
    status = solver.Solve(model)
    result = {"status":solver.StatusName(status), "seconds":time.monotonic()-start,
              "recovery":recovery, "pin_fixture":pin_fixture,
              "free_G_puller":free_puller,
              "normal_H_column":normal_column,
              "G_all_supplied":supply_g,
              "source_translation":delta,
              "G_glue_cap":cap, "best_bound":solver.BestObjectiveBound()}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result.update(G=[p for p,v in g.items() if solver.Value(v)], H=[p for p,v in h.items() if solver.Value(v)],
                      power=[(hp,op) for b,hp,op,_ in powers if solver.Value(b)],
                      G_puller=[p for b,_,_,p in powers if solver.Value(b)],
                      H_column=[{"source":s,"early":ps[:2],"late":ps[2],"arm":a}
                                for b,s,ps,a in columns if solver.Value(b)],
                      puller=[(a,p) for b,a,p in pulls if solver.Value(b)])
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source",type=Path)
    ap.add_argument("output",type=Path)
    ap.add_argument("--seconds",type=float,default=60)
    ap.add_argument("--g-glue",type=int,default=5)
    ap.add_argument("--free-puller",action="store_true")
    ap.add_argument("--normal-column",action="store_true")
    ap.add_argument("--supply-g",action="store_true",help="isolate H pickup geometry; no G power/puller required")
    a=ap.parse_args()
    if a.supply_g and not (a.free_puller and a.normal_column):
        raise ValueError("--supply-g requires --free-puller --normal-column")
    if a.output.exists(): raise ValueError("existing result")
    result={"scope":"bounded necessary geometry only, fixed G connectivity anchor; not a native candidate or universal impossibility",
            "free_G_puller":a.free_puller,
            "optimistic_load_reservation":{"limit":11,"G_other_cells":3,"recovery_riders":2,"H_push_riders_at_least":1,"G_glue_budget":5},
            "source":str(a.source),"results":[],
            "sha256":{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),a.source/'problem.json',a.source/'problem.flyer']}}
    if a.normal_column:
        result["optimistic_load_reservation"] = {"limit":11,"G_glue_budget":5,
            "G_current_hardware":1 if a.supply_g else 3,
            "G_reserved_hardware":2 if a.supply_g else 0,"H_push_riders_max":3}
    for recovery,pin in [(False,True),(False,False),(not a.normal_column,False)]:
        result["results"].append(run(a.source,a.g_glue,recovery,a.seconds,pin,a.free_puller,
                                    a.normal_column and not pin and len(result["results"]) == 2,a.supply_g))
        a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result['results'][-1]),flush=True)
        if pin and result["results"][-1]["status"] != "OPTIMAL":
            raise RuntimeError("known fixture failed calibration; do not interpret free-model bounds")


if __name__ == '__main__': main()
