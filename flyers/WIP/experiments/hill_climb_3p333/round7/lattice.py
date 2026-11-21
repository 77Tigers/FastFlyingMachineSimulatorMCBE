"""Budgeted directed block discovery on a fixed 3D lattice."""
from collections import defaultdict, deque
from ctypes import CDLL, POINTER, c_int
from functools import cache
from pathlib import Path

from ortools.sat.python import cp_model

E = (1, 0, 0)
W = (-1, 0, 0)
SIDE = ((0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
FACES = (E, W, *SIDE)


def add(p, q):
    return p[0] + q[0], p[1] + q[1], p[2] + q[2]


def shift(p, x):
    return p[0] + x, p[1], p[2]


def neighbors(p):
    return {add(p, d) for d in FACES}


def domain(fixed, empty, no_glue, strokes, cap, groups, window, enumerate_all=False):
    if fixed.keys() & empty or any(fixed.get(p)=='glue' for p in no_glue):
        return None
    slack=cap-len(fixed)
    if slack<0:
        return None
    virtual={p for _,leaves in strokes for p in leaves}
    sites=set(fixed)|virtual
    for _ in range(slack):
        sites |= {q for p in sites for q in neighbors(p)} - empty
    if window is not None:
        sites &= set(window)|set(fixed)|virtual
    sites -= empty
    terminals=set(fixed)|virtual|{p for group in groups for p,_ in group}
    def distance(p,q):
        return sum(abs(a-b) for a,b in zip(p,q))
    sites={p for p in sites if enumerate_all or p in terminals or
           sum(sorted(distance(p,q) for q in terminals)[:2])<=slack+1}
    glue={p for p in sites if p not in no_glue and fixed.get(p) not in ('glaze','passive')}
    # Charge every optional voxel on a directed path. Each chosen cell must
    # be reachable from every prescribed input inside the remaining budget.
    for root,leaves in strokes:
        allowed=sites|set(leaves)
        dist={root:0}
        queue=deque([root])
        while queue:
            p=queue.popleft()
            ns={shift(p,1)}
            if p in glue:
                ns |= {q for q in neighbors(p) if fixed.get(q)!='glaze'}
            for q in ns & allowed:
                weight=int(q not in fixed and q not in leaves)
                value=dist[p]+weight
                if value<=slack and value<dist.get(q,slack+1):
                    dist[q]=value
                    (queue.append if weight else queue.appendleft)(q)
        if not fixed.keys()<=dist.keys():
            return None
        sites &= dist.keys()
        glue &= sites
    return sites,glue


@cache
def library():
    fn=CDLL(str(Path(__file__).with_name('discovery.so'))).complete_body
    arr=POINTER(c_int)
    fn.argtypes=[c_int,c_int,arr,arr,c_int,arr,arr,c_int,arr,c_int,c_int,arr]
    fn.restype=c_int
    return fn


def solve_body(fixed, empty, no_glue, strokes, cap, groups=(), window=None,
               need_glue=(), seconds=2.5, native=False, maxresults=1, raw_cp=False):
    """Check that every input can discover the complete rigid body.

    Each group lists (site, needs_glue) alternatives. A fixed glazed block
    accepts only an eastward obstruction. A passive block can receive glue
    adhesion and can transmit an eastward obstruction. Moving foreign leaves
    can be selected by adhesion and transmit eastward force.
    """
    if raw_cp:
        if window is None:
            raise ValueError('a pinned CP window is required')
        if fixed.keys() & empty or any(fixed.get(p)=='glue' for p in no_glue):
            return 'INFEASIBLE',None
        sites=(set(window)|set(fixed))-empty
        material=sites,{p for p in sites-no_glue if fixed.get(p) not in ('glaze','passive')}
    else:
        material=domain(fixed,empty,no_glue,strokes,cap,groups,window,maxresults>1)
    if material is None:
        return 'INFEASIBLE',None
    sites,glue=material
    if not set(need_glue)<=glue:
        return 'INFEASIBLE',None
    if native:
        virtual={p for _,leaves in strokes for p in leaves}
        cells=sorted(sites|virtual)
        ix={p:i for i,p in enumerate(cells)}
        def ints(values):
            values=list(values)
            return (c_int*len(values))(*values)
        links=ints(ix.get(add(p,d),-1) for p in cells for d in FACES)
        flags=ints((p in fixed or p in need_glue) + 2*(p in glue) +
                   4*(fixed.get(p)=='glaze') + 8*(p not in sites) for p in cells)
        req=ints(sum(1<<i for i,g in enumerate(groups) if any(
            p==q and (not needs or p in glue) for q,needs in g)) for p in cells)
        assert all(len(leaves)<=1 for _,leaves in strokes)
        roots=ints(ix[p] for p,_ in strokes)
        leaves=ints(ix[l[0]] if l else -1 for _,l in strokes)
        out=(c_int*((cap+1)*maxresults))()
        count=library()(len(cells),cap,links,flags,len(strokes),roots,leaves,
                        len(groups),req,2000000,maxresults,out)
        if count<=0:
            return ('INFEASIBLE' if count==0 else 'UNKNOWN'),None
        rows=[]
        for j in range(count):
            off=j*(cap+1)
            rows.append(tuple(cells[i] for i in out[off+1:off+1+out[off]]))
        if maxresults==1:
            return 'FEASIBLE',rows[0]
        if count==maxresults:
            raise ValueError('increase solution capacity')
        return 'FEASIBLE',rows
    model = cp_model.CpModel()
    occ = {p: model.new_bool_var('') for p in sorted(sites)}
    for p in fixed:
        model.add(occ[p] == 1)
    total = sum(occ.values())
    model.add(total <= cap)
    if not set(need_glue) <= glue:
        return 'INFEASIBLE', None
    for p in need_glue:
        model.add(occ[p]==1)
    for group in groups:
        model.add_bool_or([occ[p] for p,g in group if p in sites and (not g or p in glue)])
    # Each source must be able to discover every selected rigid cell.
    for source, leaves in strokes:
        if source not in occ:
            return 'INFEASIBLE', None
        allowed = sites | set(leaves)
        incoming, outgoing = defaultdict(list), defaultdict(list)
        for p in sorted(allowed):
            ns = {shift(p, 1)}
            if p in glue:
                ns |= {q for q in neighbors(p) if fixed.get(q) != 'glaze'}
            for q in sorted(ns & allowed):
                edge = model.new_int_var(0, cap, '')
                if p in occ:
                    model.add(edge <= cap * occ[p])
                if q in occ:
                    model.add(edge <= cap * occ[q])
                outgoing[p].append(edge)
                incoming[q].append(edge)
        for p in sorted(allowed):
            supply = (total if p == source else 0) - occ.get(p, 0)
            model.add(sum(outgoing[p]) - sum(incoming[p]) == supply)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.max_time_in_seconds = seconds
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return solver.status_name(status), None
    return 'FEASIBLE', sorted(p for p in sites if solver.value(occ[p]))
