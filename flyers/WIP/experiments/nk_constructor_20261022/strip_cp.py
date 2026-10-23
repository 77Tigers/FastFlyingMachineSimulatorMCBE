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
