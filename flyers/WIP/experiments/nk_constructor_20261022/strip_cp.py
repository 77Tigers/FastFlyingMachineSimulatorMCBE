"""CP-SAT strip pattern for terrace floors: p pusher lanes in an a x b box, redstone-block lanes (each pusher needs one
beside it), plate over pushers + RBs (+ extra lanes) connected, and the slab under the pushers (+ extra lanes)
connected.  Minimise g * (plate + RB) + slab.  python strip_cp.py P A B [G]"""
import sys
from ortools.sat.python import cp_model
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def connect(m, cells, x, nb):
    root = {c: m.NewBoolVar('') for c in cells}
    m.AddExactlyOne(root.values())
    for c in cells: m.AddImplication(root[c], x[c])
    n = len(cells); f = {}
    tot = m.NewIntVar(0, n, ''); m.Add(tot == sum(x.values()))
    for u in cells:
        for v in nb[u]:
            f[u, v] = m.NewIntVar(0, n, '')
            m.Add(f[u, v] == 0).OnlyEnforceIf(x[u].Not()); m.Add(f[u, v] == 0).OnlyEnforceIf(x[v].Not())
    for u in cells:
        sup = m.NewIntVar(0, n, '')
        m.Add(sup == tot).OnlyEnforceIf(root[u]); m.Add(sup == 0).OnlyEnforceIf(root[u].Not())
        m.Add(sum(f[u, v] for v in nb[u]) - sum(f[v, u] for v in nb[u]) == sup - x[u])


def solve(p, a, b, g=2, det=2.0):
    m = cp_model.CpModel(); B = m.NewBoolVar
    L = [(y, z) for y in range(a) for z in range(b)]; Ls = set(L)
    nb = {c: [(c[0] + d[0], c[1] + d[1]) for d in N4 if (c[0] + d[0], c[1] + d[1]) in Ls] for c in L}
    P = {c: B('') for c in L}; R = {c: B('') for c in L}; PL = {c: B('') for c in L}; S = {c: B('') for c in L}
    for c in L:
        m.Add(P[c] + R[c] <= 1)
        m.AddImplication(P[c], PL[c]); m.AddImplication(R[c], PL[c]); m.AddImplication(P[c], S[c])
        m.AddBoolOr([R[v] for v in nb[c]] + [P[c].Not()])
    m.Add(sum(P.values()) == p)
    connect(m, L, PL, nb); connect(m, L, S, nb)
    m.Minimize(g * (sum(PL.values()) + sum(R.values())) + sum(S.values()))
    s = cp_model.CpSolver(); s.parameters.num_workers = 1; s.parameters.max_deterministic_time = det
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
    gl = lambda d: sorted(c for c in L if s.Value(d[c]))
    return dict(cost=int(s.ObjectiveValue()), opt=st == cp_model.OPTIMAL, P=gl(P), R=gl(R), PL=gl(PL), S=gl(S), size=(a, b))


if __name__ == '__main__':
    p, a, b = map(int, sys.argv[1:4]); g = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    r = solve(p, a, b, g)
    print(r and {k: r[k] for k in ('cost', 'opt')}, r and (len(r['PL']), len(r['R']), len(r['S'])))
    if r:
        for z in range(b - 1, -1, -1):
            print(''.join('P' if (y, z) in r['P'] else 'R' if (y, z) in r['R'] else '_' if (y, z) in r['PL'] else '.' for y in range(a)))


