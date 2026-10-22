"""exact (CP-SAT) minimum glue for body X in one link U->X: plate + coverage of U's spent columns + connected."""
import sys, json, itertools
from ortools.sat.python import cp_model
from ring_designer import Ring, ORDER, NEXT, PREV, D6, add, V4c, V1c, V5c, V6, V6c, hard_conflicts, spent_targets, route_cover
LAY = {'V4c': V4c, 'V1c': V1c, 'V5c': V5c, 'V6': V6, 'V6c': V6c}
FAR = 60


def link_ring(name, U, rel):
    X = NEXT[U]
    place = {Y: (0, (FAR * (i + 1), FAR * (i + 1)), 0) for i, Y in enumerate(ORDER)}
    place[U] = (0, (0, 0), 0); place[X] = rel
    return Ring(LAY[name], place), X


def body_cp(ring, X, margin=1, tl=30, workers=4, ub=None):
    ring.glue[X] = set(ring.plates[X])
    worlds = [ring.world(s) for s in range(8)]
    tg = spent_targets(ring, X)
    pts = list(ring.plates[X]) + tg
    lo = [min(c[i] for c in pts) - margin for i in range(3)]; hi = [max(c[i] for c in pts) + margin for i in range(3)]
    cand = [c for c in itertools.product(*[range(lo[i], hi[i] + 1) for i in range(3)])
            if c in ring.plates[X] or ring.cell_ok(X, c, worlds)]
    cs = set(cand); idx = {c: i for i, c in enumerate(cand)}
    m = cp_model.CpModel()
    v = [m.NewBoolVar('') for _ in cand]
    for c in ring.plates[X]: m.Add(v[idx[c]] == 1)
    for t in tg:
        lits = [v[idx[n]] for d in D6 if d != (1, 0, 0) and (n := add(t, d)) in cs]
        if not lits: return None
        m.AddBoolOr(lits)
    # connectivity: depth labelling from a root plate cell (each chosen non-root cell has a chosen neighbour one level lower)
    root = idx[sorted(ring.plates[X])[0]]; N = len(cand)
    dep = [m.NewIntVar(0, N, '') for _ in cand]
    m.Add(dep[root] == 0)
    for i, c in enumerate(cand):
        if i == root: continue
        nbs = [idx[n] for d in D6 if (n := add(c, d)) in cs]
        par = []
        for j in nbs:
            b = m.NewBoolVar('')
            m.AddImplication(b, v[j]); m.Add(dep[i] >= dep[j] + 1).OnlyEnforceIf(b)
            par.append(b)
        m.AddBoolOr(par + [v[i].Not()])
    if ub: m.Add(sum(v) <= ub)
    m.Minimize(sum(v))
    sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = tl; sv.parameters.num_search_workers = workers
    st = sv.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
    ring.glue[X] = {c for i, c in enumerate(cand) if sv.Value(v[i])}
    return len(ring.glue[X]), sv.StatusName(st), len(cand)


if __name__ == '__main__':
    name, U = sys.argv[1], sys.argv[2]
    rels = json.loads(sys.argv[3])
    for rel in rels:
        rel = (rel[0], tuple(rel[1]), rel[2])
        ring, X = link_ring(name, U, rel)
        g = route_cover(ring, X, maxlen=8)
        res = body_cp(ring, X, ub=g)
        bad = [b for b in ring.check() if (b[0] == X and 'not carried' not in b[2]) or (b[0] == U and 'carried by ' + X in b[2])]
        print(rel, 'greedy', g, 'cp', res, 'bad', len(bad), flush=True)
