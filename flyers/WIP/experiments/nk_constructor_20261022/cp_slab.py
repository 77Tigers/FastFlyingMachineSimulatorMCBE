"""Exact slabP-style module: choose k pusher lanes P and RB lanes R in an a x b box; plate = P+R (connected);
next body's slab at x=-3 = P lanes plus any extra lanes needed to connect it. Minimise plate + R + slab.
python cp_slab.py K A B [SECONDS]"""
import sys, json
from ortools.sat.python import cp_model
from cp_module import connect, N4


def solve(k, a, b, secs=10, workers=8):
    m = cp_model.CpModel(); L = [(y, z) for y in range(a) for z in range(b)]; Ls = set(L)
    nb = {c: [(c[0] + d[0], c[1] + d[1]) for d in N4 if (c[0] + d[0], c[1] + d[1]) in Ls] for c in L}
    P = {c: m.NewBoolVar('') for c in L}; R = {c: m.NewBoolVar('') for c in L}
    U = {c: m.NewBoolVar('') for c in L}; W = {c: m.NewBoolVar('') for c in L}
    for c in L:
        m.Add(P[c] + R[c] <= 1); m.Add(U[c] == P[c] + R[c])
        m.AddBoolOr([R[v] for v in nb[c]] + [P[c].Not()])
        m.AddImplication(P[c], W[c])
    m.Add(sum(P.values()) == k)
    connect(m, L, U, nb, 'u'); connect(m, L, W, nb, 'w')
    m.Minimize(sum(U.values()) + sum(R.values()) + sum(W.values()))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = secs; s.parameters.num_workers = workers
    st = s.Solve(m)
    g = lambda d: sorted(c for c in L if s.Value(d[c]))
    return dict(cost=int(s.ObjectiveValue()), bound=int(s.BestObjectiveBound()), P=g(P), R=g(R), W=g(W), a=a, b=b)


if __name__ == '__main__':
    k, a, b = map(int, sys.argv[1:4]); secs = float(sys.argv[4]) if len(sys.argv) > 4 else 10
    r = solve(k, a, b, secs); print(json.dumps(r))
