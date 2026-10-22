"""Exact module for the square ring's straight link (next body W one lane to the +y side, gap column y=a).
Variables per lane (y,z) in [0,a)x[0,b): P, R, C (free for W's lateral cover), pl (V plate x=1), w2/w3 (W glue at
x=-2/-3 under V).  Gap column y=a: g2/g3 (W glue at -2/-3), riser cells r (W glue at x=-1,0,1 at one z) that join
W's plate at (1, 0, z) of the next module (a copy of this one).  Rules as cp_module.py plus:
  gap g2 at z covers V's lane (a-1, z); it is beside W's own lane (0, z) at x=-2, so lane (0, z) must not be P;
  the riser at z needs lane (a-1, z) without P/R and lane (0, z) with plate.
Minimise pl + R + w2 + w3 + g2 + g3 + 3 (riser).
python cp_square.py K A B [SECONDS]"""
import sys, json
from ortools.sat.python import cp_model
from cp_module import connect, N4


def solve(k, a, b, secs=20, workers=8):
    m = cp_model.CpModel()
    L = [(y, z) for y in range(a) for z in range(b)]; Ls = set(L)
    nb = {c: [(c[0] + d[0], c[1] + d[1]) for d in N4 if (c[0] + d[0], c[1] + d[1]) in Ls] for c in L}
    B = m.NewBoolVar
    P = {c: B('') for c in L}; R = {c: B('') for c in L}; C = {c: B('') for c in L}
    pl = {c: B('') for c in L}; w2 = {c: B('') for c in L}; w3 = {c: B('') for c in L}
    G = [(a, z) for z in range(b)]
    g2 = {c: B('') for c in G}; g3 = {c: B('') for c in G}; rz = {c: B('') for c in G}
    m.AddExactlyOne(rz.values())
    for c in L:
        m.Add(P[c] + R[c] + C[c] <= 1)
        m.AddImplication(P[c], pl[c]); m.AddImplication(R[c], pl[c])
        m.AddBoolOr([R[v] for v in nb[c]] + [P[c].Not()])
        m.AddImplication(w2[c], C[c])
        cov = [w3[c]] + [w2[v] for v in nb[c]]
        if c[0] == a - 1: cov.append(g2[(a, c[1])])
        m.AddBoolOr(cov + [P[c].Not()])
    m.Add(sum(P.values()) == k)
    for z in range(b):
        g = (a, z)
        m.AddImplication(g2[g], P[(0, z)].Not())          # W's own lane beside its gap cover
        m.AddImplication(rz[g], P[(a - 1, z)].Not()); m.AddImplication(rz[g], R[(a - 1, z)].Not())
        m.AddImplication(rz[g], pl[(0, z)])
        m.AddImplication(rz[g], C[(a - 1, z)].Not())
    connect(m, L, pl, nb, 'pl')
    # W cells: under V (w2,w3), gap (g2,g3), riser bottom node (gap, x=-2 level reached by the riser)
    nodes = [(c, 2) for c in L] + [(c, 3) for c in L] + [(g, 2) for g in G] + [(g, 3) for g in G]
    sel = {}
    for c in L: sel[(c, 2)] = w2[c]; sel[(c, 3)] = w3[c]
    for g in G:
        # the riser cell at (-1, g) touches (-2, g): treat the riser as making g2 present
        x = B(''); m.AddBoolOr([g2[g], rz[g]]).OnlyEnforceIf(x); m.AddImplication(g2[g], x); m.AddImplication(rz[g], x)
        sel[(g, 2)] = x; sel[(g, 3)] = g3[g]
    lane_adj = {c: nb[c] + ([(a, c[1])] if c[0] == a - 1 else []) for c in L}
    for g in G: lane_adj[g] = [(a - 1, g[1])] + [(a, z) for z in (g[1] - 1, g[1] + 1) if 0 <= z < b]
    adj = {(c, h): [(v, h) for v in lane_adj[c]] + [(c, 5 - h)] for c in L + G for h in (2, 3)}
    connect(m, nodes, sel, adj, 'w')
    xs = {g: sel[(g, 2)] for g in G}
    m.Minimize(sum(pl.values()) + sum(R.values()) + sum(w2.values()) + sum(w3.values())
               + sum(xs.values()) + sum(g3.values()) + 3)
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = secs; s.parameters.num_workers = workers
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
    gl = lambda d: sorted(c for c in d if s.Value(d[c]))
    return dict(cost=int(s.ObjectiveValue()), bound=int(s.BestObjectiveBound()), P=gl(P), R=gl(R), C=gl(C),
                pl=gl(pl), w2=gl(w2), w3=gl(w3), g2=gl(g2), g3=gl(g3), rz=gl(rz), a=a, b=b)


if __name__ == '__main__':
    k, a, b = map(int, sys.argv[1:4]); secs = float(sys.argv[4]) if len(sys.argv) > 4 else 20
    r = solve(k, a, b, secs); print(json.dumps(r))