def solve2(p, a, b, g=2, det=2.0, margin=1, hint=None, workers=1):
    """as solve, but floor 1's spent hoppers may also be covered from beside: a cover cell at -2 in a lane with no
    hopper and no RB (the cover rides up to level 0, where an RB would be), next to the hopper; behind covers sit at -3
    in any lane. The cover (behind + beside cells) is one connected piece. Lanes may extend `margin` past the box for
    beside covers only. Minimise g * (plate + RB) + cover."""
    m = cp_model.CpModel(); B = m.NewBoolVar
    L = [(y, z) for y in range(a) for z in range(b)]; Ls = set(L)
    W = [(y, z) for y in range(-margin, a + margin) for z in range(-margin, b + margin)]; Ws = set(W)
    nbL = {c: [(c[0] + d[0], c[1] + d[1]) for d in N4 if (c[0] + d[0], c[1] + d[1]) in Ls] for c in L}
    nbW = {c: [(c[0] + d[0], c[1] + d[1]) for d in N4 if (c[0] + d[0], c[1] + d[1]) in Ws] for c in W}
    P = {c: B('') for c in L}; R = {c: B('') for c in L}; PL = {c: B('') for c in L}
    Sb = {c: B('') for c in L}; Sd = {c: B('') for c in W}
    F = m.NewConstant(0)
    g0 = lambda d, c: d.get(c, F)
    for c in L:
        m.Add(P[c] + R[c] <= 1)
        m.AddImplication(P[c], PL[c]); m.AddImplication(R[c], PL[c])
        m.AddBoolOr([R[v] for v in nbL[c]] + [P[c].Not()])
        m.AddBoolOr([Sb[c]] + [Sd[v] for v in nbW[c]] + [P[c].Not()])     # every hopper covered
    for c in W:   # beside cover only in a lane free of hoppers and RBs
        m.AddImplication(Sd[c], g0(P, c).Not()); m.AddImplication(Sd[c], g0(R, c).Not())
    m.Add(sum(P.values()) == p)
    connect(m, L, PL, nbL)
    # cover connectivity over nodes (level, lane): behind (-3, c), beside (-2, c); same-lane cells are x-neighbours
    nodes = [('b', c) for c in L] + [('d', c) for c in W]
    x = {('b', c): Sb[c] for c in L}; x.update({('d', c): Sd[c] for c in W})
    nb = {}
    for t, c in nodes:
        lat = [(t, v) for v in (nbL[c] if t == 'b' else nbW[c])]
        other = ('d' if t == 'b' else 'b', c)
        nb[(t, c)] = lat + ([other] if other in x else [])
    connect(m, nodes, x, nb)
    m.Minimize(g * (sum(PL.values()) + sum(R.values())) + sum(Sb.values()) + sum(Sd.values()))
    if hint:   # e.g. the plain strip pattern (behind covers only)
        for d, key in ((P, 'P'), (R, 'R'), (PL, 'PL'), (Sb, 'S')):
            hs = set(map(tuple, hint[key]))
            for c in d: m.AddHint(d[c], c in hs)
        for c in W: m.AddHint(Sd[c], False)
    s = cp_model.CpSolver(); s.parameters.num_workers = workers; s.parameters.max_deterministic_time = det
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
    gl = lambda d: sorted(c for c in d if s.Value(d[c]))
    return dict(cost=int(s.ObjectiveValue()), opt=st == cp_model.OPTIMAL, P=gl(P), R=gl(R), PL=gl(PL), S=gl(Sb),
                SD=gl(Sd), size=(a, b))


def solve_many(p, a, b, g=2, slack=0, limit=40, det=10.0):
    """distinct strip patterns within `slack` of the optimum (CP solution enumeration with the objective as a bound)"""
    best = solve(p, a, b, g, det)
    if best is None: return []
    m = cp_model.CpModel(); B = m.NewBoolVar
    L = [(y, z) for y in range(a) for z in range(b)]; Ls = set(L)
    nb = {c: [(c[0] + d[0], c[1] + d[1]) for d in N4 if (c[0] + d[0], c[1] + d[1]) in Ls] for c in L}
    P = {c: B('') for c in L}; R = {c: B('') for c in L}; PL = {c: B('') for c in L}; S = {c: B('') for c in L}
    for c in L:
        m.Add(P[c] + R[c] <= 1)
        m.AddImplication(P[c], PL[c]); m.AddImplication(R[c], PL[c]); m.AddImplication(P[c], S[c])
        m.AddBoolOr([R[v] for v in nb[c]] + [P[c].Not()])
    m.Add(sum(P.values()) == p)
    connect(m, L, PL, nb); connect(m, L, S, nb)
    m.Add(g * (sum(PL.values()) + sum(R.values())) + sum(S.values()) <= best['cost'] + slack)
    out = []

    class CB(cp_model.CpSolverSolutionCallback):
        def __init__(s): super().__init__(); s.seen = set()
        def on_solution_callback(s):
            key = (tuple(c for c in L if s.Value(P[c])), tuple(c for c in L if s.Value(R[c])),
                   tuple(c for c in L if s.Value(PL[c])), tuple(c for c in L if s.Value(S[c])))
            if key in s.seen: return
            s.seen.add(key); out.append(dict(P=list(key[0]), R=list(key[1]), PL=list(key[2]), S=list(key[3]), size=(a, b)))
            if len(out) >= limit: s.StopSearch()
    sv = cp_model.CpSolver(); sv.parameters.enumerate_all_solutions = True; sv.parameters.num_workers = 1
    sv.parameters.max_time_in_seconds = 60
    sv.Solve(m, CB())
    return out
