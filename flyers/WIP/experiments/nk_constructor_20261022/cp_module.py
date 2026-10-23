"""Exact flat-module optimiser (CP-SAT) for k pushers.
Lanes (y,z) in an a x b box; per lane: P (pusher at x=0), R (redstone block at x=0), C (lane kept free for the next
body's lateral cover at x=-2), or empty.  pl = V plate at x=1; w2 = next-body glue at x=-2 (C lanes only);
w3 = next-body glue at x=-3 (any lane).  Rules: P needs pl, an R neighbour, and (w3 or a C neighbour with w2);
R needs pl; plate cells connected; next-body cells (w2 + w3) connected.  Minimise pl + R + w2 + w3.
python cp_module.py K [A B] [SECONDS]"""
import sys, json
from ortools.sat.python import cp_model

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def connect(m, cells, x, adj, name):
    """x[c] selected cells must be connected: single-commodity flow from one chosen root."""
    root = {c: m.NewBoolVar('') for c in cells}
    m.AddExactlyOne(root.values())
    for c in cells: m.AddImplication(root[c], x[c])
    n = len(cells); f = {}
    for u in cells:
        for v in adj[u]:
            f[u, v] = m.NewIntVar(0, n, '')
            m.Add(f[u, v] == 0).OnlyEnforceIf(x[u].Not()); m.Add(f[u, v] == 0).OnlyEnforceIf(x[v].Not())
    for u in cells:
        inflow = sum(f[v, u] for v in adj[u]); outflow = sum(f[u, v] for v in adj[u])
        supply = m.NewIntVar(0, n, '')
        # root supplies (count-1); others consume 1 if selected
        tot = m.NewIntVar(0, n, ''); m.Add(tot == sum(x.values()))
        m.Add(supply == tot).OnlyEnforceIf(root[u]); m.Add(supply == 0).OnlyEnforceIf(root[u].Not())
        m.Add(outflow - inflow == supply - x[u])


def solve(k, a, b, secs=10, workers=8, sym=False, hint=None, det=None):
    m = cp_model.CpModel()
    L = [(y, z) for y in range(a) for z in range(b)]
    nb = {c: [(c[0] + d[0], c[1] + d[1]) for d in N4 if (c[0] + d[0], c[1] + d[1]) in set(L)] for c in L}
    B = lambda: m.NewBoolVar('')
    P = {c: B() for c in L}; R = {c: B() for c in L}; C = {c: B() for c in L}
    pl = {c: B() for c in L}; w2 = {c: B() for c in L}; w3 = {c: B() for c in L}
    for c in L:
        m.Add(P[c] + R[c] + C[c] <= 1)
        m.AddImplication(P[c], pl[c]); m.AddImplication(R[c], pl[c])
        m.AddBoolOr([R[v] for v in nb[c]] + [P[c].Not()])
        m.AddImplication(w2[c], C[c])
        m.AddBoolOr([w3[c]] + [w2[v] for v in nb[c]] + [P[c].Not()])
    m.Add(sum(P.values()) == k)
    if sym:   # mirror-symmetric under z -> b-1-z
        for (y, z) in L:
            mz = (y, b - 1 - z)
            for d in (P, R, C, pl, w2, w3): m.Add(d[(y, z)] == d[mz])
    connect(m, L, pl, nb, 'pl')
    # next-body cells: nodes (c,2) and (c,3)
    W = {(c, 2): w2[c] for c in L}; W.update({(c, 3): w3[c] for c in L})
    wadj = {(c, h): [(v, h) for v in nb[c]] + [(c, 5 - h)] for c in L for h in (2, 3)}
    connect(m, list(W), W, wadj, 'w')
    m.Minimize(sum(pl.values()) + sum(R.values()) + sum(w2.values()) + sum(w3.values()))
    if hint:
        for name, d in (('P', P), ('R', R), ('C', C), ('pl', pl), ('w2', w2), ('w3', w3)):
            hs = set(map(tuple, hint.get(name, [])))
            for c in L: m.AddHint(d[c], c in hs)
    s = cp_model.CpSolver(); s.parameters.num_workers = workers
    if det: s.parameters.max_deterministic_time = det
    else: s.parameters.max_time_in_seconds = secs
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
    g = lambda d: sorted(c for c in L if s.Value(d[c]))
    return dict(cost=int(s.ObjectiveValue()), bound=int(s.BestObjectiveBound()), opt=st == cp_model.OPTIMAL,
                P=g(P), R=g(R), C=g(C), pl=g(pl), w2=g(w2), w3=g(w3), a=a, b=b)


def show(r):
    out = []
    for z in range(r['b'] - 1, -1, -1):
        row = ''
        for y in range(r['a']):
            c = (y, z)
            ch = 'P' if c in r['P'] else 'R' if c in r['R'] else 'C' if c in r['C'] else '.'
            if c in r['w2']: ch = 'c'
            if ch in '.C' and c in r['pl']: ch = '_'
            row += ch + ('3' if c in r['w3'] else ' ')
        out.append(row)
    return '\n'.join(out)


if __name__ == '__main__':
    k = int(sys.argv[1])
    a, b = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (k, k)
    secs = float(sys.argv[4]) if len(sys.argv) > 4 else 10
    r = solve(k, a, b, secs)
    print(k, a, b, {x: r[x] for x in ('cost', 'bound', 'opt')})
    print(show(r))
