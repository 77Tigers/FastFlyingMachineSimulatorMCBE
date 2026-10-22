"""min #R lanes dominating k connected P lanes in an a x b box (slabP module)."""
import sys
from ortools.sat.python import cp_model
from cp_module import connect, N4
def solve(k, a, b, secs=10, workers=8):
    m = cp_model.CpModel(); L = [(y, z) for y in range(a) for z in range(b)]; Ls = set(L)
    nb = {c: [(c[0]+d[0], c[1]+d[1]) for d in N4 if (c[0]+d[0], c[1]+d[1]) in Ls] for c in L}
    P = {c: m.NewBoolVar('') for c in L}; R = {c: m.NewBoolVar('') for c in L}
    U = {c: m.NewBoolVar('') for c in L}
    for c in L:
        m.Add(P[c] + R[c] <= 1); m.AddBoolOr([R[v] for v in nb[c]] + [P[c].Not()])
        m.Add(U[c] == P[c] + R[c])
    m.Add(sum(P.values()) == k)
    connect(m, L, P, nb, 'p'); connect(m, L, U, nb, 'u')
    m.Minimize(sum(R.values()))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = secs; s.parameters.num_workers = workers
    st = s.Solve(m)
    return int(s.ObjectiveValue()), int(s.BestObjectiveBound()), sorted(c for c in L if s.Value(P[c])), sorted(c for c in L if s.Value(R[c]))
if __name__ == '__main__':
    k = int(sys.argv[1])
    for a, b in [(int(x.split('x')[0]), int(x.split('x')[1])) for x in sys.argv[2:]]:
        r = solve(k, a, b); print(k, a, b, 'R', r[0], 'bound', r[1])
