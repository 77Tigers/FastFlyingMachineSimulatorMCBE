"""Periodic (torus) bulk pattern search for hopper-ring modules with pusher levels.
Lane (y,z) on an a x b torus; pusher level h in LEVELS or none; V blocks S/R at x in XR; next-body (W) glue at x in XW
(position at V-local 0; it sweeps x..x+2).  Minimise (S + R + W) for a fixed number of pushers.
Rules (see README): P at h: front (h+1) is V S/R, cells h-1,h-2 free of V blocks, needs a lateral R at x=h,
no lateral R at h-1/h-2, adhesion = S in front or lateral S at h; R needs an S face neighbour; V S connected;
cover: W at (h-3) in lane or lateral W at h-2; W cell sweeps x..x+2 (lane free of V there; in a P lane only x<=h-3);
W base x must not be lateral to a ready pusher (x != h) and not lateral to a V R at x or x+1; W connected.
python cp_periodic.py A B NP [LEVELS] [SECONDS]"""
import sys
from ortools.sat.python import cp_model


def solve(a, b, NP, levels=(0, 1), secs=60, workers=12):
    m = cp_model.CpModel()
    lanes = [(y, z) for y in range(a) for z in range(b)]
    nb = {(y, z): [((y + 1) % a, z), ((y - 1) % a, z), (y, (z + 1) % b), (y, (z - 1) % b)] for (y, z) in lanes}
    XR = list(range(min(levels) - 2, max(levels) + 3))
    XW = list(range(min(levels) - 4, max(levels) + 1))
    B = m.NewBoolVar
    P = {(l, h): B('') for l in lanes for h in levels}
    S = {(x, l): B('') for x in XR for l in lanes}
    R = {(x, l): B('') for x in XR for l in lanes}
    W = {(x, l): B('') for x in XW for l in lanes}
    getS = lambda x, l: S.get((x, l)); getR = lambda x, l: R.get((x, l))
    for l in lanes:
        m.AddAtMostOne(P[l, h] for h in levels)
        for x in XR: m.AddAtMostOne([S[x, l], R[x, l]])
        for h in levels:
            p = P[l, h]
            # front
            m.AddBoolOr([S[h + 1, l], R[h + 1, l]]).OnlyEnforceIf(p)
            for x in (h, h - 1, h - 2):
                m.AddImplication(p, S[x, l].Not()); m.AddImplication(p, R[x, l].Not())
            # power
            m.AddBoolOr([R[h, v] for v in nb[l]]).OnlyEnforceIf(p)
            for v in nb[l]:
                for x in (h - 1, h - 2): m.AddImplication(p, R[x, v].Not())
            # adhesion
            m.AddBoolOr([S[h + 1, l]] + [S[h, v] for v in nb[l]]).OnlyEnforceIf(p)
            # cover
            opts = [W[h - 3, l]] if (h - 3, l) in W else []
            opts += [W[h - 2, v] for v in nb[l] if (h - 2, v) in W]
            m.AddBoolOr(opts).OnlyEnforceIf(p)
            # W never lateral to the ready pusher at its base x == h
            for v in nb[l]:
                if (h, v) in W: m.AddImplication(p, W[h, v].Not())
        # R attachment
        for x in XR:
            ns = [S[x, v] for v in nb[l]] + [S[x2, l] for x2 in (x - 1, x + 1) if (x2, l) in S]
            m.AddBoolOr(ns).OnlyEnforceIf(R[x, l])
        # W sweep: lane free of V blocks over x..x+2 and of pushers unless x <= h-3
        for x in XW:
            w = W[x, l]
            for x2 in (x, x + 1, x + 2):
                if (x2, l) in S: m.AddImplication(w, S[x2, l].Not()); m.AddImplication(w, R[x2, l].Not())
            for h in levels:
                if not x <= h - 3: m.AddImplication(w, P[l, h].Not())
            # not lateral to V R at x or x+1 (W moves while V rests)
            for v in nb[l]:
                for x2 in (x, x + 1):
                    if (x2, v) in R: m.AddImplication(w, R[x2, v].Not())
    m.Add(sum(P.values()) == NP)
    # connectivity on the torus (flow) for S and for W
    def connect(nodes, sel, adj):
        root = {u: B('') for u in nodes}; m.AddExactlyOne(root.values())
        for u in nodes: m.AddImplication(root[u], sel[u])
        n = len(nodes); tot = sum(sel.values())
        f = {}
        for u in nodes:
            for v in adj[u]:
                f[u, v] = m.NewIntVar(0, n, '')
                m.Add(f[u, v] == 0).OnlyEnforceIf(sel[u].Not()); m.Add(f[u, v] == 0).OnlyEnforceIf(sel[v].Not())
        for u in nodes:
            sup = m.NewIntVar(0, n, '')
            m.Add(sup == tot).OnlyEnforceIf(root[u]); m.Add(sup == 0).OnlyEnforceIf(root[u].Not())
            m.Add(sum(f[u, v] for v in adj[u]) - sum(f[v, u] for v in adj[u]) == sup - sel[u])
    sadj = {(x, l): [(x, v) for v in nb[l]] + [(x2, l) for x2 in (x - 1, x + 1) if (x2, l) in S] for (x, l) in S}
    connect(list(S), S, sadj)
    wadj = {(x, l): [(x, v) for v in nb[l]] + [(x2, l) for x2 in (x - 1, x + 1) if (x2, l) in W] for (x, l) in W}
    connect(list(W), W, wadj)
    m.Minimize(sum(S.values()) + sum(R.values()) + sum(W.values()))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = secs; s.parameters.num_workers = workers
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
    sol = dict(cost=int(s.ObjectiveValue()), bound=int(s.BestObjectiveBound()), opt=st == cp_model.OPTIMAL)
    sol['P'] = {l: h for (l, h), v in P.items() if s.Value(v)}
    sol['S'] = sorted(k for k, v in S.items() if s.Value(v)); sol['R'] = sorted(k for k, v in R.items() if s.Value(v))
    sol['W'] = sorted(k for k, v in W.items() if s.Value(v))
    return sol


if __name__ == '__main__':
    a, b, NP = map(int, sys.argv[1:4])
    levels = tuple(int(c) for c in sys.argv[4].split(',')) if len(sys.argv) > 4 else (0, 1)
    secs = float(sys.argv[5]) if len(sys.argv) > 5 else 60
    r = solve(a, b, NP, levels, secs)
    if not r: print('infeasible/unknown'); sys.exit()
    print(a, b, NP, levels, 'cost', r['cost'], 'bound', r['bound'], 'opt', r['opt'], 'per P', round(r['cost'] / NP, 3))
    print('P', r['P']); print('S', r['S']); print('R', r['R']); print('W', r['W'])
